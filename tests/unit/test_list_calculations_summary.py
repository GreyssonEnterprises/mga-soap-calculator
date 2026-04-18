"""Unit tests for the CalculationSummary builder used by GET /api/v1/calculations.

Only covers the pure ``_summarize_calculation`` helper. Integration tests for
the list endpoint live alongside the other endpoint integration tests and
are skipped in PR CI by design (they need a live DB + auth fixture).
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.calculate import _summarize_calculation


def _calc(recipe_data, results_data) -> SimpleNamespace:
    """Build a minimal stand-in for the Calculation ORM row.

    ``_summarize_calculation`` only reads ``id``, ``created_at``,
    ``recipe_data``, and ``results_data`` — no ORM behavior required.
    """
    return SimpleNamespace(
        id=uuid4(),
        created_at=datetime(2026, 4, 18, 12, 0, tzinfo=UTC),
        recipe_data=recipe_data,
        results_data=results_data,
    )


_METRICS = {
    "hardness": 45.0,
    "cleansing": 20.0,
    "conditioning": 60.0,
    "bubbly_lather": 20.0,
    "creamy_lather": 25.0,
    "longevity": 40.0,
    "stability": 55.0,
    "iodine": 70.0,
    "ins": 150.0,
}


class TestTopOils:
    def test_returns_top_three_by_weight(self):
        calc = _calc(
            recipe_data={
                "total_oil_weight_g": 1000.0,
                "superfat_percent": 5.0,
                "oils": [
                    {"id": "olive_oil", "common_name": "Olive Oil", "weight_g": 600.0},
                    {"id": "coconut_oil", "common_name": "Coconut Oil", "weight_g": 250.0},
                    {"id": "shea_butter", "common_name": "Shea Butter", "weight_g": 100.0},
                    {"id": "castor_oil", "common_name": "Castor Oil", "weight_g": 50.0},
                ],
            },
            results_data={"quality_metrics": _METRICS},
        )

        summary = _summarize_calculation(calc)

        assert summary.top_oils == ["Olive Oil", "Coconut Oil", "Shea Butter"]
        assert summary.oil_count == 4
        assert summary.total_oil_weight_g == 1000.0
        assert summary.superfat_percent == 5.0

    def test_falls_back_to_id_when_common_name_missing(self):
        calc = _calc(
            recipe_data={
                "total_oil_weight_g": 500.0,
                "superfat_percent": 5.0,
                "oils": [
                    {"id": "olive_oil", "weight_g": 500.0},
                ],
            },
            results_data={"quality_metrics": _METRICS},
        )

        summary = _summarize_calculation(calc)

        assert summary.top_oils == ["olive_oil"]

    def test_handles_fewer_than_three_oils(self):
        calc = _calc(
            recipe_data={
                "total_oil_weight_g": 500.0,
                "superfat_percent": 0.0,
                "oils": [
                    {"id": "olive_oil", "common_name": "Olive Oil", "weight_g": 500.0},
                ],
            },
            results_data={"quality_metrics": _METRICS},
        )

        summary = _summarize_calculation(calc)

        assert summary.top_oils == ["Olive Oil"]
        assert summary.oil_count == 1


class TestMissingData:
    def test_empty_recipe_data_does_not_crash(self):
        calc = _calc(recipe_data={}, results_data={})

        summary = _summarize_calculation(calc)

        assert summary.oil_count == 0
        assert summary.top_oils == []
        assert summary.total_oil_weight_g == 0.0
        assert summary.superfat_percent == 0.0
        assert summary.quality_metrics.hardness == 0

    def test_null_jsonb_coerced_to_empty_dict(self):
        calc = _calc(recipe_data=None, results_data=None)

        summary = _summarize_calculation(calc)

        assert summary.oil_count == 0
        assert summary.top_oils == []


class TestQualityMetrics:
    def test_metrics_passed_through(self):
        calc = _calc(
            recipe_data={"total_oil_weight_g": 1000.0, "superfat_percent": 5.0, "oils": []},
            results_data={"quality_metrics": _METRICS},
        )

        summary = _summarize_calculation(calc)

        assert summary.quality_metrics.hardness == 45.0
        assert summary.quality_metrics.conditioning == 60.0
        assert summary.quality_metrics.ins == 150.0
