"""
Percentage calculation service for soap formulations

Converts ingredient weights to percentages with high precision using Decimal arithmetic
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict

# Set high precision for Decimal calculations
getcontext().prec = 28


def calculate_ingredient_percentages(weights: Dict[str, Decimal]) -> Dict[str, Decimal]:
    """
    Calculate percentage of each ingredient in the total formulation.

    Args:
        weights: Dictionary of ingredient_id -> weight (grams)

    Returns:
        Dictionary of ingredient_id -> percentage (0-100)

    Raises:
        ValueError: If weights is empty, total is zero, or any weight is negative

    Examples:
        >>> weights = {'coconut': Decimal('300'), 'olive': Decimal('700')}
        >>> percentages = calculate_ingredient_percentages(weights)
        >>> percentages['coconut']
        Decimal('30.0')
        >>> percentages['olive']
        Decimal('70.0')
    """
    if not weights:
        raise ValueError("Weights dictionary cannot be empty")

    # Validate all weights are non-negative
    for ingredient_id, weight in weights.items():
        if weight < 0:
            raise ValueError(f"Negative weight not allowed: {ingredient_id} = {weight}")

    # Calculate total weight
    total_weight = sum(weights.values())

    if total_weight == 0:
        raise ValueError("Total weight cannot be zero")

    # Calculate percentages
    percentages = {}
    for ingredient_id, weight in weights.items():
        percentage = (weight / total_weight) * 100
        percentages[ingredient_id] = percentage

    return percentages


def normalize_percentages(percentages: Dict[str, Decimal]) -> Dict[str, Decimal]:
    """
    Normalize percentages to sum exactly to 100.0

    Handles rounding errors by distributing the difference across
    the largest percentages.

    Args:
        percentages: Dictionary of ingredient_id -> percentage

    Returns:
        Dictionary with percentages summing exactly to 100.0

    Examples:
        >>> percentages = {'a': Decimal('33.333'), 'b': Decimal('33.333'), 'c': Decimal('33.333')}
        >>> normalized = normalize_percentages(percentages)
        >>> sum(normalized.values())
        Decimal('100.0')
    """
    if not percentages:
        return {}

    # Round all percentages to 1 decimal place first
    rounded = {
        k: v.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        for k, v in percentages.items()
    }

    # Calculate difference from 100
    total = sum(rounded.values())
    diff = Decimal('100.0') - total

    if diff == 0:
        return rounded

    # Distribute difference to largest percentages
    # Sort by percentage (largest first), then by key for determinism
    sorted_items = sorted(
        rounded.items(),
        key=lambda x: (-x[1], x[0])
    )

    # Adjustment increment (0.1 for single decimal precision)
    increment = Decimal('0.1') if diff > 0 else Decimal('-0.1')
    adjustments_needed = abs(int(diff / increment))

    # Apply adjustments
    normalized = dict(sorted_items)
    for i in range(adjustments_needed):
        ingredient_id = sorted_items[i % len(sorted_items)][0]
        normalized[ingredient_id] += increment

    return normalized


def round_percentages_to_precision(
    percentages: Dict[str, Decimal],
    precision: int = 1
) -> Dict[str, Decimal]:
    """
    Round percentages to specified decimal precision.

    Ensures percentages still sum to 100.0 after rounding by applying
    normalization if needed.

    Args:
        percentages: Dictionary of ingredient_id -> percentage
        precision: Number of decimal places (default: 1)

    Returns:
        Dictionary with rounded percentages summing to 100.0

    Examples:
        >>> percentages = {'a': Decimal('33.456'), 'b': Decimal('66.544')}
        >>> rounded = round_percentages_to_precision(percentages, precision=1)
        >>> rounded['a']
        Decimal('33.5')
        >>> rounded['b']
        Decimal('66.5')
    """
    if not percentages:
        return {}

    # Create quantizer for desired precision
    if precision == 0:
        quantizer = Decimal('1')
    else:
        quantizer = Decimal('0.1') ** precision

    # Round each percentage
    rounded = {
        k: v.quantize(quantizer, rounding=ROUND_HALF_UP)
        for k, v in percentages.items()
    }

    # Check if rounding caused sum deviation
    total = sum(rounded.values())
    target = Decimal('100.0')

    if total == target:
        return rounded

    # Need to adjust for rounding errors
    diff = target - total

    # Find largest percentage to adjust
    # Sort by value (descending), then by key for determinism
    sorted_items = sorted(
        rounded.items(),
        key=lambda x: (-x[1], x[0])
    )

    # Adjust the largest percentage
    adjusted = dict(rounded)
    adjusted[sorted_items[0][0]] += diff

    return adjusted


def calculate_batch_percentages(batch_weights: Dict[str, any]) -> Dict[str, Decimal]:
    """
    Calculate percentage of each ingredient in complete batch.

    Handles all ingredient types: oils, water, lye, and additives.
    Used for regulatory-compliant INCI labels that require ALL ingredients
    sorted by percentage.

    Args:
        batch_weights: Dictionary with structure:
            {
                'oils': {'oil-id': Decimal('weight'), ...},
                'water': Decimal('weight'),
                'lye': {'naoh': Decimal('weight'), 'koh': Decimal('weight')},
                'additives': {'additive-id': Decimal('weight'), ...}
            }

    Returns:
        Dictionary of ingredient_id -> percentage (0-100)
        Flattened structure with all ingredients at same level

    Raises:
        ValueError: If batch_weights is invalid or total weight is zero

    Examples:
        >>> batch = {
        ...     'oils': {'coconut-oil': Decimal('300'), 'olive-oil': Decimal('700')},
        ...     'water': Decimal('380'),
        ...     'lye': {'naoh': Decimal('143')},
        ...     'additives': {}
        ... }
        >>> percentages = calculate_batch_percentages(batch)
        >>> percentages['olive-oil']  # Should be ~45% of total batch
        Decimal('45.7')
        >>> percentages['water']  # Should be ~25% of total batch
        Decimal('24.8')
    """
    if not batch_weights:
        raise ValueError("Batch weights cannot be empty")

    # Flatten all weights into single dictionary
    all_weights = {}

    # Add oils
    if 'oils' in batch_weights:
        for oil_id, weight in batch_weights['oils'].items():
            if weight < 0:
                raise ValueError(f"Negative weight not allowed: {oil_id} = {weight}")
            all_weights[oil_id] = weight

    # Add water
    if 'water' in batch_weights:
        water_weight = batch_weights['water']
        if water_weight < 0:
            raise ValueError(f"Negative weight not allowed: water = {water_weight}")
        all_weights['water'] = water_weight

    # Add lye (can be NaOH, KOH, or both)
    if 'lye' in batch_weights:
        for lye_type, weight in batch_weights['lye'].items():
            if weight < 0:
                raise ValueError(f"Negative weight not allowed: {lye_type} = {weight}")
            all_weights[lye_type] = weight

    # Add additives
    if 'additives' in batch_weights:
        for additive_id, weight in batch_weights['additives'].items():
            if weight < 0:
                raise ValueError(f"Negative weight not allowed: {additive_id} = {weight}")
            all_weights[additive_id] = weight

    # Use existing percentage calculation
    return calculate_ingredient_percentages(all_weights)
