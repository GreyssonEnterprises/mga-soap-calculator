# Root Cause Analysis: total_oil_weight_g Parameter Bug

**Agent**: Root Cause Analyst
**Timestamp**: 2025-11-04 13:30:00
**Task**: Investigate why API ignores batch size parameter
**Requestor**: Patterson + Shale
**Status**: ✅ Complete - Root Cause Identified

---

## Executive Summary

**ROOT CAUSE IDENTIFIED**: The `total_oil_weight_g` parameter is **MISSING FROM THE REQUEST SCHEMA**.

The `CalculationRequest` Pydantic model (`app/schemas/requests.py`) does not define `total_oil_weight_g` as a field. When users send this parameter in their request, Pydantic silently ignores it because it's not part of the validated schema.

The API then defaults to 1000g on line 108 of `app/api/v1/calculate.py`:

```python
total_oil_weight_g = 1000.0  # Default batch size
```

This is **not a calculation bug** - it's a **missing parameter in the schema definition**.

---

## Investigation Evidence

### 1. Request Schema Analysis

**File**: `/app/schemas/requests.py` (lines 89-123)

```python
class CalculationRequest(BaseModel):
    """
    Complete calculation request matching spec Section 3.1.
    """
    oils: List[OilInput]
    lye: LyeConfig
    water: WaterConfig
    superfat_percent: float
    additives: List[AdditiveInput] = []
    # ⚠️ MISSING: total_oil_weight_g field
```

**Finding**: No `total_oil_weight_g` field defined. Pydantic will reject/ignore this parameter when sent in requests.

### 2. API Endpoint Logic Analysis

**File**: `/app/api/v1/calculate.py` (lines 95-110)

```python
# Step 1: Normalize oil inputs
try:
    if all(oil.weight_g is not None for oil in request.oils):
        # Weights provided - calculate percentages
        normalized_oils = normalize_oil_inputs(request.oils)
        total_oil_weight_g = sum(oil.weight_g for oil in normalized_oils)
    else:
        # Percentages provided - validate and use default
        percentages = [oil.percentage for oil in request.oils if oil.percentage is not None]
        validate_oil_percentages(percentages)

        # ⚠️ BUG: Hardcoded 1000g default, no access to request.total_oil_weight_g
        total_oil_weight_g = 1000.0  # Default batch size
        normalized_oils = normalize_oil_inputs(request.oils, total_weight_g=total_oil_weight_g)
```

**Finding**: When oils are specified by percentage (the common case), the API defaults to 1000g. There's no code attempting to read `request.total_oil_weight_g` because the schema doesn't define it.

### 3. User Experience

**What Users Send**:
```json
{
  "oils": [
    {"id": "olive_oil", "percentage": 70},
    {"id": "castor_oil", "percentage": 20},
    {"id": "coconut_oil", "percentage": 10}
  ],
  "total_oil_weight_g": 700,  // ⚠️ IGNORED - not in schema
  "lye": {...},
  "water": {...}
}
```

**What Pydantic Does**:
- Validates the defined fields (oils, lye, water, superfat_percent, additives)
- **Silently ignores** `total_oil_weight_g` (not in schema, no validation error)
- Passes validated request to endpoint handler

**What API Returns**:
```json
{
  "recipe": {
    "total_oil_weight_g": 1000.0,  // Always 1000g
    "oils": [...],  // Calculated for 1000g batch
    "lye": {...}    // Calculated for 1000g batch
  }
}
```

### 4. Grep Verification

**Search Results**: `grep -r "total_oil_weight" app/`

Found references in:
- ✅ Response schema (`responses.py`) - defined for OUTPUT
- ✅ API endpoint (`calculate.py`) - used in logic, but hardcoded value
- ✅ Service functions - all calculations use the value correctly
- ❌ **Request schema (`requests.py`)** - **NOT DEFINED FOR INPUT**

**Conclusion**: The entire backend calculation logic is correct. The parameter just never makes it through the front door.

---

## Root Cause Summary

### The Bug Chain

1. **Schema Missing Field**: `CalculationRequest` doesn't define `total_oil_weight_g`
2. **Pydantic Ignores Unknown Fields**: User's parameter is silently dropped
3. **API Defaults to 1000g**: Line 108 uses hardcoded default
4. **All Calculations Correct**: Everything downstream works perfectly - just uses wrong input

### Why This Happened

Looking at the code comments (line 106-107):
```python
# For now, require explicit total weight for percentage-based input
# In real implementation, this could come from user or default to 1000g
```

**Hypothesis**: The developers knew this was incomplete but shipped with the hardcoded default. The comment indicates awareness that batch sizing should be user-controllable.

---

## Impact Analysis

### Technical Impact
- ✅ All calculation logic is correct
- ✅ Lye, water, quality metrics all working properly
- ❌ Batch size input completely ignored
- ❌ Users cannot calculate custom batch sizes

### User Impact
- **High**: Cannot test real-world recipes at desired sizes
- **Workaround Required**: Manual scaling on frontend (error-prone)
- **Confidence Loss**: Parameter appears to work but is ignored

### Business Impact
- Reduces API usefulness for production
- Makes testing actual recipes impossible
- Requires frontend workarounds (technical debt)

---

## Recommended Fix

### Solution: Add total_oil_weight_g to Request Schema

**File**: `app/schemas/requests.py`

**Change Required**:
```python
class CalculationRequest(BaseModel):
    """
    Complete calculation request matching spec Section 3.1.
    """
    oils: List[OilInput]
    lye: LyeConfig
    water: WaterConfig
    superfat_percent: float
    additives: List[AdditiveInput] = []
    total_oil_weight_g: Optional[float] = Field(default=1000.0, gt=0)  # ADD THIS LINE
```

**Rationale**:
- `Optional[float]`: Not required, preserves backward compatibility
- `default=1000.0`: Existing behavior for clients not sending parameter
- `gt=0`: Validation ensures positive batch sizes only

### Update Endpoint Logic

**File**: `app/api/v1/calculate.py` (lines 106-109)

**Change From**:
```python
# For now, require explicit total weight for percentage-based input
# In real implementation, this could come from user or default to 1000g
total_oil_weight_g = 1000.0  # Default batch size
normalized_oils = normalize_oil_inputs(request.oils, total_weight_g=total_oil_weight_g)
```

**Change To**:
```python
# Use batch size from request (defaults to 1000g via schema)
total_oil_weight_g = request.total_oil_weight_g
normalized_oils = normalize_oil_inputs(request.oils, total_weight_g=total_oil_weight_g)
```

**That's it.** Two line changes total:
1. Add field to schema with default
2. Use `request.total_oil_weight_g` instead of hardcoded value

---

## Validation Test Cases

### Test Case 1: Custom Batch Size
```bash
POST /api/v1/calculate
{
  "total_oil_weight_g": 700,
  "oils": [{"id": "olive_oil", "percentage": 100}],
  "lye": {"naoh_percent": 0, "koh_percent": 100},
  "water": {"method": "water_percent_of_oils", "value": 40},
  "superfat_percent": 1
}

# Expected: total_oil_weight_g = 700.0 in response
# Expected: All amounts scaled to 700g batch
```

### Test Case 2: Default Batch Size (Backward Compatibility)
```bash
POST /api/v1/calculate
{
  # No total_oil_weight_g parameter
  "oils": [{"id": "olive_oil", "percentage": 100}],
  "lye": {"naoh_percent": 0, "koh_percent": 100},
  "water": {"method": "water_percent_of_oils", "value": 40},
  "superfat_percent": 1
}

# Expected: total_oil_weight_g = 1000.0 (default)
# Expected: Existing behavior preserved
```

### Test Case 3: Weight-Based Oils (Should Still Work)
```bash
POST /api/v1/calculate
{
  "total_oil_weight_g": 500,  # Should be ignored when weights provided
  "oils": [{"id": "olive_oil", "weight_g": 800}],
  "lye": {...},
  "water": {...},
  "superfat_percent": 1
}

# Expected: total_oil_weight_g = 800.0 (sum of oil weights)
# Expected: Parameter ignored when explicit weights provided
```

---

## Complexity Assessment

### Fix Difficulty: **TRIVIAL**
- **Lines Changed**: 2
- **Risk Level**: Very Low
- **Backward Compatibility**: Preserved via default value
- **Testing Required**: Schema validation + endpoint integration tests

### Estimated Time: **15 minutes**
- 5 min: Add schema field
- 5 min: Update endpoint logic
- 5 min: Run existing tests (should still pass)

### Risk Assessment: **LOW**
- ✅ Default value preserves existing behavior
- ✅ Optional field doesn't break existing clients
- ✅ All downstream calculations already handle the parameter correctly
- ⚠️ Need to verify schema validation tests don't break

---

## Follow-Up Actions

### Immediate Fix
1. Add `total_oil_weight_g: Optional[float] = Field(default=1000.0, gt=0)` to `CalculationRequest`
2. Change line 108 to `total_oil_weight_g = request.total_oil_weight_g`
3. Run test suite to verify no regressions

### Testing
1. Update schema validation tests to include `total_oil_weight_g`
2. Add integration test for custom batch sizes
3. Verify default behavior unchanged
4. Test edge cases (0g, negative, very large batches)

### Documentation
1. Update API documentation to show `total_oil_weight_g` parameter
2. Add example requests with custom batch sizes
3. Document that parameter is ignored when using weight-based oil inputs

---

## Metadata

**Files Analyzed**:
- ✅ `app/schemas/requests.py` (Request schema - **BUG LOCATION**)
- ✅ `app/schemas/responses.py` (Response schema - correct)
- ✅ `app/api/v1/calculate.py` (Endpoint logic - **HARDCODED DEFAULT**)
- ✅ `app/services/lye_calculator.py` (Calculations - correct)
- ✅ `app/services/water_calculator.py` (Calculations - correct)
- ✅ `app/services/validation.py` (Validation - correct)

**Status**: Complete - Root Cause Identified
**Confidence**: High (100%)
**Follow-up**: Required - Implement fix and validate
**Priority**: High (blocks real-world recipe testing)

---

**Next Steps**:
1. Implement recommended fix (2 line changes)
2. Run test suite
3. Deploy to test environment
4. Validate with original bug report test case
5. Update API documentation
