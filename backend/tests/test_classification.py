"""Tests for Classification & Extraction."""
import pytest


@pytest.mark.asyncio
async def test_classify_payslip(client):
    """Should classify payslip document correctly."""
    pass


@pytest.mark.asyncio
async def test_classify_bank_statement(client):
    """Should classify bank statement correctly."""
    pass


@pytest.mark.asyncio
async def test_extract_payslip_fields(client):
    """Should extract name, employer, salary from payslip."""
    pass


@pytest.mark.asyncio
async def test_extract_tax_return_fields(client):
    """Should extract taxpayer_name, declared_income from tax return."""
    pass


@pytest.mark.asyncio
async def test_low_confidence_flagged(client):
    """Fields with confidence < 0.7 should be flagged for review."""
    pass
