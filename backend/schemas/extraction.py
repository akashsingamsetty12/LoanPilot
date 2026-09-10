"""
Extraction & Classification Schemas
=====================================
Request/response models for document classification and field extraction.


Endpoints:
  POST  /api/v1/documents/{id}/classify  → ClassificationResult
  POST  /api/v1/documents/{id}/extract   → ExtractionResult
"""

from typing import Optional
from pydantic import BaseModel, Field

from schemas.common import FieldValue


class ClassificationResult(BaseModel):
    """Result of LLM-based document classification."""
    document_id: str
    doc_type: str = Field(
        ...,
        description="payslip | bank_statement | tax_return | kyc_identity | address_proof | other",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class ExtractionResult(BaseModel):
    """
    Structured fields extracted from a document via LLM.

    Expected field keys per doc_type:
      payslip:        name, employer, pay_period, gross_salary, net_salary, deductions
      bank_statement: account_holder, bank_name, statement_period, salary_credits,
                      avg_monthly_credit, closing_balance
      tax_return:     taxpayer_name, pan_number, assessment_year, declared_income, tax_paid
      kyc_identity:   name, dob, id_type, id_number, address
      address_proof:  name, address, document_type, issue_date
    """
    document_id: str
    doc_type: str
    fields: dict[str, FieldValue]
