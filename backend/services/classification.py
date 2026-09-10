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
        If evidence is insufficient, defaults to DocumentType.OTHER.
        """
        ocr_text_combined = "\n\n".join([
            f"--- Page {p.page} ---\n{p.text}" for p in ocr_input.pages
        ])

        user_prompt = CLASSIFICATION_USER_PROMPT_TEMPLATE.format(
            document_id=ocr_input.document_id,
            filename=ocr_input.filename or "unknown",
            ocr_text=ocr_text_combined
        )

        try:
            raw_response = self.llm_client.generate_json(
                prompt=user_prompt,
                system_instruction=CLASSIFICATION_SYSTEM_PROMPT
            )

            raw_doc_type = str(raw_response.get("document_type", "other")).strip()
            norm_doc_type = normalize_document_type(raw_doc_type)
            confidence = float(raw_response.get("confidence", 0.0))
            reason = str(raw_response.get("reason", "No detailed rationale provided."))

            return ClassificationResult(
                document_id=ocr_input.document_id,
                document_type=DocumentType(norm_doc_type),
                confidence=round(confidence, 4),
                reason=reason
            )

        except Exception as err:
            return ClassificationResult(
                document_id=ocr_input.document_id,
                document_type=DocumentType.OTHER,
                confidence=0.0,
                reason=f"Classification failed with error: {str(err)}. Defaulted to 'other'."
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
            except Exception:
                pass

        ocr_input = OCRDocumentInput(
            document_id=doc_id,
            filename=filename,
            pages=[OCRPage(page=1, text=raw_text, ocr_confidence=1.0)]
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
