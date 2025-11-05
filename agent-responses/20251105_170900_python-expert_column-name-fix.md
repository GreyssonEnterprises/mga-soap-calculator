# Python Expert - Column Name Mismatch Fix

**Timestamp:** 2025-11-05T17:09:00-08:00
**Task:** Fix column name mismatch preventing additive recommendations from calculating
**Requestor:** Bob

## Response

### Problem Identified

The additive recommendation calculator was returning empty values due to a column name mismatch between the database schema and API code:

**Import Scripts Populate:**
- `typical_usage_min_percent`
- `typical_usage_max_percent`

**API Code Was Reading:**
- `usage_rate_min_pct` (NULL)
- `usage_rate_max_pct` (NULL)
- `usage_rate_standard_pct` (NULL)

### Root Cause

The Additive model (`app/models/additive.py`) has BOTH sets of columns:
- Lines 36-45: `typical_usage_min_percent`, `typical_usage_max_percent` (populated)
- Lines 68-82: `usage_rate_min_pct`, `usage_rate_max_pct`, `usage_rate_standard_pct` (empty)

The API code was reading the wrong (empty) columns.

### Solution Implemented

Updated `app/api/v1/additives.py` to read the correct populated columns:

```python
# Light usage (minimum)
if additive.typical_usage_min_percent:
    light_amount_g = round((batch_size_g * float(additive.typical_usage_min_percent)) / 100, 1)
    recommendations["light"] = UsageRecommendation(
        amount_g=light_amount_g,
        amount_oz=round(light_amount_g / 28.35, 2),
        usage_percentage=float(additive.typical_usage_min_percent)
    )

# Standard usage (calculate as average since no dedicated column exists)
if additive.typical_usage_min_percent and additive.typical_usage_max_percent:
    standard_pct = (float(additive.typical_usage_min_percent) + float(additive.typical_usage_max_percent)) / 2
    standard_amount_g = round((batch_size_g * standard_pct) / 100, 1)
    recommendations["standard"] = UsageRecommendation(
        amount_g=standard_amount_g,
        amount_oz=round(standard_amount_g / 28.35, 2),
        usage_percentage=round(standard_pct, 2)
    )

# Heavy usage (maximum)
if additive.typical_usage_max_percent:
    heavy_amount_g = round((batch_size_g * float(additive.typical_usage_max_percent)) / 100, 1)
    recommendations["heavy"] = UsageRecommendation(
        amount_g=heavy_amount_g,
        amount_oz=round(heavy_amount_g / 28.35, 2),
        usage_percentage=float(additive.typical_usage_max_percent)
    )
```

**Key Change:** Since there's no `typical_usage_percent` column for standard usage, I calculate it as the average of min and max, which provides a sensible middle-ground recommendation.

### Verification Results

**Test 1 - Honey (500g batch):**
```json
{
    "recommendations": {
        "light": {
            "amount_g": 5.0,
            "amount_oz": 0.18,
            "usage_percentage": 1.0
        },
        "standard": {
            "amount_g": 10.0,
            "amount_oz": 0.35,
            "usage_percentage": 2.0
        },
        "heavy": {
            "amount_g": 15.0,
            "amount_oz": 0.53,
            "usage_percentage": 3.0
        }
    }
}
```

**Test 2 - Aloe Powder (800g batch):**
```json
{
    "recommendations": {
        "light": {
            "amount_g": 2.0,
            "amount_oz": 0.07,
            "usage_percentage": 0.25
        },
        "standard": {
            "amount_g": 4.0,
            "amount_oz": 0.14,
            "usage_percentage": 0.5
        },
        "heavy": {
            "amount_g": 6.0,
            "amount_oz": 0.21,
            "usage_percentage": 0.75
        }
    }
}
```

Both tests show recommendations are calculating correctly with actual values instead of empty/null.

### Deployment Notes

**Container Status:**
- Built fresh container with fix: `mga-soap-calculator-api:latest`
- Tested in isolated container successfully
- Ready for production deployment

**No Migration Required:**
- No database schema changes
- Simple column name fix in API code
- Safe to deploy immediately

**Files Modified:**
- `app/api/v1/additives.py` (column name references)

**Commit:**
```
c6d6cc2 Fix: Use correct column names for additive usage rates
```

### Production Deployment Plan

1. **Tag and push container:**
   ```bash
   podman tag mga-soap-calculator-api:latest grimm-lin.local:5000/mga-soap-calculator-api:column-fix
   podman push grimm-lin.local:5000/mga-soap-calculator-api:column-fix
   ```

2. **Deploy via Ansible:**
   ```bash
   cd ansible
   ansible-playbook playbooks/deploy-quick.yml -e "image_tag=column-fix"
   ```

3. **Verify in production:**
   ```bash
   curl "https://grimm-lin.local/api/v1/additives/honey/recommend?batch_size_g=500"
   ```

### Alternative Cleanup (Optional)

Consider removing the unused `usage_rate_*` columns from the Additive model in a future cleanup migration since they're not being populated or used. But that's not urgent - the fix works with both column sets present.

## Metadata
- **Status**: Complete
- **Confidence**: High
- **Follow-up**: Optional - cleanup unused columns in future migration
- **Files**: app/api/v1/additives.py
