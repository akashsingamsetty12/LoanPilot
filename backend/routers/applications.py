"""
Applications Router
==================================
CRUD endpoints for loan applications.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.application import (
    CreateApplicationRequest,
    ApplicationSummary,
    ApplicationDetailResponse,
    ApplicationListResponse,
    DecisionRequest,
)
from services.ingestion import create_application as create_application_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationSummary, status_code=201)
async def create_application(
    request: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new loan application."""
    return await create_application_service(request, db)
    pass


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all applications with optional status filter."""
    # TODO: Implement list with pagination and filtering
    pass


@router.get("/{app_id}", response_model=ApplicationDetailResponse)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full application state for the review dashboard."""
    # TODO: Load application with all related data
    pass


@router.patch("/{app_id}/decide", response_model=ApplicationSummary)
async def decide_application(
    app_id: str,
    request: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record the human officer's final decision."""
    # TODO: Update application with decision, notes, decided_by, decided_at
    pass
