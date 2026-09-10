from typing import Optional
from fastapi import APIRouter, Query
from module4.schemas import OCRDocumentInput, ClassificationResult, ExtractionResult, DocumentType
from module4.service import DocumentProcessorService
from module4.config import settings

router = APIRouter(tags=["Module 4 — Document Classification & Extraction"])
service = DocumentProcessorService()


@router.get("/health", summary="Health check endpoint")
def health_check():
    """Returns status and active LLM configuration."""
    return {
        "status": "healthy",
        "module": "Module 4 - Document Classification & Information Extraction",
        "active_llm_provider": settings.LLM_PROVIDER,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD
    }


@router.post(
    "/documents/{id}/classify",
    response_model=ClassificationResult,
    summary="Classify document type using OCR text"
)
def classify_document(
    id: str,
    ocr_input: OCRDocumentInput
) -> ClassificationResult:
    """
    Classifies OCR text into canonical categories:
    payslip, bank_statement, tax_return, kyc_identity, address_proof, other.
    """
    if ocr_input.document_id != id:
        ocr_input.document_id = id

    return service.classify_document(ocr_input)


@router.post(
    "/documents/{id}/extract",
    response_model=ExtractionResult,
    summary="Extract canonical fields from document OCR text"
)
def extract_document(
    id: str,
    ocr_input: OCRDocumentInput,
    document_type: Optional[str] = Query(
        default=None,
        description="Optional document type override (e.g. payslip, bank_statement, tax_return, kyc_identity, address_proof, other)"
    )
) -> ExtractionResult:
    """
    Extracts structured key-value fields with confidence scores and page locations.
    If document_type is not provided, auto-classifies the document first.
    """
    if ocr_input.document_id != id:
        ocr_input.document_id = id

    return service.extract_document(ocr_input, document_type=document_type)


@router.post(
    "/documents/process",
    response_model=ExtractionResult,
    summary="Classify and extract fields in a single step"
)
def process_document(
    ocr_input: OCRDocumentInput
) -> ExtractionResult:
    """
    Unified endpoint: Accepts raw OCR input, classifies document type,
    and extracts canonical fields.
    """
    return service.process_document(ocr_input)
