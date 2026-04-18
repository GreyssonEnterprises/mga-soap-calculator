"""
Lye Calculation Service

Implements saponification value (SAP) based lye weight calculations for
NaOH (sodium hydroxide), KOH (potassium hydroxide), and mixed lye recipes.

Formulas per spec Section 5.1:
- Total SAP = Σ(oil_weight × oil_sap_value)
- Lye needed = Total SAP × (1 - superfat/100)
- For mixed lye: NaOH_weight = total_lye × naoh_percent/100

CI-02 refactor: Replaced hand-rolled classes and the ambiguous
``dict[str, any]`` return from ``calculate_lye_with_purity`` with frozen
dataclasses (``OilInput``, ``LyeResult``, ``PurityWarning``, ``PurityResult``).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OilInput:
    """Oil input with weight and SAP values."""

    weight_g: float
    sap_naoh: float
    sap_koh: float


@dataclass(frozen=True)
class LyeResult:
    """Lye calculation result (grams, rounded to 1 decimal place)."""

    naoh_g: float
    koh_g: float
    total_g: float


@dataclass(frozen=True)
class PurityWarning:
    """Warning emitted when a purity value falls outside the typical commercial range."""

    type: str
    message: str


@dataclass(frozen=True)
class PurityResult:
    """Commercial-weight lye result (purity-adjusted) with optional warnings."""

    commercial_koh_g: float
    commercial_naoh_g: float
    pure_koh_equivalent_g: float
    pure_naoh_equivalent_g: float
    total_lye_g: float
    warnings: tuple[PurityWarning, ...] = field(default_factory=tuple)


def calculate_lye(
    oils: list[OilInput],
    superfat_percent: float,
    naoh_percent: float = 100.0,
    koh_percent: float = 0.0,
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
        LyeResult with naoh_g, koh_g, and total_g (each rounded to 1 decimal)

    Raises:
        ValueError: If lye percentages don't sum to 100
        ValueError: If superfat is outside 0-100 range
    """
    # Validate inputs
    if not 0 <= superfat_percent <= 100:
        raise ValueError(f"Superfat must be 0-100%, got {superfat_percent}")

    if abs(naoh_percent + koh_percent - 100.0) > 0.01:
        raise ValueError(f"NaOH% + KOH% must equal 100%, got {naoh_percent} + {koh_percent}")

    # Calculate weighted-average SAP for the lye blend
    # Formula A: For each oil, blend its SAP values by lye percentages
    # This matches industry practice where percentages are BY WEIGHT
    total_oil_weight = sum(oil.weight_g for oil in oils)
    weighted_sap = 0.0

    for oil in oils:
        # Blend this oil's SAP values by the lye percentages
        oil_blended_sap = oil.sap_naoh * (naoh_percent / 100) + oil.sap_koh * (koh_percent / 100)
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
        naoh_g=round(naoh_needed, 1),
        koh_g=round(koh_needed, 1),
        total_g=round(total_lye_needed, 1),
    )


def validate_superfat(superfat_percent: float) -> dict[str, str]:
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
            "level": "error",
            "message": f"Negative superfat ({superfat_percent}%) is dangerous - lye-heavy soap!",
        }

    if superfat_percent > 20:
        return {
            "level": "warning",
            "message": f"High superfat ({superfat_percent}%) may produce soft, greasy bars",
        }

    return {}


def calculate_lye_with_purity(
    pure_koh_needed: float,
    pure_naoh_needed: float,
    koh_purity: float = 90.0,
    naoh_purity: float = 100.0,
) -> PurityResult:
    """
    Calculate commercial lye weights adjusted for purity.

    Industry reality: Commercial KOH is typically 85-95% pure due to moisture
    absorption (hygroscopic). NaOH is typically 98-100% pure (more stable).
    This function adjusts pure lye requirements to account for commercial
    purity, telling users how much *actual product* to weigh out.

    Formula (Spec 002-lye-purity, Section "Enhanced Formula"):
    - commercial_weight = pure_lye_needed / (purity / 100)

    Example: 117.1g pure KOH needed at 90% purity
    → 117.1 / 0.90 = 130.1g commercial KOH to weigh out

    TDD Evidence: Validates against spec reference test case
    - Input: 117.1g pure KOH, 90% purity
    - Expected: 130.1g commercial KOH (±0.5g tolerance)

    Args:
        pure_koh_needed: Pure KOH required for saponification (g)
        pure_naoh_needed: Pure NaOH required for saponification (g)
        koh_purity: KOH purity percentage (50-100, default 90)
        naoh_purity: NaOH purity percentage (50-100, default 100)

    Returns:
        PurityResult with commercial weights, pure equivalents, and the tuple
        of ``PurityWarning`` values (empty when no warnings apply).

    Note:
        Input validation (50-100% range) enforced by Pydantic schema.
        This function assumes valid inputs and focuses on calculation + warnings.
    """
    # Convert percentages to decimals
    koh_purity_decimal = koh_purity / 100
    naoh_purity_decimal = naoh_purity / 100

    # Calculate commercial weights (what user actually weighs)
    commercial_koh = pure_koh_needed / koh_purity_decimal
    commercial_naoh = pure_naoh_needed / naoh_purity_decimal

    # Generate warnings for unusual purity values (Spec lines 273-276)
    warnings: list[PurityWarning] = []

    # KOH typical range: 85-95%
    if koh_purity < 85 or koh_purity > 95:
        warnings.append(
            PurityWarning(
                type="unusual_purity",
                message=(
                    f"KOH purity of {koh_purity}% is outside typical commercial range (85-95%)"
                ),
            )
        )

    # NaOH typical range: 98-100%
    if naoh_purity < 98:
        warnings.append(
            PurityWarning(
                type="unusual_purity",
                message=(
                    f"NaOH purity of {naoh_purity}% is below typical commercial grade (98-100%)"
                ),
            )
        )

    return PurityResult(
        commercial_koh_g=round(commercial_koh, 1),
        commercial_naoh_g=round(commercial_naoh, 1),
        pure_koh_equivalent_g=round(pure_koh_needed, 1),
        pure_naoh_equivalent_g=round(pure_naoh_needed, 1),
        total_lye_g=round(commercial_koh + commercial_naoh, 1),
        warnings=tuple(warnings),
    )
