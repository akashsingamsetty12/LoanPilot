"""Tests for Classification & Extraction."""
import pytest


@pytest.mark.asyncio
async def test_classify_payslip(client):
    """Should classify payslip document correctly."""
    payload = {
        "document_id": "DOC-PAYSLIP-01",
        "filename": "payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "HORIZON TECH PRIVATE LIMITED\nEmployee Name: Rahul Kumar\nPay Period: August 2026\nGross Salary: 90000\nNet Salary: 72000",
                "ocr_confidence": 0.95
            }
        ]
    }
    res = await client.post("/api/v1/documents/DOC-PAYSLIP-01/classify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == "DOC-PAYSLIP-01"
    assert data["document_type"] == "payslip"
    assert data["doc_type"] == "payslip"
    assert data["confidence"] >= 0.70


@pytest.mark.asyncio
async def test_classify_bank_statement(client):
    """Should classify bank statement correctly."""
    payload = {
        "document_id": "DOC-BANK-01",
        "filename": "bank.pdf",
        "pages": [
            {
                "page": 1,
                "text": "STATE BANK OF INDIA\nAccount Holder: Rahul Kumar\nStatement Period: 01-Aug-2026 to 31-Aug-2026\nSalary Credit Rs. 72,000",
                "ocr_confidence": 0.96
            }
        ]
    }
    res = await client.post("/api/v1/documents/DOC-BANK-01/classify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "bank_statement"
    assert data["confidence"] >= 0.70


@pytest.mark.asyncio
async def test_extract_payslip_fields(client):
    """Should extract name, employer, salary from payslip."""
    payload = {
        "document_id": "DOC-PAYSLIP-02",
        "filename": "payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "HORIZON TECH PRIVATE LIMITED\nEmployee Name: Rahul Kumar\nPay Period: August 2026\nGross Salary: 90000\nNet Salary: 72000",
                "ocr_confidence": 0.95
            }
        ]
    }
    res = await client.post("/api/v1/documents/DOC-PAYSLIP-02/extract", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "payslip"
    fields = data["fields"]
    assert fields["name"]["value"] == "Rahul Kumar"
    assert fields["employer"]["value"] == "HORIZON TECH PRIVATE LIMITED"
    assert fields["gross_salary"]["value"] == 90000.0


@pytest.mark.asyncio
async def test_extract_tax_return_fields(client):
    """Should extract taxpayer_name, declared_income from tax return."""
    payload = {
        "document_id": "DOC-TAX-01",
        "filename": "itr.pdf",
        "pages": [
            {
                "page": 1,
                "text": "INCOME TAX RETURN\nTaxpayer Name: Rahul Kumar\nAssessment Year: 2026-27\nDeclared Income: Rs. 9,84,000",
                "ocr_confidence": 0.95
            }
        ]
    }
    res = await client.post("/api/v1/documents/DOC-TAX-01/extract", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "tax_return"
    fields = data["fields"]
    assert fields["taxpayer_name"]["value"] == "Rahul Kumar"
    assert fields["declared_income"]["value"] == 984000.0


@pytest.mark.asyncio
async def test_low_confidence_flagged(client):
    """Fields with confidence < 0.7 or missing should be flagged for review."""
    payload = {
        "document_id": "DOC-INCOMPLETE-01",
        "filename": "incomplete.pdf",
        "pages": [
            {
                "page": 1,
                "text": "Employee Name: Rahul Kumar",
                "ocr_confidence": 0.90
            }
        ]
    }
    res = await client.post("/api/v1/documents/DOC-INCOMPLETE-01/extract?document_type=payslip", json=payload)
    assert res.status_code == 200
    data = res.json()
    fields = data["fields"]
    assert fields["gross_salary"]["value"] is None
    assert fields["gross_salary"]["needs_review"] is True
