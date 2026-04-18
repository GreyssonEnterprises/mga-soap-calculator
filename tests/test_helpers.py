"""
Test helper utilities for corrected API request formats.

Provides properly formatted request builders matching app/schemas/requests.py
"""

from typing import Any


def build_calculation_request(
    oils: list[dict[str, Any]],
    superfat_percent: float = 5.0,
    water_percent_of_oils: float = 38.0,
    lye_type: str = "NaOH",
    additives: list[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Build a properly formatted calculation request.

    Args:
        oils: List of {"id": str, "percentage": float} or {"id": str, "weight_g": float}
        superfat_percent: Superfat percentage (0-100)
        water_percent_of_oils: Water as % of oils (default method)
        lye_type: "NaOH" or "KOH" (simplified - converts to lye config)
        additives: List of {"id": str, "weight_g": float} or {"id": str, "percentage": float}

    Returns:
        Properly formatted CalculationRequest dict
    """
    # Convert simplified lye_type to LyeConfig format
    lye_config = {
        "naoh_percent": 100.0 if lye_type == "NaOH" else 0.0,
        "koh_percent": 0.0 if lye_type == "NaOH" else 100.0,
    }

    # Build water config (using water_percent_of_oils as default method)
    water_config = {"method": "water_percent_of_oils", "value": water_percent_of_oils}

    return {
        "oils": oils,
        "lye": lye_config,
        "water": water_config,
        "superfat_percent": superfat_percent,
        "additives": additives or [],
    }


def build_oil_input(
    oil_id: str, percentage: float = None, weight_g: float = None
) -> dict[str, Any]:
    """
    Build properly formatted OilInput.

    Args:
        oil_id: Oil database ID (e.g., "olive_oil", "coconut_oil")
        percentage: Percentage of total oils (0-100)
        weight_g: Weight in grams

    Returns:
        OilInput dict with "id" key (not "oil_id")
    """
    oil = {"id": oil_id}
    if percentage is not None:
        oil["percentage"] = percentage
    if weight_g is not None:
        oil["weight_g"] = weight_g
    return oil


def build_additive_input(
    additive_id: str, weight_g: float = None, percentage: float = None
) -> dict[str, Any]:
    """
    Build properly formatted AdditiveInput.

    Args:
        additive_id: Additive database ID (e.g., "kaolin_clay", "titanium_dioxide")
        weight_g: Weight in grams
        percentage: Percentage of total oils

    Returns:
        AdditiveInput dict with "id" key (not "additive_id")
    """
    additive = {"id": additive_id}
    if weight_g is not None:
        additive["weight_g"] = weight_g
    if percentage is not None:
        additive["percentage"] = percentage
    return additive
