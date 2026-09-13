"""
Mismatch Injector
==============================
Defines 3 standard demo loan applications matching the project architecture:
  1. APP-0001: Intentional Income Discrepancy (Payslip ₹9,00,000 vs Tax Return ₹7,80,000) + Missing Address Proof.
  2. APP-0002: Intentional Name Variation ("Priya Sharma" in payslip/KYC vs "Priya S." in tax return).
  3. APP-0003: Clean application (100% matching, low risk, pass).
"""

DEMO_APPLICATIONS = [
    {
        "app_id": "APP-0001",
        "applicant_name": "Rahul Kumar",
        "applicant_email": "rahul.kumar@example.com",
        "loan_type": "Home Loan",
        "loan_amount": 3500000,
        "cibil_score": 745,
        "mismatch_type": "income_discrepancy_and_missing_doc",
        "payslip": {
            "name": "Rahul Kumar",
            "employer": "Horizon Technologies Pvt. Ltd.",
            "pay_period": "March 2026",
            "gross_salary": 75000,
            "basic_salary": 40000,
            "hra": 20000,
            "allowances": 15000,
            "pf_deduction": 4500,
            "tax_deduction": 2500,
            "net_salary": 68000,
            "annualized_income": 900000,
        },
        "bank_statement": {
            "account_holder": "Rahul Kumar",
            "bank_name": "State Bank of India",
            "account_number": "39482910482",
            "statement_period": "Jan 2026 - Mar 2026",
            "salary_credit": 68000,
            "avg_balance": 245000,
        },
        "tax_return": {
            "taxpayer_name": "Rahul Kumar",
            "pan": "ABCPK1234F",
            "assessment_year": "2025-26",
            "declared_income": 780000,  # Deliberate ₹1,20,000 mismatch against payslip ₹9,00,000
            "tax_paid": 32000,
        },
        "kyc": {
            "name": "Rahul Kumar",
            "id_type": "PAN Card",
            "id_number": "ABCPK1234F",
            "dob": "1990-05-15",
            "address": "Flat 402, Green Meadows, Electronic City, Bangalore",
        },
        "include_address_proof": False,  # Missing document intentional flag
    },
    {
        "app_id": "APP-0002",
        "applicant_name": "Priya Sharma",
        "applicant_email": "priya.sharma@example.com",
        "loan_type": "Personal Loan",
        "loan_amount": 800000,
        "cibil_score": 710,
        "mismatch_type": "name_variation",
        "payslip": {
            "name": "Priya Sharma",
            "employer": "Apex Global Solutions",
            "pay_period": "March 2026",
            "gross_salary": 65000,
            "basic_salary": 35000,
            "hra": 18000,
            "allowances": 12000,
            "pf_deduction": 4000,
            "tax_deduction": 3000,
            "net_salary": 58000,
            "annualized_income": 780000,
        },
        "bank_statement": {
            "account_holder": "Priya Sharma",
            "bank_name": "ICICI Bank",
            "account_number": "10492819482",
            "statement_period": "Jan 2026 - Mar 2026",
            "salary_credit": 58000,
            "avg_balance": 185000,
        },
        "tax_return": {
            "taxpayer_name": "Priya S.",  # Deliberate fuzzy name variation vs "Priya Sharma"
            "pan": "XYZPS5678G",
            "assessment_year": "2025-26",
            "declared_income": 780000,
            "tax_paid": 28000,
        },
        "kyc": {
            "name": "Priya Sharma",
            "id_type": "Aadhaar Card",
            "id_number": "9182 3847 1029",
            "dob": "1993-08-22",
            "address": "402 Palm Heights, Whitefield, Bangalore",
        },
        "include_address_proof": True,
        "address_proof": {
            "name": "Priya Sharma",
            "doc_type": "Electricity Bill",
            "address": "402 Palm Heights, Whitefield, Bangalore",
            "issue_date": "2026-02-10",
        },
    },
    {
        "app_id": "APP-0003",
        "applicant_name": "Vikram Patel",
        "applicant_email": "vikram.patel@example.com",
        "loan_type": "Car Loan",
        "loan_amount": 1200000,
        "cibil_score": 790,
        "mismatch_type": "clean_approval",
        "payslip": {
            "name": "Vikram Patel",
            "employer": "Tata Consultancy Services",
            "pay_period": "March 2026",
            "gross_salary": 100000,
            "basic_salary": 50000,
            "hra": 25000,
            "allowances": 25000,
            "pf_deduction": 6000,
            "tax_deduction": 6000,
            "net_salary": 88000,
            "annualized_income": 1200000,
        },
        "bank_statement": {
            "account_holder": "Vikram Patel",
            "bank_name": "HDFC Bank",
            "account_number": "50100234891234",
            "statement_period": "Jan 2026 - Mar 2026",
            "salary_credit": 88000,
            "avg_balance": 450000,
        },
        "tax_return": {
            "taxpayer_name": "Vikram Patel",
            "pan": "VWXYZ9876H",
            "assessment_year": "2025-26",
            "declared_income": 1200000,  # 100% Match
            "tax_paid": 95000,
        },
        "kyc": {
            "name": "Vikram Patel",
            "id_type": "PAN Card",
            "id_number": "VWXYZ9876H",
            "dob": "1988-11-04",
            "address": "Flat 301, Lakeview Apts, Shivaji Nagar, Pune",
        },
        "include_address_proof": True,
        "address_proof": {
            "name": "Vikram Patel",
            "doc_type": "Gas Bill",
            "address": "Flat 301, Lakeview Apts, Shivaji Nagar, Pune",
            "issue_date": "2026-01-15",
        },
    },
]

