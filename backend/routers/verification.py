"""
Verification Router
================================
Cross-document consistency verification checks.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.verification import VerificationResponse

router = APIRouter(prefix="/applications", tags=["Verification"])


@router.post("/{app_id}/verify", response_model=VerificationResponse)
async def verify_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run cross-document verification for an application."""
    # TODO: Call services.verification.verify_application()
    pass
