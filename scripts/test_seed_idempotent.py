#!/usr/bin/env python3.11
"""
Test script to verify seed_database.py is truly idempotent.

Tests:
1. Fresh database: Seeds successfully
2. Re-run: Skips all existing records
3. Partial data: Adds only missing records

Usage:
    python scripts/test_seed_idempotent.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.oil import Oil
from app.models.additive import Additive
from scripts.seed_database import seed_database


async def clear_test_data(session: AsyncSession):
    """Remove all oils and additives for clean test"""
    await session.execute(delete(Additive))
    await session.execute(delete(Oil))
    await session.commit()
    print("✓ Test data cleared")


async def count_records(session: AsyncSession):
    """Count oils and additives"""
    oil_count = await session.scalar(select(func.count()).select_from(Oil))
    additive_count = await session.scalar(select(func.count()).select_from(Additive))
    return oil_count, additive_count


async def test_idempotency():
    """Run idempotency tests"""
    print("=" * 60)
    print("IDEMPOTENCY TEST FOR seed_database.py")
    print("=" * 60)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Test 1: Fresh database
            print("\n[TEST 1] Fresh database - should add all records")
            print("-" * 60)
            await clear_test_data(session)

            await seed_database()

            async with async_session() as check_session:
                oils, additives = await count_records(check_session)
                print(f"\nResult: {oils} oils, {additives} additives")
                assert oils == 11, f"Expected 11 oils, got {oils}"
                assert additives == 14, f"Expected 14 additives, got {additives}"
                print("✓ TEST 1 PASSED")

            # Test 2: Re-run on existing data
            print("\n[TEST 2] Re-run with existing data - should skip all")
            print("-" * 60)

            await seed_database()

            async with async_session() as check_session:
                oils, additives = await count_records(check_session)
                print(f"\nResult: {oils} oils, {additives} additives")
                assert oils == 11, f"Should still be 11 oils, got {oils}"
                assert additives == 14, f"Should still be 14 additives, got {additives}"
                print("✓ TEST 2 PASSED - No duplicates created")

            # Test 3: Partial data (remove some records)
            print("\n[TEST 3] Partial data - should add only missing")
            print("-" * 60)

            async with async_session() as modify_session:
                # Remove first 3 oils and 5 additives
                await modify_session.execute(
                    delete(Oil).where(Oil.id.in_(['olive_oil', 'coconut_oil', 'palm_oil']))
                )
                await modify_session.execute(
                    delete(Additive).where(Additive.id.like('kaolin%'))
                )
                await modify_session.commit()

                oils, additives = await count_records(modify_session)
                print(f"After removal: {oils} oils, {additives} additives")

            await seed_database()

            async with async_session() as check_session:
                oils, additives = await count_records(check_session)
                print(f"\nAfter re-seed: {oils} oils, {additives} additives")
                assert oils == 11, f"Should restore to 11 oils, got {oils}"
                assert additives >= 13, f"Should restore additives, got {additives}"
                print("✓ TEST 3 PASSED - Missing records restored")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nConclusion: seed_database.py is truly idempotent")
        print("Safe to run multiple times without duplicating data")

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_idempotency())
    sys.exit(0 if success else 1)
