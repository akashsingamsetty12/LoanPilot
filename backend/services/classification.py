"""
Document Classification Service
============================================
Identifies each document's type using LLM classification prompt.

GOLDEN RULE: Use ONE well-designed LLM prompt, not a custom ML classifier.

Data flow:
  Raw text → LLM classification → doc_type + confidence

Supported types:
  payslip | bank_statement | tax_return | kyc_identity | address_proof | other
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.extraction import OCRDocumentInput, OCRPage, ClassificationResult, DocumentType
from utils.prompts import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT_TEMPLATE
from utils.llm_client import BaseLLMClient, get_llm_client, normalize_document_type


class DocumentClassifier:
    """
    LLM prompt-based document classifier module.
    Classifies supplied OCR text into canonical categories.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_llm_client()

    def classify(self, ocr_input: OCRDocumentInput) -> ClassificationResult:
        """
        Classifies OCR text into document category.
        If evidence is insufficient or LLM providers fail, defaults to DocumentType.OTHER.
        """
        ocr_text_combined = "\n\n".join([
            f"--- Page {p.page} ---\n{p.text}" for p in ocr_input.pages
        ])

        user_prompt = CLASSIFICATION_USER_PROMPT_TEMPLATE.format(
            document_id=ocr_input.document_id,
            filename=ocr_input.filename or "unknown",
            ocr_text=ocr_text_combined
        )

        from config import get_settings
        settings = get_settings()

        if hasattr(self.llm_client, "generate_with_fallback"):
            fallback_res = self.llm_client.generate_with_fallback(
                prompt=user_prompt,
                system_instruction=CLASSIFICATION_SYSTEM_PROMPT
            )
        else:
            try:
                raw = self.llm_client.generate_json(
                    prompt=user_prompt,
                    system_instruction=CLASSIFICATION_SYSTEM_PROMPT
                )
                from utils.llm_client import LLMFallbackResult
                fallback_res = LLMFallbackResult(
                    data=raw,
                    provider_used=getattr(self.llm_client, "provider_name", "mock"),
                    fallback_used=False,
                    attempt_count=1,
                    needs_review=False,
                    error=None
                )
            except Exception as err:
                from utils.llm_client import LLMFallbackResult
                fallback_res = LLMFallbackResult(
                    data={},
                    provider_used=None,
                    fallback_used=True,
                    attempt_count=1,
                    needs_review=True,
                    error=str(err)
                )

        if fallback_res.provider_used is None or fallback_res.error:
            return ClassificationResult(
                document_id=ocr_input.document_id,
                document_type=DocumentType.OTHER,
                confidence=0.0,
                reason=fallback_res.error or "Document classification failed",
                provider_used=None,
                fallback_used=True,
                attempt_count=fallback_res.attempt_count,
                needs_review=True,
                error=fallback_res.error or "Document classification failed"
            )

        raw_response = fallback_res.data
        raw_doc_type = str(raw_response.get("document_type", "other")).strip()
        norm_doc_type = normalize_document_type(raw_doc_type)
        confidence = float(raw_response.get("confidence", 0.0))
        reason = str(raw_response.get("reason", "No detailed rationale provided."))

        needs_review = (confidence < settings.CONFIDENCE_THRESHOLD)

        return ClassificationResult(
            document_id=ocr_input.document_id,
            document_type=DocumentType(norm_doc_type),
            confidence=round(confidence, 4),
            reason=reason,
            provider_used=fallback_res.provider_used,
            fallback_used=fallback_res.fallback_used,
            attempt_count=fallback_res.attempt_count,
            needs_review=needs_review,
            error=None
        )



async def classify_document(
    doc_id: str,
    ocr_input: Optional[OCRDocumentInput] = None,
    db: Optional[AsyncSession] = None,
    llm_client: Optional[BaseLLMClient] = None,
) -> ClassificationResult:
    """
    Classify a document's type using LLM. Accepts either an explicit OCRDocumentInput
    or fetches document raw text from database if ocr_input is not provided.
    """
    classifier = DocumentClassifier(llm_client=llm_client)

    if ocr_input is None:
        filename = "unknown"
        pages = []
        if db is not None:
            try:
                from models.document import Document
                from sqlalchemy import select
                result = await db.execute(select(Document).where(Document.id == doc_id))
                doc = result.scalar_one_or_none()
                if doc:
                    filename = doc.filename or "unknown"
                    if isinstance(doc.raw_text, list):
                        for p in doc.raw_text:
                            if isinstance(p, dict):
                                pages.append(
                                    OCRPage(
                                        page=p.get("page", 1),
                                        text=str(p.get("text", "")),
                                        ocr_confidence=float(p.get("confidence", 1.0)),
                                    )
                                )
                            elif isinstance(p, str):
                                pages.append(OCRPage(page=len(pages) + 1, text=p, ocr_confidence=1.0))
                    elif isinstance(doc.raw_text, str) and doc.raw_text.strip():
                        pages.append(OCRPage(page=1, text=doc.raw_text, ocr_confidence=1.0))
            except Exception:
                pass

        if not pages:
            pages = [OCRPage(page=1, text="", ocr_confidence=1.0)]

        ocr_input = OCRDocumentInput(
            document_id=doc_id,
            filename=filename,
            pages=pages,
        )

    if ocr_input.document_id != doc_id:
        ocr_input.document_id = doc_id

    res = classifier.classify(ocr_input)

    # Optional DB update if db session and Document record exist
    if db is not None:
        try:
            from models.document import Document
            from sqlalchemy import select
            result = await db.execute(select(Document).where(Document.id == doc_id))
            doc = result.scalar_one_or_none()
            if doc:
                doc.doc_type = res.document_type.value
                doc.classification_confidence = res.confidence
                doc.status = "classified"
                await db.commit()
        except Exception:
            pass

    return res
