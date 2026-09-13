import os
import json
from datetime import datetime

from data.dummy_generator.mismatch_injector import DEMO_APPLICATIONS


def _make_pdf(lines: list[tuple[bool, str]], out_path: str):
    """
    Generate a valid, standard PDF 1.4 document with selectable text using pure Python.
    Compatible with PyMuPDF (fitz), Tesseract OCR, and all PDF viewers.
    """
    stream_lines = ["BT"]
    y = 790
    for is_bold, text in lines:
        if text == "---":
            # Horizontal separator line approximation
            text = "―" * 60
            is_bold = False

        font = "/F2 13 Tf" if is_bold else "/F1 10 Tf"
        safe_text = (
            text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .encode("latin1", "replace")
            .decode("latin1")
        )
        stream_lines.append(f"{font} 50 {y} Td ({safe_text}) Tj")
        stream_lines.append(f"-50 -{y} Td")
        y -= 22 if is_bold else 18

    stream_lines.append("ET")
    stream_content = "\n".join(stream_lines).encode("latin1", "replace")

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj\n"
    )
    objects.append(
        f"4 0 obj\n<< /Length {len(stream_content)} >>\nstream\n".encode("latin1")
        + stream_content
        + b"\nendstream\nendobj\n"
    )
    objects.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(b"6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")

    out = [b"%PDF-1.4\n"]
    offsets = [0]
    curr = len(out[0])
    for obj in objects:
        offsets.append(curr)
        out.append(obj)
        curr += len(obj)

    xref_start = curr
    out.append(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("latin1"))
    for off in offsets[1:]:
        out.append(f"{off:010d} 00000 n \n".encode("latin1"))
    out.append(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("latin1")
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(b"".join(out))


def generate_payslip_pdf(app: dict, out_path: str):
    p = app["payslip"]
    lines = [
        (True, f"PAYSLIP FOR {p['pay_period'].upper()}"),
        (True, p["employer"]),
        (False, "---"),
        (True, "EMPLOYEE DETAILS:"),
        (False, f"Employee Name: {p['name']}"),
        (False, f"Employer: {p['employer']}"),
        (False, f"Pay Period: {p['pay_period']}"),
        (False, "---"),
        (True, "EARNINGS & DEDUCTIONS:"),
        (False, f"Basic Salary: INR {p['basic_salary']:,}"),
        (False, f"House Rent Allowance (HRA): INR {p['hra']:,}"),
        (False, f"Special Allowances: INR {p['allowances']:,}"),
        (True, f"Gross Salary: INR {p['gross_salary']:,}"),
        (False, f"Provident Fund (PF): INR {p['pf_deduction']:,}"),
        (False, f"Professional Tax: INR {p['tax_deduction']:,}"),
        (True, f"Net Take-Home Salary: INR {p['net_salary']:,}"),
        (False, "---"),
        (False, f"Annualized Compensation: INR {p['annualized_income']:,}"),
    ]
    _make_pdf(lines, out_path)


def generate_bank_statement_pdf(app: dict, out_path: str):
    b = app["bank_statement"]
    lines = [
        (True, f"{b['bank_name'].upper()} - ACCOUNT STATEMENT"),
        (False, f"Statement Period: {b['statement_period']}"),
        (False, "---"),
        (True, "ACCOUNT HOLDER:"),
        (False, f"Account Holder Name: {b['account_holder']}"),
        (False, f"Account Number: {b['account_number']}"),
        (False, f"Bank: {b['bank_name']}"),
        (False, "---"),
        (True, "SUMMARY OF CREDITS:"),
        (False, f"Monthly Salary Credit: INR {b['salary_credit']:,}"),
        (False, f"Average Monthly Balance: INR {b['avg_balance']:,}"),
        (False, f"Credit Type: NEFT / ECS SALARY CREDIT"),
        (False, f"Account Status: ACTIVE / REGULAR"),
    ]
    _make_pdf(lines, out_path)


def generate_tax_return_pdf(app: dict, out_path: str):
    t = app["tax_return"]
    lines = [
        (True, "INDIAN INCOME TAX RETURN VERIFICATION FORM (ITR-V)"),
        (False, f"Assessment Year: {t['assessment_year']}"),
        (False, "---"),
        (True, "TAXPAYER INFORMATION:"),
        (False, f"Taxpayer Name: {t['taxpayer_name']}"),
        (False, f"Permanent Account Number (PAN): {t['pan']}"),
        (False, f"Filing Status: Original Return u/s 139(1)"),
        (False, "---"),
        (True, "INCOME DETAILS:"),
        (True, f"Gross Total Income: INR {t['declared_income']:,}"),
        (False, f"Deductions Under Chapter VI-A: INR 1,50,000"),
        (False, f"Total Tax Payable: INR {t['tax_paid']:,}"),
        (False, f"Verification Status: Electronically Verified"),
    ]
    _make_pdf(lines, out_path)


def generate_kyc_pdf(app: dict, out_path: str):
    k = app["kyc"]
    lines = [
        (True, f"GOVERNMENT OF INDIA - {k['id_type'].upper()}"),
        (False, "Official Identity Verification Document"),
        (False, "---"),
        (True, "CARDHOLDER DETAILS:"),
        (False, f"Full Name: {k['name']}"),
        (False, f"Identification Number: {k['id_number']}"),
        (False, f"Date of Birth (DOB): {k['dob']}"),
        (False, f"Address: {k['address']}"),
        (False, "Verification: Digitally Signed & Authenticated"),
    ]
    _make_pdf(lines, out_path)


def generate_address_proof_pdf(app: dict, out_path: str):
    a = app["address_proof"]
    lines = [
        (True, f"RESIDENTIAL ADDRESS PROOF - {a['doc_type'].upper()}"),
        (False, f"Billing / Issue Date: {a['issue_date']}"),
        (False, "---"),
        (True, "CONSUMER DETAILS:"),
        (False, f"Consumer Name: {a['name']}"),
        (False, f"Premises Address: {a['address']}"),
        (False, f"Document Type: {a['doc_type']}"),
        (False, "Status: Bill Paid / Service Verified"),
    ]
    _make_pdf(lines, out_path)


def generate_all(base_dir: str = "data/sample_applications"):
    """Generate all sample applications with intentional demo mismatches."""
    print(f"Generating demo loan applications in '{base_dir}'...")
    os.makedirs(base_dir, exist_ok=True)

    for app in DEMO_APPLICATIONS:
        app_id = app["app_id"]
        app_dir = os.path.join(base_dir, app_id)
        os.makedirs(app_dir, exist_ok=True)

        print(f"Generating {app_id} ({app['applicant_name']}) - Mismatch: {app['mismatch_type']}")

        generate_payslip_pdf(app, os.path.join(app_dir, "payslip.pdf"))
        generate_bank_statement_pdf(app, os.path.join(app_dir, "bank_statement.pdf"))
        generate_tax_return_pdf(app, os.path.join(app_dir, "tax_return.pdf"))
        generate_kyc_pdf(app, os.path.join(app_dir, "kyc_identity.pdf"))

        if app.get("include_address_proof"):
            generate_address_proof_pdf(app, os.path.join(app_dir, "address_proof.pdf"))

        # Save manifest
        manifest_path = os.path.join(app_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(app, f, indent=2)

    print("All sample application documents successfully generated!")


if __name__ == "__main__":
    generate_all()

