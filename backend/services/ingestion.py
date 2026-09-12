"""
Document Ingestion Service
=======================================
Handles file upload validation, storage, status tracking, and metadata creation.

Data flow:
  Upload → validate file → generate IDs → save to disk → create DB record → ready for OCR
"""

from datetime import datetime, timezone
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.application import Application
from models.document import Document
from schemas.application import CreateApplicationRequest, ApplicationSummary
from schemas.document import DocumentUploadResponse
from utils.file_helpers import (
    validate_file_type,
    validate_file_size,
    get_upload_path,
)
from utils.id_generator import generate_application_id, generate_document_id


async def create_application(
    request: CreateApplicationRequest,
    db: AsyncSession,
) -> ApplicationSummary:
    """Create a new loan application."""
    application = Application(
        id=generate_application_id(),
        applicant_name=request.applicant_name,
        kaggle_loan_id=request.kaggle_loan_id,
        status="created",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return ApplicationSummary(
        id=application.id,
        applicant_name=application.applicant_name,
        status=application.status,
        document_count=0,
        risk_level=application.risk_level,
        recommendation=application.recommendation,
        created_at=application.created_at,
    )


async def upload_document(
    app_id: str,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentUploadResponse:
    """Upload and store a single document for a loan application."""
    result = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if application is None:
        raise ValueError(f"Application not found: {app_id}")

    if not file.content_type or not validate_file_type(file.content_type):
        raise ValueError("Unsupported file type. Use PDF, JPG, JPEG or PNG.")

    content = await file.read()

    if not validate_file_size(len(content)):
        raise ValueError("File size exceeds the allowed limit.")

    doc_id = generate_document_id()
    upload_path = get_upload_path(
        app_id,
        doc_id,
        file.filename or "document",
    )
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(content)

    document = Document(
        id=doc_id,
        application_id=app_id,
        filename=file.filename or "document",
        file_path=str(upload_path),
        file_type=file.content_type,
        file_size=len(content),
        status="uploaded",
        doc_type="unclassified",
        created_at=datetime.now(timezone.utc),
    )

    db.add(document)

    application.status = "documents_uploaded"
    application.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(document)

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        status=document.status,
    )


async def get_document_status(doc_id: str, db: AsyncSession) -> dict:
    """Get the processing status of a document."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError(f"Document not found: {doc_id}")

    return {
        "document_id": document.id,
        "status": document.status,
        "error_message": document.error_message,
    }


async def list_documents(app_id: str, db: AsyncSession) -> list:
    """List all documents for an application."""
    result = await db.execute(
        select(Document)
        .where(Document.application_id == app_id)
        .order_by(Document.created_at)
    )
    return list(result.scalars().all())
