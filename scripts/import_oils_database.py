"""
Import 147 comprehensive oils from JSON to PostgreSQL database.

This script extends the seed_database.py pattern for idempotent operation,
validating data against scientific ranges before import.

Usage:
    python scripts/import_oils_database.py [--dry-run] [--verbose]

Features:
    - Idempotent: Safe to run multiple times
    - Validated: Checks SAP values, fatty acid sums, quality metrics
    - Transactional: All-or-nothing ACID compliance
    - Progress reporting: Shows import status

Exit Codes:
    0: Success
    1: Validation error or JSON parse error
    2: Database error
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Tuple, List

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.oil import Oil


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_sap_naoh_range(sap_value: float) -> Tuple[bool, str]:
    """
    Validate SAP NaOH value is within range [0.000, 0.350].

    Note: Extended to 0.000 for waxes and special materials (pine tar, candelilla, etc.)
    Extended upper limit to 0.350 for fractionated oils (MCT oils).

    Args:
        sap_value: SAP value for NaOH in g/g

    Returns:
        (is_valid, error_message)
    """
    if 0.000 <= sap_value <= 0.350:
        return True, ""
    return False, f"SAP NaOH {sap_value:.3f} outside valid range [0.000, 0.350]"


def validate_sap_koh_range(sap_value: float) -> Tuple[bool, str]:
    """
    Validate SAP KOH value is within range [0.000, 0.490].

    Note: Extended to 0.000 for waxes and special materials.
    Extended upper limit for fractionated oils.

    Args:
        sap_value: SAP value for KOH in g/g

    Returns:
        (is_valid, error_message)
    """
    if 0.000 <= sap_value <= 0.490:
        return True, ""
    return False, f"SAP KOH {sap_value:.3f} outside valid range [0.000, 0.490]"


def validate_fatty_acids_sum(fatty_acids: Dict[str, float], oil_id: str) -> Tuple[bool, str]:
    """
    Validate fatty acids sum to reasonable range (allowing incomplete profiles).

    Special cases:
    - pine_tar: Resin-based, not fatty acid based
    - Waxes (candelilla, carnauba, jojoba, beeswax): Composed of wax esters, not triglycerides
    - Exotic oils: May have incomplete profiles (30-105% tolerance)

    Args:
        fatty_acids: Dictionary of 8 fatty acid percentages
        oil_id: Oil identifier for special case detection

    Returns:
        (is_valid, error_message)
    """
    # Special materials without typical fatty acid profiles
    special_materials = ["pine_tar", "candelilla_wax", "carnauba_wax", "jojoba_liquid_wax_ester", "beeswax"]
    if oil_id in special_materials:
        return True, ""

    # Calculate sum of all fatty acids
    fatty_acid_sum = sum(fatty_acids.values())

    # Allow 30-105% range (accounting for minor fatty acids, waxes, and measurement variations)
    # Some exotic oils have incomplete profiles
    if 30.0 <= fatty_acid_sum <= 105.0:
        return True, ""

    return False, f"Fatty acids sum {fatty_acid_sum:.1f}% outside valid range [30, 105]"


def validate_quality_metrics_range(quality_metrics: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validate quality metrics are in range [0, 100].

    Note: Extended upper limit to 100 for pure fatty acids (e.g., lauric acid).

    Args:
        quality_metrics: Dictionary of 7 quality metrics

    Returns:
        (is_valid, error_message)
    """
    for metric_name, metric_value in quality_metrics.items():
        if not (0 <= metric_value <= 100):
            return False, f"Quality metric '{metric_name}' value {metric_value} outside valid range [0, 100]"

    return True, ""


def validate_oil_data(oil_id: str, oil_data: Dict) -> Tuple[bool, str]:
    """
    Validate complete oil data against all rules.

    Checks:
    - SAP NaOH range [0.000, 0.350]
    - SAP KOH range [0.000, 0.490]
    - Fatty acids sum 30-105% (or any for special materials)
    - Quality metrics range [0, 100]

    Args:
        oil_id: Oil identifier
        oil_data: Complete oil data dictionary

    Returns:
        (is_valid, error_message)
    """
    # Validate SAP NaOH
    valid, error = validate_sap_naoh_range(oil_data["sap_value_naoh"])
    if not valid:
        return False, f"{oil_id}: {error}"

    # Validate SAP KOH
    valid, error = validate_sap_koh_range(oil_data["sap_value_koh"])
    if not valid:
        return False, f"{oil_id}: {error}"

    # Validate fatty acids sum
    valid, error = validate_fatty_acids_sum(oil_data["fatty_acids"], oil_id)
    if not valid:
        return False, f"{oil_id}: {error}"

    # Validate quality metrics
    valid, error = validate_quality_metrics_range(oil_data["quality_contributions"])
    if not valid:
        return False, f"{oil_id}: {error}"

    return True, ""


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_oils_from_json(json_path: str) -> Dict[str, dict]:
    """
    Load oils data from JSON file.

    Args:
        json_path: Path to JSON file containing oils data

    Returns:
        Dictionary mapping oil_id to oil data

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # The JSON structure is a dictionary with oil_id as keys
    return data


def validate_all_oils(oils_data: Dict[str, dict]) -> Tuple[bool, List[str]]:
    """
    Validate all oils before import (fail-fast).

    Args:
        oils_data: Dictionary of all oils to validate

    Returns:
        (all_valid, list_of_error_messages)
    """
    errors = []

    for oil_id, oil_data in oils_data.items():
        # Ensure id field matches key
        if "id" not in oil_data:
            oil_data["id"] = oil_id
        elif oil_data["id"] != oil_id:
            errors.append(f"{oil_id}: ID mismatch - key='{oil_id}', data='{oil_data['id']}'")
            continue

        # Validate oil data
        valid, error = validate_oil_data(oil_id, oil_data)
        if not valid:
            errors.append(error)

    return len(errors) == 0, errors


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

async def is_oil_exists(session: AsyncSession, oil_id: str) -> bool:
    """
    Check if oil already exists in database.

    Args:
        session: Database session
        oil_id: Oil identifier to check

    Returns:
        True if oil exists, False otherwise
    """
    result = await session.execute(
        select(Oil).where(Oil.id == oil_id)
    )
    return result.scalar_one_or_none() is not None


async def import_oils_database(
    json_path: str = "working/user-feedback/oils-db-additions/complete-oils-database.json",
    dry_run: bool = False,
    verbose: bool = False
) -> Tuple[int, int]:
    """
    Import oils from JSON to database with validation and idempotency.

    Process:
    1. Load JSON data
    2. Validate all oils (fail-fast)
    3. Start database transaction
    4. For each oil: check existence, skip if exists, insert if new
    5. Commit transaction
    6. Report summary

    Args:
        json_path: Path to JSON file with oils data
        dry_run: If True, validate only without database operations
        verbose: If True, show detailed progress

    Returns:
        (oils_added, oils_skipped)

    Raises:
        SystemExit: On validation or database errors
    """
    # Step 1: Load JSON data
    if verbose:
        print(f"Loading oils from {json_path}...")

    try:
        oils_data = load_oils_from_json(json_path)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"✓ Loaded {len(oils_data)} oils")

    # Step 2: Validate all oils (fail-fast)
    if verbose:
        print("Validating oil data...")

    all_valid, errors = validate_all_oils(oils_data)
    if not all_valid:
        print(f"❌ Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"✓ All {len(oils_data)} oils passed validation")

    # If dry-run, stop here
    if dry_run:
        print(f"\n✅ Dry-run validation successful!")
        print(f"   - {len(oils_data)} oils ready for import")
        return 0, 0

    # Step 3-5: Database operations
    if verbose:
        print("Connecting to database...")

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    oils_added = 0
    oils_skipped = 0

    try:
        async with async_session() as session:
            async with session.begin():
                if verbose:
                    print("Processing oils...")

                for oil_id, oil_data in oils_data.items():
                    # Check if oil already exists
                    if await is_oil_exists(session, oil_id):
                        oils_skipped += 1
                        if verbose:
                            print(f"  ⊘ Skipping {oil_id} (already exists)")
                        continue

                    # Create new Oil instance
                    oil = Oil(
                        id=oil_data["id"],
                        common_name=oil_data["common_name"],
                        inci_name=oil_data["inci_name"],
                        sap_value_naoh=oil_data["sap_value_naoh"],
                        sap_value_koh=oil_data["sap_value_koh"],
                        iodine_value=oil_data["iodine_value"],
                        ins_value=oil_data["ins_value"],
                        fatty_acids=oil_data["fatty_acids"],
                        quality_contributions=oil_data["quality_contributions"]
                    )

                    session.add(oil)
                    oils_added += 1

                    if verbose:
                        print(f"  + Adding {oil_id}")

                # Commit transaction
                if verbose:
                    print("Committing transaction...")

        if verbose:
            print("✓ Transaction committed successfully")

    except Exception as e:
        print(f"❌ Database error: {e}", file=sys.stderr)
        sys.exit(2)

    finally:
        await engine.dispose()

    return oils_added, oils_skipped


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for oil import script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import 147 comprehensive oils to database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data without importing to database"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress information"
    )
    parser.add_argument(
        "--json-path",
        default="working/user-feedback/oils-db-additions/complete-oils-database.json",
        help="Path to JSON file with oils data"
    )

    args = parser.parse_args()

    try:
        added, skipped = asyncio.run(
            import_oils_database(
                json_path=args.json_path,
                dry_run=args.dry_run,
                verbose=args.verbose
            )
        )

        print(f"\n✅ Import completed successfully!")
        print(f"   - Oils added: {added}")
        print(f"   - Oils skipped: {skipped}")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Import failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
