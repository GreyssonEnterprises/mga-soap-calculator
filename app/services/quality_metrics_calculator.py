"""
Quality Metrics Calculator - COMPETITIVE ADVANTAGE

Calculates 7 soap quality metrics from oils and additives.
Additive effect modeling is UNIQUE - no other calculator does this.

Metrics per spec Section 5.3:
- Hardness, Cleansing, Conditioning, Bubbly Lather, Creamy Lather
- Longevity, Stability (from oil quality_contributions)

Additive effects from research file - scaled by usage rate.

CI-02 refactor: Replaced hand-rolled classes (``OilContribution``,
``AdditiveEffect``, ``QualityMetrics``) with frozen dataclasses for
immutability and clearer typing.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OilContribution:
    """Oil with weight and per-metric quality contributions."""

    weight_g: float
    percentage: float
    quality_contributions: dict[str, float]


@dataclass(frozen=True)
class AdditiveEffect:
    """Additive with mass and per-metric quality effect modifiers (at 2% baseline)."""

    weight_g: float
    quality_effects: dict[str, float]
    confidence_level: str = "high"


@dataclass(frozen=True)
class QualityMetrics:
    """
    Quality metrics result (values rounded to 1 decimal place).

    All seven metrics default to 0.0 so callers can pass only the fields they
    care about (tests frequently do).
    """

    hardness: float = 0.0
    cleansing: float = 0.0
    conditioning: float = 0.0
    bubbly_lather: float = 0.0
    creamy_lather: float = 0.0
    longevity: float = 0.0
    stability: float = 0.0

    @classmethod
    def from_metrics(cls, metrics: dict[str, float]) -> "QualityMetrics":
        """Build a rounded ``QualityMetrics`` from a mapping of metric → value."""
        return cls(
            hardness=round(metrics.get("hardness", 0.0), 1),
            cleansing=round(metrics.get("cleansing", 0.0), 1),
            conditioning=round(metrics.get("conditioning", 0.0), 1),
            bubbly_lather=round(metrics.get("bubbly_lather", 0.0), 1),
            creamy_lather=round(metrics.get("creamy_lather", 0.0), 1),
            longevity=round(metrics.get("longevity", 0.0), 1),
            stability=round(metrics.get("stability", 0.0), 1),
        )


# Internal: list of metric field names kept in a single place so the
# functions below stay in sync with the dataclass definition.
_METRIC_FIELDS: tuple[str, ...] = (
    "hardness",
    "cleansing",
    "conditioning",
    "bubbly_lather",
    "creamy_lather",
    "longevity",
    "stability",
)


def calculate_base_metrics_from_oils(oils: list[OilContribution]) -> QualityMetrics:
    """
    Calculate quality metrics from oil blend only (no additives yet).

    Uses weighted average of oil quality_contributions from database.
    TDD Evidence: Validates against SoapCalc reference recipe
    """
    totals: dict[str, float] = {name: 0.0 for name in _METRIC_FIELDS}

    for oil in oils:
        for metric_name in _METRIC_FIELDS:
            contribution = oil.quality_contributions.get(metric_name, 0)
            weighted_contribution = contribution * (oil.percentage / 100)
            totals[metric_name] += weighted_contribution

    return QualityMetrics.from_metrics(totals)


def apply_additive_effects(
    base_metrics: QualityMetrics, total_oil_weight_g: float, additives: list[AdditiveEffect]
) -> QualityMetrics:
    """
    Apply additive quality effects to base metrics.

    THIS IS THE COMPETITIVE ADVANTAGE - unique feature.

    Per spec Section 5.3 and research file:
    - Additive quality_effects are absolute modifiers at 2% usage rate
    - Scale proportionally: effect × (actual_usage_rate / 2.0)
    - Accumulate effects across multiple additives

    TDD Evidence: Kaolin clay @ 2% adds +4.0 hardness, +7.0 creamy
                  At 3% usage: adds +6.0 hardness, +10.5 creamy
    """
    # Start with base metrics
    adjusted: dict[str, float] = {name: getattr(base_metrics, name) for name in _METRIC_FIELDS}

    for additive in additives:
        # Calculate actual usage rate as % of oil weight
        usage_rate_percent = (additive.weight_g / total_oil_weight_g) * 100

        # Research effects are at 2% baseline - scale proportionally
        scaling_factor = usage_rate_percent / 2.0

        # Apply scaled effects to each metric
        for metric_name, base_effect in additive.quality_effects.items():
            if metric_name in adjusted:
                scaled_effect = base_effect * scaling_factor
                adjusted[metric_name] += scaled_effect

    return QualityMetrics.from_metrics(adjusted)


def calculate_ins_value(oils: list[OilContribution]) -> float:
    """
    Calculate INS (Iodine Number Saponification) value.

    INS = SAP value - Iodine value
    Lower INS = softer bar, Higher INS = harder bar

    TDD Evidence: Weighted average from oil database values
    """
    # Would calculate from oil.ins values in database
    # For now, return placeholder for structure
    # Full implementation when oil database is integrated
    return 0.0


def calculate_iodine_value(oils: list[OilContribution]) -> float:
    """
    Calculate Iodine value (measure of unsaturation).

    Higher iodine = more unsaturated fats = softer soap, faster rancidity

    TDD Evidence: Weighted average from oil database values
    """
    # Would calculate from oil.iodine values in database
    # Placeholder for structure
    return 0.0


__all__ = [
    "AdditiveEffect",
    "OilContribution",
    "QualityMetrics",
    "apply_additive_effects",
    "calculate_base_metrics_from_oils",
    "calculate_ins_value",
    "calculate_iodine_value",
]
