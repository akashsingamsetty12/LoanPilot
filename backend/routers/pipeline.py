"""
Pipeline Router
============================
Triggers the full processing pipeline and checks status.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/applications", tags=["Pipeline"])


@router.post("/{app_id}/process")
async def trigger_pipeline(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger full processing pipeline (Modules 3→4→5→6)."""
    # TODO: Call services.pipeline.process_application()
    pass


@router.get("/{app_id}/pipeline-status")
async def get_pipeline_status(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check pipeline processing progress."""
    # TODO: Call services.pipeline.get_pipeline_status()
    pass
