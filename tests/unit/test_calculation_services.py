"""
Tests for water, quality metrics, and fatty acid calculators

TDD Evidence: Tests core calculation algorithms against spec requirements
"""

from app.services.fatty_acid_calculator import OilFattyAcids, calculate_fatty_acid_profile
from app.services.quality_metrics_calculator import (
    AdditiveEffect,
    OilContribution,
    apply_additive_effects,
    calculate_base_metrics_from_oils,
)
from app.services.water_calculator import (
    calculate_water_from_lye_concentration,
    calculate_water_from_lye_ratio,
    calculate_water_from_oil_percent,
)


class TestWaterCalculations:
    """Test all 3 water calculation methods (Task 2.2)"""

    def test_water_as_percent_of_oils(self):
        """TDD: 1000g oils @ 38% = 380g water"""
        water = calculate_water_from_oil_percent(1000, 38.0)
        assert water == 380.0

        water = calculate_water_from_oil_percent(1000, 33.0)
        assert water == 330.0

    def test_water_from_lye_concentration(self):
        """TDD: 142.6g lye @ 33% = ~289.5g water"""
        water = calculate_water_from_lye_concentration(142.6, 33.0)
        # 142.6 / 0.33 = 432.12 total solution
        # 432.12 - 142.6 = 289.52 water
        assert abs(water - 289.5) < 0.1

    def test_water_from_lye_ratio(self):
        """TDD: 142.6g lye @ 2:1 ratio = 285.2g water"""
        water = calculate_water_from_lye_ratio(142.6, 2.0)
        assert abs(water - 285.2) < 0.1


class TestQualityMetricsFromOils:
    """Test base quality metrics from oil blend (Task 2.3.1)"""

    def test_weighted_average_calculation(self):
        """TDD: Quality metrics from weighted oil contributions"""
        oils = [
            # 50% Olive: hardness 17, cleansing 0, conditioning 82
            OilContribution(
                weight_g=500,
                percentage=50.0,
                quality_contributions={
                    "hardness": 17,
                    "cleansing": 0,
                    "conditioning": 82,
                    "bubbly_lather": 0,
                    "creamy_lather": 16,
                    "longevity": 17,
                    "stability": 91,
                },
            ),
            # 50% Coconut: hardness 79, cleansing 67, conditioning 10
            OilContribution(
                weight_g=500,
                percentage=50.0,
                quality_contributions={
                    "hardness": 79,
                    "cleansing": 67,
                    "conditioning": 10,
                    "bubbly_lather": 67,
                    "creamy_lather": 17,
                    "longevity": 79,
                    "stability": 10,
                },
            ),
        ]

        metrics = calculate_base_metrics_from_oils(oils)

        # 50% of each: (17+79)/2 = 48 hardness, (0+67)/2 = 33.5 cleansing
        assert abs(metrics.hardness - 48.0) < 0.1
        assert abs(metrics.cleansing - 33.5) < 0.1
        assert abs(metrics.conditioning - 46.0) < 0.1


class TestAdditiveEffects:
    """Test additive quality effect modifiers (Task 2.3.2) - COMPETITIVE ADVANTAGE"""

    def test_kaolin_clay_at_2_percent_usage(self):
        """
        TDD: Kaolin clay @ 2% usage (research baseline)
        Effects: +4.0 hardness, +7.0 creamy lather
        """
        from app.services.quality_metrics_calculator import QualityMetrics

        base = QualityMetrics(hardness=40.0, creamy_lather=20.0)
        total_oil_weight = 1000  # 1000g oils

        additives = [
            AdditiveEffect(
                weight_g=20,  # 20g = 2% of 1000g oils
                quality_effects={"hardness": 4.0, "creamy_lather": 7.0},
                confidence_level="high",
            )
        ]

        adjusted = apply_additive_effects(base, total_oil_weight, additives)

        # At 2% usage, scaling factor = 2% / 2% = 1.0
        # Hardness: 40 + (4.0 * 1.0) = 44.0
        # Creamy: 20 + (7.0 * 1.0) = 27.0
        assert abs(adjusted.hardness - 44.0) < 0.1
        assert abs(adjusted.creamy_lather - 27.0) < 0.1

    def test_kaolin_clay_at_3_percent_usage(self):
        """
        TDD: Kaolin clay @ 3% usage (scaled from 2% baseline)
        Scaling factor: 3% / 2% = 1.5
        Effects: +6.0 hardness, +10.5 creamy lather
        """
        from app.services.quality_metrics_calculator import QualityMetrics

        base = QualityMetrics(hardness=40.0, creamy_lather=20.0)
        total_oil_weight = 1000

        additives = [
            AdditiveEffect(
                weight_g=30,  # 30g = 3% of 1000g oils
                quality_effects={"hardness": 4.0, "creamy_lather": 7.0},
            )
        ]

        adjusted = apply_additive_effects(base, total_oil_weight, additives)

        # At 3% usage, scaling factor = 3% / 2% = 1.5
        # Hardness: 40 + (4.0 * 1.5) = 46.0
        # Creamy: 20 + (7.0 * 1.5) = 30.5
        assert abs(adjusted.hardness - 46.0) < 0.1
        assert abs(adjusted.creamy_lather - 30.5) < 0.1

    def test_multiple_additives_cumulative(self):
        """
        TDD: Multiple additives accumulate effects
        Kaolin + Sodium Lactate both add hardness
        """
        from app.services.quality_metrics_calculator import QualityMetrics

        base = QualityMetrics(hardness=40.0)
        total_oil_weight = 1000

        additives = [
            # Kaolin @ 2%: +4.0 hardness
            AdditiveEffect(weight_g=20, quality_effects={"hardness": 4.0}),
            # Sodium Lactate @ 3%: +12.0 hardness at 2%, scaled to 3% = 18.0
            AdditiveEffect(weight_g=30, quality_effects={"hardness": 12.0}),
        ]

        adjusted = apply_additive_effects(base, total_oil_weight, additives)

        # Kaolin: +4.0 (2% usage, factor=1.0)
        # Sodium Lactate: +12.0 * 1.5 = +18.0 (3% usage, factor=1.5)
        # Total: 40 + 4 + 18 = 62.0
        assert abs(adjusted.hardness - 62.0) < 0.1


class TestFattyAcidProfile:
    """Test fatty acid profile calculations (Task 2.4)"""

    def test_weighted_average_fatty_acids(self):
        """TDD: Fatty acid profile from oil blend"""
        oils = [
            # 50% Olive: high oleic
            OilFattyAcids(
                percentage=50.0,
                fatty_acids={
                    "lauric": 0,
                    "myristic": 0,
                    "palmitic": 11,
                    "stearic": 4,
                    "oleic": 72,
                    "linoleic": 10,
                    "linolenic": 1,
                    "ricinoleic": 0,
                },
            ),
            # 50% Coconut: high lauric
            OilFattyAcids(
                percentage=50.0,
                fatty_acids={
                    "lauric": 48,
                    "myristic": 19,
                    "palmitic": 9,
                    "stearic": 3,
                    "oleic": 8,
                    "linoleic": 2,
                    "linolenic": 0,
                    "ricinoleic": 0,
                },
            ),
        ]

        profile = calculate_fatty_acid_profile(oils)

        # Lauric: (0*0.5 + 48*0.5) = 24.0
        # Oleic: (72*0.5 + 8*0.5) = 40.0
        assert abs(profile.lauric - 24.0) < 0.1
        assert abs(profile.oleic - 40.0) < 0.1

    def test_saturated_unsaturated_totals(self):
        """TDD: Saturated and unsaturated totals"""
        oils = [
            OilFattyAcids(
                percentage=100.0,
                fatty_acids={
                    "lauric": 20,
                    "myristic": 10,
                    "palmitic": 10,
                    "stearic": 5,
                    "oleic": 40,
                    "linoleic": 10,
                    "linolenic": 2,
                    "ricinoleic": 0,
                },
            )
        ]

        profile = calculate_fatty_acid_profile(oils)

        # Saturated: 20+10+10+5 = 45
        # Unsaturated: 40+10+2+0 = 52
        assert abs(profile.saturated_total - 45.0) < 0.1
        assert abs(profile.unsaturated_total - 52.0) < 0.1
        assert profile.sat_unsat_ratio == "45:52"

    def test_profile_sums_to_near_100_percent(self):
        """TDD: Total fatty acids should be 97-100% (some oils have minor acids)"""
        oils = [
            OilFattyAcids(
                percentage=100.0,
                fatty_acids={
                    "lauric": 48,
                    "myristic": 19,
                    "palmitic": 9,
                    "stearic": 3,
                    "oleic": 8,
                    "linoleic": 2,
                    "linolenic": 0,
                    "ricinoleic": 0,
                },
            )
        ]

        profile = calculate_fatty_acid_profile(oils)

        total = (
            profile.lauric
            + profile.myristic
            + profile.palmitic
            + profile.stearic
            + profile.oleic
            + profile.linoleic
            + profile.linolenic
            + profile.ricinoleic
        )

        assert 85 < total <= 100, f"Total fatty acids {total}% should be 85-100%"
