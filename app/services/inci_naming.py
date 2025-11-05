"""
INCI naming service for saponified oils

Provides saponified INCI nomenclature for soap ingredients using reference data
and pattern-based generation as fallback.

Reference: docs/research.md - 37 researched oils with saponified INCI names
"""
import json
import re
from pathlib import Path
from typing import Tuple

from app.models.oil import Oil


def load_reference_data() -> dict:
    """
    Load saponified INCI reference data from JSON file.

    Returns:
        dict: Oil ID -> {saponified_inci_naoh, saponified_inci_koh}

    Raises:
        FileNotFoundError: If reference data file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    reference_file = Path(__file__).parent.parent.parent / "data" / "oils" / "saponified_inci.json"

    if not reference_file.exists():
        raise FileNotFoundError(f"Reference data not found: {reference_file}")

    with open(reference_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def generate_saponified_name(common_name: str, lye_type: str) -> str:
    """
    Generate saponified INCI name using pattern-based logic.

    Pattern:
    - Remove "Oil" or "Butter" suffix
    - Remove trailing vowel before adding "-ate" (Coconut → Coco, Olive → Oliv)
    - Add "-ate" suffix
    - Prefix with "Sodium" (NaOH) or "Potassium" (KOH)

    Examples:
        "Coconut Oil" + "naoh" -> "Sodium Cocoate"
        "Olive Oil" + "koh" -> "Potassium Olivate"
        "Shea Butter" + "naoh" -> "Sodium Sheaate"

    Args:
        common_name: Oil common name (e.g., "Coconut Oil")
        lye_type: "naoh" or "koh"

    Returns:
        str: Generated saponified INCI name

    Raises:
        ValueError: If common_name is empty or lye_type invalid
        TypeError: If common_name is None
    """
    if not common_name:
        raise ValueError("Common name cannot be empty")

    if common_name is None:
        raise TypeError("Common name cannot be None")

    if lye_type not in ("naoh", "koh"):
        raise ValueError(f"Invalid lye_type: {lye_type}. Must be 'naoh' or 'koh'")

    # Prefix selection
    prefix = "Sodium" if lye_type == "naoh" else "Potassium"

    # Clean the common name
    base_name = common_name.strip()

    # Remove common suffixes
    base_name = re.sub(r'\s+(Oil|Butter)$', '', base_name, flags=re.IGNORECASE)

    # INCI nomenclature patterns for saponification
    # Special case: "nut" ending (Coconut -> Coco)
    if base_name.lower().endswith('nut'):
        base_name = base_name[:-3]
    # Standard pattern: remove trailing 'e' (Olive -> Oliv)
    elif base_name.endswith('e') and len(base_name) > 1:
        base_name = base_name[:-1]
    # Other vowel endings: keep as-is (Shea -> Shea)

    # Add -ate suffix
    saponified = f"{base_name}ate"

    # Combine with prefix
    result = f"{prefix} {saponified}"

    return result


def get_saponified_inci_name(oil: Oil, lye_type: str) -> Tuple[str, bool]:
    """
    Get saponified INCI name for an oil with fallback logic.

    Priority:
    1. Use oil.saponified_inci_name if available (from reference data)
       - For NaOH: use as-is
       - For KOH: convert "Sodium" to "Potassium"
    2. Fallback to pattern-based generation

    Args:
        oil: Oil model instance
        lye_type: "naoh" or "koh"

    Returns:
        Tuple[str, bool]: (saponified_inci_name, is_generated)
            - saponified_inci_name: The INCI name
            - is_generated: True if pattern-generated, False if from reference

    Examples:
        oil.saponified_inci_name = "Sodium Cocoate"
        get_saponified_inci_name(oil, "naoh") -> ("Sodium Cocoate", False)
        get_saponified_inci_name(oil, "koh") -> ("Potassium Cocoate", False)

        oil.saponified_inci_name = None
        get_saponified_inci_name(oil, "naoh") -> ("Sodium Exoticate", True)
    """
    # Check if we have reference data
    if oil.saponified_inci_name:
        # Reference data exists
        if lye_type == "naoh":
            # Use as-is (already in Sodium form)
            return (oil.saponified_inci_name, False)
        else:
            # Convert to Potassium form
            koh_name = oil.saponified_inci_name.replace("Sodium", "Potassium")
            return (koh_name, False)

    # No reference data - use pattern generation
    generated_name = generate_saponified_name(oil.common_name, lye_type)
    return (generated_name, True)
