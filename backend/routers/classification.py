"""
Classification Router
==================================
LLM-based document type classification.

Canonical Endpoint:
  POST /api/v1/documents/{doc_id}/classify
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.extraction import ClassificationResult, OCRDocumentInput
from services.classification import classify_document as classify_service

router = APIRouter(prefix="/documents", tags=["Classification"])


@router.post("/{doc_id}/classify", response_model=ClassificationResult)
async def classify_document(
    doc_id: str,
    ocr_input: Optional[OCRDocumentInput] = None,
    db: AsyncSession = Depends(get_db),
):
    """Classify a document's type using LLM."""
    return await classify_service(doc_id=doc_id, ocr_input=ocr_input, db=db)
