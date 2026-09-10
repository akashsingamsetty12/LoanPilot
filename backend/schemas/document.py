"""
Document Schemas
=================
Request/response models for document upload and status endpoints.

Endpoints:
  POST  /api/v1/applications/{id}/documents  → list[DocumentUploadResponse]
  GET   /api/v1/applications/{id}/documents   → DocumentListResponse
  GET   /api/v1/documents/{id}                → DocumentResponse
  GET   /api/v1/documents/{id}/status         → StatusResponse
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

from schemas.common import FieldValue


class DocumentUploadResponse(BaseModel):
    """Response after a document is uploaded successfully."""
    document_id: str
    filename: str
    file_type: str
    status: str = "uploaded"


class DocumentResponse(BaseModel):
    """Full document details including extracted data."""
    document_id: str
    application_id: str
    filename: str
    file_type: str
    file_size: int
    doc_type: str                                      # payslip | bank_statement | etc.
    status: str
    pages: Optional[int] = None
    ocr_confidence: Optional[float] = None
    classification_confidence: Optional[float] = None
    extracted_fields: Optional[dict[str, FieldValue]] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """List of documents for an application."""
    documents: list[DocumentResponse]
    total: int
