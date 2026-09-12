"""
Pipeline Router
============================
Triggers the full processing pipeline and checks status.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.pipeline import (
    process_application as pipeline_process_application,
    get_pipeline_status as pipeline_get_status,
)

router = APIRouter(prefix="/applications", tags=["Pipeline"])


@router.post("/{app_id}/process")
async def trigger_pipeline(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger full processing pipeline (OCR → Classification → Extraction → Validation → Verification → Risk)."""
    try:
        return await pipeline_process_application(app_id=app_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution encountered an error: {str(e)}",
        )


@router.get("/{app_id}/pipeline-status")
async def get_pipeline_status(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check real-time pipeline processing progress and document statuses."""
    try:
        return await pipeline_get_status(app_id=app_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve pipeline status: {str(e)}",
        )
