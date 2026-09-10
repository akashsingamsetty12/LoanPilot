import pytest
from module4.confidence import parse_numeric_value
from module4.llm_client import normalize_document_type, normalize_ocr_label, clean_and_parse_json


def test_parse_numeric_value_currencies():
    assert parse_numeric_value("Rs. 87,500") == 87500.0
    assert parse_numeric_value("Rs 87,500") == 87500.0
    assert parse_numeric_value("INR 87,500") == 87500.0
    assert parse_numeric_value("₹87,500") == 87500.0
    assert parse_numeric_value("₹ 87,500") == 87500.0
    assert parse_numeric_value("87,500") == 87500.0
    assert parse_numeric_value("87.5k") == 87500.0
    assert parse_numeric_value("1.2 Lakh") == 120000.0
    assert parse_numeric_value("2.5 Cr") == 25000000.0
    assert parse_numeric_value("$1,250.50") == 1250.50


def test_parse_numeric_value_invalid_cases():
    assert parse_numeric_value(None) is None
    assert parse_numeric_value("null") is None
    assert parse_numeric_value("N/A") is None
    assert parse_numeric_value("Arbitrary String") is None


def test_normalize_document_type():
    assert normalize_document_type("bank_statement") == "bank_statement"
    assert normalize_document_type("bank statement") == "bank_statement"
    assert normalize_document_type("BANK STATEMENT") == "bank_statement"
    assert normalize_document_type("tax_return") == "tax_return"
    assert normalize_document_type("Tax Return") == "tax_return"
    assert normalize_document_type("kyc_identity") == "kyc_identity"
    assert normalize_document_type("KYC Identity") == "kyc_identity"
    assert normalize_document_type("kyc") == "kyc_identity"
    assert normalize_document_type("address_proof") == "address_proof"
    assert normalize_document_type("Address Proof") == "address_proof"
    assert normalize_document_type("payslip") == "payslip"
    assert normalize_document_type("Pay Slip") == "payslip"
    assert normalize_document_type("random_doc") == "other"


def test_normalize_ocr_label():
    assert normalize_ocr_label("Gr0ss Salary") == "gross salary"
    assert normalize_ocr_label("Emp1oyee Name") == "employee name"
    assert normalize_ocr_label("Pay Peri0d") == "pay period"
    assert normalize_ocr_label("Sa1ary Credit") == "salary credit"


def test_clean_and_parse_json_markdown_wrappers():
    raw_markdown = """
    ```json
    {
      "document_type": "payslip",
      "confidence": 0.95
    }
    ```
    """
    parsed = clean_and_parse_json(raw_markdown)
    assert parsed["document_type"] == "payslip"
    assert parsed["confidence"] == 0.95
