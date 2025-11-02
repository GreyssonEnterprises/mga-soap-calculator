# Python Pro - Phase 2 Mixed Lye Formula Fix

**Timestamp:** 2025-11-01
**Agent:** python-pro
**Task:** Fix lye calculator to use Formula A (industry-standard weight percentages)
**Requestor:** Bob / Domain Expert (Shale)

## Problem Statement

The lye calculator was using **Formula B** (separate SAP calculations), but the professional soap-making industry uses **Formula A** (weighted-average SAP with weight splitting).

### Industry Clarification

**Domain Expert (Shale from MGA Automotive):** When we say "70% NaOH / 30% KOH", we ALWAYS mean **by weight**:
- 70% of the total lye WEIGHT is NaOH
- 30% of the total lye WEIGHT is KOH
- NOT molecular equivalents
- NOT separate SAP calculations

This is the convention used in actual MGA soap recipes.

## Changes Made

### 1. Updated `app/services/lye_calculator.py`

**Changed from Formula B (WRONG):**
```python
# Calculate each lye separately using their SAP values
total_sap_naoh = sum(oil.weight_g * oil.sap_naoh for oil in oils)
total_sap_koh = sum(oil.weight_g * oil.sap_koh for oil in oils)
naoh_needed = total_sap_naoh * superfat_multiplier * (naoh_percent / 100)
koh_needed = total_sap_koh * superfat_multiplier * (koh_percent / 100)
```

**To Formula A (CORRECT):**
```python
# Calculate weighted-average SAP for the lye blend
total_oil_weight = sum(oil.weight_g for oil in oils)
weighted_sap = 0.0

for oil in oils:
    # Blend this oil's SAP values by the lye percentages
    oil_blended_sap = (
        oil.sap_naoh * (naoh_percent / 100) +
        oil.sap_koh * (koh_percent / 100)
    )
    # Weight by this oil's contribution to total
    oil_weight_ratio = oil.weight_g / total_oil_weight
    weighted_sap += oil_blended_sap * oil_weight_ratio

# Calculate total lye needed using weighted SAP
total_lye_needed = total_oil_weight * weighted_sap * superfat_multiplier

# Split by weight percentages (industry convention)
naoh_needed = total_lye_needed * (naoh_percent / 100)
koh_needed = total_lye_needed * (koh_percent / 100)
```

**Documentation Added:**
- Clear comments explaining weight percentage convention
- Formula A methodology documented in docstring
- Industry practice clarification

### 2. Updated `tests/unit/test_lye_calculator.py`

**Updated Test Expectations:**
- `test_70_30_naoh_koh_split`: Now expects 99.9g NaOH, 42.8g KOH (Formula A)
- `test_50_50_naoh_koh_split`: Now expects 84.0g NaOH, 84.0g KOH (Formula A)
- Reduced tolerance to **0.1g** (was 0.2g) for higher accuracy

**Added New Test:**
```python
def test_mixed_lye_weight_percentage_convention():
    """
    Industry convention: 70% NaOH / 30% KOH means BY WEIGHT.

    Validates:
    - Weight splitting is correct
    - Matches professional soap-maker specifications
    - NOT molecular equivalents
    """
```

This test explicitly validates the weight percentage convention with verification that the resulting lye amounts are in the correct ratio.

## Formula A vs Formula B Difference

### Example: 1000g oil, SAP_NaOH=0.134, SAP_KOH=0.188, 5% SF, 70/30 split

**Formula B (separate SAP - WRONG for industry):**
- NaOH = 1000 × 0.134 × 0.95 × 0.70 = 89.2g
- KOH = 1000 × 0.188 × 0.95 × 0.30 = 53.6g
- Total = 142.8g

**Formula A (weighted SAP - CORRECT for industry):**
- Weighted SAP = (0.134 × 0.70) + (0.188 × 0.30) = 0.1502
- Total lye = 1000 × 0.1502 × 0.95 = 142.69g
- NaOH = 142.69 × 0.70 = 99.9g
- KOH = 142.69 × 0.30 = 42.8g

**Difference:**
- Formula B: 89.2g NaOH, 53.6g KOH
- Formula A: 99.9g NaOH, 42.8g KOH
- Significant difference (~10g NaOH, ~10g KOH)

This matters for soap quality and safety!

## Test Results

```
============================= test session starts ==============================
tests/unit/test_lye_calculator.py::TestNaOHCalculation::test_100_percent_naoh_standard_recipe PASSED
tests/unit/test_lye_calculator.py::TestNaOHCalculation::test_naoh_with_zero_superfat PASSED
tests/unit/test_lye_calculator.py::TestNaOHCalculation::test_naoh_with_high_superfat PASSED
tests/unit/test_lye_calculator.py::TestKOHCalculation::test_100_percent_koh PASSED
tests/unit/test_lye_calculator.py::TestMixedLyeCalculation::test_70_30_naoh_koh_split PASSED
tests/unit/test_lye_calculator.py::TestMixedLyeCalculation::test_50_50_naoh_koh_split PASSED
tests/unit/test_lye_calculator.py::TestMixedLyeCalculation::test_mixed_lye_weight_percentage_convention PASSED
tests/unit/test_lye_calculator.py::TestSuperfatValidation::test_valid_superfat_no_warning PASSED
tests/unit/test_lye_calculator.py::TestSuperfatValidation::test_high_superfat_warning PASSED
tests/unit/test_lye_calculator.py::TestSuperfatValidation::test_negative_superfat_error PASSED
tests/unit/test_lye_calculator.py::TestSuperfatValidation::test_invalid_lye_percentages PASSED
tests/unit/test_lye_calculator.py::TestSuperfatValidation::test_invalid_superfat_out_of_range PASSED
tests/unit/test_lye_calculator.py::TestRoundingPrecision::test_output_rounded_to_one_decimal PASSED

============================== 13 passed in 0.23s ==============================
```

**Coverage:** 100% for `app/services/lye_calculator.py`

## Validation Checklist

- ✅ 100% NaOH recipes still work (unchanged from Formula A)
- ✅ 100% KOH recipes still work (unchanged from Formula A)
- ✅ Mixed lye (70/30, 50/50) use weight percentages
- ✅ All tests pass with 0.1g tolerance
- ✅ Matches industry practice per Shale
- ✅ Documentation clearly explains convention
- ✅ New test validates weight percentage convention

## Impact

This fix ensures the calculator produces **industry-correct results** for mixed lye recipes. The previous Formula B approach would have:
- Produced incorrect NaOH/KOH ratios
- Not matched MGA's actual soap recipes
- Confused professional soap makers expecting weight-based splits

Now the calculator correctly implements the weight percentage convention used by professional soap makers.

## Metadata

- **Status:** Complete
- **Confidence:** High
- **Follow-up:** No (all requirements met)
- **Files Modified:**
  - `app/services/lye_calculator.py`
  - `tests/unit/test_lye_calculator.py`
