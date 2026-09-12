"""Tests for end-to-end pipeline."""

import pytest


@pytest.mark.asyncio
async def test_pipeline_trigger(client, sample_application_data):
    """POST /applications/{id}/process should start pipeline."""
    create_res = await client.post("/api/v1/applications", json=sample_application_data)
    app_id = create_res.json()["id"]

    response = await client.post(f"/api/v1/applications/{app_id}/process")
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == app_id
    assert data["status"] == "review"


@pytest.mark.asyncio
async def test_pipeline_status(client, sample_application_data):
    """Pipeline status should track progress."""
    create_res = await client.post("/api/v1/applications", json=sample_application_data)
    app_id = create_res.json()["id"]

    response = await client.get(f"/api/v1/applications/{app_id}/pipeline-status")
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == app_id
    assert "progress_percent" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_pipeline_not_found(client):
    """Non-existent application should return 404."""
    response = await client.post("/api/v1/applications/APP-NONEXISTENT/process")
    assert response.status_code == 404
