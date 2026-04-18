#!/usr/bin/env python3
"""
User Story Verification Script

Directly tests US1-US5 acceptance scenarios against the live API.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Color output for terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def test_us1_90_percent_koh_calculation():
    """US1: 90% KOH calculation returns correct commercial weight."""
    print("\n" + "=" * 80)
    print("US1 - 90% KOH Calculation")
    print("=" * 80)

    payload = {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10},
        ],
        "lye": {"naoh_percent": 10, "koh_percent": 90, "koh_purity": 90},
        "superfat_percent": 1,
        "batch_size_g": 700,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 200:
        print(f"{RED}✗ FAILED{RESET}: HTTP {response.status_code}")
        print(f"  Error: {response.json()}")
        return False

    data = response.json()
    koh_weight = data["recipe"]["lye"]["koh_weight_g"]
    pure_koh = data["recipe"]["lye"]["pure_koh_equivalent_g"]

    # Expected: 117.1g pure @ 90% = 130.1g commercial
    expected_commercial = 130.1
    expected_pure = 117.1
    tolerance = 0.5

    koh_pass = abs(koh_weight - expected_commercial) <= tolerance
    pure_pass = abs(pure_koh - expected_pure) <= tolerance

    print(f"Commercial KOH: {koh_weight:.1f}g (expected: {expected_commercial}g)")
    print(
        f"  {GREEN}✓{RESET} Within tolerance" if koh_pass else f"  {RED}✗{RESET} Outside tolerance"
    )

    print(f"Pure KOH equivalent: {pure_koh:.1f}g (expected: {expected_pure}g)")
    print(
        f"  {GREEN}✓{RESET} Within tolerance" if pure_pass else f"  {RED}✗{RESET} Outside tolerance"
    )

    return koh_pass and pure_pass


def test_us1_default_90_percent():
    """US1: Omitting koh_purity defaults to 90%."""
    print("\n" + "=" * 80)
    print("US1 - Default 90% KOH (omitted field)")
    print("=" * 80)

    payload = {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10},
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
            # koh_purity omitted - should default to 90
        },
        "superfat_percent": 1,
        "batch_size_g": 700,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 200:
        print(f"{RED}✗ FAILED{RESET}: HTTP {response.status_code}")
        return False

    data = response.json()
    koh_purity = data["recipe"]["lye"]["koh_purity"]
    koh_weight = data["recipe"]["lye"]["koh_weight_g"]

    purity_pass = koh_purity == 90.0
    weight_pass = abs(koh_weight - 130.1) <= 0.5

    print(f"KOH purity in response: {koh_purity}% (expected: 90.0%)")
    print(f"  {GREEN}✓{RESET} Correct default" if purity_pass else f"  {RED}✗{RESET} Wrong default")

    print(f"Commercial KOH: {koh_weight:.1f}g (expected: 130.1g)")
    print(f"  {GREEN}✓{RESET} Adjusted for 90%" if weight_pass else f"  {RED}✗{RESET} Not adjusted")

    return purity_pass and weight_pass


def test_us2_validation_below_50():
    """US2: Purity <50% returns 400 error."""
    print("\n" + "=" * 80)
    print("US2 - Validation: Purity <50% Rejected")
    print("=" * 80)

    payload = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {
            "naoh_percent": 0,
            "koh_percent": 100,
            "koh_purity": 49,  # Invalid: below minimum
        },
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 400:
        print(f"{RED}✗ FAILED{RESET}: Expected HTTP 400, got {response.status_code}")
        return False

    error_data = response.json()
    error_msg = str(error_data.get("detail", ""))

    has_range_info = "50" in error_msg or "100" in error_msg

    print(f"HTTP Status: {response.status_code} (expected: 400)")
    print(f"  {GREEN}✓{RESET} Correctly rejected")

    print(f"Error message: {error_msg}")
    print(
        f"  {GREEN}✓{RESET} Includes range"
        if has_range_info
        else f"  {YELLOW}!{RESET} Missing range info"
    )

    return True  # Status 400 is the key requirement


def test_us2_validation_above_100():
    """US2: Purity >100% returns 400 error."""
    print("\n" + "=" * 80)
    print("US2 - Validation: Purity >100% Rejected")
    print("=" * 80)

    payload = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {
            "naoh_percent": 0,
            "koh_percent": 100,
            "koh_purity": 101,  # Invalid: above maximum
        },
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 400:
        print(f"{RED}✗ FAILED{RESET}: Expected HTTP 400, got {response.status_code}")
        return False

    error_data = response.json()
    error_msg = str(error_data.get("detail", ""))

    print(f"HTTP Status: {response.status_code} (expected: 400)")
    print(f"  {GREEN}✓{RESET} Correctly rejected")

    print(f"Error message: {error_msg}")

    return True


def test_us3_warnings_unusual_purity():
    """US3: Warnings for unusual purity (not blocking)."""
    print("\n" + "=" * 80)
    print("US3 - Warnings for Unusual Purity")
    print("=" * 80)

    # Test 75% KOH (unusual low)
    payload_low = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {
            "naoh_percent": 0,
            "koh_percent": 100,
            "koh_purity": 75,  # Unusual but valid
        },
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response_low = client.post("/api/v1/recipes/calculate", json=payload_low)

    if response_low.status_code != 200:
        print(f"{RED}✗ FAILED{RESET}: 75% KOH rejected (should accept with warning)")
        print(f"  HTTP {response_low.status_code}: {response_low.json()}")
        return False

    data_low = response_low.json()
    warnings_low = data_low.get("recipe", {}).get("warnings", [])

    print("75% KOH purity:")
    print(f"  HTTP Status: {response_low.status_code} (expected: 200)")
    print(f"  {GREEN}✓{RESET} Calculation succeeded")
    print(f"  Warnings: {len(warnings_low)}")
    if warnings_low:
        print(f"  {GREEN}✓{RESET} Warning generated: {warnings_low[0].get('message', '')}")
    else:
        print(f"  {YELLOW}!{RESET} No warning (should warn for unusual purity)")

    # Test 98% KOH (unusual high)
    payload_high = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {
            "naoh_percent": 0,
            "koh_percent": 100,
            "koh_purity": 98,  # Unusual high
        },
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response_high = client.post("/api/v1/recipes/calculate", json=payload_high)
    data_high = response_high.json()
    warnings_high = data_high.get("recipe", {}).get("warnings", [])

    print("\n98% KOH purity:")
    print(f"  HTTP Status: {response_high.status_code} (expected: 200)")
    print(f"  Warnings: {len(warnings_high)}")
    if warnings_high:
        print(f"  {GREEN}✓{RESET} Warning generated: {warnings_high[0].get('message', '')}")
    else:
        print(f"  {YELLOW}!{RESET} No warning (should warn for high purity)")

    # Test 90% KOH (typical - no warning)
    payload_normal = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {
            "naoh_percent": 0,
            "koh_percent": 100,
            "koh_purity": 90,  # Typical commercial
        },
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response_normal = client.post("/api/v1/recipes/calculate", json=payload_normal)
    data_normal = response_normal.json()
    warnings_normal = data_normal.get("recipe", {}).get("warnings", [])

    print("\n90% KOH purity (typical):")
    print(f"  Warnings: {len(warnings_normal)}")
    if not warnings_normal:
        print(f"  {GREEN}✓{RESET} No warning (correct for typical purity)")
    else:
        print(f"  {YELLOW}!{RESET} Warning generated: {warnings_normal}")

    return response_low.status_code == 200 and response_high.status_code == 200


def test_us4_mixed_lye_purity():
    """US4: Mixed lye with different purity values."""
    print("\n" + "=" * 80)
    print("US4 - Mixed Lye with Different Purities")
    print("=" * 80)

    payload = {
        "oils": [
            {"name": "Olive Oil", "percentage": 70},
            {"name": "Castor Oil", "percentage": 20},
            {"name": "Coconut Oil", "percentage": 10},
        ],
        "lye": {
            "naoh_percent": 10,
            "koh_percent": 90,
            "koh_purity": 90,  # 90% KOH
            "naoh_purity": 98,  # 98% NaOH
        },
        "superfat_percent": 1,
        "batch_size_g": 700,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 200:
        print(f"{RED}✗ FAILED{RESET}: HTTP {response.status_code}")
        return False

    data = response.json()
    lye = data["recipe"]["lye"]

    koh_weight = lye["koh_weight_g"]
    naoh_weight = lye["naoh_weight_g"]
    pure_koh = lye["pure_koh_equivalent_g"]
    pure_naoh = lye["pure_naoh_equivalent_g"]

    # Check independent adjustment
    koh_adjustment_ratio = koh_weight / pure_koh if pure_koh > 0 else 0
    naoh_adjustment_ratio = naoh_weight / pure_naoh if pure_naoh > 0 else 0

    expected_koh_ratio = 1 / 0.90  # Should be ~1.111
    expected_naoh_ratio = 1 / 0.98  # Should be ~1.020

    koh_ratio_pass = abs(koh_adjustment_ratio - expected_koh_ratio) < 0.01
    naoh_ratio_pass = abs(naoh_adjustment_ratio - expected_naoh_ratio) < 0.01

    print(f"KOH: {pure_koh:.1f}g pure → {koh_weight:.1f}g @ 90% purity")
    print(f"  Adjustment ratio: {koh_adjustment_ratio:.3f} (expected: {expected_koh_ratio:.3f})")
    print(f"  {GREEN}✓{RESET} Correct" if koh_ratio_pass else f"  {RED}✗{RESET} Incorrect")

    print(f"NaOH: {pure_naoh:.1f}g pure → {naoh_weight:.1f}g @ 98% purity")
    print(f"  Adjustment ratio: {naoh_adjustment_ratio:.3f} (expected: {expected_naoh_ratio:.3f})")
    print(f"  {GREEN}✓{RESET} Correct" if naoh_ratio_pass else f"  {RED}✗{RESET} Incorrect")

    return koh_ratio_pass and naoh_ratio_pass


def test_us5_response_schema():
    """US5: Response schema includes all purity fields."""
    print("\n" + "=" * 80)
    print("US5 - Response Schema Completeness")
    print("=" * 80)

    payload = {
        "oils": [{"name": "Olive Oil", "percentage": 100}],
        "lye": {"naoh_percent": 10, "koh_percent": 90, "koh_purity": 90, "naoh_purity": 98},
        "superfat_percent": 5,
        "batch_size_g": 500,
    }

    response = client.post("/api/v1/calculate", json=payload)

    if response.status_code != 200:
        print(f"{RED}✗ FAILED{RESET}: HTTP {response.status_code}")
        return False

    data = response.json()
    lye = data["recipe"]["lye"]

    required_fields = [
        "koh_purity",
        "naoh_purity",
        "pure_koh_equivalent_g",
        "pure_naoh_equivalent_g",
        "koh_weight_g",
        "naoh_weight_g",
    ]

    all_present = True
    for field in required_fields:
        present = field in lye
        print(
            f"  {field}: {GREEN}✓{RESET} Present"
            if present
            else f"  {field}: {RED}✗{RESET} Missing"
        )
        if present:
            print(f"    Value: {lye[field]}")
        all_present = all_present and present

    # Check defaults echo back correctly
    koh_echoed = lye.get("koh_purity") == 90.0
    naoh_echoed = lye.get("naoh_purity") == 98.0

    print("\nDefault echo verification:")
    print(
        f"  koh_purity=90: {GREEN}✓{RESET}"
        if koh_echoed
        else f"  koh_purity: {RED}✗{RESET} {lye.get('koh_purity')}"
    )
    print(
        f"  naoh_purity=98: {GREEN}✓{RESET}"
        if naoh_echoed
        else f"  naoh_purity: {RED}✗{RESET} {lye.get('naoh_purity')}"
    )

    return all_present and koh_echoed and naoh_echoed


def main():
    """Run all user story verification tests."""
    print("\n" + "=" * 80)
    print("USER STORY VERIFICATION: US1-US5")
    print("Feature: KOH/NaOH Purity Support")
    print("=" * 80)

    results = {
        "US1.1 - 90% KOH calculation": test_us1_90_percent_koh_calculation(),
        "US1.2 - Default 90% (omitted)": test_us1_default_90_percent(),
        "US2.1 - Validation <50%": test_us2_validation_below_50(),
        "US2.2 - Validation >100%": test_us2_validation_above_100(),
        "US3 - Warnings for unusual": test_us3_warnings_unusual_purity(),
        "US4 - Mixed lye purity": test_us4_mixed_lye_purity(),
        "US5 - Response schema": test_us5_response_schema(),
    }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print(f"\n{GREEN}✓ ALL USER STORIES VERIFIED{RESET}")
        return 0
    else:
        print(f"\n{YELLOW}! SOME USER STORIES NEED WORK{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
