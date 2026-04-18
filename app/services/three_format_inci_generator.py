"""
Three-format INCI label generation service (Spec 003)

Generates raw_inci (pre-saponification), saponified_inci (post-saponification),
and common_names formats from calculation recipe data.

All ingredients sorted by percentage (descending) per regulatory requirements.
"""

from decimal import Decimal

from app.models.oil import Oil
from app.services.inci_naming import get_saponified_inci_name


class IngredientData:
    """Single ingredient with all three naming formats and percentage"""

    def __init__(
        self,
        raw_inci_name: str,
        saponified_inci_name: str | None,
        common_name: str,
        percentage: float,
        category: str,
        notes: str | None = None,
    ):
        self.raw_inci_name = raw_inci_name
        self.saponified_inci_name = saponified_inci_name
        self.common_name = common_name
        self.percentage = percentage
        self.category = category
        self.notes = notes


def calculate_total_batch_weight(recipe_data: dict) -> Decimal:
    """
    Calculate total batch weight from recipe data

    Includes: oils + water + lye

    Args:
        recipe_data: Recipe JSONB data from Calculation model

    Returns:
        Total batch weight in grams
    """
    total = Decimal("0")

    # Add oil weights
    # NOTE: persisted recipe_data uses "weight_g" (see _calculation_pipeline).
    # Keep in sync with the main oil-iteration loop below.
    oils = recipe_data.get("oils", [])
    for oil_item in oils:
        weight = Decimal(str(oil_item.get("weight_g", 0)))
        total += weight

    # Add water weight
    water_weight = Decimal(str(recipe_data.get("water_weight_g", 0)))
    total += water_weight

    # Add lye weights
    lye = recipe_data.get("lye", {})
    naoh_weight = Decimal(str(lye.get("naoh_weight_g", 0)))
    koh_weight = Decimal(str(lye.get("koh_weight_g", 0)))
    total += naoh_weight + koh_weight

    return total


def generate_three_format_labels(
    recipe_data: dict,
    oils_dict: dict[str, Oil],
    format_filter: str = "all",
    include_percentages: bool = False,
    line_by_line: bool = False,
) -> tuple[str | None, str | None, str | None, list[dict]]:
    """
    Generate INCI labels in all three formats from recipe data

    Args:
        recipe_data: Recipe JSONB data from Calculation model
        oils_dict: Dictionary of oil_id -> Oil model instances
        format_filter: Which formats to generate
            ("all", "raw_inci", "saponified_inci", "common_names")
        include_percentages: Whether to include percentage values in label strings
        line_by_line: Whether to use newline separation instead of commas

    Returns:
        Tuple of (raw_inci, saponified_inci, common_names, ingredients_breakdown)

    Raises:
        ValueError: If oils referenced in recipe are not in oils_dict
    """
    # Determine lye type from recipe data
    lye = recipe_data.get("lye", {})
    naoh_weight = float(lye.get("naoh_weight_g", 0))
    koh_weight = float(lye.get("koh_weight_g", 0))

    if naoh_weight > 0 and koh_weight == 0:
        lye_type = "naoh"
    elif koh_weight > 0 and naoh_weight == 0:
        lye_type = "koh"
    elif naoh_weight > 0 and koh_weight > 0:
        lye_type = "mixed"
    else:
        raise ValueError("Recipe must have either NaOH or KOH lye")

    # Calculate total batch weight
    total_weight = calculate_total_batch_weight(recipe_data)

    if total_weight == 0:
        raise ValueError("Recipe has zero total weight")

    # Build ingredient list with all data
    ingredients: list[IngredientData] = []

    # Add water
    water_weight = Decimal(str(recipe_data.get("water_weight_g", 0)))
    if water_weight > 0:
        water_pct = float((water_weight / total_weight) * 100)
        ingredients.append(
            IngredientData(
                raw_inci_name="Aqua",
                saponified_inci_name="Aqua",
                common_name="Water",
                percentage=water_pct,
                category="water",
                notes=None,
            )
        )

    # Add oils
    # NOTE: persisted recipe_data from _calculation_pipeline uses "id" and "weight_g"
    # (not "oil_id" / "weight_grams"). Keep in sync with _recipe_data_payload.
    oils = recipe_data.get("oils", [])
    for oil_item in oils:
        oil_id = oil_item["id"]

        if oil_id not in oils_dict:
            raise ValueError(f"Oil not found in database: {oil_id}")

        oil = oils_dict[oil_id]
        weight = Decimal(str(oil_item["weight_g"]))
        percentage = float((weight / total_weight) * 100)

        # Get saponified name based on lye type
        if lye_type == "mixed":
            # For mixed lye, use NaOH as primary
            saponified_name, _ = get_saponified_inci_name(oil, "naoh")
        else:
            saponified_name, _ = get_saponified_inci_name(oil, lye_type)

        ingredients.append(
            IngredientData(
                raw_inci_name=oil.inci_name,
                saponified_inci_name=saponified_name,
                common_name=oil.common_name,
                percentage=percentage,
                category="oil",
                notes=f"Saponifies to {saponified_name}",
            )
        )

    # Add lye (only in raw format, not in saponified)
    if naoh_weight > 0:
        lye_pct = float((Decimal(str(naoh_weight)) / total_weight) * 100)
        ingredients.append(
            IngredientData(
                raw_inci_name="Sodium Hydroxide",
                saponified_inci_name=None,  # Not in saponified format
                common_name="Sodium Hydroxide",
                percentage=lye_pct,
                category="lye",
                notes="Excluded in saponified format",
            )
        )

    if koh_weight > 0:
        lye_pct = float((Decimal(str(koh_weight)) / total_weight) * 100)
        ingredients.append(
            IngredientData(
                raw_inci_name="Potassium Hydroxide",
                saponified_inci_name=None,  # Not in saponified format
                common_name="Potassium Hydroxide",
                percentage=lye_pct,
                category="lye",
                notes="Excluded in saponified format",
            )
        )

    # Sort by percentage (descending) - REGULATORY REQUIREMENT
    ingredients.sort(key=lambda x: x.percentage, reverse=True)

    # Build label strings based on format_filter
    separator = "\n" if line_by_line else ", "

    raw_inci = None
    saponified_inci = None
    common_names = None

    if format_filter in ("all", "raw_inci"):
        # Raw INCI: includes all ingredients with botanical INCI names
        raw_parts = []
        for ing in ingredients:
            if include_percentages:
                raw_parts.append(f"{ing.raw_inci_name} ({ing.percentage:.1f}%)")
            else:
                raw_parts.append(ing.raw_inci_name)
        raw_inci = separator.join(raw_parts)

    if format_filter in ("all", "saponified_inci"):
        # Saponified INCI: exclude lye, use saponified names for oils
        saponified_parts = []
        for ing in ingredients:
            if ing.saponified_inci_name:  # Excludes lye (None)
                if include_percentages:
                    saponified_parts.append(f"{ing.saponified_inci_name} ({ing.percentage:.1f}%)")
                else:
                    saponified_parts.append(ing.saponified_inci_name)
        saponified_inci = separator.join(saponified_parts)

    if format_filter in ("all", "common_names"):
        # Common names: consumer-friendly names
        common_parts = []
        for ing in ingredients:
            if include_percentages:
                common_parts.append(f"{ing.common_name} ({ing.percentage:.1f}%)")
            else:
                common_parts.append(ing.common_name)
        common_names = separator.join(common_parts)

    # Build ingredients breakdown (all ingredients, all formats)
    breakdown = []
    for ing in ingredients:
        breakdown.append(
            {
                "name": ing.raw_inci_name,  # Use raw INCI as default name
                "percentage": round(ing.percentage, 1),
                "category": ing.category,
                "notes": ing.notes,
            }
        )

    return raw_inci, saponified_inci, common_names, breakdown
