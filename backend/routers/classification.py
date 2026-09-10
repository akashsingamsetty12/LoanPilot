"""
Classification Router
==================================
LLM-based document type classification.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.extraction import ClassificationResult

router = APIRouter(prefix="/documents", tags=["Classification"])


@router.post("/{doc_id}/classify", response_model=ClassificationResult)
async def classify_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Classify a document's type using LLM."""
    # TODO: Call services.classification.classify_document()
    pass
