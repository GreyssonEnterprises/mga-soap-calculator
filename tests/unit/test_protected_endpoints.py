"""Tests for JWT-protected calculation endpoints"""

import uuid
from datetime import timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from passlib.hash import bcrypt

from app.core.security import create_access_token
from app.models.calculation import Calculation
from app.models.user import User


class TestCalculationEndpointAuthentication:
    """Test JWT protection on calculation endpoints"""

    @pytest.mark.asyncio
    async def test_create_calculation_requires_jwt(self, async_client: AsyncClient):
        """Test POST /calculate returns 401 without JWT token"""
        request_data = {
            "oils": [
                {"id": "olive_oil", "percentage": 60.0},
                {"id": "coconut_oil", "percentage": 40.0},
            ],
            "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
            "water": {"method": "water_as_percent_of_oils", "value": 38.0},
            "superfat_percent": 5.0,
        }

        # Request without Authorization header
        response = await async_client.post("/api/v1/calculate", json=request_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_create_calculation_with_invalid_jwt(self, async_client: AsyncClient):
        """Test POST /calculate returns 401 with invalid JWT token"""
        request_data = {
            "oils": [
                {"id": "olive_oil", "percentage": 60.0},
                {"id": "coconut_oil", "percentage": 40.0},
            ],
            "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
            "water": {"method": "water_as_percent_of_oils", "value": 38.0},
            "superfat_percent": 5.0,
        }

        # Request with invalid token
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await async_client.post("/api/v1/calculate", json=request_data, headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_calculation_with_expired_jwt(self, async_client: AsyncClient):
        """Test POST /calculate returns 401 with expired JWT token"""
        # Create expired token
        user_id = str(uuid.uuid4())
        expired_token = create_access_token(
            data={"sub": user_id, "email": "test@example.com"}, expires_delta=timedelta(seconds=-1)
        )

        request_data = {
            "oils": [
                {"id": "olive_oil", "percentage": 60.0},
                {"id": "coconut_oil", "percentage": 40.0},
            ],
            "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
            "water": {"method": "water_as_percent_of_oils", "value": 38.0},
            "superfat_percent": 5.0,
        }

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await async_client.post("/api/v1/calculate", json=request_data, headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "expired" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_calculation_requires_jwt(self, async_client: AsyncClient):
        """Test GET /calculate/{id} returns 401 without JWT token"""
        calc_id = str(uuid.uuid4())

        # Request without Authorization header
        response = await async_client.get(f"/api/v1/calculate/{calc_id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_calculation_with_invalid_jwt(self, async_client: AsyncClient):
        """Test GET /calculate/{id} returns 401 with invalid JWT token"""
        calc_id = str(uuid.uuid4())

        # Request with invalid token
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await async_client.get(f"/api/v1/calculate/{calc_id}", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCalculationOwnershipValidation:
    """Test ownership validation for calculation access"""

    @pytest.mark.asyncio
    async def test_user_can_access_own_calculation(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test user can GET their own calculation"""
        # Create user
        user = User(email="owner@example.com", hashed_password=bcrypt.hash("TestPassword123!"))
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create calculation owned by user
        calculation = Calculation(
            user_id=user.id,
            recipe_data={"oils": [], "lye": {}, "water_weight_g": 100},
            results_data={"quality_metrics": {}},
        )
        test_db_session.add(calculation)
        await test_db_session.commit()
        await test_db_session.refresh(calculation)

        # Create valid JWT for user
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # Request calculation with valid JWT
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get(f"/api/v1/calculate/{calculation.id}", headers=headers)

        # Should succeed since user owns the calculation
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["calculation_id"] == str(calculation.id)
        assert data["user_id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_users_calculation(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test user cannot GET another user's calculation (403 Forbidden)"""
        # Create owner user
        owner_user = User(
            email="owner@example.com", hashed_password=bcrypt.hash("OwnerPassword123!")
        )
        test_db_session.add(owner_user)

        # Create different user
        other_user = User(
            email="other@example.com", hashed_password=bcrypt.hash("OtherPassword123!")
        )
        test_db_session.add(other_user)
        await test_db_session.commit()
        await test_db_session.refresh(owner_user)
        await test_db_session.refresh(other_user)

        # Create calculation owned by owner_user
        calculation = Calculation(
            user_id=owner_user.id,
            recipe_data={"oils": [], "lye": {}, "water_weight_g": 100},
            results_data={"quality_metrics": {}},
        )
        test_db_session.add(calculation)
        await test_db_session.commit()
        await test_db_session.refresh(calculation)

        # Create JWT for other_user (NOT the owner)
        token = create_access_token(data={"sub": str(other_user.id), "email": other_user.email})

        # Try to access owner_user's calculation with other_user's JWT
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get(f"/api/v1/calculate/{calculation.id}", headers=headers)

        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "FORBIDDEN"
        assert "don't own" in data["detail"]["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_get_nonexistent_calculation_returns_404(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test GET for non-existent calculation returns 404"""
        # Create user
        user = User(email="user@example.com", hashed_password=bcrypt.hash("TestPassword123!"))
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create valid JWT
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # Request non-existent calculation
        nonexistent_id = str(uuid.uuid4())
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get(f"/api/v1/calculate/{nonexistent_id}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "NOT_FOUND"
