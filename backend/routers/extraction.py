"""
Extraction Router
==============================
LLM-based structured field extraction.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.extraction import ExtractionResult

router = APIRouter(prefix="/documents", tags=["Extraction"])


@router.post("/{doc_id}/extract", response_model=ExtractionResult)
async def extract_fields(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Extract structured fields from a document via LLM."""
    # TODO: Call services.extraction.extract_fields()
    pass
