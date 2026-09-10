"""Tests for Document endpoints."""
import pytest


@pytest.mark.asyncio
async def test_upload_documents(client):
    """POST /applications/{id}/documents should accept files."""
    pass


@pytest.mark.asyncio
async def test_list_documents(client):
    """GET /applications/{id}/documents should return doc list."""
    pass


@pytest.mark.asyncio
async def test_get_document_status(client):
    """GET /documents/{id}/status should return processing state."""
    pass
