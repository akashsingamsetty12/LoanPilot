"""
Risk Assessment Model
======================
Stores risk scoring results and flags for a loan application.

"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class RiskAssessment(Base):
    """Risk assessment results with scored flags and evidence."""

    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(20), ForeignKey("applications.id"), unique=True, nullable=False)

    # Risk score (transparent, rule-based — NOT black-box ML)
    score = Column(Float, nullable=False, default=0.0)       # 0-100
    level = Column(String(10), nullable=False, default="LOW") # LOW (0-30) | MEDIUM (31-60) | HIGH (61-100)

    # Flags with severity and evidence
    flags = Column(JSON, nullable=True)
    # format: [{"severity": "HIGH", "reason": "Income discrepancy...",
    #           "field": "annual_income", "evidence": "DOC-001 p.1 vs DOC-003 p.2",
    #           "details": {"payslip_value": 900000, "tax_value": 780000, "difference": 120000}}, ...]

    # Recommendation (NEVER auto-approve or auto-reject)
    recommendation = Column(String(50), nullable=False, default="NEEDS_HUMAN_REVIEW")
    summary = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    application = relationship("Application", back_populates="risk_assessment")

    def __repr__(self) -> str:
        return f"<RiskAssessment(app={self.application_id}, score={self.score}, level={self.level})>"
