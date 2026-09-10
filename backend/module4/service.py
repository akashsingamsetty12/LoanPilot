from typing import Optional, Union
from module4.schemas import OCRDocumentInput, ClassificationResult, ExtractionResult, DocumentType
from module4.classifier import DocumentClassifier
from module4.extractor import DocumentExtractor
from module4.llm_client import BaseLLMClient, get_llm_client


class DocumentProcessorService:
    """
    High-level service orchestrator for Module 4.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_llm_client()
        self.classifier = DocumentClassifier(llm_client=self.llm_client)
        self.extractor = DocumentExtractor(llm_client=self.llm_client)

    def classify_document(self, ocr_input: OCRDocumentInput) -> ClassificationResult:
        """Runs LLM prompt classification on supplied OCR text."""
        return self.classifier.classify(ocr_input)

    def extract_document(self, ocr_input: OCRDocumentInput, document_type: Optional[Union[DocumentType, str]] = None) -> ExtractionResult:
        """
        Runs LLM field extraction on supplied OCR text.
        If document_type is not specified, classifies the document first.
        """
        if not document_type:
            class_res = self.classify_document(ocr_input)
            document_type = class_res.document_type

        return self.extractor.extract(ocr_input, document_type=document_type)

    def process_document(self, ocr_input: OCRDocumentInput) -> ExtractionResult:
        """Unified workflow: Classify document -> Extract structured fields."""
        classification = self.classify_document(ocr_input)
        return self.extractor.extract(ocr_input, document_type=classification.document_type)
