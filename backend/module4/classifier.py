from typing import Optional
from module4.schemas import OCRDocumentInput, ClassificationResult, DocumentType
from module4.prompts import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT_TEMPLATE
from module4.llm_client import BaseLLMClient, get_llm_client, normalize_document_type


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
        # Combine text across all pages with explicit page markers
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
