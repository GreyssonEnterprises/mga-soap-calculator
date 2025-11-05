# Implementation: KOH/NaOH Purity Support

**Agent**: Implementer
**Feature**: 002-lye-purity
**Branch**: `002-lye-purity`
**Timestamp**: 2025-11-04 15:42:00
**Requested by**: User

## Implementation Summary

Implementing safety-critical KOH/NaOH purity support feature with strict TDD workflow following spec-kit methodology.

**Feature Overview**:
- Add purity adjustment to lye calculations (90% KOH default, 100% NaOH default)
- Safety-critical: Incorrect calculations cause chemical burns
- Breaking change: KOH default changes from 100% to 90%
- TDD mandatory: Tests FIRST, then implementation

## Codebase Structure Analysis

**Existing Architecture**:
```
app/
├── schemas/
│   ├── requests.py          # Pydantic request models (LyeConfig exists)
│   └── responses.py         # Pydantic response models
├── services/
│   ├── lye_calculator.py    # Core lye calculation logic (calculate_lye function)
│   ├── water_calculator.py
│   ├── quality_metrics_calculator.py
│   └── validation.py
├── api/v1/
│   └── calculate.py         # API endpoint (uses lye_calculator)
└── models/
    └── calculation.py       # SQLAlchemy model

tests/
├── unit/                    # Unit tests exist
├── integration/             # Integration tests exist
└── conftest.py              # Test fixtures
```

**Key Findings**:
1. Lye calculation logic is in `app/services/lye_calculator.py` (NOT `app/core/saponification.py`)
2. Plan references non-existent `saponification.py` - should be `lye_calculator.py`
3. LyeConfig already exists in `app/schemas/requests.py` with validators
4. Test infrastructure already in place (unit + integration directories)
5. Using FastAPI + Pydantic 2.0 + SQLAlchemy async

## Phase 1: Setup (Tasks T001-T004) ✅ COMPLETE

### Tasks Completed:
- ✅ T001 - Feature branch `002-lye-purity` verified (already exists)
- ✅ T002 - spec.md reviewed for safety-critical requirements
- ✅ T003 - plan.md reviewed for TDD workflow
- ✅ T004 - Constitution compliance verified (ALL 8 principles PASS)

### Key Requirements Summary:

**Breaking Change**:
- KOH default: 100% → 90% (CRITICAL)
- Impact: 30% more KOH in all calculations
- Requires stakeholder approval + user migration guide

**Safety Requirements**:
- Range validation: 50-100% (hard bounds)
- Hard cap: 100% maximum (no >100%)
- Fail-safe: Block dangerous values BEFORE calculation
- Accuracy: ±0.5g tolerance per 500g batch

**Calculation Formula**:
```python
commercial_weight = pure_lye_needed / (purity / 100)
# Example: 117.1g pure @ 90% purity = 130.1g commercial
```

**Test Coverage**:
- Unit tests (formula correctness)
- Property-based tests (Hypothesis - boundaries)
- Validation tests (reject invalid)
- Integration tests (API E2E)
- Backward compatibility tests (90% default)
- Target: >90% coverage

### Constitution Verification:
✅ All 8 principles PASS:
1. API-First: No frontend changes
2. Research-Backed: Industry standards documented
3. Test-First: TDD mandatory
4. Data Integrity: Migration with ACID
5. Performance: <5ms overhead target
6. Security: Pydantic validation
7. Deployment: Ansible playbook update
8. Observability: Logging + monitoring

---

## Phase 2: Foundational (TDD Infrastructure) 🚧 IN PROGRESS

**Purpose**: Test infrastructure + base schemas BEFORE any user stories

**Critical TDD Gate**: ALL tests must exist and FAIL before implementation begins

### File Path Corrections (Plan.md References Wrong Files):

**Plan says**: `app/core/saponification.py`
**Actual file**: `app/services/lye_calculator.py`

All references to `saponification.py` should be `lye_calculator.py` in implementation.

### Test Infrastructure Setup (T010-T015)

Creating test files with FAILING test stubs:

1. **T010**: `tests/unit/test_lye_calculator_purity.py` (NEW)
   - Purity calculation formula tests
   - Replaces plan's `test_saponification.py` reference

2. **T011**: `tests/unit/test_purity_validation.py` (NEW)
   - Boundary value tests (50%, 100%, 49%, 101%)
   - Pydantic validation tests

3. **T012**: `tests/unit/test_purity_warnings.py` (NEW)
   - Warning generation tests (<85%, >95% KOH)
   - Non-blocking warning validation

4. **T013**: `tests/property/test_purity_properties.py` (NEW - directory may not exist)
   - Hypothesis property-based tests
   - Edge case coverage (1000+ random combinations)

5. **T014**: `tests/integration/test_purity_api.py` (NEW)
   - API endpoint integration tests
   - Full request-response cycle

6. **T015**: `tests/integration/test_backward_compat.py` (NEW)
   - Breaking change verification
   - 90% default behavior tests

### Base Schema Enhancement (T020-T026)

Modifying existing Pydantic models:

1. **T020-T021**: Add purity fields to `LyeConfig` in `app/schemas/requests.py`
   ```python
   koh_purity: Optional[float] = Field(default=90.0, ge=50.0, le=100.0)
   naoh_purity: Optional[float] = Field(default=100.0, ge=50.0, le=100.0)
   ```

2. **T022**: Add validator to `LyeConfig` for percentage sum (already exists)

3. **T023-T024**: Add purity fields to response schema in `app/schemas/responses.py`

4. **T025**: Create `WarningMessage` schema in `app/schemas/responses.py`

5. **T026**: Add warnings array to `CalculationResponse`

### Database Schema (T030-T034)

Add columns to `Calculation` model in `app/models/calculation.py`:

1. **T030**: `koh_purity` DECIMAL(5,2) NOT NULL DEFAULT 90.0
2. **T031**: `naoh_purity` DECIMAL(5,2) NOT NULL DEFAULT 100.0
3. **T032**: `purity_assumed` BOOLEAN NOT NULL DEFAULT FALSE
4. **T033**: CheckConstraint for koh_purity (50-100)
5. **T034**: CheckConstraint for naoh_purity (50-100)

### Database Migration (T040-T045)

Alembic migration for purity columns:

1. **T040**: Create migration file `alembic/versions/<timestamp>_add_lye_purity.py`
2. **T041**: Add columns with defaults (koh=90, naoh=100)
3. **T042**: Update existing recipes to koh_purity=100, purity_assumed=TRUE (preserve legacy)
4. **T043**: Add database constraints
5. **T044**: Implement downgrade() (rollback path)
6. **T045**: Test migration in dev (upgrade + downgrade)

### Phase 2 Checkpoint Requirements:

Before proceeding to user stories:
- ✅ All test files exist
- ✅ All tests FAIL (no implementation yet)
- ✅ Schema changes committed
- ✅ Database migration created and tested
- ✅ Foundation ready for parallel user story work

---

## Next Steps

1. **Create test directory structure** (if `tests/property/` doesn't exist)
2. **Write ALL foundational tests** (T010-T015) - MUST FAIL
3. **Implement base schemas** (T020-T026)
4. **Create database migration** (T040-T045)
5. **Verify foundation complete** before user stories

**Pausing for validation**: Ready to proceed with Phase 2 Foundational implementation?

---

## Metadata
- **Status**: Phase 1 Complete, Phase 2 Started
- **Current Phase**: Foundational (TDD Infrastructure)
- **Next Tasks**: T010-T015 (Test file creation)
- **Confidence**: High
- **Branch Status**: Clean, ready for commits
- **Breaking Change**: Stakeholder approval pending
