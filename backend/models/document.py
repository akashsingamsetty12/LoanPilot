"""
Document Model
===============
Represents an uploaded document (PDF/image) within a loan application.
Tracks OCR processing, classification, and field extraction state.

"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from utils.id_generator import generate_document_id


class Document(Base):
    """A single uploaded document belonging to a loan application."""

    __tablename__ = "documents"

    id = Column(String(20), primary_key=True, default=generate_document_id)
    application_id = Column(String(20), ForeignKey("applications.id"), nullable=False)

    # File metadata
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)   # MIME: application/pdf, image/jpeg, image/png
    file_size = Column(Integer, nullable=False)       # bytes

    # Processing status
    # Valid statuses: uploaded, ocr_processing, ocr_complete, classifying,
    #   classified, extracting, extracted, failed
    status = Column(String(50), nullable=False, default="uploaded")
    error_message = Column(Text, nullable=True)

    # OCR output
    pages = Column(Integer, nullable=True)
    ocr_confidence = Column(Float, nullable=True)      # 0.0-1.0 average
    raw_text = Column(JSON, nullable=True)
    # raw_text format: [{"page": 1, "text": "...", "confidence": 0.94}, ...]

    # Classification
    # Valid types: payslip, bank_statement, tax_return, kyc_identity, address_proof, other, unclassified
    doc_type = Column(String(50), nullable=False, default="unclassified")
    classification_confidence = Column(Float, nullable=True)

    # Extraction
    extracted_fields = Column(JSON, nullable=True)
    # extracted_fields format: {"name": {"value": "...", "confidence": 0.97, "page": 1}, ...}

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    application = relationship("Application", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.doc_type}, status={self.status})>"
