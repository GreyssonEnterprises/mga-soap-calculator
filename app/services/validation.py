"""
Business Validation Logic (Tasks 3.2.1, 3.2.2, 3.2.3)

TDD Evidence: Tests written first in test_validation_logic.py
Implements spec Section 6 validation rules and warning generation.
"""

from app.schemas.requests import AdditiveInput, OilInput
from app.schemas.responses import Warning


def validate_oil_percentages(percentages: list[float]) -> bool:
    """
    Validate that oil percentages sum to exactly 100%.

    Per spec Section 6.1:
    - STRICT validation: sum must equal 100.0
    - Floating point tolerance: 0.1% (to handle rounding)

    Args:
        percentages: List of oil percentages

    Returns:
        True if valid

    Raises:
        ValueError: If percentages don't sum to 100%
    """
    total = sum(percentages)

    # Floating point tolerance of 0.1%
    if abs(total - 100.0) > 0.1:
        raise ValueError(f"Oil percentages must sum to exactly 100%, got {total:.2f}%")

    return True


def normalize_oil_inputs(
    oils: list[OilInput], total_weight_g: float | None = None
) -> list[OilInput]:
    """
    Normalize oil inputs to have both weight_g AND percentage.

    If weights provided: calculate percentages
    If percentages provided: calculate weights (requires total_weight_g)

    Args:
        oils: List of oil inputs
        total_weight_g: Total oil weight (required if percentages provided)

    Returns:
        List of normalized oil inputs with both fields populated
    """
    normalized = []

    # Case 1: All oils have weights
    if all(oil.weight_g is not None for oil in oils):
        total = sum(oil.weight_g for oil in oils)

        for oil in oils:
            percentage = (oil.weight_g / total) * 100
            normalized.append(
                OilInput(id=oil.id, weight_g=oil.weight_g, percentage=round(percentage, 1))
            )

    # Case 2: All oils have percentages
    elif all(oil.percentage is not None for oil in oils):
        if total_weight_g is None:
            raise ValueError("total_weight_g required when oils have percentages")

        for oil in oils:
            weight_g = (oil.percentage / 100) * total_weight_g
            normalized.append(
                OilInput(id=oil.id, weight_g=round(weight_g, 1), percentage=oil.percentage)
            )

    # Case 3: Mixed weights and percentages (more complex normalization)
    else:
        # For now, require all weights or all percentages
        raise ValueError("All oils must use either weights or percentages, not mixed")

    return normalized


def normalize_additive_inputs(
    additives: list[AdditiveInput], total_oil_weight_g: float
) -> list[AdditiveInput]:
    """
    Normalize additive inputs to have both weight_g AND percentage.

    Args:
        additives: List of additive inputs
        total_oil_weight_g: Total oil weight for percentage calculation

    Returns:
        List of normalized additive inputs
    """
    normalized = []

    for additive in additives:
        if additive.weight_g is not None:
            # Calculate percentage from weight
            percentage = (additive.weight_g / total_oil_weight_g) * 100
            normalized.append(
                AdditiveInput(
                    id=additive.id, weight_g=additive.weight_g, percentage=round(percentage, 1)
                )
            )
        elif additive.percentage is not None:
            # Calculate weight from percentage
            weight_g = (additive.percentage / 100) * total_oil_weight_g
            normalized.append(
                AdditiveInput(
                    id=additive.id, weight_g=round(weight_g, 1), percentage=additive.percentage
                )
            )

    return normalized


def generate_superfat_warnings(superfat_percent: float) -> list[Warning]:
    """
    Generate warnings for extreme superfat values.

    Per spec Section 6.2:
    - >20%: Warning about soft, greasy bars
    - <0%: Error (handled in validation, not warning)

    Args:
        superfat_percent: Superfat percentage

    Returns:
        List of warnings (may be empty)
    """
    warnings = []

    if superfat_percent > 20.0:
        warnings.append(
            Warning(
                code="HIGH_SUPERFAT",
                message=f"Superfat >20% (got {superfat_percent}%) may produce soft, greasy bars",
                severity="warning",
                details={"superfat_percent": superfat_percent},
            )
        )

    return warnings


def generate_unknown_additive_warning(additive_id: str) -> Warning:
    """
    Generate warning for unknown additive ID.

    Per spec Section 6.2:
    - Unknown additives generate warning (non-blocking)
    - Calculation proceeds excluding unknown additives

    Args:
        additive_id: Unknown additive ID

    Returns:
        Warning object
    """
    return Warning(
        code="UNKNOWN_ADDITIVE_ID",
        message=f"Additive '{additive_id}' not found in database - excluded from calculation",
        severity="warning",
        details={"additive_id": additive_id},
    )


def round_to_precision(value: float, decimals: int = 1) -> float:
    """
    Round numeric value to specified decimal precision.

    Per spec Section 6.3:
    - All outputs rounded to 1 decimal place

    Args:
        value: Numeric value to round
        decimals: Number of decimal places (default: 1)

    Returns:
        Rounded value
    """
    return round(value, decimals)


def round_quality_metrics(metrics: dict[str, float]) -> dict[str, float]:
    """
    Apply precision rounding to all quality metrics.

    Args:
        metrics: Dictionary of metric names to values

    Returns:
        Dictionary with all values rounded to 1 decimal
    """
    return {name: round_to_precision(value) for name, value in metrics.items()}
