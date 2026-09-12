"""
Validation Router
==============================
Within-document validation checks (deterministic).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.verification import ValidationResponse
from services.validation import validate_application as run_validation


router = APIRouter(
    prefix="/applications",
    tags=["Validation"],
)


@router.post(
    "/{app_id}/validate",
    response_model=ValidationResponse,
)
async def validate_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run within-document validation for all docs in an application."""

    return await run_validation(
        app_id=app_id,
        db=db,
    )