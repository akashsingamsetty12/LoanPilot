"""
Document Ingestion Service
=======================================
Handles application creation, file upload,
validation, storage, and document metadata.
"""

from datetime import datetime, timezone
from pathlib import Path

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
    # Collision-safe application ID generation
    app_id = generate_application_id()
    while (await db.execute(select(Application.id).where(Application.id == app_id))).scalar_one_or_none():
        app_id = generate_application_id()

    application = Application(
        id=app_id,
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
    """Upload and register a single loan document."""

    # Check application exists
    result = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if application is None:
        raise ValueError(f"Application not found: {app_id}")

    # Validate file type
    if not file.content_type or not validate_file_type(file.content_type):
        raise ValueError("Unsupported file type. Use PDF, JPG, JPEG or PNG.")

    # Read file
    content = await file.read()

    # Validate file size
    if not validate_file_size(len(content)):
        raise ValueError("File size exceeds the allowed limit.")

    target_filename = file.filename or "document"

    # Check if a document with this filename already exists for this application
    existing_result = await db.execute(
        select(Document).where(
            Document.application_id == app_id,
            Document.filename == target_filename,
        )
    )
    existing_doc = existing_result.scalars().first()

    if existing_doc is not None:
        upload_path = Path(existing_doc.file_path) if existing_doc.file_path else get_upload_path(app_id, existing_doc.id, target_filename)
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(content)

        existing_doc.file_path = str(upload_path)
        existing_doc.file_size = len(content)
        existing_doc.file_type = file.content_type
        existing_doc.status = "uploaded"
        existing_doc.created_at = datetime.now(timezone.utc)

        application.status = "documents_uploaded"
        application.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_doc)

        return DocumentUploadResponse(
            document_id=existing_doc.id,
            filename=existing_doc.filename,
            file_type=existing_doc.file_type,
            status=existing_doc.status,
        )

    # Generate document ID
    doc_id = generate_document_id()
    while (await db.execute(select(Document.id).where(Document.id == doc_id))).scalar_one_or_none():
        doc_id = generate_document_id()

    # Generate upload path
    upload_path = get_upload_path(
        app_id,
        doc_id,
        target_filename,
    )
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Save file
    upload_path.write_bytes(content)

    # Create database record
    document = Document(
        id=doc_id,
        application_id=app_id,
        filename=target_filename,
        file_path=str(upload_path),
        file_type=file.content_type,
        file_size=len(content),
        status="uploaded",
        doc_type="unclassified",
        created_at=datetime.now(timezone.utc),
    )

    db.add(document)

    # Update application status
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
        .order_by(Document.created_at.desc())
    )
    docs = list(result.scalars().all())
    seen = set()
    unique_docs = []
    for doc in docs:
        fn = doc.filename or doc.id
        if fn not in seen:
            seen.add(fn)
            unique_docs.append(doc)
    unique_docs.reverse()
    return unique_docs
