"""
Integration tests for idempotent oil import.

Tests verify that import script can be run multiple times safely
without creating duplicates or errors.
"""

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.oil import Oil
from scripts.import_oils_database import import_oils_database


@pytest.fixture
async def test_db_session():
    """Create test database session"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


class TestImportIdempotency:
    """Test that import can be run multiple times safely"""

    @pytest.mark.asyncio
    async def test_import_idempotency(self, test_db_session):
        """
        Run import twice, verify:
        1. First run adds 147 oils
        2. Second run adds 0 oils (all skipped)
        3. Total count remains 158
        """
        # Count oils before first import
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        initial_count = result.scalar()

        # Run import first time
        json_path = "working/user-feedback/oils-db-additions/complete-oils-database.json"
        added_1, skipped_1 = await import_oils_database(json_path)

        # Verify first import added 147 oils
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        count_after_first = result.scalar()
        assert count_after_first == initial_count + 147
        assert added_1 == 147
        assert skipped_1 == 0

        # Run import second time
        added_2, skipped_2 = await import_oils_database(json_path)

        # Verify second import added 0 oils (all skipped)
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        count_after_second = result.scalar()
        assert count_after_second == count_after_first
        assert added_2 == 0
        assert skipped_2 == 147

    @pytest.mark.asyncio
    async def test_partial_reimport(self, test_db_session):
        """
        Test partial re-import:
        1. Import all 147 oils
        2. Delete 10 specific oils
        3. Re-import
        4. Verify those 10 oils restored
        """
        # Run initial import
        json_path = "working/user-feedback/oils-db-additions/complete-oils-database.json"
        await import_oils_database(json_path)

        # Get 10 oils to delete
        result = await test_db_session.execute(select(Oil).limit(10))
        oils_to_delete = result.scalars().all()
        deleted_ids = [oil.id for oil in oils_to_delete]

        # Delete those 10 oils
        await test_db_session.execute(delete(Oil).where(Oil.id.in_(deleted_ids)))
        await test_db_session.commit()

        # Count after deletion
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        count_after_deletion = result.scalar()

        # Re-import
        added, skipped = await import_oils_database(json_path)

        # Verify only 10 oils re-added
        assert added == 10
        assert skipped == 137  # 147 - 10 deleted

        # Verify count restored
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        final_count = result.scalar()
        assert final_count == count_after_deletion + 10

        # Verify deleted oils are back
        for oil_id in deleted_ids:
            result = await test_db_session.execute(select(Oil).where(Oil.id == oil_id))
            restored_oil = result.scalar_one_or_none()
            assert restored_oil is not None, f"Oil {oil_id} not restored"

    @pytest.mark.asyncio
    async def test_no_duplicate_ids(self, test_db_session):
        """Verify no duplicate oil IDs exist after multiple imports"""
        # Run import multiple times
        json_path = "working/user-feedback/oils-db-additions/complete-oils-database.json"
        await import_oils_database(json_path)
        await import_oils_database(json_path)
        await import_oils_database(json_path)

        # Query all oil IDs
        result = await test_db_session.execute(select(Oil.id))
        all_ids = [row[0] for row in result.all()]

        # Verify no duplicates
        unique_ids = set(all_ids)
        assert len(all_ids) == len(unique_ids), (
            f"Found {len(all_ids) - len(unique_ids)} duplicate IDs"
        )
