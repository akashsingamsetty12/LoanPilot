import json
import os
import pytest
from module4.schemas import OCRDocumentInput, DocumentType
from module4.classifier import DocumentClassifier
from module4.llm_client import MockLLMClient


@pytest.fixture
def sample_payslip_input():
    json_path = os.path.join(os.path.dirname(__file__), "sample_ocr.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return OCRDocumentInput(**data)


def test_classify_payslip(sample_payslip_input):
    classifier = DocumentClassifier(llm_client=MockLLMClient())
    result = classifier.classify(sample_payslip_input)

    assert result.document_id == "DOC-001"
    assert result.document_type == DocumentType.PAYSLIP
    assert result.confidence >= 0.70
    assert "salary" in result.reason.lower() or "payslip" in result.reason.lower() or "employee" in result.reason.lower()


def test_classify_bank_statement():
    classifier = DocumentClassifier(llm_client=MockLLMClient())
    input_data = OCRDocumentInput(
        document_id="DOC-002",
        filename="bank_stmt.pdf",
        pages=[{
            "page": 1,
            "text": "STATE BANK OF INDIA\nAccount Number: 123456789\nBalance: 150000\nStatement Period: 01-Aug-2026 to 31-Aug-2026\nTransactions...",
            "ocr_confidence": 0.96
        }]
    )
    result = classifier.classify(input_data)
    assert result.document_type == DocumentType.BANK_STATEMENT
    assert result.confidence >= 0.70


def test_classify_tax_return():
    classifier = DocumentClassifier(llm_client=MockLLMClient())
    input_data = OCRDocumentInput(
        document_id="DOC-003",
        filename="itr.pdf",
        pages=[{
            "page": 1,
            "text": "INCOME TAX DEPARTMENT\nForm 16 / ITR\nAssessment Year: 2026-27\nTaxpayer Name: Rahul Kumar\nTotal Income: 1080000",
            "ocr_confidence": 0.95
        }]
    )
    result = classifier.classify(input_data)
    assert result.document_type == DocumentType.TAX_RETURN
    assert result.confidence >= 0.70


def test_classify_insufficient_evidence_defaults_to_other():
    classifier = DocumentClassifier(llm_client=MockLLMClient())
    input_data = OCRDocumentInput(
        document_id="DOC-004",
        filename="random.pdf",
        pages=[{
            "page": 1,
            "text": "Hello world random text page with no financial or identity markers.",
            "ocr_confidence": 0.90
        }]
    )
    result = classifier.classify(input_data)
    assert result.document_type == DocumentType.OTHER
    assert result.confidence < 0.70
