"""
Information Extraction Service
==========================================
Extracts structured fields from document text using LLM prompts.
Each field is tagged with value, confidence, page, and needs_review.

Data flow:
  Raw text + doc_type → LLM extraction → canonical structured JSON

Expected fields per doc_type:
  payslip:        name, employer, pay_period, gross_salary, net_salary
  bank_statement: account_holder, bank, statement_period, salary_credits, average_monthly_credit
  tax_return:     taxpayer_name, assessment_year, declared_income
  kyc_identity:   name, DOB, address, ID_number
  address_proof:  name, address, document_issuer, issue_date

RULE: Handle low-confidence extractions by flagging them for review, NOT guessing.
"""

from typing import Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.extraction import OCRDocumentInput, OCRPage, ExtractionResult, DocumentType, ExtractedField
from utils.prompts import EXTRACTION_SYSTEM_PROMPTS, EXTRACTION_USER_PROMPT_TEMPLATE
from utils.llm_client import BaseLLMClient, get_llm_client, normalize_document_type
from utils.confidence import process_fields_confidence
from services.classification import classify_document


class DocumentExtractor:
    """
    LLM prompt-based information extraction module.
    Extracts canonical structured fields for a classified document type.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_llm_client()

    def extract(self, ocr_input: OCRDocumentInput, document_type: Union[DocumentType, str]) -> ExtractionResult:
        """
        Extracts document-specific fields based on document_type.
        """
        raw_doc_type = document_type.value if isinstance(document_type, DocumentType) else str(document_type)
        norm_doc_type = normalize_document_type(raw_doc_type)

        # Handle 'other' document type: no specific extractions required
        if norm_doc_type == DocumentType.OTHER.value or norm_doc_type not in EXTRACTION_SYSTEM_PROMPTS:
            return ExtractionResult(
                document_id=ocr_input.document_id,
                document_type=DocumentType(norm_doc_type),
                type=DocumentType(norm_doc_type),
                filename=ocr_input.filename,
                ocr_confidence=ocr_input.ocr_confidence,
                fields={}
            )

        system_instruction = EXTRACTION_SYSTEM_PROMPTS[norm_doc_type]

        # Combine text across all pages
        ocr_text_combined = "\n\n".join([
            f"--- Page {p.page} ---\n{p.text}" for p in ocr_input.pages
        ])

        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            document_type=norm_doc_type,
            document_id=ocr_input.document_id,
            filename=ocr_input.filename or "unknown",
            ocr_text=ocr_text_combined
        )

        try:
            raw_response = self.llm_client.generate_json(
                prompt=user_prompt,
                system_instruction=system_instruction
            )
            processed_fields = process_fields_confidence(raw_response)

        except Exception as err:
            print(f"[Warning] Extraction LLM call failed: {err}")
            processed_fields = {}

        return ExtractionResult(
            document_id=ocr_input.document_id,
            document_type=DocumentType(norm_doc_type),
            type=DocumentType(norm_doc_type),
            filename=ocr_input.filename,
            ocr_confidence=ocr_input.ocr_confidence,
            fields=processed_fields
        )


async def extract_fields(
    doc_id: str,
    ocr_input: Optional[OCRDocumentInput] = None,
    document_type: Optional[Union[DocumentType, str]] = None,
    db: Optional[AsyncSession] = None,
    llm_client: Optional[BaseLLMClient] = None,
) -> ExtractionResult:
    """
    Extract structured fields from a document using LLM.
    If document_type is not provided, auto-classifies first.
    """
    extractor = DocumentExtractor(llm_client=llm_client)

    if ocr_input is None:
        raw_text = ""
        filename = "unknown"
        if db is not None:
            try:
                from models.document import Document
                from sqlalchemy import select
                result = await db.execute(select(Document).where(Document.id == doc_id))
                doc = result.scalar_one_or_none()
                if doc:
                    raw_text = doc.raw_text or ""
                    filename = doc.filename or "unknown"
                    if not document_type and doc.doc_type:
                        document_type = doc.doc_type
            except Exception:
                pass

        ocr_input = OCRDocumentInput(
            document_id=doc_id,
            filename=filename,
            pages=[OCRPage(page=1, text=raw_text, ocr_confidence=1.0)]
        )

    if ocr_input.document_id != doc_id:
        ocr_input.document_id = doc_id

    if not document_type:
        class_res = await classify_document(doc_id=doc_id, ocr_input=ocr_input, db=db, llm_client=llm_client)
        document_type = class_res.document_type

    res = extractor.extract(ocr_input, document_type=document_type)

    # Optional DB update if db session and Document record exist
    if db is not None:
        try:
            from models.document import Document
            from sqlalchemy import select
            result = await db.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if doc:
                doc.extracted_fields = {k: v.model_dump() for k, v in res.fields.items()}
                doc.status = "extracted"
                await db.commit()
        except Exception:
            pass

    return res


async def process_document(
    ocr_input: OCRDocumentInput,
    llm_client: Optional[BaseLLMClient] = None,
) -> ExtractionResult:
    """Unified workflow: Classify document -> Extract structured fields."""
    class_res = await classify_document(doc_id=ocr_input.document_id, ocr_input=ocr_input, llm_client=llm_client)
    return await extract_fields(
        doc_id=ocr_input.document_id,
        ocr_input=ocr_input,
        document_type=class_res.document_type,
        llm_client=llm_client
    )
