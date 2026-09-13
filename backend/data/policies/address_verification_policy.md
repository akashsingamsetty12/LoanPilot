# Address Verification Policy

## 1. Primary Address Proof Validation
The residential address listed on the loan application must be verified against:
1. Official KYC Identity Document (Aadhaar, Passport, Voter ID)
2. Recent Utility Bill or Lease Agreement (issued within the last 90 days)

## 2. Address Matching Rules
- Address matching utilizes fuzzy string comparison for minor formatting variations (e.g., "Street" vs "St", "Apartment" vs "Apt", postal zip codes).
- Address variations with > 80% similarity threshold are marked as MATCH.
- Address mismatches below 80% similarity are assigned a MEDIUM risk flag (+10 pts) and require officer verification of proof of residency.
