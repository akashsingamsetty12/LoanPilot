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
    # TODO: Implement test after create_application() is ready
    pass


@pytest.mark.asyncio
async def test_list_applications(client):
    """GET /applications should return paginated list."""
    pass


@pytest.mark.asyncio
async def test_get_application_detail(client):
    """GET /applications/{id} should return full state."""
    pass


@pytest.mark.asyncio
async def test_decide_application(client):
    """PATCH /applications/{id}/decide should record decision."""
    pass
