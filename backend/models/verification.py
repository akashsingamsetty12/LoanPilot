"""
Verification Result Model
==========================
Stores cross-document verification results for a loan application.

"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class VerificationResult(Base):
    """Cross-document verification results for an application."""

    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(20), ForeignKey("applications.id"), unique=True, nullable=False)

    # Verification outcomes
    matches = Column(JSON, nullable=True)
    # format: ["name_consistency", "employer_consistency", ...]

    mismatches = Column(JSON, nullable=True)
    # format: [{"field": "annual_income", "sources": ["payslip", "tax_return"],
    #           "values": [900000, 780000], "difference": 120000,
    #           "evidence": "DOC-001 p.1 vs DOC-003 p.2", "severity": "HIGH"}, ...]

    missing_documents = Column(JSON, nullable=True)
    # format: ["address_proof", ...]

    # Completeness tracking
    documents_required = Column(JSON, nullable=True)
    # format: ["payslip", "bank_statement", "tax_return", "kyc_identity"]

    documents_present = Column(JSON, nullable=True)
    # format: ["payslip", "bank_statement", "tax_return"]

    is_complete = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    application = relationship("Application", back_populates="verification")

    def __repr__(self) -> str:
        return f"<VerificationResult(app={self.application_id}, complete={self.is_complete})>"
