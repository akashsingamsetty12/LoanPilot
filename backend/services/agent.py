"""
AI Agent Service
==============================
Orchestrates pipeline outputs into evidence-backed reasoning.
Powers the "Ask LoanPilot" chatbot and generates explanations.


Architecture:
  Lightweight tool-calling agent (LangChain or plain function-calling) with 3-4 tools:
    Tool 1: get_application_data(app_id)         → application + documents summary
    Tool 2: get_verification_results(app_id)     → matches, mismatches, missing docs
    Tool 3: get_flag_evidence(app_id, flag_idx)  → detailed evidence for a flag
    Tool 4: get_document_text(doc_id, page)      → raw text from a specific page

RULE: Use ONLY the application's own data. NO hallucinated facts.

Data flow:
  Flags + verification results → chat answers + evidence

Input:  AgentQueryRequest (natural language question)
Output: AgentQueryResponse (answer + evidence + sources + follow-ups)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.agent import AgentQueryRequest, AgentQueryResponse


async def query_agent(
    app_id: str,
    request: AgentQueryRequest,
    db: AsyncSession,
) -> AgentQueryResponse:
    """
    Answer a natural language question about a loan application.

    Example questions:
      - "Why was this application flagged?"
      - "Which document is missing?"
      - "Show me the evidence for the income discrepancy"
      - "What is the applicant's income?"
      - "Compare the names across all documents"

    Steps:
      1. Load application data, verification results, and flags from DB
      2. Build agent context with available tools
      3. Send question to LLM with tool definitions
      4. Parse tool calls and execute them against DB
      5. Return evidence-backed answer

    TODO: implement agent with tool-calling
    """
    raise NotImplementedError("query_agent() is not implemented")


# ── Agent Tools ──

async def tool_get_application_data(app_id: str, db: AsyncSession) -> dict:
    """Agent tool: fetch application summary with documents."""
    raise NotImplementedError("tool_get_application_data() is not implemented")


async def tool_get_verification_results(app_id: str, db: AsyncSession) -> dict:
    """Agent tool: fetch verification matches/mismatches."""
    raise NotImplementedError("tool_get_verification_results() is not implemented")


async def tool_get_flag_evidence(app_id: str, flag_index: int, db: AsyncSession) -> dict:
    """Agent tool: fetch detailed evidence for a specific flag."""
    raise NotImplementedError("tool_get_flag_evidence() is not implemented")


async def tool_get_document_text(doc_id: str, page: int, db: AsyncSession) -> dict:
    """Agent tool: fetch raw OCR text from a specific document page."""
    raise NotImplementedError("tool_get_document_text() is not implemented")
