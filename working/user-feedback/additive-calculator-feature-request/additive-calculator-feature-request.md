# Feature Request: Smart Additive Calculator

**Date:** 2025-11-04
**Priority:** High
**Category:** Recipe Formulation / User Experience
**Status:** Proposed

## Problem Statement

Soap makers need to manually calculate additive amounts based on batch size and recommended usage rates. This requires:
1. Knowing standard usage rates for each additive
2. Converting batch size to pounds (if using tablespoon-based rates)
3. Calculating exact grams needed
4. Risk of using too much/too little

The API should automatically suggest proper additive amounts based on batch size and provide usage rate recommendations.

## Current Behavior

**API Request:**
```json
{
  "oils": [...],
  "additives": [
    {"id": "kaolin_clay", "usage_percent": 2}  // User must know 2% is correct
  ]
}
```

**Problems:**
- User has to manually look up that kaolin clay should be 1-2%
- User has to calculate percentages themselves
- No guidance on what's too much/too little
- No warnings about tricky additives (honey accelerates trace, etc.)

## Proposed Solution

### API Enhancement: Additive Recommendations

**New Endpoint:** `GET /api/v1/additives/{id}/recommend`

**Query Parameters:**
- `batch_size_g` - Total oil weight in grams
- `soap_type` - "bar" or "liquid" (some additives behave differently)

**Response:**
```json
{
  "additive": {
    "id": "honey",
    "common_name": "Honey",
    "inci_name": "Honey"
  },
  "recommendations": {
    "standard_rate": {
      "percentage": 2,
      "description": "1 tablespoon per pound of oils",
      "amount_g": 31.0,
      "amount_oz": 1.1
    },
    "range": {
      "min_percentage": 1,
      "max_percentage": 3,
      "min_amount_g": 15.5,
      "max_amount_g": 46.5
    }
  },
  "usage_instructions": {
    "when_to_add": "Add to warm oils before mixing in lye solution",
    "preparation": "None required",
    "mixing_tips": "Stir well to distribute evenly"
  },
  "warnings": [
    {
      "type": "acceleration",
      "message": "Honey can cause soap to accelerate trace or overheat. Work quickly."
    },
    {
      "type": "gel_phase",
      "message": "Honey generates heat - soap may gel faster than expected."
    }
  ],
  "effects_on_soap": {
    "lather": "+15% bubbly lather",
    "hardness": "+5% bar hardness",
    "color": "Light tan to amber",
    "scent": "Mild honey aroma (may fade)"
  }
}
```

### Enhanced Calculation Request

**User-Friendly Request Format:**
```json
{
  "oils": [
    {"id": "olive_oil", "percentage": 70},
    {"id": "coconut_oil", "percentage": 30}
  ],
  "batch_size_g": 700,
  "lye": {...},
  "water": {...},
  "superfat_percent": 5,
  "additives": [
    {
      "id": "honey",
      "amount": "standard"  // NEW: use "standard", "light", "heavy", or specific percentage
    },
    {
      "id": "kaolin_clay",
      "amount": "light"  // Will use lower end of range
    }
  ]
}
```

**Response with Calculated Amounts:**
```json
{
  "recipe": {
    "total_oil_weight_g": 700,
    "oils": [...],
    "additives": [
      {
        "id": "honey",
        "common_name": "Honey",
        "requested_amount": "standard",
        "calculated_weight_g": 14.0,  // 2% of 700g
        "usage_percentage": 2.0,
        "when_to_add": "Add to warm oils before lye",
        "warnings": ["Can accelerate trace", "May cause overheating"]
      },
      {
        "id": "kaolin_clay",
        "common_name": "Kaolin Clay",
        "requested_amount": "light",
        "calculated_weight_g": 7.0,  // 1% of 700g (low end)
        "usage_percentage": 1.0,
        "when_to_add": "Add to lye water for more color extraction",
        "warnings": []
      }
    ]
  }
}
```

## Database Schema

### Additives Table Enhancement

```python
class Additive(Base):
    # Existing fields
    id = Column(String, primary_key=True)
    common_name = Column(String)
    inci_name = Column(String)

    # NEW FIELDS
    usage_rate_min_pct = Column(Float)  # e.g., 0.5
    usage_rate_max_pct = Column(Float)  # e.g., 3.0
    usage_rate_standard_pct = Column(Float)  # e.g., 2.0
    usage_rate_description = Column(String)  # e.g., "1 tablespoon per pound"

    when_to_add = Column(String)  # "Add to oils", "Add to lye water", "At trace"
    preparation_instructions = Column(Text)
    mixing_tips = Column(Text)

    # Effect modifiers (if applicable)
    lather_modifier = Column(Float)  # e.g., 1.15 for +15%
    hardness_modifier = Column(Float)
    color_effect = Column(String)
    scent_effect = Column(String)

    # Warnings
    accelerates_trace = Column(Boolean, default=False)
    causes_overheating = Column(Boolean, default=False)
    turns_brown = Column(Boolean, default=False)
    can_be_scratchy = Column(Boolean, default=False)

    # Categorization
    category = Column(String)  # exfoliant, colorant, lather_booster, etc.
```

### Pre-populated Additives Data

Using the additives-usage-reference.json data, populate the database:

```python
additives_seed_data = [
    {
        "id": "honey",
        "common_name": "Honey",
        "inci_name": "Honey",
        "usage_rate_min_pct": 1.0,
        "usage_rate_max_pct": 3.0,
        "usage_rate_standard_pct": 2.0,
        "usage_rate_description": "1 tablespoon per pound of oils",
        "when_to_add": "Add to warm oils before lye solution",
        "category": "lather_booster",
        "accelerates_trace": True,
        "causes_overheating": True,
        "lather_modifier": 1.15,
        "color_effect": "Light tan to amber"
    },
    {
        "id": "kaolin_clay",
        "common_name": "Kaolin Clay",
        "inci_name": "Kaolin",
        "usage_rate_min_pct": 1.0,
        "usage_rate_max_pct": 2.0,
        "usage_rate_standard_pct": 1.5,
        "usage_rate_description": "1 teaspoon per pound of oils",
        "when_to_add": "Add to lye water for more color, or at trace for swirling",
        "category": "clay",
        "color_effect": "White/cream"
    },
    # ... (populate all 19 additives from reference)
]
```

## User Experience Flow

### Scenario 1: Auto-Calculate Standard Amounts

**User Input:**
"I want to make 700g of soap with honey and kaolin clay"

**Calculator Response:**
```
Recipe: 700g oils

Recommended Additives:
✓ Honey - 14g (2% standard rate)
  Purpose: Lather booster
  Add to: Warm oils before lye
  ⚠️ Warning: Can accelerate trace and cause overheating

✓ Kaolin Clay - 10.5g (1.5% standard rate)
  Purpose: Colorant, light exfoliation
  Add to: Lye water (for more color) or at trace (for swirling)
```

### Scenario 2: Customize Amounts

**User Input:**
"I want light exfoliation with coffee grounds"

**Calculator Response:**
```
Coffee Grounds:
• Light: 7g (1% - minimal exfoliation)
• Standard: 14g (2% - moderate exfoliation)
• Heavy: 21g (3% - maximum exfoliation)

Selected: 7g (light)
Add to: Lye water for color extraction, or oils for speckling
```

### Scenario 3: Warning System

**User Input:**
"Add 5% honey to my recipe"

**Calculator Response:**
```
⚠️ WARNING: 5% honey exceeds recommended maximum (3%)

Risks:
- Severe trace acceleration
- High risk of overheating/volcano
- May cause cracking or separation

Recommended: Reduce to 2-3% (14-21g for your 700g batch)
```

## Frontend Features

### Additive Selector UI

```jsx
<AdditiveSelector>
  <SearchBar placeholder="Search additives (honey, clay, oatmeal...)" />

  <AdditiveCard additive="honey">
    <h3>Honey</h3>
    <p>Lather booster, adds natural amber color</p>

    <AmountSelector>
      <button>Light (1%)</button>
      <button selected>Standard (2%)</button>
      <button>Heavy (3%)</button>
      <input type="number" placeholder="Custom %" />
    </AmountSelector>

    <CalculatedAmount>
      For your 700g batch: 14g
    </CalculatedAmount>

    <Instructions>
      Add to warm oils before lye solution
      ⚠️ Can accelerate trace
    </Instructions>
  </AdditiveCard>
</AdditiveSelector>
```

### Smart Suggestions

**Based on Recipe Type:**
- High coconut oil % → Suggest milk powder or honey (boost conditioning)
- High olive oil (castile) → Suggest salt or sodium lactate (improve hardness)
- Very soft recipe → Suggest beeswax or sodium lactate
- Liquid soap → Filter out additives that don't work in liquid

## Competitive Advantage

**Most Calculators:**
- No additive guidance
- Users must research usage rates separately
- No warnings about problematic additives
- No effect modifiers

**MGA Calculator:**
- Built-in usage rate database
- Automatic amount calculation
- Proactive warnings
- Effect predictions (lather boost, color changes)
- Instructions on when/how to add

**Subscription Value:**
- Saves research time
- Prevents formulation errors
- Professional knowledge base
- Recipe success rate improvement

## Implementation Priority

**High Priority** because:
1. **User Safety:** Prevents dangerous mistakes (overheating from too much honey/sugar)
2. **Recipe Success:** Proper additive amounts improve soap quality
3. **Time Savings:** No manual research or calculation needed
4. **Competitive Feature:** Major differentiator from free calculators
5. **Educational Value:** Teaches users proper soap making techniques
6. **Low Implementation Cost:** Database + simple calculation logic

## Data Requirements

**Already Have:**
- 19 additives with usage rates and instructions (additives-usage-reference.json)
- Categories and purposes defined
- Warnings documented

**Need to Add:**
- Effect modifiers (lather boost %, hardness increase %)
- Color/scent descriptions
- Compatibility rules (which additives work with bar vs liquid)
- Combination warnings (some additives don't mix well)

## Example Implementation

### Calculation Logic

```python
def calculate_additive_amount(additive, oil_weight_g, amount_level="standard"):
    """
    Calculate additive amount based on batch size and usage level.

    Args:
        additive: Additive model instance
        oil_weight_g: Total oil weight in grams
        amount_level: "light", "standard", "heavy", or float percentage

    Returns:
        Calculated weight in grams and usage percentage
    """
    if amount_level == "light":
        usage_pct = additive.usage_rate_min_pct
    elif amount_level == "heavy":
        usage_pct = additive.usage_rate_max_pct
    elif amount_level == "standard":
        usage_pct = additive.usage_rate_standard_pct
    else:
        usage_pct = float(amount_level)  # Custom percentage

    # Calculate amount
    amount_g = (oil_weight_g * usage_pct) / 100

    # Check for warnings
    warnings = []
    if usage_pct > additive.usage_rate_max_pct:
        warnings.append(f"Exceeds recommended maximum ({additive.usage_rate_max_pct}%)")

    if additive.accelerates_trace:
        warnings.append("Can accelerate trace - work quickly")

    if additive.causes_overheating:
        warnings.append("May cause overheating - monitor temperature")

    return {
        "weight_g": round(amount_g, 1),
        "usage_percentage": usage_pct,
        "warnings": warnings
    }
```

## Success Metrics

- Users successfully add additives without formula failures
- Reduced support requests about additive amounts
- Increased recipe complexity (users experiment more with additives)
- Higher subscription retention (valuable professional feature)

## Related Features

### Future Enhancements:
1. **Additive Combinations:** Suggest compatible additive pairings
2. **Seasonal Suggestions:** Recommend additives based on time of year
3. **Skin Type Matching:** Suggest additives for dry/oily/sensitive skin
4. **Color Palette Tool:** Preview how colorant additives affect final soap color
5. **Batch Scaling:** Auto-adjust additive amounts when scaling recipes

---

**Submitted by:** Shale + Patterson (Product Development)
**Next Steps:** Review with Grimm, estimate implementation effort, prioritize in roadmap
**Dependencies:** Additives database with usage rates and instructions
**Estimated Implementation:** 4-6 hours (database setup + calculation logic + API endpoints + tests)
