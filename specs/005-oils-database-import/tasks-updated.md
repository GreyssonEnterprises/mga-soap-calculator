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

- [x] T001 Review spec.md and plan.md to understand 147 oil import requirements
- [x] T002 Verify Oil model at `app/models/oil.py` has all required fields (NO migration needed)
- [x] T003 Study existing seed pattern at `scripts/seed_database.py` for idempotent duplicate detection
- [x] T004 Validate JSON structure in `working/user-feedback/oils-db-additions/complete-oils-database.json` (147 oils)

**Checkpoint**: ✅ Understanding complete - ready for TDD infrastructure

---

## Phase 2: Foundational (TDD Infrastructure)

**Purpose**: Test infrastructure MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Create Test Files (RED phase setup)

- [x] T005 [P] Create `tests/unit/test_oils_validation.py` with test skeleton
- [x] T006 [P] Create `tests/unit/test_oils_import.py` with test skeleton
- [x] T007 [P] Create `tests/integration/test_oils_data_integrity.py` with test skeleton
- [x] T008 [P] Create `tests/integration/test_oils_import_idempotent.py` with test skeleton

### Write Validation Tests (RED phase - tests FAIL initially)

- [x] T009 [P] Write test_validate_sap_naoh_range() in `tests/unit/test_oils_validation.py` (expect 0.100-0.300)
- [x] T010 [P] Write test_validate_sap_koh_range() in `tests/unit/test_oils_validation.py` (expect 0.140-0.420)
- [x] T011 [P] Write test_validate_fatty_acids_sum() in `tests/unit/test_oils_validation.py` (expect 95-100%)
- [x] T012 [P] Write test_validate_quality_metrics_range() in `tests/unit/test_oils_validation.py` (expect 0-99)
- [x] T013 Write test_pine_tar_special_case() in `tests/unit/test_oils_validation.py` (allow zero fatty acids)

### Create Import Script Skeleton

- [x] T014 Create `scripts/import_oils_database.py` with function stubs (load_oils_from_json, validate_oil_data, import_oils_database)
- [x] T015 Create `scripts/validate_oils_data.py` CLI skeleton for pre-import validation

### Write Import Logic Tests (RED phase - tests FAIL initially)

- [x] T016 [P] Write test_load_json_data() in `tests/unit/test_oils_import.py` (parse 147 oils)
- [x] T017 [P] Write test_validate_all_oils() in `tests/unit/test_oils_import.py` (all oils pass validation)
- [x] T018 Write test_duplicate_detection() in `tests/unit/test_oils_import.py` (skip existing oils)

**Checkpoint**: ✅ Foundation ready - all tests written and FAILING (RED phase complete) - user story implementation can now begin

**TEST RESULTS**:
- 16 validation tests FAIL with NotImplementedError ✅
- 6 import tests FAIL with NotImplementedError ✅
- 2 integration tests skipped (require database) ✅

---

## Phase 3: User Story 1 - Soap Maker Accesses 147 Oils (Priority: P1) 🎯 MVP

**Goal**: Import all 147 oils from JSON to database with validation and idempotency

**Status**: READY TO IMPLEMENT (RED phase verified)

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

**Checkpoint**: User Story 1 implementation ready to begin - all tests waiting to turn GREEN

---

## Remaining Phases

See original tasks.md for Phase 4 (US2), Phase 5 (Polish), and execution strategy.

