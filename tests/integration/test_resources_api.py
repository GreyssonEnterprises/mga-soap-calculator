"""
Integration tests for resource discovery API endpoints.

Tests with actual test database to verify:
- Response schemas match Pydantic models
- Search functionality works correctly
- Pagination metadata is accurate
- Sorting works as expected
- Filtering produces correct results
"""
import pytest
from httpx import AsyncClient
from fastapi import status


class TestOilsEndpointIntegration:
    """Integration tests for GET /api/v1/oils endpoint"""

    @pytest.mark.asyncio
    async def test_list_oils_returns_200(self, async_client: AsyncClient):
        """Test oils endpoint returns 200 OK"""
        response = await async_client.get("/api/v1/oils")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_list_oils_response_schema(self, async_client: AsyncClient):
        """Test oils endpoint response matches schema"""
        response = await async_client.get("/api/v1/oils")
        data = response.json()

        # Verify top-level structure
        assert "oils" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data

        # Verify types
        assert isinstance(data["oils"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)
        assert isinstance(data["has_more"], bool)

        # Verify defaults
        assert data["limit"] == 50
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_oils_item_schema(self, async_client: AsyncClient):
        """Test individual oil items match schema"""
        response = await async_client.get("/api/v1/oils")
        data = response.json()

        if len(data["oils"]) > 0:
            oil = data["oils"][0]

            # Required fields
            assert "id" in oil
            assert "common_name" in oil
            assert "inci_name" in oil
            assert "sap_value_naoh" in oil
            assert "sap_value_koh" in oil
            assert "iodine_value" in oil
            assert "ins_value" in oil
            assert "fatty_acids" in oil
            assert "quality_contributions" in oil

            # Types
            assert isinstance(oil["id"], str)
            assert isinstance(oil["common_name"], str)
            assert isinstance(oil["inci_name"], str)
            assert isinstance(oil["sap_value_naoh"], (int, float))
            assert isinstance(oil["sap_value_koh"], (int, float))
            assert isinstance(oil["iodine_value"], (int, float))
            assert isinstance(oil["ins_value"], (int, float))
            assert isinstance(oil["fatty_acids"], dict)
            assert isinstance(oil["quality_contributions"], dict)

    @pytest.mark.asyncio
    async def test_list_oils_search_by_common_name(self, async_client: AsyncClient):
        """Test search functionality finds oils by common name"""
        # Search for "olive" (should match "Olive Oil")
        response = await async_client.get("/api/v1/oils?search=olive")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # All results should contain "olive" in common_name or inci_name (case-insensitive)
        for oil in data["oils"]:
            assert (
                "olive" in oil["common_name"].lower()
                or "olive" in oil["inci_name"].lower()
            ), f"Oil {oil['id']} doesn't match search term 'olive'"

    @pytest.mark.asyncio
    async def test_list_oils_search_by_inci_name(self, async_client: AsyncClient):
        """Test search functionality finds oils by INCI name"""
        # Search for "cocos" (should match "Cocos Nucifera Oil" - Coconut)
        response = await async_client.get("/api/v1/oils?search=cocos")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["total_count"] > 0

        # All results should contain "cocos" (case-insensitive)
        for oil in data["oils"]:
            assert (
                "cocos" in oil["common_name"].lower()
                or "cocos" in oil["inci_name"].lower()
            )

    @pytest.mark.asyncio
    async def test_list_oils_search_case_insensitive(self, async_client: AsyncClient):
        """Test search is case-insensitive"""
        # Try different cases
        response_lower = await async_client.get("/api/v1/oils?search=olive")
        response_upper = await async_client.get("/api/v1/oils?search=OLIVE")
        response_mixed = await async_client.get("/api/v1/oils?search=OlIvE")

        data_lower = response_lower.json()
        data_upper = response_upper.json()
        data_mixed = response_mixed.json()

        # All should return same count
        assert data_lower["total_count"] == data_upper["total_count"]
        assert data_lower["total_count"] == data_mixed["total_count"]

    @pytest.mark.asyncio
    async def test_list_oils_search_no_results(self, async_client: AsyncClient):
        """Test search with no matching results"""
        response = await async_client.get("/api/v1/oils?search=nonexistent_oil_xyz")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["total_count"] == 0
        assert len(data["oils"]) == 0
        assert data["has_more"] is False

    @pytest.mark.asyncio
    async def test_list_oils_sort_by_common_name_asc(self, async_client: AsyncClient):
        """Test sorting by common_name ascending"""
        response = await async_client.get("/api/v1/oils?sort_by=common_name&sort_order=asc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Extract names
        names = [oil["common_name"] for oil in data["oils"]]

        # Verify sorted
        assert names == sorted(names), "Oils not sorted by common_name ascending"

    @pytest.mark.asyncio
    async def test_list_oils_sort_by_common_name_desc(self, async_client: AsyncClient):
        """Test sorting by common_name descending"""
        response = await async_client.get("/api/v1/oils?sort_by=common_name&sort_order=desc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        names = [oil["common_name"] for oil in data["oils"]]
        assert names == sorted(names, reverse=True), "Oils not sorted by common_name descending"

    @pytest.mark.asyncio
    async def test_list_oils_sort_by_ins_value_asc(self, async_client: AsyncClient):
        """Test sorting by ins_value ascending"""
        response = await async_client.get("/api/v1/oils?sort_by=ins_value&sort_order=asc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        ins_values = [oil["ins_value"] for oil in data["oils"]]
        assert ins_values == sorted(ins_values), "Oils not sorted by ins_value ascending"

    @pytest.mark.asyncio
    async def test_list_oils_sort_by_ins_value_desc(self, async_client: AsyncClient):
        """Test sorting by ins_value descending"""
        response = await async_client.get("/api/v1/oils?sort_by=ins_value&sort_order=desc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        ins_values = [oil["ins_value"] for oil in data["oils"]]
        assert ins_values == sorted(ins_values, reverse=True), "Oils not sorted by ins_value descending"

    @pytest.mark.asyncio
    async def test_list_oils_sort_by_iodine_value_asc(self, async_client: AsyncClient):
        """Test sorting by iodine_value ascending"""
        response = await async_client.get("/api/v1/oils?sort_by=iodine_value&sort_order=asc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        iodine_values = [oil["iodine_value"] for oil in data["oils"]]
        assert iodine_values == sorted(iodine_values), "Oils not sorted by iodine_value ascending"

    @pytest.mark.asyncio
    async def test_list_oils_pagination_limit(self, async_client: AsyncClient):
        """Test pagination limit parameter"""
        response = await async_client.get("/api/v1/oils?limit=5")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["limit"] == 5
        assert len(data["oils"]) <= 5

    @pytest.mark.asyncio
    async def test_list_oils_pagination_offset(self, async_client: AsyncClient):
        """Test pagination offset parameter"""
        # Get first page
        response_page1 = await async_client.get("/api/v1/oils?limit=5&offset=0")
        data_page1 = response_page1.json()

        # Get second page
        response_page2 = await async_client.get("/api/v1/oils?limit=5&offset=5")
        data_page2 = response_page2.json()

        assert response_page1.status_code == status.HTTP_200_OK
        assert response_page2.status_code == status.HTTP_200_OK

        # Both pages should have same total_count
        assert data_page1["total_count"] == data_page2["total_count"]

        # Pages should have different data (if enough oils exist)
        if data_page1["total_count"] > 5:
            page1_ids = {oil["id"] for oil in data_page1["oils"]}
            page2_ids = {oil["id"] for oil in data_page2["oils"]}
            assert page1_ids != page2_ids, "Pagination pages contain same data"

    @pytest.mark.asyncio
    async def test_list_oils_has_more_flag_accuracy(self, async_client: AsyncClient):
        """Test has_more flag is accurate"""
        response = await async_client.get("/api/v1/oils?limit=5&offset=0")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Calculate expected has_more
        expected_has_more = (data["offset"] + data["limit"]) < data["total_count"]
        assert data["has_more"] == expected_has_more

    @pytest.mark.asyncio
    async def test_list_oils_limit_bounds_validation(self, async_client: AsyncClient):
        """Test limit parameter bounds (1-100)"""
        # Test below minimum (should be rejected by FastAPI)
        response_low = await async_client.get("/api/v1/oils?limit=0")
        assert response_low.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test above maximum (should be rejected)
        response_high = await async_client.get("/api/v1/oils?limit=101")
        assert response_high.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test valid values
        response_min = await async_client.get("/api/v1/oils?limit=1")
        assert response_min.status_code == status.HTTP_200_OK

        response_max = await async_client.get("/api/v1/oils?limit=100")
        assert response_max.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_list_oils_offset_negative_validation(self, async_client: AsyncClient):
        """Test offset cannot be negative"""
        response = await async_client.get("/api/v1/oils?offset=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_list_oils_invalid_sort_by(self, async_client: AsyncClient):
        """Test invalid sort_by field is rejected"""
        response = await async_client.get("/api/v1/oils?sort_by=invalid_field")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_list_oils_invalid_sort_order(self, async_client: AsyncClient):
        """Test invalid sort_order is rejected"""
        response = await async_client.get("/api/v1/oils?sort_order=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdditivesEndpointIntegration:
    """Integration tests for GET /api/v1/additives endpoint"""

    @pytest.mark.asyncio
    async def test_list_additives_returns_200(self, async_client: AsyncClient):
        """Test additives endpoint returns 200 OK"""
        response = await async_client.get("/api/v1/additives")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_list_additives_response_schema(self, async_client: AsyncClient):
        """Test additives endpoint response matches schema"""
        response = await async_client.get("/api/v1/additives")
        data = response.json()

        # Verify top-level structure
        assert "additives" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data

        # Verify types
        assert isinstance(data["additives"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)
        assert isinstance(data["has_more"], bool)

    @pytest.mark.asyncio
    async def test_list_additives_item_schema(self, async_client: AsyncClient):
        """Test individual additive items match schema"""
        response = await async_client.get("/api/v1/additives")
        data = response.json()

        if len(data["additives"]) > 0:
            additive = data["additives"][0]

            # Required fields
            assert "id" in additive
            assert "common_name" in additive
            assert "inci_name" in additive
            assert "typical_usage_min_percent" in additive
            assert "typical_usage_max_percent" in additive
            assert "quality_effects" in additive
            assert "confidence_level" in additive
            assert "verified_by_mga" in additive
            assert "safety_warnings" in additive  # Can be null

            # Types
            assert isinstance(additive["id"], str)
            assert isinstance(additive["common_name"], str)
            assert isinstance(additive["inci_name"], str)
            assert isinstance(additive["typical_usage_min_percent"], (int, float))
            assert isinstance(additive["typical_usage_max_percent"], (int, float))
            assert isinstance(additive["quality_effects"], dict)
            assert isinstance(additive["confidence_level"], str)
            assert isinstance(additive["verified_by_mga"], bool)
            assert additive["safety_warnings"] is None or isinstance(additive["safety_warnings"], dict)

    @pytest.mark.asyncio
    async def test_list_additives_search_functionality(self, async_client: AsyncClient):
        """Test search functionality for additives"""
        # Search for "clay" (should match kaolin_clay if in seed data)
        response = await async_client.get("/api/v1/additives?search=clay")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # All results should contain "clay" (case-insensitive)
        for additive in data["additives"]:
            assert (
                "clay" in additive["common_name"].lower()
                or "clay" in additive["inci_name"].lower()
            )

    @pytest.mark.asyncio
    async def test_list_additives_filter_by_confidence_high(self, async_client: AsyncClient):
        """Test filtering by confidence level: high"""
        response = await async_client.get("/api/v1/additives?confidence=high")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # All results should have high confidence
        for additive in data["additives"]:
            assert additive["confidence_level"] == "high"

    @pytest.mark.asyncio
    async def test_list_additives_filter_by_confidence_medium(self, async_client: AsyncClient):
        """Test filtering by confidence level: medium"""
        response = await async_client.get("/api/v1/additives?confidence=medium")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        for additive in data["additives"]:
            assert additive["confidence_level"] == "medium"

    @pytest.mark.asyncio
    async def test_list_additives_filter_by_confidence_low(self, async_client: AsyncClient):
        """Test filtering by confidence level: low"""
        response = await async_client.get("/api/v1/additives?confidence=low")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        for additive in data["additives"]:
            assert additive["confidence_level"] == "low"

    @pytest.mark.asyncio
    async def test_list_additives_filter_verified_only_true(self, async_client: AsyncClient):
        """Test filtering by verified_only=true"""
        response = await async_client.get("/api/v1/additives?verified_only=true")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # All results should be verified
        for additive in data["additives"]:
            assert additive["verified_by_mga"] is True

    @pytest.mark.asyncio
    async def test_list_additives_filter_verified_only_false(self, async_client: AsyncClient):
        """Test verified_only=false returns all additives"""
        response_all = await async_client.get("/api/v1/additives?verified_only=false")
        response_verified = await async_client.get("/api/v1/additives?verified_only=true")

        data_all = response_all.json()
        data_verified = response_verified.json()

        # All should include verified and unverified
        assert data_all["total_count"] >= data_verified["total_count"]

    @pytest.mark.asyncio
    async def test_list_additives_combined_filters(self, async_client: AsyncClient):
        """Test combining multiple filters"""
        response = await async_client.get(
            "/api/v1/additives?confidence=high&verified_only=true"
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # All results should match both filters
        for additive in data["additives"]:
            assert additive["confidence_level"] == "high"
            assert additive["verified_by_mga"] is True

    @pytest.mark.asyncio
    async def test_list_additives_sort_by_common_name_asc(self, async_client: AsyncClient):
        """Test sorting by common_name ascending"""
        response = await async_client.get("/api/v1/additives?sort_by=common_name&sort_order=asc")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        names = [add["common_name"] for add in data["additives"]]
        assert names == sorted(names), "Additives not sorted by common_name ascending"

    @pytest.mark.asyncio
    async def test_list_additives_sort_by_confidence_level(self, async_client: AsyncClient):
        """Test sorting by confidence_level"""
        response = await async_client.get(
            "/api/v1/additives?sort_by=confidence_level&sort_order=asc"
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Extract confidence levels
        confidence_levels = [add["confidence_level"] for add in data["additives"]]

        # Verify sorted (high < low < medium alphabetically)
        assert confidence_levels == sorted(confidence_levels)

    @pytest.mark.asyncio
    async def test_list_additives_pagination(self, async_client: AsyncClient):
        """Test pagination works for additives"""
        response = await async_client.get("/api/v1/additives?limit=3&offset=0")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["limit"] == 3
        assert len(data["additives"]) <= 3

    @pytest.mark.asyncio
    async def test_list_additives_invalid_confidence_rejected(self, async_client: AsyncClient):
        """Test invalid confidence value is rejected"""
        response = await async_client.get("/api/v1/additives?confidence=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestResourceEndpointsConsistency:
    """Test consistency between oils and additives endpoints"""

    @pytest.mark.asyncio
    async def test_both_endpoints_use_same_pagination_structure(self, async_client: AsyncClient):
        """Test both endpoints return consistent pagination metadata"""
        oils_response = await async_client.get("/api/v1/oils")
        additives_response = await async_client.get("/api/v1/additives")

        oils_data = oils_response.json()
        additives_data = additives_response.json()

        # Both should have same metadata fields
        metadata_fields = ["total_count", "limit", "offset", "has_more"]

        for field in metadata_fields:
            assert field in oils_data, f"Oils missing {field}"
            assert field in additives_data, f"Additives missing {field}"

    @pytest.mark.asyncio
    async def test_both_endpoints_require_no_authentication(self, async_client: AsyncClient):
        """Test both endpoints are public (no auth required)"""
        # Request without auth headers
        oils_response = await async_client.get("/api/v1/oils")
        additives_response = await async_client.get("/api/v1/additives")

        # Both should return 200 (not 401/403)
        assert oils_response.status_code == status.HTTP_200_OK
        assert additives_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_both_endpoints_default_limit_50(self, async_client: AsyncClient):
        """Test both endpoints default to limit=50"""
        oils_response = await async_client.get("/api/v1/oils")
        additives_response = await async_client.get("/api/v1/additives")

        oils_data = oils_response.json()
        additives_data = additives_response.json()

        assert oils_data["limit"] == 50
        assert additives_data["limit"] == 50
