from typing import Optional, Union
from module4.schemas import OCRDocumentInput, ExtractionResult, DocumentType, ExtractedField
from module4.prompts import EXTRACTION_SYSTEM_PROMPTS, EXTRACTION_USER_PROMPT_TEMPLATE
from module4.llm_client import BaseLLMClient, get_llm_client, normalize_document_type
from module4.confidence import process_fields_confidence


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
