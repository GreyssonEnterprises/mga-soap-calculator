"""
Unit tests for Pydantic purity validation rules.

Tests Pydantic Field constraints for koh_purity and naoh_purity fields.

SAFETY-CRITICAL: Validation prevents dangerous purity values that could result
in catastrophically incorrect lye calculations causing chemical burns.

Test Coverage:
- Range validation (50-100%)
- Boundary rejection (<50%, >100%)
- Type validation (numeric only)
- Default value behavior (koh_purity: 90, naoh_purity: 100)
- Error message clarity
- Optional field behavior
"""

import pytest

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def valid_purity_values():
    """Collection of valid purity values within 50-100% range."""
    return [50.0, 50.01, 75.0, 85.0, 90.0, 95.0, 98.0, 99.99, 100.0]


@pytest.fixture
def invalid_purity_below_minimum():
    """Invalid purity values below 50% minimum."""
    return [0, 0.1, 25.0, 49.0, 49.99]


@pytest.fixture
def invalid_purity_above_maximum():
    """Invalid purity values above 100% maximum."""
    return [100.01, 101, 105, 150, 200]


@pytest.fixture
def sample_recipe_base():
    """Base recipe structure without purity fields."""
    return {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10},
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
        },
        "superfat_percent": 1,
        "batch_size_g": 700,
    }


# ============================================================================
# VALIDATION TESTS - VALID VALUES
# ============================================================================


class TestPurityValidationValidValues:
    """Test that valid purity values (50-100%) are accepted."""

    @pytest.mark.parametrize("purity", [50.0, 75.0, 90.0, 98.0, 100.0])
    def test_valid_koh_purity_accepted(self, sample_recipe_base, purity):
        """
        Test valid KOH purity values are accepted.

        Given: Recipe with koh_purity in range [50.0, 100.0]
        When: Pydantic validates the request
        Then: Validation passes without errors
        """
        # TODO: Implement test
        # Expected: No ValidationError raised

    @pytest.mark.parametrize("purity", [50.0, 98.0, 100.0])
    def test_valid_naoh_purity_accepted(self, sample_recipe_base, purity):
        """
        Test valid NaOH purity values are accepted.

        Given: Recipe with naoh_purity in range [50.0, 100.0]
        When: Pydantic validates the request
        Then: Validation passes without errors
        """
        # TODO: Implement test
        # Expected: No ValidationError raised

    def test_boundary_50_percent_accepted(self):
        """
        Test minimum boundary value (50%) is accepted.

        Given: Recipe with purity = 50.0
        When: Validation occurs
        Then: Accepted as valid minimum
        """
        # TODO: Implement test
        # Expected: purity = 50.0 passes validation

    def test_boundary_100_percent_accepted(self):
        """
        Test maximum boundary value (100%) is accepted.

        Given: Recipe with purity = 100.0
        When: Validation occurs
        Then: Accepted as valid maximum
        """
        # TODO: Implement test
        # Expected: purity = 100.0 passes validation


# ============================================================================
# VALIDATION TESTS - INVALID VALUES
# ============================================================================


class TestPurityValidationInvalidValues:
    """Test that invalid purity values are rejected with clear errors."""

    @pytest.mark.parametrize("invalid_purity", [0, 25.0, 49.0, 49.99])
    def test_koh_purity_below_50_rejected(self, sample_recipe_base, invalid_purity):
        """
        Test KOH purity below 50% is rejected.

        Given: Recipe with koh_purity < 50
        When: Pydantic validates the request
        Then: ValidationError raised with message about 50% minimum
        """
        # TODO: Implement test
        # Expected: ValidationError with "must be between 50% and 100%"

    @pytest.mark.parametrize("invalid_purity", [100.01, 101, 150])
    def test_koh_purity_above_100_rejected(self, sample_recipe_base, invalid_purity):
        """
        Test KOH purity above 100% is rejected.

        Given: Recipe with koh_purity > 100
        When: Pydantic validates the request
        Then: ValidationError raised with message about 100% maximum
        """
        # TODO: Implement test
        # Expected: ValidationError with "cannot exceed 100%"

    def test_naoh_purity_negative_rejected(self):
        """
        Test negative purity values are rejected.

        Given: Recipe with negative purity value
        When: Validation occurs
        Then: ValidationError raised
        """
        # TODO: Implement test
        # Expected: ValidationError with message about valid range

    def test_zero_purity_rejected(self):
        """
        Test zero purity is rejected (would cause divide-by-zero).

        Given: Recipe with purity = 0
        When: Validation occurs
        Then: ValidationError raised preventing divide-by-zero
        """
        # TODO: Implement test
        # Expected: ValidationError with "must be between 50% and 100%"


# ============================================================================
# ERROR MESSAGE TESTS
# ============================================================================


class TestPurityValidationErrorMessages:
    """Test that validation error messages are clear and actionable."""

    def test_error_message_includes_received_value(self):
        """
        Test error message includes the invalid value provided.

        Given: Recipe with invalid purity (e.g., 49)
        When: ValidationError is raised
        Then: Error message includes "Received: 49%"
        """
        # TODO: Implement test
        # Expected: Error message format: "...Received: {value}%"

    def test_error_message_specifies_valid_range(self):
        """
        Test error message specifies valid range (50-100%).

        Given: Recipe with invalid purity
        When: ValidationError is raised
        Then: Error message includes "must be between 50% and 100%"
        """
        # TODO: Implement test
        # Expected: Error message includes valid range

    def test_error_distinguishes_koh_vs_naoh(self):
        """
        Test error messages distinguish between KOH and NaOH fields.

        Given: Invalid koh_purity value
        When: ValidationError is raised
        Then: Error message specifies "KOH purity" (not just "purity")
        """
        # TODO: Implement test
        # Expected: Field name in error message


# ============================================================================
# DEFAULT VALUE TESTS
# ============================================================================


class TestPurityDefaultValues:
    """Test default purity values when fields are omitted."""

    def test_koh_purity_defaults_to_90(self, sample_recipe_base):
        """
        Test KOH purity defaults to 90% when omitted.

        Given: Recipe without koh_purity field
        When: Pydantic parses the request
        Then: koh_purity is set to 90.0
        """
        # TODO: Implement test
        # Expected: model.koh_purity == 90.0

    def test_naoh_purity_defaults_to_100(self, sample_recipe_base):
        """
        Test NaOH purity defaults to 100% when omitted (backward compatible).

        Given: Recipe without naoh_purity field
        When: Pydantic parses the request
        Then: naoh_purity is set to 100.0
        """
        # TODO: Implement test
        # Expected: model.naoh_purity == 100.0

    def test_both_purity_fields_optional(self, sample_recipe_base):
        """
        Test both purity fields are optional and use defaults.

        Given: Recipe with neither koh_purity nor naoh_purity
        When: Pydantic parses the request
        Then: Both fields receive their default values
        """
        # TODO: Implement test
        # Expected: koh_purity=90.0, naoh_purity=100.0

    def test_explicit_purity_overrides_default(self):
        """
        Test explicit purity value overrides default.

        Given: Recipe with explicit koh_purity=85
        When: Pydantic parses the request
        Then: koh_purity is 85.0 (not default 90.0)
        """
        # TODO: Implement test
        # Expected: Explicit value takes precedence


# ============================================================================
# TYPE VALIDATION TESTS
# ============================================================================


class TestPurityTypeValidation:
    """Test purity fields accept correct types and reject invalid types."""

    def test_purity_accepts_float(self):
        """
        Test purity fields accept float values.

        Given: Recipe with purity as float (90.5)
        When: Validation occurs
        Then: Float is accepted
        """
        # TODO: Implement test

    def test_purity_accepts_int(self):
        """
        Test purity fields accept integer values.

        Given: Recipe with purity as int (90)
        When: Validation occurs
        Then: Int is coerced to float and accepted
        """
        # TODO: Implement test

    def test_purity_rejects_string(self):
        """
        Test purity fields reject string values.

        Given: Recipe with purity as string ("90")
        When: Validation occurs
        Then: ValidationError raised
        """
        # TODO: Implement test
        # Expected: Type error for non-numeric value

    def test_purity_rejects_none(self):
        """
        Test purity fields reject None (use default instead).

        Given: Recipe with purity = None
        When: Validation occurs
        Then: Default value is used (not None)
        """
        # TODO: Implement test
