"""Pytest configuration and shared fixtures"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base

# Test database URL (use different database for tests)
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "/mga_soap_calculator", "/mga_soap_calculator_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create test database engine and seed test data"""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed test data (oils and additives)
    from app.models import Additive, Oil
    from scripts.seed_data import ADDITIVE_SEED_DATA, OIL_SEED_DATA

    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        # Add oils
        for oil_data in OIL_SEED_DATA:
            oil = Oil(**oil_data)
            session.add(oil)

        # Add additives
        for additive_data in ADDITIVE_SEED_DATA:
            additive = Additive(**additive_data)
            session.add(additive)

        await session.commit()

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


# Alias for compatibility with tests using async_session name
async_session = test_db_session


@pytest_asyncio.fixture(scope="function")
async def test_db(test_db_engine):
    """
    Callable fixture that returns async context manager for database sessions
    Used by E2E tests that need direct database access
    """
    from contextlib import asynccontextmanager

    async_session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    @asynccontextmanager
    async def _get_session():
        async with async_session_factory() as session:
            yield session

    return _get_session


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints"""
    # Import here to avoid circular imports
    from httpx import ASGITransport

    from app.db.base import get_db
    from app.main import app

    # Create session factory
    async_session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Override the database dependency
    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Use ASGITransport for httpx 0.24+
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # Clear overrides after test
    app.dependency_overrides.clear()


# Alias for E2E tests that use "client" parameter name
client = async_client
