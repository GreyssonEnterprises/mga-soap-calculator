"""Integration Test Configuration

Ensures test database has seeded reference data
"""
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from scripts.seed_data import OIL_SEED_DATA, ADDITIVE_SEED_DATA
from app.models.oil import Oil
from app.models.additive import Additive


@pytest_asyncio.fixture(scope="function", autouse=True)
async def seed_test_data(test_db_engine):
    """
    Automatically seed test database with oils and additives
    Runs for every integration test using actual seed data
    Uses merge to avoid duplicate key violations
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Seed oils (from production seed data) - use merge for upsert behavior
        for oil_data in OIL_SEED_DATA:  # All oils for integration tests
            oil = Oil(**oil_data)
            await session.merge(oil)

        # Seed additives (from production seed data) - use merge for upsert behavior
        for additive_data in ADDITIVE_SEED_DATA:  # All additives for integration tests
            additive = Additive(**additive_data)
            await session.merge(additive)

        await session.commit()
