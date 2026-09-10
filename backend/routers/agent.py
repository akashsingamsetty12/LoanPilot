"""
Agent Router
=========================
"Ask LoanPilot" chatbot endpoint.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.agent import AgentQueryRequest, AgentQueryResponse

router = APIRouter(prefix="/applications", tags=["Agent"])


@router.post("/{app_id}/agent/query", response_model=AgentQueryResponse)
async def query_agent(
    app_id: str,
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Ask LoanPilot a question about an application."""
    # TODO: Call services.agent.query_agent()
    pass
