"""
AI Agent Service — Orchestrator Loop
====================================
Orchestrates multi-turn tool calling, policy retrieval, evidence verification,
and response validation for the "Ask LoanPilot" investigation chatbot.

Cognizant Explainability Note:
- Async Orchestration: run_agent() is async def and awaits all tool executions and LLM calls.
- Multi-Turn Loop: Capped at MAX_TURNS (default 5). On each turn, the agent evaluates the user question,
  selects tools, receives results, and iterates until an evidence-grounded answer is produced.
- Application Isolation: Server-side application_id argument overriding ensures that the LLM
  cannot supply an arbitrary application_id to read another applicant's data.
- Refusal Safeguards: Prompts and fallback schemas strictly enforce that the agent NEVER executes
  automated approval/rejection decisions. All recommendations require human review.
- Response Repair Retry: If the LLM produces malformed JSON on turn completion, a single repair prompt
  is sent to fix the JSON schema without discarding the gathered reasoning trace.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import get_settings
from models.application import Application
from schemas.agent import (
    AgentQueryRequest,
    AgentQueryResponse,
    AgentResponse,
    EvidenceItem,
    TraceStep
)
from services.agent_tools import TOOL_REGISTRY, TOOLS
from utils.llm_client import llm_client, clean_and_parse_json

logger = logging.getLogger("loanpilot.agent_service")

SYSTEM_PROMPT = """
You are LoanPilot's AI Investigation Agent — an expert assistant for loan officers reviewing loan applications.

STRICT MANDATORY RULES:
1. ALWAYS call a tool FIRST before attempting to answer any question. Never answer from ungrounded assumptions.
2. NEVER state document or page evidence without having called `get_flag_evidence` first.
3. NEVER recommend approving or rejecting a loan application. Always redirect final decisions to the human underwriter.
4. Ground recommendations in policy passages retrieved via `search_policy` whenever possible.
5. If tools return no data or an error, say "I don't have that information" rather than guessing.
6. Your final output MUST be a single valid JSON object matching the AgentResponse schema:
{
  "answer": "Clear natural language summary...",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "evidence": [{"document": "DOC-0001", "page": 1, "value": "..."}],
  "policy_reference": "Policy passage citation...",
  "recommendation": "NEEDS_HUMAN_REVIEW",
  "requires_human_review": true
}
"""


async def run_agent(application_id: str, question: str, db: AsyncSession) -> AgentResponse:
    """
    Execute the multi-turn agent orchestration loop to answer a question about an application.

    Steps:
      1. Verify application exists in DB
      2. Initialize conversation with system prompt and user question
      3. Multi-turn loop (up to MAX_TURNS):
         a. Call resilient LLM client with tools
         b. If tool_use: execute requested tools asynchronously, record trace step, append result
         c. If end_turn: parse and validate AgentResponse JSON schema (with 1 repair retry if invalid)
      4. Return validated AgentResponse with full execution trace
    """
    settings = get_settings()
    max_turns = settings.MAX_AGENT_TURNS

    # 1. Verify application existence
    stmt = select(Application).where(Application.id == application_id)
    res = await db.execute(stmt)
    app = res.scalar_one_or_none()

    if not app:
        return AgentResponse(
            answer=f"Application '{application_id}' not found.",
            requires_human_review=True,
            trace=[]
        )

    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": question}
    ]

    trace_steps: List[TraceStep] = []
    step_counter = 1

    # 2. Multi-turn orchestration loop
    for turn in range(1, max_turns + 1):
        logger.info(f"[Turn {turn}/{max_turns}] Invoking LLM for application {application_id}")
        
        try:
            llm_resp = await llm_client.chat(messages, TOOLS, SYSTEM_PROMPT)
        except Exception as e:
            logger.error(f"LLM client invocation error on turn {turn}: {str(e)}")
            return AgentResponse(
                answer=f"An error occurred while consulting the AI engine: {str(e)}. Please review application files manually.",
                requires_human_review=True,
                trace=trace_steps
            )

        # Case A: LLM requests tool execution
        if llm_resp.stop_reason == "tool_use" and llm_resp.tool_calls:
            # Append assistant's tool-use intent to message history
            messages.append({
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": tc["id"], "name": tc["name"], "args": tc["args"]}
                    for tc in llm_resp.tool_calls
                ]
            })

            tool_result_content = []
            for tc in llm_resp.tool_calls:
                t_name = tc.get("name")
                t_args = tc.get("args", {})
                t_id = tc.get("id")

                if t_name not in TOOL_REGISTRY:
                    t_result = {"error": f"Unknown tool '{t_name}'"}
                else:
                    # Security Overwrite: Inject authentic application_id server-side
                    if "application_id" in t_args or t_name != "search_policy":
                        t_args["application_id"] = application_id

                    try:
                        tool_fn = TOOL_REGISTRY[t_name]
                        if t_name == "search_policy":
                            query_str = t_args.get("query", question)
                            t_result = await tool_fn(query=query_str)
                        else:
                            t_result = await tool_fn(db=db, **t_args)
                    except Exception as err:
                        logger.error(f"Tool '{t_name}' execution error: {str(err)}")
                        t_result = {"error": str(err)}

                # Build human-readable summary for reasoning trace
                if "error" in t_result:
                    summary_str = f"Error: {t_result['error']}"
                elif t_name == "get_application_data":
                    summary_str = f"Retrieved applicant '{t_result.get('applicant_name')}', status='{t_result.get('status')}', {len(t_result.get('documents', []))} documents."
                elif t_name == "get_verification_results":
                    summary_str = f"Found {len(t_result.get('mismatches', []))} mismatches, {len(t_result.get('matches', []))} matches."
                elif t_name == "get_risk_flags":
                    summary_str = f"Retrieved risk score {t_result.get('score')} ({t_result.get('level')}), {len(t_result.get('flags', []))} risk flags."
                elif t_name == "get_flag_evidence":
                    summary_str = f"Retrieved evidence string: {t_result.get('evidence_string')}"
                elif t_name == "search_policy":
                    summary_str = f"Retrieved {len(t_result.get('chunks', []))} matching policy passages."
                else:
                    summary_str = f"Executed {t_name} successfully."

                trace_steps.append(TraceStep(
                    step=step_counter,
                    tool=t_name,
                    args=t_args,
                    summary=summary_str
                ))
                step_counter += 1

                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": t_id,
                    "content": t_result
                })

            messages.append({
                "role": "tool",
                "content": tool_result_content
            })
            continue

        # Case B: LLM completed execution and returned final text
        if llm_resp.text:
            parsed = None
            try:
                parsed = clean_and_parse_json(llm_resp.text)
            except Exception as parse_err:
                logger.warning(f"JSON parsing failed on turn {turn}: {str(parse_err)}. Requesting repair retry.")

            # Schema repair retry attempt
            if not parsed or not isinstance(parsed, dict) or "answer" not in parsed:
                repair_prompt = (
                    "Your previous response was not valid JSON matching the required schema. "
                    "Return ONLY valid JSON matching this exact schema: "
                    '{"answer": "...", "risk_level": "MEDIUM", "evidence": [], "policy_reference": "...", "recommendation": "NEEDS_HUMAN_REVIEW", "requires_human_review": true}'
                )
                messages.append({"role": "user", "content": repair_prompt})
                try:
                    repair_resp = await llm_client.chat(messages, [], SYSTEM_PROMPT)
                    if repair_resp.text:
                        parsed = clean_and_parse_json(repair_resp.text)
                except Exception as repair_err:
                    logger.error(f"Repair retry failed: {str(repair_err)}")

            if isinstance(parsed, dict) and "answer" in parsed:
                evidence_list = []
                for ev in parsed.get("evidence", []):
                    if isinstance(ev, dict):
                        evidence_list.append(EvidenceItem(
                            document=str(ev.get("document", "Document")),
                            page=int(ev.get("page", 1)),
                            value=str(ev.get("value", ""))
                        ))
                    elif isinstance(ev, str):
                        evidence_list.append(EvidenceItem(document=ev, page=1, value=ev))

                return AgentResponse(
                    answer=parsed.get("answer", "Analysis complete."),
                    risk_level=parsed.get("risk_level", app.risk_level or "MEDIUM"),
                    evidence=evidence_list,
                    policy_reference=parsed.get("policy_reference"),
                    recommendation=parsed.get("recommendation", "NEEDS_HUMAN_REVIEW"),
                    requires_human_review=True,
                    trace=trace_steps
                )

            # Fallback if raw text couldn't be parsed into JSON dictionary
            return AgentResponse(
                answer=llm_resp.text,
                risk_level=app.risk_level or "MEDIUM",
                evidence=[],
                policy_reference="Loan Documentation SOP",
                recommendation="NEEDS_HUMAN_REVIEW",
                requires_human_review=True,
                trace=trace_steps
            )

    # If MAX_TURNS reached without explicit final answer
    return AgentResponse(
        answer=f"Analysis reached maximum turn limit ({max_turns}). Please review gathered risk flags and verification results manually.",
        risk_level=app.risk_level or "MEDIUM",
        evidence=[],
        policy_reference="Underwriting Guidelines Section 1",
        recommendation="NEEDS_HUMAN_REVIEW",
        requires_human_review=True,
        trace=trace_steps
    )


async def query_agent(
    app_id: str,
    request: AgentQueryRequest,
    db: AsyncSession,
) -> AgentQueryResponse:
    """
    Backward-compatible helper function for query_agent.
    """
    agent_resp = await run_agent(app_id, request.question, db)
    return AgentQueryResponse(
        answer=agent_resp.answer,
        evidence=[f"{ev.document} p.{ev.page}: {ev.value}" for ev in agent_resp.evidence],
        sources=[ev.document for ev in agent_resp.evidence],
        follow_up_questions=["Show me the detailed income discrepancy evidence", "What does policy say about income mismatches?"]
    )
