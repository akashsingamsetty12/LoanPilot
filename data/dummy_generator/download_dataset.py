"""
Kaggle Dataset Download
========================
Downloads the Loan Approval Prediction Dataset.

Source: https://www.kaggle.com/datasets/architsharma01/loan-approval-prediction-dataset

Columns:
  loan_id, no_of_dependents, education, self_employed, income_annum,
  loan_amount, loan_term, cibil_score, residential_assets_value,
  commercial_assets_value, luxury_assets_value, bank_asset_value, loan_status

Usage:
  Option A: kaggle datasets download -d architsharma01/loan-approval-prediction-dataset
  Option B: Manual download from the Kaggle URL and extract to data/kaggle/

TODO: download the dataset and place CSV at data/kaggle/loan_approval_dataset.csv
"""

import os
from pathlib import Path


def download_dataset():
    """
    Download the Kaggle dataset using the kaggle CLI.
    Requires: KAGGLE_USERNAME and KAGGLE_KEY environment variables.
    """
    output_dir = Path(__file__).parent.parent / "kaggle"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading dataset to {output_dir}...")
    os.system(
        f"kaggle datasets download "
        f"-d architsharma01/loan-approval-prediction-dataset "
        f"-p {output_dir} --unzip"
    )
    print("Done! Check data/kaggle/ for the CSV file.")


if __name__ == "__main__":
    download_dataset()
