"""
Unit tests for CI-02 service return-type migration in `app/services/lye_calculator.py`.

These tests lock in the dataclass contracts introduced by the CI-02 refactor:
- ``OilInput`` / ``LyeResult`` / ``PurityWarning`` / ``PurityResult`` are all
  frozen dataclasses (hashable, immutable).
- ``calculate_lye_with_purity`` returns a ``PurityResult`` (not a dict), whose
  ``warnings`` field is always a tuple of ``PurityWarning`` (never ``None``).

Math correctness for the underlying calculations is covered elsewhere
(``test_lye_calculator.py``, ``test_purity_warnings.py``). This file focuses
on the return-type contract the rest of the codebase depends on.
"""

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from app.services.lye_calculator import (
    LyeResult,
    OilInput,
    PurityResult,
    PurityWarning,
    calculate_lye,
    calculate_lye_with_purity,
)


class TestOilInputAndLyeResultContract:
    """`OilInput` and `LyeResult` are frozen dataclasses."""

    def test_oil_input_is_frozen_dataclass(self):
        oil = OilInput(weight_g=500.0, sap_naoh=0.134, sap_koh=0.188)
        assert is_dataclass(oil)
        with pytest.raises(FrozenInstanceError):
            oil.weight_g = 999.0  # type: ignore[misc]

    def test_lye_result_is_frozen_dataclass(self):
        oils = [OilInput(weight_g=1000.0, sap_naoh=0.134, sap_koh=0.188)]
        result = calculate_lye(oils=oils, superfat_percent=5.0)
        assert is_dataclass(result)
        assert isinstance(result, LyeResult)
        with pytest.raises(FrozenInstanceError):
            result.naoh_g = 0.0  # type: ignore[misc]


class TestPurityResultContract:
    """`calculate_lye_with_purity` returns a PurityResult, not a dict."""

    def test_returns_purity_result_instance(self):
        result = calculate_lye_with_purity(pure_koh_needed=100.0, pure_naoh_needed=0.0)
        assert isinstance(result, PurityResult)
        assert is_dataclass(result)

    def test_is_frozen(self):
        result = calculate_lye_with_purity(pure_koh_needed=100.0, pure_naoh_needed=0.0)
        with pytest.raises(FrozenInstanceError):
            result.total_lye_g = 0.0  # type: ignore[misc]

    def test_typical_inputs_produce_empty_warnings_tuple(self):
        # 90% KOH + 100% NaOH are both inside the typical commercial ranges.
        result = calculate_lye_with_purity(
            pure_koh_needed=117.1,
            pure_naoh_needed=10.0,
            koh_purity=90.0,
            naoh_purity=100.0,
        )
        assert result.warnings == ()
        assert isinstance(result.warnings, tuple)

    def test_unusual_purity_emits_purity_warning_dataclass(self):
        result = calculate_lye_with_purity(
            pure_koh_needed=100.0,
            pure_naoh_needed=50.0,
            koh_purity=70.0,  # below 85% → KOH warning
            naoh_purity=90.0,  # below 98% → NaOH warning
        )
        assert len(result.warnings) == 2
        for warning in result.warnings:
            assert isinstance(warning, PurityWarning)
            assert warning.type == "unusual_purity"
            assert warning.message  # non-empty

    def test_attribute_access_matches_previous_dict_keys(self):
        """Caller-visible fields preserved from the pre-refactor dict shape."""
        result = calculate_lye_with_purity(
            pure_koh_needed=117.1,
            pure_naoh_needed=10.0,
            koh_purity=90.0,
            naoh_purity=100.0,
        )
        # Previously returned dict keys — now dataclass attributes
        assert hasattr(result, "commercial_koh_g")
        assert hasattr(result, "commercial_naoh_g")
        assert hasattr(result, "pure_koh_equivalent_g")
        assert hasattr(result, "pure_naoh_equivalent_g")
        assert hasattr(result, "total_lye_g")
        # Sanity-check the round-to-1dp contract is preserved
        assert result.commercial_koh_g == round(117.1 / 0.90, 1)
