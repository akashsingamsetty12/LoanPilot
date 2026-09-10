"""
Validation Router
==============================
Within-document validation checks (deterministic).

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.verification import ValidationResponse

router = APIRouter(prefix="/applications", tags=["Validation"])


@router.post("/{app_id}/validate", response_model=ValidationResponse)
async def validate_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run within-document validation for all docs in an application."""
    # TODO: Call services.validation.validate_application()
    pass
