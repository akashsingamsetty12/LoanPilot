import pytest
from fastapi.testclient import TestClient
from module4.main import app
from module4.schemas import OCRDocumentInput, DocumentType
from module4.service import DocumentProcessorService

client = TestClient(app)
service = DocumentProcessorService()


# --- TEST CASE 1: PAYSLIP ---
def test_case_1_payslip():
    ocr_payload = {
        "document_id": "TEST-PAYSLIP-01",
        "filename": "technova_payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "TECHNOVA SOLUTIONS PVT LTD\nEmployee Name: Ananya Rao\nPay Period: July 2026\nGross Salary: Rs. 87,500\nNet Salary: Rs. 71,200",
                "ocr_confidence": 0.95
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    cls_data = res_cls.json()
    assert cls_data["document_type"] == "payslip"
    assert cls_data["confidence"] >= 0.70

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    ext_data = res_ext.json()
    fields = ext_data["fields"]

    assert fields["name"]["value"] == "Ananya Rao"
    assert fields["name"]["page"] == 1
    assert fields["name"]["needs_review"] is False

    assert fields["employer"]["value"] == "TECHNOVA SOLUTIONS PVT LTD"
    assert fields["employer"]["page"] == 1

    assert fields["pay_period"]["value"] == "July 2026"
    assert float(fields["gross_salary"]["value"]) == 87500.0
    assert float(fields["net_salary"]["value"]) == 71200.0


# --- TEST CASE 2: BANK STATEMENT ---
def test_case_2_bank_statement():
    ocr_payload = {
        "document_id": "TEST-BANK-02",
        "filename": "unity_bank.pdf",
        "pages": [
            {
                "page": 1,
                "text": "UNITY BANK\nAccount Holder: Rohan Mehta\nStatement Period: 01-07-2026 to 31-07-2026\nSalary Credit 02-07-2026 Rs. 72,500\nSalary Credit 02-06-2026 Rs. 72,500\nAverage Monthly Credit: Rs. 68,900",
                "ocr_confidence": 0.96
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "bank_statement"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["account_holder"]["value"] == "Rohan Mehta"
    assert fields["bank"]["value"] == "UNITY BANK"
    assert fields["statement_period"]["value"] == "01-07-2026 to 31-07-2026"
    assert float(fields["average_monthly_credit"]["value"]) == 68900.0


# --- TEST CASE 3: TAX RETURN ---
def test_case_3_tax_return():
    ocr_payload = {
        "document_id": "TEST-TAX-03",
        "filename": "itr_kavya.pdf",
        "pages": [
            {
                "page": 1,
                "text": "INCOME TAX RETURN\nTaxpayer Name: Kavya Sharma\nAssessment Year: 2026-27\nDeclared Income: Rs. 9,84,000",
                "ocr_confidence": 0.94
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "tax_return"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["taxpayer_name"]["value"] == "Kavya Sharma"
    assert fields["assessment_year"]["value"] == "2026-27"
    assert float(fields["declared_income"]["value"]) == 984000.0


# --- TEST CASE 4: KYC IDENTITY ---
def test_case_4_kyc_identity():
    ocr_payload = {
        "document_id": "TEST-KYC-04",
        "filename": "arjun_id.pdf",
        "pages": [
            {
                "page": 1,
                "text": "IDENTITY DOCUMENT\nName: Arjun Verma\nDate of Birth: 14-02-2002\nAddress: 22 Lake View Road, Bengaluru\nID Number: ZXQ7845129",
                "ocr_confidence": 0.95
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "kyc_identity"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["name"]["value"] == "Arjun Verma"
    assert fields["DOB"]["value"] == "14-02-2002"
    assert fields["address"]["value"] == "22 Lake View Road, Bengaluru"
    assert fields["ID_number"]["value"] == "ZXQ7845129"


# --- TEST CASE 5: ADDRESS PROOF ---
def test_case_5_address_proof():
    ocr_payload = {
        "document_id": "TEST-ADDR-05",
        "filename": "meera_bill.pdf",
        "pages": [
            {
                "page": 1,
                "text": "ELECTRICITY BILL\nCustomer Name: Meera Nair\nService Address: 18 Green Park, Hyderabad\nIssued By: Metro Power Corporation\nIssue Date: 05-08-2026",
                "ocr_confidence": 0.93
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "address_proof"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["name"]["value"] == "Meera Nair"
    assert fields["address"]["value"] == "18 Green Park, Hyderabad"
    assert fields["document_issuer"]["value"] == "Metro Power Corporation"
    assert fields["issue_date"]["value"] == "05-08-2026"


# --- TEST CASE 6: RANDOM / IRRELEVANT DOCUMENT ---
def test_case_6_other_document():
    ocr_payload = {
        "document_id": "TEST-OTHER-06",
        "filename": "library_card.pdf",
        "pages": [
            {
                "page": 1,
                "text": "LIBRARY MEMBERSHIP CARD\nMember: Student User\nMembership valid until December 2026\nBooks issued: 3",
                "ocr_confidence": 0.91
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    cls_data = res_cls.json()

    assert cls_data["document_type"] == "other"
    assert cls_data["confidence"] < 0.70

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    assert res_ext.json()["fields"] == {}


# --- TEST CASE 7: INCOMPLETE PAYSLIP ---
def test_case_7_incomplete_payslip():
    ocr_payload = {
        "document_id": "TEST-INCOMPLETE-07",
        "filename": "brightstar_payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "BRIGHTSTAR SERVICES\nEmployee: Neha\nGross Salary: Rs. 64,000",
                "ocr_confidence": 0.90
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "payslip"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["name"]["value"] == "Neha"
    assert fields["employer"]["value"] == "BRIGHTSTAR SERVICES"
    assert float(fields["gross_salary"]["value"]) == 64000.0

    # Unavailable fields must be null and flagged for review
    assert fields["pay_period"]["value"] is None
    assert fields["pay_period"]["needs_review"] is True
    assert fields["net_salary"]["value"] is None
    assert fields["net_salary"]["needs_review"] is True


# --- TEST CASE 8: MESSY OCR ---
def test_case_8_messy_ocr():
    ocr_payload = {
        "document_id": "TEST-MESSY-08",
        "filename": "messy_payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "ABC TEC HNOLOGIES\nEmp1oyee Name: Vikram Rao\nPay Peri0d: Aug 2026\nGr0ss Salary: 95000\nNet Salary: 78500",
                "ocr_confidence": 0.82
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "payslip"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["name"]["value"] == "Vikram Rao"
    assert float(fields["gross_salary"]["value"]) == 95000.0
    assert float(fields["net_salary"]["value"]) == 78500.0


# --- TEST CASE 9: MULTI-PAGE DOCUMENT ---
def test_case_9_multi_page():
    ocr_payload = {
        "document_id": "TEST-MULTIPAGE-09",
        "filename": "multi_page_bank.pdf",
        "pages": [
            {
                "page": 1,
                "text": "UNITY BANK\nAccount Holder: Sana Kapoor\nStatement Period: June 2026",
                "ocr_confidence": 0.95
            },
            {
                "page": 2,
                "text": "Salary Credit: Rs. 81,000\nAverage Monthly Credit: Rs. 79,500",
                "ocr_confidence": 0.94
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    assert res_cls.json()["document_type"] == "bank_statement"

    res_ext = client.post(f"/documents/{ocr_payload['document_id']}/extract", json=ocr_payload)
    assert res_ext.status_code == 200
    fields = res_ext.json()["fields"]

    assert fields["account_holder"]["value"] == "Sana Kapoor"
    assert fields["account_holder"]["page"] == 1

    assert float(fields["average_monthly_credit"]["value"]) == 79500.0
    assert fields["average_monthly_credit"]["page"] == 2


# --- TEST CASE 10: AMBIGUOUS DOCUMENT ---
def test_case_10_ambiguous_document():
    ocr_payload = {
        "document_id": "TEST-AMBIGUOUS-10",
        "filename": "summary.pdf",
        "pages": [
            {
                "page": 1,
                "text": "Financial Summary\nName: Rahul\nMonthly amount: Rs. 80,000\nEmployer details unavailable",
                "ocr_confidence": 0.75
            }
        ]
    }

    res_cls = client.post(f"/documents/{ocr_payload['document_id']}/classify", json=ocr_payload)
    assert res_cls.status_code == 200
    cls_data = res_cls.json()

    assert cls_data["document_type"] == "other"
    assert cls_data["confidence"] < 0.70


# --- ADDITIONAL RANDOM TEST CASES (A THROUGH J) ---

def test_case_a_different_payslip():
    ocr_payload = {
        "document_id": "TEST-PAYSLIP-A",
        "filename": "acme_payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "ACME CORPORATION\nEmployee Name: Priya Singh\nPay Period: June 2026\nGross Salary: ₹ 1,20,000\nNet Salary: ₹ 98,000",
                "ocr_confidence": 0.96
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "payslip"
    assert data["fields"]["name"]["value"] == "Priya Singh"
    assert data["fields"]["gross_salary"]["value"] == 120000.0


def test_case_b_different_bank_statement():
    ocr_payload = {
        "document_id": "TEST-BANK-B",
        "filename": "hdfc_bank.pdf",
        "pages": [
            {
                "page": 1,
                "text": "HDFC BANK\nAccount Holder: Aman Gupta\nStatement Period: 01-05-2026 to 31-05-2026\nSalary Credit: INR 1,50,000\nAverage Monthly Credit: INR 1,45,000",
                "ocr_confidence": 0.97
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "bank_statement"
    assert data["fields"]["account_holder"]["value"] == "Aman Gupta"
    assert data["fields"]["average_monthly_credit"]["value"] == 145000.0


def test_case_c_different_tax_return():
    ocr_payload = {
        "document_id": "TEST-TAX-C",
        "filename": "form16_suresh.pdf",
        "pages": [
            {
                "page": 1,
                "text": "FORM 16 - INCOME TAX DEPARTMENT\nTaxpayer Name: Suresh Patel\nAssessment Year: 2025-26\nDeclared Income: 15.5 Lakh",
                "ocr_confidence": 0.95
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "tax_return"
    assert data["fields"]["taxpayer_name"]["value"] == "Suresh Patel"
    assert data["fields"]["declared_income"]["value"] == 1550000.0


def test_case_d_different_kyc():
    ocr_payload = {
        "document_id": "TEST-KYC-D",
        "filename": "passport_deepak.pdf",
        "pages": [
            {
                "page": 1,
                "text": "PASSPORT - REPUBLIC OF INDIA\nName: Deepak Joshi\nDate of Birth: 25-11-1995\nAddress: 45 Civil Lines, Jaipur\nID Number: K8942157",
                "ocr_confidence": 0.98
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "kyc_identity"
    assert data["fields"]["name"]["value"] == "Deepak Joshi"
    assert data["fields"]["ID_number"]["value"] == "K8942157"


def test_case_e_different_address_proof():
    ocr_payload = {
        "document_id": "TEST-ADDR-E",
        "filename": "gas_bill.pdf",
        "pages": [
            {
                "page": 1,
                "text": "GAS BILL - UTILITY PROOF\nCustomer Name: Anita Roy\nService Address: 78 Salt Lake, Kolkata\nIssued By: City Gas Distribution\nIssue Date: 10-07-2026",
                "ocr_confidence": 0.94
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_type"] == "address_proof"
    assert data["fields"]["name"]["value"] == "Anita Roy"


def test_case_f_irrelevant_documents():
    for text, doc_id in [
        ("RESTAURANT RECEIPT\nTotal: Rs 450\nTable 4", "TEST-IRRELEVANT-1"),
        ("MOVIE TICKET - PVR CINEMAS\nSeat F12\nDate 04-09-2026", "TEST-IRRELEVANT-2"),
        ("COLLEGE EVENT NOTICE\nAnnual Fest starting tomorrow", "TEST-IRRELEVANT-3")
    ]:
        payload = {
            "document_id": doc_id,
            "filename": "irrelevant.pdf",
            "pages": [{"page": 1, "text": text, "ocr_confidence": 0.90}]
        }
        res = client.post(f"/documents/{doc_id}/classify", json=payload)
        assert res.status_code == 200
        assert res.json()["document_type"] == "other"


def test_case_g_incomplete_bank_statement():
    ocr_payload = {
        "document_id": "TEST-BANK-G",
        "filename": "incomplete_bank.pdf",
        "pages": [
            {
                "page": 1,
                "text": "STATE BANK OF INDIA\nAccount Holder: Priya Sharma",
                "ocr_confidence": 0.92
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    fields = res.json()["fields"]
    assert fields["account_holder"]["value"] == "Priya Sharma"
    assert fields["average_monthly_credit"]["value"] is None
    assert fields["average_monthly_credit"]["needs_review"] is True


def test_case_h_multipage_payslip():
    ocr_payload = {
        "document_id": "TEST-PAYSLIP-H",
        "filename": "multipage_payslip.pdf",
        "pages": [
            {
                "page": 1,
                "text": "GLOBAL CORP INC\nEmployee Name: Ramesh Kumar",
                "ocr_confidence": 0.95
            },
            {
                "page": 2,
                "text": "Pay Period: May 2026\nGross Salary: 105000\nNet Salary: 89000",
                "ocr_confidence": 0.94
            }
        ]
    }
    res = client.post("/documents/process", json=ocr_payload)
    assert res.status_code == 200
    fields = res.json()["fields"]
    assert fields["name"]["page"] == 1
    assert fields["gross_salary"]["page"] == 2
    assert fields["gross_salary"]["value"] == 105000.0
