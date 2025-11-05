# Tasks: Comprehensive Oils Database Import

**Input**: Design documents from `/specs/005-oils-database-import/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story following TDD methodology.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `scripts/`, `tests/`, `app/` at repository root
- Tests organized: `tests/unit/`, `tests/integration/`
- Source data: `working/user-feedback/oils-db-additions/complete-oils-database.json`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and understanding existing patterns

- [ ] T001 Review spec.md and plan.md to understand 147 oil import requirements
- [ ] T002 Verify Oil model at `app/models/oil.py` has all required fields (NO migration needed)
- [ ] T003 Study existing seed pattern at `scripts/seed_database.py` for idempotent duplicate detection
- [ ] T004 Validate JSON structure in `working/user-feedback/oils-db-additions/complete-oils-database.json` (147 oils)

**Checkpoint**: Understanding complete - ready for TDD infrastructure

---

## Phase 2: Foundational (TDD Infrastructure)

**Purpose**: Test infrastructure MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Create Test Files (RED phase setup)

- [ ] T005 [P] Create `tests/unit/test_oils_validation.py` with test skeleton
- [ ] T006 [P] Create `tests/unit/test_oils_import.py` with test skeleton
- [ ] T007 [P] Create `tests/integration/test_oils_data_integrity.py` with test skeleton
- [ ] T008 [P] Create `tests/integration/test_oils_import_idempotent.py` with test skeleton

### Write Validation Tests (RED phase - tests FAIL initially)

- [ ] T009 [P] Write test_validate_sap_naoh_range() in `tests/unit/test_oils_validation.py` (expect 0.100-0.300)
- [ ] T010 [P] Write test_validate_sap_koh_range() in `tests/unit/test_oils_validation.py` (expect 0.140-0.420)
- [ ] T011 [P] Write test_validate_fatty_acids_sum() in `tests/unit/test_oils_validation.py` (expect 95-100%)
- [ ] T012 [P] Write test_validate_quality_metrics_range() in `tests/unit/test_oils_validation.py` (expect 0-99)
- [ ] T013 Write test_pine_tar_special_case() in `tests/unit/test_oils_validation.py` (allow zero fatty acids)

### Create Import Script Skeleton

- [ ] T014 Create `scripts/import_oils_database.py` with function stubs (load_oils_from_json, validate_oil_data, import_oils_database)
- [ ] T015 Create `scripts/validate_oils_data.py` CLI skeleton for pre-import validation

### Write Import Logic Tests (RED phase - tests FAIL initially)

- [ ] T016 [P] Write test_load_json_data() in `tests/unit/test_oils_import.py` (parse 147 oils)
- [ ] T017 [P] Write test_validate_all_oils() in `tests/unit/test_oils_import.py` (all oils pass validation)
- [ ] T018 Write test_duplicate_detection() in `tests/unit/test_oils_import.py` (skip existing oils)

**Checkpoint**: Foundation ready - all tests written and FAILING (RED phase complete) - user story implementation can now begin

---

## Phase 3: User Story 1 - Soap Maker Accesses 147 Oils (Priority: P1) 🎯 MVP

**Goal**: Import all 147 oils from JSON to database with validation and idempotency

**Test Criteria**:
- Query returns 147 new oils (158 total with existing 11 seed oils)
- All SAP values within scientific ranges
- All fatty acid profiles sum to 95-100% (except Pine Tar special case)
- Re-import is idempotent (0 duplicates)

**Independent Test**:
```bash
python scripts/import_oils_database.py
# Expected: "147 oils added, 0 skipped"
psql -d mga_soap_calculator -c "SELECT COUNT(*) FROM oils;"
# Expected: 158 (11 existing + 147 new)
```

### Implementation for US1 - Data Loading

- [ ] T019 [US1] Implement load_oils_from_json() in `scripts/import_oils_database.py` to parse JSON with error handling
- [ ] T020 [US1] Verify test_load_json_data() now PASSES (GREEN phase)

### Implementation for US1 - Validation Logic

- [ ] T021 [P] [US1] Implement validate_sap_naoh_range() in `scripts/import_oils_database.py` (0.100-0.300)
- [ ] T022 [P] [US1] Implement validate_sap_koh_range() in `scripts/import_oils_database.py` (0.140-0.420)
- [ ] T023 [P] [US1] Implement validate_fatty_acids_sum() in `scripts/import_oils_database.py` (95-100% with Pine Tar exception)
- [ ] T024 [P] [US1] Implement validate_quality_metrics() in `scripts/import_oils_database.py` (0-99 range)
- [ ] T025 [US1] Implement validate_oil_data() wrapper in `scripts/import_oils_database.py` combining all validation rules
- [ ] T026 [US1] Verify all validation tests in `tests/unit/test_oils_validation.py` now PASS (GREEN phase)

### Implementation for US1 - Import Logic

- [ ] T027 [US1] Implement is_oil_exists() duplicate detection in `scripts/import_oils_database.py` using SELECT pattern from seed_database.py
- [ ] T028 [US1] Implement import_oils_database() async function in `scripts/import_oils_database.py` with transaction management
- [ ] T029 [US1] Add progress logging (every 10 oils) to import_oils_database()
- [ ] T030 [US1] Add error handling (JSON parse, validation, database) to import_oils_database()
- [ ] T031 [US1] Implement summary reporting (X added, Y skipped, time elapsed) in import_oils_database()
- [ ] T032 [US1] Verify test_duplicate_detection() now PASSES (GREEN phase)

### Implementation for US1 - CLI Interface

- [ ] T033 [US1] Implement validate_oils_data.py CLI with argparse (--json-path argument)
- [ ] T034 [US1] Add __main__ block to import_oils_database.py for script execution
- [ ] T035 [US1] Add command-line argument support (--dry-run, --verbose) to import_oils_database.py

### Integration Tests for US1

- [ ] T036 [US1] Write and verify test_import_all_147_oils() in `tests/integration/test_oils_data_integrity.py` (count = 158 total)
- [ ] T037 [US1] Write and verify test_import_idempotency() in `tests/integration/test_oils_import_idempotent.py` (run twice, no duplicates)
- [ ] T038 [US1] Write and verify test_partial_reimport() in `tests/integration/test_oils_import_idempotent.py` (delete some, re-import restores)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - 147 oils imported successfully

---

## Phase 4: User Story 2 - Professional Formulator Uses Complete Fatty Acid Data (Priority: P2)

**Goal**: Validate that 98% of oils (144+ of 147) have complete fatty acid profiles

**Test Criteria**:
- At least 144 oils have all 8 fatty acids defined
- Fatty acids sum to 95-105% for each oil (allowing rounding variance)
- Special cases documented (Pine Tar, Meadowfoam)

**Independent Test**:
```bash
python scripts/validate_oils_data.py working/user-feedback/oils-db-additions/complete-oils-database.json
# Expected: "144/147 oils have complete fatty acid profiles (97.96%)"
```

### Tests for US2 (RED phase)

- [ ] T039 [P] [US2] Write test_fatty_acid_completeness_percentage() in `tests/integration/test_oils_data_integrity.py` (≥144 oils complete)
- [ ] T040 [P] [US2] Write test_fatty_acid_sum_validation() in `tests/integration/test_oils_data_integrity.py` (95-105% sum)
- [ ] T041 [US2] Write test_special_cases_documented() in `tests/integration/test_oils_data_integrity.py` (Pine Tar, Meadowfoam)

### Implementation for US2 - Validation Enhancements

- [ ] T042 [US2] Add check_fatty_acid_completeness() function to `scripts/import_oils_database.py`
- [ ] T043 [US2] Add generate_fatty_acid_report() to import_oils_database.py (count complete oils)
- [ ] T044 [US2] Add special case detection to validate_oil_data() for Pine Tar and Meadowfoam
- [ ] T045 [US2] Update validate_oils_data.py CLI to output fatty acid completeness report

### Implementation for US2 - Post-Import Verification

- [ ] T046 [US2] Add post_import_verification() to import_oils_database.py (run after import completes)
- [ ] T047 [US2] Implement fatty acid completeness query in post_import_verification()
- [ ] T048 [US2] Add reporting for oils with incomplete profiles (if any)
- [ ] T049 [US2] Verify all US2 tests now PASS (GREEN phase)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - import complete with validation

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the entire feature

### Performance Validation

- [ ] T050 [P] Add performance timing to import_oils_database.py (verify <5 min target)
- [ ] T051 [P] Test batch commit strategy (single transaction for all 147 oils)
- [ ] T052 Optimize progress logging (every 10 oils, not every oil)

### Error Handling & Logging

- [ ] T053 [P] Add structured error messages with oil name and validation failure reason
- [ ] T054 [P] Add non-zero exit codes for different failure types (JSON parse=1, validation=1, DB=2)
- [ ] T055 Implement transaction rollback on validation failure

### Documentation & Deployment

- [ ] T056 [P] Add docstrings to all functions in `scripts/import_oils_database.py`
- [ ] T057 [P] Create usage documentation in `scripts/import_oils_database.py` module docstring
- [ ] T058 Add validation report example to validate_oils_data.py docstring
- [ ] T059 Update repository README.md with import script usage instructions (if needed)

### Final Verification

- [ ] T060 Run full test suite: `pytest tests/unit/test_oils_*.py tests/integration/test_oils_*.py -v`
- [ ] T061 Verify code coverage ≥90%: `pytest --cov=scripts.import_oils_database --cov-report=term-missing`
- [ ] T062 Execute full import: `python scripts/import_oils_database.py` (verify success)
- [ ] T063 Verify database state: Query oils table, verify 158 total oils with correct data
- [ ] T064 Test API: `curl http://localhost:8000/v1/oils | jq '. | length'` → 158

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
  - **CRITICAL**: All tests must be written and FAILING before implementation begins (RED phase)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational - No dependencies on other stories
  - User Story 2 (P2) can start after Foundational - May reference US1 but is independently testable
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### TDD Workflow Within Each Phase

**RED → GREEN → REFACTOR cycle**:

1. **RED Phase** (Foundational): Write tests that FAIL
2. **GREEN Phase** (US1/US2): Implement code to make tests PASS
3. **REFACTOR Phase** (Polish): Optimize and improve

### Within User Story 1

**Tests First (RED)**:
- T005-T018: Create all test files and write tests (expect FAILURE)

**Implementation (GREEN)**:
- T019-T020: Data loading
- T021-T026: Validation logic (verify tests pass)
- T027-T032: Import logic (verify tests pass)
- T033-T035: CLI interface

**Integration (REFACTOR)**:
- T036-T038: Integration tests

### Within User Story 2

**Tests First (RED)**:
- T039-T041: Write validation tests (expect FAILURE)

**Implementation (GREEN)**:
- T042-T045: Validation enhancements
- T046-T049: Post-import verification (verify tests pass)

### Parallel Opportunities

**Within Foundational Phase (Phase 2)**:
- T005-T008: All test file creation (parallel)
- T009-T012: All validation test writing (parallel)
- T016-T017: Import test writing (parallel)

**Within US1 Implementation**:
- T021-T024: All validation implementations (parallel)

**Within US2 Implementation**:
- T039-T040: Test writing (parallel)

**Within Polish Phase**:
- T050-T051: Performance tasks (parallel)
- T053-T054: Error handling tasks (parallel)
- T056-T057: Documentation tasks (parallel)

---

## Parallel Example: Foundational Phase

```bash
# Launch all test file creations together:
Task: "Create tests/unit/test_oils_validation.py with test skeleton"
Task: "Create tests/unit/test_oils_import.py with test skeleton"
Task: "Create tests/integration/test_oils_data_integrity.py with test skeleton"
Task: "Create tests/integration/test_oils_import_idempotent.py with test skeleton"

# Launch all validation test implementations together:
Task: "Write test_validate_sap_naoh_range() in tests/unit/test_oils_validation.py"
Task: "Write test_validate_sap_koh_range() in tests/unit/test_oils_validation.py"
Task: "Write test_validate_fatty_acids_sum() in tests/unit/test_oils_validation.py"
Task: "Write test_validate_quality_metrics_range() in tests/unit/test_oils_validation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) ⭐ RECOMMENDED

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational - **CRITICAL** (T005-T018)
   - **Verify all tests FAIL** before proceeding (RED phase complete)
3. Complete Phase 3: User Story 1 (T019-T038)
   - **Verify tests PASS** as implementation progresses (GREEN phase)
4. **STOP and VALIDATE**:
   - Run: `python scripts/import_oils_database.py`
   - Verify: 147 oils imported, 158 total in database
   - Test idempotency: Run again, verify 0 added, 147 skipped
5. Deploy/demo if ready

**MVP Delivers**: 147 comprehensive oils available via API (53% more than competitors)

### Full Feature (Both User Stories)

1. Complete MVP (Phases 1-3)
2. Complete Phase 4: User Story 2 (T039-T049)
   - Validate fatty acid completeness (≥144 oils = 98%)
   - Document special cases
3. Complete Phase 5: Polish (T050-T064)
4. Full verification and deployment

**Full Feature Delivers**: 147 oils + fatty acid quality validation + professional-grade data integrity

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational done (all tests written and FAILING):
   - **Developer A**: User Story 1 implementation (T019-T038)
   - **Developer B**: User Story 2 tests and planning (T039-T041)
3. After US1 complete:
   - **Developer B**: User Story 2 implementation (T042-T049)
   - **Developer A**: Polish tasks (T050-T064)

---

## Notes

### File Structure Created

```
scripts/
├── import_oils_database.py      # NEW: Main import script (T014, T019-T035)
└── validate_oils_data.py         # NEW: Pre-import validation CLI (T015, T033)

tests/
├── unit/
│   ├── test_oils_import.py       # NEW: Import logic tests (T006, T016-T018)
│   └── test_oils_validation.py   # NEW: Validation rules tests (T005, T009-T013)
└── integration/
    ├── test_oils_data_integrity.py    # NEW: Data integrity tests (T007, T036, T039-T041)
    └── test_oils_import_idempotent.py # NEW: Idempotency tests (T008, T037-T038)
```

### Key Design Decisions

- **NO schema changes**: Oil model at `app/models/oil.py` already complete
- **Extends existing pattern**: `scripts/seed_database.py` provides idempotent duplicate detection
- **TDD methodology**: Tests written FIRST (RED), implementation makes them PASS (GREEN)
- **Single transaction**: All 147 oils in one ACID-compliant PostgreSQL transaction
- **Idempotent**: Safe to run multiple times, duplicate detection prevents errors
- **Special cases**: Pine Tar (zero fatty acids), Meadowfoam (C20/C22 approximation) handled

### Validation Rules Summary

- **SAP NaOH**: 0.100-0.300 g/g
- **SAP KOH**: 0.140-0.420 g/g
- **Fatty Acids**: Sum 95-100% (5% tolerance for rounding)
- **Quality Metrics**: 0-99 range
- **Iodine**: 0-200 typical
- **INS**: 0-350 typical
- **INCI names**: May be empty (acceptable)

### Performance Target

- Import time: <5 minutes for 147 oils (~2s per oil average)
- Single transaction commit
- Progress logging every 10 oils

### Testing Philosophy

- **RED phase**: Write tests that FAIL (Foundational phase)
- **GREEN phase**: Implement to make tests PASS (US1/US2 phases)
- **REFACTOR phase**: Optimize and improve (Polish phase)
- Target: ≥90% code coverage
- Integration tests verify real database operations

---

## Quick Reference

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD CRITICAL**: Verify tests fail (RED) before implementing (GREEN)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, premature optimization
