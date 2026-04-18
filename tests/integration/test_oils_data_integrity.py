"""
Integration tests for oils data integrity.

Tests verify complete import process and data quality in database.
All tests should FAIL initially (RED phase).
"""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.oil import Oil


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


class TestImportCompleteness:
    """Test that all 147 oils are imported correctly"""

    @pytest.mark.asyncio
    async def test_import_all_147_oils(self, test_db_session):
        """After import, database should contain 158 total oils (11 seed + 147 new)"""
        result = await test_db_session.execute(select(func.count()).select_from(Oil))
        total_oils = result.scalar()

        assert total_oils == 158, f"Expected 158 oils, found {total_oils}"

    @pytest.mark.asyncio
    async def test_all_oils_have_valid_sap_values(self, test_db_session):
        """All oils should have SAP values within scientific ranges"""
        result = await test_db_session.execute(select(Oil))
        oils = result.scalars().all()

        for oil in oils:
            assert 0.100 <= oil.sap_value_naoh <= 0.300, (
                f"{oil.common_name} SAP NaOH {oil.sap_value_naoh} out of range"
            )
            assert 0.140 <= oil.sap_value_koh <= 0.420, (
                f"{oil.common_name} SAP KOH {oil.sap_value_koh} out of range"
            )

    @pytest.mark.asyncio
    async def test_all_oils_have_fatty_acid_profiles(self, test_db_session):
        """All oils should have complete fatty acid profiles"""
        result = await test_db_session.execute(select(Oil))
        oils = result.scalars().all()

        required_fatty_acids = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]

        for oil in oils:
            fatty_acids = oil.fatty_acids

            # Check all required fatty acids present
            for fa in required_fatty_acids:
                assert fa in fatty_acids, f"{oil.common_name} missing fatty acid: {fa}"

    @pytest.mark.asyncio
    async def test_all_oils_have_quality_contributions(self, test_db_session):
        """All oils should have complete quality contribution metrics"""
        result = await test_db_session.execute(select(Oil))
        oils = result.scalars().all()

        required_quality_metrics = [
            "hardness",
            "cleansing",
            "conditioning",
            "bubbly_lather",
            "creamy_lather",
            "longevity",
            "stability",
        ]

        for oil in oils:
            quality = oil.quality_contributions

            # Check all required metrics present
            for metric in required_quality_metrics:
                assert metric in quality, f"{oil.common_name} missing quality metric: {metric}"

                # Check metric in valid range (0-99)
                value = quality[metric]
                assert 0 <= value <= 99, (
                    f"{oil.common_name} {metric} value {value} out of range [0, 99]"
                )


class TestFattyAcidCompleteness:
    """Test fatty acid profile completeness (US2 requirement)"""

    @pytest.mark.asyncio
    async def test_fatty_acid_completeness_percentage(self, test_db_session):
        """At least 98% of oils (144/147 new oils) should have complete fatty acid profiles"""
        result = await test_db_session.execute(select(Oil))
        oils = result.scalars().all()

        oils_with_complete_profiles = 0

        for oil in oils:
            fatty_acids = oil.fatty_acids
            fatty_acid_sum = sum(fatty_acids.values())

            # Complete profile = fatty acids sum to 95-105% (allowing variance)
            # Exception: pine_tar can have zero sum
            if oil.id == "pine_tar":
                oils_with_complete_profiles += 1
            elif 95 <= fatty_acid_sum <= 105:
                oils_with_complete_profiles += 1

        completeness_percentage = (oils_with_complete_profiles / len(oils)) * 100

        assert completeness_percentage >= 98.0, (
            f"Only {completeness_percentage:.2f}% oils have complete profiles (need ≥98%)"
        )

    @pytest.mark.asyncio
    async def test_fatty_acid_sum_validation(self, test_db_session):
        """Fatty acids should sum to 95-105% for each oil (allowing rounding variance)"""
        result = await test_db_session.execute(select(Oil))
        oils = result.scalars().all()

        invalid_oils = []

        for oil in oils:
            # Special case: pine_tar can have zero sum
            if oil.id == "pine_tar":
                continue

            fatty_acids = oil.fatty_acids
            fatty_acid_sum = sum(fatty_acids.values())

            if not (95 <= fatty_acid_sum <= 105):
                invalid_oils.append((oil.common_name, fatty_acid_sum))

        assert len(invalid_oils) == 0, f"Oils with invalid fatty acid sums: {invalid_oils}"

    @pytest.mark.asyncio
    async def test_special_cases_documented(self, test_db_session):
        """Special case oils (Pine Tar, Meadowfoam) should be present and handled correctly"""
        # Test Pine Tar special case
        result = await test_db_session.execute(select(Oil).where(Oil.id == "pine_tar"))
        pine_tar = result.scalar_one_or_none()

        if pine_tar:
            # Pine Tar can have zero fatty acids (resin-based)
            fatty_acid_sum = sum(pine_tar.fatty_acids.values())
            assert fatty_acid_sum == 0 or 95 <= fatty_acid_sum <= 105, (
                "Pine Tar fatty acid sum should be 0 (resin) or 95-105%"
            )

        # Test Meadowfoam if present (C20/C22 approximated as oleic)
        result = await test_db_session.execute(select(Oil).where(Oil.id == "meadowfoam_oil"))
        meadowfoam = result.scalar_one_or_none()

        if meadowfoam:
            # Meadowfoam should have oleic acid representing C20/C22 long chains
            assert meadowfoam.fatty_acids["oleic"] > 0, (
                "Meadowfoam should have oleic acid (C20/C22 approximation)"
            )
