#!/usr/bin/env python3
"""
Import additives from JSON reference data.

Source: working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json
Count: 19 additives with extended fields (category, purpose, how_to_add)

Usage:
    python scripts/import_additives.py [--dry-run] [--verbose]
"""

import argparse
import asyncio
import json
import logging
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.models.additive import Additive

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Source data file
DATA_FILE = (
    Path(__file__).parent.parent
    / "working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json"
)


def parse_usage_rate(usage_rate_str: str) -> tuple[float, float]:
    """
    Parse usage rate string to min/max percentages.

    Examples:
        "1-3%" → (1.0, 3.0)
        "~2%" → (1.0, 3.0)  # default range around midpoint
        "0.5-1%" → (0.5, 1.0)
        "~0.1%" → (0.05, 0.15)
    """
    # Remove whitespace
    rate = usage_rate_str.strip()

    # Range pattern: "1-3%"
    range_match = re.match(r"(\d+\.?\d*)-(\d+\.?\d*)%", rate)
    if range_match:
        min_pct = float(range_match.group(1))
        max_pct = float(range_match.group(2))
        return (min_pct, max_pct)

    # Approximate pattern: "~2%"
    approx_match = re.match(r"~(\d+\.?\d*)%", rate)
    if approx_match:
        midpoint = float(approx_match.group(1))
        # Use ±50% range around midpoint
        min_pct = max(0.1, midpoint * 0.5)
        max_pct = midpoint * 1.5
        return (min_pct, max_pct)

    # Single value: "2%"
    single_match = re.match(r"(\d+\.?\d*)%", rate)
    if single_match:
        value = float(single_match.group(1))
        # Use ±25% range
        min_pct = max(0.1, value * 0.75)
        max_pct = value * 1.25
        return (min_pct, max_pct)

    # Fallback
    logger.warning(f"Could not parse usage rate: {usage_rate_str}")
    return (1.0, 3.0)


def generate_additive_id(name: str) -> str:
    """Generate ID from common name."""
    return name.lower().replace(" ", "_").replace("(", "").replace(")", "")


def map_additive(raw_data: dict) -> dict:
    """
    Map JSON data to Additive model fields.

    Input format:
    {
        "name": "Coffee Grounds",
        "usage_rate_percentage": "~2%",
        "purpose": "Exfoliation & color",
        "how_to_add": "Toss in lye water...",
        "category": "exfoliant",
        "notes": "Adjustable based on...",
        "warnings": "Can be rough on skin"
    }
    """
    # Parse usage rate
    min_pct, max_pct = parse_usage_rate(raw_data["usage_rate_percentage"])

    # Build quality effects (empty for now - no data in source)
    quality_effects = {}

    # Build safety warnings
    safety_warnings = None
    if "warnings" in raw_data or "notes" in raw_data:
        safety_warnings = {}
        if "warnings" in raw_data:
            safety_warnings["warnings"] = raw_data["warnings"]
        if "notes" in raw_data:
            safety_warnings["notes"] = raw_data["notes"]

    return {
        "id": generate_additive_id(raw_data["name"]),
        "common_name": raw_data["name"],
        "inci_name": raw_data["name"],  # No INCI data in source
        "typical_usage_min_percent": min_pct,
        "typical_usage_max_percent": max_pct,
        "quality_effects": quality_effects,
        "confidence_level": "low",  # Not validated by MGA
        "verified_by_mga": False,
        "safety_warnings": safety_warnings,
    }


async def load_existing_ids(db: AsyncSession) -> set[str]:
    """Load existing additive IDs."""
    result = await db.execute(select(Additive.id))
    return {row[0] for row in result.fetchall()}


async def import_additives(dry_run: bool = False, verbose: bool = False) -> None:
    """
    Import additives from JSON file.

    Args:
        dry_run: If True, only validate data without inserting
        verbose: If True, show detailed progress
    """
    # Load source data
    logger.info(f"Loading data from {DATA_FILE}")
    with open(DATA_FILE) as f:
        data = json.load(f)

    additives_raw = data["additives_reference"]
    logger.info(f"Found {len(additives_raw)} additives in source data")

    # Map to model format
    additives_mapped = [map_additive(raw) for raw in additives_raw]

    if verbose:
        logger.info("Sample mapped data:")
        logger.info(json.dumps(additives_mapped[0], indent=2))

    if dry_run:
        logger.info("DRY RUN - No database changes")
        logger.info(f"Would import {len(additives_mapped)} additives")
        return

    # Database import
    async with AsyncSessionLocal() as db:
        # Load existing IDs
        existing_ids = await load_existing_ids(db)
        logger.info(f"Found {len(existing_ids)} existing additives")

        # Filter new additives
        new_additives = [add for add in additives_mapped if add["id"] not in existing_ids]

        if not new_additives:
            logger.info("No new additives to import")
            return

        logger.info(f"Importing {len(new_additives)} new additives")

        # Insert in single transaction
        for add_data in new_additives:
            additive = Additive(**add_data)
            db.add(additive)

            if verbose:
                logger.info(f"  Added: {add_data['common_name']} ({add_data['id']})")

        await db.commit()
        logger.info(f"✓ Successfully imported {len(new_additives)} additives")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Import additives from JSON reference data")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data without inserting to database",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")

    args = parser.parse_args()

    asyncio.run(import_additives(dry_run=args.dry_run, verbose=args.verbose))


if __name__ == "__main__":
    main()
