"""
Validation Service
===============================
Within-document validation: required fields, formats, and numeric ranges.

GOLDEN RULE: This is DETERMINISTIC. No LLM. Pure Python rules.

Data flow:
  Canonical JSON → validation checks → errors/warnings list

Checks per document type:
  All types:       required fields present, confidence thresholds
  payslip:         salary > 0, pay_period is valid date range
  bank_statement:  salary_credits > 0, statement_period valid
  tax_return:      PAN format (AAAAA0000A), declared_income > 0, valid assessment year
  kyc_identity:    DOB valid date, age 18-100, ID number format
  address_proof:   address non-empty, issue_date valid

Input:  All documents' extracted_fields for an application
Output: ValidationResponse with errors and warnings
"""

import re
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document
from schemas.verification import ValidationError, ValidationResponse


# Required document types for a complete loan application.
REQUIRED_DOCUMENT_TYPES = {
    "payslip",
    "bank_statement",
    "tax_return",
    "kyc_identity",
}


# Required extracted fields for each document type.
REQUIRED_FIELDS = {
    "payslip": [
        "name",
        "employer",
        "pay_period",
        "gross_salary",
        "net_salary",
        "deductions",
    ],
    "bank_statement": [
        "account_holder",
        "bank_name",
        "statement_period",
        "salary_credits",
        "avg_monthly_credit",
        "closing_balance",
    ],
    "tax_return": [
        "taxpayer_name",
        "pan_number",
        "assessment_year",
        "declared_income",
        "tax_paid",
    ],
    "kyc_identity": [
        "name",
        "dob",
        "id_type",
        "id_number",
        "address",
    ],
    "address_proof": [
        "name",
        "address",
        "document_type",
        "issue_date",
    ],
}


def _get_value(field_data):
    """
    Get the actual value from an extracted field.

    Field data normally looks like:
    {
        "value": "...",
        "confidence": 0.97,
        "page": 1
    }

    This helper also accepts a raw value for robustness.
    """
    if isinstance(field_data, dict) and "value" in field_data:
        return field_data.get("value")

    return field_data


def _get_confidence(field_data):
    """Return extraction confidence if available."""
    if isinstance(field_data, dict):
        confidence = field_data.get("confidence")

        if confidence is not None:
            try:
                return float(confidence)
            except (TypeError, ValueError):
                return None

    return None


def _is_empty(value) -> bool:
    """Return True when an extracted value is missing or empty."""
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    return False


def _to_number(value):
    """
    Convert common numeric formats into float.

    Handles values such as:
      900000
      "900000"
      "9,00,000"
      "₹90,000"
      "INR 90000"
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.strip()
        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace("₹", "")
        cleaned = re.sub(r"(?i)\bINR\b", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def _parse_date(value):
    """
    Parse common date formats.

    Returns:
        datetime.date or None
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    value = value.strip()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def _parse_date_range(value):
    """
    Parse a date range such as:

        "2026-08-01 to 2026-08-31"
        "01/08/2026 - 31/08/2026"

    Returns:
        (start_date, end_date) or (None, None)
    """
    if not isinstance(value, str):
        return None, None

    parts = re.split(r"\s+(?:to|until)\s+|\s*[-–—]\s*", value.strip(), flags=re.I)

    if len(parts) != 2:
        return None, None

    start = _parse_date(parts[0].strip())
    end = _parse_date(parts[1].strip())

    return start, end


def _error(
    document_id: str,
    field: str,
    error_type: str,
    message: str,
    severity: str = "MEDIUM",
) -> ValidationError:
    """Create a standard validation error."""
    return ValidationError(
        document_id=document_id,
        field=field,
        error_type=error_type,
        message=message,
        severity=severity,
    )


async def validate_application(
    app_id: str,
    db: AsyncSession,
) -> ValidationResponse:
    """
    Run within-document validation checks for all documents in an application.

    Steps:
      1. Load all documents for this application from DB
      2. Validate required fields
      3. Validate formats and numeric ranges
      4. Check extraction confidence
      5. Check document completeness
      6. Return ValidationResponse
    """

    result = await db.execute(
        select(Document).where(Document.application_id == app_id)
    )

    documents = result.scalars().all()

    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # Track document types for completeness checking.
    present_types = {
        document.doc_type
        for document in documents
        if document.doc_type
        and document.doc_type not in {"other", "unclassified"}
    }

    # Validate every document.
    for document in documents:
        fields = document.extracted_fields or {}

        # Skip documents that have not reached extraction.
        if not fields:
            continue

        # 1. Required fields
        required_fields = REQUIRED_FIELDS.get(document.doc_type, [])

        for field_name in required_fields:
            field_data = fields.get(field_name)
            value = _get_value(field_data)

            if _is_empty(value):
                errors.append(
                    _error(
                        document.id,
                        field_name,
                        "missing_required",
                        f"Required field '{field_name}' is missing.",
                        "HIGH",
                    )
                )

        # 2. Confidence checks
        for field_name, field_data in fields.items():
            confidence = _get_confidence(field_data)

            if confidence is not None and confidence < 0.70:
                warnings.append(
                    _error(
                        document.id,
                        field_name,
                        "low_confidence",
                        f"Extraction confidence for '{field_name}' is "
                        f"{confidence:.2f}, below the 0.70 threshold.",
                        "LOW",
                    )
                )

        # 3. Document-specific validation
        if document.doc_type == "payslip":
            errors.extend(validate_payslip_fields(fields, document.id))

        elif document.doc_type == "bank_statement":
            errors.extend(validate_bank_statement_fields(fields, document.id))

        elif document.doc_type == "tax_return":
            errors.extend(validate_tax_return_fields(fields, document.id))

        elif document.doc_type == "kyc_identity":
            errors.extend(validate_kyc_fields(fields, document.id))

        elif document.doc_type == "address_proof":
            errors.extend(validate_address_proof_fields(fields, document.id))

    # 4. Document completeness
    missing_documents = REQUIRED_DOCUMENT_TYPES - present_types

    for doc_type in sorted(missing_documents):
        errors.append(
            _error(
                "APPLICATION",
                doc_type,
                "missing_required",
                f"Required document type '{doc_type}' is missing.",
                "HIGH",
            )
        )

    return ValidationResponse(
        application_id=app_id,
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


# ── Validation Rule Functions ──


def validate_payslip_fields(
    fields: dict,
    document_id: str = "UNKNOWN",
) -> list[ValidationError]:
    """Check payslip-specific field validity."""

    errors = []

    gross_salary = _to_number(_get_value(fields.get("gross_salary")))
    net_salary = _to_number(_get_value(fields.get("net_salary")))
    deductions = _to_number(_get_value(fields.get("deductions")))

    # Salary must be greater than zero.
    if gross_salary is not None and gross_salary <= 0:
        errors.append(
            _error(
                document_id,
                "gross_salary",
                "out_of_range",
                "Gross salary must be greater than zero.",
                "HIGH",
            )
        )

    if net_salary is not None and net_salary <= 0:
        errors.append(
            _error(
                document_id,
                "net_salary",
                "out_of_range",
                "Net salary must be greater than zero.",
                "HIGH",
            )
        )

    if deductions is not None and deductions < 0:
        errors.append(
            _error(
                document_id,
                "deductions",
                "out_of_range",
                "Deductions cannot be negative.",
                "MEDIUM",
            )
        )

    # Net salary should not normally exceed gross salary.
    if (
        gross_salary is not None
        and net_salary is not None
        and net_salary > gross_salary
    ):
        errors.append(
            _error(
                document_id,
                "net_salary",
                "out_of_range",
                "Net salary cannot be greater than gross salary.",
                "HIGH",
            )
        )

    # Validate pay period.
    pay_period = _get_value(fields.get("pay_period"))

    if not _is_empty(pay_period):
        start, end = _parse_date_range(pay_period)

        if start is None or end is None:
            errors.append(
                _error(
                    document_id,
                    "pay_period",
                    "invalid_format",
                    "Pay period must contain a valid start and end date.",
                    "MEDIUM",
                )
            )
        elif start > end:
            errors.append(
                _error(
                    document_id,
                    "pay_period",
                    "invalid_format",
                    "Pay period start date cannot be after the end date.",
                    "HIGH",
                )
            )

    return errors


def validate_bank_statement_fields(
    fields: dict,
    document_id: str = "UNKNOWN",
) -> list[ValidationError]:
    """Check bank statement-specific field validity."""

    errors = []

    salary_credits = _to_number(
        _get_value(fields.get("salary_credits"))
    )

    avg_monthly_credit = _to_number(
        _get_value(fields.get("avg_monthly_credit"))
    )

    closing_balance = _to_number(
        _get_value(fields.get("closing_balance"))
    )

    if salary_credits is not None and salary_credits <= 0:
        errors.append(
            _error(
                document_id,
                "salary_credits",
                "out_of_range",
                "Salary credits must be greater than zero.",
                "HIGH",
            )
        )

    if avg_monthly_credit is not None and avg_monthly_credit <= 0:
        errors.append(
            _error(
                document_id,
                "avg_monthly_credit",
                "out_of_range",
                "Average monthly credit must be greater than zero.",
                "MEDIUM",
            )
        )

    if closing_balance is not None and closing_balance < 0:
        errors.append(
            _error(
                document_id,
                "closing_balance",
                "out_of_range",
                "Closing balance cannot be negative.",
                "MEDIUM",
            )
        )

    # Validate statement period.
    statement_period = _get_value(
        fields.get("statement_period")
    )

    if not _is_empty(statement_period):
        start, end = _parse_date_range(statement_period)

        if start is None or end is None:
            errors.append(
                _error(
                    document_id,
                    "statement_period",
                    "invalid_format",
                    "Statement period must contain a valid start and end date.",
                    "MEDIUM",
                )
            )
        elif start > end:
            errors.append(
                _error(
                    document_id,
                    "statement_period",
                    "invalid_format",
                    "Statement period start date cannot be after the end date.",
                    "HIGH",
                )
            )

    return errors


def validate_tax_return_fields(
    fields: dict,
    document_id: str = "UNKNOWN",
) -> list[ValidationError]:
    """Check tax return-specific field validity."""

    errors = []

    # PAN must follow AAAAA0000A format.
    pan = _get_value(fields.get("pan_number"))

    if not _is_empty(pan):
        if not isinstance(pan, str) or not re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]",
            pan.strip().upper(),
        ):
            errors.append(
                _error(
                    document_id,
                    "pan_number",
                    "invalid_format",
                    "PAN must match the format AAAAA0000A.",
                    "HIGH",
                )
            )

    # Declared income must be positive.
    declared_income = _to_number(
        _get_value(fields.get("declared_income"))
    )

    if declared_income is not None and declared_income <= 0:
        errors.append(
            _error(
                document_id,
                "declared_income",
                "out_of_range",
                "Declared income must be greater than zero.",
                "HIGH",
            )
        )

    # Tax paid cannot be negative.
    tax_paid = _to_number(
        _get_value(fields.get("tax_paid"))
    )

    if tax_paid is not None and tax_paid < 0:
        errors.append(
            _error(
                document_id,
                "tax_paid",
                "out_of_range",
                "Tax paid cannot be negative.",
                "MEDIUM",
            )
        )

    # Assessment year should look like 2025-26 / 2025–26.
    assessment_year = _get_value(
        fields.get("assessment_year")
    )

    if not _is_empty(assessment_year):
        normalized = str(assessment_year).strip()

        if not re.fullmatch(r"\d{4}\s*[-–]\s*\d{2}", normalized):
            errors.append(
                _error(
                    document_id,
                    "assessment_year",
                    "invalid_format",
                    "Assessment year must use a format such as 2025-26.",
                    "MEDIUM",
                )
            )

    return errors


def validate_kyc_fields(
    fields: dict,
    document_id: str = "UNKNOWN",
) -> list[ValidationError]:
    """Check KYC/identity-specific field validity."""

    errors = []

    # Validate date of birth.
    dob = _get_value(fields.get("dob"))

    if not _is_empty(dob):
        parsed_dob = _parse_date(dob)

        if parsed_dob is None:
            errors.append(
                _error(
                    document_id,
                    "dob",
                    "invalid_format",
                    "Date of birth is not a valid date.",
                    "HIGH",
                )
            )
        else:
            today = date.today()

            if parsed_dob > today:
                errors.append(
                    _error(
                        document_id,
                        "dob",
                        "out_of_range",
                        "Date of birth cannot be in the future.",
                        "HIGH",
                    )
                )
            else:
                age = (
                    today.year
                    - parsed_dob.year
                    - (
                        (today.month, today.day)
                        < (parsed_dob.month, parsed_dob.day)
                    )
                )

                if age < 18 or age > 100:
                    errors.append(
                        _error(
                            document_id,
                            "dob",
                            "out_of_range",
                            "Applicant age must be between 18 and 100 years.",
                            "HIGH",
                        )
                    )

    # ID number should not be empty.
    id_number = _get_value(fields.get("id_number"))

    if not _is_empty(id_number):
        if not isinstance(id_number, str) or len(id_number.strip()) < 4:
            errors.append(
                _error(
                    document_id,
                    "id_number",
                    "invalid_format",
                    "Identity document number appears invalid.",
                    "MEDIUM",
                )
            )

    return errors


def validate_address_proof_fields(
    fields: dict,
    document_id: str = "UNKNOWN",
) -> list[ValidationError]:
    """Check address proof-specific field validity."""

    errors = []

    address = _get_value(fields.get("address"))

    if _is_empty(address):
        errors.append(
            _error(
                document_id,
                "address",
                "missing_required",
                "Address must not be empty.",
                "HIGH",
            )
        )

    issue_date = _get_value(fields.get("issue_date"))

    if not _is_empty(issue_date):
        if _parse_date(issue_date) is None:
            errors.append(
                _error(
                    document_id,
                    "issue_date",
                    "invalid_format",
                    "Issue date is not a valid date.",
                    "MEDIUM",
                )
            )

    return errors