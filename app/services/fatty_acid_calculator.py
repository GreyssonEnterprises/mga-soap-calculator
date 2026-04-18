"""
Fatty Acid Profile Calculator

Calculates weighted average fatty acid composition of oil blend.
Fatty acids tracked per spec Section 5.4:
- Saturated: Lauric, Myristic, Palmitic, Stearic
- Unsaturated: Ricinoleic, Oleic, Linoleic, Linolenic

CI-02 refactor: Replaced hand-rolled ``OilFattyAcids`` / ``FattyAcidProfile``
classes with frozen dataclasses. Derived totals remain computed properties
(saturated_total, unsaturated_total, sat_unsat_ratio) since they're pure
functions of the stored fields.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OilFattyAcids:
    """Oil with fatty acid profile (percentages keyed by fatty-acid name)."""

    percentage: float
    fatty_acids: dict[str, float]


@dataclass(frozen=True)
class FattyAcidProfile:
    """
    Fatty acid composition result (percent-by-weight, rounded to 1 decimal place).

    Saturated acids: lauric, myristic, palmitic, stearic
    Unsaturated acids: ricinoleic, oleic, linoleic, linolenic
    """

    # Saturated
    lauric: float = 0.0
    myristic: float = 0.0
    palmitic: float = 0.0
    stearic: float = 0.0
    # Unsaturated
    ricinoleic: float = 0.0
    oleic: float = 0.0
    linoleic: float = 0.0
    linolenic: float = 0.0

    @classmethod
    def from_acids(cls, acids: dict[str, float]) -> "FattyAcidProfile":
        """Build a rounded ``FattyAcidProfile`` from a mapping of acid → percent."""
        return cls(
            lauric=round(acids.get("lauric", 0.0), 1),
            myristic=round(acids.get("myristic", 0.0), 1),
            palmitic=round(acids.get("palmitic", 0.0), 1),
            stearic=round(acids.get("stearic", 0.0), 1),
            ricinoleic=round(acids.get("ricinoleic", 0.0), 1),
            oleic=round(acids.get("oleic", 0.0), 1),
            linoleic=round(acids.get("linoleic", 0.0), 1),
            linolenic=round(acids.get("linolenic", 0.0), 1),
        )

    @property
    def saturated_total(self) -> float:
        """Total saturated fatty acids."""
        return round(self.lauric + self.myristic + self.palmitic + self.stearic, 1)

    @property
    def unsaturated_total(self) -> float:
        """Total unsaturated fatty acids."""
        return round(self.ricinoleic + self.oleic + self.linoleic + self.linolenic, 1)

    @property
    def sat_unsat_ratio(self) -> str:
        """Saturated:Unsaturated ratio as a string."""
        sat = int(round(self.saturated_total))
        unsat = int(round(self.unsaturated_total))
        return f"{sat}:{unsat}"


_ACID_FIELDS: tuple[str, ...] = (
    "lauric",
    "myristic",
    "palmitic",
    "stearic",
    "ricinoleic",
    "oleic",
    "linoleic",
    "linolenic",
)


def calculate_fatty_acid_profile(oils: list[OilFattyAcids]) -> FattyAcidProfile:
    """
    Calculate weighted average fatty acid profile.

    Each oil contributes its fatty acids weighted by percentage in blend.

    TDD Evidence: Profile should sum to ~100% (97-100% due to minor acids)
    """
    acids: dict[str, float] = {name: 0.0 for name in _ACID_FIELDS}

    for oil in oils:
        for acid_name in _ACID_FIELDS:
            acid_percentage = oil.fatty_acids.get(acid_name, 0)
            weighted = acid_percentage * (oil.percentage / 100)
            acids[acid_name] += weighted

    return FattyAcidProfile.from_acids(acids)
