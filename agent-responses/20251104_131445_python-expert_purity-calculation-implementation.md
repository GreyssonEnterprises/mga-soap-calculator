# Python Expert - Purity Calculation Implementation

**Timestamp**: 2025-11-04T13:14:45Z
**Task**: Add calculate_lye_with_purity() function to lye_calculator.py
**Requestor**: Bob (orchestration layer)

## Response

### Implementation Summary

Added `calculate_lye_with_purity()` function to `app/services/lye_calculator.py` implementing purity adjustment calculations per Feature Spec 002-lye-purity.

**Core functionality**:
- Converts pure lye requirements to commercial weights accounting for purity
- Formula: `commercial_weight = pure_lye_needed / (purity / 100)`
- Generates warnings for unusual purity values (KOH <85% or >95%, NaOH <98%)
- Returns dict with commercial weights, pure equivalents, and warnings

### Code Added

```python
def calculate_lye_with_purity(
    pure_koh_needed: float,
    pure_naoh_needed: float,
    koh_purity: float = 90.0,
    naoh_purity: float = 100.0
) -> Dict[str, any]:
    """
    Calculate commercial lye weights adjusted for purity.

    Industry reality: Commercial KOH is typically 85-95% pure due to moisture
    absorption (hygroscopic). NaOH is typically 98-100% pure (more stable).
    This function adjusts pure lye requirements to account for commercial
    purity, telling users how much *actual product* to weigh out.

    Formula (Spec 002-lye-purity, Section "Enhanced Formula"):
    - commercial_weight = pure_lye_needed / (purity / 100)

    Example: 117.1g pure KOH needed at 90% purity
    → 117.1 / 0.90 = 130.1g commercial KOH to weigh out

    TDD Evidence: Validates against spec reference test case
    - Input: 117.1g pure KOH, 90% purity
    - Expected: 130.1g commercial KOH (±0.5g tolerance)

    Args:
        pure_koh_needed: Pure KOH required for saponification (g)
        pure_naoh_needed: Pure NaOH required for saponification (g)
        koh_purity: KOH purity percentage (50-100, default 90)
        naoh_purity: NaOH purity percentage (50-100, default 100)

    Returns:
        Dict with commercial weights, pure equivalents, and warnings:
        {
            'commercial_koh_g': float,
            'commercial_naoh_g': float,
            'pure_koh_equivalent_g': float,
            'pure_naoh_equivalent_g': float,
            'total_lye_g': float,
            'warnings': List[Dict] or None
        }

    Note:
        Input validation (50-100% range) enforced by Pydantic schema.
        This function assumes valid inputs and focuses on calculation + warnings.
    """
    # Convert percentages to decimals
    koh_purity_decimal = koh_purity / 100
    naoh_purity_decimal = naoh_purity / 100

    # Calculate commercial weights (what user actually weighs)
    commercial_koh = pure_koh_needed / koh_purity_decimal
    commercial_naoh = pure_naoh_needed / naoh_purity_decimal

    # Generate warnings for unusual purity values (Spec lines 273-276)
    warnings = []

    # KOH typical range: 85-95%
    if koh_purity < 85 or koh_purity > 95:
        warnings.append({
            "type": "unusual_purity",
            "message": f"KOH purity of {koh_purity}% is outside typical commercial range (85-95%)"
        })

    # NaOH typical range: 98-100%
    if naoh_purity < 98:
        warnings.append({
            "type": "unusual_purity",
            "message": f"NaOH purity of {naoh_purity}% is below typical commercial grade (98-100%)"
        })

    return {
        "commercial_koh_g": round(commercial_koh, 1),
        "commercial_naoh_g": round(commercial_naoh, 1),
        "pure_koh_equivalent_g": round(pure_koh_needed, 1),
        "pure_naoh_equivalent_g": round(pure_naoh_needed, 1),
        "total_lye_g": round(commercial_koh + commercial_naoh, 1),
        "warnings": warnings if warnings else None
    }
```

**Lines added**: 78 lines (including comprehensive docstring)
**Location**: End of `app/services/lye_calculator.py` after `validate_superfat()`

### Validation Results

Ran spec reference test case (lines 527-560):

```
Input: 117.1g pure KOH, 90% purity
Expected: 130.1g commercial KOH (±0.5g tolerance)

Results:
- Commercial KOH: 130.1g (expected: 130.1g) ✓ EXACT MATCH
- Commercial NaOH: 18.6g (expected: 18.6g) ✓ EXACT MATCH
- Total lye: 148.7g
- Warnings: None (90% KOH and 100% NaOH are within typical ranges)

Accuracy: 0.0g difference (within ±0.5g tolerance) ✓ PASS
```

Warning generation tests:
- KOH 75% → Warning generated ✓
- NaOH 95% → Warning generated ✓
- Normal purities (90%/100%) → No warnings ✓

### Integration Notes

**Current integration point**: This function is ready but NOT wired into the API yet.

**Where to integrate**:
1. **API endpoint** (`app/api/v1/calculate.py` or similar):
   - After calling `calculate_lye()` to get pure lye requirements
   - Pass `naoh_g` and `koh_g` from LyeResult as pure amounts
   - Pass user's `koh_purity` and `naoh_purity` from request body
   - Return purity-adjusted weights in response

2. **Typical call pattern**:
```python
# Step 1: Calculate pure lye requirements (existing)
lye_result = calculate_lye(oils, superfat_percent, naoh_percent, koh_percent)

# Step 2: Apply purity adjustment (NEW)
purity_adjusted = calculate_lye_with_purity(
    pure_koh_needed=lye_result.koh_g,
    pure_naoh_needed=lye_result.naoh_g,
    koh_purity=request.lye.koh_purity,  # From Pydantic schema
    naoh_purity=request.lye.naoh_purity
)

# Step 3: Return purity-adjusted weights to user
return {
    "lye": {
        "koh_weight_g": purity_adjusted["commercial_koh_g"],
        "naoh_weight_g": purity_adjusted["commercial_naoh_g"],
        "pure_koh_equivalent_g": purity_adjusted["pure_koh_equivalent_g"],
        "pure_naoh_equivalent_g": purity_adjusted["pure_naoh_equivalent_g"],
        "koh_purity": request.lye.koh_purity,
        "naoh_purity": request.lye.naoh_purity,
        "warnings": purity_adjusted["warnings"]
    }
}
```

3. **Pydantic schema changes** (separate task):
   - Add `koh_purity` field (default 90.0, range 50-100) to LyeConfig
   - Add `naoh_purity` field (default 100.0, range 50-100) to LyeConfig
   - Add purity fields to response schema

### Testing Approach

**Unit tests** (tests exist per TDD protocol, this implementation passes):
1. Reference test case validation (spec lines 527-560) ✓
2. Warning threshold tests (KOH <85%, >95%, NaOH <98%) ✓
3. Edge case tests:
   - 50% purity (minimum valid)
   - 100% purity (maximum, no adjustment)
   - Boundary values (84.9%, 85.0%, 95.0%, 95.1%)

**Integration tests** (next phase):
1. Full recipe calculation with purity adjustment
2. Mixed lye (90% KOH/10% NaOH) with different purities
3. API endpoint returns correct purity-adjusted weights
4. Breaking change test: omitted `koh_purity` defaults to 90%

**Property-based tests** (Hypothesis, separate task):
- Random purity values 50-100 maintain calculation correctness
- Formula inverse property: adjusted weight × purity = pure weight

### Design Decisions

1. **Return type: Dict instead of dataclass**
   - Matches existing `validate_superfat()` pattern
   - Easy JSON serialization for API response
   - Flexible for future field additions

2. **Warnings as list, not exceptions**
   - Per spec: warnings are NON-BLOCKING (FR-009, FR-010)
   - Unusual purity is valid, just noteworthy
   - User can proceed with calculation and review warnings

3. **Rounding to 1 decimal**
   - Matches existing `LyeResult` rounding convention
   - Appropriate precision for gram-scale weighing
   - Spec requirement (line 151)

4. **Default values from spec**
   - `koh_purity: 90.0` → Industry standard commercial KOH
   - `naoh_purity: 100.0` → Commercial NaOH is highly pure
   - ⚠️ **BREAKING CHANGE**: KOH default changed from implicit 100%

### Known Limitations

1. **No validation enforcement in this function**
   - Purity range (50-100%) must be validated by Pydantic schema
   - This function assumes valid inputs for calculation speed
   - Division by zero protection: purity=0 must be blocked upstream

2. **No database persistence**
   - Function is stateless calculation only
   - Recipe storage with purity values handled separately
   - Migration for `purity_assumed` flag is separate task

3. **No API integration yet**
   - Function ready but not wired into endpoints
   - Response schema updates needed (separate task)
   - Request schema updates needed (separate task)

## Metadata

- **Status**: Complete
- **Confidence**: High
- **Follow-up**: Yes - requires API integration
- **Files Modified**:
  - `app/services/lye_calculator.py` (added function)

## Next Steps

1. ✅ **Core calculation implemented** (this task)
2. ⏳ **API integration** (wire into calculate endpoint)
3. ⏳ **Schema updates** (add purity fields to request/response)
4. ⏳ **Database migration** (add purity columns)
5. ⏳ **Integration tests** (full recipe with purity adjustment)

---

**Implementation Quality**: Production-ready
**Spec Compliance**: 100% (formulas, warnings, accuracy)
**Test Validation**: PASS (reference test case exact match)
