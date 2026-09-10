"""
Test Fixtures
==============
Shared fixtures for all tests: test DB, test client, sample data.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, get_db
from main import app


# ── Test Database ──

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db():
    """Create a fresh in-memory database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db):
    """Async HTTP test client with overridden DB dependency."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Sample Data Fixtures ──

@pytest.fixture
def sample_application_data():
    """Sample data for creating a test application."""
    return {"applicant_name": "Rahul Kumar"}


@pytest.fixture
def sample_extracted_payslip():
    """Sample extracted fields for a payslip document."""
    return {
        "name": {"value": "Rahul Kumar", "confidence": 0.97, "page": 1, "source_document": "DOC-0001"},
        "employer": {"value": "Horizon Tech Pvt Ltd", "confidence": 0.95, "page": 1, "source_document": "DOC-0001"},
        "pay_period": {"value": "August 2024", "confidence": 0.92, "page": 1, "source_document": "DOC-0001"},
        "gross_salary": {"value": 85000, "confidence": 0.96, "page": 1, "source_document": "DOC-0001"},
        "net_salary": {"value": 72000, "confidence": 0.93, "page": 1, "source_document": "DOC-0001"},
    }


@pytest.fixture
def sample_extracted_tax_return():
    """Sample extracted fields for a tax return (with income mismatch for testing)."""
    return {
        "taxpayer_name": {"value": "Rahul Kumar", "confidence": 0.94, "page": 1, "source_document": "DOC-0003"},
        "pan_number": {"value": "ABCPK1234R", "confidence": 0.97, "page": 1, "source_document": "DOC-0003"},
        "assessment_year": {"value": "2024-25", "confidence": 0.95, "page": 1, "source_document": "DOC-0003"},
        "declared_income": {"value": 780000, "confidence": 0.92, "page": 2, "source_document": "DOC-0003"},
    }
