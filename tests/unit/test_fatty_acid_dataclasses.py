"""
Unit tests for CI-02 service return-type migration in
``app/services/fatty_acid_calculator.py``.

Locks in the frozen-dataclass contract for ``OilFattyAcids`` and
``FattyAcidProfile``. Math correctness is covered elsewhere
(``tests/unit/test_calculation_services.py``).
"""

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from app.services.fatty_acid_calculator import (
    FattyAcidProfile,
    OilFattyAcids,
    calculate_fatty_acid_profile,
)


class TestFattyAcidProfileContract:
    def test_is_frozen_dataclass(self):
        profile = FattyAcidProfile(lauric=48.0)
        assert is_dataclass(profile)
        with pytest.raises(FrozenInstanceError):
            profile.lauric = 0.0  # type: ignore[misc]

    def test_defaults_zero_every_field(self):
        profile = FattyAcidProfile()
        for field_name in (
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "ricinoleic",
            "oleic",
            "linoleic",
            "linolenic",
        ):
            assert getattr(profile, field_name) == 0.0

    def test_from_acids_rounds_each_field(self):
        profile = FattyAcidProfile.from_acids({"lauric": 47.99, "oleic": 8.48, "palmitic": 9.04})
        assert profile.lauric == 48.0
        assert profile.oleic == 8.5
        assert profile.palmitic == 9.0

    def test_derived_totals_and_ratio(self):
        profile = FattyAcidProfile(
            lauric=20.0,
            myristic=10.0,
            palmitic=10.0,
            stearic=5.0,
            oleic=40.0,
            linoleic=10.0,
            linolenic=2.0,
            ricinoleic=0.0,
        )
        assert profile.saturated_total == 45.0
        assert profile.unsaturated_total == 52.0
        assert profile.sat_unsat_ratio == "45:52"


class TestOilFattyAcidsContract:
    def test_is_frozen_dataclass(self):
        oil = OilFattyAcids(percentage=50.0, fatty_acids={"lauric": 48.0})
        assert is_dataclass(oil)
        with pytest.raises(FrozenInstanceError):
            oil.percentage = 0.0  # type: ignore[misc]


class TestReturnTypesRoundTrip:
    def test_calculate_fatty_acid_profile_returns_fatty_acid_profile(self):
        oils = [
            OilFattyAcids(percentage=100.0, fatty_acids={"lauric": 48.0, "oleic": 8.0}),
        ]
        result = calculate_fatty_acid_profile(oils)
        assert isinstance(result, FattyAcidProfile)
        assert result.lauric == 48.0
        assert result.oleic == 8.0
