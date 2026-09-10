"""
LLM Client Abstraction
=======================
Unified interface for LLM API calls. Supports OpenAI (GPT-4o / GPT-4o-mini),
Google Gemini, and Mock provider for offline execution and testing.
"""

import json
import re
from typing import Dict, Any, Optional
from config import get_settings
from utils.confidence import parse_numeric_value


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

    # Priority 1: Exact document category phrase matching
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

    # Priority 2: Fallback field keyword signals
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
    Safe OCR label normalization helper to handle common OCR digit-for-letter substitutions
    (e.g., 'gr0ss' -> 'gross', 'emp1oyee' -> 'employee', 'peri0d' -> 'period', 'sa1ary' -> 'salary')
    without modifying extracted field values.
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


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM Client for offline execution, unit testing, and evaluation
    without requiring external API keys. Uses deterministic rules to extract
    structured JSON from OCR text.
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

        # KYC Identity checks (requires clear official ID signals)
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

        # Payslip checks
        if "gross salary" in normalized_prompt or "net salary" in normalized_prompt or "pay period" in normalized_prompt or "payslip" in normalized_prompt or "employee name" in normalized_prompt:
            return {
                "document_type": "payslip",
                "confidence": 0.95,
                "reason": "Found clear salary indicators (gross/net salary, employee name, pay period)."
            }

        # Bank Statement checks
        if "bank" in normalized_prompt and ("statement" in normalized_prompt or "account holder" in normalized_prompt or "balance" in normalized_prompt or "salary credit" in normalized_prompt or "transaction" in normalized_prompt):
            return {
                "document_type": "bank_statement",
                "confidence": 0.92,
                "reason": "Found bank statement keywords (account holder, balance, transactions)."
            }

        # Tax Return checks
        if "assessment year" in normalized_prompt or "income tax" in normalized_prompt or "itr" in normalized_prompt or "tax return" in normalized_prompt or "form 16" in normalized_prompt:
            return {
                "document_type": "tax_return",
                "confidence": 0.93,
                "reason": "Found income tax assessment keywords."
            }

        # Address Proof checks
        if "electricity bill" in normalized_prompt or "water bill" in normalized_prompt or "address proof" in normalized_prompt or "utility bill" in normalized_prompt or "service address" in normalized_prompt:
            return {
                "document_type": "address_proof",
                "confidence": 0.90,
                "reason": "Found address proof utility bill indicators."
            }

        # Unclassifiable / ambiguous documents
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
    else:
        return MockLLMClient()


class LLMClient:
    """
    Backwards-compatible wrapper over get_llm_client().
    """

    def __init__(self):
        self._impl = get_llm_client()

    def generate_json(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        return self._impl.generate_json(prompt, system_instruction)


llm_client = LLMClient()
