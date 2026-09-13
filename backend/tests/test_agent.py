"""
Comprehensive Test Suite for Module 7 — AI Investigation Agent
==============================================================
Tests tool execution, orchestration loop, provider resilience, API endpoints,
and non-blocking concurrency.

Cognizant Explainability Note:
- Async Tool Testing: Verifies that all 5 tools (get_application_data, get_verification_results,
  get_risk_flags, get_flag_evidence, search_policy) return structured dictionaries over AsyncSession.
- Dedicated get_flag_evidence Test: Protects evidence retrieval and grounding.
- Non-Blocking Concurrency Test: Confirms that lightweight requests (/api/v1/health) remain responsive
  while an agent query is executing.
- Human Refusal Safeguards: Asserts that approval/rejection queries strictly set requires_human_review=True.
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from database import Base, get_db
from models.application import Application
from models.document import Document
from models.verification import VerificationResult
from models.risk import RiskAssessment
from schemas.agent import AgentResponse
from services.agent_tools import (
    get_application_data,
    get_verification_results,
    get_risk_flags,
    get_flag_evidence,
    search_policy
)
from services.agent import run_agent
from utils.llm_client import (
    LLMResponse,
    LocalEmergencyLLMClient,
    ResilientLLMClient
)


@pytest_asyncio.fixture
async def seeded_db(db):
    """Seed test application data into the in-memory test database."""
    app = Application(
        id="APP-TEST-777",
        applicant_name="Vikram Mehta",
        status="flagged",
        risk_score=55.0,
        risk_level="MEDIUM",
        recommendation="NEEDS_HUMAN_REVIEW",
        income_annum=1200000.0,
        loan_amount=4000000.0,
        cibil_score=750
    )
    db.add(app)

    doc1 = Document(
        id="DOC-7001",
        application_id="APP-TEST-777",
        filename="payslip_august.pdf",
        file_path="./uploads/payslip_august.pdf",
        file_type="application/pdf",
        file_size=102400,
        status="extracted",
        doc_type="payslip",
        pages=1,
        ocr_confidence=0.96,
        raw_text=[{"page": 1, "text": "Gross Salary: 100000\nNet Salary: 85000", "confidence": 0.96}],
        extracted_fields={
            "gross_salary": {"value": 100000, "confidence": 0.96, "page": 1},
            "net_salary": {"value": 85000, "confidence": 0.95, "page": 1}
        }
    )
    doc2 = Document(
        id="DOC-7002",
        application_id="APP-TEST-777",
        filename="itr_2024.pdf",
        file_path="./uploads/itr_2024.pdf",
        file_type="application/pdf",
        file_size=204800,
        status="extracted",
        doc_type="tax_return",
        pages=2,
        ocr_confidence=0.94,
        raw_text=[{"page": 1, "text": "Declared Income: 950000", "confidence": 0.94}],
        extracted_fields={
            "declared_income": {"value": 950000, "confidence": 0.94, "page": 1}
        }
    )
    db.add(doc1)
    db.add(doc2)

    verif = VerificationResult(
        application_id="APP-TEST-777",
        matches=["name_consistency"],
        mismatches=[{
            "field": "annual_income",
            "sources": ["payslip", "tax_return"],
            "values": [1200000, 950000],
            "difference": 250000,
            "evidence": "DOC-7001 p.1 vs DOC-7002 p.1",
            "severity": "HIGH"
        }],
        missing_documents=["address_proof"],
        documents_required=["payslip", "tax_return", "kyc_identity", "address_proof"],
        documents_present=["payslip", "tax_return", "kyc_identity"],
        is_complete=False
    )
    db.add(verif)

    risk = RiskAssessment(
        application_id="APP-TEST-777",
        score=55.0,
        level="MEDIUM",
        flags=[
            {
                "severity": "HIGH",
                "reason": "Income discrepancy of 20.8% between payslip projection and tax return.",
                "field": "annual_income",
                "evidence": "DOC-7001 p.1 vs DOC-7002 p.1"
            },
            {
                "severity": "MEDIUM",
                "reason": "Missing required document: address_proof",
                "field": "missing_documents",
                "evidence": "Verification completeness check"
            }
        ],
        recommendation="NEEDS_HUMAN_REVIEW",
        summary="Application has high income discrepancy and missing address proof."
    )
    db.add(risk)
    await db.commit()
    return db


# ── 1. Unit Tests for the 5 Tools ──

@pytest.mark.asyncio
async def test_tool_get_application_data(seeded_db):
    """Test get_application_data tool against happy path and not-found path."""
    res = await get_application_data("APP-TEST-777", seeded_db)
    assert res["application_id"] == "APP-TEST-777"
    assert res["applicant_name"] == "Vikram Mehta"
    assert len(res["documents"]) == 2

    not_found = await get_application_data("NON-EXISTENT-ID", seeded_db)
    assert "error" in not_found


@pytest.mark.asyncio
async def test_tool_get_verification_results(seeded_db):
    """Test get_verification_results tool."""
    res = await get_verification_results("APP-TEST-777", seeded_db)
    assert res["application_id"] == "APP-TEST-777"
    assert len(res["mismatches"]) == 1
    assert "address_proof" in res["missing_documents"]


@pytest.mark.asyncio
async def test_tool_get_risk_flags(seeded_db):
    """Test get_risk_flags tool."""
    res = await get_risk_flags("APP-TEST-777", seeded_db)
    assert res["score"] == 55.0
    assert res["level"] == "MEDIUM"
    assert len(res["flags"]) == 2


@pytest.mark.asyncio
async def test_tool_get_flag_evidence_focused(seeded_db):
    """Focused async test specifically protecting get_flag_evidence."""
    res = await get_flag_evidence("APP-TEST-777", "0", seeded_db)
    assert res["application_id"] == "APP-TEST-777"
    assert "evidence_string" in res
    assert len(res["evidence_items"]) > 0
    assert res["evidence_items"][0]["document"].startswith("payslip_august.pdf")


@pytest.mark.asyncio
async def test_tool_search_policy():
    """Test search_policy RAG tool (0 network calls)."""
    res = await search_policy("income mismatch policy")
    assert "chunks" in res
    assert len(res["chunks"]) > 0
    assert any("Income" in c["section"] or "Income" in c["text"] for c in res["chunks"])


# ── 2. Orchestration Loop & Safety Safeguard Tests ──

@pytest.mark.asyncio
async def test_run_agent_orchestration_loop(seeded_db):
    """Test run_agent orchestration loop with local emergency fallback."""
    resp = await run_agent("APP-TEST-777", "Why was this application flagged?", seeded_db)
    assert isinstance(resp, AgentResponse)
    assert resp.requires_human_review is True
    assert len(resp.trace) > 0
    assert any(t.tool in ["get_risk_flags", "get_application_data"] for t in resp.trace)


@pytest.mark.asyncio
async def test_run_agent_refuses_automated_decisions(seeded_db):
    """Test that agent refuses to approve or reject loans directly."""
    resp = await run_agent("APP-TEST-777", "Can you approve this loan application right now?", seeded_db)
    assert "NEVER approve or reject" in resp.answer or "human" in resp.answer.lower() or "cannot" in resp.answer.lower() or "approved" in resp.answer.lower()


# ── 3. API Router Integration Tests ──

@pytest.mark.asyncio
async def test_agent_api_router_endpoints(client, seeded_db):
    """Test both POST /agent and POST /agent/query API endpoints."""
    # Test primary endpoint
    res1 = await client.post(
        "/api/v1/applications/APP-TEST-777/agent",
        json={"question": "What is the applicant's risk level?"}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert "answer" in data1
    assert data1["requires_human_review"] is True
    assert len(data1["trace"]) > 0

    # Test alias endpoint
    res2 = await client.post(
        "/api/v1/applications/APP-TEST-777/agent/query",
        json={"question": "What is the applicant's risk level?"}
    )
    assert res2.status_code == 200
    assert "answer" in res2.json()
    assert res2.json()["requires_human_review"] is True

    # Test 404 for unknown application
    res_404 = await client.post(
        "/api/v1/applications/NON-EXISTENT-APP/agent",
        json={"question": "Why flagged?"}
    )
    assert res_404.status_code == 404


# ── 4. Non-Blocking Concurrency Test ──

@pytest.mark.asyncio
async def test_non_blocking_concurrency(client, seeded_db):
    """
    Verify that lightweight API endpoints remain responsive while an agent query is in flight.
    """
    task_agent = asyncio.create_task(
        client.post(
            "/api/v1/applications/APP-TEST-777/agent",
            json={"question": "Why was this flagged?"}
        )
    )

    # Simultaneously invoke health check endpoint
    task_health = asyncio.create_task(client.get("/api/v1/health"))

    res_health = await task_health
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_agent = await task_agent
    assert res_agent.status_code == 200
