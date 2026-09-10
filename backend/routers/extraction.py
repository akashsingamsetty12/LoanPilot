"""
Extraction Router
==============================
LLM-based structured field extraction.

Canonical Endpoints:
  POST /api/v1/documents/{doc_id}/extract
  POST /api/v1/documents/process
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.extraction import ExtractionResult, OCRDocumentInput
from services.extraction import extract_fields as extract_service, process_document as process_service

router = APIRouter(prefix="/documents", tags=["Extraction"])


@router.post("/process", response_model=ExtractionResult)
async def process_document(
    ocr_input: OCRDocumentInput,
    db: AsyncSession = Depends(get_db),
):
    """Classify and extract fields in a single step."""
    return await process_service(ocr_input=ocr_input)


@router.post("/{doc_id}/extract", response_model=ExtractionResult)
async def extract_fields(
    doc_id: str,
    ocr_input: Optional[OCRDocumentInput] = None,
    document_type: Optional[str] = Query(default=None, description="Optional document type override"),
    db: AsyncSession = Depends(get_db),
):
    """Extract structured fields from a document via LLM."""
    return await extract_service(doc_id=doc_id, ocr_input=ocr_input, document_type=document_type, db=db)
