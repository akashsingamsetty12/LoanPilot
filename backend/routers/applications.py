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
from services.ingestion import create_application as create_application_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationSummary, status_code=201)
async def create_application(
    request: CreateApplicationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new loan application."""
    return await create_application_service(request, db)


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
            document_count=len(set(doc.filename for doc in app.documents)) if app.documents else 0,
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

    # Format documents (deduplicating by filename to keep latest)
    doc_list = []
    seen_filenames = set()
    sorted_docs = sorted(
        app.documents or [],
        key=lambda d: d.created_at or datetime.min,
        reverse=True,
    )
    for doc in sorted_docs:
        fn = doc.filename or doc.id
        if fn in seen_filenames:
            continue
        seen_filenames.add(fn)
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
    doc_list.reverse()

    # Format verification
    verification_data = None
    if app.verification:
        verification_data = {
            "application_id": app.id,
            "overall_status": getattr(app.verification, "overall_status", "verified" if getattr(app.verification, "is_complete", False) else "flagged" if getattr(app.verification, "mismatches", None) else "processing"),
            "confidence_score": getattr(app.verification, "confidence_score", 0.95),
            "matches": app.verification.matches or [],
            "mismatches": app.verification.mismatches or [],
            "missing_documents": app.verification.missing_documents or [],
            "documents_required": getattr(app.verification, "documents_required", []) or [],
            "documents_present": getattr(app.verification, "documents_present", []) or [],
            "is_complete": getattr(app.verification, "is_complete", False),
            "field_validations": getattr(app.verification, "field_validations", []) or [],
            "verified_at": getattr(app.verification, "verified_at", getattr(app.verification, "created_at", None)),
        }

    # Format risk
    risk_data = None
    if app.risk_assessment:
        score_val = getattr(app.risk_assessment, "score", app.risk_score or 0.0)
        level_val = getattr(app.risk_assessment, "level", app.risk_level or "LOW")
        risk_data = {
            "application_id": app.id,
            "score": score_val,
            "level": level_val,
            "risk_score": score_val,
            "risk_level": level_val,
            "recommendation": getattr(app.risk_assessment, "recommendation", app.recommendation or "NEEDS_HUMAN_REVIEW"),
            "summary": getattr(app.risk_assessment, "summary", None),
            "confidence_score": getattr(app.risk_assessment, "confidence_score", 0.90),
            "flags": getattr(app.risk_assessment, "flags", []) or [],
            "evidence": getattr(app.risk_assessment, "evidence", []) or [],
            "assessed_at": getattr(app.risk_assessment, "created_at", None),
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
    if normalized_decision == "approved":
        app.status = "completed"
    elif normalized_decision == "rejected":
        app.status = "rejected"
    elif normalized_decision == "needs_more_info":
        app.status = "review"
    else:
        app.status = "completed"
    app.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(app)

    return ApplicationSummary(
        id=app.id,
        applicant_name=app.applicant_name,
        status=app.decision if app.decision in ("approved", "rejected") else app.status,
        document_count=len(app.documents) if app.documents else 0,
        risk_level=app.risk_level,
        recommendation=app.recommendation,
        created_at=app.created_at,
    )
