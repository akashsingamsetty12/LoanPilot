"""
Agent Router
=========================
"Ask LoanPilot" AI Investigation Agent endpoints.

Cognizant Explainability Note:
- Endpoint Alignment: Supports both POST /applications/{app_id}/agent (spec requirement)
  and POST /applications/{app_id}/agent/query (existing router path) via the SAME async run_agent() function.
- Session Injection: Uses FastAPI's Depends(get_db) dependency to inject the AsyncSession into the orchestrator.
- HTTP Exception Handling: Verifies application existence and returns clean HTTP 404 error if app is missing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.application import Application
from schemas.agent import AgentQueryRequest, AgentResponse
from services.agent import run_agent

router = APIRouter(prefix="/applications", tags=["Agent"])


@router.post("/{app_id}/agent", response_model=AgentResponse)
async def query_agent_endpoint(
    app_id: str,
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Primary AI Investigation Agent endpoint.
    Accepts natural language question, runs multi-turn tool orchestration loop,
    and returns evidence-backed AgentResponse with reasoning trace.
    """
    stmt = select(Application).where(Application.id == app_id)
    res = await db.execute(stmt)
    app = res.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{app_id}' not found."
        )

    return await run_agent(app_id, request.question, db)


@router.post("/{app_id}/agent/query", response_model=AgentResponse)
async def query_agent_alias_endpoint(
    app_id: str,
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Alias endpoint pointing to the exact same run_agent() orchestrator.
    Maintains 100% backward compatibility with existing frontend API calls.
    """
    return await query_agent_endpoint(app_id, request, db)
