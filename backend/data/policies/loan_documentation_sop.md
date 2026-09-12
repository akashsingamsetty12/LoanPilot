# Loan Documentation Standard Operating Procedure (SOP)

## 1. Document Classification Standards
Each uploaded application document must be classified into one of the canonical document types:
- `payslip`: Salary slip, pay stub, or wage slip showing gross and net earnings.
- `bank_statement`: Official bank account statement showing monthly transaction history and salary credits.
- `tax_return`: Form 16, Income Tax Return (ITR), or official tax assessment.
- `kyc_identity`: Passport, Aadhaar card, PAN card, or Driver's License.
- `address_proof`: Utility bill (electricity, water, gas) or residential lease agreement.

## 2. Name Consistency Matching
- Primary applicant name must match across all submitted documents using fuzzy matching with a minimum 85% similarity threshold.
- Name variations due to middle name initials, honorifics (Mr./Ms./Dr.), or maiden names must be verified against government KYC identity proofs.

## 3. Evidence Citation Protocol
- Every risk flag or discrepancy cited during investigation MUST reference specific source document IDs, page numbers, and extracted values (e.g., "DOC-001 p.1 vs DOC-003 p.2").
