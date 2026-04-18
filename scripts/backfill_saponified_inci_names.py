#!/usr/bin/env python3
"""
Backfill saponified_inci_name from reference data

Usage: python scripts/backfill_saponified_inci_names.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.models.oil import Oil


async def load_reference_data() -> dict:
    """Load saponified INCI reference data from JSON file"""
    reference_file = project_root / "app" / "data" / "saponified-inci-terms.json"

    with open(reference_file) as f:
        data = json.load(f)

    # Build lookup dictionary: oil_id -> saponified_inci_naoh
    lookup = {}
    for oil_entry in data["oils"]:
        lookup[oil_entry["oil_id"]] = oil_entry["saponified_inci_naoh"]

    return lookup


async def backfill_oils(session: AsyncSession, reference_lookup: dict) -> dict:
    """
    Backfill saponified_inci_name for oils in reference data

    Returns:
        dict: Statistics (updated_count, missing_count, total_count)
    """
    # Get all oils
    result = await session.execute(select(Oil))
    oils = result.scalars().all()

    updated_count = 0
    missing_count = 0

    for oil in oils:
        if oil.id in reference_lookup:
            # Update with reference data
            oil.saponified_inci_name = reference_lookup[oil.id]
            updated_count += 1
        else:
            # Log missing oils for manual review
            print(f"WARNING: No reference data for oil: {oil.id} ({oil.common_name})")
            missing_count += 1

    await session.commit()

    return {
        "updated_count": updated_count,
        "missing_count": missing_count,
        "total_count": len(oils),
    }


async def main():
    """Execute backfill operation"""
    print("=" * 60)
    print("Saponified INCI Names Backfill Script")
    print("=" * 60)

    print("\nLoading reference data...")
    reference_lookup = await load_reference_data()
    print(f"✓ Loaded {len(reference_lookup)} oil entries from reference data")

    print("\nBackfilling saponified_inci_name values...")
    async with AsyncSessionLocal() as session:
        stats = await backfill_oils(session, reference_lookup)

    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"Total oils in database: {stats['total_count']}")
    print(f"✓ Updated with reference data: {stats['updated_count']}")
    print(f"⚠ Missing reference data: {stats['missing_count']}")

    if stats["missing_count"] > 0:
        print("\n⚠ ACTION REQUIRED:")
        print("  Review oils without reference data above and either:")
        print("  1. Add entries to app/data/saponified-inci-terms.json")
        print("  2. Allow pattern-based generation at runtime")
    else:
        print("\n✓ All oils have saponified INCI names!")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
