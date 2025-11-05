"""
Script to seed the database with oils and additives.

Usage:
    python scripts/seed_database.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.oil import Oil
from app.models.additive import Additive
from scripts.seed_data import OIL_SEED_DATA, ADDITIVE_SEED_DATA


async def seed_database():
    """
    Seed database with oils and additives.

    Idempotent: Safe to run multiple times, will only add missing data.
    Uses merge() to handle existing records gracefully.
    """
    print("🌱 Starting database seed...")

    # Create async engine (disable echo for cleaner output)
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Seed oils with duplicate detection
        print(f"\n📦 Processing {len(OIL_SEED_DATA)} oils...")
        oils_added = 0
        oils_skipped = 0

        for oil_data in OIL_SEED_DATA:
            # Check if oil already exists
            result = await session.execute(
                select(Oil).where(Oil.id == oil_data["id"])
            )
            existing_oil = result.scalar_one_or_none()

            if existing_oil:
                print(f"  ⏭ {oil_data['common_name']} (already exists)")
                oils_skipped += 1
            else:
                oil = Oil(**oil_data)
                session.add(oil)
                print(f"  ✓ {oil.common_name}")
                oils_added += 1

        # Seed additives with duplicate detection
        print(f"\n🧪 Processing {len(ADDITIVE_SEED_DATA)} additives...")
        additives_added = 0
        additives_skipped = 0

        for additive_data in ADDITIVE_SEED_DATA:
            # Check if additive already exists
            result = await session.execute(
                select(Additive).where(Additive.id == additive_data["id"])
            )
            existing_additive = result.scalar_one_or_none()

            if existing_additive:
                confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}[additive_data["confidence_level"]]
                print(f"  ⏭ {confidence_emoji} {additive_data['common_name']} (already exists)")
                additives_skipped += 1
            else:
                additive = Additive(**additive_data)
                session.add(additive)
                confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}[additive.confidence_level]
                print(f"  ✓ {confidence_emoji} {additive.common_name} ({additive.confidence_level})")
                additives_added += 1

        # Commit all new records
        if oils_added > 0 or additives_added > 0:
            await session.commit()
            print(f"\n✅ Database seed completed!")
            print(f"   - Oils: {oils_added} added, {oils_skipped} skipped")
            print(f"   - Additives: {additives_added} added, {additives_skipped} skipped")
        else:
            print(f"\n✓ No new data to add")
            print(f"   - All {len(OIL_SEED_DATA)} oils already present")
            print(f"   - All {len(ADDITIVE_SEED_DATA)} additives already present")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
