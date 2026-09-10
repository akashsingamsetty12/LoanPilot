"""
Risk Router
========================
Risk scoring and flag endpoints.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.risk import RiskResponse

router = APIRouter(prefix="/applications", tags=["Risk"])


@router.get("/{app_id}/flags", response_model=RiskResponse)
async def get_flags(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get risk score and prioritized flags for an application."""
    # TODO: Load RiskAssessment from DB
    pass


@router.post("/{app_id}/assess-risk", response_model=RiskResponse)
async def assess_risk(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger risk assessment for an application."""
    # TODO: Call services.risk_engine.assess_risk()
    pass
