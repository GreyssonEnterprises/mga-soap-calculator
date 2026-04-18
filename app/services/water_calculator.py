"""
Water Calculation Service

Three methods per spec Section 5.2:
1. Water as % of total oil weight
2. Lye concentration (% of water+lye solution)
3. Water:lye ratio
"""


def calculate_water_from_oil_percent(total_oil_weight_g: float, water_percent: float) -> float:
    """
    Method 1: Water as percentage of oils

    Common values: 38%, 33%, 28%
    Formula: water = total_oil_weight × (water_percent / 100)

    TDD Evidence: 1000g oils @ 38% = 380g water
    """
    if not 0 < water_percent <= 100:
        raise ValueError(f"Water percent must be 0-100%, got {water_percent}")

    water_g = total_oil_weight_g * (water_percent / 100)
    return round(water_g, 1)


def calculate_water_from_lye_concentration(
    total_lye_weight_g: float, lye_concentration_percent: float
) -> float:
    """
    Method 2: Lye concentration (lye as % of total lye solution)

    Common values: 25%, 33%, 40%
    Formula: water = (lye / concentration) - lye

    TDD Evidence: 142.6g lye @ 33% concentration = 289.5g water
    """
    if not 0 < lye_concentration_percent <= 50:
        raise ValueError(f"Lye concentration must be 0-50%, got {lye_concentration_percent}")

    # Total solution = lye / concentration
    # Water = total solution - lye
    total_solution_g = total_lye_weight_g / (lye_concentration_percent / 100)
    water_g = total_solution_g - total_lye_weight_g
    return round(water_g, 1)


def calculate_water_from_lye_ratio(total_lye_weight_g: float, water_lye_ratio: float) -> float:
    """
    Method 3: Water:lye ratio

    Common values: 1.5:1, 2:1, 2.5:1
    Formula: water = total_lye_weight × water_lye_ratio

    TDD Evidence: 142.6g lye @ 2:1 ratio = 285.2g water
    """
    if not 0.5 <= water_lye_ratio <= 4.0:
        raise ValueError(f"Water:lye ratio must be 0.5-4.0, got {water_lye_ratio}")

    water_g = total_lye_weight_g * water_lye_ratio
    return round(water_g, 1)
