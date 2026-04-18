"""
Unit tests for app/data/reference-recipes.yaml.

Validates that MGA's captured production recipes load, parse, and remain
structurally sound. Recipes missing catalog entries (e.g., beef tallow
not yet seeded) are permitted as long as the gaps are documented in
each recipe's `catalog_gaps` field.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REFERENCE_YAML = (
    Path(__file__).parent.parent.parent
    / "app"
    / "data"
    / "reference-recipes.yaml"
)
SEED_YAML = (
    Path(__file__).parent.parent.parent
    / "app"
    / "data"
    / "seed-data.yaml"
)


@pytest.fixture(scope="module")
def reference_doc() -> dict:
    return yaml.safe_load(REFERENCE_YAML.read_text())


@pytest.fixture(scope="module")
def seed_oil_ids() -> set[str]:
    doc = yaml.safe_load(SEED_YAML.read_text())
    return {o["id"] for o in doc.get("oils", [])}


@pytest.fixture(scope="module")
def seed_additive_ids() -> set[str]:
    doc = yaml.safe_load(SEED_YAML.read_text())
    return {a["id"] for a in doc.get("additives", [])}


@pytest.mark.unit
class TestReferenceRecipes:
    def test_yaml_loads(self, reference_doc: dict) -> None:
        assert isinstance(reference_doc, dict)
        assert "recipes" in reference_doc
        assert isinstance(reference_doc["recipes"], list)

    def test_has_expected_recipe_count(self, reference_doc: dict) -> None:
        # Midnight Morsels (1) + 24 new captures (17 top-level minus 3 non-
        # saponified plus 10 Midnight High Tea) = 25.
        assert len(reference_doc["recipes"]) >= 25

    def test_recipe_ids_are_unique(self, reference_doc: dict) -> None:
        ids = [r["id"] for r in reference_doc["recipes"]]
        assert len(ids) == len(set(ids)), f"duplicate recipe ids: {ids}"

    def test_every_recipe_has_required_fields(self, reference_doc: dict) -> None:
        required = {"id", "common_name", "description", "lye", "water",
                    "superfat_percent", "oils"}
        for recipe in reference_doc["recipes"]:
            missing = required - set(recipe.keys())
            assert not missing, f"recipe {recipe.get('id')} missing {missing}"

    def test_lye_block_is_valid(self, reference_doc: dict) -> None:
        for recipe in reference_doc["recipes"]:
            lye = recipe["lye"]
            assert lye["type"] in {"naoh", "koh", "mixed"}
            # naoh_purity defaults to 100 per schema rules; some recipes omit
            if "naoh_purity" in lye:
                assert 80 <= lye["naoh_purity"] <= 100

    def test_water_block_is_valid(self, reference_doc: dict) -> None:
        valid_methods = {"percent_of_oils", "lye_concentration",
                         "water_lye_ratio"}
        for recipe in reference_doc["recipes"]:
            water = recipe["water"]
            assert water["method"] in valid_methods
            assert isinstance(water["value"], (int, float))
            assert water["value"] > 0

    def test_superfat_is_reasonable(self, reference_doc: dict) -> None:
        for recipe in reference_doc["recipes"]:
            sf = recipe["superfat_percent"]
            assert 0 <= sf <= 20, f"{recipe['id']} superfat out of range: {sf}"

    def test_oils_sum_to_100_or_gap_documented(self, reference_doc: dict) -> None:
        """
        Each recipe's oils[] must either sum to 100% (+/- 0.1) OR declare
        the missing oils in catalog_gaps. This lets us add recipes that
        reference uncataloged oils (e.g., beef tallow) without lying about
        the math.
        """
        tolerance = 0.1
        for recipe in reference_doc["recipes"]:
            total = sum(o["percentage"] for o in recipe.get("oils", []))
            if abs(total - 100.0) <= tolerance:
                continue
            gaps = recipe.get("catalog_gaps") or []
            assert gaps, (
                f"{recipe['id']}: oils sum to {total:.2f} (not 100) and no "
                f"catalog_gaps entry documents the missing fats"
            )

    def test_every_oil_id_resolves_or_is_gapped(
        self, reference_doc: dict, seed_oil_ids: set[str]
    ) -> None:
        for recipe in reference_doc["recipes"]:
            for oil in recipe.get("oils", []):
                oil_id = oil["id"]
                if oil_id in seed_oil_ids:
                    continue
                gaps_text = " ".join(recipe.get("catalog_gaps") or [])
                assert oil_id in gaps_text, (
                    f"{recipe['id']}: oil '{oil_id}' is not in seed-data.yaml "
                    f"and is not mentioned in catalog_gaps"
                )

    def test_every_additive_id_resolves_or_is_gapped(
        self, reference_doc: dict, seed_additive_ids: set[str]
    ) -> None:
        for recipe in reference_doc["recipes"]:
            for additive in recipe.get("additives", []) or []:
                aid = additive["id"]
                if aid in seed_additive_ids:
                    continue
                gaps_text = " ".join(recipe.get("catalog_gaps") or [])
                assert aid in gaps_text, (
                    f"{recipe['id']}: additive '{aid}' is not in "
                    f"seed-data.yaml and is not mentioned in catalog_gaps"
                )
