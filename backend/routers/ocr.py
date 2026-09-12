"""
OCR Router
=======================
Trigger OCR processing on uploaded documents.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.ocr import process_document

router = APIRouter(prefix="/documents", tags=["OCR"])


@router.post("/{doc_id}/ocr")
async def trigger_ocr(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger OCR processing for a document."""
    return await process_document(doc_id, db)