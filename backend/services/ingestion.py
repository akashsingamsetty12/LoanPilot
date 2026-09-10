"""
Document Ingestion Service
=======================================
Handles file upload validation, storage, status tracking, and metadata creation.


Data flow:
  Upload → validate file → generate IDs → save to disk → create DB record → push to OCR queue

Dependencies:
  - utils/file_helpers.py (file validation, path generation)
  - utils/id_generator.py (APP/DOC ID generation)
  - models/application.py, models/document.py

Input:  UploadFile from FastAPI
Output: Document record in DB with status="uploaded"
"""

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.application import CreateApplicationRequest, ApplicationSummary
from schemas.document import DocumentUploadResponse


async def create_application(
    request: CreateApplicationRequest,
    db: AsyncSession,
) -> ApplicationSummary:
    """
    Create a new loan application.

    Steps:
      1. Generate application ID (APP-XXXX)
      2. Create Application record in DB
      3. Return ApplicationSummary

    TODO: implement this
    """
    raise NotImplementedError("create_application() is not implemented")


async def upload_document(
    app_id: str,
    file: UploadFile,
    db: AsyncSession,
) -> DocumentUploadResponse:
    """
    Upload a single document for a loan application.

    Steps:
      1. Validate file type (PDF/JPG/PNG) using utils/file_helpers.validate_file_type()
      2. Validate file size using utils/file_helpers.validate_file_size()
      3. Generate document ID (DOC-XXXX)
      4. Save file to disk: uploads/{app_id}/{doc_id}/{filename}
      5. Create Document record in DB with status="uploaded"
      6. Return DocumentUploadResponse

    TODO: implement this
    """
    raise NotImplementedError("upload_document() is not implemented")


async def get_document_status(doc_id: str, db: AsyncSession) -> dict:
    """
    Get the processing status of a document.

    TODO: implement this
    """
    raise NotImplementedError("get_document_status() is not implemented")


async def list_documents(app_id: str, db: AsyncSession) -> list:
    """
    List all documents for an application.

    TODO: implement this
    """
    raise NotImplementedError("list_documents() is not implemented")
