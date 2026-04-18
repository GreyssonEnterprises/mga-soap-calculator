"""
Unit tests for the three-stage calculation pipeline in
``app/api/v1/_calculation_pipeline.py``.

The pure ``compute_recipe`` stage is exercised here without a live DB or an
HTTP client. ``resolve_inputs`` and ``persist_calculation`` depend on an
``AsyncSession`` and are covered by the existing integration/e2e test suites
(``tests/integration/test_soapcalc_accuracy.py``, the full create-calculation
happy path, etc.).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.api.v1._calculation_pipeline import (
    ComputedRecipe,
    ResolvedInputs,
    _recipe_data_payload,
    _results_data_payload,
    compute_recipe,
)
from app.schemas.requests import AdditiveInput, LyeConfig, OilInput, WaterConfig


def _make_oil_row(
    oil_id: str,
    common_name: str,
    sap_naoh: float,
    sap_koh: float,
    iodine: float,
    ins: float,
    fatty_acids: dict[str, float],
    quality_contributions: dict[str, float],
) -> SimpleNamespace:
    """Build a duck-typed stand-in for the `Oil` SQLAlchemy model."""
    return SimpleNamespace(
        id=oil_id,
        common_name=common_name,
        sap_value_naoh=sap_naoh,
        sap_value_koh=sap_koh,
        iodine_value=iodine,
        ins_value=ins,
        fatty_acids=fatty_acids,
        quality_contributions=quality_contributions,
    )


def _olive_coconut_palm_inputs(superfat_percent: float = 5.0) -> ResolvedInputs:
    """Standard 50/30/20 Olive/Coconut/Palm recipe at 1000g, 100% NaOH."""
    db_oils = {
        "olive": _make_oil_row(
            "olive",
            "Olive Oil",
            sap_naoh=0.134,
            sap_koh=0.188,
            iodine=84.0,
            ins=109.0,
            fatty_acids={"palmitic": 11.0, "stearic": 4.0, "oleic": 72.0, "linoleic": 10.0},
            quality_contributions={"hardness": 17.0, "conditioning": 83.0, "longevity": 25.0},
        ),
        "coconut": _make_oil_row(
            "coconut",
            "Coconut Oil",
            sap_naoh=0.178,
            sap_koh=0.250,
            iodine=10.0,
            ins=258.0,
            fatty_acids={"lauric": 48.0, "myristic": 19.0},
            quality_contributions={"hardness": 79.0, "cleansing": 67.0, "bubbly_lather": 67.0},
        ),
        "palm": _make_oil_row(
            "palm",
            "Palm Oil",
            sap_naoh=0.142,
            sap_koh=0.199,
            iodine=53.0,
            ins=145.0,
            fatty_acids={"palmitic": 44.0, "oleic": 39.0},
            quality_contributions={"hardness": 50.0, "conditioning": 49.0},
        ),
    }
    normalized_oils = [
        OilInput(id="olive", weight_g=500.0, percentage=50.0),
        OilInput(id="coconut", weight_g=300.0, percentage=30.0),
        OilInput(id="palm", weight_g=200.0, percentage=20.0),
    ]
    return ResolvedInputs(
        normalized_oils=normalized_oils,
        total_oil_weight_g=1000.0,
        db_oils=db_oils,
        normalized_additives=[],
        db_additives={},
        unknown_additive_ids=[],
        lye=LyeConfig(naoh_percent=100.0, koh_percent=0.0, koh_purity=90.0, naoh_purity=100.0),
        water=WaterConfig(method="water_percent_of_oils", value=38.0),
        superfat_percent=superfat_percent,
    )


class TestComputeRecipeHappyPath:
    def test_returns_frozen_computed_recipe(self):
        inputs = _olive_coconut_palm_inputs()
        computed = compute_recipe(inputs)
        assert isinstance(computed, ComputedRecipe)
        # Frozen — any field mutation raises.
        with pytest.raises(Exception):  # FrozenInstanceError
            computed.iodine_value = 0.0  # type: ignore[misc]

    def test_returns_expected_lye_and_water_shapes(self):
        inputs = _olive_coconut_palm_inputs()
        computed = compute_recipe(inputs)

        # 100% NaOH, 5% superfat, SoapCalc-ish reference math.
        # NaOH weight should be ~141-142g (see tests/unit/test_lye_calculator.py).
        assert 140.0 <= computed.recipe.lye.naoh_weight_g <= 145.0
        assert computed.recipe.lye.koh_weight_g == 0.0
        # Water @ 38% of 1000g oils → 380.0g.
        assert computed.recipe.water_weight_g == 380.0
        assert computed.recipe.water_method == "water_percent_of_oils"
        assert computed.recipe.water_method_value == 38.0

    def test_quality_metrics_base_and_final_equal_when_no_additives(self):
        inputs = _olive_coconut_palm_inputs()
        computed = compute_recipe(inputs)
        # Without additives the two snapshots should match on every metric.
        for metric in (
            "hardness",
            "cleansing",
            "conditioning",
            "bubbly_lather",
            "creamy_lather",
            "longevity",
            "stability",
        ):
            assert getattr(computed.quality_metrics, metric) == getattr(
                computed.quality_metrics_base, metric
            )

    def test_warnings_empty_for_standard_recipe(self):
        inputs = _olive_coconut_palm_inputs(superfat_percent=5.0)
        computed = compute_recipe(inputs)
        # 100% NaOH + default 90% KOH purity → no purity warnings.
        # 5% superfat → no superfat warning.
        assert computed.warnings == []


class TestComputeRecipeAdditives:
    def test_unknown_additive_id_surfaces_as_warning(self):
        base = _olive_coconut_palm_inputs()
        inputs = ResolvedInputs(
            normalized_oils=base.normalized_oils,
            total_oil_weight_g=base.total_oil_weight_g,
            db_oils=base.db_oils,
            normalized_additives=[
                AdditiveInput(id="ghost", weight_g=20.0, percentage=2.0),
            ],
            db_additives={},
            unknown_additive_ids=["ghost"],
            lye=base.lye,
            water=base.water,
            superfat_percent=base.superfat_percent,
        )
        computed = compute_recipe(inputs)
        codes = {w.code for w in computed.warnings}
        assert "UNKNOWN_ADDITIVE_ID" in codes

    def test_high_superfat_emits_warning(self):
        inputs = _olive_coconut_palm_inputs(superfat_percent=25.0)
        computed = compute_recipe(inputs)
        codes = {w.code for w in computed.warnings}
        assert "HIGH_SUPERFAT" in codes


class TestPersistPayloadHelpers:
    """The private JSONB-builder helpers round-trip the numeric data."""

    def test_recipe_data_payload_includes_lye_and_oils(self):
        inputs = _olive_coconut_palm_inputs()
        computed = compute_recipe(inputs)
        payload = _recipe_data_payload(inputs, computed)

        assert payload["total_oil_weight_g"] == 1000.0
        assert payload["superfat_percent"] == inputs.superfat_percent
        assert payload["water_method"] == "water_percent_of_oils"
        assert payload["water_method_value"] == 38.0
        assert {row["id"] for row in payload["oils"]} == {"olive", "coconut", "palm"}
        assert "naoh_weight_g" in payload["lye"]
        assert "pure_koh_equivalent_g" in payload["lye"]

    def test_results_data_payload_includes_both_metric_snapshots(self):
        inputs = _olive_coconut_palm_inputs()
        computed = compute_recipe(inputs)
        payload = _results_data_payload(computed)
        assert "quality_metrics" in payload
        assert "quality_metrics_base" in payload
        assert "fatty_acid_profile" in payload
        assert "saturated_unsaturated_ratio" in payload
        # iodine + ins echoed into both metric snapshots.
        assert payload["quality_metrics"]["iodine"] == computed.iodine_value
        assert payload["quality_metrics_base"]["ins"] == computed.ins_value
