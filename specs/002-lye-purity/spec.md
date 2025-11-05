# Feature Specification: KOH/NaOH Purity Support

**Feature Branch**: `002-lye-purity`
**Created**: 2025-11-04
**Status**: Ready for Implementation
**Input**: User feedback document: `working/user-feedback/koh-purity-feature-request.md`
**Safety Classification**: CRITICAL - Incorrect lye calculations can cause chemical burns

## ⚠️ BREAKING CHANGE NOTICE

**This feature introduces a BREAKING CHANGE for existing KOH users:**

- **Previous behavior**: API defaulted to 100% pure KOH for all calculations
- **New behavior**: API defaults to 90% pure KOH (real-world commercial grade)
- **Impact**: Existing API clients will receive 30% more KOH by default unless they explicitly pass `koh_purity: 100`
- **Risk**: Over-lye soap (chemical burn hazard) if existing users don't update their API calls
- **Migration Required**: All existing KOH users MUST either:
  1. Explicitly pass `koh_purity: 100` to maintain previous calculations, OR
  2. Update their recipes to account for 90% default if using commercial KOH

**Recommended API Version Bump**: v1 → v2 to clearly signal breaking change

**Deprecation Period Recommended**: Consider 30-day warning period where API returns deprecation warning headers for requests omitting `koh_purity` parameter.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Liquid Soap Maker Uses Commercial 90% KOH (Priority: P1)

Shale (MGA Automotive liquid soap production) purchases commercial-grade KOH which is 90% pure due to moisture absorption. She needs the API to calculate the correct amount of 90% pure KOH to use in her recipe, not the amount of pure KOH. Currently she must manually adjust API results by dividing by 0.90, which is error-prone and time-consuming.

**Why this priority**: This is a SAFETY-CRITICAL calculation. Using the wrong amount of lye results in either caustic soap (chemical burn risk) or soft soap (won't saponify properly). 90% KOH purity is the industry standard for liquid soap making, affecting the majority of liquid soap use cases.

**Independent Test**: Can be fully tested by submitting a recipe with `koh_purity: 90` parameter and verifying the returned KOH weight matches manual calculation (pure_koh_needed / 0.90). Delivers immediate safety and accuracy value for commercial KOH users without requiring any other changes.

**Acceptance Scenarios**:

1. **Given** a recipe requiring 117.1g pure KOH with 90% KOH purity specified, **When** API calculates lye requirements, **Then** returns `koh_weight_g: 130.1` (117.1 ÷ 0.90) and `pure_koh_equivalent_g: 117.1` in response

2. **Given** the same recipe without `koh_purity` field (omitted), **When** API calculates lye requirements, **Then** returns `koh_weight_g: 130.1` and `koh_purity: 90` in response (**CHANGED: now defaults to 90% for KOH**)

3. **Given** a recipe with 700g oils (70% olive, 20% castor, 10% coconut) using 90% KOH/10% NaOH mix with 1% superfat and 90% KOH purity, **When** API calculates, **Then** returns KOH weight within 0.5g of expected 130.1g and NaOH weight within 0.5g of expected 18.6g

---

### User Story 2 - Validation Prevents Dangerous Purity Values (Priority: P1)

Shale accidentally enters `koh_purity: 9` instead of `90` when creating a recipe via API. The system must catch this error before returning dangerous calculation results that could lead to severe chemical burns.

**Why this priority**: SAFETY-CRITICAL validation. Typos or incorrect purity values result in catastrophically wrong lye amounts. This validation is as important as the calculation itself.

**Independent Test**: Can be fully tested by submitting requests with invalid purity values (0, 49, 101, 150, negative numbers) and verifying appropriate 400 Bad Request errors are returned with clear explanations. Delivers immediate safety value by preventing dangerous calculations.

**Acceptance Scenarios**:

1. **Given** a recipe with `koh_purity: 49`, **When** API validates request, **Then** returns 400 Bad Request with error message "KOH purity must be between 50% and 100%. Received: 49%"

2. **Given** a recipe with `koh_purity: 101`, **When** API validates request, **Then** returns 400 Bad Request with error message "KOH purity cannot exceed 100%. Received: 101%"

3. **Given** a recipe with `koh_purity: 0`, **When** API validates request, **Then** returns 400 Bad Request with error message "KOH purity must be between 50% and 100%. Received: 0%"

4. **Given** a recipe with `naoh_purity: -5`, **When** API validates request, **Then** returns 400 Bad Request with error message "NaOH purity must be between 50% and 100%. Received: -5%"

---

### User Story 3 - Warning for Unusual Purity Values (Priority: P2)

Shale enters `koh_purity: 75` which is technically valid but unusual for commercial KOH. The API should process the calculation correctly but include a warning that this purity level is outside the typical commercial range.

**Why this priority**: Important for user education and error detection (user may have made a mistake), but not blocking for core functionality. Warnings improve safety without preventing valid edge cases.

**Independent Test**: Can be tested by submitting recipes with purity values in warning zones (50-84%, 96-100%) and verifying warning messages are included in response metadata. Delivers educational value and helps catch potential user errors.

**Acceptance Scenarios**:

1. **Given** a recipe with `koh_purity: 75`, **When** API calculates lye requirements, **Then** returns correct calculations AND includes warning in response: "Unusual KOH purity detected (75%). Commercial KOH is typically 85-95% pure. Verify this value is correct."

2. **Given** a recipe with `koh_purity: 98`, **When** API calculates lye requirements, **Then** returns correct calculations AND includes warning: "High KOH purity detected (98%). Commercial KOH is typically 85-95% pure. This may indicate laboratory-grade KOH."

3. **Given** a recipe with `koh_purity: 90` (typical commercial), **When** API calculates, **Then** returns calculations WITHOUT any warnings (90% is within expected range)

---

### User Story 4 - Mixed Lye Purity in Same Recipe (Priority: P2)

Shale creates a dual-lye recipe using 90% pure KOH and 98% pure NaOH in the same batch. Each lye type needs independent purity adjustment in the calculation.

**Why this priority**: Important for professional soap makers who use mixed lye formulations with different purity grades, but less common than single-lye recipes. Demonstrates complete purity handling.

**Independent Test**: Can be tested by submitting recipe with different purity values for KOH and NaOH, verifying each calculation is adjusted independently. Delivers advanced functionality for professional users.

**Acceptance Scenarios**:

1. **Given** a recipe with 90% KOH/10% NaOH split, `koh_purity: 90`, `naoh_purity: 98`, **When** API calculates, **Then** returns KOH weight adjusted by 0.90 divisor AND NaOH weight adjusted by 0.98 divisor independently

2. **Given** a recipe with only KOH (100% KOH/0% NaOH) and `koh_purity: 85`, **When** API calculates, **Then** returns only KOH weight adjusted for 85% purity, no NaOH calculation

3. **Given** a recipe with mixed lye and `koh_purity: 90` but `naoh_purity` omitted, **When** API calculates, **Then** applies 90% purity adjustment to KOH and assumes 100% purity (default) for NaOH

---

### User Story 5 - Response Schema Clearly Shows Purity Calculations (Priority: P3)

Shale reviews API response after calculation and needs to understand both the commercial KOH amount to weigh out AND the pure KOH equivalent for her records and quality control documentation.

**Why this priority**: Important for transparency and user confidence in calculations, but core calculation (P1) is more critical. This enhances usability without changing functionality.

**Independent Test**: Can be tested by verifying response schema includes all purity-related fields: actual weights, purity percentages used, and pure equivalents. Delivers documentation and verification value.

**Acceptance Scenarios**:

1. **Given** a recipe with 90% KOH purity, **When** API returns response, **Then** includes fields: `koh_weight_g` (actual amount to use), `koh_purity` (percentage used), `pure_koh_equivalent_g` (theoretical pure amount)

2. **Given** a recipe with mixed lye purities, **When** API returns response, **Then** includes separate purity and equivalent fields for both KOH and NaOH: `koh_purity`, `naoh_purity`, `pure_koh_equivalent_g`, `pure_naoh_equivalent_g`

3. **Given** a recipe with default 90% KOH purity, **When** API returns response, **Then** includes purity field showing 90% and equivalent values showing adjusted calculations (**CHANGED: reflects new 90% default**)

---

### Edge Cases

- **What happens when user specifies 100% purity explicitly vs. omitting purity field?** For KOH: explicit 100% gives 100% calculations, omitting gives 90% default (BREAKING CHANGE). For NaOH: both produce 100% (unchanged).

- **How does system handle purity values with high decimal precision (e.g., 89.7234%)?** Accept up to 2 decimal places, round for display but maintain precision in calculations. (FINAL DECISION: Accept 2 decimals, display 1)

- **What if both KOH and NaOH purity are at warning thresholds?** Include separate warnings for each in response warnings array.

- **How does purity affect cost calculations?** Commercial KOH weight (adjusted for purity) should be used for cost calculations, not pure equivalent. (FINAL DECISION: Only show commercial cost)

- **What if user updates existing recipe to add purity parameter?** Recipe version increments, new calculation with purity adjustment stored while preserving original recipe with assumed purity flag. (FINAL DECISION: Tag existing recipes with "assumed 100% purity" metadata)

- **How does system handle very low superfat (0-1%) with purity adjustments?** Calculation proceeds normally but may trigger separate superfat warning if combined effect approaches 0% safety margin.

- **What happens with extreme batch scaling (1000x) combined with purity adjustment?** Both scaling and purity adjustment apply multiplicatively, maintain precision throughout calculation chain.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept optional `koh_purity` parameter as decimal percentage (50.0-100.0) in lye configuration section of recipe request
- **FR-002**: System MUST accept optional `naoh_purity` parameter as decimal percentage (50.0-100.0) in lye configuration section of recipe request
- **FR-003**: System MUST default to 90% purity for KOH when purity parameter is omitted (**BREAKING CHANGE** from 100% default)
- **FR-003b**: System MUST default to 100% purity for NaOH when purity parameter is omitted (unchanged, backward compatible)
- **FR-004**: System MUST validate purity values are within 50.0-100.0 range and return 400 Bad Request with descriptive error for out-of-range values
- **FR-004b**: System MUST enforce hard cap of 100% purity maximum (FINAL DECISION: No >100% allowed)
- **FR-005**: System MUST calculate commercial lye weight using formula: `commercial_weight = pure_lye_needed / (purity / 100)`
- **FR-006**: System MUST apply purity adjustment independently to KOH and NaOH when both are present in recipe
- **FR-007**: System MUST include purity values used in calculation response (echo back for verification)
- **FR-008**: System MUST include pure lye equivalent values in response (`pure_koh_equivalent_g`, `pure_naoh_equivalent_g`)
- **FR-009**: System MUST generate warning when KOH purity is outside 85-95% range (typical commercial grade) - WARNING only, not error (FINAL DECISION)
- **FR-010**: System MUST generate warning when NaOH purity is below 98% (typical commercial grade is 98-100%) - WARNING only, not error (FINAL DECISION)
- **FR-011**: System MUST maintain calculation accuracy within 0.5g per 500g batch after purity adjustment
- **FR-012**: System MUST use commercial (purity-adjusted) lye weights for cost calculations, not pure equivalents (FINAL DECISION: Commercial cost only)
- **FR-013**: System MUST tag existing recipes (created before purity feature) with metadata flag indicating "assumed 100% purity" (FINAL DECISION: Migration strategy)
- **FR-014**: System MUST include purity parameters in stored recipes for future retrieval and version history
- **FR-015**: System MUST accept purity values up to 2 decimal places (e.g., 89.75%) for calculation precision (FINAL DECISION)
- **FR-016**: System MUST display purity values rounded to 1 decimal place in API responses (FINAL DECISION)

### Non-Functional Requirements

- **NFR-001**: SAFETY - Purity validation MUST NOT allow calculation to proceed with invalid or missing purity validation (fail-safe design)
- **NFR-002**: PERFORMANCE - Purity adjustment calculation overhead MUST NOT exceed 5ms per request
- **NFR-003**: BACKWARD COMPATIBILITY - **BREAKING CHANGE WARNING**: Existing API clients using KOH without explicit purity parameter will receive different results (30% more KOH). Migration guidance REQUIRED.
- **NFR-004**: DOCUMENTATION - API documentation mentions purity parameters but NOT prominently (FINAL DECISION: User chose minimal documentation)
- **NFR-005**: TESTING - TDD required with property-based tests for purity edge cases (49%, 50%, 50.01%, 99.99%, 100%, 100.01%)
- **NFR-006**: DATA INTEGRITY - Recipe versions with different purity values MUST be stored separately in version history
- **NFR-007**: API VERSIONING - Consider API version bump (v1 → v2) to signal breaking change in KOH default behavior

### Key Entities *(updated from MVP spec)*

- **Recipe** (enhanced): Add optional `koh_purity` (decimal 50.0-100.0, default **90.0** for KOH) and `naoh_purity` (decimal 50.0-100.0, default 100.0 for NaOH) fields to lye configuration
- **Calculation Result** (enhanced): Add `koh_purity`, `naoh_purity`, `pure_koh_equivalent_g`, `pure_naoh_equivalent_g` fields to lye section of response
- **Validation Rules** (new): Purity range constraints (50-100%), hard cap at 100% max, warning thresholds (KOH: 85-95%, NaOH: 98-100%), error messages for out-of-range values
- **Recipe Metadata** (new): Add `purity_assumed` boolean flag to indicate legacy recipes created before purity feature (FINAL DECISION: Migration strategy)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API correctly calculates 90% KOH purity adjustment within 0.5g for test recipe from user feedback (700g oils, expected 130.1g commercial KOH)
- **SC-002**: All purity values outside 50-100% range are rejected with 400 error (tested with boundary value testing: 49%, 49.9%, 50%, 100%, 100.1%, 101%)
- **SC-003**: Breaking change documented with migration guide for existing API users transitioning to 90% KOH default
- **SC-004**: Warning messages generated for 100% of requests with unusual purity values (tested with 75% KOH, 97% NaOH) - warnings only, not errors (FINAL DECISION)
- **SC-005**: Property-based tests validate purity calculation correctness for 1000+ random valid purity combinations (Hypothesis testing)
- **SC-006**: Response schema includes all required purity fields for recipe with 90% KOH: `koh_weight_g`, `koh_purity`, `pure_koh_equivalent_g`
- **SC-007**: Cost calculations use commercial lye weights only, not pure equivalents (FINAL DECISION verified)
- **SC-008**: Documentation mentions purity parameters in API reference but NOT as prominent callout (FINAL DECISION: Minimal user-facing docs)
- **SC-009**: Code coverage remains >90% with comprehensive purity validation and calculation tests
- **SC-010**: Zero safety incidents from incorrect purity calculations in 30-day production use (monitored via error tracking)
- **SC-011**: All existing recipes tagged with `purity_assumed: true` metadata flag during migration (FINAL DECISION: Migration strategy)
- **SC-012**: Purity values with 2 decimal precision accepted and calculated correctly, displayed with 1 decimal rounding (FINAL DECISION)
- **SC-013**: Purity values >100% rejected with clear error message enforcing 100% hard cap (FINAL DECISION)

## API Schema Changes

### Request Schema (Enhanced)

```json
{
  "oils": [
    {"name": "Olive Oil", "percentage": 70},
    {"name": "Castor Oil", "percentage": 20},
    {"name": "Coconut Oil", "percentage": 10}
  ],
  "lye": {
    "naoh_percent": 10,
    "koh_percent": 90,
    "koh_purity": 90,      // NEW: Optional, defaults to 90 (BREAKING CHANGE)
    "naoh_purity": 100     // NEW: Optional, defaults to 100 (unchanged)
  },
  "superfat_percent": 1,
  "water_lye_ratio": 3.0,
  "batch_size_g": 700
}
```

### Response Schema (Enhanced)

```json
{
  "recipe": {
    "lye": {
      "naoh_weight_g": 18.6,
      "koh_weight_g": 130.1,              // Commercial weight (adjusted)
      "total_lye_g": 148.7,
      "naoh_percent": 10,
      "koh_percent": 90,
      "koh_purity": 90,                    // NEW: Echo back purity used (default 90)
      "naoh_purity": 100,                  // NEW: Echo back purity used (default 100)
      "pure_koh_equivalent_g": 117.1,     // NEW: Theoretical pure amount
      "pure_naoh_equivalent_g": 18.6      // NEW: Theoretical pure amount
    },
    "warnings": [                           // NEW: Optional warnings array
      {
        "type": "unusual_purity",
        "message": "KOH purity of 75% is below typical commercial range (85-95%). Verify this value is correct."
      }
    ],
    "metadata": {
      "purity_assumed": false              // NEW: Migration tracking flag
    }
  }
}
```

### Validation Rules Schema

```python
# Pydantic model constraints
class LyeConfig(BaseModel):
    naoh_percent: float = Field(ge=0, le=100)
    koh_percent: float = Field(ge=0, le=100)
    koh_purity: Optional[float] = Field(
        default=90.0,  # CHANGED from 100.0 - BREAKING CHANGE
        ge=50.0,
        le=100.0,      # FINAL DECISION: Hard cap at 100%
        decimal_places=2  # FINAL DECISION: Accept 2 decimals
    )
    naoh_purity: Optional[float] = Field(
        default=100.0,  # Unchanged
        ge=50.0,
        le=100.0,
        decimal_places=2
    )

    @model_validator(mode='after')
    def validate_lye_percentages_sum_to_100(self) -> 'LyeConfig':
        if not math.isclose(self.naoh_percent + self.koh_percent, 100.0):
            raise ValueError("NaOH and KOH percentages must sum to 100")
        return self

    @model_validator(mode='after')
    def validate_purity_warnings(self) -> 'LyeConfig':
        # FINAL DECISION: Generate warnings (not errors) for unusual purity values
        # KOH typical range: 85-95%
        # NaOH typical range: 98-100%
        return self
```

## Calculation Formulas

### Current Formula (100% Pure Assumption)
```python
# Simplified current approach
pure_koh_needed = total_koh_for_saponification * (koh_percent / 100)
pure_naoh_needed = total_naoh_for_saponification * (naoh_percent / 100)
```

### Enhanced Formula (Purity Adjustment)
```python
# Step 1: Calculate pure lye requirements (unchanged)
pure_koh_needed = total_koh_for_saponification * (koh_percent / 100)
pure_naoh_needed = total_naoh_for_saponification * (naoh_percent / 100)

# Step 2: Adjust for purity to get commercial weights
koh_purity_decimal = koh_purity / 100  # Default: 90 -> 0.90 (BREAKING CHANGE)
naoh_purity_decimal = naoh_purity / 100  # Default: 100 -> 1.00 (unchanged)

commercial_koh_weight = pure_koh_needed / koh_purity_decimal
commercial_naoh_weight = pure_naoh_needed / naoh_purity_decimal

# Step 3: Total lye weight (commercial, what user actually weighs)
total_lye_weight = commercial_koh_weight + commercial_naoh_weight
```

### Validation Example
```python
# Test case from user feedback
oils = [
    {"name": "Olive Oil", "weight_g": 489},
    {"name": "Castor Oil", "weight_g": 140},
    {"name": "Coconut Oil", "weight_g": 70}
]
koh_percent = 90
naoh_percent = 10
superfat = 1
koh_purity = 90  # Now the default (BREAKING CHANGE)
naoh_purity = 100

# Expected results (from user feedback)
expected_pure_koh = 117.1  # g
expected_commercial_koh = 130.1  # g (117.1 / 0.90)
expected_naoh = 18.6  # g (already at 100% purity)

# Tolerance: within 0.5g per result
```

## Technical Architecture Notes

### Calculation Module Changes
- **File**: `app/core/saponification.py`
- **Function**: `calculate_lye_requirements()`
- **Changes**:
  - Add purity adjustment step after pure lye calculation, before returning results
  - **BREAKING CHANGE**: Default `koh_purity` parameter from 100.0 to 90.0
  - Maintain `naoh_purity` default at 100.0 (unchanged)
- **Backward Compatibility Impact**: **BREAKING** - existing KOH calculations will return 30% more lye unless clients explicitly pass `koh_purity: 100`

### Validation Module Changes
- **File**: `app/schemas/recipe.py`
- **Changes**:
  - Add `koh_purity` (default 90.0) and `naoh_purity` (default 100.0) fields to `LyeConfig` Pydantic model
  - Add validation constraints: 50.0-100.0 range, 100.0 hard cap, 2 decimal precision
- **Validators**:
  - Custom validator for warning generation (non-blocking, FINAL DECISION)
  - Error validator for >100% or <50% values
  - Decimal precision validator (accept 2, display 1, FINAL DECISION)

### Database Schema Changes
- **Table**: `recipes`
- **Changes**:
  - Add `koh_purity` column (DECIMAL(5,2), default **90.00** - BREAKING CHANGE)
  - Add `naoh_purity` column (DECIMAL(5,2), default 100.00)
  - Add `purity_assumed` column (BOOLEAN, default FALSE) for migration tracking (FINAL DECISION)
- **Migration**:
  - Alembic migration adds columns with new defaults
  - **CRITICAL**: Existing recipes get `purity_assumed: true` flag to indicate legacy 100% KOH assumption
  - New recipes get `purity_assumed: false` flag

### Warning System Implementation
- **Response Model**: Add optional `warnings` array to calculation response
- **Warning Types**: `unusual_purity`, `low_purity`, `high_purity`
- **Thresholds**:
  - KOH: warn if <85% or >95%
  - NaOH: warn if <98%
  - **FINAL DECISION**: Warnings only, never block calculations

### Testing Strategy
- **Unit Tests**: Test purity calculation formula in isolation with known values
- **Property-Based Tests**: Hypothesis tests for purity edge cases (boundaries, precision)
- **Integration Tests**: API endpoint tests with various purity combinations
- **Breaking Change Tests**: Verify existing API calls without `koh_purity` now return 90% default calculations
- **Migration Tests**: Verify legacy recipes tagged with `purity_assumed: true`
- **Safety Tests**: Verify dangerous purity values (0%, 200%, negative, >100%) are blocked
- **Precision Tests**: Verify 2 decimal input accepted, 1 decimal output displayed (FINAL DECISION)

### Performance Considerations
- **Overhead**: Purity adjustment is simple division, negligible performance impact (<1ms)
- **Database**: Indexed queries unaffected by additional columns
- **Caching**: No caching strategy changes needed

## Out of Scope (Explicitly NOT This Feature)

- **Multi-stage lye purity handling** (e.g., different purity for hot process vs. cold process) - Future enhancement
- **Automatic purity detection from supplier database** - Requires supplier integration (Phase 2+)
- **Purity recommendations based on soap type** (liquid vs. bar) - User education feature (Phase 3+)
- **Historical purity tracking per user** (e.g., "user typically uses 90% KOH") - User preference system (Phase 3+)
- **Purity adjustment for other ingredients** (water purity, oil purity) - Separate feature consideration
- **Conversion between KOH and NaOH with purity** - Advanced calculator feature (Phase 2+)
- **Batch-to-batch purity variance modeling** - Quality control feature for manufacturers
- **Mobile app interface for purity selection** - Phase 3 web UI first, then mobile (post-Phase 3)
- **Prominent user-facing documentation** - FINAL DECISION: Minimal docs only in API reference

## Dependencies & Prerequisites

### No External Research Required
This feature uses well-established chemistry (simple ratio adjustment). Industry-standard purity values are documented in user feedback:
- **KOH**: 85-95% pure (commercial grade, hygroscopic) - **Default: 90%**
- **NaOH**: 98-100% pure (commercial grade, more stable) - **Default: 100%**

### Integration with MVP Spec
- **Builds on**: FR-001 (saponification calculation) from 001-mvp-api spec
- **Enhances**: Calculation Result entity from 001-mvp-api spec
- **Maintains**: All MVP calculation accuracy and performance requirements
- **BREAKS**: Backward compatibility for KOH calculations (30% increase in default output)

### Technology Requirements
- No new dependencies required (uses existing FastAPI, Pydantic, SQLAlchemy stack)
- Alembic migration for database schema update
- Updated OpenAPI documentation (automatic via FastAPI)

### Team Readiness
- Straightforward calculation enhancement (division operation)
- Standard Pydantic validation patterns
- Routine database migration
- **Migration planning required** for breaking change communication

## Constitution Compliance

### Test-First Development (Principle III)
- TDD mandatory for purity calculation logic
- Property-based tests for edge cases (Hypothesis)
- Integration tests for API endpoints
- **Breaking change tests** for default behavior verification
- Red-Green-Refactor cycle enforced

### Research-Backed Calculations (Principle II)
- No peer-reviewed research required (simple ratio math)
- Industry-standard purity values documented in user feedback with competitor analysis
- No "community wisdom" used (values from supplier specifications and competitor calculator defaults)

### Data Integrity (Principle IV)
- Recipe versions preserve purity values
- Database migration maintains data consistency
- ACID compliance for recipe updates with new purity fields
- **Migration flag** preserves knowledge of legacy vs. explicit purity (FINAL DECISION)

### Safety Priority
- Validation is fail-safe (blocks dangerous values)
- Warning system educates users on unusual values (FINAL DECISION: warnings, not errors)
- Error messages clearly explain validation failures
- **Breaking change warning** in documentation and migration guide

### Backward Compatibility
- **BREAKING CHANGE**: Default 90% KOH purity changes existing calculations
- **Migration required**: Existing users must explicitly pass `koh_purity: 100` to maintain previous behavior
- NaOH default 100% purity maintains backward compatibility (unchanged)
- Optional parameters allow explicit control
- **Recommended**: API version bump (v1 → v2) to signal breaking change

## ✅ RESOLVED DECISIONS (Final Status)

All open questions have been resolved with user decisions. The following decisions are FINAL:

### 1. Default Purity Strategy ⚠️ BREAKING CHANGE
**FINAL DECISION**: Default to **90% for KOH** (user override of spec recommendation)
- **Previous Recommendation**: 100% for backward compatibility
- **User Decision**: 90% reflects real-world commercial KOH
- **Impact**: BREAKING CHANGE - existing API clients will get 30% more KOH
- **Migration**: Requires user communication and explicit `koh_purity: 100` for legacy behavior
- **NaOH**: Remains 100% default (unchanged, backward compatible)

### 2. Warning vs. Error Threshold ✅ MATCHES SPEC
**FINAL DECISION**: Purity <85% issues **WARNING** only, not error
- **Spec Recommendation**: Warning only
- **User Decision**: Confirmed - allows edge cases while alerting users
- **Implementation**: Generate warnings for KOH <85% or >95%, NaOH <98%
- **Behavior**: Calculations proceed, warnings included in response array

### 3. Documentation Prominence ⚠️ USER OVERRIDE
**FINAL DECISION**: **DO NOT add prominent purity documentation** for users
- **Previous Recommendation**: Add "Important Notes" section with highlighted explanation
- **User Decision**: Minimal documentation - mention in API reference only, not prominently
- **Implementation**: NFR-004 modified - API docs mention purity but no special callouts
- **Rationale**: User prefers streamlined documentation approach

### 4. Cost Calculation Display ✅ MATCHES SPEC
**FINAL DECISION**: Only show **commercial cost** in cost breakdown
- **Spec Recommendation**: Commercial cost only
- **User Decision**: Confirmed - avoid confusion, pure equivalent is chemistry reference only
- **Implementation**: FR-012 uses commercial (purity-adjusted) weights for all cost calculations

### 5. Migration Strategy ✅ MATCHES SPEC
**FINAL DECISION**: Tag existing recipes with "assumed 100% purity" metadata flag
- **Spec Recommendation**: Yes, add metadata field
- **User Decision**: Confirmed
- **Implementation**: New `purity_assumed` boolean column, TRUE for legacy recipes, FALSE for new
- **Purpose**: Track which recipes used explicit purity vs. defaulted values

### 6. Decimal Precision ✅ MATCHES SPEC
**FINAL DECISION**: Accept **2 decimal places**, display **1 decimal place**
- **Spec Recommendation**: 2 decimal input, 1 decimal output
- **User Decision**: Confirmed
- **Implementation**:
  - Validation accepts up to 2 decimals (e.g., 89.75%)
  - Response displays rounded to 1 decimal (e.g., 89.8%)
  - Internal calculations maintain full precision

### 7. Maximum Purity Hard Cap ✅ MATCHES SPEC
**FINAL DECISION**: Hard cap at **100% maximum**, no theoretical >100% scenarios
- **Spec Recommendation**: Hard cap at 100% for safety
- **User Decision**: Confirmed
- **Implementation**:
  - Validation rejects any purity >100.0%
  - Clear error message: "Purity cannot exceed 100%"
  - No academic/theoretical mode (future feature if needed)

## Implementation Priority

**HIGH PRIORITY** - Implement in Phase 1 or early Phase 2

**Justification**:
1. **Safety Critical**: Incorrect lye calculations cause chemical burns
2. **Industry Standard**: All major soap calculators support purity adjustment
3. **High Impact**: Affects majority of liquid soap users (90% use commercial KOH)
4. **Low Complexity**: Straightforward calculation and validation enhancement
5. **Breaking Change**: Requires careful migration planning and user communication
6. **User Requested**: Directly addresses documented user pain point

## Success Dependencies

- **Blocks**: This feature is independent and does not block other features
- **Blocked By**: Must have MVP saponification calculation working (001-mvp-api FR-001)
- **Enhances**: Cost calculator accuracy (MVP FR-006) by using commercial lye weights
- **Integration**: Works seamlessly with existing recipe storage (MVP FR-005) and quality metrics (MVP FR-002)

## Reference Test Case (from User Feedback)

```json
{
  "test_name": "Commercial 90% KOH Liquid Soap Recipe",
  "input": {
    "oils": [
      {"name": "Olive Oil", "percentage": 70},
      {"name": "Castor Oil", "percentage": 20},
      {"name": "Coconut Oil", "percentage": 10}
    ],
    "lye": {
      "naoh_percent": 10,
      "koh_percent": 90,
      "koh_purity": 90,    // Explicit (matches new default)
      "naoh_purity": 100   // Explicit (matches default)
    },
    "superfat_percent": 1,
    "water_lye_ratio": 3.0,
    "batch_size_g": 700
  },
  "expected_output": {
    "lye": {
      "koh_weight_g": 130.1,
      "naoh_weight_g": 18.6,
      "pure_koh_equivalent_g": 117.1,
      "pure_naoh_equivalent_g": 18.6,
      "koh_purity": 90,
      "naoh_purity": 100
    }
  },
  "tolerance_g": 0.5,
  "source": "User feedback testing with real recipe requirements"
}
```

## Migration Guide for Existing Users

### Breaking Change Summary
**What Changed**: Default KOH purity changed from 100% to 90%

**Impact**: Existing API calls without `koh_purity` parameter will receive **30% more KOH** in response

**Risk**: Over-lye soap (chemical burn hazard) if users don't update their code or recipes

### Migration Options

#### Option 1: Maintain Previous Behavior (Recommended for Existing Users)
**Add explicit `koh_purity: 100` to all API requests:**
```json
{
  "lye": {
    "koh_percent": 100,
    "koh_purity": 100  // Add this to maintain previous calculations
  }
}
```

#### Option 2: Adopt New Default (If Using Commercial 90% KOH)
**Remove or update your manual adjustments:**
- If you were dividing API results by 0.90, you can now remove that adjustment
- If you were using 100% pure KOH, switch to Option 1 above

#### Option 3: Specify Actual Purity (Best Practice)
**Use your supplier's actual purity specification:**
```json
{
  "lye": {
    "koh_percent": 90,
    "koh_purity": 88  // Use actual supplier specification
  }
}
```

### Deprecation Period Recommendation
Consider implementing a 30-day warning period where API returns deprecation headers:
```
X-API-Warning: KOH purity parameter omitted. Defaulting to 90%.
               Will become required in v2.1 after 2025-12-04.
```

### API Versioning Recommendation
Consider bumping API version (v1 → v2) to clearly signal breaking change:
- `GET /api/v1/calculate` - Legacy behavior (100% default, deprecated)
- `GET /api/v2/calculate` - New behavior (90% KOH default)

## Next Steps

1. **Review Specification**: Technical review with Grimm and stakeholders
2. **Approve Breaking Change**: Explicit stakeholder approval for 90% KOH default
3. **Plan Migration Communication**: Draft user notification of breaking change
4. **Run `/speckit.plan`**: Generate implementation plan with tasks
5. **Create Feature Branch**: `002-lye-purity` from main
6. **TDD Implementation**: Write tests first, implement purity calculation
7. **Database Migration**: Alembic migration for purity columns and `purity_assumed` flag
8. **Integration Testing**: Verify backward compatibility breaking change behavior
9. **Documentation Update**: Update OpenAPI docs with purity parameters (minimal prominence per user decision)
10. **User Validation**: Test with Shale using real recipes
11. **Migration Testing**: Verify legacy recipe tagging with `purity_assumed: true`
12. **Production Deployment**: Ansible playbook deployment with migration guide
13. **User Communication**: Notify existing API users of breaking change and migration options

---

**Version**: 2.0 (Updated with Final Decisions)
**Last Updated**: 2025-11-04
**Specification Author**: Spec Writer Agent
**Technical Reviewer**: [Pending]
**Stakeholder Approval**: [Pending Breaking Change Approval]
**Breaking Change Notice**: ⚠️ KOH default purity 100% → 90% requires user migration
