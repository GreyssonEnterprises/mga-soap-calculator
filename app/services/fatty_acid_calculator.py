"""
Fatty Acid Profile Calculator

Calculates weighted average fatty acid composition of oil blend.
Fatty acids tracked per spec Section 5.4:
- Saturated: Lauric, Myristic, Palmitic, Stearic
- Unsaturated: Ricinoleic, Oleic, Linoleic, Linolenic
"""


class OilFattyAcids:
    """Oil with fatty acid profile"""

    def __init__(self, percentage: float, fatty_acids: dict[str, float]):
        self.percentage = percentage
        self.fatty_acids = fatty_acids


class FattyAcidProfile:
    """Fatty acid composition result"""

    def __init__(self, **acids):
        # Saturated
        self.lauric = round(acids.get("lauric", 0), 1)
        self.myristic = round(acids.get("myristic", 0), 1)
        self.palmitic = round(acids.get("palmitic", 0), 1)
        self.stearic = round(acids.get("stearic", 0), 1)
        # Unsaturated
        self.ricinoleic = round(acids.get("ricinoleic", 0), 1)
        self.oleic = round(acids.get("oleic", 0), 1)
        self.linoleic = round(acids.get("linoleic", 0), 1)
        self.linolenic = round(acids.get("linolenic", 0), 1)

    @property
    def saturated_total(self) -> float:
        """Total saturated fatty acids"""
        return round(self.lauric + self.myristic + self.palmitic + self.stearic, 1)

    @property
    def unsaturated_total(self) -> float:
        """Total unsaturated fatty acids"""
        return round(self.ricinoleic + self.oleic + self.linoleic + self.linolenic, 1)

    @property
    def sat_unsat_ratio(self) -> str:
        """Saturated:Unsaturated ratio as string"""
        sat = int(round(self.saturated_total))
        unsat = int(round(self.unsaturated_total))
        return f"{sat}:{unsat}"


def calculate_fatty_acid_profile(oils: list[OilFattyAcids]) -> FattyAcidProfile:
    """
    Calculate weighted average fatty acid profile.

    Each oil contributes its fatty acids weighted by percentage in blend.

    TDD Evidence: Profile should sum to ~100% (97-100% due to minor acids)
    """
    acids = {
        "lauric": 0.0,
        "myristic": 0.0,
        "palmitic": 0.0,
        "stearic": 0.0,
        "ricinoleic": 0.0,
        "oleic": 0.0,
        "linoleic": 0.0,
        "linolenic": 0.0,
    }

    for oil in oils:
        for acid_name in acids.keys():
            acid_percentage = oil.fatty_acids.get(acid_name, 0)
            weighted = acid_percentage * (oil.percentage / 100)
            acids[acid_name] += weighted

    return FattyAcidProfile(**acids)
