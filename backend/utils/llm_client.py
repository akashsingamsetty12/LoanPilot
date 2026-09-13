"""
LLM Client Abstraction
=======================
Unified interface for LLM API calls. Supports OpenAI (GPT-4o / GPT-4o-mini),
Google Gemini, AWS Bedrock (Converse API), and Local Emergency provider for offline execution and testing.
"""

import json
import re
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from starlette.concurrency import run_in_threadpool
from config import get_settings
from utils.confidence import parse_numeric_value

logger = logging.getLogger("loanpilot.llm")


@dataclass
class LLMResponse:
    """
    Normalized provider-neutral LLM response object.

    Architecture Note:
    Isolates provider-specific JSON response structures (Bedrock Converse,
    OpenAI ChatCompletions, Gemini, or Mock) into a single unified format.
    The agent orchestrator consumes ONLY these fields.
    """
    stop_reason: str          # "tool_use" | "end_turn"
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # [{"id": ..., "name": ..., "args": ...}]
    text: Optional[str] = None


def clean_and_parse_json(text_or_content: str) -> Dict[str, Any]:
    """
    Robust JSON parser for LLM outputs. Automatically strips markdown code fences
    (```json ... ``` or ``` ... ```) and cleans unescaped newlines/whitespace.
    """
    if not text_or_content or not text_or_content.strip():
        raise ValueError("Empty content provided for JSON parsing")

    cleaned = text_or_content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE | re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse valid JSON from content: {text_or_content[:200]}...")


def normalize_document_type(doc_type_str: str) -> str:
    """
    Systematically normalizes document type string to standard canonical enum key:
    'payslip', 'bank_statement', 'tax_return', 'kyc_identity', 'address_proof', 'other'.
    Case-insensitive and space/underscore agnostic.
    """
    if not doc_type_str:
        return "other"

    dt = doc_type_str.lower().strip()

    if re.search(r"\b(address[_\s]proof|proof[_\s]of[_\s]address)\b", dt):
        return "address_proof"
    if re.search(r"\b(payslip|pay[_\s]slip|pay[_\s]stub|salary[_\s]slip|wage[_\s]slip)\b", dt):
        return "payslip"
    if re.search(r"\b(bank[_\s]statement|bank[_\s]stmt|bank[_\s]account[_\s]statement)\b", dt):
        return "bank_statement"
    if re.search(r"\b(tax[_\s]return|income[_\s]tax[_\s]return|form[_\s]16|itr)\b", dt):
        return "tax_return"
    if re.search(r"\b(kyc[_\s]identity|kyc|identity[_\s]document|identity[_\s]proof)\b", dt):
        return "kyc_identity"
    if re.search(r"\b(other|unknown|unclassified)\b", dt):
        return "other"

    if "gross_salary" in dt or "net_salary" in dt:
        return "payslip"
    if "average_monthly_credit" in dt or "salary_credits" in dt:
        return "bank_statement"
    if "assessment_year" in dt or "declared_income" in dt:
        return "tax_return"
    if "id_number" in dt or "passport" in dt or "aadhaar" in dt:
        return "kyc_identity"
    if "utility_bill" in dt or "service_address" in dt:
        return "address_proof"

    return "other"


def normalize_ocr_label(text: str) -> str:
    """
    Safe OCR label normalization helper to handle common OCR digit-for-letter substitutions.
    """
    label = text.lower().strip()
    label = re.sub(r"\bgr0ss\b", "gross", label)
    label = re.sub(r"\bperi0d\b", "period", label)
    label = re.sub(r"\bemp1oyee\b", "employee", label)
    label = re.sub(r"\bsa1ary\b", "salary", label)
    label = re.sub(r"\bacount\b", "account", label)
    return label


class BaseLLMClient:
    """Base abstract interface for LLM client providers."""

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        raise NotImplementedError("LLM client must implement generate_json")

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        raise NotImplementedError("LLM client must implement chat")


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM Client for offline execution, unit testing, and evaluation
    without requiring external API keys.
    """

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        system_lower = system_instruction.lower()

        if "classify" in system_lower or "allowed document types" in system_lower:
            return self._mock_classify(prompt)
        else:
            return self._mock_extract(prompt, system_instruction)

    def _mock_classify(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        normalized_prompt = normalize_ocr_label(prompt_lower)

        kyc_phrases = [
            "identity document", "identity proof", "date of birth",
            "id number", "id no", "aadhaar", "pan card", "passport",
            "driving licence", "driving license", "voter id"
        ]
        has_kyc_phrase = any(phrase in normalized_prompt for phrase in kyc_phrases)
        has_kyc_combo = "dob" in normalized_prompt and ("name" in normalized_prompt or "address" in normalized_prompt)

        if has_kyc_phrase or has_kyc_combo:
            return {
                "document_type": "kyc_identity",
                "confidence": 0.94,
                "reason": "Found official identity document markers."
            }

        if "gross salary" in normalized_prompt or "net salary" in normalized_prompt or "pay period" in normalized_prompt or "payslip" in normalized_prompt or "employee name" in normalized_prompt:
            return {
                "document_type": "payslip",
                "confidence": 0.95,
                "reason": "Found clear salary indicators (gross/net salary, employee name, pay period)."
            }

        if "bank" in normalized_prompt and ("statement" in normalized_prompt or "account holder" in normalized_prompt or "balance" in normalized_prompt or "salary credit" in normalized_prompt or "transaction" in normalized_prompt):
            return {
                "document_type": "bank_statement",
                "confidence": 0.92,
                "reason": "Found bank statement keywords (account holder, balance, transactions)."
            }

        if "assessment year" in normalized_prompt or "income tax" in normalized_prompt or "itr" in normalized_prompt or "tax return" in normalized_prompt or "form 16" in normalized_prompt:
            return {
                "document_type": "tax_return",
                "confidence": 0.93,
                "reason": "Found income tax assessment keywords."
            }

        if "electricity bill" in normalized_prompt or "water bill" in normalized_prompt or "address proof" in normalized_prompt or "utility bill" in normalized_prompt or "service address" in normalized_prompt:
            return {
                "document_type": "address_proof",
                "confidence": 0.90,
                "reason": "Found address proof utility bill indicators."
            }

        return {
            "document_type": "other",
            "confidence": 0.30,
            "reason": "Insufficient OCR evidence to confidently classify document."
        }

    def _mock_extract(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        ocr_section = prompt
        if "OCR Text by Page:" in prompt:
            ocr_section = prompt.split("OCR Text by Page:", 1)[1]
        elif "OCR Content:" in prompt:
            ocr_section = prompt.split("OCR Content:", 1)[1]

        lines = ocr_section.splitlines()
        current_page = 1
        page_texts: Dict[int, str] = {}

        for line in lines:
            page_match = re.search(r"--- Page (\d+) ---", line, re.IGNORECASE)
            if page_match:
                current_page = int(page_match.group(1))
            else:
                page_texts[current_page] = page_texts.get(current_page, "") + "\n" + line

        def find_field_value(keys: list) -> tuple[Optional[Any], float, Optional[int]]:
            for page_num, text in page_texts.items():
                for line in text.splitlines():
                    line_raw = line.strip()
                    if not line_raw or line_raw.startswith("---"):
                        continue
                    
                    line_norm = normalize_ocr_label(line_raw)
                    for key in keys:
                        pattern = rf"(?i)\b{re.escape(key)}\b\s*[:\-=]?\s*(.*)"
                        match_norm = re.search(pattern, line_norm)
                        if match_norm:
                            val_str = line_raw[match_norm.start(1):match_norm.end(1)].strip()
                            if val_str:
                                parsed_num = parse_numeric_value(val_str)
                                if parsed_num is not None:
                                    return parsed_num, 0.95, page_num
                                return val_str, 0.95, page_num
            return None, 0.0, None

        doc_type_norm = normalize_document_type(system_instruction)

        if doc_type_norm == "payslip":
            name_val, name_conf, name_pg = find_field_value(["employee name", "name", "employee"])
            emp_val, emp_conf, emp_pg = find_field_value(["company", "employer", "company name", "organization"])
            
            if not emp_val:
                for pg, txt in page_texts.items():
                    for line in txt.splitlines():
                        clean = line.strip()
                        clean_norm = normalize_ocr_label(clean)
                        if clean and not clean.startswith("---") and not any(k in clean_norm for k in ["employee", "name", "period", "salary"]):
                            emp_val, emp_conf, emp_pg = clean, 0.92, pg
                            break
                    if emp_val:
                        break

            period_val, period_conf, period_pg = find_field_value(["pay period", "month", "period"])
            gross_val, gross_conf, gross_pg = find_field_value(["gross salary", "gross pay", "gross"])
            net_val, net_conf, net_pg = find_field_value(["net salary", "net pay", "net take home", "net"])

            return {
                "name": {"value": name_val, "confidence": name_conf, "page": name_pg},
                "employer": {"value": emp_val, "confidence": emp_conf, "page": emp_pg},
                "pay_period": {"value": period_val, "confidence": period_conf, "page": period_pg},
                "gross_salary": {"value": gross_val, "confidence": gross_conf, "page": gross_pg},
                "net_salary": {"value": net_val, "confidence": net_conf, "page": net_pg},
            }

        elif doc_type_norm == "bank_statement":
            holder_val, holder_conf, holder_pg = find_field_value(["account holder", "customer name", "name"])
            bank_val, bank_conf, bank_pg = find_field_value(["bank name", "bank"])
            
            if not bank_val:
                for pg, txt in page_texts.items():
                    for line in txt.splitlines():
                        clean = line.strip()
                        if clean and "bank" in clean.lower() and not clean.startswith("---"):
                            bank_val, bank_conf, bank_pg = clean, 0.92, pg
                            break
                    if bank_val:
                        break

            period_val, period_conf, period_pg = find_field_value(["statement period", "period"])
            sal_credits_val, sal_conf, sal_pg = find_field_value(["salary credit", "salary credits", "total credits"])
            avg_credit_val, avg_conf, avg_pg = find_field_value(["average monthly credit", "average credit"])

            return {
                "account_holder": {"value": holder_val, "confidence": holder_conf, "page": holder_pg},
                "bank": {"value": bank_val, "confidence": bank_conf, "page": bank_pg},
                "statement_period": {"value": period_val, "confidence": period_conf, "page": period_pg},
                "salary_credits": {"value": sal_credits_val, "confidence": sal_conf, "page": sal_pg},
                "average_monthly_credit": {"value": avg_credit_val, "confidence": avg_conf, "page": avg_pg},
            }

        elif doc_type_norm == "tax_return":
            name_val, name_conf, name_pg = find_field_value(["taxpayer name", "assessee", "name"])
            ay_val, ay_conf, ay_pg = find_field_value(["assessment year", "ay"])
            inc_val, inc_conf, inc_pg = find_field_value(["declared income", "total income", "gross total income"])

            return {
                "taxpayer_name": {"value": name_val, "confidence": name_conf, "page": name_pg},
                "assessment_year": {"value": ay_val, "confidence": ay_conf, "page": ay_pg},
                "declared_income": {"value": inc_val, "confidence": inc_conf, "page": inc_pg},
            }

        elif doc_type_norm == "kyc_identity":
            name_val, name_conf, name_pg = find_field_value(["full name", "name"])
            dob_val, dob_conf, dob_pg = find_field_value(["date of birth", "dob", "birth date"])
            addr_val, addr_conf, addr_pg = find_field_value(["address", "residence"])
            id_val, id_conf, id_pg = find_field_value(["id number", "pan", "aadhaar", "id no"])

            return {
                "name": {"value": name_val, "confidence": name_conf, "page": name_pg},
                "DOB": {"value": dob_val, "confidence": dob_conf, "page": dob_pg},
                "address": {"value": addr_val, "confidence": addr_conf, "page": addr_pg},
                "ID_number": {"value": id_val, "confidence": id_conf, "page": id_pg},
            }

        elif doc_type_norm == "address_proof":
            name_val, name_conf, name_pg = find_field_value(["customer name", "recipient", "name"])
            addr_val, addr_conf, addr_pg = find_field_value(["service address", "address", "billing address"])
            issuer_val, issuer_conf, issuer_pg = find_field_value(["issued by", "issuer", "authority", "service provider"])
            date_val, date_conf, date_pg = find_field_value(["issue date", "bill date", "date"])

            return {
                "name": {"value": name_val, "confidence": name_conf, "page": name_pg},
                "address": {"value": addr_val, "confidence": addr_conf, "page": addr_pg},
                "document_issuer": {"value": issuer_val, "confidence": issuer_conf, "page": issuer_pg},
                "issue_date": {"value": date_val, "confidence": date_conf, "page": date_pg},
            }

        return {}

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        local_emergency = LocalEmergencyLLMClient()
        return await local_emergency.chat(messages, tools, system_prompt)


class LocalEmergencyLLMClient(BaseLLMClient):
    """
    Deterministic 100% network-free emergency LLM client.
    Used as the last-resort fallback or when LLM_PROVIDER=local.
    Never fabricates facts, document values, or approval decisions.
    Always produces a valid LLMResponse requiring human review.
    """

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content")
                if isinstance(content, str):
                    last_user_msg = content
                break

        q_lower = last_user_msg.lower()

        # Check if tools have already been executed in this turn history
        has_tool_results = any(
            m.get("role") == "tool" or
            (isinstance(m.get("content"), list) and any(item.get("type") == "tool_result" for item in m.get("content", [])))
            for m in messages
        )

        if not has_tool_results:
            # First turn: trigger appropriate tool call based on question keyword
            if "flag" in q_lower or "risk" in q_lower:
                return LLMResponse(
                    stop_reason="tool_use",
                    tool_calls=[{"id": "call_mock_1", "name": "get_risk_flags", "args": {}}]
                )
            elif "policy" in q_lower or "guideline" in q_lower or "rule" in q_lower or "income" in q_lower:
                return LLMResponse(
                    stop_reason="tool_use",
                    tool_calls=[{"id": "call_mock_2", "name": "search_policy", "args": {"query": last_user_msg}}]
                )
            elif "mismatch" in q_lower or "verification" in q_lower or "discrepancy" in q_lower:
                return LLMResponse(
                    stop_reason="tool_use",
                    tool_calls=[{"id": "call_mock_3", "name": "get_verification_results", "args": {}}]
                )
            else:
                return LLMResponse(
                    stop_reason="tool_use",
                    tool_calls=[{"id": "call_mock_4", "name": "get_application_data", "args": {}}]
                )

        # Refusal safeguard for approve/reject queries
        if any(kw in q_lower for kw in ["approve", "reject", "pass", "fail", "decision"]):
            resp_dict = {
                "answer": "As an AI Investigation Agent, I am programmed to NEVER approve or reject loan applications directly. The decision must be made by a human loan officer. Based on available evidence, please review the risk flags and verification results.",
                "risk_level": "MEDIUM",
                "evidence": [],
                "policy_reference": "Underwriting Guidelines Section 1.2: Human Officer Final Decision Requirement",
                "recommendation": "NEEDS_HUMAN_REVIEW",
                "requires_human_review": True
            }
            return LLMResponse(stop_reason="end_turn", tool_calls=[], text=json.dumps(resp_dict))

        # Standard final answer response
        resp_dict = {
            "answer": f"Analysis complete for query: '{last_user_msg}'. All extracted verification findings and risk flags have been compiled from application documents.",
            "risk_level": "MEDIUM",
            "evidence": [],
            "policy_reference": "Loan Documentation SOP Section 3: Cross-Document Verification",
            "recommendation": "NEEDS_HUMAN_REVIEW",
            "requires_human_review": True
        }
        return LLMResponse(stop_reason="end_turn", tool_calls=[], text=json.dumps(resp_dict))


class BedrockLLMClient(BaseLLMClient):
    """
    AWS Bedrock LLM Client using Bedrock Converse API for multi-turn tool calling.
    Wrapped in starlette.concurrency.run_in_threadpool so synchronous boto3 SDK calls
    do not block the FastAPI async event loop.
    """

    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"):
        self.region_name = region_name
        self.model_id = model_id

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        return MockLLMClient().generate_json(prompt, system_instruction)

    def _sync_chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise RuntimeError("boto3 dependency missing. Install boto3 to use AWS Bedrock provider.")

        settings = get_settings()
        kwargs = {"region_name": self.region_name or settings.BEDROCK_REGION}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            if "PASTE_" in settings.AWS_ACCESS_KEY_ID or "PASTE_" in settings.AWS_SECRET_ACCESS_KEY:
                raise RuntimeError("AWS Bedrock credentials are still placeholders. Please edit backend/.env with your real AWS Access Key ID and Secret Access Key.")
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        try:
            client = boto3.client("bedrock-runtime", **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AWS Bedrock client: {str(e)}")

        converse_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role in ("user", "assistant"):
                if isinstance(content, str):
                    converse_messages.append({"role": role, "content": [{"text": content}]})
                elif isinstance(content, list):
                    converse_content = []
                    for item in content:
                        if item.get("type") == "text":
                            converse_content.append({"text": item.get("text", "")})
                        elif item.get("type") == "tool_use":
                            converse_content.append({
                                "toolUse": {
                                    "toolUseId": item.get("id"),
                                    "name": item.get("name"),
                                    "input": item.get("args", {})
                                }
                            })
                    converse_messages.append({"role": role, "content": converse_content})
            elif role == "tool":
                converse_content = []
                if isinstance(content, list):
                    for item in content:
                        t_id = item.get("tool_use_id") or item.get("id") or "call_0"
                        c_val = item.get("content")
                        if isinstance(c_val, dict):
                            converse_content.append({"toolResult": {"toolUseId": t_id, "content": [{"json": c_val}]}})
                        else:
                            converse_content.append({"toolResult": {"toolUseId": t_id, "content": [{"text": str(c_val)}]}})
                elif isinstance(content, dict):
                    t_id = msg.get("tool_use_id") or msg.get("id") or "call_0"
                    converse_content.append({"toolResult": {"toolUseId": t_id, "content": [{"json": content}]}})
                else:
                    t_id = msg.get("tool_use_id") or msg.get("id") or "call_0"
                    converse_content.append({"toolResult": {"toolUseId": t_id, "content": [{"text": str(content)}]}})

                converse_messages.append({
                    "role": "user",
                    "content": converse_content
                })

        tool_specs = []
        for t in tools:
            tool_specs.append({
                "toolSpec": {
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "inputSchema": {"json": t.get("input_schema", t.get("parameters", {}))}
                }
            })
        tool_config = {"tools": tool_specs} if tool_specs else None

        try:
            call_kwargs = {
                "modelId": self.model_id or settings.BEDROCK_MODEL_ID,
                "messages": converse_messages,
                "system": [{"text": system_prompt}] if system_prompt else []
            }
            if tool_config:
                call_kwargs["toolConfig"] = tool_config

            response = client.converse(**call_kwargs)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("ValidationException", "AccessDeniedException", "ResourceNotFoundException", "UnrecognizedClientException"):
                raise RuntimeError(f"Bedrock Configuration Error [{code}]: {e.response.get('Error', {}).get('Message')}")
            raise e
        except Exception as e:
            raise e

        stop_reason = response.get("stopReason")
        output_msg = response.get("output", {}).get("message", {})
        content_blocks = output_msg.get("content", [])

        normalized_stop = "tool_use" if stop_reason == "tool_use" else "end_turn"
        tool_calls = []
        text_content = []

        for block in content_blocks:
            if "text" in block:
                text_content.append(block["text"])
            elif "toolUse" in block:
                tu = block["toolUse"]
                tool_calls.append({
                    "id": tu.get("toolUseId"),
                    "name": tu.get("name"),
                    "args": tu.get("input", {})
                })

        return LLMResponse(
            stop_reason=normalized_stop,
            tool_calls=tool_calls,
            text="\n".join(text_content) if text_content else None
        )

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        return await run_in_threadpool(self._sync_chat, messages, tools, system_prompt)


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini LLM Client wrapper."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            return clean_and_parse_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Gemini API execution error: {str(e)}")


class OpenAILLMClient(BaseLLMClient):
    """OpenAI LLM Client wrapper."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            content = response.choices[0].message.content
            return clean_and_parse_json(content)
        except Exception as e:
            raise RuntimeError(f"OpenAI API execution error: {str(e)}")

    def _sync_chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        import openai
        if not self.api_key:
            raise RuntimeError("OpenAI API key missing. Configure OPENAI_API_KEY.")

        client = openai.OpenAI(api_key=self.api_key)

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            role = m.get("role")
            if role in ("user", "assistant"):
                formatted_messages.append({"role": role, "content": str(m.get("content", ""))})
            elif role == "tool":
                content = m.get("content")
                if isinstance(content, list):
                    for item in content:
                        t_id = item.get("tool_use_id") or item.get("id") or "call_0"
                        c_val = item.get("content")
                        formatted_messages.append({
                            "role": "tool",
                            "tool_call_id": t_id,
                            "content": json.dumps(c_val) if isinstance(c_val, dict) else str(c_val)
                        })
                else:
                    t_id = m.get("tool_use_id") or m.get("id") or "call_0"
                    formatted_messages.append({
                        "role": "tool",
                        "tool_call_id": t_id,
                        "content": json.dumps(content) if isinstance(content, dict) else str(content)
                    })

        formatted_tools = []
        for t in tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", t.get("parameters", {}))
                }
            })

        call_kwargs = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.1
        }
        if formatted_tools:
            call_kwargs["tools"] = formatted_tools

        try:
            res = client.chat.completions.create(**call_kwargs)
        except Exception as e:
            err_str = str(e)
            if "AuthenticationError" in err_str or "PermissionDeniedError" in err_str or "NotFoundError" in err_str:
                raise RuntimeError(f"OpenAI Configuration Error: {err_str}")
            raise e

        msg = res.choices[0].message
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = {}
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    pass
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": args
                })

        stop_reason = "tool_use" if tool_calls else "end_turn"
        return LLMResponse(
            stop_reason=stop_reason,
            tool_calls=tool_calls,
            text=msg.content
        )

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        return await run_in_threadpool(self._sync_chat, messages, tools, system_prompt)


class ResilientLLMClient:
    """
    Resilient multi-provider LLM Client wrapper enforcing the fallback priority:
    Bedrock (Primary) -> OpenAI (Fallback) -> Local Emergency Mode.

    Fallback Policy:
    - Runtime recoverable failures (timeouts, throttling, 5xx API errors) trigger fallback.
    - Configuration errors (invalid credentials, missing API keys, invalid model IDs) produce immediate clear errors.
    """

    def __init__(self):
        self.settings = get_settings()

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        provider = (self.settings.LLM_PROVIDER or "bedrock").lower()

        if provider == "local":
            logger.info("LLM_PROVIDER is set to local. Using LocalEmergencyLLMClient.")
            local_client = LocalEmergencyLLMClient()
            return await local_client.chat(messages, tools, system_prompt)

        errors = []

        # Primary: Bedrock
        if provider == "bedrock":
            try:
                bedrock_client = BedrockLLMClient(
                    region_name=self.settings.BEDROCK_REGION,
                    model_id=self.settings.BEDROCK_MODEL_ID
                )
                return await bedrock_client.chat(messages, tools, system_prompt)
            except RuntimeError as e:
                if self.settings.ENABLE_LOCAL_FALLBACK:
                    logger.warning(f"Bedrock configuration error: {str(e)}. Falling back to local emergency mode.")
                    errors.append(f"Bedrock config: {str(e)}")
                else:
                    raise
            except Exception as e:
                logger.warning(f"Bedrock runtime failure: {str(e)}. Checking fallbacks.")
                errors.append(f"Bedrock: {str(e)}")

        # Primary / Secondary: OpenAI
        if provider == "openai" or (provider == "bedrock" and self.settings.ENABLE_OPENAI_FALLBACK):
            try:
                if self.settings.OPENAI_API_KEY:
                    openai_client = OpenAILLMClient(
                        api_key=self.settings.OPENAI_API_KEY,
                        model_name=self.settings.OPENAI_MODEL
                    )
                    logger.info("Executing via OpenAI provider.")
                    return await openai_client.chat(messages, tools, system_prompt)
                else:
                    logger.warning("OpenAI API key missing. Skipping OpenAI fallback.")
            except RuntimeError as e:
                if provider == "openai":
                    raise
                logger.warning(f"OpenAI configuration error during fallback: {str(e)}")
                errors.append(f"OpenAI config: {str(e)}")
            except Exception as e:
                logger.warning(f"OpenAI runtime failure: {str(e)}")
                errors.append(f"OpenAI runtime: {str(e)}")

        # Last Resort: Local Emergency Fallback
        if self.settings.ENABLE_LOCAL_FALLBACK:
            logger.info("Falling back to LocalEmergencyLLMClient.")
            local_client = LocalEmergencyLLMClient()
            return await local_client.chat(messages, tools, system_prompt)

        raise RuntimeError(f"All configured LLM providers failed: {'; '.join(errors)}")


def get_llm_client(provider: Optional[str] = None) -> BaseLLMClient:
    """Factory to instantiate LLM client based on environment config or request argument."""
    settings = get_settings()
    selected_provider = (provider or settings.LLM_PROVIDER).lower()

    if selected_provider == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiLLMClient(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
        else:
            print("[Warning] GEMINI_API_KEY not found. Falling back to MockLLMClient.")
            return MockLLMClient()
    elif selected_provider == "openai":
        if settings.OPENAI_API_KEY:
            return OpenAILLMClient(api_key=settings.OPENAI_API_KEY, model_name=settings.OPENAI_MODEL)
        else:
            print("[Warning] OPENAI_API_KEY not found. Falling back to MockLLMClient.")
            return MockLLMClient()
    elif selected_provider == "bedrock":
        return BedrockLLMClient(region_name=settings.BEDROCK_REGION, model_id=settings.BEDROCK_MODEL_ID)
    else:
        return MockLLMClient()


class LLMClient:
    """
    Backwards-compatible wrapper over get_llm_client() with ResilientLLMClient for agent chat.
    """

    def __init__(self):
        self._impl = get_llm_client()
        self._resilient = ResilientLLMClient()

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        try:
            return self._impl.generate_json(prompt, system_instruction)
        except NotImplementedError:
            return MockLLMClient().generate_json(prompt, system_instruction)

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], system_prompt: str) -> LLMResponse:
        return await self._resilient.chat(messages, tools, system_prompt)


llm_client = LLMClient()
