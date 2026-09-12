"""
Cross-Document Verification Service
================================================
Compares fields across documents to detect inconsistencies.

GOLDEN RULE:
    DETERMINISTIC rules for numbers/dates.
    RapidFuzz ONLY for string variations (names, addresses).

Data flow:
    Canonical JSON
        ↓
    Cross-document checks
        ↓
    VerificationResponse
        ↓
    VerificationResult stored in DB

Cross-document checks:
    1. Name consistency
    2. Employer consistency
    3. Income consistency
    4. Address consistency
    5. Date consistency
    6. Document completeness
"""

import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document
from models.verification import VerificationResult
from schemas.verification import VerificationResponse


# Required document types for a complete application
REQUIRED_DOCUMENT_TYPES = {
    "payslip",
    "bank_statement",
    "tax_return",
    "kyc_identity",
}


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def _get_value(document, field_name):
    """Get the actual value from an extracted field."""

    fields = document.extracted_fields or {}
    field_data = fields.get(field_name)

    if isinstance(field_data, dict):
        return field_data.get("value")

    return field_data


def _to_number(value):
    """Convert currency-like values into a number."""

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = (
            value.replace(",", "")
            .replace("₹", "")
            .replace("INR", "")
            .strip()
        )

        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def _parse_date(value):
    """Parse common date formats."""

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
    """Parse a date range such as '01-08-2026 to 31-08-2026'."""

    if not isinstance(value, str):
        return None, None

    value = value.strip()

    # First handle ranges separated by "to" or "until".
    parts = re.split(
        r"\s+(?:to|until)\s+",
        value,
        flags=re.IGNORECASE,
    )

    # Handle ranges using an en dash or em dash.
    if len(parts) != 2:
        parts = re.split(r"\s*[–—]\s*", value)

    if len(parts) != 2:
        return None, None

    start = _parse_date(parts[0].strip())
    end = _parse_date(parts[1].strip())

    return start, end


# ─────────────────────────────────────────────
# Main Verification Function
# ─────────────────────────────────────────────

async def verify_application(
    app_id: str,
    db: AsyncSession,
) -> VerificationResponse:
    """
    Run all cross-document verification checks for an application.
    """

    # Load all documents belonging to this application.
    result = await db.execute(
        select(Document).where(Document.application_id == app_id)
    )

    documents = result.scalars().all()

    # Run every verification check.
    name_result = check_name_consistency(documents)
    income_result = check_income_consistency(documents)
    employer_result = check_employer_consistency(documents)
    address_result = check_address_consistency(documents)
    date_result = check_date_consistency(documents)
    completeness_result = check_document_completeness(documents)

    # Collect matches and mismatches.
    matches = []
    mismatches = []

    for check_result in [
        name_result,
        income_result,
        employer_result,
        address_result,
        date_result,
    ]:
        matches.extend(check_result.get("matches", []))
        mismatches.extend(check_result.get("mismatches", []))

    # Document completeness information.
    missing_documents = completeness_result["missing_documents"]
    documents_required = completeness_result["documents_required"]
    documents_present = completeness_result["documents_present"]
    is_complete = completeness_result["is_complete"]

    # Add missing documents as mismatches so they are visible.
    for document_type in missing_documents:
        mismatches.append({
            "field": "document_completeness",
            "sources": [],
            "values": [document_type],
            "difference": None,
            "evidence": (
                f"Required document '{document_type}' "
                f"is missing."
            ),
            "severity": "HIGH",
        })

    # Save/update the verification result in the database.
    db_result = await db.execute(
        select(VerificationResult).where(
            VerificationResult.application_id == app_id
        )
    )

    verification_record = db_result.scalar_one_or_none()

    if verification_record is None:
        verification_record = VerificationResult(
            application_id=app_id
        )
        db.add(verification_record)

    verification_record.matches = matches
    verification_record.mismatches = mismatches
    verification_record.missing_documents = missing_documents
    verification_record.documents_required = documents_required
    verification_record.documents_present = documents_present
    verification_record.is_complete = is_complete

    await db.commit()
    await db.refresh(verification_record)

    # Build API response.
    return VerificationResponse(
        application_id=app_id,
        matches=[
            item.get("check", "unknown")
            if isinstance(item, dict)
            else str(item)
            for item in matches
        ],
        mismatches=mismatches,
        missing_documents=missing_documents,
        documents_required=documents_required,
        documents_present=documents_present,
        is_complete=is_complete,
        cross_check_summary={
            "name_consistency": (
                "MATCH"
                if name_result.get("matched", True)
                else "MISMATCH"
            ),
            "income_consistency": (
                "MATCH"
                if income_result.get("matched", True)
                else "MISMATCH"
            ),
            "employer_consistency": (
                "MATCH"
                if employer_result.get("matched", True)
                else "MISMATCH"
            ),
            "address_consistency": (
                "MATCH"
                if address_result.get("matched", True)
                else "MISMATCH"
            ),
            "date_consistency": (
                "MATCH"
                if date_result.get("matched", True)
                else "MISMATCH"
            ),
            "document_completeness": (
                "COMPLETE"
                if is_complete
                else "INCOMPLETE"
            ),
        },
    )


# ─────────────────────────────────────────────
# Name Consistency
# ─────────────────────────────────────────────

def check_name_consistency(documents: list) -> dict:
    """Compare names across all documents using fuzzy matching."""

    from utils.fuzzy_match import names_match

    name_sources = []

    for document in documents:
        fields = document.extracted_fields or {}

        field_data = (
            fields.get("name")
            or fields.get("account_holder")
            or fields.get("taxpayer_name")
        )

        if not field_data:
            continue

        if isinstance(field_data, dict):
            name = field_data.get("value")
        else:
            name = field_data

        if name:
            name_sources.append({
                "document_id": document.id,
                "document_type": document.doc_type,
                "name": str(name).strip(),
            })

    if len(name_sources) < 2:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    reference = name_sources[0]

    matches = []
    mismatches = []

    for source in name_sources[1:]:
        matched, score = names_match(
            reference["name"],
            source["name"],
        )

        evidence = (
            f'{reference["document_id"]} '
            f'({reference["document_type"]}): '
            f'"{reference["name"]}" vs '
            f'{source["document_id"]} '
            f'({source["document_type"]}): '
            f'"{source["name"]}" — similarity {score:.1f}'
        )

        if matched:
            matches.append({
                "check": "name_consistency",
                "evidence": evidence,
            })
        else:
            mismatches.append({
                "field": "name",
                "sources": [
                    reference["document_id"],
                    source["document_id"],
                ],
                "values": [
                    reference["name"],
                    source["name"],
                ],
                "difference": None,
                "evidence": evidence,
                "severity": "HIGH",
            })

    return {
        "matched": len(mismatches) == 0,
        "matches": matches,
        "mismatches": mismatches,
    }


# ─────────────────────────────────────────────
# Income Consistency
# ─────────────────────────────────────────────

def check_income_consistency(documents: list) -> dict:
    """Compare income across payslip, bank statement, and tax return."""

    payslip = next(
        (doc for doc in documents if doc.doc_type == "payslip"),
        None,
    )

    bank_statement = next(
        (doc for doc in documents if doc.doc_type == "bank_statement"),
        None,
    )

    tax_return = next(
        (doc for doc in documents if doc.doc_type == "tax_return"),
        None,
    )

    matches = []
    mismatches = []

    # Payslip monthly salary × 12 vs tax return annual income.
    if payslip and tax_return:
        gross_salary = _to_number(
            _get_value(payslip, "gross_salary")
        )

        declared_income = _to_number(
            _get_value(tax_return, "declared_income")
        )

        if gross_salary is not None and declared_income is not None:
            annualized_salary = gross_salary * 12
            difference = abs(
                annualized_salary - declared_income
            )

            tolerance = annualized_salary * 0.10

            evidence = (
                f"{payslip.id} monthly gross salary = "
                f"₹{gross_salary:.2f}; annualized = "
                f"₹{annualized_salary:.2f}; "
                f"{tax_return.id} declared income = "
                f"₹{declared_income:.2f}; "
                f"difference = ₹{difference:.2f}"
            )

            if difference <= tolerance:
                matches.append({
                    "check": "annual_income_consistency",
                    "evidence": evidence,
                })
            else:
                mismatches.append({
                    "field": "annual_income",
                    "sources": [
                        payslip.id,
                        tax_return.id,
                    ],
                    "values": [
                        annualized_salary,
                        declared_income,
                    ],
                    "difference": difference,
                    "evidence": evidence,
                    "severity": "HIGH",
                })

    # Payslip net salary vs bank statement salary credits.
    if payslip and bank_statement:
        net_salary = _to_number(
            _get_value(payslip, "net_salary")
        )

        salary_credits = _to_number(
            _get_value(bank_statement, "salary_credits")
        )

        if net_salary is not None and salary_credits is not None:
            difference = abs(
                net_salary - salary_credits
            )

            tolerance = net_salary * 0.10

            evidence = (
                f"{payslip.id} net salary = "
                f"₹{net_salary:.2f}; "
                f"{bank_statement.id} salary credits = "
                f"₹{salary_credits:.2f}; "
                f"difference = ₹{difference:.2f}"
            )

            if difference <= tolerance:
                matches.append({
                    "check": "salary_credit_consistency",
                    "evidence": evidence,
                })
            else:
                mismatches.append({
                    "field": "salary_credits",
                    "sources": [
                        payslip.id,
                        bank_statement.id,
                    ],
                    "values": [
                        net_salary,
                        salary_credits,
                    ],
                    "difference": difference,
                    "evidence": evidence,
                    "severity": "MEDIUM",
                })

    return {
        "matched": len(mismatches) == 0,
        "matches": matches,
        "mismatches": mismatches,
    }


# ─────────────────────────────────────────────
# Employer Consistency
# ─────────────────────────────────────────────

def check_employer_consistency(documents: list) -> dict:
    """Compare employer name across documents."""

    from utils.fuzzy_match import organizations_match

    payslip = next(
        (doc for doc in documents if doc.doc_type == "payslip"),
        None,
    )

    bank_statement = next(
        (doc for doc in documents if doc.doc_type == "bank_statement"),
        None,
    )

    if not payslip or not bank_statement:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    employer = _get_value(payslip, "employer")

    # Bank statements may use employer or salary_source.
    bank_employer = (
        _get_value(bank_statement, "employer")
        or _get_value(bank_statement, "salary_source")
    )

    if not employer or not bank_employer:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    matched, score = organizations_match(
        str(employer),
        str(bank_employer),
    )

    evidence = (
        f'{payslip.id} employer = "{employer}" vs '
        f'{bank_statement.id} employer = '
        f'"{bank_employer}" — similarity {score:.1f}'
    )

    if matched:
        return {
            "matched": True,
            "matches": [
                {
                    "check": "employer_consistency",
                    "evidence": evidence,
                }
            ],
            "mismatches": [],
        }

    return {
        "matched": False,
        "matches": [],
        "mismatches": [
            {
                "field": "employer",
                "sources": [
                    payslip.id,
                    bank_statement.id,
                ],
                "values": [
                    employer,
                    bank_employer,
                ],
                "difference": None,
                "evidence": evidence,
                "severity": "HIGH",
            }
        ],
    }


# ─────────────────────────────────────────────
# Address Consistency
# ─────────────────────────────────────────────

def check_address_consistency(documents: list) -> dict:
    """Compare address across KYC and address proof."""

    from utils.fuzzy_match import addresses_match

    kyc_document = next(
        (doc for doc in documents if doc.doc_type == "kyc_identity"),
        None,
    )

    address_proof = next(
        (doc for doc in documents if doc.doc_type == "address_proof"),
        None,
    )

    if not kyc_document or not address_proof:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    kyc_address = _get_value(
        kyc_document,
        "address",
    )

    proof_address = _get_value(
        address_proof,
        "address",
    )

    if not kyc_address or not proof_address:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    matched, score = addresses_match(
        str(kyc_address),
        str(proof_address),
    )

    evidence = (
        f'{kyc_document.id} KYC address = '
        f'"{kyc_address}" vs '
        f'{address_proof.id} address proof = '
        f'"{proof_address}" — similarity {score:.1f}'
    )

    if matched:
        return {
            "matched": True,
            "matches": [
                {
                    "check": "address_consistency",
                    "evidence": evidence,
                }
            ],
            "mismatches": [],
        }

    return {
        "matched": False,
        "matches": [],
        "mismatches": [
            {
                "field": "address",
                "sources": [
                    kyc_document.id,
                    address_proof.id,
                ],
                "values": [
                    kyc_address,
                    proof_address,
                ],
                "difference": None,
                "evidence": evidence,
                "severity": "HIGH",
            }
        ],
    }


# ─────────────────────────────────────────────
# Date Consistency
# ─────────────────────────────────────────────

def check_date_consistency(documents: list) -> dict:
    """Check whether the payslip period falls within the bank statement period."""

    payslip = next(
        (doc for doc in documents if doc.doc_type == "payslip"),
        None,
    )

    bank_statement = next(
        (doc for doc in documents if doc.doc_type == "bank_statement"),
        None,
    )

    if not payslip or not bank_statement:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    pay_period = _get_value(
        payslip,
        "pay_period",
    )

    statement_period = _get_value(
        bank_statement,
        "statement_period",
    )

    if not pay_period or not statement_period:
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    pay_start, pay_end = _parse_date_range(
        pay_period
    )

    statement_start, statement_end = _parse_date_range(
        statement_period
    )

    if not all([
        pay_start,
        pay_end,
        statement_start,
        statement_end,
    ]):
        return {
            "matched": True,
            "matches": [],
            "mismatches": [],
        }

    evidence = (
        f"{payslip.id} pay period = "
        f"{pay_period} vs "
        f"{bank_statement.id} statement period = "
        f"{statement_period}"
    )

    if (
        pay_start >= statement_start
        and pay_end <= statement_end
    ):
        return {
            "matched": True,
            "matches": [
                {
                    "check": "date_consistency",
                    "evidence": evidence,
                }
            ],
            "mismatches": [],
        }

    return {
        "matched": False,
        "matches": [],
        "mismatches": [
            {
                "field": "pay_period",
                "sources": [
                    payslip.id,
                    bank_statement.id,
                ],
                "values": [
                    pay_period,
                    statement_period,
                ],
                "difference": None,
                "evidence": evidence,
                "severity": "MEDIUM",
            }
        ],
    }


# ─────────────────────────────────────────────
# Document Completeness
# ─────────────────────────────────────────────

def check_document_completeness(documents: list) -> dict:
    """Check if all required document types are present."""

    present_documents = {
        document.doc_type
        for document in documents
        if document.doc_type
        and document.doc_type not in {
            "other",
            "unclassified",
        }
    }

    missing_documents = (
        REQUIRED_DOCUMENT_TYPES - present_documents
    )

    return {
        "documents_required": sorted(
            REQUIRED_DOCUMENT_TYPES
        ),
        "documents_present": sorted(
            present_documents
        ),
        "missing_documents": sorted(
            missing_documents
        ),
        "is_complete": len(missing_documents) == 0,
    }