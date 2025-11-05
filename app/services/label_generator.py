"""
INCI label generation service

Orchestrates percentage calculation and INCI naming to produce complete labels
"""
from typing import List, Tuple, Dict, Any
from decimal import Decimal

from app.models.oil import Oil
from app.services.inci_naming import get_saponified_inci_name
from app.services.percentage_calculator import calculate_ingredient_percentages


class InciIngredientDetail:
    """Detailed ingredient information for INCI label"""

    def __init__(
        self,
        oil: Oil,
        percentage: Decimal,
        saponified_inci_name: str,
        is_generated: bool
    ):
        self.oil_id = oil.id
        self.common_name = oil.common_name
        self.saponified_inci_name = saponified_inci_name
        self.percentage = float(percentage)
        self.is_generated = is_generated

    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            'oil_id': self.oil_id,
            'common_name': self.common_name,
            'saponified_inci_name': self.saponified_inci_name,
            'percentage': self.percentage,
            'is_generated': self.is_generated
        }


def sort_ingredients_by_percentage(ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort ingredients by percentage in descending order.

    Used for regulatory-compliant INCI labels where ingredients must be listed
    from highest to lowest percentage.

    Args:
        ingredients: List of ingredient dictionaries containing 'percentage' key
                    Each dict must have at minimum: {'name': str, 'percentage': Decimal}

    Returns:
        Sorted list of ingredients (descending by percentage)
        Original list is not modified

    Examples:
        >>> ingredients = [
        ...     {'name': 'Water', 'percentage': Decimal('35.0')},
        ...     {'name': 'Olive Oil', 'percentage': Decimal('50.0')},
        ...     {'name': 'Lye', 'percentage': Decimal('15.0')}
        ... ]
        >>> sorted_list = sort_ingredients_by_percentage(ingredients)
        >>> sorted_list[0]['name']
        'Olive Oil'
        >>> sorted_list[-1]['name']
        'Lye'
    """
    if not ingredients:
        return []

    # Sort by percentage descending
    # Create new list to avoid modifying original
    return sorted(ingredients, key=lambda x: x['percentage'], reverse=True)


def generate_inci_label(
    oil_weights: dict[str, Decimal],
    oils_dict: dict[str, Oil],
    lye_type: str
) -> Tuple[str, List[InciIngredientDetail]]:
    """
    Generate complete INCI label from oil weights.

    Process:
    1. Calculate percentages for each oil
    2. Get saponified INCI name for each oil
    3. Sort by percentage (descending)
    4. Format as comma-separated label

    Args:
        oil_weights: Dictionary of oil_id -> weight (Decimal)
        oils_dict: Dictionary of oil_id -> Oil model
        lye_type: 'naoh' or 'koh'

    Returns:
        Tuple of (inci_label_string, list_of_ingredient_details)

    Raises:
        ValueError: If oils_dict doesn't contain all oil_ids from oil_weights

    Examples:
        >>> oil_weights = {'coconut-oil': Decimal('300'), 'olive-oil': Decimal('700')}
        >>> oils_dict = {'coconut-oil': coconut_oil_model, 'olive-oil': olive_oil_model}
        >>> label, details = generate_inci_label(oil_weights, oils_dict, 'naoh')
        >>> label
        'Sodium Olivate, Sodium Cocoate'
        >>> len(details)
        2
    """
    # Validate all oils are present
    for oil_id in oil_weights:
        if oil_id not in oils_dict:
            raise ValueError(f"Oil not found in database: {oil_id}")

    # Step 1: Calculate percentages
    percentages = calculate_ingredient_percentages(oil_weights)

    # Step 2: Build ingredient details with INCI names
    ingredient_details = []

    for oil_id, percentage in percentages.items():
        oil = oils_dict[oil_id]

        # Get saponified INCI name
        saponified_name, is_generated = get_saponified_inci_name(oil, lye_type)

        detail = InciIngredientDetail(
            oil=oil,
            percentage=percentage,
            saponified_inci_name=saponified_name,
            is_generated=is_generated
        )
        ingredient_details.append(detail)

    # Step 3: Sort by percentage (descending)
    ingredient_details.sort(key=lambda x: x.percentage, reverse=True)

    # Step 4: Format INCI label string
    inci_names = [detail.saponified_inci_name for detail in ingredient_details]
    inci_label = ", ".join(inci_names)

    return inci_label, ingredient_details
