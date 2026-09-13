"""Module 6 request/response schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class Flag(BaseModel):
    severity: str = Field(..., description="HIGH | MEDIUM | LOW | PASS")
    reason: str
    field: Optional[str] = None
    evidence: str
    details: Optional[dict] = None


class RiskResponse(BaseModel):
    application_id: str
    score: float = Field(..., ge=0, le=100)
    level: str
    flags: list[Flag] = Field(default_factory=list)
    recommendation: str = "NEEDS_HUMAN_REVIEW"
    summary: str = ""
