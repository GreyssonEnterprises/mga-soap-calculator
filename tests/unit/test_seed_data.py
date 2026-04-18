"""Unit tests for seed data validation

TDD: Tests written before seed data implementation
Written: 2025-11-01 (before seed_data.py implementation)
Phase: Phase 1 Foundation
Evidence: Test-first development - seed data implemented to pass these tests
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.additive import Additive
from app.models.oil import Oil
from scripts.seed_data import ADDITIVE_SEED_DATA, OIL_SEED_DATA


@pytest.mark.unit
async def test_oil_seed_data_has_minimum_required_oils():
    """Test that seed data contains at least 10 oils"""
    assert len(OIL_SEED_DATA) >= 10, "Seed data must contain at least 10 oils"


@pytest.mark.unit
async def test_oil_seed_data_olive_oil_sap_values():
    """Test that Olive Oil SAP values match spec exactly"""
    olive_oil = next((oil for oil in OIL_SEED_DATA if oil["id"] == "olive_oil"), None)

    assert olive_oil is not None, "Olive Oil must be in seed data"
    assert olive_oil["sap_value_naoh"] == 0.134, (
        "Olive Oil NaOH SAP must be 0.134 (spec requirement)"
    )
    assert olive_oil["sap_value_koh"] == 0.188, "Olive Oil KOH SAP must be 0.188 (spec requirement)"


@pytest.mark.unit
async def test_oil_seed_data_complete_fatty_acid_profiles():
    """Test that all oils have complete 8 fatty acid profiles"""
    required_fatty_acids = [
        "lauric",
        "myristic",
        "palmitic",
        "stearic",
        "ricinoleic",
        "oleic",
        "linoleic",
        "linolenic",
    ]

    for oil in OIL_SEED_DATA:
        assert "fatty_acids" in oil, f"{oil['id']} missing fatty_acids"
        for fatty_acid in required_fatty_acids:
            assert fatty_acid in oil["fatty_acids"], f"{oil['id']} missing {fatty_acid}"


@pytest.mark.unit
async def test_oil_seed_data_complete_quality_contributions():
    """Test that all oils have complete 7 quality metric contributions"""
    required_metrics = [
        "hardness",
        "cleansing",
        "conditioning",
        "bubbly_lather",
        "creamy_lather",
        "longevity",
        "stability",
    ]

    for oil in OIL_SEED_DATA:
        assert "quality_contributions" in oil, f"{oil['id']} missing quality_contributions"
        for metric in required_metrics:
            assert metric in oil["quality_contributions"], f"{oil['id']} missing {metric}"


@pytest.mark.unit
async def test_oil_seed_data_has_inci_names():
    """Test that all oils have INCI names for professional use"""
    for oil in OIL_SEED_DATA:
        assert "inci_name" in oil and oil["inci_name"], f"{oil['id']} missing INCI name"


@pytest.mark.unit
async def test_additive_seed_data_has_minimum_required_additives():
    """Test that seed data contains at least 10 additives"""
    assert len(ADDITIVE_SEED_DATA) >= 10, "Seed data must contain at least 10 additives"


@pytest.mark.unit
async def test_additive_seed_data_kaolin_clay_effects():
    """Test that Kaolin Clay effects match research data"""
    kaolin = next((add for add in ADDITIVE_SEED_DATA if add["id"] == "kaolin_clay"), None)

    assert kaolin is not None, "Kaolin Clay must be in seed data"
    assert kaolin["quality_effects"]["hardness"] == 4.0, (
        "Kaolin hardness effect should be +4.0 at 2% usage"
    )
    assert kaolin["quality_effects"]["creamy_lather"] == 7.0, (
        "Kaolin creamy lather effect should be +7.0 at 2% usage"
    )
    assert kaolin["typical_usage_min_percent"] == 1.0
    assert kaolin["typical_usage_max_percent"] == 3.0


@pytest.mark.unit
async def test_additive_seed_data_sodium_lactate_effects():
    """Test that Sodium Lactate effects match research data"""
    sodium_lactate = next(
        (add for add in ADDITIVE_SEED_DATA if add["id"] == "sodium_lactate"), None
    )

    assert sodium_lactate is not None, "Sodium Lactate must be in seed data"
    assert sodium_lactate["quality_effects"]["hardness"] == 12.0, (
        "Sodium lactate hardness effect should be +12.0"
    )
    assert sodium_lactate["confidence_level"] == "high", (
        "Sodium lactate should have high confidence"
    )


@pytest.mark.unit
async def test_additive_seed_data_high_confidence_additives_present():
    """Test that all high-confidence additives from research are present"""
    high_confidence_ids = [
        "sodium_lactate",
        "sugar",
        "honey",
        "colloidal_oatmeal",
        "kaolin_clay",
        "sea_salt_brine",
    ]

    seed_data_ids = [add["id"] for add in ADDITIVE_SEED_DATA]

    for additive_id in high_confidence_ids:
        assert additive_id in seed_data_ids, (
            f"High-confidence additive '{additive_id}' missing from seed data"
        )


@pytest.mark.unit
async def test_additive_seed_data_confidence_levels_set():
    """Test that all additives have confidence levels (high, medium, low)"""
    valid_confidence_levels = ["high", "medium", "low"]

    for additive in ADDITIVE_SEED_DATA:
        assert "confidence_level" in additive, f"{additive['id']} missing confidence_level"
        assert additive["confidence_level"] in valid_confidence_levels, (
            f"{additive['id']} has invalid confidence_level"
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_seed_oils_can_be_inserted(test_db_session: AsyncSession):
    """Test that seed oil data can be inserted into database (idempotent)"""
    # Insert first oil from seed data if it doesn't already exist
    oil_data = OIL_SEED_DATA[0]

    existing_result = await test_db_session.execute(select(Oil).where(Oil.id == oil_data["id"]))
    existing = existing_result.scalar_one_or_none()

    if existing is None:
        oil = Oil(**oil_data)
        test_db_session.add(oil)
        await test_db_session.commit()

    # Query back
    result = await test_db_session.execute(select(Oil).where(Oil.id == oil_data["id"]))
    inserted_oil = result.scalar_one()

    assert inserted_oil.id == oil_data["id"]
    assert inserted_oil.sap_value_naoh == oil_data["sap_value_naoh"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_seed_additives_can_be_inserted(test_db_session: AsyncSession):
    """Test that seed additive data can be inserted into database (idempotent)"""
    # Insert first additive from seed data if it doesn't already exist
    additive_data = ADDITIVE_SEED_DATA[0]

    existing_result = await test_db_session.execute(
        select(Additive).where(Additive.id == additive_data["id"])
    )
    existing = existing_result.scalar_one_or_none()

    if existing is None:
        additive = Additive(**additive_data)
        test_db_session.add(additive)
        await test_db_session.commit()

    # Query back
    result = await test_db_session.execute(
        select(Additive).where(Additive.id == additive_data["id"])
    )
    inserted_additive = result.scalar_one()

    assert inserted_additive.id == additive_data["id"]
    assert inserted_additive.confidence_level == additive_data["confidence_level"]
