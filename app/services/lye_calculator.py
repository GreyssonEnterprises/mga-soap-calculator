"""
Lye Calculation Service

Implements saponification value (SAP) based lye weight calculations for
NaOH (sodium hydroxide), KOH (potassium hydroxide), and mixed lye recipes.

Formulas per spec Section 5.1:
- Total SAP = Σ(oil_weight × oil_sap_value)
- Lye needed = Total SAP × (1 - superfat/100)
- For mixed lye: NaOH_weight = total_lye × naoh_percent/100
"""
from typing import Dict, List


class OilInput:
    """Oil input with weight and SAP values"""

    def __init__(self, weight_g: float, sap_naoh: float, sap_koh: float):
        self.weight_g = weight_g
        self.sap_naoh = sap_naoh
        self.sap_koh = sap_koh


class LyeResult:
    """Lye calculation result"""

    def __init__(self, naoh_g: float, koh_g: float, total_g: float):
        self.naoh_g = round(naoh_g, 1)
        self.koh_g = round(koh_g, 1)
        self.total_g = round(total_g, 1)


def calculate_lye(
    oils: List[OilInput],
    superfat_percent: float,
    naoh_percent: float = 100.0,
    koh_percent: float = 0.0
) -> LyeResult:
    """
    Calculate lye weights for soap recipe.

    INDUSTRY CONVENTION: Mixed lye percentages are BY WEIGHT.
    "70% NaOH / 30% KOH" means 70% of total lye WEIGHT is NaOH.
    This is Formula A - weighted-average SAP method.

    TDD Evidence: Validates against SoapCalc reference data
    - 500g Olive (50%), 300g Coconut (30%), 200g Palm (20%) @ 5% superfat
    - Expected: ~142.6g NaOH (100% NaOH)
    - Expected: ~200g KOH (100% KOH)
    - For 70% NaOH, 30% KOH: weight-based split

    Args:
        oils: List of OilInput with weights and SAP values
        superfat_percent: Percentage of unsaponified fats (0-100)
        naoh_percent: Percentage of total lye as NaOH BY WEIGHT (0-100)
        koh_percent: Percentage of total lye as KOH BY WEIGHT (0-100)

    Returns:
        LyeResult with naoh_g, koh_g, and total_g

    Raises:
        ValueError: If lye percentages don't sum to 100
        ValueError: If superfat is outside 0-100 range
    """
    # Validate inputs
    if not 0 <= superfat_percent <= 100:
        raise ValueError(f"Superfat must be 0-100%, got {superfat_percent}")

    if abs(naoh_percent + koh_percent - 100.0) > 0.01:
        raise ValueError(
            f"NaOH% + KOH% must equal 100%, got {naoh_percent} + {koh_percent}"
        )

    # Calculate weighted-average SAP for the lye blend
    # Formula A: For each oil, blend its SAP values by lye percentages
    # This matches industry practice where percentages are BY WEIGHT
    total_oil_weight = sum(oil.weight_g for oil in oils)
    weighted_sap = 0.0

    for oil in oils:
        # Blend this oil's SAP values by the lye percentages
        oil_blended_sap = (
            oil.sap_naoh * (naoh_percent / 100) +
            oil.sap_koh * (koh_percent / 100)
        )
        # Weight by this oil's contribution to total
        oil_weight_ratio = oil.weight_g / total_oil_weight
        weighted_sap += oil_blended_sap * oil_weight_ratio

    # Apply superfat reduction
    # Superfat = percentage of oils left unsaponified
    superfat_multiplier = 1 - (superfat_percent / 100)

    # Calculate total lye needed using weighted SAP
    total_lye_needed = total_oil_weight * weighted_sap * superfat_multiplier

    # Split by weight percentages (industry convention)
    naoh_needed = total_lye_needed * (naoh_percent / 100)
    koh_needed = total_lye_needed * (koh_percent / 100)

    return LyeResult(
        naoh_g=naoh_needed,
        koh_g=koh_needed,
        total_g=total_lye_needed
    )


def validate_superfat(superfat_percent: float) -> Dict[str, str]:
    """
    Validate superfat percentage and generate warnings.

    TDD Evidence: Tests boundary conditions
    - 0-20%: Normal range, no warnings
    - >20%: High superfat warning (bar may be too soft/greasy)
    - <0%: Invalid (lye-heavy, dangerous)

    Args:
        superfat_percent: Superfat percentage to validate

    Returns:
        Dict with 'level' and 'message' if warning needed, empty dict otherwise
    """
    if superfat_percent < 0:
        return {
            'level': 'error',
            'message': f'Negative superfat ({superfat_percent}%) is dangerous - lye-heavy soap!'
        }

    if superfat_percent > 20:
        return {
            'level': 'warning',
            'message': f'High superfat ({superfat_percent}%) may produce soft, greasy bars'
        }

    return {}
