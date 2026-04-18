"""
Unit tests for the YAML-backed seed loader introduced by CI-07.

Locks in the invariants that the seed file continues to satisfy after being
migrated out of ``scripts/seed_data.py``:

- ``app/data/seed-data.yaml`` is present and parses as a mapping.
- Oil and additive counts match the pre-migration baseline (11 oils, 14
  additives).
- Every oil record carries the required spec fields (SAP values, 8 fatty
  acids, 7 quality contributions, INCI name).
- Every additive carries a valid confidence level.
- The back-compat shim ``scripts.seed_data`` re-exports the same data as the
  loader.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.data.seed_loader import (
    ADDITIVE_SEED_DATA,
    OIL_SEED_DATA,
    SEED_FILE_PATH,
    load_seed_data,
)

_REQUIRED_FATTY_ACIDS = (
    "lauric",
    "myristic",
    "palmitic",
    "stearic",
    "ricinoleic",
    "oleic",
    "linoleic",
    "linolenic",
)
_REQUIRED_QUALITY_CONTRIBS = (
    "hardness",
    "cleansing",
    "conditioning",
    "bubbly_lather",
    "creamy_lather",
    "longevity",
    "stability",
)
_VALID_CONFIDENCE_LEVELS = {"high", "medium", "low"}


class TestSeedFilePresence:
    def test_yaml_file_exists(self):
        assert SEED_FILE_PATH.exists(), (
            f"Seed file missing at {SEED_FILE_PATH}. It is the canonical source."
        )

    def test_yaml_top_level_is_mapping(self):
        with SEED_FILE_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert isinstance(data, dict)
        assert "oils" in data
        assert "additives" in data


class TestSeedCountsPreserved:
    # Catalog may grow over time as new oils / additives are added for MGA
    # reference recipes. Assert the pre-migration baseline is preserved as a
    # floor — never fewer than the 11 oils and 14 additives the Phase 3 YAML
    # migration captured from the prior Python seed script.

    def test_oil_count_at_or_above_baseline(self):
        assert len(OIL_SEED_DATA) >= 11

    def test_additive_count_at_or_above_baseline(self):
        assert len(ADDITIVE_SEED_DATA) >= 14


class TestOilRecordShape:
    @pytest.mark.parametrize("oil", OIL_SEED_DATA, ids=[oil["id"] for oil in OIL_SEED_DATA])
    def test_oil_has_sap_values_and_inci_name(self, oil):
        assert oil["id"]
        assert oil["common_name"]
        assert oil["inci_name"]
        assert isinstance(oil["sap_value_naoh"], (int, float))
        assert isinstance(oil["sap_value_koh"], (int, float))

    @pytest.mark.parametrize("oil", OIL_SEED_DATA, ids=[oil["id"] for oil in OIL_SEED_DATA])
    def test_oil_has_complete_fatty_acid_profile(self, oil):
        assert "fatty_acids" in oil
        for acid in _REQUIRED_FATTY_ACIDS:
            assert acid in oil["fatty_acids"], f"{oil['id']} missing {acid}"

    @pytest.mark.parametrize("oil", OIL_SEED_DATA, ids=[oil["id"] for oil in OIL_SEED_DATA])
    def test_oil_has_complete_quality_contributions(self, oil):
        assert "quality_contributions" in oil
        for metric in _REQUIRED_QUALITY_CONTRIBS:
            assert metric in oil["quality_contributions"], f"{oil['id']} missing {metric}"


class TestAdditiveRecordShape:
    @pytest.mark.parametrize(
        "additive",
        ADDITIVE_SEED_DATA,
        ids=[add["id"] for add in ADDITIVE_SEED_DATA],
    )
    def test_additive_has_valid_confidence_level(self, additive):
        assert additive["confidence_level"] in _VALID_CONFIDENCE_LEVELS

    @pytest.mark.parametrize(
        "additive",
        ADDITIVE_SEED_DATA,
        ids=[add["id"] for add in ADDITIVE_SEED_DATA],
    )
    def test_additive_has_usage_and_quality_effects(self, additive):
        assert "typical_usage_min_percent" in additive
        assert "typical_usage_max_percent" in additive
        assert "quality_effects" in additive
        assert isinstance(additive["quality_effects"], dict)
        assert additive["quality_effects"], f"{additive['id']} has empty quality_effects"


class TestLoadSeedDataAPI:
    def test_loader_accepts_explicit_path(self, tmp_path: Path):
        sample = tmp_path / "seed.yaml"
        sample.write_text(
            """
oils:
  - id: fake
    common_name: Fake
    inci_name: Fake Oil
    sap_value_naoh: 0.1
    sap_value_koh: 0.1
    iodine_value: 10.0
    ins_value: 10.0
    fatty_acids:
      lauric: 0.0
      myristic: 0.0
      palmitic: 0.0
      stearic: 0.0
      ricinoleic: 0.0
      oleic: 100.0
      linoleic: 0.0
      linolenic: 0.0
    quality_contributions:
      hardness: 0.0
      cleansing: 0.0
      conditioning: 100.0
      bubbly_lather: 0.0
      creamy_lather: 0.0
      longevity: 0.0
      stability: 0.0
additives: []
""",
            encoding="utf-8",
        )
        data = load_seed_data(sample)
        assert len(data["oils"]) == 1
        assert data["additives"] == []

    def test_loader_rejects_non_mapping_root(self, tmp_path: Path):
        sample = tmp_path / "broken.yaml"
        sample.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ValueError, match="top-level mapping"):
            load_seed_data(sample)


class TestBackwardCompatibleShim:
    def test_scripts_seed_data_re_exports_loader_lists(self):
        # Round-trip via the legacy import path used by existing callers.
        from scripts import seed_data as legacy

        assert legacy.OIL_SEED_DATA is OIL_SEED_DATA
        assert legacy.ADDITIVE_SEED_DATA is ADDITIVE_SEED_DATA
