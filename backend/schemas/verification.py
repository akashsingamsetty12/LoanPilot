"""
Verification Schemas
=====================
Request/response models for cross-document verification.


Endpoints:
  POST  /api/v1/applications/{id}/validate  → ValidationResponse
  POST  /api/v1/applications/{id}/verify    → VerificationResponse
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """A single within-document validation error."""
    document_id: str
    field: str
    error_type: str   # missing_required | invalid_format | out_of_range
    message: str
    severity: str = "MEDIUM"  # HIGH | MEDIUM | LOW


class ValidationResponse(BaseModel):
    """Result of within-document validation checks (deterministic)."""
    application_id: str
    valid: bool
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []


class MismatchDetail(BaseModel):
    """A single cross-document mismatch with evidence."""
    field: str                              # e.g. "annual_income"
    sources: list[str]                      # e.g. ["payslip", "tax_return"]
    values: list[Any]                       # e.g. [900000, 780000]
    difference: Optional[float] = None      # e.g. 120000
    evidence: str                           # e.g. "DOC-001 p.1 vs DOC-003 p.2"
    severity: str                           # HIGH | MEDIUM | LOW


class VerificationResponse(BaseModel):
    """Result of cross-document verification checks (deterministic + fuzzy match)."""
    application_id: str
    matches: list[str] = []                 # e.g. ["name_consistency", "employer_consistency"]
    mismatches: list[MismatchDetail] = []
    missing_documents: list[str] = []       # e.g. ["address_proof"]
    documents_required: list[str] = []
    documents_present: list[str] = []
    is_complete: bool = False
    cross_check_summary: dict[str, str] = {}  # e.g. {"name": "MATCH", "income": "MISMATCH"}
