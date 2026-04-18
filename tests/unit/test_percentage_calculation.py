"""
Unit tests for percentage calculation service

TDD RED PHASE: These tests MUST FAIL initially (no implementation exists yet)
"""

from decimal import Decimal

import pytest

# Import will fail initially - this is expected in RED phase
from app.services.percentage_calculator import (
    calculate_ingredient_percentages,
    normalize_percentages,
    round_percentages_to_precision,
)


class TestCalculateIngredientPercentages:
    """Test basic percentage calculation from weights"""

    def test_simple_two_ingredient_percentage(self):
        """Calculate percentages for two ingredients of equal weight"""
        weights = {"oil-a": Decimal("100.0"), "oil-b": Decimal("100.0")}

        percentages = calculate_ingredient_percentages(weights)

        assert percentages["oil-a"] == Decimal("50.0")
        assert percentages["oil-b"] == Decimal("50.0")

    def test_unequal_weights(self):
        """Calculate percentages for unequal weights"""
        weights = {"coconut": Decimal("300.0"), "olive": Decimal("700.0")}

        percentages = calculate_ingredient_percentages(weights)

        assert percentages["coconut"] == Decimal("30.0")
        assert percentages["olive"] == Decimal("70.0")

    def test_three_ingredient_mix(self):
        """Calculate percentages for three ingredients"""
        weights = {"coconut": Decimal("200.0"), "olive": Decimal("500.0"), "palm": Decimal("300.0")}

        percentages = calculate_ingredient_percentages(weights)

        assert percentages["coconut"] == Decimal("20.0")
        assert percentages["olive"] == Decimal("50.0")
        assert percentages["palm"] == Decimal("30.0")

    def test_percentages_sum_to_100(self):
        """All percentages should sum to exactly 100.0"""
        weights = {
            "oil-a": Decimal("123.45"),
            "oil-b": Decimal("234.56"),
            "oil-c": Decimal("345.67"),
        }

        percentages = calculate_ingredient_percentages(weights)
        total = sum(percentages.values())

        # Due to Decimal arithmetic, may have tiny precision differences
        # Use quantize to compare at reasonable precision
        assert total.quantize(Decimal("0.01")) == Decimal("100.00")

    def test_single_ingredient(self):
        """Single ingredient should be 100%"""
        weights = {"only-oil": Decimal("500.0")}

        percentages = calculate_ingredient_percentages(weights)

        assert percentages["only-oil"] == Decimal("100.0")

    def test_empty_weights_dict(self):
        """Empty weights should raise ValueError"""
        with pytest.raises(ValueError):
            calculate_ingredient_percentages({})

    def test_zero_total_weight(self):
        """All zero weights should raise ValueError"""
        weights = {"oil-a": Decimal("0.0"), "oil-b": Decimal("0.0")}

        with pytest.raises(ValueError):
            calculate_ingredient_percentages(weights)

    def test_negative_weight(self):
        """Negative weights should raise ValueError"""
        weights = {"oil-a": Decimal("100.0"), "oil-b": Decimal("-50.0")}

        with pytest.raises(ValueError):
            calculate_ingredient_percentages(weights)


class TestNormalizePercentages:
    """Test percentage normalization to sum exactly to 100"""

    def test_normalize_percentages_close_to_100(self):
        """Percentages that sum to 99.99 or 100.01 should normalize to 100.0"""
        percentages = {
            "a": Decimal("33.34"),
            "b": Decimal("33.33"),
            "c": Decimal("33.33"),  # Sum = 100.00
        }

        normalized = normalize_percentages(percentages)
        total = sum(normalized.values())

        assert total == Decimal("100.0")

    def test_normalize_rounding_errors(self):
        """Handle rounding errors that don't sum to 100"""
        percentages = {
            "a": Decimal("33.333"),
            "b": Decimal("33.333"),
            "c": Decimal("33.333"),  # Sum = 99.999
        }

        normalized = normalize_percentages(percentages)
        total = sum(normalized.values())

        assert total == Decimal("100.0")

    def test_normalize_preserves_order(self):
        """Largest percentages should get rounding adjustments first"""
        percentages = {
            "large": Decimal("70.001"),
            "medium": Decimal("20.001"),
            "small": Decimal("9.998"),  # Sum = 100.000
        }

        normalized = normalize_percentages(percentages)

        # All should round to nearest, preserving proportions
        assert normalized["large"] == Decimal("70.0")
        assert normalized["medium"] == Decimal("20.0")
        assert normalized["small"] == Decimal("10.0")


class TestRoundPercentagesToPrecision:
    """Test percentage rounding with precision control"""

    def test_round_to_one_decimal(self):
        """Round percentages to 1 decimal place"""
        percentages = {"a": Decimal("33.456"), "b": Decimal("66.544")}

        rounded = round_percentages_to_precision(percentages, precision=1)

        assert rounded["a"] == Decimal("33.5")
        assert rounded["b"] == Decimal("66.5")

    def test_round_to_two_decimals(self):
        """Round percentages to 2 decimal places"""
        percentages = {"a": Decimal("33.4567"), "b": Decimal("66.5433")}

        rounded = round_percentages_to_precision(percentages, precision=2)

        assert rounded["a"] == Decimal("33.46")
        assert rounded["b"] == Decimal("66.54")

    def test_round_to_integer(self):
        """Round percentages to integers (0 decimals)"""
        percentages = {"a": Decimal("33.6"), "b": Decimal("66.4")}

        rounded = round_percentages_to_precision(percentages, precision=0)

        assert rounded["a"] == Decimal("34")
        assert rounded["b"] == Decimal("66")

    def test_sum_preserved_after_rounding(self):
        """After rounding, percentages should still sum to 100"""
        percentages = {"a": Decimal("33.333"), "b": Decimal("33.333"), "c": Decimal("33.334")}

        rounded = round_percentages_to_precision(percentages, precision=1)
        total = sum(rounded.values())

        assert total == Decimal("100.0")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_small_percentage(self):
        """Handle very small percentages (< 1%)"""
        weights = {"major": Decimal("999.0"), "trace": Decimal("1.0")}

        percentages = calculate_ingredient_percentages(weights)

        assert percentages["major"] == Decimal("99.9")
        assert percentages["trace"] == Decimal("0.1")

    def test_high_precision_weights(self):
        """Handle high precision weight values"""
        weights = {"a": Decimal("123.456789"), "b": Decimal("876.543211")}

        percentages = calculate_ingredient_percentages(weights)
        total = sum(percentages.values())

        assert total == Decimal("100.0")

    def test_many_ingredients(self):
        """Calculate percentages for many ingredients"""
        weights = {f"oil-{i}": Decimal("10.0") for i in range(20)}

        percentages = calculate_ingredient_percentages(weights)
        total = sum(percentages.values())

        assert total == Decimal("100.0")
        assert all(p == Decimal("5.0") for p in percentages.values())

    def test_decimal_vs_float_consistency(self):
        """Decimal calculations should be more precise than float"""
        weights = {"a": Decimal("0.1"), "b": Decimal("0.2")}

        percentages = calculate_ingredient_percentages(weights)

        # Verify Decimal precision (repeating decimal 33.333...)
        # Round to reasonable precision for comparison
        assert percentages["a"].quantize(Decimal("0.000001")) == Decimal("33.333333")
        # Decimal maintains precision, unlike float rounding errors

    def test_preserve_ingredient_keys(self):
        """All input ingredient keys should be preserved in output"""
        weights = {
            "coconut-oil": Decimal("100.0"),
            "olive-oil-extra-virgin": Decimal("200.0"),
            "palm-kernel-oil": Decimal("300.0"),
        }

        percentages = calculate_ingredient_percentages(weights)

        assert set(percentages.keys()) == set(weights.keys())
