"""
Pre-import validation CLI for oils data.

Validates JSON file without importing to database,
providing detailed quality reports.

Usage:
    python scripts/validate_oils_data.py <json_path>
"""
import sys
import json
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.import_oils_database import (
    load_oils_from_json,
    validate_all_oils,
)


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_oils_data.py <json_path>")
        sys.exit(1)

    json_path = sys.argv[1]

    print(f"🔍 Validating oils data from: {json_path}\n")

    try:
        # Load JSON
        print("📦 Loading JSON data...")
        oils_data = load_oils_from_json(json_path)
        print(f"   ✓ Loaded {len(oils_data)} oils\n")

        # Validate all oils
        print("🧪 Validating all oils...")
        is_valid, errors = validate_all_oils(oils_data)

        if is_valid:
            print(f"   ✅ All {len(oils_data)} oils passed validation!\n")

            # Generate quality report
            print("📊 Data Quality Report:")
            print(f"   - Total oils: {len(oils_data)}")

            # Count oils with complete fatty acid profiles
            complete_profiles = 0
            for oil_id, oil_data in oils_data.items():
                fatty_acids = oil_data["fatty_acids"]
                fatty_acid_sum = sum(fatty_acids.values())

                # Complete = 95-105% or pine_tar special case
                if oil_id == "pine_tar" or (95 <= fatty_acid_sum <= 105):
                    complete_profiles += 1

            completeness_pct = (complete_profiles / len(oils_data)) * 100
            print(f"   - Complete fatty acid profiles: {complete_profiles}/{len(oils_data)} ({completeness_pct:.2f}%)")

            sys.exit(0)
        else:
            print(f"   ❌ Validation failed with {len(errors)} errors:\n")
            for error in errors:
                print(f"      {error}")
            sys.exit(1)

    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
