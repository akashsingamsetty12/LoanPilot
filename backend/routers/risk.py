from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.risk import RiskResponse
from services.risk_engine import build_risk_response, get_risk_assessment, assess_risk as run_assess_risk

router = APIRouter(prefix="/applications", tags=["Risk"])


@router.get("/{app_id}/flags", response_model=RiskResponse)
async def get_flags(app_id: str, db: AsyncSession = Depends(get_db)):
    """Spec API contract: Get risk score and prioritized flags with evidence."""
    return await get_risk_assessment(app_id, db)


@router.post("/{app_id}/risk", response_model=RiskResponse)
async def calculate_risk_endpoint(app_id: str, db: AsyncSession = Depends(get_db)):
    """Run/refresh risk assessment for an application."""
    return await run_assess_risk(app_id, db)


@router.post("/{app_id}/assess-risk", response_model=RiskResponse)
async def assess_risk_custom(app_id: str, verification_result: dict):
    """Receive verification JSON directly and return risk assessment."""
    return build_risk_response(app_id, verification_result)

