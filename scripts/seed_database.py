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

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.oil import Oil
from app.models.additive import Additive
from scripts.seed_data import OIL_SEED_DATA, ADDITIVE_SEED_DATA


async def seed_database():
    """Seed database with oils and additives"""
    print("🌱 Starting database seed...")

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Seed oils
        print(f"\n📦 Seeding {len(OIL_SEED_DATA)} oils...")
        for oil_data in OIL_SEED_DATA:
            oil = Oil(**oil_data)
            session.add(oil)
            print(f"  ✓ {oil.common_name}")

        # Seed additives
        print(f"\n🧪 Seeding {len(ADDITIVE_SEED_DATA)} additives...")
        for additive_data in ADDITIVE_SEED_DATA:
            additive = Additive(**additive_data)
            session.add(additive)
            confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}[additive.confidence_level]
            print(f"  {confidence_emoji} {additive.common_name} ({additive.confidence_level})")

        # Commit all
        await session.commit()
        print(f"\n✅ Database seeded successfully!")
        print(f"   - {len(OIL_SEED_DATA)} oils")
        print(f"   - {len(ADDITIVE_SEED_DATA)} additives")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
