# Python Expert - Batch Size Parameter Fix

**Timestamp:** 2025-11-04T17:09:01-08:00
**Task:** Fix missing total_oil_weight_g parameter
**Requestor:** root-cause-analyst findings

## Problem Summary

**Root Cause** (from root-cause-analyst investigation):
- `total_oil_weight_g` parameter missing from CalculationRequest schema
- Hardcoded 1000g default in calculate.py line 108
- Pydantic silently drops the parameter because not declared in schema

## Fix Applied

### 1. Schema Update (`app/schemas/requests.py`)

**Added parameter to CalculationRequest:**
```python
total_oil_weight_g: Optional[float] = Field(default=1000.0, gt=0)
```

**Location:** Line 108 (after `additives` field)

**Rationale:**
- Optional field with 1000g default preserves existing behavior
- `gt=0` constraint ensures positive batch sizes only
- Backward compatible - existing clients work without change

### 2. Logic Update (`app/api/v1/calculate.py`)

**Changed line 107:**
```python
# OLD: total_oil_weight_g = 1000.0  # Default batch size
# NEW:
total_oil_weight_g = request.total_oil_weight_g  # Use request value
```

**Rationale:**
- Uses parameter from validated request
- Defaults to 1000g if client omits parameter
- No hardcoded magic numbers

## Validation

### Expected Behavior

✅ **Default (no parameter):** 1000g batch
✅ **Explicit 700g:** Respects 700g request
✅ **Explicit 1500g:** Respects 1500g request
✅ **Backward compatible:** Existing clients work unchanged

### Build Status

```bash
podman build -t mga-soap-calc:test .
# Result: SUCCESS
# Image: 0e056f370ae1
```

### Testing Required

Next steps for quality-engineer:

1. **Unit test** - Schema validation accepts parameter
2. **Integration test** - API respects batch sizes
3. **Regression test** - Default behavior unchanged

Test scenarios:
```json
// Test 1: Default (should use 1000g)
{
  "oils": [{"id": "olive", "percentage": 100.0}],
  "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
  "water": {"method": "water_percent_of_oils", "value": 38.0},
  "superfat_percent": 5.0
}

// Test 2: Explicit 700g
{
  "oils": [{"id": "olive", "percentage": 100.0}],
  "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
  "water": {"method": "water_percent_of_oils", "value": 38.0},
  "superfat_percent": 5.0,
  "total_oil_weight_g": 700.0
}

// Test 3: Explicit 1500g
{
  "oils": [{"id": "olive", "percentage": 100.0}],
  "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
  "water": {"method": "water_percent_of_oils", "value": 38.0},
  "superfat_percent": 5.0,
  "total_oil_weight_g": 1500.0
}
```

## Impact Assessment

### Files Changed
- `app/schemas/requests.py` - 1 line added
- `app/api/v1/calculate.py` - 1 line changed (comment updated, logic simplified)

### Risk Level
**LOW** - Backward compatible change with default preservation

### User Impact
**POSITIVE** - Enables custom batch sizes (previously impossible)

### Technical Debt
**REDUCED** - Eliminated hardcoded magic number

## Implementation Notes

### Why Optional with Default?

Making the field required would break existing API clients. Optional with default=1000.0 provides:
- Backward compatibility
- Explicit control when needed
- Clear migration path

### Alternative Approaches Considered

**❌ Required field:** Breaks existing clients
**❌ Server-side config:** Less flexible for users
**✅ Optional with default:** Best of both worlds

## Status

- ✅ Schema updated
- ✅ Logic updated
- ✅ Docker build successful
- ⏳ Awaiting quality-engineer validation
- ⏳ Awaiting deployment-engineer container push

**Confidence:** High
**Follow-up:** Yes (testing required)
**Files:**
- app/schemas/requests.py
- app/api/v1/calculate.py
