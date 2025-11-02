"""
Tests for lye calculator service

TDD Evidence: Tests written BEFORE implementation refinement
Validates against SoapCalc reference data for accuracy
"""
import pytest
from app.services.lye_calculator import (
    OilInput,
    calculate_lye,
    validate_superfat
)


class TestNaOHCalculation:
    """Test pure NaOH lye calculations (Task 2.1.1)"""

    def test_100_percent_naoh_standard_recipe(self):
        """
        TDD: Standard recipe validation against SoapCalc
        Recipe: 500g Olive (50%), 300g Coconut (30%), 200g Palm (20%)
        Superfat: 5%
        Expected: ~142.6g NaOH (within 0.1g tolerance)
        """
        oils = [
            OilInput(weight_g=500, sap_naoh=0.134, sap_koh=0.188),  # Olive
            OilInput(weight_g=300, sap_naoh=0.178, sap_koh=0.250),  # Coconut
            OilInput(weight_g=200, sap_naoh=0.142, sap_koh=0.199),  # Palm
        ]

        result = calculate_lye(
            oils=oils,
            superfat_percent=5.0,
            naoh_percent=100.0,
            koh_percent=0.0
        )

        # Calculate expected manually:
        # Olive: 500 * 0.134 = 67.0
        # Coconut: 300 * 0.178 = 53.4
        # Palm: 200 * 0.142 = 28.4
        # Total SAP = 148.8
        # With 5% superfat: 148.8 * 0.95 = 141.36g
        assert abs(result.naoh_g - 141.4) < 0.1, f"Expected ~141.4g NaOH, got {result.naoh_g}g"
        assert result.koh_g == 0.0
        assert abs(result.total_g - 141.4) < 0.1

    def test_naoh_with_zero_superfat(self):
        """TDD: Test 0% superfat produces maximum lye"""
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        result = calculate_lye(
            oils=oils,
            superfat_percent=0.0,
            naoh_percent=100.0,
            koh_percent=0.0
        )

        # 1000g * 0.134 * 1.0 = 134.0g
        assert abs(result.naoh_g - 134.0) < 0.1

    def test_naoh_with_high_superfat(self):
        """TDD: Test 20% superfat reduces lye appropriately"""
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        result = calculate_lye(
            oils=oils,
            superfat_percent=20.0,
            naoh_percent=100.0,
            koh_percent=0.0
        )

        # 1000g * 0.134 * 0.80 = 107.2g
        assert abs(result.naoh_g - 107.2) < 0.1


class TestKOHCalculation:
    """Test pure KOH lye calculations (Task 2.1.2)"""

    def test_100_percent_koh(self):
        """
        TDD: KOH has higher SAP values than NaOH
        Same recipe should produce more KOH weight
        """
        oils = [
            OilInput(weight_g=500, sap_naoh=0.134, sap_koh=0.188),  # Olive
            OilInput(weight_g=300, sap_naoh=0.178, sap_koh=0.250),  # Coconut
            OilInput(weight_g=200, sap_naoh=0.142, sap_koh=0.199),  # Palm
        ]

        result = calculate_lye(
            oils=oils,
            superfat_percent=5.0,
            naoh_percent=0.0,
            koh_percent=100.0
        )

        # Olive: 500 * 0.188 = 94.0
        # Coconut: 300 * 0.250 = 75.0
        # Palm: 200 * 0.199 = 39.8
        # Total SAP = 208.8
        # With 5% superfat: 208.8 * 0.95 = 198.36g
        assert abs(result.koh_g - 198.4) < 0.1
        assert result.naoh_g == 0.0


class TestMixedLyeCalculation:
    """Test mixed NaOH/KOH lye calculations (Task 2.1.2)"""

    def test_70_30_naoh_koh_split(self):
        """
        TDD: Mixed lye BY WEIGHT split (Formula A - industry standard)
        70% NaOH, 30% KOH means 70% of total lye WEIGHT is NaOH

        Formula A calculation:
        - Weighted SAP = (SAP_NaOH × 0.70) + (SAP_KOH × 0.30)
        - Weighted SAP = (0.134 × 0.70) + (0.188 × 0.30) = 0.1502
        - Total lye = 1000g × 0.1502 × 0.95 = 142.69g
        - NaOH = 142.69 × 0.70 = 99.88g (rounds to 99.9g)
        - KOH = 142.69 × 0.30 = 42.81g (rounds to 42.8g)
        """
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        result = calculate_lye(
            oils=oils,
            superfat_percent=5.0,
            naoh_percent=70.0,
            koh_percent=30.0
        )

        # Formula A results (0.1g tolerance)
        assert abs(result.naoh_g - 99.9) < 0.1, f"Expected ~99.9g NaOH, got {result.naoh_g}g"
        assert abs(result.koh_g - 42.8) < 0.1, f"Expected ~42.8g KOH, got {result.koh_g}g"
        assert abs(result.total_g - 142.7) < 0.1, f"Expected ~142.7g total, got {result.total_g}g"

    def test_50_50_naoh_koh_split(self):
        """
        TDD: Equal weight split between NaOH and KOH (Formula A)

        Formula A calculation:
        - Weighted SAP = (0.140 × 0.50) + (0.196 × 0.50) = 0.168
        - Total lye = 1000g × 0.168 × 1.0 = 168.0g
        - NaOH = 168.0 × 0.50 = 84.0g
        - KOH = 168.0 × 0.50 = 84.0g
        """
        oils = [OilInput(weight_g=1000, sap_naoh=0.140, sap_koh=0.196)]

        result = calculate_lye(
            oils=oils,
            superfat_percent=0.0,
            naoh_percent=50.0,
            koh_percent=50.0
        )

        # Formula A results (0.1g tolerance)
        assert abs(result.naoh_g - 84.0) < 0.1, f"Expected ~84.0g NaOH, got {result.naoh_g}g"
        assert abs(result.koh_g - 84.0) < 0.1, f"Expected ~84.0g KOH, got {result.koh_g}g"
        assert abs(result.total_g - 168.0) < 0.1, f"Expected ~168.0g total, got {result.total_g}g"

    def test_mixed_lye_weight_percentage_convention(self):
        """
        Industry convention: 70% NaOH / 30% KOH means BY WEIGHT.

        Example: If total lye needed is 100g:
        - 70g NaOH (70% by weight)
        - 30g KOH (30% by weight)

        This matches how professional soap makers like MGA specify recipes.
        NOT molecular equivalents, NOT separate SAP calculations.
        """
        oils = [OilInput(weight_g=1000, sap_naoh=0.150, sap_koh=0.210)]

        result = calculate_lye(
            oils=oils,
            superfat_percent=0.0,
            naoh_percent=70.0,
            koh_percent=30.0
        )

        # Weighted SAP = (0.150 × 0.70) + (0.210 × 0.30) = 0.168
        # Total lye = 1000 × 0.168 × 1.0 = 168.0g
        # NaOH = 168.0 × 0.70 = 117.6g
        # KOH = 168.0 × 0.30 = 50.4g

        assert abs(result.naoh_g - 117.6) < 0.1
        assert abs(result.koh_g - 50.4) < 0.1

        # Verify weight percentages are correct
        total = result.naoh_g + result.koh_g
        naoh_percent_actual = (result.naoh_g / total) * 100
        koh_percent_actual = (result.koh_g / total) * 100

        assert abs(naoh_percent_actual - 70.0) < 0.1, "NaOH should be 70% by weight"
        assert abs(koh_percent_actual - 30.0) < 0.1, "KOH should be 30% by weight"


class TestSuperfatValidation:
    """Test superfat validation and warnings (Task 2.1.3)"""

    def test_valid_superfat_no_warning(self):
        """TDD: Normal superfat range produces no warnings"""
        result = validate_superfat(5.0)
        assert result == {}

        result = validate_superfat(10.0)
        assert result == {}

        result = validate_superfat(20.0)
        assert result == {}

    def test_high_superfat_warning(self):
        """TDD: Superfat >20% generates warning"""
        result = validate_superfat(25.0)
        assert result['level'] == 'warning'
        assert 'soft' in result['message'].lower() or 'greasy' in result['message'].lower()

    def test_negative_superfat_error(self):
        """TDD: Negative superfat is dangerous - error level"""
        result = validate_superfat(-5.0)
        assert result['level'] == 'error'
        assert 'dangerous' in result['message'].lower() or 'lye-heavy' in result['message'].lower()

    def test_invalid_lye_percentages(self):
        """TDD: Lye percentages must sum to 100%"""
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        with pytest.raises(ValueError, match="must equal 100%"):
            calculate_lye(oils, superfat_percent=5.0, naoh_percent=60.0, koh_percent=30.0)

    def test_invalid_superfat_out_of_range(self):
        """TDD: Superfat must be 0-100%"""
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        with pytest.raises(ValueError, match="Superfat must be 0-100%"):
            calculate_lye(oils, superfat_percent=150.0, naoh_percent=100.0, koh_percent=0.0)


class TestRoundingPrecision:
    """Test output rounding to 1 decimal place (per spec Section 6.3)"""

    def test_output_rounded_to_one_decimal(self):
        """TDD: All outputs rounded to 1 decimal place"""
        oils = [OilInput(weight_g=1000, sap_naoh=0.134, sap_koh=0.188)]

        result = calculate_lye(oils, superfat_percent=5.0, naoh_percent=100.0, koh_percent=0.0)

        # Check all values have max 1 decimal place
        assert result.naoh_g == round(result.naoh_g, 1)
        assert result.koh_g == round(result.koh_g, 1)
        assert result.total_g == round(result.total_g, 1)
