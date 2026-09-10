import json
from module4.schemas import OCRDocumentInput
from module4.service import DocumentProcessorService

# Load sample OCR JSON input from prompt specification
sample_input = {
  "document_id": "DOC-001",
  "filename": "payslip.pdf",
  "pages": [
    {
      "page": 1,
      "text": "HORIZON TECH PRIVATE LIMITED\nEmployee Name: Rahul Kumar\nPay Period: August 2026\nGross Salary: 90000\nNet Salary: 72000",
      "ocr_confidence": 0.94
    }
  ]
}

ocr_doc = OCRDocumentInput(**sample_input)
service = DocumentProcessorService()

print("--- 1. CLASSIFICATION RESULT ---")
classification = service.classify_document(ocr_doc)
print(json.dumps(classification.model_dump(), indent=2))

print("\n--- 2. EXTRACTION RESULT ---")
extraction = service.extract_document(ocr_doc)
print(json.dumps(extraction.model_dump(), indent=2))
