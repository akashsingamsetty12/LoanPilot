"""
Common Schemas
===============
Shared Pydantic models used across multiple schema modules.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class EvidenceSource(BaseModel):
    """Points to a specific location in a source document."""
    document_id: str = Field(..., description="Document ID, e.g. DOC-0001")
    page: int = Field(..., description="1-indexed page number")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR/extraction confidence")


class FieldValue(BaseModel):
    """A single extracted field with its value, confidence, and source evidence."""
    value: Any = Field(..., description="The extracted value (str, int, or float)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    page: int = Field(..., description="Source page number (1-indexed)")
    source_document: str = Field(..., description="Source document ID, e.g. DOC-0001")


class StatusResponse(BaseModel):
    """Generic status response for pipeline operations."""
    status: str
    message: str
