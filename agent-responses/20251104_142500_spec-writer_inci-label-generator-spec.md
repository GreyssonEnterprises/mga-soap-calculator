# Spec Writer - INCI Label Generator Specification

**Timestamp:** 2025-11-04T14:25:00Z
**Task:** Create comprehensive spec-kit specification for INCI Label Generator feature
**Requestor:** User (Grimm)

## Response

### Specification Created

**Location:** `.specify/specs/003-inci-label-generator/spec.md`

Successfully created a complete spec-kit specification for the INCI Label Generator feature based on the user feedback documentation. The specification is implementation-ready and follows spec-kit methodology.

### Key Specification Components

**User Stories (2)**
1. Generate INCI labels in multiple formats for regional compliance
2. Labels sorted by percentage for regulatory requirements

**Functional Requirements (6)**
1. **Multiple Label Format Support**: Three variants (raw INCI, saponified INCI, common names) with format-specific lye handling
2. **Percentage-Based Sorting**: All ingredients sorted by total batch percentage (regulatory requirement)
3. **Saponified INCI Naming Logic**: Sodium/Potassium salt naming patterns with 37 pre-mapped terms
4. **API Endpoint Design**: `/api/v1/recipes/{recipe_id}/inci-label` following FastAPI patterns
5. **Edge Case Handling**: Missing INCI names, trace ingredients, multiple lye types, essential vs. fragrance oils
6. **Output Format Options**: Comma-separated and line-by-line formats for copy-paste convenience

**Existing Code Leveraged (5 areas)**
1. Resource endpoint pattern from `resources.py` (async FastAPI router structure)
2. Oil model structure from `oil.py` (extend with saponified_inci_name field)
3. Schema patterns from `resource.py` (Pydantic BaseModel approach)
4. Database query patterns (SQLAlchemy async select patterns)
5. Calculation logic reference (percentage calculations from existing recipe data)

**Out of Scope (10 items)**
- Frontend implementation
- PDF export
- Multi-language translations
- Allergen detection
- Advanced regulatory validation
- Label styling/formatting
- Barcode generation
- Custom templates
- Version tracking
- Approval workflows

### Technical Analysis

**Database Changes Required**
- Add `saponified_inci_name` String(200) field to oils table
- Populate with 37 known values from saponified-inci-terms.json
- Generate fallback values for remaining oils using pattern: "Sodium [OilName]ate"

**Critical Implementation Details**
1. **Sorting Algorithm**: Must calculate each ingredient's percentage of TOTAL batch weight (not just oil weight)
2. **Lye Handling**: Raw format includes lye as separate ingredient; saponified format does NOT
3. **Water Percentage**: Calculate from actual water weight in recipe, not water-to-lye ratio
4. **Mixed Lye**: List both sodium and potassium salts when recipe uses dual-lye formulation
5. **Performance Target**: <100ms response time for real-time label preview

**API Response Structure**
```json
{
  "raw_inci": "Water, Olea Europaea Fruit Oil, Cocos Nucifera Oil, Sodium Hydroxide, ...",
  "saponified_inci": "Water, Sodium Olivate, Sodium Cocoate, ...",
  "common_names": "Water, Olive Oil, Coconut Oil, Lye, ...",
  "ingredients_breakdown": [
    {
      "name": "Water",
      "inci_raw": "Water",
      "inci_saponified": "Water",
      "percentage": 38.2
    },
    ...
  ]
}
```

### Reference Data Analysis

**INCI Reference Database**: 339 entries covering oils, additives, essential oils, colorants, and specialty ingredients

**Saponified Terms**: 37 oils with official saponified INCI names:
- Pattern consistency: "Sodium [Base]ate" for NaOH soaps
- Special case: Castor Oil has alternative naming
- Crisco Shortening maps to two salts: "Sodium Soybeanate, Sodium Palmate"
- Complete coverage of common soap-making oils

**Source Material Quality**
- Well-researched feature request with detailed implementation guidance
- Clear distinction between U.S. and European labeling conventions
- Regulatory context provided (percentage-based sorting requirement)
- Complete use cases with example recipes
- Edge cases documented (mixed lye, liquid soap, multiple additives)

### Implementation Priority Justification

**Priority: HIGH** (upgraded from medium in original request)

**Reasoning:**
1. **Professional Differentiator**: Most soap calculators lack this feature
2. **Regulatory Compliance**: Solves real legal requirement (percentage sorting)
3. **Time Savings**: Eliminates manual INCI lookup and label formatting
4. **Subscription Value**: Premium feature justifying paid tier
5. **Low Implementation Complexity**: Straightforward text generation from existing data
6. **Immediate User Value**: Requested by professional soap makers
7. **Data Ready**: Reference database complete and validated

### Success Criteria

**Functional Success**
- Generate all three label formats correctly
- All ingredients sorted by percentage (descending)
- Saponified names match INCI standards
- Edge cases handled gracefully (missing data, trace ingredients, mixed lye)

**Performance Success**
- Response time <100ms (fast enough for real-time preview)
- Accurate percentage calculations to 1 decimal place
- Copy-paste ready formatting (no cleanup needed)

**Quality Success**
- TDD implementation with comprehensive test coverage
- API documentation auto-generated from schemas
- Professional presentation meeting labeling standards

### Specification Quality Validation

**Completeness Check**
- ✅ Goal statement clear and measurable
- ✅ User stories with acceptance criteria
- ✅ Specific requirements (6 detailed areas)
- ✅ Existing code to leverage identified (5 patterns)
- ✅ Out of scope clearly defined (10 items)
- ✅ No actual code in specification
- ✅ Concise sections with essential information only

**Implementation Readiness**
- ✅ Database schema changes specified
- ✅ API endpoint design detailed
- ✅ Response format documented
- ✅ Edge cases enumerated
- ✅ Performance targets defined
- ✅ Reference data sources identified
- ✅ Existing patterns to follow cited

**Spec-Kit Compliance**
- ✅ Follows spec-kit template structure exactly
- ✅ No additional sections added
- ✅ Sections kept short and skimmable
- ✅ Technical approach described without implementation code
- ✅ Ready for spec-panel review via /sc:spec-panel

## Metadata

- **Status**: Complete
- **Confidence**: High
- **Follow-up**: Ready for /sc:spec-panel review and implementation
- **Files Created**:
  - `.specify/specs/003-inci-label-generator/spec.md`
  - `agent-responses/20251104_142500_spec-writer_inci-label-generator-spec.md`
- **Reference Materials Used**:
  - `working/user-feedback/inci-name-options-feature-request/inci-name-options-feature-request.md`
  - `working/user-feedback/inci-name-options-feature-request/inci-reference-database.json`
  - `working/user-feedback/inci-name-options-feature-request/saponified-inci-terms.json`
  - `app/api/v1/resources.py` (pattern reference)
  - `app/models/oil.py` (schema reference)
  - `app/schemas/resource.py` (response schema patterns)

## Next Steps

1. **Review**: Run `/sc:spec-panel` to get multi-expert specification review
2. **Refine**: Incorporate spec-panel feedback if needed
3. **Implement**: Begin TDD implementation following specification
4. **Test**: Comprehensive test coverage per coding-protocols
5. **Document**: API documentation auto-generated from schemas
6. **Deploy**: Container deployment via existing Ansible playbooks
