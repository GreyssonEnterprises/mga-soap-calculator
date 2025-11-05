# System Architect - Comprehensive Oils Database Import Tasks

**Timestamp**: 2025-11-05T06:06:23Z
**Task**: Generate implementation tasks for 147 oils database import
**Requestor**: User

## Response

Generated comprehensive tasks.md for the Comprehensive Oils Database Import feature (005).

### Task File Location
`/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/specs/005-oils-database-import/tasks.md`

### Task Summary

**Total Tasks**: 64 tasks across 5 phases

**Phase Breakdown**:
- **Phase 1: Setup** (4 tasks) - Understanding and verification
- **Phase 2: Foundational** (14 tasks) - TDD infrastructure (CRITICAL - blocks all stories)
- **Phase 3: User Story 1** (20 tasks) - Import 147 oils with validation
- **Phase 4: User Story 2** (11 tasks) - Validate fatty acid completeness (98%)
- **Phase 5: Polish** (15 tasks) - Performance, documentation, final verification

### Key Design Decisions

1. **TDD Methodology**:
   - Phase 2: Write all tests FIRST (expect FAILURE - RED phase)
   - Phase 3-4: Implement to make tests PASS (GREEN phase)
   - Phase 5: Refactor and optimize (REFACTOR phase)

2. **No Schema Changes**:
   - Existing Oil model at `app/models/oil.py` already complete
   - All required fields present (id, common_name, inci_name, SAP values, fatty_acids JSONB, quality_contributions JSONB)
   - NO migration needed

3. **Extends Existing Pattern**:
   - Follows `scripts/seed_database.py` idempotent duplicate detection
   - Uses async/await with AsyncSession
   - Single transaction ACID compliance

4. **Parallel Execution Opportunities**:
   - Phase 2: Test file creation (T005-T008) - 4 parallel tasks
   - Phase 2: Validation tests (T009-T012) - 4 parallel tasks
   - Phase 3: Validation implementations (T021-T024) - 4 parallel tasks
   - Phase 4: US2 tests (T039-T040) - 2 parallel tasks
   - Phase 5: Multiple polish tasks parallelizable

### User Stories

**US1 (P1) - Soap Maker Accesses 147 Oils**: 🎯 MVP
- **Goal**: Import all 147 oils from JSON to database
- **Test Criteria**: 158 total oils (11 existing + 147 new), idempotent re-import
- **Tasks**: T019-T038 (20 tasks)

**US2 (P2) - Professional Formulator Uses Complete Fatty Acid Data**:
- **Goal**: Validate 98% oils have complete fatty acid profiles
- **Test Criteria**: ≥144 oils with all 8 fatty acids, sum 95-105%
- **Tasks**: T039-T049 (11 tasks)

### Files to Create

**Scripts** (2 new files):
- `scripts/import_oils_database.py` - Main import script with validation
- `scripts/validate_oils_data.py` - Pre-import validation CLI tool

**Tests** (4 new files):
- `tests/unit/test_oils_validation.py` - Validation rules unit tests
- `tests/unit/test_oils_import.py` - Import logic unit tests
- `tests/integration/test_oils_data_integrity.py` - Data integrity integration tests
- `tests/integration/test_oils_import_idempotent.py` - Idempotency integration tests

### Validation Rules

From spec.md and plan.md:

- **SAP NaOH**: 0.100-0.300 g/g
- **SAP KOH**: 0.140-0.420 g/g (KOH factor ~1.403x NaOH)
- **Fatty Acids**: Sum 95-100% (5% tolerance for rounding)
- **Quality Metrics**: 0-99 range
- **Iodine**: 0-200 typical range
- **INS**: 0-350 typical range
- **INCI names**: May be empty (acceptable)

**Special Cases**:
- **Pine Tar**: Zero fatty acids allowed (resin acids, not traditional fatty acids)
- **Meadowfoam**: C20/C22 long-chain fatty acids approximated as oleic

### Performance Targets

- **Import time**: <5 minutes for 147 oils (~2s per oil average)
- **Strategy**: Single transaction, batch commit, progress logging every 10 oils
- **Expected**: ~2-3 minutes actual (well under budget)

### Implementation Strategies

**MVP First (Recommended)** ⭐:
1. Complete Setup (T001-T004)
2. Complete Foundational - verify all tests FAIL (T005-T018)
3. Complete User Story 1 - verify tests PASS (T019-T038)
4. Validate: Import 147 oils, verify 158 total
5. Deploy/demo

**Delivers**: 147 comprehensive oils (53% more than competitors)

**Full Feature**:
1. Complete MVP (Phases 1-3)
2. Add User Story 2 validation (T039-T049)
3. Polish and optimize (T050-T064)
4. Full verification

**Delivers**: 147 oils + fatty acid quality validation + professional-grade data integrity

### Critical Path

**Phase 2 (Foundational) is CRITICAL**:
- BLOCKS all user story work
- Must write all tests FIRST
- Must verify tests FAIL before implementation (RED phase)
- Only then can US1/US2 implementation begin (GREEN phase)

**Sequential Dependencies**:
- Phase 1 → Phase 2 → Phase 3/4 → Phase 5
- Within phases, many tasks can run in parallel (marked [P])

### Testing Philosophy

**RED → GREEN → REFACTOR**:
1. **RED**: Write tests that FAIL (Phase 2 Foundational)
2. **GREEN**: Implement to make tests PASS (Phase 3-4 User Stories)
3. **REFACTOR**: Optimize and improve (Phase 5 Polish)

**Coverage Target**: ≥90% code coverage for import script

**Integration Testing**: Real database operations, idempotency verification

### Data Source

- **File**: `working/user-feedback/oils-db-additions/complete-oils-database.json`
- **Size**: 4117 lines, 147 oils
- **Structure**: JSON object with oil_id keys, each containing complete oil data
- **Maps 1:1 to Oil model**: NO transformation needed

### Risk Mitigation

- **Pre-import validation**: Catch all issues before database commit
- **Idempotency**: Duplicate detection prevents data corruption
- **Transaction safety**: Single PostgreSQL transaction with automatic rollback
- **Performance**: 147 oils well within 5-minute target
- **Backward compatibility**: No schema changes, existing API unchanged

### Next Steps

1. Review generated tasks.md
2. Confirm task structure and dependencies
3. Begin Phase 1 (Setup) tasks
4. Execute Phase 2 (Foundational) to write all tests (RED phase)
5. Implement User Story 1 (GREEN phase)

## Metadata

- **Status**: Complete
- **Confidence**: High
- **Follow-up**: Ready for implementation via `/speckit.implement`
- **Files**:
  - Generated: `specs/005-oils-database-import/tasks.md`
  - Source data: `working/user-feedback/oils-db-additions/complete-oils-database.json`
  - Existing reference: `scripts/seed_database.py`, `app/models/oil.py`

## Quality Validation

✅ **TDD Methodology**: Explicit RED → GREEN → REFACTOR phases
✅ **User Story Organization**: Tasks grouped by US1, US2 for independent implementation
✅ **Parallel Opportunities**: 15+ tasks marked [P] for concurrent execution
✅ **File Paths**: All tasks include exact file paths
✅ **Constitution Compliance**: No schema changes, extends existing patterns, <5 min performance target
✅ **MVP Definition**: Clear MVP path (US1 only = 147 oils imported)
✅ **Dependencies**: Sequential phases with parallel tasks within phases
✅ **Special Cases**: Pine Tar and Meadowfoam documented in validation tasks
✅ **Integration Tests**: Idempotency and data integrity verification included

## Architecture Notes

This is a **data import operation**, not a feature expansion:

- **No API changes**: Existing `/v1/oils` endpoint already returns all oil fields
- **No schema changes**: Oil model complete, no migration required
- **No frontend changes**: Oils automatically available via existing endpoint
- **Pure data operation**: Populate database from authoritative JSON source

**Complexity**: LOW - Extends proven pattern with validation

**Blocks**: Feature #006 (Additive Calculator), Feature #008 (INCI Generator)

**Priority**: CRITICAL - Foundational data for upcoming features
