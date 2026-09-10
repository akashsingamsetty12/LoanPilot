"""
Documents Router
=============================
Upload and status tracking endpoints for loan documents.

"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from schemas.common import StatusResponse

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
    # TODO: Call services.ingestion.upload_document() for each file
    pass


@router.get("/applications/{app_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List all documents for an application."""
    # TODO: Call services.ingestion.list_documents()
    pass


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a single document."""
    # TODO: Fetch document from DB
    pass


@router.get("/documents/{doc_id}/status", response_model=StatusResponse)
async def get_document_status(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check processing status of a document."""
    # TODO: Call services.ingestion.get_document_status()
    pass
