import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from schemas.agent import ReportResponse
from services.report import generate_report as run_generate_report, get_report as run_get_report

router = APIRouter(prefix="/applications", tags=["Report"])


@router.get("/{app_id}/report", response_model=ReportResponse)
async def get_report(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Spec API Contract: Get the generated verification report."""
    try:
        return await run_get_report(app_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch report: {str(e)}")


@router.post("/{app_id}/report/generate", response_model=ReportResponse)
async def generate_report_endpoint(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger report generation."""
    try:
        return await run_generate_report(app_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.get("/{app_id}/report/download")
@router.get("/{app_id}/report/pdf")
async def download_report(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download the report as official PDF verification dossier."""
    settings = get_settings()
    pdf_file = os.path.join(settings.UPLOAD_DIR, app_id, "reports", f"report_{app_id}.pdf")
    if not os.path.exists(pdf_file):
        await run_generate_report(app_id, db)

    if os.path.exists(pdf_file):
        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename=f"LoanPilot_Report_{app_id}.pdf"
        )

    # Fallback to HTML if PDF is not available
    html_file = os.path.join(settings.UPLOAD_DIR, app_id, "reports", f"report_{app_id}.html")
    if os.path.exists(html_file):
        return FileResponse(
            html_file,
            media_type="text/html",
            filename=f"LoanPilot_Report_{app_id}.html"
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file could not be generated.")


