#!/usr/bin/env python3
"""
Import essential oils from JSON reference data.

Source: working/user-feedback/essential-oils-usage-reference.json
Count: 39 essential oils with scent profiles, blending, and usage rates

Usage:
    python scripts/import_essential_oils.py [--dry-run] [--verbose]
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
    from app.models.essential_oil import EssentialOil
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("EssentialOil model not found. Create app/models/essential_oil.py first.")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Source data file
DATA_FILE = (
    Path(__file__).parent.parent / "working/user-feedback/essential-oils-usage-reference.json"
)


def generate_eo_id(name: str) -> str:
    """Generate ID from common name."""
    return name.lower().replace(" ", "_").replace("(", "").replace(")", "")


def map_essential_oil(raw_data: dict) -> dict:
    """
    Map JSON data to EssentialOil model fields.

    Input format:
    {
        "name": "Lavender (English)",
        "botanical_name": "Lavandula augustifolia",
        "max_usage_rate_pct": 3.0,
        "scent_profile": "Sweet, herbaceous, and floral",
        "usage_notes": "Long used in perfume industry...",
        "blends_with": ["Bergamot", "Chamomile", "Geranium"],
        "note": "Middle",
        "category": "floral",
        "warnings": "Can fade quickly",
        "color_effect": "Slightly yellow"
    }
    """
    return {
        "id": generate_eo_id(raw_data["name"]),
        "common_name": raw_data["name"],
        "botanical_name": raw_data["botanical_name"],
        "max_usage_rate_pct": raw_data["max_usage_rate_pct"],
        "scent_profile": raw_data["scent_profile"],
        "usage_notes": raw_data.get("usage_notes", ""),
        "blends_with": raw_data.get("blends_with", []),  # JSONB array
        "note": raw_data["note"],
        "category": raw_data["category"],
        "warnings": raw_data.get("warnings"),
        "color_effect": raw_data.get("color_effect"),
    }


async def load_existing_ids(db: AsyncSession) -> set[str]:
    """Load existing essential oil IDs."""
    result = await db.execute(select(EssentialOil.id))
    return {row[0] for row in result.fetchall()}


async def import_essential_oils(dry_run: bool = False, verbose: bool = False) -> None:
    """
    Import essential oils from JSON file.

    Args:
        dry_run: If True, only validate data without inserting
        verbose: If True, show detailed progress
    """
    # Load source data
    logger.info(f"Loading data from {DATA_FILE}")
    with open(DATA_FILE) as f:
        data = json.load(f)

    eos_raw = data["essential_oils_reference"]
    logger.info(f"Found {len(eos_raw)} essential oils in source data")

    # Validate usage rates
    for eo in eos_raw:
        rate = eo["max_usage_rate_pct"]
        if not (0.025 <= rate <= 3.0):
            logger.warning(f"Unusual usage rate for {eo['name']}: {rate}% (expected 0.025-3.0%)")

    # Map to model format
    eos_mapped = [map_essential_oil(raw) for raw in eos_raw]

    if verbose:
        logger.info("Sample mapped data:")
        logger.info(json.dumps(eos_mapped[0], indent=2))

    if dry_run:
        logger.info("DRY RUN - No database changes")
        logger.info(f"Would import {len(eos_mapped)} essential oils")

        # Show category distribution
        categories = {}
        for eo in eos_mapped:
            cat = eo["category"]
            categories[cat] = categories.get(cat, 0) + 1
        logger.info("Category distribution:")
        for cat, count in sorted(categories.items()):
            logger.info(f"  {cat}: {count}")

        return

    # Database import
    async with AsyncSessionLocal() as db:
        # Load existing IDs
        existing_ids = await load_existing_ids(db)
        logger.info(f"Found {len(existing_ids)} existing essential oils")

        # Filter new EOs
        new_eos = [eo for eo in eos_mapped if eo["id"] not in existing_ids]

        if not new_eos:
            logger.info("No new essential oils to import")
            return

        logger.info(f"Importing {len(new_eos)} new essential oils")

        # Insert in single transaction
        for eo_data in new_eos:
            eo = EssentialOil(**eo_data)
            db.add(eo)

            if verbose:
                logger.info(
                    f"  Added: {eo_data['common_name']} ({eo_data['category']}, {eo_data['max_usage_rate_pct']}%)"
                )

        await db.commit()
        logger.info(f"✓ Successfully imported {len(new_eos)} essential oils")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Import essential oils from JSON reference data")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data without inserting to database",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")

    args = parser.parse_args()

    asyncio.run(import_essential_oils(dry_run=args.dry_run, verbose=args.verbose))


if __name__ == "__main__":
    main()
