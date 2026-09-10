"""
Application Model
==================
Represents a loan application with its lifecycle status,
risk assessment results, and human officer decisions.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import relationship

from database import Base
from utils.id_generator import generate_application_id


class Application(Base):
    """A loan application submitted for document verification."""

    __tablename__ = "applications"

    id = Column(String(20), primary_key=True, default=generate_application_id)
    applicant_name = Column(String(255), nullable=False)

    # Processing lifecycle
    # Valid statuses: created, documents_uploaded, processing, ocr_complete,
    #   classified, extracted, validated, verified, flagged, review, decided
    status = Column(String(50), nullable=False, default="created")

    # Risk assessment
    risk_score = Column(Float, nullable=True)           # 0-100
    risk_level = Column(String(10), nullable=True)      # LOW | MEDIUM | HIGH
    recommendation = Column(String(50), nullable=True)  # NEEDS_HUMAN_REVIEW | LOW_RISK | HIGH_RISK_REVIEW_REQUIRED

    # Human officer decision (set via PATCH /applications/{id}/decide)
    decision = Column(String(50), nullable=True)        # approved | rejected | needs_more_info
    decision_notes = Column(Text, nullable=True)
    decided_by = Column(String(255), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)

    # Kaggle dataset linkage (optional — for tracing back to source data)
    kaggle_loan_id = Column(String(50), nullable=True)
    income_annum = Column(Float, nullable=True)
    loan_amount = Column(Float, nullable=True)
    loan_term = Column(Integer, nullable=True)
    cibil_score = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    documents = relationship(
        "Document", back_populates="application", cascade="all, delete-orphan"
    )
    verification = relationship(
        "VerificationResult", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
    risk_assessment = relationship(
        "RiskAssessment", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, applicant={self.applicant_name}, status={self.status})>"
