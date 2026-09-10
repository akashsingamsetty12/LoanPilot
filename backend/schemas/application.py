"""
Application Schemas
====================
Request/response models for application endpoints.

Endpoints:
  POST   /api/v1/applications              → CreateApplicationRequest → ApplicationSummary
  GET    /api/v1/applications               → ApplicationListResponse
  GET    /api/v1/applications/{id}          → ApplicationDetailResponse
  PATCH  /api/v1/applications/{id}/decide   → DecisionRequest → ApplicationSummary
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class CreateApplicationRequest(BaseModel):
    """Request body for creating a new loan application."""
    applicant_name: str = Field(..., min_length=1, max_length=255)
    kaggle_loan_id: Optional[str] = None


class ApplicationSummary(BaseModel):
    """Summary view of an application (used in list views and responses)."""
    id: str
    applicant_name: str
    status: str
    document_count: int = 0
    risk_level: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationDetailResponse(BaseModel):
    """
    Full application state — used by the review dashboard.
    Assembles data from all modules into one response.
    """
    id: str
    applicant_name: str
    status: str
    documents: list[Any] = []           # list[DocumentResponse] — avoids circular import
    verification: Optional[Any] = None  # VerificationResponse
    risk: Optional[Any] = None          # RiskResponse
    recommendation: Optional[str] = None
    decision: Optional[str] = None
    decision_notes: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""
    applications: list[ApplicationSummary]
    total: int


class DecisionRequest(BaseModel):
    """Request body for the human officer's final decision."""
    decision: str = Field(..., description="approved | rejected | needs_more_info")
    notes: Optional[str] = None
    decided_by: Optional[str] = None
