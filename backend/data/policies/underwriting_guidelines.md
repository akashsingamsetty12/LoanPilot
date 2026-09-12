# Underwriting Guidelines

## 1. Human Officer Final Decision Requirement
- **Mandatory Human-in-the-Loop Rule**: Underwriting systems, AI investigation agents, and automated risk scoring tools are strictly advisory. Automated systems are PROHIBITED from executing final loan approvals or rejections without a licensed human loan officer's manual decision.
- All AI recommendations must default to `NEEDS_HUMAN_REVIEW` whenever risk flags or document discrepancies are identified.

## 2. Risk Level Classifications
- **LOW Risk (Score 0 - 30)**: Standard processing path. Basic cross-document verification passed with high confidence.
- **MEDIUM Risk (Score 31 - 60)**: Requires targeted loan officer review of highlighted field discrepancies (e.g. minor address variation or date discrepancy).
- **HIGH Risk (Score 61 - 100)**: Requires full underwriting audit, mandatory supervisor escalation, and secondary background check.

## 3. Decision Refusal and Safeguards
- Any request asking the AI system to "approve" or "reject" an application must be formally refused with a redirection to the human underwriting officer.
