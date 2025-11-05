"""
Tests for total_oil_weight_g (batch size) parameter handling

TDD Evidence: Verifies fix for batch size bug - API was ignoring user-specified
total_oil_weight_g and always using hardcoded 1000g default.

Bug Report: User requests 700g batch, API returns 1000g batch
Fix: Added total_oil_weight_g parameter to schema with proper default and wiring
"""
import pytest
from app.schemas.requests import CalculationRequest, OilInput, LyeConfig, WaterConfig


class TestBatchSizeParameter:
    """Test explicit batch size handling"""

    def test_explicit_700g_batch_size(self):
        """TDD: User specifies 700g total_oil_weight_g → calculations use 700g"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0,
            total_oil_weight_g=700.0
        )

        assert request.total_oil_weight_g == 700.0

    def test_explicit_1500g_batch_size(self):
        """TDD: User specifies 1500g → larger batch calculations"""
        request = CalculationRequest(
            oils=[OilInput(id="coconut_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0,
            total_oil_weight_g=1500.0
        )

        assert request.total_oil_weight_g == 1500.0

    def test_omitted_batch_size_defaults_to_1000g(self):
        """TDD: No total_oil_weight_g specified → defaults to 1000g (backward compatible)"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0
            # total_oil_weight_g omitted - should default to 1000.0
        )

        assert request.total_oil_weight_g == 1000.0

    def test_very_small_batch_50g(self):
        """TDD: Edge case - tiny 50g batch for testing"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0,
            total_oil_weight_g=50.0
        )

        assert request.total_oil_weight_g == 50.0

    def test_very_large_batch_5000g(self):
        """TDD: Edge case - large 5kg commercial batch"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0,
            total_oil_weight_g=5000.0
        )

        assert request.total_oil_weight_g == 5000.0

    def test_zero_batch_size_invalid(self):
        """TDD: Batch size must be > 0 (caught by Field(gt=0))"""
        with pytest.raises(Exception):  # Pydantic validation error
            CalculationRequest(
                oils=[OilInput(id="olive_oil", percentage=100.0)],
                lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
                water=WaterConfig(method="water_percent_of_oils", value=38.0),
                superfat_percent=5.0,
                total_oil_weight_g=0.0  # Invalid
            )

    def test_negative_batch_size_invalid(self):
        """TDD: Negative batch size rejected"""
        with pytest.raises(Exception):  # Pydantic validation error
            CalculationRequest(
                oils=[OilInput(id="olive_oil", percentage=100.0)],
                lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
                water=WaterConfig(method="water_percent_of_oils", value=38.0),
                superfat_percent=5.0,
                total_oil_weight_g=-100.0  # Invalid
            )


class TestBatchSizeCalculationFlow:
    """Test that batch size propagates correctly through calculation logic"""

    def test_batch_size_affects_oil_weights(self):
        """
        TDD: Batch size scales oil weights correctly
        700g batch @ 100% olive → 700g olive oil (not 1000g)
        """
        from app.services.validation import normalize_oil_inputs

        oils = [OilInput(id="olive_oil", percentage=100.0)]
        normalized = normalize_oil_inputs(oils, total_weight_g=700.0)

        assert len(normalized) == 1
        assert normalized[0].weight_g == 700.0
        assert normalized[0].percentage == 100.0

    def test_batch_size_affects_multi_oil_blend(self):
        """
        TDD: Batch size scales multi-oil recipe correctly
        700g batch @ 70% olive + 30% coconut → 490g olive + 210g coconut
        """
        from app.services.validation import normalize_oil_inputs

        oils = [
            OilInput(id="olive_oil", percentage=70.0),
            OilInput(id="coconut_oil", percentage=30.0)
        ]
        normalized = normalize_oil_inputs(oils, total_weight_g=700.0)

        olive = next(o for o in normalized if o.id == "olive_oil")
        coconut = next(o for o in normalized if o.id == "coconut_oil")

        assert olive.weight_g == 490.0  # 70% of 700g
        assert coconut.weight_g == 210.0  # 30% of 700g

    def test_batch_size_affects_additive_percentages(self):
        """
        TDD: Additive percentages calculated from correct batch size
        20g kaolin in 700g batch = 2.9% rounded (not 2.0% from 1000g)
        """
        from app.schemas.requests import AdditiveInput
        from app.services.validation import normalize_additive_inputs

        additives = [AdditiveInput(id="kaolin_clay", weight_g=20.0)]
        normalized = normalize_additive_inputs(additives, total_oil_weight_g=700.0)

        assert len(normalized) == 1
        assert normalized[0].weight_g == 20.0
        # 20g / 700g = 2.857... → rounds to 2.9%
        assert normalized[0].percentage == 2.9


class TestBatchSizeRegressionPrevention:
    """Ensure batch size fix doesn't break existing features"""

    def test_purity_calculations_still_work(self):
        """TDD: Batch size change doesn't affect purity feature"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(
                naoh_percent=0,
                koh_percent=100,
                koh_purity=85.0  # Non-standard purity
            ),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0,
            total_oil_weight_g=700.0
        )

        # Purity feature still accessible
        assert request.lye.koh_purity == 85.0
        assert request.total_oil_weight_g == 700.0

    def test_water_calculations_use_correct_batch_size(self):
        """TDD: Water as percent of oils uses correct total_oil_weight_g"""
        from app.services.water_calculator import calculate_water_from_oil_percent

        # 700g oils @ 38% water
        water_g = calculate_water_from_oil_percent(700.0, 38.0)

        # 700 * 0.38 = 266g (not 380g from 1000g)
        assert water_g == 266.0

    def test_existing_1000g_calculations_unchanged(self):
        """TDD: Backward compatibility - omitted batch_size still works"""
        request = CalculationRequest(
            oils=[OilInput(id="olive_oil", percentage=100.0)],
            lye=LyeConfig(naoh_percent=0, koh_percent=100, koh_purity=90),
            water=WaterConfig(method="water_percent_of_oils", value=38.0),
            superfat_percent=5.0
            # No total_oil_weight_g - backward compatible default
        )

        # Defaults to 1000g
        assert request.total_oil_weight_g == 1000.0

        # Normalizing with default produces 1000g oil
        from app.services.validation import normalize_oil_inputs
        normalized = normalize_oil_inputs(request.oils, total_weight_g=request.total_oil_weight_g)
        assert normalized[0].weight_g == 1000.0
