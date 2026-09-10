import json
import os
import pytest
from module4.schemas import OCRDocumentInput, DocumentType
from module4.extractor import DocumentExtractor
from module4.llm_client import MockLLMClient


@pytest.fixture
def sample_payslip_input():
    json_path = os.path.join(os.path.dirname(__file__), "sample_ocr.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return OCRDocumentInput(**data)


def test_extract_payslip_fields(sample_payslip_input):
    extractor = DocumentExtractor(llm_client=MockLLMClient())
    result = extractor.extract(sample_payslip_input, document_type=DocumentType.PAYSLIP)

    assert result.document_id == "DOC-001"
    assert result.document_type == DocumentType.PAYSLIP
    assert result.filename == "payslip.pdf"
    assert result.ocr_confidence == 0.94

    fields = result.fields
    assert "name" in fields
    assert fields["name"].value == "Rahul Kumar"
    assert fields["name"].page == 1
    assert fields["name"].confidence >= 0.70
    assert fields["name"].needs_review is False

    assert "employer" in fields
    assert fields["employer"].value == "HORIZON TECH PRIVATE LIMITED"
    assert fields["employer"].page == 1

    assert "pay_period" in fields
    assert fields["pay_period"].value == "August 2026"

    assert "gross_salary" in fields
    assert float(fields["gross_salary"].value) == 90000.0

    assert "net_salary" in fields
    assert float(fields["net_salary"].value) == 72000.0


def test_extract_missing_fields_flags_needs_review():
    extractor = DocumentExtractor(llm_client=MockLLMClient())
    incomplete_input = OCRDocumentInput(
        document_id="DOC-999",
        filename="incomplete_payslip.pdf",
        pages=[{
            "page": 1,
            "text": "Employee Name: Rahul Kumar\nPay Period: August 2026",
            "ocr_confidence": 0.85
        }]
    )
    result = extractor.extract(incomplete_input, document_type=DocumentType.PAYSLIP)
    fields = result.fields

    # gross_salary and net_salary are missing, so value should be None and needs_review True
    assert fields["gross_salary"].value is None
    assert fields["gross_salary"].confidence == 0.0
    assert fields["gross_salary"].needs_review is True


def test_extract_other_document_type():
    extractor = DocumentExtractor(llm_client=MockLLMClient())
    other_input = OCRDocumentInput(
        document_id="DOC-888",
        filename="other.pdf",
        pages=[{
            "page": 1,
            "text": "Some unclassifiable text page",
            "ocr_confidence": 0.90
        }]
    )
    result = extractor.extract(other_input, document_type=DocumentType.OTHER)
    assert result.document_type == DocumentType.OTHER
    assert result.fields == {}
