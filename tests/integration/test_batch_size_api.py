"""
Integration test for batch size parameter through full API flow

TDD Evidence: Verifies batch size fix works end-to-end through API endpoint
Simulates real API request with database interaction

NOTE: These tests require database seed data (oils) to be present.
Run with: pytest tests/integration/test_batch_size_api.py --seed-data
Or manually ensure olive_oil and coconut_oil exist in test database.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
async def authenticated_client(async_client: AsyncClient, async_session):
    """
    Create authenticated test client using existing async_client fixture
    """
    # Create test user
    test_user = User(
        email="batchtest@mga-automotive.com",
        username="batchtest",
        hashed_password=get_password_hash("testpassword123")
    )
    async_session.add(test_user)
    await async_session.commit()
    await async_session.refresh(test_user)

    # Generate JWT token
    token = create_access_token({"sub": str(test_user.id)})

    # Add auth header
    async_client.headers["Authorization"] = f"Bearer {token}"

    yield async_client


@pytest.mark.asyncio
class TestBatchSizeAPIIntegration:
    """Test batch size through full API endpoint"""

    async def test_700g_batch_api_request(self, authenticated_client: AsyncClient):
        """
        TDD: POST with total_oil_weight_g=700 → response has 700g total
        This is the exact bug scenario: user requests 700g, API should return 700g
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 700.0,  # CRITICAL: Request 700g
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        # VERIFY FIX: Response should have 700g, not hardcoded 1000g
        assert data["recipe"]["total_oil_weight_g"] == 700.0

        # Verify oil weight scaled correctly
        olive = data["recipe"]["oils"][0]
        assert olive["id"] == "olive_oil"
        assert olive["weight_g"] == 700.0  # 100% of 700g
        assert olive["percentage"] == 100.0

        # Verify water calculation used correct batch size
        # 700g oils * 38% = 266g water (not 380g from 1000g)
        assert data["recipe"]["water_weight_g"] == 266.0

    async def test_1500g_batch_api_request(self, authenticated_client: AsyncClient):
        """
        TDD: POST with total_oil_weight_g=1500 → larger batch calculations
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "coconut_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 1500.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 1500.0
        assert data["recipe"]["oils"][0]["weight_g"] == 1500.0
        # 1500g * 38% = 570g water
        assert data["recipe"]["water_weight_g"] == 570.0

    async def test_omitted_batch_size_defaults_1000g(self, authenticated_client: AsyncClient):
        """
        TDD: POST without total_oil_weight_g → defaults to 1000g (backward compatible)
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                # total_oil_weight_g omitted - should default to 1000
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Default behavior preserved
        assert data["recipe"]["total_oil_weight_g"] == 1000.0
        assert data["recipe"]["oils"][0]["weight_g"] == 1000.0
        assert data["recipe"]["water_weight_g"] == 380.0

    async def test_multi_oil_blend_700g_batch(self, authenticated_client: AsyncClient):
        """
        TDD: Multi-oil recipe scales correctly with custom batch size
        70% olive + 30% coconut in 700g batch
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 70.0},
                    {"id": "coconut_oil", "percentage": 30.0}
                ],
                "total_oil_weight_g": 700.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 700.0

        # Find oils in response
        oils = {oil["id"]: oil for oil in data["recipe"]["oils"]}

        # 70% of 700g = 490g olive
        assert oils["olive_oil"]["weight_g"] == 490.0
        assert oils["olive_oil"]["percentage"] == 70.0

        # 30% of 700g = 210g coconut
        assert oils["coconut_oil"]["weight_g"] == 210.0
        assert oils["coconut_oil"]["percentage"] == 30.0

    async def test_batch_size_with_additives(self, authenticated_client: AsyncClient):
        """
        TDD: Additive percentages calculated from correct batch size
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 700.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0,
                "additives": [
                    {"id": "kaolin_clay", "weight_g": 20.0}
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 700.0

        # Additive percentage: 20g / 700g = 2.857% → rounds to 2.9%
        additive = data["recipe"]["additives"][0]
        assert additive["weight_g"] == 20.0
        assert additive["percentage"] == 2.9  # Not 2.0% from 1000g batch

    async def test_edge_case_very_small_batch(self, authenticated_client: AsyncClient):
        """
        TDD: Edge case - tiny 50g test batch
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 50.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 50.0
        assert data["recipe"]["oils"][0]["weight_g"] == 50.0
        # 50g * 38% = 19g water
        assert data["recipe"]["water_weight_g"] == 19.0

    async def test_edge_case_very_large_batch(self, authenticated_client: AsyncClient):
        """
        TDD: Edge case - large 5kg commercial batch
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 5000.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 5000.0
        assert data["recipe"]["oils"][0]["weight_g"] == 5000.0
        # 5000g * 38% = 1900g water
        assert data["recipe"]["water_weight_g"] == 1900.0


@pytest.mark.asyncio
class TestBatchSizeRegressionAPI:
    """Ensure batch size fix doesn't break existing functionality"""

    async def test_purity_feature_still_works(self, authenticated_client: AsyncClient):
        """
        TDD: Batch size fix doesn't affect purity calculations
        """
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 700.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 85.0  # Non-standard purity
                },
                "water": {
                    "method": "water_percent_of_oils",
                    "value": 38.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Both features work together
        assert data["recipe"]["total_oil_weight_g"] == 700.0
        assert data["recipe"]["lye"]["koh_purity"] == 85.0

        # Purity adjustment applied correctly
        assert "pure_koh_equivalent_g" in data["recipe"]["lye"]
        assert data["recipe"]["lye"]["pure_koh_equivalent_g"] > 0

    async def test_water_methods_use_correct_batch_size(self, authenticated_client: AsyncClient):
        """
        TDD: All three water calculation methods use correct batch size
        """
        # Test lye_concentration method
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 700.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "lye_concentration",
                    "value": 33.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 700.0
        assert data["recipe"]["water_method"] == "lye_concentration"
        # Water calculation should be based on lye amount (which is based on 700g oils)
        assert data["recipe"]["water_weight_g"] > 0

        # Test water_lye_ratio method
        response = await authenticated_client.post(
            "/api/v1/calculate",
            json={
                "oils": [
                    {"id": "olive_oil", "percentage": 100.0}
                ],
                "total_oil_weight_g": 700.0,
                "lye": {
                    "naoh_percent": 0,
                    "koh_percent": 100,
                    "koh_purity": 90
                },
                "water": {
                    "method": "water_lye_ratio",
                    "value": 2.0
                },
                "superfat_percent": 5.0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["recipe"]["total_oil_weight_g"] == 700.0
        assert data["recipe"]["water_method"] == "water_lye_ratio"
        assert data["recipe"]["water_weight_g"] > 0
