"""
Integration tests for calculation-based INCI label endpoint (Spec 003)

TDD Evidence: Tests written FIRST before implementation
RED phase: These tests will fail until endpoint is implemented

User Story:
- As a professional soap maker, I want to generate INCI labels for my SAVED recipes
- The endpoint should work with Calculation IDs (saved recipes), not raw formulations
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import Calculation
from app.models.user import User


@pytest.fixture
async def sample_user(test_db_session: AsyncSession) -> User:
    """
    Create a sample user for testing

    Uses a valid Argon2id hash format (dummy hash, not a real password)
    """
    user = User(
        id=uuid4(),
        email="soap_maker@example.com",
        # Valid Argon2id format (dummy hash for testing, ≥80 chars required)
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$dGVzdHNhbHRkdW1teWRhdGExMjM0NTY=$abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOP",
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest.fixture
async def sample_calculation(test_db_session: AsyncSession, sample_user: User) -> Calculation:
    """
    Create a sample calculation with recipe data

    This mimics what the calculation API would store when a user
    creates a recipe calculation.
    """
    calculation = Calculation(
        id=uuid4(),
        user_id=sample_user.id,
        recipe_data={
            "oils": [
                {"id": "coconut_oil", "weight_g": 300.0},
                {"id": "olive_oil", "weight_g": 700.0},
            ],
            "lye": {"naoh_weight_g": 135.0, "koh_weight_g": 0.0, "type": "naoh"},
            "water_weight_g": 300.0,
            "superfat_percent": 5.0,
        },
        results_data={"quality_metrics": {"hardness": 29, "cleansing": 18, "conditioning": 59}},
        koh_purity=90.0,
        naoh_purity=100.0,
    )
    test_db_session.add(calculation)
    await test_db_session.commit()
    await test_db_session.refresh(calculation)
    return calculation


@pytest.mark.asyncio
async def test_get_inci_label_all_formats(client: AsyncClient, sample_calculation: Calculation):
    """
    Test GET /api/v1/inci/calculations/{id}/inci-label with format=all

    Expected behavior:
    - Returns all three formats: raw_inci, saponified_inci, common_names
    - Ingredients sorted by percentage (descending)
    - Water percentage included properly
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label", params={"format": "all"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "raw_inci" in data
    assert "saponified_inci" in data
    assert "common_names" in data
    assert "ingredients_breakdown" in data

    # Verify raw INCI format (includes lye)
    raw_inci = data["raw_inci"]
    assert "Sodium Hydroxide" in raw_inci or "NaOH" in raw_inci
    assert "Olea Europaea" in raw_inci or "Olive" in raw_inci
    assert "Cocos Nucifera" in raw_inci or "Coconut" in raw_inci

    # Verify saponified INCI format (no lye, has salts)
    saponified_inci = data["saponified_inci"]
    assert "Sodium Hydroxide" not in saponified_inci
    assert "Sodium Olivate" in saponified_inci
    assert "Sodium Cocoate" in saponified_inci

    # Verify common names format
    common_names = data["common_names"]
    assert "Olive Oil" in common_names
    assert "Coconut Oil" in common_names


@pytest.mark.asyncio
async def test_get_inci_label_single_format_raw(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test format=raw_inci returns ONLY raw format
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "raw_inci"},
    )

    assert response.status_code == 200
    data = response.json()

    # Only raw_inci should be present
    assert "raw_inci" in data
    assert "saponified_inci" not in data
    assert "common_names" not in data


@pytest.mark.asyncio
async def test_get_inci_label_single_format_saponified(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test format=saponified_inci returns ONLY saponified format
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "saponified_inci"},
    )

    assert response.status_code == 200
    data = response.json()

    # Only saponified_inci should be present
    assert "saponified_inci" in data
    assert "raw_inci" not in data
    assert "common_names" not in data


@pytest.mark.asyncio
async def test_get_inci_label_single_format_common_names(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test format=common_names returns ONLY common names format
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "common_names"},
    )

    assert response.status_code == 200
    data = response.json()

    # Only common_names should be present
    assert "common_names" in data
    assert "raw_inci" not in data
    assert "saponified_inci" not in data


@pytest.mark.asyncio
async def test_get_inci_label_with_percentages(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test include_percentages=true adds percentage values to labels
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "saponified_inci", "include_percentages": True},
    )

    assert response.status_code == 200
    data = response.json()

    # Should have ingredients_breakdown with percentages
    assert "ingredients_breakdown" in data
    breakdown = data["ingredients_breakdown"]
    assert len(breakdown) > 0

    # Each ingredient should have percentage field
    for ingredient in breakdown:
        assert "name" in ingredient
        assert "percentage" in ingredient
        assert isinstance(ingredient["percentage"], (int, float))
        assert 0 <= ingredient["percentage"] <= 100


@pytest.mark.asyncio
async def test_get_inci_label_line_by_line_format(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test line_by_line=true returns newline-separated format
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "raw_inci", "line_by_line": True},
    )

    assert response.status_code == 200
    data = response.json()

    raw_inci = data["raw_inci"]
    # Should have newlines, not commas
    assert "\n" in raw_inci
    # Should NOT have comma separation (unless it's part of ingredient name)
    lines = raw_inci.split("\n")
    assert len(lines) > 1


@pytest.mark.asyncio
async def test_get_inci_label_nonexistent_calculation(client: AsyncClient):
    """
    Test 404 response for non-existent calculation ID
    """
    fake_id = uuid4()
    response = await client.get(f"/api/v1/inci/calculations/{fake_id}/inci-label")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_get_inci_label_invalid_format_parameter(
    client: AsyncClient, sample_calculation: Calculation
):
    """
    Test 422 validation error for invalid format parameter
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "invalid_format"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_inci_label_percentage_sorting(client: AsyncClient, sample_calculation: Calculation):
    """
    Test that ingredients are sorted by percentage (descending)

    This is a regulatory requirement - ingredients must be listed
    from highest to lowest percentage.
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label",
        params={"format": "all", "include_percentages": True},
    )

    assert response.status_code == 200
    data = response.json()

    breakdown = data["ingredients_breakdown"]
    percentages = [ing["percentage"] for ing in breakdown]

    # Verify descending order
    assert percentages == sorted(percentages, reverse=True)


@pytest.mark.asyncio
async def test_inci_label_includes_water(client: AsyncClient, sample_calculation: Calculation):
    """
    Test that water is included in INCI label with proper INCI name

    Water should appear as "Aqua" or "Water" depending on format.
    """
    response = await client.get(
        f"/api/v1/inci/calculations/{sample_calculation.id}/inci-label", params={"format": "all"}
    )

    assert response.status_code == 200
    data = response.json()

    # Raw and saponified should use "Aqua" (INCI name)
    assert "Aqua" in data["raw_inci"] or "Water" in data["raw_inci"]
    assert "Aqua" in data["saponified_inci"] or "Water" in data["saponified_inci"]

    # Common names should use "Water"
    assert "Water" in data["common_names"]


@pytest.mark.asyncio
async def test_inci_label_koh_soap_uses_potassium_salts(
    test_db_session: AsyncSession, client: AsyncClient, sample_user: User
):
    """
    Test that KOH soaps use "Potassium" instead of "Sodium" in saponified names
    """
    # Create KOH calculation
    koh_calculation = Calculation(
        id=uuid4(),
        user_id=sample_user.id,
        recipe_data={
            "oils": [
                {"id": "coconut_oil", "weight_g": 500.0},
                {"id": "olive_oil", "weight_g": 500.0},
            ],
            "lye": {"naoh_weight_g": 0.0, "koh_weight_g": 189.0, "type": "koh"},
            "water_weight_g": 400.0,
            "superfat_percent": 5.0,
        },
        results_data={"quality_metrics": {}},
        koh_purity=90.0,
        naoh_purity=100.0,
    )
    test_db_session.add(koh_calculation)
    await test_db_session.commit()
    await test_db_session.refresh(koh_calculation)

    response = await client.get(
        f"/api/v1/inci/calculations/{koh_calculation.id}/inci-label",
        params={"format": "saponified_inci"},
    )

    assert response.status_code == 200
    data = response.json()

    saponified = data["saponified_inci"]
    # Should use Potassium, not Sodium
    assert "Potassium" in saponified
    assert "Sodium" not in saponified
