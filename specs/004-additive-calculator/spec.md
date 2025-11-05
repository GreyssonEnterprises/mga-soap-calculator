# Specification: Smart Additive Calculator

## Goal
Enable soap makers to automatically calculate precise additive amounts based on batch size with intelligent usage recommendations (light/standard/heavy) and safety warnings, eliminating manual calculations and reducing formulation errors.

## User Stories

- As a soap maker, I want automatic additive amount calculations based on my batch size so that I don't have to manually calculate percentages and weights
- As a formulator, I want usage recommendations (light/standard/heavy) for each additive so that I can achieve the desired effect without guesswork
- As a beginner, I want clear warnings about problematic additives (acceleration, overheating, scratchy texture) so that I avoid formulation failures
- As an advanced crafter, I want to see preparation instructions and mixing tips so that I incorporate additives correctly
- As a recipe creator, I want essential oil amount calculations based on safe usage rates so that my soap is skin-safe
- As a designer, I want colorant recommendations based on batch size so that I achieve consistent color results

## Specific Requirements

**Additive Recommendation Endpoint**
- New endpoint: `GET /api/v1/additives/{id}/recommend?batch_size_g={size}`
- Calculate light/standard/heavy usage amounts based on batch size
- Include usage percentages (min/standard/max) in response
- Return calculated weights in both grams and ounces
- Provide when_to_add instructions (to oils, to lye water, at trace)
- Include preparation requirements (disperse in water, melt first, grind finely)
- Display mixing tips for optimal incorporation
- Return safety warnings (accelerates trace, causes overheating, can be scratchy)

**Enhanced Recipe Calculation Request**
- Accept additives with amount levels: "light", "standard", "heavy", or numeric percentage
- Auto-calculate additive weights: `(batch_size_g × usage_percent) / 100`
- Return calculated amounts with usage_percentage and calculated_weight_g
- Include when_to_add instructions in recipe response
- Display applicable warnings for each additive
- Support essential oils with safe usage rate validation
- Support colorants with amount recommendations

**Usage Rate Database Schema**
- Store usage_rate_min_percent (e.g., 0.5 for salt, 1.0 for kaolin clay)
- Store usage_rate_max_percent (e.g., 1.0 for salt, 3.0 for honey)
- Store usage_rate_standard_percent (recommended amount)
- Store usage_rate_description ("1 tablespoon per pound of oils")
- Store when_to_add guidance (timing for incorporation)
- Store preparation_instructions (how to prepare additive)
- Store mixing_tips (best practices for even distribution)
- Store category (exfoliant, colorant, lather_booster, hardener, clay, botanical)

**Warning System**
- Flag accelerates_trace (honey, sugar, milk, lemongrass EO)
- Flag causes_overheating (honey, milk powder)
- Flag can_be_scratchy (ground botanicals, coffee grounds, salt scrubs)
- Flag turns_brown (most herbs except calendula)
- Check usage_percent > max_percent → return warning
- Display multiple warnings per additive when applicable

**Essential Oil Calculations**
- Support max_usage_rate_pct per essential oil (0.025% to 3%)
- Calculate safe amounts: `batch_size_g × (max_usage_rate_pct / 100)`
- Provide scent_profile descriptions
- Show blends_with recommendations
- Display warnings (fades quickly, can accelerate trace, skin sensitivity)
- Include note type (top/middle/base) for blending guidance

**Colorant Recommendations**
- Calculate amounts based on desired color intensity
- Support natural colorants (clays, botanicals, powders, infused oils)
- Provide color_range descriptions ("pale yellow to burnt orange")
- Include method instructions (infuse in oil, add to lye, add at trace)
- Display warnings (fades with time, scratchy texture, stains)
- Support botanical_name for proper identification

**Response Performance**
- Calculation endpoint responds in <50ms
- Database queries use indexed additive lookups
- Calculation formula: `(batch_size × usage_rate) / 100`
- Return rounded weights (1 decimal place)

**Data Integrity**
- Pre-populate database with 19 core additives from reference
- Include 45+ essential oils with CPSR-validated max rates
- Include natural colorants across 7 color families
- Mark confidence_level (high/medium/low) per research backing
- Flag verified_by_mga for empirically tested additives

## Visual Design

No visual mockups provided for this API-focused feature. Frontend integration to be specified separately.

## Existing Code to Leverage

**`app/api/v1/resources.py` - List Additives Endpoint**
- Pagination pattern (limit, offset, has_more)
- Search filtering (common_name, inci_name)
- Confidence filtering (high/medium/low)
- Verified filtering (verified_by_mga boolean)
- Sort ordering (common_name, confidence_level)
- Reuse this pattern for filtered additive discovery

**`app/models/additive.py` - Additive Database Model**
- Already has typical_usage_min_percent and typical_usage_max_percent
- Already has quality_effects as JSONB
- Already has confidence_level and verified_by_mga
- Already has safety_warnings as JSONB
- Extend this model with new fields: usage_rate_standard_percent, when_to_add, preparation_instructions, mixing_tips, category, accelerates_trace, causes_overheating, can_be_scratchy, turns_brown

**`app/schemas/resource.py` - Response Schemas**
- AdditiveListItem includes typical_usage ranges
- Pattern for including confidence and verification status
- Use similar structure for recommendation responses with calculated amounts

**Calculation Formula Pattern**
- Simple percentage calculation: `amount_g = (batch_size_g × usage_pct) / 100`
- Apply to all additives, essential oils, and colorants consistently
- Round to 1 decimal place for user-friendly display

**Database Seeding Pattern**
- Use existing seed_database.py pattern
- Load additives from `additives-usage-reference.json`
- Load essential oils from `essential-oils-usage-reference.json`
- Load colorants from `natural-colorants-reference.json`
- Mark data sources in confidence_level field

## Out of Scope

- Frontend UI for additive selection (API-only specification)
- Interactive additive search widget
- Visual color preview system
- Additive combination recommendations (which additives pair well)
- Seasonal additive suggestions
- Skin-type matching for additives
- Batch scaling interface (automatic adjustment when changing batch size)
- Additive inventory tracking
- Custom additive creation by users
- Advanced fragrance blending calculator with scent notes
- Additive cost calculations
- Supplier recommendations
