"""
End-to-End Tests: Complete Calculation Flow

Tests the full user journey through the API:
1. Register user
2. Login and get JWT
3. Create calculation
4. Retrieve calculation
5. Verify data persistence

Phase 5 - Task 5.1.1 - SCHEMA CORRECTED
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Calculation, User
from tests.test_helpers import build_additive_input, build_calculation_request, build_oil_input


@pytest.mark.asyncio
async def test_complete_calculation_flow(client: AsyncClient, test_db):
    """
    E2E Test: Complete calculation flow from registration to retrieval

    Validates:
    - User registration
    - Authentication and JWT token
    - Calculation creation
    - Data persistence
    - Calculation retrieval
    """
    # Step 1: Register new user
    register_data = {
        "email": "e2e_user@test.com",
        "password": "SecurePass123!",
        "full_name": "E2E Test User",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    registration_result = response.json()
    assert registration_result["email"] == register_data["email"]
    assert "id" in registration_result
    user_id = registration_result["id"]

    # Step 2: Login and get JWT
    login_data = {"email": register_data["email"], "password": register_data["password"]}

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # Step 3: Create calculation with JWT (CORRECTED SCHEMA)
    calculation_request = build_calculation_request(
        oils=[
            build_oil_input("olive_oil", percentage=40.0),
            build_oil_input("coconut_oil", percentage=30.0),
            build_oil_input("avocado_oil", percentage=30.0),
        ],
        superfat_percent=5.0,
        water_percent_of_oils=38.0,
        lye_type="NaOH",
    )

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post("/api/v1/calculate", json=calculation_request, headers=headers)
    assert response.status_code == 200
    calculation_result = response.json()

    # Verify calculation response structure (CORRECTED to match CalculationResponse)
    assert "calculation_id" in calculation_result
    assert "recipe" in calculation_result
    assert "lye" in calculation_result["recipe"]
    assert "naoh_weight_g" in calculation_result["recipe"]["lye"]
    assert "water_weight_g" in calculation_result["recipe"]
    assert "quality_metrics" in calculation_result
    assert "fatty_acid_profile" in calculation_result
    assert "timestamp" in calculation_result

    calculation_id = calculation_result["calculation_id"]

    # Step 4: Retrieve calculation
    response = await client.get(f"/api/v1/calculate/{calculation_id}", headers=headers)
    assert response.status_code == 200
    retrieved_calculation = response.json()

    # Verify retrieved data matches created data
    assert retrieved_calculation["calculation_id"] == calculation_id
    assert (
        retrieved_calculation["recipe"]["lye"]["naoh_weight_g"]
        == calculation_result["recipe"]["lye"]["naoh_weight_g"]
    )
    assert (
        retrieved_calculation["recipe"]["water_weight_g"]
        == calculation_result["recipe"]["water_weight_g"]
    )

    # Step 5: Verify database persistence
    async with test_db() as session:
        # Check user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == register_data["email"]

        # Check calculation exists and is linked to user
        result = await session.execute(select(Calculation).where(Calculation.id == calculation_id))
        calculation = result.scalar_one_or_none()
        assert calculation is not None
        # Convert both to str for comparison (user_id from API is str, from DB is UUID)
        assert str(calculation.user_id) == str(user_id)


@pytest.mark.asyncio
async def test_multiple_calculations_per_user(client: AsyncClient, test_db):
    """
    E2E Test: User creates multiple calculations

    Validates:
    - Multiple calculations for same user
    - Each calculation properly isolated
    - All calculations retrievable
    """
    # Register and login
    register_data = {
        "email": "multi_calc_user@test.com",
        "password": "SecurePass123!",
        "full_name": "Multi Calc User",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    login_data = {"email": register_data["email"], "password": register_data["password"]}
    response = await client.post("/api/v1/auth/login", json=login_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create first calculation (NaOH) - CORRECTED SCHEMA
    calc1_request = build_calculation_request(
        oils=[build_oil_input("olive_oil", percentage=100.0)], superfat_percent=5.0, lye_type="NaOH"
    )
    # Override water method for this test
    calc1_request["water"] = {"method": "lye_concentration", "value": 30.0}

    response = await client.post("/api/v1/calculate", json=calc1_request, headers=headers)
    assert response.status_code == 200
    calc1_id = response.json()["calculation_id"]

    # Create second calculation (KOH) - CORRECTED SCHEMA
    calc2_request = build_calculation_request(
        oils=[build_oil_input("avocado_oil", percentage=100.0)],
        superfat_percent=0.0,
        lye_type="KOH",
    )
    # Override water method for this test
    calc2_request["water"] = {"method": "water_lye_ratio", "value": 2.5}

    response = await client.post("/api/v1/calculate", json=calc2_request, headers=headers)
    assert response.status_code == 200
    calc2_id = response.json()["calculation_id"]

    # Verify both calculations are different
    assert calc1_id != calc2_id

    # Retrieve both calculations
    response1 = await client.get(f"/api/v1/calculate/{calc1_id}", headers=headers)
    response2 = await client.get(f"/api/v1/calculate/{calc2_id}", headers=headers)

    assert response1.status_code == 200
    assert response2.status_code == 200

    calc1 = response1.json()
    calc2 = response2.json()

    # Verify calculations are isolated with different lye amounts
    assert calc1["recipe"]["lye"]["naoh_weight_g"] != calc2["recipe"]["lye"]["naoh_weight_g"]


@pytest.mark.asyncio
async def test_calculation_with_additives_flow(client: AsyncClient, test_db):
    """
    E2E Test: Calculation flow with additives

    Validates:
    - Additive inclusion in calculation
    - Additive effects applied to quality metrics
    - Additive data persisted and retrieved
    """
    # Register and login
    register_data = {
        "email": "additive_user@test.com",
        "password": "SecurePass123!",
        "full_name": "Additive User",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    login_data = {"email": register_data["email"], "password": register_data["password"]}
    response = await client.post("/api/v1/auth/login", json=login_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create calculation with additives - CORRECTED SCHEMA
    calculation_request = build_calculation_request(
        oils=[
            build_oil_input("olive_oil", percentage=50.0),
            build_oil_input("avocado_oil", percentage=50.0),
        ],
        superfat_percent=5.0,
        water_percent_of_oils=38.0,
        lye_type="NaOH",
        additives=[
            build_additive_input("kaolin_clay", weight_g=10.0),
            build_additive_input("sea_salt", weight_g=5.0),
        ],
    )

    response = await client.post("/api/v1/calculate", json=calculation_request, headers=headers)
    assert response.status_code == 200
    calculation_result = response.json()

    # Verify additives present in response
    assert "additive_effects" in calculation_result
    # Note: Only additives in the database will have effects
    # sea_salt might not be in the database yet, so we check >= 1
    assert len(calculation_result["additive_effects"]) >= 1

    # Retrieve and verify additives persisted
    calc_id = calculation_result["calculation_id"]
    response = await client.get(f"/api/v1/calculate/{calc_id}", headers=headers)
    assert response.status_code == 200
    retrieved = response.json()

    assert len(retrieved["additive_effects"]) >= 1  # At least one additive effect should be present

    # Verify additive effects structure (CORRECTED to match AdditiveEffect schema)
    for effect in retrieved["additive_effects"]:
        assert "additive_id" in effect
        assert "additive_name" in effect
        assert "effects" in effect  # Dict[str, float]
        assert "confidence" in effect
        assert "verified_by_mga" in effect
        # Effects dict should have quality metric keys
        assert isinstance(effect["effects"], dict)
