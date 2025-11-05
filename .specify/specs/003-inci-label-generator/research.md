# Phase 0 Research: INCI Label Generator

**Feature**: 003-inci-label-generator
**Research Date**: 2025-11-05
**Researcher**: System Architect

## Research Objectives

1. Document saponified INCI naming patterns for NaOH and KOH soap salts
2. Define percentage calculation methodology for regulatory compliance
3. Identify edge cases in saponified nomenclature
4. Design reference data structure for saponified-inci-terms.json
5. Establish sorting and formatting rules for multi-ingredient labels

## 1. Saponified INCI Naming Patterns

### 1.1 NaOH Soap Salts (Bar Soap)

**Standard Pattern**: `Sodium [Base Oil Name]ate`

**Examples**:
- Coconut Oil → `Sodium Cocoate`
- Olive Oil → `Sodium Olivate`
- Palm Oil → `Sodium Palmate`
- Shea Butter → `Sodium Shea Butterate`
- Sweet Almond Oil → `Sodium Sweet Almondate`

**Chemical Explanation**: Saponification converts triglycerides (oils) into glycerin and fatty acid salts. When using sodium hydroxide (NaOH), the resulting salt is the sodium form of the fatty acids present in the oil.

### 1.2 KOH Soap Salts (Liquid Soap)

**Standard Pattern**: `Potassium [Base Oil Name]ate`

**Examples**:
- Coconut Oil → `Potassium Cocoate`
- Olive Oil → `Potassium Olivate`
- Castor Oil → `Potassium Castorate` or `Potassium Ricinoleate`

**Chemical Explanation**: Potassium hydroxide (KOH) produces softer, more water-soluble soap salts, ideal for liquid soap formulations. The naming pattern follows the same suffix logic as sodium soaps but produces different physical properties.

### 1.3 Special Cases and Exceptions

**Castor Oil (Dual Nomenclature)**:
- Option 1: `Sodium Castorate` (derived from oil common name)
- Option 2: `Sodium Ricinoleate` (derived from ricinoleic acid, the dominant fatty acid)
- **Recommendation**: Use both forms separated by "or" - `Sodium Castorate or Sodium Ricinoleate`
- **Rationale**: Both are INCI-compliant; dual listing provides clarity for regulators familiar with either term

**Complex Oil Names**:
- Oils with multi-word names generally append entire name before "-ate" suffix
- Example: `Sodium Shea Butterate` (not "Sodium Sheate")
- Hyphenated oils maintain hyphens: `Sweet Almond Oil` → `Sodium Sweet Almondate`

**Oils Without Established Saponified INCI Names**:
- Generic pattern generation: Remove common suffixes ("Oil", "Butter"), append "-ate"
- Example: `Mango Butter` → `Sodium Mangoate` (if not in reference data)
- Flag these as "generated" for manual review in production data

### 1.4 Mixed Lye Formulations

**Scenario**: Recipe uses both NaOH and KOH (e.g., dual-lye soap for specific texture)

**INCI Representation**:
- List BOTH sodium and potassium salts for each oil
- Order by total percentage of each salt form
- Example for Coconut Oil (60% NaOH, 40% KOH):
  - `Sodium Cocoate` (60% of coconut contribution)
  - `Potassium Cocoate` (40% of coconut contribution)

**Percentage Calculation for Mixed Lye**:
```
Sodium Salt % = (Oil Weight × NaOH Ratio) / Total Batch Weight × 100
Potassium Salt % = (Oil Weight × KOH Ratio) / Total Batch Weight × 100
```

Where:
- `NaOH Ratio` = NaOH weight / (NaOH weight + KOH weight)
- `KOH Ratio` = KOH weight / (NaOH weight + KOH weight)

## 2. Percentage Calculation Methodology

### 2.1 Total Batch Weight Components

**Formula**:
```
Total Batch Weight = Oil Weight + Water Weight + Lye Weight + Additive Weight
```

Where:
- **Oil Weight**: Sum of all oil/fat ingredient weights
- **Water Weight**: Total water used (including water from additives like aloe vera juice)
- **Lye Weight**: NaOH weight + KOH weight (for mixed lye)
- **Additive Weight**: Sum of all non-oil ingredients (clays, botanicals, fragrances, colorants)

### 2.2 Individual Ingredient Percentage

**Formula**:
```
Ingredient % = (Ingredient Weight / Total Batch Weight) × 100
```

**Precision**: Round to 2 decimal places for internal calculations, display as needed by format (typically 1 decimal or whole number for labels)

### 2.3 Regulatory Compliance

**Sorting Requirement**: All ingredients MUST be sorted in descending order by percentage (highest to lowest). This is a regulatory requirement in most cosmetics jurisdictions (FDA, EU, Canada).

**Threshold Handling**:
- Ingredients below 1% still listed in order (not excluded)
- No "and other ingredients" clauses - full transparency required
- Trace amounts (<0.1%) may be labeled as "less than 1%" in consumer-facing labels, but API returns exact percentages

### 2.4 Saponified Oil Percentage Calculation

**Key Insight**: Post-saponification, oil weight is NOT the percentage. The soap salt weight must be calculated.

**Chemical Transformation**:
```
Oil + Lye → Soap Salt + Glycerin
```

**Soap Salt Weight Calculation**:
```
Soap Salt Weight = Oil Weight + (Lye Weight Used for That Oil)
```

**Lye Allocation by Oil**:
```
Lye for Oil = Oil Weight × SAP Value × (1 - Superfat Decimal)
```

Where:
- `SAP Value` = Saponification value (NaOH or KOH per gram of oil)
- `Superfat Decimal` = Superfat percentage / 100 (e.g., 5% = 0.05)

**Example Calculation**:
- Coconut Oil: 100g (SAP NaOH: 0.19)
- Superfat: 5% (0.95 reaction ratio)
- Lye used: 100 × 0.19 × 0.95 = 18.05g
- Soap salt weight: 100 + 18.05 = 118.05g
- Total batch weight: 500g
- Sodium Cocoate percentage: (118.05 / 500) × 100 = 23.61%

### 2.5 Water and Lye in Raw INCI Format

**Raw INCI (Pre-Saponification)**:
- Water: Listed as `Water` or `Aqua` at its full percentage
- Lye: Listed as `Sodium Hydroxide` and/or `Potassium Hydroxide` at their full percentages
- Oils: Listed by INCI name at their full percentages

**Saponified INCI (Post-Saponification)**:
- Water: Reduced percentage (some water reacts during saponification, though minor)
- Lye: EXCLUDED (fully incorporated into soap salts)
- Oils: Converted to soap salts with adjusted percentages

## 3. Edge Case Handling

### 3.1 Missing INCI Names

**Scenario**: Oil or additive lacks a standardized INCI name

**Fallback Strategy**:
1. Check reference data (saponified-inci-terms.json)
2. If missing, use common name as fallback
3. Flag in response metadata for manual review
4. Log warning for data completeness improvement

**Example**:
```json
{
  "saponified_inci": "Sodium Mangoate",
  "metadata": {
    "generated": true,
    "confidence": "medium",
    "source": "pattern-based generation"
  }
}
```

### 3.2 Trace Ingredients (<1%)

**Handling**: Include in sorted list regardless of percentage

**Regulatory Rationale**: Even trace amounts of allergens or functional ingredients must be disclosed

**Display Precision**: Show actual percentage (e.g., 0.3%) rather than rounding to 0%

### 3.3 Additives Without INCI Names

**Examples**: "Mica" (mineral colorant), "Turmeric Powder" (botanical)

**Strategy**:
- Use common name in ALL formats (raw, saponified, common)
- Do not attempt to generate pseudo-INCI names
- Maintain consistency across formats for non-oils

### 3.4 Essential Oils vs Fragrance Oils

**Essential Oils**: Use botanical INCI name (e.g., `Lavandula Angustifolia Oil`)

**Fragrance Oils**: Use generic term `Fragrance` or `Parfum` (EU convention)

**Detection Logic**:
```python
if ingredient.type == "essential_oil":
    use_botanical_inci_name()
elif ingredient.type == "fragrance_oil":
    use_generic_term("Fragrance")
```

### 3.5 Multiple Lye Types in Single Recipe

**Scenario**: Recipe uses both NaOH and KOH

**Raw INCI Format**:
```
Sodium Hydroxide, Potassium Hydroxide, [other ingredients sorted by %]
```

**Saponified INCI Format**:
- Both sodium and potassium salts for each oil
- Example: `Sodium Cocoate, Potassium Olivate, Sodium Palmate`
- Sorted by individual salt percentage (not combined oil percentage)

## 4. Reference Data Structure Design

### 4.1 saponified-inci-terms.json Schema

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-05",
  "source": "Industry standard INCI nomenclature database",
  "oils": [
    {
      "oil_id": "coconut-oil",
      "common_name": "Coconut Oil",
      "raw_inci_name": "Cocos Nucifera Oil",
      "saponified_inci_naoh": "Sodium Cocoate",
      "saponified_inci_koh": "Potassium Cocoate",
      "alternates": [],
      "notes": "Standard nomenclature, no exceptions"
    },
    {
      "oil_id": "castor-oil",
      "common_name": "Castor Oil",
      "raw_inci_name": "Ricinus Communis Seed Oil",
      "saponified_inci_naoh": "Sodium Castorate or Sodium Ricinoleate",
      "saponified_inci_koh": "Potassium Castorate or Potassium Ricinoleate",
      "alternates": [
        "Sodium Ricinoleate",
        "Sodium Castorate"
      ],
      "notes": "Dual nomenclature acceptable; both forms INCI-compliant"
    },
    {
      "oil_id": "olive-oil",
      "common_name": "Olive Oil",
      "raw_inci_name": "Olea Europaea Fruit Oil",
      "saponified_inci_naoh": "Sodium Olivate",
      "saponified_inci_koh": "Potassium Olivate",
      "alternates": [],
      "notes": "Standard nomenclature"
    }
  ]
}
```

### 4.2 Schema Field Definitions

- `oil_id`: Unique identifier matching Oil model primary key
- `common_name`: Consumer-friendly name (e.g., "Coconut Oil")
- `raw_inci_name`: Pre-saponification INCI name (botanical Latin)
- `saponified_inci_naoh`: Post-saponification with NaOH
- `saponified_inci_koh`: Post-saponification with KOH
- `alternates`: List of acceptable alternative nomenclatures
- `notes`: Implementation guidance or special handling instructions

### 4.3 Coverage and Expansion

**Initial Coverage**: 37 oils (common soapmaking oils)

**Expansion Strategy**:
1. Add oils as requested by MGA production use
2. Research INCI databases for new oils (Personal Care Products Council)
3. Validate with cosmetic chemist for accuracy
4. Version reference data file for tracking changes

## 5. Sorting and Formatting Rules

### 5.1 Ingredient Sorting Algorithm

```python
def sort_ingredients(ingredients: List[Ingredient]) -> List[Ingredient]:
    """
    Sort ingredients by percentage in descending order.
    Ties broken alphabetically by INCI name.
    """
    return sorted(
        ingredients,
        key=lambda x: (-x.percentage, x.inci_name)
    )
```

**Key Rules**:
- Primary sort: Percentage (descending)
- Secondary sort: INCI name (alphabetical) for ties
- Maintain precision during sort (don't round until display)

### 5.2 Output Format Options

**Single-Line Format (Default)**:
```
Sodium Cocoate, Aqua, Sodium Olivate, Sodium Shea Butterate, Glycerin, Fragrance
```

**Line-by-Line Format** (Optional):
```
Sodium Cocoate
Aqua
Sodium Olivate
Sodium Shea Butterate
Glycerin
Fragrance
```

**Percentage-Included Format** (Debugging):
```
Sodium Cocoate (23.6%), Aqua (20.5%), Sodium Olivate (18.2%), ...
```

### 5.3 Professional Presentation Rules

1. **Capitalization**: Each ingredient capitalized per INCI standards
2. **Separator**: Comma + space (`, `) between ingredients
3. **Termination**: No trailing punctuation (no final period or comma)
4. **Latin Names**: Maintain proper Latin capitalization (e.g., `Olea Europaea`)
5. **Consistency**: All three formats use same sorting order

## 6. Implementation Recommendations

### 6.1 Service Architecture

**Recommended Services**:

1. **inci_naming.py**: Saponified name generation
   - Input: Oil object, lye type (NaOH/KOH)
   - Output: Saponified INCI name string
   - Lookup reference data, fallback to pattern generation

2. **label_generator.py**: Label formatting and sorting
   - Input: Recipe object with calculations
   - Output: Three label format strings + breakdown array
   - Calculate percentages, sort ingredients, format output

### 6.2 Performance Optimization

**Database Query Strategy**:
- Single query for recipe with eager-loaded relationships (oils, additives)
- Avoid N+1 query problem with proper SQLAlchemy relationship loading
- Consider caching reference data (saponified-inci-terms.json) in memory

**Calculation Efficiency**:
- Pre-calculate total batch weight once
- Use list comprehension for percentage calculations
- Sort once after all percentages calculated

### 6.3 Testing Strategy

**Property-Based Tests (Hypothesis)**:
- Percentage sum always equals ~100% (allow rounding tolerance)
- Sorting order maintained for all ingredient counts
- No negative percentages
- Percentage precision consistent

**Unit Tests**:
- Saponified name generation for 37 reference oils
- Edge cases (missing data, trace ingredients, mixed lye)
- Format output structure validation

**Integration Tests**:
- Complete recipe INCI label generation
- Multiple formats returned correctly
- Percentage breakdown accuracy

### 6.4 Data Migration

**Alembic Migration**:
```python
# Add saponified_inci_name column to oils table
op.add_column('oils', sa.Column('saponified_inci_name', sa.String(200), nullable=True))

# Backfill from reference data
# Load saponified-inci-terms.json and update existing oils
```

**Backfill Strategy**:
1. Run migration to add column
2. Execute data script to populate from reference JSON
3. Flag oils without reference data for manual review
4. Consider making column NOT NULL after backfill complete

## 7. Open Questions and Future Considerations

### 7.1 Resolved Questions

✅ **Q**: Should saponified percentages account for glycerin production?
**A**: No. Glycerin is typically listed separately if retained in soap (not washed out). Soap salt percentage includes oil + lye consumed.

✅ **Q**: How to handle superfat in INCI labels?
**A**: Superfat oils remain as unsaponified oils in raw format, excluded from saponified format (since not reacted).

✅ **Q**: Are water percentage adjustments necessary post-saponification?
**A**: Minor - some water reacts, but effect is negligible (<2%). Use actual water weight for simplicity.

### 7.2 Future Enhancements (Out of Scope for Phase 2)

- Multi-language INCI translations (EU requires local language + INCI)
- Allergen highlighting (bold or asterisk for common allergens)
- PDF label export with formatting
- Historical label versioning (track INCI changes over time)
- Custom label templates (letterhead, brand styling)

## 8. References

**INCI Nomenclature Standards**:
- Personal Care Products Council (PCPC) INCI Dictionary
- International Nomenclature of Cosmetic Ingredients (EU)
- FDA labeling requirements for cosmetics (USA)

**Saponification Chemistry**:
- Triglyceride + Base → Soap Salt + Glycerin
- SAP values from verified soapmaking databases (SoapCalc, Soapmaking Friend)

**Regulatory Requirements**:
- FDA: Ingredients listed in descending order of predominance
- EU Cosmetics Regulation 1223/2009: INCI naming required
- Canada Cosmetics Regulations: Similar descending order requirement

## 9. Success Criteria for Research Phase

✅ **Documented**: Saponified INCI naming patterns for NaOH and KOH
✅ **Defined**: Percentage calculation methodology with examples
✅ **Identified**: Edge cases and handling strategies
✅ **Designed**: Reference data structure (saponified-inci-terms.json)
✅ **Established**: Sorting and formatting rules
✅ **Recommended**: Service architecture and testing approach

**Research Phase Complete** - Ready for Phase 1 (Design)
