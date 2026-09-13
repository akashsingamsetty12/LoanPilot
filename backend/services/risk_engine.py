"""Module 6: Explainable risk scoring and inconsistency flagging."""
from typing import Any

from schemas.risk import Flag


RULES = {
    "missing_document": (20, "HIGH"),
    "name_mismatch": (25, "HIGH"),
    "income_discrepancy_high": (30, "HIGH"),
    "income_discrepancy_medium": (15, "MEDIUM"),
    "address_mismatch": (10, "MEDIUM"),
    "low_ocr_confidence": (5, "LOW"),
    "date_inconsistency": (10, "MEDIUM"),
}


def score_to_level(score: float) -> str:
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MEDIUM"
    return "HIGH"


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _make_flag(severity: str, reason: str, evidence: str, field: str | None = None, details: dict | None = None) -> Flag:
    return Flag(severity=severity, reason=reason, field=field, evidence=evidence or "Not provided", details=details)


def calculate_risk_score(verification_result: dict) -> tuple[float, list[Flag]]:
    """Convert Module 5 findings into a capped score and explainable flags.

    Accepts common keys: findings, verification_findings, missing_documents,
    and ocr_confidence. Unknown finding types are retained as LOW flags with
    zero points so no verification issue is silently lost.
    """
    score = 0.0
    flags: list[Flag] = []
    findings = verification_result.get("verification_findings") or verification_result.get("findings") or []

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        kind = _text(finding.get("type") or finding.get("flag_type") or finding.get("category")).lower()
        description = _text(finding.get("description") or finding.get("reason") or "Verification inconsistency detected")
        evidence = _text(finding.get("evidence"))
        if not evidence:
            docs = finding.get("documents") or []
            pages = finding.get("pages") or []
            evidence = ", ".join(f"{d} p.{pages[i] if i < len(pages) else '?'}" for i, d in enumerate(docs)) or "Module 5 verification result"

        points = 0
        severity = "LOW"
        if "missing" in kind or "missing" in description.lower():
            points, severity = RULES["missing_document"]
        elif "name" in kind:
            points, severity = RULES["name_mismatch"]
        elif "income" in kind or "salary" in kind:
            difference = finding.get("difference_percent")
            if difference is None:
                difference = finding.get("percentage_difference", 0)
            try:
                difference = abs(float(difference))
            except (TypeError, ValueError):
                difference = 0
            key = "income_discrepancy_high" if difference > 20 else "income_discrepancy_medium"
            points, severity = RULES[key]
        elif "address" in kind:
            points, severity = RULES["address_mismatch"]
        elif "ocr" in kind or "confidence" in kind:
            points, severity = RULES["low_ocr_confidence"]
        elif "date" in kind:
            points, severity = RULES["date_inconsistency"]

        score += points
        flags.append(_make_flag(severity, description, evidence, finding.get("field"), {"points": points, **finding}))

    missing = verification_result.get("missing_documents") or []
    for document in missing:
        score += RULES["missing_document"][0]
        flags.append(_make_flag("HIGH", f"Missing required document: {_text(document)}", f"Document: {_text(document)}", "missing_document", {"points": 20}))

    if not flags:
        flags.append(_make_flag("PASS", "No verification inconsistencies were reported.", "Module 5 verification result", details={"points": 0}))

    return min(score, 100.0), flags


def build_risk_response(application_id: str, verification_result: dict) -> dict:
    score, flags = calculate_risk_score(verification_result)
    level = score_to_level(score)
    summary = "; ".join(flag.reason for flag in flags)
    return {
        "application_id": application_id,
        "score": score,
        "level": level,
        "flags": [flag.model_dump() for flag in flags],
        "recommendation": "NEEDS_HUMAN_REVIEW",
        "summary": summary,
    }


async def assess_risk(app_id: str, db) -> dict:
    """Integration placeholder: load Module 5 result from DB in your backend.

    Keep database-specific persistence in the team's existing integration layer.
    """
    raise NotImplementedError("Connect this function to the existing VerificationResult database model.")
