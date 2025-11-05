# Specification: INCI Label Generator

## Goal
Provide professional soap makers with copy-ready INCI ingredient labels in multiple formats (raw oils, saponified salts, common names) with regulatory-compliant percentage-based sorting.

## User Stories

- As a professional soap maker, I want to generate INCI labels in multiple formats so that I can comply with different regional labeling requirements
- As a product developer, I want labels sorted by percentage so that my product labels meet regulatory requirements

## Specific Requirements

**Multiple Label Format Support**
- Generate three format variants: raw INCI (pre-saponification), saponified INCI (post-saponification), and common names
- Raw format includes lye as separate ingredient (oils not yet chemically transformed)
- Saponified format excludes lye (incorporated into sodium/potassium salts)
- Common names format uses everyday ingredient names for consumer clarity
- Each format must be copy-paste ready with proper comma separation

**Percentage-Based Sorting (Regulatory Requirement)**
- Sort ALL ingredients by percentage in descending order (highest to lowest)
- Include oils, water, lye, additives, fragrances, colorants in single sorted list
- Calculate each ingredient's percentage of total batch weight (oils + water + lye + additives)
- Water percentage must reflect actual water weight in final batch
- Lye percentage calculated from total lye weight (NaOH + KOH)

**Saponified INCI Naming Logic**
- Add `saponified_inci_name` field to oils table for NaOH soap salts
- Pattern: "Sodium [OilName]ate" (e.g., Coconut Oil → Sodium Cocoate)
- Handle special cases: Castor Oil → "Sodium Castorate or Sodium Ricinoleate"
- Support KOH soap salts: "Potassium [OilName]ate" for liquid soap
- Mixed lye soaps list both sodium and potassium salts proportionally
- Populate from provided saponified-inci-terms.json reference data (37 oils)

**API Endpoint Design**
- New GET endpoint: `/api/v1/recipes/{recipe_id}/inci-label`
- Return three label formats: raw_inci, saponified_inci, common_names
- Include ingredients_breakdown array with percentages for debugging/verification
- Fast response time (<100ms) suitable for real-time label preview
- Follow existing FastAPI patterns from resources.py endpoint structure

**Edge Case Handling**
- Missing INCI names: fallback to common name
- Trace ingredients (<1%): still include in sorted list
- Additives without INCI names: use common name in all formats
- Essential oils vs. fragrance oils: "Essential Oil" vs. "Fragrance"
- Multiple lye types: list both "Sodium Hydroxide, Potassium Hydroxide"
- Generic saponified term generation for oils without reference data

**Output Format Options**
- Default: comma-separated single-line format
- Optional: line-by-line format for label printing
- Maintain professional presentation with proper capitalization
- No trailing punctuation (labels end cleanly without periods)
- Clear distinction between format types in response structure

## Visual Design

No visual mockups provided - this is a pure API feature. Frontend implementation will add format selector dropdown/toggle.

## Existing Code to Leverage

**Resource Endpoint Pattern (app/api/v1/resources.py)**
- Follow async FastAPI router structure with APIRouter prefix="/api/v1"
- Use AsyncSession database dependency pattern from get_db
- Apply consistent response schema patterns with BaseModel
- Leverage existing search and filtering query patterns
- Reuse pagination metadata approach for consistency

**Oil Model Structure (app/models/oil.py)**
- Extend existing Oil model with new saponified_inci_name field (String(200))
- Maintain JSONB pattern for structured data (fatty_acids, quality_contributions)
- Follow mapped_column type hints and nullable patterns
- Use server_default timestamps pattern for created_at/updated_at
- Keep consistent comment style for database field documentation

**Schema Pattern (app/schemas/resource.py)**
- Create new inci_label.py schema file following resource.py structure
- Use Pydantic BaseModel with Field descriptions
- Apply from_attributes Config for ORM compatibility
- Follow typing patterns: Dict[str, float], List, Optional
- Maintain descriptive Field documentation for API docs

**Database Query Patterns**
- Use SQLAlchemy select() async patterns from resources.py
- Apply async/await for database operations consistently
- Follow relationship loading patterns if recipe relationships added
- Maintain transaction safety with AsyncSession context

**Calculation Logic Reference**
- Percentage calculations follow existing total batch weight pattern
- Oil percentages already calculated in recipe data structure
- Water and lye weights available in recipe calculation results
- Additive percentages calculated as (additive_weight / total_batch_weight) * 100

## Out of Scope

- Frontend implementation and UI design (API-only specification)
- PDF label export or printable formats
- Multi-language INCI translations beyond English
- Allergen warning detection or highlighting
- Regulatory compliance validation beyond sorting
- Label text wrapping or formatting optimization
- Barcode generation for product labels
- Custom label templates or styling
- Historical label version tracking
- Label approval workflow features
