"""
Report Router
==========================
Report generation and download endpoints.

"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.agent import ReportResponse

router = APIRouter(prefix="/applications", tags=["Report"])


@router.get("/{app_id}/report", response_model=ReportResponse)
async def get_report(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the generated verification report."""
    # TODO: Call services.report.get_report()
    pass


@router.post("/{app_id}/report/generate", response_model=ReportResponse)
async def generate_report(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger report generation."""
    # TODO: Call services.report.generate_report()
    pass


@router.get("/{app_id}/report/download")
async def download_report(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download the report as PDF."""
    # TODO: Return FileResponse for the generated PDF
    pass
