"""
Master Generator
==============================
Generates all dummy documents for testing.


Usage: python -m data.dummy_generator.generate_all

Steps:
  1. Load Kaggle CSV (data/kaggle/loan_approval_dataset.csv)
  2. Pick 20-50 rows
  3. For each row: generate payslip, bank statement, tax return, KYC PDFs
  4. Inject 2-3 deliberate mismatch applications
  5. Save to data/sample_applications/{APP-XXXX}/

TODO: implement end-to-end generation
"""


def generate_all():
    print("Generating all dummy documents...")
    print("Steps:")
    print("  1. Load Kaggle CSV")
    print("  2. Generate document sets for 20-50 applications")
    print("  3. Inject 2-3 mismatch applications")
    print("  4. Save to data/sample_applications/")


if __name__ == "__main__":
    generate_all()
