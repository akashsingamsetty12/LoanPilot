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


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.application import Application
from models.verification import VerificationResult
from models.risk import RiskAssessment
from schemas.risk import RiskResponse


async def assess_risk(app_id: str, db: AsyncSession) -> RiskResponse:
    """Load Module 5 VerificationResult from DB, calculate score & flags, and persist RiskAssessment."""
    # 1. Fetch VerificationResult
    vr_stmt = select(VerificationResult).where(VerificationResult.application_id == app_id)
    vr_res = await db.execute(vr_stmt)
    vr = vr_res.scalar_one_or_none()

    verification_data = {}
    if vr:
        findings = []
        if isinstance(vr.mismatches, list):
            findings.extend(vr.mismatches)
        missing_docs = vr.missing_documents if isinstance(vr.missing_documents, list) else []
        verification_data = {
            "verification_findings": findings,
            "missing_documents": missing_docs,
        }

    # 2. Calculate score and flags
    score, flags = calculate_risk_score(verification_data)
    level = score_to_level(score)
    summary = "; ".join(flag.reason for flag in flags)
    flags_dump = [f.model_dump() for f in flags]

    # 3. Upsert RiskAssessment in DB
    risk_stmt = select(RiskAssessment).where(RiskAssessment.application_id == app_id)
    risk_res = await db.execute(risk_stmt)
    risk_record = risk_res.scalar_one_or_none()

    if risk_record:
        risk_record.score = score
        risk_record.level = level
        risk_record.flags = flags_dump
        risk_record.recommendation = "NEEDS_HUMAN_REVIEW"
        risk_record.summary = summary
    else:
        risk_record = RiskAssessment(
            application_id=app_id,
            score=score,
            level=level,
            flags=flags_dump,
            recommendation="NEEDS_HUMAN_REVIEW",
            summary=summary,
        )
        db.add(risk_record)

    # 4. Update Application risk fields
    app_stmt = select(Application).where(Application.id == app_id)
    app_res = await db.execute(app_stmt)
    app = app_res.scalar_one_or_none()
    if app:
        app.risk_score = score
        app.risk_level = level
        app.recommendation = "NEEDS_HUMAN_REVIEW"

    await db.commit()
    await db.refresh(risk_record)

    return RiskResponse(
        application_id=app_id,
        score=score,
        level=level,
        flags=flags,
        recommendation="NEEDS_HUMAN_REVIEW",
        summary=summary,
    )


async def get_risk_assessment(app_id: str, db: AsyncSession) -> RiskResponse:
    """Retrieve existing RiskAssessment or calculate on demand."""
    stmt = select(RiskAssessment).where(RiskAssessment.application_id == app_id)
    res = await db.execute(stmt)
    risk_record = res.scalar_one_or_none()

    if risk_record:
        flags_data = [Flag(**f) if isinstance(f, dict) else f for f in (risk_record.flags or [])]
        return RiskResponse(
            application_id=app_id,
            score=risk_record.score,
            level=risk_record.level,
            flags=flags_data,
            recommendation=risk_record.recommendation or "NEEDS_HUMAN_REVIEW",
            summary=risk_record.summary or "",
        )

    return await assess_risk(app_id, db)

