"""
Integration tests for purity API endpoint.

Tests end-to-end API behavior with purity parameters through actual
HTTP requests to the FastAPI application.

SAFETY-CRITICAL: These tests validate complete request-response flow
including validation, calculation, and response formatting.

Test Coverage:
- POST /api/v1/recipes/calculate with purity parameters
- HTTP 200 responses with correct purity-adjusted weights
- HTTP 400 responses for invalid purity values
- Response structure includes purity fields
- Response includes pure_koh_equivalent_g and pure_naoh_equivalent_g
- Mixed lye calculations with different purity values
- Default purity behavior (koh: 90%, naoh: 100%)
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def recipe_with_90_koh_purity():
    """
    Recipe payload with explicit 90% KOH purity.

    Expected results:
    - pure_koh_equivalent_g: 117.1
    - koh_weight_g: 130.1 (117.1 / 0.90)
    """
    return {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10}
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
            "koh_purity": 90
        },
        "superfat_percent": 1,
        "batch_size_g": 700
    }


@pytest.fixture
def recipe_mixed_purity():
    """Recipe with different KOH and NaOH purity values."""
    return {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10}
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
            "koh_purity": 90,
            "naoh_purity": 98
        },
        "superfat_percent": 1,
        "batch_size_g": 700
    }


@pytest.fixture
def recipe_without_purity():
    """Recipe without purity fields (test defaults)."""
    return {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10}
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
        },
        "superfat_percent": 1,
        "batch_size_g": 700
    }


# ============================================================================
# SUCCESSFUL CALCULATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPurityAPISuccess:
    """Test successful API responses with purity parameters."""

    async def test_90_percent_koh_purity_calculation(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API returns correct weights for 90% KOH purity.

        Given: POST /api/v1/recipes/calculate with koh_purity=90
        When: Request is processed
        Then: HTTP 200 with koh_weight_g=130.1 and pure_koh_equivalent_g=117.1
        """
        # TODO: Implement test
        # Expected: response.status_code == 200
        # Expected: response.json()["koh_weight_g"] ≈ 130.1 (±0.5)
        # Expected: response.json()["pure_koh_equivalent_g"] ≈ 117.1 (±0.5)

    async def test_mixed_purity_independent_adjustments(
        self,
        async_client: AsyncClient,
        recipe_mixed_purity
    ):
        """
        Test API handles different purity values for KOH and NaOH.

        Given: POST with koh_purity=90 and naoh_purity=98
        When: Request is processed
        Then: KOH and NaOH weights adjusted independently
        """
        # TODO: Implement test
        # Expected: response.status_code == 200
        # Expected: koh_weight adjusted by 0.90
        # Expected: naoh_weight adjusted by 0.98

    async def test_100_percent_purity_no_adjustment(
        self,
        async_client: AsyncClient
    ):
        """
        Test 100% purity returns unadjusted weights.

        Given: POST with koh_purity=100
        When: Request is processed
        Then: koh_weight_g == pure_koh_equivalent_g (no adjustment)
        """
        # TODO: Implement test
        # Expected: koh_weight_g == pure_koh_equivalent_g

    async def test_response_includes_purity_fields(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test response includes purity values and pure equivalents.

        Given: POST with explicit purity values
        When: Response is returned
        Then: Response contains koh_purity, naoh_purity, pure_koh_equivalent_g, pure_naoh_equivalent_g
        """
        # TODO: Implement test
        # Expected: "koh_purity" in response.json()
        # Expected: "naoh_purity" in response.json()
        # Expected: "pure_koh_equivalent_g" in response.json()
        # Expected: "pure_naoh_equivalent_g" in response.json()


# ============================================================================
# DEFAULT BEHAVIOR TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPurityAPIDefaults:
    """Test default purity values when fields are omitted."""

    async def test_omitted_koh_purity_defaults_to_90(
        self,
        async_client: AsyncClient,
        recipe_without_purity
    ):
        """
        Test API defaults to 90% KOH when field is omitted.

        Given: POST without koh_purity field
        When: Request is processed
        Then: Response includes koh_purity=90.0 and adjusted calculation
        """
        # TODO: Implement test
        # Expected: response.json()["koh_purity"] == 90.0
        # Expected: koh_weight_g reflects 90% adjustment

    async def test_omitted_naoh_purity_defaults_to_100(
        self,
        async_client: AsyncClient,
        recipe_without_purity
    ):
        """
        Test API defaults to 100% NaOH when field is omitted (backward compatible).

        Given: POST without naoh_purity field
        When: Request is processed
        Then: Response includes naoh_purity=100.0 with no adjustment
        """
        # TODO: Implement test
        # Expected: response.json()["naoh_purity"] == 100.0
        # Expected: naoh_weight_g == pure_naoh_equivalent_g


# ============================================================================
# VALIDATION ERROR TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPurityAPIValidationErrors:
    """Test API validation errors for invalid purity values."""

    async def test_koh_purity_below_50_returns_400(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API rejects KOH purity below 50%.

        Given: POST with koh_purity=49
        When: Request is validated
        Then: HTTP 400 with error message about 50% minimum
        """
        # TODO: Implement test
        # Expected: response.status_code == 400
        # Expected: error message includes "must be between 50% and 100%"

    async def test_koh_purity_above_100_returns_400(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API rejects KOH purity above 100%.

        Given: POST with koh_purity=101
        When: Request is validated
        Then: HTTP 400 with error message about 100% maximum
        """
        # TODO: Implement test
        # Expected: response.status_code == 400
        # Expected: error message includes "cannot exceed 100%"

    async def test_naoh_purity_negative_returns_400(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API rejects negative purity values.

        Given: POST with naoh_purity=-5
        When: Request is validated
        Then: HTTP 400 with error message about valid range
        """
        # TODO: Implement test
        # Expected: response.status_code == 400

    async def test_zero_purity_returns_400(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API rejects zero purity (would cause divide-by-zero).

        Given: POST with koh_purity=0
        When: Request is validated
        Then: HTTP 400 before calculation occurs
        """
        # TODO: Implement test
        # Expected: response.status_code == 400


# ============================================================================
# WARNING TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPurityAPIWarnings:
    """Test warning generation in API responses."""

    async def test_unusual_purity_generates_warning(
        self,
        async_client: AsyncClient
    ):
        """
        Test API includes warning for unusual purity values.

        Given: POST with koh_purity=75 (unusual but valid)
        When: Request is processed
        Then: HTTP 200 with warning in response metadata
        """
        # TODO: Implement test
        # Expected: response.status_code == 200
        # Expected: response.json()["metadata"]["warnings"] contains warning

    async def test_typical_purity_no_warnings(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test no warnings for typical commercial purity values.

        Given: POST with koh_purity=90 (typical commercial)
        When: Request is processed
        Then: HTTP 200 without warnings
        """
        # TODO: Implement test
        # Expected: response.status_code == 200
        # Expected: no warnings in response


# ============================================================================
# PRECISION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPurityAPIPrecision:
    """Test calculation precision meets ±0.5g accuracy requirement."""

    async def test_calculation_within_tolerance(
        self,
        async_client: AsyncClient,
        recipe_with_90_koh_purity
    ):
        """
        Test API calculations are within ±0.5g tolerance.

        Given: POST with known expected weights
        When: Calculation is performed
        Then: Results are within ±0.5g of manual calculation
        """
        # TODO: Implement test
        # Expected: abs(koh_weight_g - 130.1) <= 0.5
