"""
Risk Schemas
=============
Request/response models for risk scoring and flag endpoints.


Endpoints:
  GET   /api/v1/applications/{id}/flags       → RiskResponse
  POST  /api/v1/applications/{id}/assess-risk  → RiskResponse
"""

from typing import Optional
from pydantic import BaseModel, Field


class Flag(BaseModel):
    """A single risk flag with severity, explanation, and evidence."""
    severity: str = Field(..., description="HIGH | MEDIUM | LOW | PASS")
    reason: str = Field(..., description="Human-readable explanation")
    field: Optional[str] = None           # e.g. "annual_income"
    evidence: str = Field(..., description="e.g. DOC-001 p.1 vs DOC-003 p.2")
    details: Optional[dict] = None        # Additional numeric details


class RiskResponse(BaseModel):
    """Complete risk assessment for an application."""
    application_id: str
    score: float = Field(..., ge=0, le=100, description="Weighted rule-based score")
    level: str = Field(..., description="LOW (0-30) | MEDIUM (31-60) | HIGH (61-100)")
    flags: list[Flag] = []
    recommendation: str = "NEEDS_HUMAN_REVIEW"
    summary: str = ""
