"""
Agent & Report Schemas
=======================
Request/response models for AI agent chat and report generation.


Endpoints:
  POST  /api/v1/applications/{id}/agent/query      → AgentQueryRequest → AgentQueryResponse
  GET   /api/v1/applications/{id}/report            → ReportResponse
  POST  /api/v1/applications/{id}/report/generate   → ReportResponse
  GET   /api/v1/applications/{id}/report/download   → FileResponse (PDF)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """User question to the 'Ask LoanPilot' chatbot."""
    question: str = Field(..., min_length=1, description="Natural language question")
    conversation_id: Optional[str] = None  # For multi-turn chat


class AgentQueryResponse(BaseModel):
    """Agent response with evidence-backed answer."""
    answer: str
    evidence: list[str] = []             # e.g. ["DOC-001 p.1", "DOC-003 p.2"]
    sources: list[str] = []              # e.g. ["payslip", "tax_return"]
    follow_up_questions: list[str] = []  # Suggested next questions


class ReportResponse(BaseModel):
    """Generated loan verification report."""
    application_id: str
    report_html: str
    report_url: Optional[str] = None     # URL to download PDF
    generated_at: datetime
    sections: list[str] = [
        "applicant_info",
        "document_summary",
        "verification",
        "flags",
        "recommendation",
    ]
