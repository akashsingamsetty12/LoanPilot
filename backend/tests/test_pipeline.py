"""Tests for end-to-end pipeline."""
import pytest


@pytest.mark.asyncio
async def test_pipeline_trigger(client):
    """POST /applications/{id}/process should start pipeline."""
    pass


@pytest.mark.asyncio
async def test_pipeline_status(client):
    """Pipeline status should track progress."""
    pass


@pytest.mark.asyncio
async def test_full_pipeline_integration(client):
    """
    Full integration test:
    1. Create application
    2. Upload documents
    3. Trigger pipeline
    4. Verify all steps complete
    5. Check flags are generated
    TODO:     """
    pass
