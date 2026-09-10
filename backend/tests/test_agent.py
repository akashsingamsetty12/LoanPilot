"""Tests for AI Agent & Report."""
import pytest


@pytest.mark.asyncio
async def test_agent_why_flagged(client):
    """Agent should explain why an application was flagged."""
    pass


@pytest.mark.asyncio
async def test_agent_missing_document(client):
    """Agent should identify missing documents."""
    pass


@pytest.mark.asyncio
async def test_agent_no_hallucination(client):
    """Agent should only use application data, not hallucinate."""
    pass


@pytest.mark.asyncio
async def test_report_generation(client):
    """Report should include all required sections."""
    pass


@pytest.mark.asyncio
async def test_report_pdf_download(client):
    """PDF download endpoint should return a file."""
    pass
