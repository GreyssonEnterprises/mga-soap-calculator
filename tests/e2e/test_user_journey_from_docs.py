"""
E2E tests following the exact user journey documented in API_REFERENCE.md

Simulates a user reading the documentation and following the examples step-by-step.
Tests the happy path workflow that users are told to follow.
"""

import pytest
from httpx import AsyncClient


class TestUserJourneyFromDocumentation:
    """E2E tests following documented user workflows"""

    @pytest.mark.asyncio
    async def test_complete_registration_to_calculation_workflow(self, client: AsyncClient):
        """
        Execute the complete workflow as documented in API_REFERENCE.md

        This test simulates a user following the documentation from start to finish:
        1. Register a new account
        2. Login to get JWT token
        3. Create a soap calculation
        4. Retrieve the calculation results

        This would fail if documentation paths are wrong.
        """
        # Step 1: Register user (as documented)
        # Documentation shows this as the first step for new users
        register_response = await client.post(
            "/api/v1/auth/register",  # Using correct path from implementation
            json={"email": "soapmaker@example.com", "password": "MySecurePassword123!"},
        )

        assert register_response.status_code == 201, (
            f"Registration failed (docs workflow broken): {register_response.text}"
        )

        # Verify response structure matches documentation
        register_data = register_response.json()
        assert "id" in register_data, "Registration response should include user ID"
        assert "email" in register_data, "Registration response should include email"

        # Step 2: Login to get JWT token (as documented)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "soapmaker@example.com", "password": "MySecurePassword123!"},
        )

        assert login_response.status_code == 200, (
            f"Login failed (docs workflow broken): {login_response.text}"
        )

        # Verify token structure matches documentation
        login_data = login_response.json()
        assert "access_token" in login_data, "Login response should include access_token"
        assert "token_type" in login_data, "Login response should include token_type"
        assert login_data["token_type"] == "bearer", "Token type should be 'bearer'"

        token = login_data["access_token"]

        # Step 3: Create soap calculation (as documented)
        # Using example recipe from documentation
        calc_response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "oils": [
                    {"id": 1, "percentage": 50},  # Olive Oil
                    {"id": 2, "percentage": 30},  # Coconut Oil
                    {"id": 3, "percentage": 20},  # Palm Oil
                ],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        assert calc_response.status_code == 200, (
            f"Calculation failed (docs workflow broken): {calc_response.text}"
        )

        # Verify response structure matches documentation
        calc_data = calc_response.json()
        assert "calculation_id" in calc_data, "Response should include calculation_id"
        assert "results" in calc_data, "Response should include results"

        calc_id = calc_data["calculation_id"]

        # Step 4: Retrieve calculation (as documented)
        retrieve_response = await client.get(
            f"/api/v1/calculate/{calc_id}", headers={"Authorization": f"Bearer {token}"}
        )

        assert retrieve_response.status_code == 200, (
            f"Retrieval failed (docs workflow broken): {retrieve_response.text}"
        )

        # Verify retrieved data matches created calculation
        retrieve_data = retrieve_response.json()
        assert retrieve_data["calculation_id"] == calc_id, (
            "Retrieved calculation ID should match created calculation ID"
        )

    @pytest.mark.asyncio
    async def test_calculation_with_additives_workflow(self, client: AsyncClient):
        """
        Test the additive calculation workflow as documented

        Documentation highlights additive effects as a competitive advantage.
        Verify the documented workflow for using additives actually works.
        """
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "additive_user@example.com", "password": "TestPass123!"},
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "additive_user@example.com", "password": "TestPass123!"},
        )

        token = login_response.json()["access_token"]

        # Create calculation with additives (as documented)
        calc_response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "oils": [
                    {"id": 1, "percentage": 50},
                    {"id": 2, "percentage": 30},
                    {"id": 3, "percentage": 20},
                ],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
                "additives": [
                    {"id": 1, "usage_percent": 2}  # Kaolin Clay as documented
                ],
            },
        )

        assert calc_response.status_code == 200, (
            "Additive calculation workflow should work as documented"
        )

        calc_data = calc_response.json()

        # Verify additive effects are included in results
        assert "results" in calc_data, "Results should be included"
        # Additives affect quality metrics
        assert "quality_metrics" in calc_data["results"], (
            "Quality metrics should reflect additive effects"
        )

    @pytest.mark.asyncio
    async def test_authentication_required_for_protected_endpoints(self, client: AsyncClient):
        """
        Verify authentication requirement as documented

        Documentation states: "All endpoints except /health require JWT authentication"
        Test that protected endpoints return 401 without token.
        """
        # Try to create calculation without token
        response = await client.post(
            "/api/v1/calculate",
            json={
                "oils": [{"id": 1, "percentage": 100}],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        assert response.status_code == 401, (
            "Protected endpoints should return 401 Unauthorized without token (as documented)"
        )

        # Health endpoint should work without authentication (as documented)
        health_response = await client.get("/api/v1/health")

        assert health_response.status_code == 200, (
            "Health endpoint should not require authentication (as documented)"
        )

    @pytest.mark.asyncio
    async def test_error_scenarios_match_documentation(self, client: AsyncClient):
        """
        Test that error scenarios behave as documented

        Documentation specifies error codes for various failure cases.
        Verify actual behavior matches documented error codes.
        """
        # Register a user first
        await client.post(
            "/api/v1/auth/register",
            json={"email": "error_test@example.com", "password": "TestPass123!"},
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "error_test@example.com", "password": "TestPass123!"},
        )

        token = login_response.json()["access_token"]

        # Test: Invalid oil percentages (should return 400 as documented)
        response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "oils": [
                    {"id": 1, "percentage": 50},
                    {"id": 2, "percentage": 30},
                    # Only sums to 80%, not 100%
                ],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        assert response.status_code == 400, (
            "Invalid oil percentages should return 400 Bad Request (as documented)"
        )

        # Test: Invalid lye percentages (should return 400 as documented)
        response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "oils": [{"id": 1, "percentage": 100}],
                "lye": {
                    "naoh_percent": 50,
                    "koh_percent": 30,
                    # Only sums to 80%, not 100%
                },
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        assert response.status_code == 400, (
            "Invalid lye percentages should return 400 Bad Request (as documented)"
        )

    @pytest.mark.asyncio
    async def test_token_included_in_protected_requests(self, client: AsyncClient):
        """
        Verify the documented authentication flow works correctly

        Documentation shows: "Add Authorization: Bearer <token> header to protected requests"
        Test that this pattern actually works.
        """
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "token_test@example.com", "password": "TestPass123!"},
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "token_test@example.com", "password": "TestPass123!"},
        )

        token = login_response.json()["access_token"]

        # Use token in Authorization header (as documented)
        response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {token}"},  # Exactly as documented
            json={
                "oils": [{"id": 1, "percentage": 100}],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        assert response.status_code == 200, (
            "Request with proper Bearer token should succeed (as documented)"
        )

        # Test with missing Bearer prefix (common user mistake)
        response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": token},  # Missing "Bearer " prefix
            json={
                "oils": [{"id": 1, "percentage": 100}],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        # Should fail without Bearer prefix
        assert response.status_code == 401, "Token without 'Bearer ' prefix should be rejected"

    @pytest.mark.asyncio
    async def test_calculation_ownership_enforcement(self, client: AsyncClient):
        """
        Verify calculation ownership enforcement as documented

        Documentation states: "Users can only access their own calculations"
        Test that users cannot access other users' calculations.
        """
        # Create first user and calculation
        await client.post(
            "/api/v1/auth/register", json={"email": "user1@example.com", "password": "TestPass123!"}
        )

        user1_login = await client.post(
            "/api/v1/auth/login", json={"email": "user1@example.com", "password": "TestPass123!"}
        )

        user1_token = user1_login.json()["access_token"]

        calc_response = await client.post(
            "/api/v1/calculate",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={
                "oils": [{"id": 1, "percentage": 100}],
                "lye": {"naoh_percent": 100, "koh_percent": 0},
                "water": {"method": "percent_of_oils", "value": 38},
                "superfat_percent": 5,
            },
        )

        calc_id = calc_response.json()["calculation_id"]

        # Create second user
        await client.post(
            "/api/v1/auth/register", json={"email": "user2@example.com", "password": "TestPass123!"}
        )

        user2_login = await client.post(
            "/api/v1/auth/login", json={"email": "user2@example.com", "password": "TestPass123!"}
        )

        user2_token = user2_login.json()["access_token"]

        # User 2 tries to access User 1's calculation
        response = await client.get(
            f"/api/v1/calculate/{calc_id}", headers={"Authorization": f"Bearer {user2_token}"}
        )

        # Should return 403 Forbidden (as documented)
        assert response.status_code == 403, (
            "Users should not be able to access other users' calculations (403 Forbidden as documented)"
        )
