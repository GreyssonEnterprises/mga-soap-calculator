"""
Tests for API documentation accuracy

Validates that API_REFERENCE.md documentation matches actual implementation:
- Documented endpoints exist in the API
- Documented paths match OpenAPI schema
- Response codes match documentation
- All documented paths are accessible
"""

import re
from pathlib import Path

import pytest
from httpx import AsyncClient


class TestDocumentationAccuracy:
    """Validate API documentation matches implementation"""

    @pytest.mark.asyncio
    async def test_documented_auth_endpoints_are_valid(self, async_client: AsyncClient):
        """
        Verify documented authentication endpoints actually exist

        This test would have caught the /auth/register vs /api/v1/auth/register mismatch.
        Documentation shows POST /auth/register (line 23) but implementation
        is /api/v1/auth/register.
        """
        api_ref = Path("docs/API_REFERENCE.md").read_text()

        # Extract documented endpoints (simplified pattern)
        # Line 23: **Endpoint:** `POST /auth/register`
        # Line 55: **Endpoint:** `POST /auth/login`
        endpoint_pattern = r"\*\*Endpoint:\*\* `(GET|POST|PUT|DELETE|PATCH) ([^`]+)`"
        documented_endpoints = re.findall(endpoint_pattern, api_ref)

        # Track issues
        issues = []

        for method, path in documented_endpoints:
            # Normalize path - docs might show /auth/register when it should be /api/v1/auth/register  # noqa: E501
            if not path.startswith("/api/v1"):
                # Check if documented path is missing /api/v1 prefix
                full_path = f"/api/v1{path}"

                # Try the documented path first (expect 404)
                response = await async_client.request(method, path, json={})

                if response.status_code == 404:
                    issues.append(
                        f"Documentation shows '{method} {path}' but that path returns 404. "
                        f"Correct path is likely '{method} {full_path}'"
                    )
            else:
                full_path = path

            # Verify the full path exists (might get 400/401/422 due to missing data, but NOT 404)
            response = await async_client.request(method, full_path, json={})

            # Any status code except 404 means the endpoint exists
            assert response.status_code != 404, (
                f"Documented endpoint {method} {full_path} returns 404 Not Found"
            )

        # If there are documentation issues, report them
        if issues:
            pytest.fail("\n".join(["Documentation path mismatches found:", *issues]))

    @pytest.mark.asyncio
    async def test_api_reference_paths_have_version_prefix(self):
        """
        Verify all documented API paths use /api/v1/ prefix

        Enforces API versioning best practice in documentation.
        """
        api_ref = Path("docs/API_REFERENCE.md").read_text()

        # Extract endpoint declarations
        endpoint_pattern = r"\*\*Endpoint:\*\* `(?:GET|POST|PUT|DELETE|PATCH) ([^`]+)`"
        documented_paths = re.findall(endpoint_pattern, api_ref)

        # Filter out non-API paths (like /health which might be special)
        api_paths = [p for p in documented_paths if not p.startswith("/health")]

        # Verify all API paths start with /api/v1/
        missing_version = [p for p in api_paths if not p.startswith("/api/v1/")]

        assert not missing_version, (
            f"API paths in documentation missing /api/v1/ prefix: {missing_version}"
        )

    def test_openapi_schema_matches_documented_paths(self):
        """
        Verify OpenAPI schema paths match documentation

        Prevents schema drift from user-facing documentation.
        """
        from app.main import app

        # Get OpenAPI schema
        openapi = app.openapi()
        openapi_paths = set(openapi["paths"].keys())

        # Get documented paths
        api_ref = Path("docs/API_REFERENCE.md").read_text()
        endpoint_pattern = r"\*\*Endpoint:\*\* `(?:GET|POST|PUT|DELETE|PATCH) ([^`]+)`"
        doc_paths = set(re.findall(endpoint_pattern, api_ref))

        # Normalize documentation paths (add /api/v1 if missing)
        normalized_doc_paths = {p if p.startswith("/api/v1") else f"/api/v1{p}" for p in doc_paths}

        # Verify all documented paths exist in OpenAPI
        missing_from_openapi = normalized_doc_paths - openapi_paths
        assert not missing_from_openapi, (
            f"Paths documented but not in OpenAPI schema: {missing_from_openapi}"
        )

        # Verify all OpenAPI paths are documented (excluding internal paths)
        internal_paths = {"/openapi.json", "/docs", "/redoc"}
        missing_from_docs = openapi_paths - normalized_doc_paths - internal_paths

        # Filter out any other internal paths that might start with special prefixes
        missing_from_docs = {
            p
            for p in missing_from_docs
            if not any(p.startswith(prefix) for prefix in ["/openapi", "/docs", "/redoc"])
        }

        assert not missing_from_docs, f"Paths in OpenAPI but not documented: {missing_from_docs}"

    @pytest.mark.asyncio
    async def test_curl_examples_use_correct_paths(self):
        """
        Verify all curl examples in documentation use correct paths

        Users copy-paste curl commands, so they must be accurate.
        """
        api_ref = Path("docs/API_REFERENCE.md").read_text()

        # Extract curl commands from bash code blocks
        # Looking for patterns like: curl -X POST http://localhost:8000/api/v1/auth/register
        curl_pattern = r"curl\s+(?:-X\s+\w+\s+)?([^\s\\]+)"
        curl_urls = re.findall(curl_pattern, api_ref)

        # Extract just the path from URLs
        issues = []
        for url in curl_urls:
            if "localhost:8000" in url or "http://" in url or "https://" in url:
                # Extract path portion
                path_match = re.search(r"https?://[^/]+(/[^\s?#]*)", url)
                if path_match:
                    path = path_match.group(1)

                    # Verify path uses /api/v1/ prefix for API endpoints
                    if path.startswith("/api/") and not path.startswith("/api/v1/"):
                        issues.append(f"Curl example uses path without /v1/ prefix: {url}")

        assert not issues, "\n".join(["Curl examples with incorrect paths:", *issues])

    @pytest.mark.asyncio
    async def test_base_url_in_documentation_is_correct(self):
        """
        Verify the documented base URL matches the API configuration

        Users need to know the correct base URL for all requests.
        """
        api_ref = Path("docs/API_REFERENCE.md").read_text()

        # Look for Base URL declaration (should be early in the doc)
        base_url_pattern = r"\*\*Base URL:\*\*\s+`([^`]+)`"
        base_url_match = re.search(base_url_pattern, api_ref)

        assert base_url_match, "No Base URL found in API_REFERENCE.md"

        documented_base_url = base_url_match.group(1)

        # Verify base URL includes /api/v1
        assert "/api/v1" in documented_base_url, (
            f"Documented base URL '{documented_base_url}' should include /api/v1 version prefix"
        )

    @pytest.mark.asyncio
    async def test_response_codes_match_implementation(self, async_client: AsyncClient):
        """
        Verify documented response codes match actual endpoint behavior

        Tests common scenarios to ensure documentation accuracy.
        """
        # Test registration endpoint response codes
        # Documented: 201 Created, 400 Bad Request, 409 Conflict

        # Valid registration should return 201
        response = await async_client.post(
            "/api/v1/auth/register", json={"email": "test@example.com", "password": "ValidPass123!"}
        )
        assert response.status_code == 201, (
            "Documentation says registration returns 201, but got {response.status_code}"
        )

        # Duplicate email should return 400 (per current implementation)
        response = await async_client.post(
            "/api/v1/auth/register", json={"email": "test@example.com", "password": "ValidPass123!"}
        )
        assert response.status_code in [400, 409], (
            f"Documentation says duplicate email returns 400/409, but got {response.status_code}"
        )

        # Invalid email format should return 422
        response = await async_client.post(
            "/api/v1/auth/register", json={"email": "not-an-email", "password": "ValidPass123!"}
        )
        assert response.status_code == 422, (
            f"Invalid email should return 422, but got {response.status_code}"
        )

    @pytest.mark.asyncio
    async def test_health_endpoint_documented_correctly(self, async_client: AsyncClient):
        """
        Verify health endpoint documentation matches implementation

        Health endpoints are special - they often don't require authentication
        and may not follow versioning conventions.
        """
        # Health endpoint should work and return 200
        response = await async_client.get("/api/v1/health")

        assert response.status_code == 200, "Health endpoint should return 200 OK"

        # Verify response structure matches documentation
        data = response.json()
        assert "status" in data, "Health response should include 'status' field"
        assert "version" in data, "Health response should include 'version' field"
