"""
Agent & Report Schemas
=======================
Request/response models for AI agent chat and report generation.

Cognizant Explainability Note:
- EvidenceItem: Structured evidence snippet linking back to document ID, page, and exact extracted value.
- TraceStep: Recorded step in the agent's multi-turn thought process showing tool called, input args, and result summary.
- AgentResponse: Final output returned to the frontend UI, containing the answer, evidence items, policy references, recommendation, human review flag, and step-by-step reasoning trace.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """User question to the 'Ask LoanPilot' chatbot."""
    question: str = Field(..., min_length=1, description="Natural language question")
    conversation_id: Optional[str] = None  # For multi-turn chat


class EvidenceItem(BaseModel):
    """Specific document evidence supporting a factual finding."""
    document: str = Field(..., description="Source document ID or filename, e.g., DOC-0001")
    page: int = Field(1, description="Page number where evidence was located")
    value: str = Field(..., description="Extracted value or text snippet")


class TraceStep(BaseModel):
    """Execution step recorded during agent tool orchestration."""
    step: int = Field(..., description="1-indexed step number")
    tool: str = Field(..., description="Name of tool executed")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments supplied to tool")
    summary: str = Field(..., description="Human-readable result summary")


class AgentResponse(BaseModel):
    """Structured response returned by the AI Investigation Agent."""
    answer: str = Field(..., description="Evidence-backed answer to user query")
    risk_level: Optional[str] = Field(None, description="Assessed risk level: LOW | MEDIUM | HIGH")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting document evidence items")
    policy_reference: Optional[str] = Field(None, description="Relevant lending policy passage cited")
    recommendation: Optional[str] = Field(None, description="Suggested action, e.g., NEEDS_HUMAN_REVIEW")
    requires_human_review: bool = Field(True, description="Always True for human-in-the-loop compliance")
    trace: List[TraceStep] = Field(default_factory=list, description="Step-by-step agent reasoning trace")


class AgentQueryResponse(BaseModel):
    """Backward-compatible agent response model."""
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
