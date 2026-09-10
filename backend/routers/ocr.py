"""
OCR Router
=======================
Trigger OCR processing on uploaded documents.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/documents", tags=["OCR"])


@router.post("/{doc_id}/ocr")
async def trigger_ocr(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger OCR processing for a document."""
    # TODO: Call services.ocr.process_document()
    pass
