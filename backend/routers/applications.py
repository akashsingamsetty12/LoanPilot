"""
Applications Router
==================================
CRUD endpoints and underwriter decisions for loan applications.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.application import Application
from models.document import Document
from schemas.application import (
    CreateApplicationRequest,
    ApplicationSummary,
    ApplicationDetailResponse,
    ApplicationListResponse,
    DecisionRequest,
)
from services.ingestion import create_application as ingestion_create_application

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationSummary, status_code=201)
async def create_application(
    request: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new loan application."""
    return await ingestion_create_application(request, db)


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    status: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """List all applications with optional status filter and pagination."""
    # Base query
    query = select(Application)
    count_query = select(func.count(Application.id))

    if status:
        query = query.where(Application.status == status.lower())
        count_query = count_query.where(Application.status == status.lower())

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination and sorting (newest first)
    offset = (page - 1) * limit
    query = (
        query.options(selectinload(Application.documents))
        .order_by(Application.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    applications = result.scalars().all()

    # Map to summaries
    summaries = [
        ApplicationSummary(
            id=app.id,
            applicant_name=app.applicant_name,
            status=app.status,
            document_count=len(app.documents) if app.documents else 0,
            risk_level=app.risk_level,
            recommendation=app.recommendation,
            created_at=app.created_at,
        )
        for app in applications
    ]

    return ApplicationListResponse(applications=summaries, total=total)


@router.get("/{app_id}", response_model=ApplicationDetailResponse)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full application state for the review dashboard."""
    query = (
        select(Application)
        .options(
            selectinload(Application.documents),
            selectinload(Application.verification),
            selectinload(Application.risk_assessment),
        )
        .where(Application.id == app_id)
    )

    result = await db.execute(query)
    app = result.scalar_one_or_none()

    if app is None:
        raise HTTPException(
            status_code=404,
            detail=f"Application not found: {app_id}",
        )

    # Format documents
    doc_list = []
    for doc in app.documents or []:
        doc_list.append(
            {
                "document_id": doc.id,
                "application_id": doc.application_id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "doc_type": doc.doc_type or "unclassified",
                "status": doc.status,
                "pages": doc.pages,
                "ocr_confidence": doc.ocr_confidence,
                "classification_confidence": doc.classification_confidence,
                "extracted_fields": doc.extracted_fields,
                "error_message": doc.error_message,
                "created_at": doc.created_at,
            }
        )

    # Format verification
    verification_data = None
    if app.verification:
        verification_data = {
            "application_id": app.id,
            "overall_status": app.verification.overall_status,
            "confidence_score": app.verification.confidence_score,
            "matches": app.verification.matches or [],
            "mismatches": app.verification.mismatches or [],
            "missing_documents": app.verification.missing_documents or [],
            "field_validations": app.verification.field_validations or [],
            "verified_at": app.verification.verified_at,
        }

    # Format risk
    risk_data = None
    if app.risk_assessment:
        risk_data = {
            "application_id": app.id,
            "risk_score": app.risk_assessment.risk_score,
            "risk_level": app.risk_assessment.risk_level,
            "recommendation": app.risk_assessment.recommendation,
            "confidence_score": app.risk_assessment.confidence_score,
            "flags": app.risk_assessment.flags or [],
            "evidence": app.risk_assessment.evidence or [],
            "assessed_at": app.risk_assessment.assessed_at,
        }

    return ApplicationDetailResponse(
        id=app.id,
        applicant_name=app.applicant_name,
        status=app.status,
        documents=doc_list,
        verification=verification_data,
        risk=risk_data,
        recommendation=app.recommendation,
        decision=app.decision,
        decision_notes=app.decision_notes,
        decided_by=app.decided_by,
        decided_at=app.decided_at,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


@router.patch("/{app_id}/decide", response_model=ApplicationSummary)
@router.post("/{app_id}/decide", response_model=ApplicationSummary)
async def decide_application(
    app_id: str,
    request: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record the human officer's final decision on an application."""
    normalized_decision = request.decision.strip().lower()
    valid_decisions = {"approved", "rejected", "needs_more_info"}

    if normalized_decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid decision '{request.decision}'. "
                f"Must be one of: {', '.join(sorted(valid_decisions))}"
            ),
        )

    result = await db.execute(
        select(Application)
        .options(selectinload(Application.documents))
        .where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()

    if app is None:
        raise HTTPException(
            status_code=404,
            detail=f"Application not found: {app_id}",
        )

    app.decision = normalized_decision
    app.decision_notes = request.notes
    app.decided_by = request.decided_by or "underwriter"
    app.decided_at = datetime.now(timezone.utc)
    app.status = "decided"
    app.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(app)

    return ApplicationSummary(
        id=app.id,
        applicant_name=app.applicant_name,
        status=app.status,
        document_count=len(app.documents) if app.documents else 0,
        risk_level=app.risk_level,
        recommendation=app.recommendation,
        created_at=app.created_at,
    )
