# Bug Report: total_oil_weight_g Parameter Not Respected

**Date:** 2025-11-04
**Priority:** High
**Category:** API Bug / Batch Sizing
**Status:** Needs Fix

## Problem Statement

The API ignores the `total_oil_weight_g` parameter in calculation requests and defaults to 1000g batches regardless of what the user specifies. This makes it impossible to calculate recipes at specific batch sizes.

## Current Behavior

**API Request:**
```json
{
  "oils": [
    {"id": "olive_oil", "percentage": 70},
    {"id": "castor_oil", "percentage": 20},
    {"id": "coconut_oil", "percentage": 10}
  ],
  "total_oil_weight_g": 700,  // <-- IGNORED
  "lye": {...},
  "water": {...}
}
```

**API Response:**
```json
{
  "recipe": {
    "total_oil_weight_g": 1000.0,  // <-- Always 1000, ignores request
    "oils": [
      {"id": "olive_oil", "weight_g": 700.0, "percentage": 70.0},
      {"id": "castor_oil", "weight_g": 200.0, "percentage": 20.0},
      {"id": "coconut_oil", "weight_g": 100.0, "percentage": 10.0}
    ],
    "lye": {
      "koh_weight_g": 212.7  // Calculated for 1000g, not 700g
    }
  }
}
```

## Expected Behavior

**API Should:**
1. Accept `total_oil_weight_g` parameter
2. Calculate all amounts based on specified batch size
3. Return `total_oil_weight_g` matching the request

**For 700g batch:**
```json
{
  "recipe": {
    "total_oil_weight_g": 700.0,  // Should match request
    "oils": [
      {"id": "olive_oil", "weight_g": 490.0, "percentage": 70.0},
      {"id": "castor_oil", "weight_g": 140.0, "percentage": 20.0},
      {"id": "coconut_oil", "weight_g": 70.0, "percentage": 10.0}
    ],
    "lye": {
      "koh_weight_g": 148.9  // Calculated for 700g batch
    }
  }
}
```

## Impact

### User Impact:
- Users cannot calculate recipes at desired batch sizes
- Must manually scale all amounts (oils, lye, water, additives)
- Error-prone manual calculations
- Poor user experience

### Business Impact:
- Cannot test real-world recipes
- Makes API less usable for production
- Workaround required on frontend
- Reduces API value proposition

## Test Case Demonstrating Bug

**Test Recipe:**
- 700g total oils
- 70% olive oil (490g)
- 20% castor oil (140g)
- 10% coconut oil (70g)
- 100% KOH at 90% purity
- 1% superfat
- 20% lye concentration

**Expected Results:**
- Total oil weight: 700g
- KOH (90% pure): 149g
- Water: 597g

**Actual API Results (for 1000g batch):**
- Total oil weight: 1000g
- KOH (90% pure): 212.7g
- Water: 818g

**Scaled to 700g (manual workaround):**
- 212.7g × 0.7 = 148.9g ✓ (matches expected)

**Conclusion:** The KOH purity calculation IS correct, but it's calculating for 1000g instead of 700g.

## Root Cause (Hypothesis)

Possible causes:
1. `total_oil_weight_g` parameter not defined in API schema
2. Parameter defined but not used in calculation logic
3. Default value (1000g) hardcoded and overriding request
4. Parameter name mismatch between request and backend

## Proposed Fix

### Option 1: Respect total_oil_weight_g Parameter

```python
def calculate_recipe(request):
    # Use batch size from request, default to 1000g if not provided
    total_oil_weight_g = request.total_oil_weight_g or 1000.0

    # Calculate oil weights based on batch size
    for oil in request.oils:
        oil.weight_g = (oil.percentage / 100) * total_oil_weight_g

    # Rest of calculations use total_oil_weight_g
    # ...
```

### Option 2: Remove Parameter, Always Use 1000g

If batch sizing isn't a planned feature:
- Remove `total_oil_weight_g` from request schema
- Document that API always returns 1000g batches
- Users scale on frontend

**Recommendation:** Option 1 - Batch sizing is essential for real-world use

## Validation Test

After fix, run this test:

```bash
# Request 700g batch
POST /api/v1/calculate
{
  "total_oil_weight_g": 700,
  "oils": [{"id": "olive_oil", "percentage": 100}],
  ...
}

# Should return:
{
  "recipe": {
    "total_oil_weight_g": 700.0,  // Must match request
    "oils": [
      {"id": "olive_oil", "weight_g": 700.0}  // Not 1000
    ]
  }
}
```

## Workaround (Temporary)

**Frontend Calculation:**
```javascript
function scaleToBatchSize(apiResponse, desiredBatchSizeG) {
  const scaleFactor = desiredBatchSizeG / apiResponse.recipe.total_oil_weight_g;

  return {
    ...apiResponse,
    recipe: {
      ...apiResponse.recipe,
      total_oil_weight_g: desiredBatchSizeG,
      oils: apiResponse.recipe.oils.map(oil => ({
        ...oil,
        weight_g: oil.weight_g * scaleFactor
      })),
      lye: {
        ...apiResponse.recipe.lye,
        naoh_weight_g: apiResponse.recipe.lye.naoh_weight_g * scaleFactor,
        koh_weight_g: apiResponse.recipe.lye.koh_weight_g * scaleFactor,
        total_lye_g: apiResponse.recipe.lye.total_lye_g * scaleFactor
      },
      water_weight_g: apiResponse.recipe.water_weight_g * scaleFactor
    }
  };
}
```

## Priority

**High** because:
- Blocks real-world recipe testing
- Core functionality expected by users
- Easy fix (likely simple parameter wiring)
- Required for production use

---

**Reported by:** Shale + Patterson (API Testing)
**Next Steps:** Review parameter handling in backend code, implement fix, validate with test cases
**Estimated Fix Time:** 30 minutes - 1 hour
