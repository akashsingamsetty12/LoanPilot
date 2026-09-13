"""
Documents Router
=============================
Upload and status tracking endpoints for loan documents.
"""

import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_settings

from database import get_db
from schemas.document import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
)
from schemas.common import StatusResponse
from services.ingestion import (
    upload_document,
    list_documents,
    get_document_status,
)
from models.document import Document
from sqlalchemy import select


router = APIRouter(tags=["Documents"])


@router.post(
    "/applications/{app_id}/documents",
    response_model=list[DocumentUploadResponse],
    status_code=201,
)
async def upload_documents(
    app_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or more documents for a loan application."""

    try:
        uploaded_documents = []

        for file in files:
            result = await upload_document(app_id, file, db)
            uploaded_documents.append(result)

        return uploaded_documents

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/applications/{app_id}/documents",
    response_model=DocumentListResponse,
)
async def list_documents_endpoint(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List all documents for an application."""

    documents = await list_documents(app_id, db)

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                document_id=document.id,
                application_id=document.application_id,
                filename=document.filename,
                file_type=document.file_type,
                file_size=document.file_size,
                doc_type=document.doc_type,
                status=document.status,
                pages=document.pages,
                ocr_confidence=document.ocr_confidence,
                classification_confidence=document.classification_confidence,
                extracted_fields=document.extracted_fields,
                error_message=document.error_message,
                created_at=document.created_at,
            )
            for document in documents
        ],
        total=len(documents),
    )


@router.get(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a single document."""

    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {doc_id}",
        )

    return DocumentResponse(
        document_id=document.id,
        application_id=document.application_id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        doc_type=document.doc_type,
        status=document.status,
        pages=document.pages,
        ocr_confidence=document.ocr_confidence,
        classification_confidence=document.classification_confidence,
        extracted_fields=document.extracted_fields,
        error_message=document.error_message,
        created_at=document.created_at,
    )


@router.get(
    "/documents/{doc_id}/status",
    response_model=StatusResponse,
)
async def get_document_status_endpoint(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check processing status of a document."""

    try:
        result = await get_document_status(doc_id, db)

        return {
            "status": result["status"],
            "message": result.get("message") or result.get("error_message") or "Document status retrieved successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{doc_id}/file")
async def get_document_file_endpoint(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve the raw document file (PDF or image) for in-browser preview or download."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")

    settings = get_settings()
    target_path = None
    candidates = [
        document.file_path,
        os.path.join(settings.UPLOAD_DIR, document.application_id, document.id, document.filename) if document.application_id and document.filename else None,
        os.path.join("uploads", document.application_id, document.id, document.filename) if document.application_id and document.filename else None,
        os.path.join("/app/uploads", document.application_id, document.id, document.filename) if document.application_id and document.filename else None,
    ]
    for c in candidates:
        if c and os.path.exists(c):
            target_path = c
            break

    if not target_path:
        raise HTTPException(status_code=404, detail=f"Document file not found on disk for {doc_id}")

    import mimetypes
    media_type = document.file_type
    if not media_type or media_type == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(target_path)
        media_type = guessed or "application/octet-stream"

    return FileResponse(
        path=target_path,
        media_type=media_type,
        content_disposition_type="inline",
        filename=document.filename,
    )