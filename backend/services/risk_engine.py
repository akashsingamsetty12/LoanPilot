"""
Risk & Inconsistency Flagging Engine
=================================================
Converts verification findings into scored, prioritized flags.


GOLDEN RULE: Transparent, explainable scoring rule — NOT a black-box ML model.
             Every score point is traceable. Every flag has evidence.
             NEVER auto-approve or auto-reject.

Scoring rules:
  +20 pts  Missing required document (per document)
  +25 pts  Name mismatch across documents
  +30 pts  Income discrepancy > 20% (HIGH)
  +15 pts  Income discrepancy 10-20% (MEDIUM)
  +10 pts  Address mismatch (MEDIUM)
  +5  pts  Low OCR confidence < 0.8 (LOW)
  +10 pts  Date inconsistency (MEDIUM)

Score → Level mapping:
  0-30:  LOW
  31-60: MEDIUM
  61-100: HIGH

Data flow:
  Verification results → risk score + level + flags + evidence

Input:  VerificationResult from DB
Output: RiskAssessment stored in DB + RiskResponse returned
"""

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.risk import RiskResponse


async def assess_risk(app_id: str, db: AsyncSession) -> RiskResponse:
    """
    Calculate risk score and generate flags for an application.

    Steps:
      1. Load VerificationResult for this application from DB
      2. Apply scoring rules (see scoring table in docstring above)
      3. For each finding, create a Flag with:
         - severity: HIGH | MEDIUM | LOW | PASS
         - reason: human-readable string
         - evidence: "DOC-001 p.1 vs DOC-003 p.2"
         - details: numeric breakdown (optional)
      4. Calculate total score (cap at 100)
      5. Map score to level: LOW (0-30), MEDIUM (31-60), HIGH (61-100)
      6. Set recommendation (always "NEEDS_HUMAN_REVIEW" if any flags)
      7. Generate human-readable summary of all flags
      8. Create/update RiskAssessment in DB
      9. Update Application.risk_score, risk_level, recommendation
     10. Return RiskResponse

    TODO: implement risk scoring logic
    """
    raise NotImplementedError("assess_risk() is not implemented")


def calculate_risk_score(verification_result: dict) -> tuple[float, list]:
    """
    Calculate the 0-100 risk score from verification results.

    Returns:
      (score, flags_list)

    TODO: implement scoring rules
    """
    raise NotImplementedError("calculate_risk_score() is not implemented")


def score_to_level(score: float) -> str:
    """Map a 0-100 score to LOW/MEDIUM/HIGH."""
    if score <= 30:
        return "LOW"
    elif score <= 60:
        return "MEDIUM"
    else:
        return "HIGH"
