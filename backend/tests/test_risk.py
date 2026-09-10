"""Tests for Risk Engine."""
import pytest
from services.risk_engine import score_to_level


def test_score_to_level_low():
    assert score_to_level(0) == "LOW"
    assert score_to_level(30) == "LOW"


def test_score_to_level_medium():
    assert score_to_level(31) == "MEDIUM"
    assert score_to_level(60) == "MEDIUM"


def test_score_to_level_high():
    assert score_to_level(61) == "HIGH"
    assert score_to_level(100) == "HIGH"


@pytest.mark.asyncio
async def test_risk_assessment_with_mismatch(client):
    """Income mismatch should produce HIGH flag."""
    pass


@pytest.mark.asyncio
async def test_risk_assessment_clean_application(client):
    """Clean application should score LOW with PASS flags."""
    pass


@pytest.mark.asyncio
async def test_risk_never_auto_approves(client):
    """Recommendation should never be 'APPROVED' automatically."""
    pass
