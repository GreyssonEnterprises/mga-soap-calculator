# Spec Shaper - Requirements Research Complete

**Timestamp:** 2025-11-01T14:45:30Z
**Task:** Document user requirements for Core Soap Calculation API
**Requestor:** Bob

## Response

Successfully documented comprehensive requirements from user answers to 22 clarifying questions.

### Key Decisions Captured

**API Design:**
- RESTful with GET and POST endpoints
- JWT authentication from Phase 1
- Versioned (/api/v1/) from the start
- Single recipe per request (Phase 1 scope)

**Calculation Capabilities:**
- Dual lye support (NaOH + KOH simultaneously)
- Three water calculation methods (% of oils, lye concentration, water:lye ratio)
- 1 decimal precision throughout
- Fixed temperature assumptions (85-100°F oils, 70°F room)

**Additive Handling:**
- Custom additives accepted with warnings
- Effects fixed from research data (agent-os/research/soap-additive-effects.md)
- Safety combination warnings included
- Calculate excluding unknowns, inform user

**Output Completeness:**
- All quality metrics required (Hardness, Cleansing, Conditioning, Bubbly, Creamy, Longevity, Stability)
- Full fatty acid profiles (8 fatty acids)
- INS and Iodine values included
- Sat:Unsat ratio calculated
- Numeric values only (no text recommendations)

**Validation Strategy:**
- Strict 100% oil total requirement (no tolerance)
- Unknown ingredients excluded with warnings
- Error/warning split as specified (errors block, warnings inform)

### Reference Materials

Located at: `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/reference`

**Contents:**
1. **soapcalcnet-analysis.md** - Competitor analysis identifying gaps
2. **View_Print Recipe.html** - Complete SoapCalc.net output example showing:
   - Multi-unit display (pounds/ounces/grams)
   - All quality metrics with suggested ranges
   - Full fatty acid breakdown
   - Water calculations (all three methods)
   - Lye calculations
   - Recipe: 40% Avocado, 30% Babassu, 30% Coconut Oil
3. **View_Print Recipe_files/** - CSS and image assets from SoapCalc

**Critical Competitive Insight:**
- SoapCalc.net CANNOT handle custom additives with quality effects
- Our additive effect calculations are unique differentiator
- Must match SoapCalc's output completeness while adding additive intelligence

### Implementation Clarity

All questions answered. Zero ambiguities remaining. Ready for detailed spec writing in /write-spec phase.

### Critical Requirements

1. **Database persistence** (GET endpoint requirement)
2. **Multi-lye chemistry support** (NaOH + KOH combinations)
3. **Flexible input normalization** (weight OR percentage for oils)
4. **Comprehensive output generation** (match SoapCalc completeness + additive effects)
5. **Warning system implementation** (non-blocking validation)
6. **Custom additive differentiation** (competitive advantage vs SoapCalc)

### Calculation Requirements Identified

From SoapCalc reference analysis:

**Core Formulas:**
- Lye weight = SAP × oil weight × (1 - superfat)
- Water weight (three methods supported)
- Hardness = Lauric + Myristic + Palmitic + Stearic
- Cleansing = Lauric + Myristic
- Conditioning = Oleic + Linoleic + Linolenic + Ricinoleic
- Bubbly = Lauric + Myristic + Ricinoleic
- Creamy = Palmitic + Stearic + Ricinoleic
- INS = SAP value - Iodine value
- Sat:Unsat ratio calculation

**Plus Additive Effects:**
- Modify quality metrics based on research data
- Issue warnings for problematic combinations

### Data Model Needs

**Recipe Schema:**
- UUID, user_id, oils (flexible input), lye types, water method, additives, results, timestamp

**Oil Library:**
- Oil ID, name, INCI name, SAP (NaOH), SAP (KOH), fatty acid profile (8 acids)

**Additive Library:**
- Additive ID, name, INCI name, effect modifiers, warnings, incompatibilities

### Next Steps for Spec Writing

Phase 3 ready to begin. User should be notified that requirements research is complete.

Spec writer will need:
1. Detailed API schemas (request/response matching SoapCalc completeness)
2. Database models (recipes, oils, additives)
3. Calculation algorithms (all formulas specified)
4. Error/warning codes
5. Example requests/responses
6. JWT auth flow
7. Endpoint specifications
8. Validation rules
9. INCI name handling

## Metadata
- Status: Complete
- Confidence: High
- Follow-up: No - proceed to Phase 3 (user notification)
- Files Created:
  - `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/agent-os/specs/2025-11-01-core-calculation-api/requirements-notes.md`
  - This agent response file
