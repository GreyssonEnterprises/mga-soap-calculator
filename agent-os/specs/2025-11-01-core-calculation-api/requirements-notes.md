# Requirements Research Notes

**Date:** 2025-11-01
**Feature:** Core Soap Calculation API
**Researcher:** Spec Shaper Agent

## User Responses Summary

### API Design & Architecture Decisions

**Endpoint Structure:**
- Primary: `POST /api/v1/calculate` - Create new calculation
- Secondary: `GET /api/v1/calculate/{id}` - Retrieve saved calculations
- Rationale: Save successful recipes for recreation at different batch sizes

**Authentication:**
- JWT from Phase 1
- Rationale: Customer-facing goal requires proper auth from the start

**Request Payload Flexibility:**
- Oils: Support both weight (grams) AND percentage
- Water: Calculate from lye concentration
- Rationale: Professional soap makers use different input methods

**Batch Operations:**
- Single recipe per request in Phase 1
- Future: May add batch support

**Versioning:**
- `/api/v1/` structure from day one
- Rationale: Avoid breaking changes in future

### Calculation Scope & Precision Decisions

**Lye Type Support:**
- MUST support both NaOH and KOH
- Some recipes use both lye types simultaneously
- Critical requirement for MGA's actual recipes

**Water Calculation Methods:**
- Support ALL THREE: water as % of oils, lye concentration, water:lye ratio
- Rationale: Different soap makers use different conventions

**Temperature Assumptions:**
- Oil temperature: 85-100°F
- Room temperature: ~70°F (21°C)
- No user input required for Phase 1

**Precision:**
- 1 decimal place for weights (grams)
- 1 decimal place for percentages/metrics
- Rationale: Professional precision without over-engineering

### Additive Implementation Decisions

**Input Flexibility:**
- Accept additives by percentage OR weight
- Rationale: Match oil input flexibility

**Validation Approach:**
- Accept custom (unknown) additives
- Calculate WITHOUT custom additives
- Return WARNING for excluded additives
- Rationale: Don't block innovation, but be honest about limitations

**Effect Modifiers:**
- FIXED based on research data (agent-os/research/soap-additive-effects.md)
- Future: May update research basis
- No user overrides in Phase 1

**Safety Warnings:**
- Calculate effects for all additives
- Issue warnings for problematic combinations
- Rationale: Inform users without blocking calculations

### Output Requirements Decisions

**Comprehensive Response:**
- Include INS and Iodine values in Phase 1
- Return ALL quality metrics (Hardness, Cleansing, Conditioning, Bubbly, Creamy, Longevity, Stability)
- Full fatty acid profile in every response
- Rationale: Complete professional-grade output

**Simplicity:**
- Numeric values only
- NO textual usage recommendations
- Rationale: Let soap makers interpret data themselves

### Error Handling & Validation Decisions

**Error vs Warning Split:**
- **Errors** (block calculation): Invalid oil IDs, negative weights, superfat > 100%, missing required fields
- **Warnings** (calculate with flag): Superfat < 0%, superfat > 20%, extreme values, problematic combos
- Approved as specified

**Unknown Ingredients:**
- Proceed with calculation
- Exclude unknown items
- Return warning listing excluded items
- Rationale: Partial success better than total failure

**Percentage Strictness:**
- Oil percentages MUST sum to exactly 100%
- NO tolerance for 99-101%
- Rationale: Chemical precision requirements

## Reference Materials Found

Located at: `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/reference`

### Files Analyzed:

**1. soapcalcnet-analysis.md**
- Competitor analysis of SoapCalc.net
- Features liked: INCI name display (both Latin and common names), soap bar quality metrics
- Gap identified: Cannot add custom non-fat additives and see effects on bar quality
- **CRITICAL**: Our API must solve this gap - custom additive support is a differentiator

**2. View_Print Recipe.html**
- Actual SoapCalc.net recipe output (saved HTML)
- Recipe example: 40% Avocado Oil, 30% Babassu Oil, 30% Coconut Oil
- Shows complete output structure including:
  - Oil weights in pounds, ounces, and grams
  - Lye (NaOH) calculations
  - Water calculations (multiple methods shown: water as % of oils, lye concentration, water:lye ratio)
  - Quality metrics: Hardness (58), Cleansing (41), Conditioning (34), Bubbly (41), Creamy (17)
  - Iodine value (40) and INS value (186)
  - Full fatty acid profile (Lauric 29%, Myristic 12%, Palmitic 14%, Stearic 3%, Ricinoleic 0%, Oleic 29%, Linoleic 5%, Linolenic 0%)
  - Sat:Unsat ratio (63:37)
  - Fragrance calculations

**3. View_Print Recipe_files/**
- Supporting assets (CSS, images) from SoapCalc.net output
- Contains column.gif for bar graphs
- CSS files: ViewRecipeV4.css, Graph.css

### Key Insights from Reference Materials:

**Output Format Reference:**
- SoapCalc provides comprehensive numeric output - we should match or exceed
- Three-unit display (pounds/ounces/grams) - we'll support grams primarily, can add others later
- Quality metrics with suggested ranges shown - we should include ranges in documentation
- Fatty acid breakdown is essential professional feature

**Competitive Advantage:**
- SoapCalc CANNOT handle custom additives with quality impact
- Our additive effect calculations will be unique value proposition
- Research-based additive effects (from agent-os/research/soap-additive-effects.md) is our differentiator

**Validation Standards:**
- SoapCalc example shows oils totaling exactly 100%
- Quality metrics calculated from fatty acid profiles
- INS and Iodine are standard industry calculations

## Key Architectural Decisions

1. **Database Storage Required:** GET endpoint means calculations must be persisted
2. **Multi-Lye Support:** Schema must handle NaOH + KOH combinations
3. **Flexible Input:** API must normalize weight/percentage inputs
4. **Comprehensive Output:** Every response includes full data set (match SoapCalc completeness)
5. **Warning System:** Non-blocking validation with informative warnings
6. **Custom Additive Handling:** Core differentiator vs SoapCalc.net

## Implementation Priorities

**Must Have (Phase 1):**
- JWT authentication
- Both NaOH and KOH support (including dual-lye recipes)
- All three water calculation methods
- Full quality metrics + fatty acid profiles (match SoapCalc output)
- Custom additive warnings (competitive advantage)
- Calculation persistence (for GET endpoint)
- INS and Iodine calculations
- Sat:Unsat ratio calculation

**Future Enhancements:**
- Batch calculation support
- User override of additive effects
- Textual recommendations
- Temperature input options
- Multi-unit output (pounds/ounces/grams)
- Fragrance oil calculations

## Data Model Implications

**Recipe Storage Schema Needs:**
- Recipe ID (UUID)
- Oils (flexible: weight OR percentage)
- Lye type(s) (NaOH, KOH, or both with individual weights)
- Water calculation method used
- Additives (with exclusion warnings)
- Calculated results (all metrics)
- Timestamp
- User ID (for JWT auth)

**Oil Library Schema:**
- Oil ID
- Name (common + INCI)
- SAP value (for NaOH)
- SAP value (for KOH)
- Fatty acid profile (Lauric, Myristic, Palmitic, Stearic, Ricinoleic, Oleic, Linoleic, Linolenic)

**Additive Library Schema:**
- Additive ID
- Name (common + INCI)
- Effect modifiers (from research)
- Validation status (verified/unverified)
- Safety warnings
- Combination incompatibilities

## Calculation Requirements

**Core Calculations (from SoapCalc reference):**
1. Lye weight calculation (SAP value × oil weight × (1 - superfat))
2. Water weight (from user's chosen method: % of oils, lye concentration, or water:lye ratio)
3. Quality metrics from fatty acid profiles:
   - Hardness = Lauric + Myristic + Palmitic + Stearic
   - Cleansing = Lauric + Myristic
   - Conditioning = Oleic + Linoleic + Linolenic + Ricinoleic
   - Bubbly = Lauric + Myristic + Ricinoleic
   - Creamy = Palmitic + Stearic + Ricinoleic
4. Iodine value calculation (industry standard formula)
5. INS value calculation (SAP value - Iodine value)
6. Sat:Unsat ratio (saturated vs unsaturated fatty acids)

**Additive Effect Calculations:**
- Modify base quality metrics based on additive effects
- Reference: agent-os/research/soap-additive-effects.md
- Exclude unknown additives with warnings

## Technical Constraints

- Precision: 1 decimal place throughout
- Validation: Strict 100% oil total
- Temperature: Hardcoded assumptions (85-100°F oils, 70°F room)
- Effects: Fixed from research (no user overrides)
- Authentication: JWT required from Phase 1

## Competitive Analysis Summary

**SoapCalc.net Strengths:**
- Comprehensive output format (our benchmark)
- Multiple unit systems (pounds/ounces/grams)
- Visual graphs (nice-to-have for future)
- INCI name support (we should include)

**SoapCalc.net Weaknesses (Our Opportunities):**
- NO custom additive effect calculations (our differentiator)
- Limited API access (we're API-first)
- No authentication/saving (we have JWT + persistence)

## Open Questions Resolved

All 22 questions answered. No remaining ambiguities for spec writing phase.

## Next Steps for /write-spec

1. Design detailed API schema (request/response structures matching SoapCalc completeness)
2. Define database models (recipes, oils, additives, calculations)
3. Specify calculation algorithms:
   - Saponification calculations (NaOH + KOH)
   - Water calculations (all three methods)
   - Quality metric formulas (from fatty acid profiles)
   - INS and Iodine calculations
   - Additive effect modifiers
4. Document error codes and warning messages
5. Create example requests/responses (reference SoapCalc output format)
6. Define authentication flow (JWT implementation)
7. Specify endpoint behavior (POST create, GET retrieve)
8. Document calculation precision rules (1 decimal place)
9. Define validation rules (100% oil total, superfat ranges)
10. Specify INCI name handling
