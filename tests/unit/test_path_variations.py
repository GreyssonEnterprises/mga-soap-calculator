"""
Tests for common path variations and mistakes

Tests that wrong paths fail appropriately and correct paths work as expected.
Documents expected behavior for edge cases and common user mistakes.

This file extends existing path variation tests with comprehensive coverage.
"""
import pytest
from httpx import AsyncClient
from fastapi import status


class TestPathVariations:
    """Test common path mistakes and correct path usage"""

    @pytest.mark.asyncio
    async def test_missing_api_v1_prefix_returns_404(self, async_client: AsyncClient):
        """
        Verify common user mistake (missing /api/v1/ prefix) returns 404

        Users might try /auth/register instead of /api/v1/auth/register
        especially if documentation is unclear about the prefix requirement.
        """
        test_data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }

        # Wrong path: missing /api/v1/ prefix entirely
        response = await async_client.post("/auth/register", json=test_data)

        assert response.status_code == 404, \
            "Path without /api/v1/ prefix should return 404 Not Found"

        # Verify error message indicates not found
        data = response.json()
        assert "detail" in data, "Error response should include detail"

    @pytest.mark.asyncio
    async def test_missing_v1_only_returns_404(self, async_client: AsyncClient):
        """
        Verify another common mistake (missing just /v1/) returns 404

        Users might try /api/auth/register instead of /api/v1/auth/register
        """
        test_data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }

        # Wrong path: has /api/ but missing /v1/
        response = await async_client.post("/api/auth/register", json=test_data)

        assert response.status_code == 404, \
            "Path with /api/ but without /v1/ should return 404 Not Found"

    @pytest.mark.asyncio
    async def test_missing_api_only_returns_404(self, async_client: AsyncClient):
        """
        Test path with /v1/ but missing /api/ prefix

        Less common mistake but should still return 404.
        """
        test_data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }

        # Wrong path: has /v1/ but missing /api/
        response = await async_client.post("/v1/auth/register", json=test_data)

        assert response.status_code == 404, \
            "Path with /v1/ but without /api/ should return 404 Not Found"

    @pytest.mark.asyncio
    async def test_correct_path_works_for_registration(self, async_client: AsyncClient):
        """
        Positive control: verify correct path actually works

        This is the path users SHOULD use: /api/v1/auth/register
        """
        test_data = {
            "email": "correct_path_test@example.com",
            "password": "TestPass123!"
        }

        # Correct path: /api/v1/auth/register
        response = await async_client.post("/api/v1/auth/register", json=test_data)

        assert response.status_code == 201, \
            "Correct path /api/v1/auth/register should return 201 Created"

        # Verify response structure
        data = response.json()
        assert "id" in data, "Response should include user ID"
        assert "email" in data, "Response should include email"

    @pytest.mark.asyncio
    async def test_correct_path_works_for_login(self, async_client: AsyncClient, test_db_session):
        """
        Verify correct login path works

        Path: /api/v1/auth/login
        """
        from app.models.user import User
        from passlib.hash import bcrypt

        # Create user first
        user = User(
            email="login_path_test@example.com",
            hashed_password=bcrypt.hash("TestPass123!")
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Correct path: /api/v1/auth/login
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "login_path_test@example.com",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 200, \
            "Correct path /api/v1/auth/login should return 200 OK"

        data = response.json()
        assert "access_token" in data, "Response should include JWT token"

    @pytest.mark.asyncio
    async def test_case_sensitivity_of_paths(self, async_client: AsyncClient):
        """
        Test whether paths are case-sensitive

        Users might try /api/v1/Auth/Register instead of /api/v1/auth/register
        """
        test_data = {
            "email": "case_test@example.com",
            "password": "TestPass123!"
        }

        # Wrong case: Auth instead of auth
        response = await async_client.post("/api/v1/Auth/Register", json=test_data)

        # FastAPI paths are case-sensitive by default
        assert response.status_code == 404, \
            "Paths should be case-sensitive - /Auth/Register should return 404"

    @pytest.mark.asyncio
    async def test_calculate_endpoint_path_variations(self, async_client: AsyncClient, test_db_session):
        """
        Test path variations for calculate endpoint

        Ensures /api/v1/calculate is the only valid path.
        """
        from app.models.user import User
        from passlib.hash import bcrypt
        from app.core.security import create_access_token

        # Create user and token
        user = User(
            email="calc_path_test@example.com",
            hashed_password=bcrypt.hash("TestPass123!")
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        token = create_access_token({"sub": str(user.id), "email": user.email})

        test_calc = {
            "oils": [{"id": 1, "percentage": 100}],
            "lye": {"naoh_percent": 100, "koh_percent": 0},
            "water": {"method": "percent_of_oils", "value": 38},
            "superfat_percent": 5
        }

        # Test wrong paths
        wrong_paths = [
            "/calculate",              # Missing /api/v1
            "/api/calculate",          # Missing /v1
            "/v1/calculate",           # Missing /api
        ]

        for wrong_path in wrong_paths:
            response = await async_client.post(
                wrong_path,
                headers={"Authorization": f"Bearer {token}"},
                json=test_calc
            )

            assert response.status_code == 404, \
                f"Wrong path {wrong_path} should return 404"

        # Test correct path
        response = await async_client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json=test_calc
        )

        assert response.status_code == 200, \
            "Correct path /api/v1/calculate should work"

    @pytest.mark.asyncio
    async def test_health_endpoint_path_variations(self, async_client: AsyncClient):
        """
        Test health endpoint path variations

        Health endpoint should work at /api/v1/health
        """
        # Correct path
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200, \
            "Health endpoint should work at /api/v1/health"

        # Test if /health (without /api/v1) also works
        response = await async_client.get("/health")

        # The main.py shows health at /api/v1/health, so /health should return 404
        # This documents the expected behavior
