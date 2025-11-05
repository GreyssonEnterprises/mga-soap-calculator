# Feature Request: INCI Name Format Options

**Date:** 2025-11-04
**Priority:** Medium
**Category:** Ingredient Labeling
**Status:** Proposed

## Problem Statement

Soap makers use different INCI naming conventions for ingredient labels depending on their labeling philosophy and regulatory requirements. The API should support generating ingredient lists in both formats.

## Two INCI Naming Approaches

### Approach 1: Raw Oil INCI Names
Lists the original oil names as they were before saponification.

**IMPORTANT:** Because these are pre-saponification ingredients, you MUST list the lye separately.

**Example Recipe:** Coconut Oil + Olive Oil + Castor Oil

**Ingredient Label:**
```
Cocos Nucifera Oil, Olea Europaea Fruit Oil, Ricinus Communis Seed Oil, Water, Sodium Hydroxide
```

**When Used:**
- European soap makers
- "Made with" marketing emphasis
- Emphasizing natural origins
- Some artisan/handmade soap makers

**Why Lye is Listed:** The oils haven't been chemically transformed yet in this naming convention, so lye appears as a separate ingredient.

### Approach 2: Saponified INCI Names
Lists the soap salts created after saponification with sodium hydroxide.

**IMPORTANT:** Lye is NOT listed separately because it's been chemically converted into the soap salts (the "Sodium" in "Sodium Cocoate" indicates NaOH was used).

**Same Recipe:**

**Ingredient Label:**
```
Sodium Cocoate, Sodium Olivate, Sodium Castorate, Water
```

**When Used:**
- U.S. soap makers (more common)
- Technically accurate (oils are chemically transformed)
- Commercial/professional products
- Regulatory compliance emphasis

**Why Lye is NOT Listed:** The lye has been chemically converted during saponification. "Sodium Cocoate" = Coconut Oil + Sodium Hydroxide (after reaction). No free lye remains in finished soap.

## Current Behavior

The API currently provides:
- Raw INCI names in the `inci_name` field (e.g., "Cocos Nucifera Oil")
- No saponified INCI names

Users cannot easily generate properly formatted ingredient labels for finished soap.

## Proposed Solution

### API Response Enhancement

Add a `saponified_inci_name` field to each oil in the response:

```json
{
  "recipe": {
    "oils": [
      {
        "id": "coconut_oil",
        "common_name": "Coconut Oil",
        "weight_g": 100,
        "percentage": 50,
        "inci_name": "Cocos Nucifera Oil",           // Existing
        "saponified_inci_name": "Sodium Cocoate"     // NEW
      },
      {
        "id": "olive_oil",
        "common_name": "Olive Oil",
        "weight_g": 100,
        "percentage": 50,
        "inci_name": "Olea Europaea Fruit Oil",      // Existing
        "saponified_inci_name": "Sodium Olivate"     // NEW
      }
    ]
  },
  "ingredient_labels": {                              // NEW SECTION
    "raw_inci": "Cocos Nucifera Oil, Olea Europaea Fruit Oil, Water, Sodium Hydroxide",
    "saponified_inci": "Sodium Cocoate, Sodium Olivate, Water",
    "common_names": "Coconut Oil, Olive Oil, Water, Lye"
  }
}
```

### Database Schema Addition

Add `saponified_inci_name` field to oils table:

```python
class Oil(Base):
    # ... existing fields ...
    inci_name = Column(String)
    saponified_inci_name = Column(String)  # NEW
```

### Saponified INCI Naming Rules

**For NaOH (Sodium Hydroxide) Soap:**
- Pattern: "Sodium [Oil Name]ate"
- Coconut Oil → Sodium Cocoate
- Olive Oil → Sodium Olivate
- Palm Oil → Sodium Palmate
- Tallow → Sodium Tallowate
- Castor Oil → Sodium Castorate or Sodium Ricinoleate

**For KOH (Potassium Hydroxide) Soap:**
- Pattern: "Potassium [Oil Name]ate"
- Coconut Oil → Potassium Cocoate
- Olive Oil → Potassium Olivate
- (Used in liquid soap formulations)

**For Mixed Lye:**
- List both sodium and potassium salts in proportion
- Example (90% KOH / 10% NaOH): "Potassium Olivate, Sodium Olivate"

## Implementation Details

### Database Population

Use the provided `saponified-inci-terms.json` reference file:

```python
# Load saponified terms reference
with open('saponified-inci-terms.json', 'r') as f:
    saponified_terms = json.load(f)

# Update oils table
for oil in Oil.query.all():
    common_name = oil.common_name
    # Match to saponified term
    if common_name in saponified_terms:
        oil.saponified_inci_name = saponified_terms[common_name]
    else:
        # Generate generic saponified name
        base_name = common_name.replace(' Oil', '').replace(' Butter', '')
        oil.saponified_inci_name = f"Sodium {base_name}ate"
```

### Response Generation Logic

**CRITICAL:** All ingredients MUST be sorted by percentage in descending order (highest to lowest). This includes oils, additives, fragrances, colorants, and all other ingredients.

```python
def generate_ingredient_labels(recipe):
    # Collect ALL ingredients with their percentages
    ingredients = []

    # Calculate total batch weight
    total_weight = recipe.total_oil_weight_g + recipe.water_weight_g + recipe.lye.total_lye_g

    # Add oils (sorted by percentage)
    for oil in recipe.oils:
        ingredients.append({
            'name': oil.common_name,
            'inci_raw': oil.inci_name,
            'inci_saponified': oil.saponified_inci_name,
            'percentage': oil.percentage * (recipe.total_oil_weight_g / total_weight)
        })

    # Add water
    water_pct = (recipe.water_weight_g / total_weight) * 100
    ingredients.append({
        'name': 'Water',
        'inci_raw': 'Water',
        'inci_saponified': 'Water',
        'percentage': water_pct
    })

    # Add lye (only for raw format - saponified format doesn't list it)
    lye_pct = (recipe.lye.total_lye_g / total_weight) * 100
    lye_name = "Sodium Hydroxide" if recipe.lye.naoh_percent > 50 else "Potassium Hydroxide"
    if recipe.lye.naoh_percent > 0 and recipe.lye.koh_percent > 0:
        lye_name = "Sodium Hydroxide, Potassium Hydroxide"

    ingredients.append({
        'name': 'Lye',
        'inci_raw': lye_name,
        'inci_saponified': None,  # Not listed in saponified format
        'percentage': lye_pct
    })

    # Add additives (if present)
    for additive in recipe.additives:
        additive_pct = (additive.weight_g / total_weight) * 100
        ingredients.append({
            'name': additive.common_name,
            'inci_raw': additive.inci_name or additive.common_name,
            'inci_saponified': additive.inci_name or additive.common_name,
            'percentage': additive_pct
        })

    # Add fragrance (if present)
    if recipe.fragrance:
        fragrance_pct = (recipe.fragrance.weight_g / total_weight) * 100
        ingredients.append({
            'name': 'Fragrance',
            'inci_raw': 'Fragrance' if recipe.fragrance.is_fo else 'Essential Oil',
            'inci_saponified': 'Fragrance' if recipe.fragrance.is_fo else 'Essential Oil',
            'percentage': fragrance_pct
        })

    # SORT ALL INGREDIENTS BY PERCENTAGE (descending)
    ingredients.sort(key=lambda x: x['percentage'], reverse=True)

    # Generate labels in each format
    raw_inci_list = [ing['inci_raw'] for ing in ingredients if ing['inci_raw']]
    saponified_inci_list = [ing['inci_saponified'] for ing in ingredients if ing['inci_saponified']]
    common_names_list = [ing['name'] for ing in ingredients]

    return {
        "raw_inci": ", ".join(raw_inci_list),
        "saponified_inci": ", ".join(saponified_inci_list),
        "common_names": ", ".join(common_names_list),
        "ingredients_breakdown": ingredients  # For debugging/verification
    }
```

### Frontend Display Options

Give users a toggle or dropdown to choose labeling format:

```jsx
<select name="inci_format">
  <option value="saponified">Saponified (Sodium Olivate)</option>
  <option value="raw">Raw Oils (Olea Europaea Fruit Oil)</option>
  <option value="common">Common Names (Olive Oil)</option>
</select>
```

## User Value Proposition

### For Subscription Users:

**Professional Features:**
- Auto-generate compliant ingredient labels
- Support for both U.S. and European labeling conventions
- Copy-paste ready text for product labels
- Reduces labeling errors and regulatory risk

**Time Savings:**
- No manual INCI term lookup
- Automatic alphabetical or percentage-based sorting
- Instant label generation with each calculation

**Flexibility:**
- Choose labeling style based on market/regulations
- Switch between formats for A/B testing marketing copy
- Educate customers with both naming styles

## Implementation Priority

**Medium Priority** because:
1. **User Convenience:** Significant time-saver for professional soap makers
2. **Regulatory Compliance:** Helps users meet labeling requirements
3. **Competitive Feature:** Not all calculators offer this
4. **Low Effort:** Straightforward text generation from existing data
5. **Subscription Value:** Professional feature that justifies subscription cost

## Data Requirements

**Already Have:**
- Complete INCI reference database (339 entries)
- Saponified INCI terms (37 oils)
- Can generate missing saponified terms programmatically

**Need to Add:**
- Saponified INCI name field to oils table (~147 new values)
- Ingredient label generation logic in API response
- Frontend toggle/dropdown for label format selection

## Alternative Workarounds (Temporary)

**Client-Side Generation:**
```javascript
function generateIngredientLabel(oils, format = 'saponified') {
  const sorted = oils.sort((a, b) => b.percentage - a.percentage);

  if (format === 'saponified') {
    return sorted.map(oil => oil.saponified_inci_name).join(', ') + ', Water';
  } else if (format === 'raw') {
    return sorted.map(oil => oil.inci_name).join(', ') + ', Water, Sodium Hydroxide';
  } else {
    return sorted.map(oil => oil.common_name).join(', ') + ', Water, Lye';
  }
}
```

## Marketing Benefits

**Subscription Tier Feature:**
- "Professional INCI label generation"
- "Compliant ingredient lists - auto-generated"
- "European and U.S. labeling formats supported"
- "One-click label copy for product packaging"

**Differentiator from Free Calculators:**
- Most free calculators don't generate proper INCI labels
- Professional soap makers will pay for time-saving automation
- Reduces regulatory compliance risk

## Example Use Cases

### Use Case 1: Complete Recipe with Additives and Fragrance
Recipe:
- 35% Olive Oil
- 30% Coconut Oil
- 20% Palm Oil
- 10% Castor Oil
- 5% Shea Butter
- 2% Kaolin Clay (additive)
- 3% Lavender Essential Oil (fragrance)
- Water (38% of oils = typical)
- Lye (calculated)

**Saponified INCI Label (sorted by percentage):**
```
Water, Sodium Olivate, Sodium Cocoate, Sodium Palmate, Sodium Castorate,
Sodium Shea Butterate, Lavender Essential Oil, Kaolin Clay
```

**Raw INCI Label (sorted by percentage):**
```
Water, Olea Europaea Fruit Oil, Cocos Nucifera Oil, Elaeis Guineensis Oil,
Ricinus Communis Seed Oil, Butyrospermum Parkii Fruit, Sodium Hydroxide,
Lavandula Angustifolia Oil, Kaolin
```

**Common Names Label:**
```
Water, Olive Oil, Coconut Oil, Palm Oil, Castor Oil, Shea Butter, Lye,
Lavender Essential Oil, Kaolin Clay
```

### Use Case 2: Liquid Soap (KOH)
Recipe: 70% Olive, 20% Coconut, 10% Castor (all KOH)

**Saponified INCI Label:**
```
Potassium Olivate, Potassium Cocoate, Potassium Castorate, Water
```

### Use Case 3: Mixed Lye Soap
Recipe: 50% Coconut, 50% Olive (90% KOH / 10% NaOH)

**Saponified INCI Label:**
```
Water, Potassium Cocoate, Potassium Olivate, Sodium Cocoate, Sodium Olivate
```
(Lists predominant lye type first, then minor)

## Related Features to Consider

### Future Enhancements:
1. **Allergen Warnings:** Auto-detect common allergens (nut oils, etc.)
2. **Label Sorting:** Alphabetical vs. percentage-based ingredient ordering
3. **Multi-Language:** INCI translations for international markets
4. **PDF Label Export:** Generate printable ingredient labels
5. **Regulatory Compliance Checker:** Validate label meets local requirements

## Success Metrics

- Users can generate compliant ingredient labels in <5 seconds
- Support for 95%+ of common labeling conventions
- Reduce user support requests about ingredient naming
- Increase subscription conversions from professional makers

---

**Submitted by:** Shale + Patterson (API Testing & Product Development)
**Next Steps:** Review with Grimm, estimate implementation effort, prioritize in roadmap
**Dependencies:** Oils database with saponified INCI terms
**Estimated Implementation:** 2-4 hours (database update + API logic + tests)
