"""Tests for Application endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Health endpoint should return 200 with app info."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_application(client, sample_application_data):
    """POST /applications should create a new application."""
    response = await client.post("/api/v1/applications", json=sample_application_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("APP-")
    assert data["applicant_name"] == sample_application_data["applicant_name"]
    assert data["status"] == "created"


@pytest.mark.asyncio
async def test_list_applications(client, sample_application_data):
    """GET /applications should return paginated list."""
    # Create two applications
    await client.post("/api/v1/applications", json={"applicant_name": "Applicant One"})
    await client.post("/api/v1/applications", json={"applicant_name": "Applicant Two"})

    response = await client.get("/api/v1/applications?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "applications" in data
    assert "total" in data
    assert data["total"] >= 2
    assert len(data["applications"]) >= 2


@pytest.mark.asyncio
async def test_get_application_detail(client, sample_application_data):
    """GET /applications/{id} should return full state."""
    create_res = await client.post("/api/v1/applications", json=sample_application_data)
    app_id = create_res.json()["id"]

    response = await client.get(f"/api/v1/applications/{app_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == app_id
    assert data["applicant_name"] == sample_application_data["applicant_name"]
    assert "documents" in data
    assert isinstance(data["documents"], list)


@pytest.mark.asyncio
async def test_decide_application(client, sample_application_data):
    """PATCH /applications/{id}/decide should record decision."""
    create_res = await client.post("/api/v1/applications", json=sample_application_data)
    app_id = create_res.json()["id"]

    decision_payload = {
        "decision": "approved",
        "notes": "Verified all income proofs.",
        "decided_by": "Senior Officer",
    }
    response = await client.patch(f"/api/v1/applications/{app_id}/decide", json=decision_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == app_id
    assert data["status"] == "decided"
