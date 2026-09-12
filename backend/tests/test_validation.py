"""
Tests for Validation & Verification.
"""

import pytest

from models.document import Document

from services.validation import (
    validate_application,
    validate_payslip_fields,
    validate_tax_return_fields,
)

from services.verification import (
    check_name_consistency,
    check_income_consistency,
    check_document_completeness,
)


def make_document(
    document_id,
    doc_type,
    extracted_fields,
):
    """Create a lightweight Document object for testing."""

    return Document(
        id=document_id,
        application_id="APP-0001",
        filename=f"{document_id}.pdf",
        file_path=f"/tmp/{document_id}.pdf",
        file_type="application/pdf",
        file_size=1000,
        status="processed",
        doc_type=doc_type,
        extracted_fields=extracted_fields,
    )


@pytest.mark.asyncio
async def test_validate_missing_required_fields(client, db):
    """Should flag missing required payslip fields."""

    document = make_document(
        "DOC-0001",
        "payslip",
        {
            "name": {
                "value": "Rahul Kumar",
                "confidence": 0.97,
                "page": 1,
            }
        },
    )

    db.add(document)
    await db.commit()

    result = await validate_application(
        "APP-0001",
        db,
    )

    error_fields = {
        error.field
        for error in result.errors
    }

    assert result.valid is False
    assert "employer" in error_fields
    assert "pay_period" in error_fields
    assert "gross_salary" in error_fields
    assert "net_salary" in error_fields
    assert "deductions" in error_fields


def test_validate_invalid_pan_format():
    """Should flag PAN numbers not matching AAAAA0000A format."""

    fields = {
        "pan_number": {
            "value": "INVALID123",
            "confidence": 0.97,
            "page": 1,
        }
    }

    errors = validate_tax_return_fields(
        fields,
        "DOC-0003",
    )

    assert len(errors) == 1
    assert errors[0].field == "pan_number"
    assert errors[0].error_type == "invalid_format"
    assert errors[0].severity == "HIGH"


def test_validate_salary_range():
    """Should flag negative or zero salary values."""

    fields = {
        "gross_salary": {
            "value": 0,
            "confidence": 0.96,
            "page": 1,
        },
        "net_salary": {
            "value": -1000,
            "confidence": 0.93,
            "page": 1,
        },
    }

    errors = validate_payslip_fields(
        fields,
        "DOC-0001",
    )

    error_fields = {
        error.field
        for error in errors
    }

    assert "gross_salary" in error_fields
    assert "net_salary" in error_fields


@pytest.mark.asyncio
async def test_name_consistency_match(client):
    """Matching names across documents should pass."""

    payslip = make_document(
        "DOC-0001",
        "payslip",
        {
            "name": {
                "value": "Rahul Kumar",
                "confidence": 0.97,
                "page": 1,
            }
        },
    )

    tax_return = make_document(
        "DOC-0003",
        "tax_return",
        {
            "taxpayer_name": {
                "value": "Rahul Kumar",
                "confidence": 0.94,
                "page": 1,
            }
        },
    )

    result = check_name_consistency(
        [payslip, tax_return]
    )

    assert result["matched"] is True
    assert len(result["mismatches"]) == 0
    assert len(result["matches"]) == 1


@pytest.mark.asyncio
async def test_name_consistency_fuzzy_match(client):
    """Similar names should match using fuzzy matching."""

    payslip = make_document(
        "DOC-0001",
        "payslip",
        {
            "name": {
                "value": "Jon Smith",
                "confidence": 0.97,
                "page": 1,
            }
        },
    )

    tax_return = make_document(
        "DOC-0003",
        "tax_return",
        {
            "taxpayer_name": {
                "value": "John Smith",
                "confidence": 0.94,
                "page": 1,
            }
        },
    )

    result = check_name_consistency(
        [payslip, tax_return]
    )

    assert result["matched"] is True
    assert len(result["mismatches"]) == 0


@pytest.mark.asyncio
async def test_income_mismatch_detection(client):
    """
    Payslip monthly income × 12 vs tax-return
    declared income should detect a mismatch.
    """

    payslip = make_document(
        "DOC-0001",
        "payslip",
        {
            "gross_salary": {
                "value": 90000,
                "confidence": 0.96,
                "page": 1,
            }
        },
    )

    tax_return = make_document(
        "DOC-0003",
        "tax_return",
        {
            "declared_income": {
                "value": 780000,
                "confidence": 0.92,
                "page": 2,
            }
        },
    )

    result = check_income_consistency(
        [payslip, tax_return]
    )

    assert result["matched"] is False
    assert len(result["mismatches"]) == 1

    mismatch = result["mismatches"][0]

    assert mismatch["field"] == "annual_income"
    assert mismatch["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_missing_document_detection(client):
    """Should detect when required document types are absent."""

    payslip = make_document(
        "DOC-0001",
        "payslip",
        {},
    )

    bank_statement = make_document(
        "DOC-0002",
        "bank_statement",
        {},
    )

    documents = [
        payslip,
        bank_statement,
    ]

    result = check_document_completeness(
        documents
    )

    assert result["is_complete"] is False

    assert "tax_return" in result["missing_documents"]
    assert "kyc_identity" in result["missing_documents"]


@pytest.mark.asyncio
async def test_document_completeness(client):
    """Should report complete when all required types are present."""

    documents = [
        make_document(
            "DOC-0001",
            "payslip",
            {},
        ),
        make_document(
            "DOC-0002",
            "bank_statement",
            {},
        ),
        make_document(
            "DOC-0003",
            "tax_return",
            {},
        ),
        make_document(
            "DOC-0004",
            "kyc_identity",
            {},
        ),
    ]

    result = check_document_completeness(
        documents
    )

    assert result["is_complete"] is True
    assert result["missing_documents"] == []