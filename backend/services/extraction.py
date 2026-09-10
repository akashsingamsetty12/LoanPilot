"""
Information Extraction Service
==========================================
Extracts structured fields from document text using LLM prompts.
Each field is tagged with value, confidence, page, and source document.


Data flow:
  Raw text + doc_type → LLM extraction → canonical structured JSON

Expected fields per doc_type:
  payslip:        name, employer, pay_period, gross_salary, net_salary, deductions
  bank_statement: account_holder, bank_name, statement_period, salary_credits,
                  avg_monthly_credit, closing_balance
  tax_return:     taxpayer_name, pan_number, assessment_year, declared_income, tax_paid
  kyc_identity:   name, dob, id_type, id_number, address
  address_proof:  name, address, document_type, issue_date

RULE: Handle low-confidence extractions by flagging them for review, NOT guessing.

Input:  Document.raw_text and Document.doc_type
Output: Document.extracted_fields updated as JSON with per-field evidence
"""

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.extraction import ExtractionResult


async def extract_fields(doc_id: str, db: AsyncSession) -> ExtractionResult:
    """
    Extract structured fields from a document using LLM.

    Steps:
      1. Load Document.raw_text and Document.doc_type from DB
      2. Build type-specific LLM prompt (see field lists in docstring above)
      3. Instruct LLM to return structured JSON with:
         {"field_name": {"value": ..., "confidence": 0.0-1.0, "page": N}}
      4. Call LLM via utils/llm_client.py
      5. Parse response, add source_document to each field
      6. If any field confidence < 0.7, flag it for review
      7. Store in Document.extracted_fields
      8. Update Document.status = "extracted"
      9. Return ExtractionResult

    TODO: implement extraction prompts for each doc_type
    """
    raise NotImplementedError("extract_fields() is not implemented")
