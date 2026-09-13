"""Module 6 risk API routes."""
from fastapi import APIRouter
from schemas.risk import RiskResponse
from services.risk_engine import build_risk_response

router = APIRouter(prefix="/applications", tags=["Risk"])


@router.post("/{app_id}/assess-risk", response_model=RiskResponse)
async def assess_risk(app_id: str, verification_result: dict):
    """Receive Module 5 verification JSON and return risk assessment."""
    return build_risk_response(app_id, verification_result)
