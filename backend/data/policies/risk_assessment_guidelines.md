# Risk Assessment Guidelines

## 1. Transparent Scoring Model
LoanPilot utilizes a transparent, rule-based risk scoring model (0-100 scale). Black-box ML models are excluded to ensure 100% explainability.

## 2. Risk Scoring Penalty Deductions
- **+20 points**: Missing required document (per missing document).
- **+25 points**: Name discrepancy across documents (< 85% fuzzy match).
- **+30 points**: Income discrepancy > 20% (HIGH severity).
- **+15 points**: Income discrepancy 10% - 20% (MEDIUM severity).
- **+10 points**: Address mismatch between KYC and utility bill (MEDIUM severity).
- **+10 points**: Pay period / statement date inconsistency.
- **+5 points**: Low OCR extraction confidence (< 0.80).

## 3. Mandatory Evidence Traceability
Every assigned score point must be supported by an verifiable evidence snippet citing the exact document page and extracted value.
