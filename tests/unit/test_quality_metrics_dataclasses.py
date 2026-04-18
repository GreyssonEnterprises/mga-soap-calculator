"""
Unit tests for CI-02 service return-type migration in
``app/services/quality_metrics_calculator.py``.

These tests lock in the new frozen-dataclass contracts:
- ``OilContribution``, ``AdditiveEffect``, and ``QualityMetrics`` are frozen.
- ``QualityMetrics.from_metrics`` rounds every field to 1 decimal place.

Math correctness for base-metric calculation and additive-effect modeling is
covered by ``tests/unit/test_calculation_services.py``; this file focuses on
the type/immutability contract the rest of the codebase relies on.
"""

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from app.services.quality_metrics_calculator import (
    AdditiveEffect,
    OilContribution,
    QualityMetrics,
    apply_additive_effects,
    calculate_base_metrics_from_oils,
)


class TestQualityMetricsContract:
    def test_is_frozen_dataclass(self):
        metrics = QualityMetrics(hardness=40.0)
        assert is_dataclass(metrics)
        with pytest.raises(FrozenInstanceError):
            metrics.hardness = 100.0  # type: ignore[misc]

    def test_defaults_zero_every_metric(self):
        metrics = QualityMetrics()
        assert metrics.hardness == 0.0
        assert metrics.cleansing == 0.0
        assert metrics.conditioning == 0.0
        assert metrics.bubbly_lather == 0.0
        assert metrics.creamy_lather == 0.0
        assert metrics.longevity == 0.0
        assert metrics.stability == 0.0

    def test_from_metrics_rounds_to_one_decimal(self):
        # Use round-down values that don't straddle Python banker's rounding.
        metrics = QualityMetrics.from_metrics(
            {
                "hardness": 48.12,
                "cleansing": 33.48,
                "conditioning": 46.04,
            }
        )
        assert metrics.hardness == 48.1
        assert metrics.cleansing == 33.5
        assert metrics.conditioning == 46.0

    def test_from_metrics_ignores_unknown_keys(self):
        # Extra keys should not break the constructor — they are dropped silently.
        metrics = QualityMetrics.from_metrics({"hardness": 10.0, "iodine": 99.0, "ins": 150.0})
        assert metrics.hardness == 10.0


class TestOilContributionAndAdditiveEffectContract:
    def test_oil_contribution_is_frozen(self):
        oc = OilContribution(
            weight_g=100.0, percentage=10.0, quality_contributions={"hardness": 50.0}
        )
        assert is_dataclass(oc)
        with pytest.raises(FrozenInstanceError):
            oc.weight_g = 0.0  # type: ignore[misc]

    def test_additive_effect_is_frozen_with_default_confidence(self):
        ae = AdditiveEffect(weight_g=20.0, quality_effects={"hardness": 4.0})
        assert is_dataclass(ae)
        assert ae.confidence_level == "high"
        with pytest.raises(FrozenInstanceError):
            ae.weight_g = 0.0  # type: ignore[misc]


class TestReturnTypesRoundTripThroughCalculators:
    """Live compute paths still return the new `QualityMetrics` dataclass."""

    def test_calculate_base_metrics_returns_quality_metrics(self):
        oils = [
            OilContribution(
                weight_g=500.0,
                percentage=50.0,
                quality_contributions={"hardness": 20.0},
            ),
            OilContribution(
                weight_g=500.0,
                percentage=50.0,
                quality_contributions={"hardness": 60.0},
            ),
        ]
        result = calculate_base_metrics_from_oils(oils)
        assert isinstance(result, QualityMetrics)
        assert result.hardness == 40.0

    def test_apply_additive_effects_returns_quality_metrics(self):
        base = QualityMetrics(hardness=40.0)
        additives = [AdditiveEffect(weight_g=20.0, quality_effects={"hardness": 4.0})]
        result = apply_additive_effects(base, total_oil_weight_g=1000.0, additives=additives)
        assert isinstance(result, QualityMetrics)
        assert result.hardness == 44.0  # +4.0 at 2% baseline == 1.0 scaling factor
