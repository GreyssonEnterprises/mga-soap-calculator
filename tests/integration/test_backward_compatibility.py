"""
Integration tests for backward compatibility with legacy API behavior.

Tests ensure existing API clients continue to function correctly despite
the BREAKING CHANGE to default KOH purity (100% → 90%).

SAFETY-CRITICAL: Backward compatibility tests prevent production incidents
where existing users receive over-lye soap calculations after deployment.

Test Coverage:
- Legacy behavior: explicitly passing koh_purity=100 maintains old calculations
- New behavior: omitting koh_purity uses 90% default (breaking change)
- NaOH backward compatibility: omitting naoh_purity still defaults to 100%
- Pure NaOH recipes unaffected (no breaking change for NaOH-only)
- Migration path validation
- Response field additions don't break existing parsers
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def legacy_koh_recipe_no_purity():
    """
    Legacy API request that omitted purity (assumed 100% KOH).

    This is the BREAKING CHANGE scenario: previously returned weights for
    100% pure KOH, now returns weights for 90% commercial KOH.
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
            # NO koh_purity field (legacy behavior)
        },
        "superfat_percent": 1,
        "batch_size_g": 700
    }


@pytest.fixture
def legacy_koh_recipe_explicit_100():
    """
    Migrated API request with explicit koh_purity=100.

    This maintains legacy behavior for users who update their code.
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
            "koh_purity": 100  # Explicit to maintain legacy behavior
        },
        "superfat_percent": 1,
        "batch_size_g": 700
    }


@pytest.fixture
def pure_naoh_recipe():
    """Pure NaOH recipe (no KOH) - should be unaffected by breaking change."""
    return {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10}
        ],
        "lye": {
            "naoh_percent": 100,
            "koh_percent": 0,
        },
        "superfat_percent": 5,
        "batch_size_g": 500
    }


# ============================================================================
# BREAKING CHANGE TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilityBreakingChange:
    """Test breaking change behavior: default KOH purity 100% → 90%."""

    async def test_legacy_request_receives_90_percent_calculation(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test legacy requests (no koh_purity) now use 90% default.

        Given: POST without koh_purity field (legacy behavior)
        When: Request is processed with new default
        Then: Response uses 90% purity calculation (BREAKING CHANGE)
        """
        # TODO: Implement test
        # Expected: response.json()["koh_purity"] == 90.0
        # Expected: response.json()["koh_weight_g"] reflects 90% adjustment
        # Expected: koh_weight > legacy_100_percent_weight

    async def test_explicit_100_percent_maintains_legacy_behavior(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_explicit_100
    ):
        """
        Test explicit koh_purity=100 maintains legacy calculations.

        Given: POST with explicit koh_purity=100
        When: Request is processed
        Then: Response matches old behavior (no adjustment)
        """
        # TODO: Implement test
        # Expected: response.json()["koh_purity"] == 100.0
        # Expected: koh_weight_g == pure_koh_equivalent_g

    async def test_breaking_change_weight_difference(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity,
        legacy_koh_recipe_explicit_100
    ):
        """
        Test weight difference between old and new default behavior.

        Given: Same recipe with and without explicit koh_purity=100
        When: Both requests are processed
        Then: New default (90%) returns ~11% more KOH weight than explicit 100%
        """
        # TODO: Implement test
        # Expected: weight_90 ≈ weight_100 * 1.111


# ============================================================================
# NaOH BACKWARD COMPATIBILITY TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilityNaOH:
    """Test NaOH backward compatibility (no breaking change)."""

    async def test_pure_naoh_recipe_unchanged(
        self,
        async_client: AsyncClient,
        pure_naoh_recipe
    ):
        """
        Test pure NaOH recipes are unaffected by KOH default change.

        Given: POST with 100% NaOH, 0% KOH, no purity fields
        When: Request is processed
        Then: NaOH calculation identical to legacy behavior
        """
        # TODO: Implement test
        # Expected: naoh_purity defaults to 100.0
        # Expected: No purity adjustment for NaOH

    async def test_naoh_default_remains_100_percent(
        self,
        async_client: AsyncClient
    ):
        """
        Test NaOH purity still defaults to 100% (backward compatible).

        Given: POST without naoh_purity field
        When: Request is processed
        Then: naoh_purity=100.0 (unchanged from legacy)
        """
        # TODO: Implement test
        # Expected: response.json()["naoh_purity"] == 100.0


# ============================================================================
# MIGRATION PATH TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilityMigrationPath:
    """Test migration paths for existing API clients."""

    async def test_migration_step_1_add_explicit_koh_purity(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_explicit_100
    ):
        """
        Test migration step 1: Add explicit koh_purity=100 to maintain behavior.

        Given: Existing user adds koh_purity=100 to all requests
        When: Requests are processed
        Then: Calculations remain identical to legacy behavior
        """
        # TODO: Implement test
        # Expected: Matches legacy calculations exactly

    async def test_migration_step_2_adjust_to_90_percent(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test migration step 2: User adopts 90% default for commercial KOH.

        Given: User removes explicit koh_purity (accepts new default)
        When: Request is processed
        Then: Receives correct calculation for 90% commercial KOH
        """
        # TODO: Implement test
        # Expected: koh_purity=90.0, adjusted weight

    async def test_migration_no_code_change_scenario(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test scenario: User makes no code changes after deployment.

        Given: Legacy code without koh_purity field
        When: Request hits new API
        Then: Receives 90% calculation (BREAKING CHANGE impact)
        """
        # TODO: Implement test
        # Expected: User gets different (higher) KOH weight
        # This is the safety concern requiring communication


# ============================================================================
# RESPONSE STRUCTURE COMPATIBILITY TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilityResponseStructure:
    """Test new response fields don't break existing parsers."""

    async def test_new_fields_addition_backward_compatible(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test new response fields don't break parsers expecting old structure.

        Given: POST from legacy client
        When: Response includes new purity fields
        Then: Response is valid JSON-compatible superset of old structure
        """
        # TODO: Implement test
        # Expected: All old fields present + new purity fields
        # Expected: Parsers ignoring unknown fields still work

    async def test_response_includes_legacy_fields(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test all legacy response fields are still present.

        Given: POST request
        When: Response is generated
        Then: All pre-existing fields are present (no removals)
        """
        # TODO: Implement test
        # Expected: koh_weight_g, naoh_weight_g, water_weight_g, etc. present

    async def test_pure_equivalents_are_additive_fields(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test pure_koh_equivalent_g and pure_naoh_equivalent_g are additive.

        Given: POST request
        When: Response is generated
        Then: New pure_*_equivalent_g fields are added without replacing existing fields
        """
        # TODO: Implement test
        # Expected: Both koh_weight_g (commercial) and pure_koh_equivalent_g present


# ============================================================================
# LEGACY CALCULATION VERIFICATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilityLegacyCalculations:
    """Test explicit purity=100 matches legacy calculations exactly."""

    async def test_legacy_calculation_reference_case(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_explicit_100
    ):
        """
        Test reference case: explicit 100% purity matches documented legacy results.

        Given: POST with koh_purity=100 (legacy behavior)
        When: Calculation is performed
        Then: Results match documented legacy API behavior exactly
        """
        # TODO: Implement test with known legacy reference values
        # Expected: Exact match to pre-feature calculations

    async def test_legacy_precision_maintained(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_explicit_100
    ):
        """
        Test calculation precision unchanged for legacy behavior.

        Given: POST with koh_purity=100
        When: Calculation is performed
        Then: Precision is identical to legacy system (±0.5g)
        """
        # TODO: Implement test
        # Expected: Same precision as before feature


# ============================================================================
# SAFETY VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestBackwardCompatibilitySafety:
    """Test safety implications of breaking change."""

    async def test_over_lye_risk_without_migration(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test breaking change results in HIGHER lye calculation (safer).

        Given: Legacy request without purity field
        When: New default (90%) is applied
        Then: Result is MORE lye than legacy (over-lye, not under-lye)

        Safety Note: Over-lye is safer than under-lye (soap is caustic but
        will saponify, vs soft/non-functional). However, still requires
        user communication about the change.
        """
        # TODO: Implement test
        # Expected: new_weight > legacy_weight (over-lye scenario)

    async def test_deprecation_warning_for_omitted_koh_purity(
        self,
        async_client: AsyncClient,
        legacy_koh_recipe_no_purity
    ):
        """
        Test API includes deprecation warning when koh_purity is omitted.

        Given: POST without koh_purity field
        When: Request is processed
        Then: Response includes warning about default change
        """
        # TODO: Implement test
        # Expected: Deprecation warning in response metadata
