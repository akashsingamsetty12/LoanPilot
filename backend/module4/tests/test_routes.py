import json
import os
import pytest
from fastapi.testclient import TestClient
from module4.main import app

client = TestClient(app)


@pytest.fixture
def sample_payload():
    json_path = os.path.join(os.path.dirname(__file__), "sample_ocr.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Module 4" in data["module"]


def test_classify_endpoint(sample_payload):
    response = client.post("/documents/DOC-001/classify", json=sample_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == "DOC-001"
    assert data["document_type"] == "payslip"
    assert "confidence" in data
    assert "reason" in data


def test_extract_endpoint(sample_payload):
    response = client.post("/documents/DOC-001/extract", json=sample_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == "DOC-001"
    assert data["type"] == "payslip"
    assert data["document_type"] == "payslip"
    assert "fields" in data

    fields = data["fields"]
    assert "name" in fields
    assert fields["name"]["value"] == "Rahul Kumar"
    assert fields["name"]["page"] == 1
    assert "confidence" in fields["name"]
    assert "needs_review" in fields["name"]

    assert "employer" in fields
    assert fields["employer"]["value"] == "HORIZON TECH PRIVATE LIMITED"

    assert "gross_salary" in fields
    assert float(fields["gross_salary"]["value"]) == 90000.0


def test_process_endpoint(sample_payload):
    response = client.post("/documents/process", json=sample_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == "DOC-001"
    assert data["document_type"] == "payslip"
    assert "fields" in data
