#!/usr/bin/env python3
"""
Import natural colorants from JSON reference data.

Source: working/user-feedback/natural-colorants-reference.json
Count: 79 colorants across 9 color families

Color families:
- yellow (14)
- orange (10)
- pink (7)
- red (5)
- blue (5)
- purple (4)
- brown (17)
- green (14)
- black_gray (3)

Usage:
    python scripts/import_colorants.py [--dry-run] [--verbose]
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal

# Import will fail if model doesn't exist - user must create it first
try:
    from app.models.colorant import Colorant
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("Colorant model not found. Create app/models/colorant.py first.")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Source data file
DATA_FILE = Path(__file__).parent.parent / "working/user-feedback/natural-colorants-reference.json"

# Valid color categories
VALID_CATEGORIES = {
    "yellow",
    "orange",
    "pink",
    "red",
    "blue",
    "purple",
    "brown",
    "green",
    "black_gray",
}


def generate_colorant_id(name: str, category: str) -> str:
    """Generate ID from name and category."""
    base = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    return f"{base}_{category}"


def map_colorant(raw_data: dict, category: str) -> dict:
    """
    Map JSON data to Colorant model fields.

    Input format:
    {
        "name": "Turmeric",
        "botanical": "Curcuma longa",
        "usage_rate": "1/32 tsp (yellow) to 1 tsp (orange) PPO",
        "method": "Add to lye or at trace, premix in oil",
        "range": "Pale yellow to burnt orange",
        "warnings": "Does not disperse in water",
        "notes": "Additional notes"
    }
    """
    return {
        "id": generate_colorant_id(raw_data["name"], category),
        "name": raw_data["name"],
        "botanical_name": raw_data.get("botanical", raw_data["name"]),
        "color_category": category,
        "usage_rate": raw_data["usage"],
        "method": raw_data["method"],
        "color_range_description": raw_data["range"],
        "warnings": raw_data.get("warnings"),
        "notes": raw_data.get("notes"),
    }


async def load_existing_ids(db: AsyncSession) -> set[str]:
    """Load existing colorant IDs."""
    result = await db.execute(select(Colorant.id))
    return {row[0] for row in result.fetchall()}


async def import_colorants(dry_run: bool = False, verbose: bool = False) -> None:
    """
    Import colorants from JSON file.

    Args:
        dry_run: If True, only validate data without inserting
        verbose: If True, show detailed progress
    """
    # Load source data
    logger.info(f"Loading data from {DATA_FILE}")
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Process nested structure (color families as keys)
    colorants_mapped = []
    category_counts = {}

    for category, colorants_raw in data.items():
        # Validate category
        if category not in VALID_CATEGORIES:
            logger.warning(f"Unknown category: {category}")
            continue

        # Map colorants in this category
        for raw in colorants_raw:
            colorants_mapped.append(map_colorant(raw, category))

        category_counts[category] = len(colorants_raw)

    logger.info(f"Found {len(colorants_mapped)} colorants across {len(category_counts)} categories")

    if verbose:
        logger.info("Category distribution:")
        for cat, count in sorted(category_counts.items()):
            logger.info(f"  {cat}: {count}")

        logger.info("\nSample mapped data:")
        logger.info(json.dumps(colorants_mapped[0], indent=2))

    if dry_run:
        logger.info("DRY RUN - No database changes")
        logger.info(f"Would import {len(colorants_mapped)} colorants")
        return

    # Database import
    async with AsyncSessionLocal() as db:
        # Load existing IDs
        existing_ids = await load_existing_ids(db)
        logger.info(f"Found {len(existing_ids)} existing colorants")

        # Filter new colorants
        new_colorants = [
            col for col in colorants_mapped if col["id"] not in existing_ids
        ]

        if not new_colorants:
            logger.info("No new colorants to import")
            return

        logger.info(f"Importing {len(new_colorants)} new colorants")

        # Insert in single transaction
        for col_data in new_colorants:
            colorant = Colorant(**col_data)
            db.add(colorant)

            if verbose:
                logger.info(
                    f"  Added: {col_data['common_name']} ({col_data['category']}: {col_data['color_range']})"
                )

        await db.commit()
        logger.info(f"✓ Successfully imported {len(new_colorants)} colorants")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Import natural colorants from JSON reference data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data without inserting to database",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )

    args = parser.parse_args()

    asyncio.run(import_colorants(dry_run=args.dry_run, verbose=args.verbose))


if __name__ == "__main__":
    main()
