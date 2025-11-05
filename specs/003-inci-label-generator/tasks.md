---
description: "Implementation tasks for INCI Label Generator feature"
---

# Tasks: INCI Label Generator

**Input**: Design documents from `/specs/003-inci-label-generator/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/inci-label.yaml, research.md

**Tests**: TDD is MANDATORY per MGA Soap Calculator constitution - tests MUST be written BEFORE implementation

**Organization**: Tasks grouped by phase with clear dependencies. User stories executed with tests-first approach.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Single project structure at repository root:
- Backend: `app/` (models, services, api, schemas)
- Tests: `tests/` (unit, integration)
- Migrations: `alembic/versions/`
- Data: `app/data/`
- Scripts: `scripts/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Database schema extension and reference data preparation

- [ ] T001 Create Alembic migration for saponified_inci_name field in alembic/versions/003_add_saponified_inci_name.py
- [ ] T002 [P] Create reference data file app/data/saponified-inci-terms.json with 37 oil entries
- [ ] T003 [P] Create backfill script scripts/backfill_saponified_inci_names.py for populating saponified INCI names
- [ ] T004 Run migration and backfill to populate Oil model with saponified INCI data
- [ ] T005 [P] Update Oil model in app/models/oil.py with saponified_inci_name field

---

## Phase 2: Foundational (Core Services)

**Purpose**: Shared services that both user stories depend on - BLOCKS all story work

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [ ] T006 [P] Write unit tests for INCI naming service in tests/unit/test_inci_naming.py (TDD - write FIRST, ensure FAIL)
- [ ] T007 [P] Write unit tests for percentage calculation in tests/unit/test_percentage_calculation.py (TDD - write FIRST, ensure FAIL)
- [ ] T008 [P] Write property-based tests for edge cases using Hypothesis in tests/unit/test_inci_edge_cases.py (TDD - write FIRST, ensure FAIL)
- [ ] T009 Implement INCI naming service in app/services/inci_naming.py (includes get_saponified_inci_name, generate_saponified_name, fallback logic)
- [ ] T010 Implement percentage calculation service in app/services/percentage_calculator.py (calculates ingredient percentages from batch weights)
- [ ] T011 Verify foundational tests pass (Green phase) - all unit tests and property-based tests passing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multiple Format Support (Priority: P1) 🎯 MVP

**Goal**: Generate INCI labels in three formats (raw oils, saponified salts, common names)

**Independent Test**: API returns all three label formats with proper ingredient transformation

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Contract test for raw INCI format in tests/integration/test_inci_endpoint_raw.py (verify pre-saponification format with lye included)
- [ ] T013 [P] [US1] Contract test for saponified INCI format in tests/integration/test_inci_endpoint_saponified.py (verify post-saponification with sodium salts)
- [ ] T014 [P] [US1] Contract test for common names format in tests/integration/test_inci_endpoint_common.py (verify consumer-friendly names)
- [ ] T015 [P] [US1] Integration test for format parameter handling in tests/integration/test_inci_format_selection.py (all, raw_inci, saponified_inci, common_names)

### Implementation for User Story 1

- [ ] T016 [US1] Create Pydantic schemas in app/schemas/inci_label.py (InciLabelResponse, IngredientBreakdown, LabelFormats)
- [ ] T017 [US1] Implement label generator service in app/services/label_generator.py (format_raw_inci, format_saponified_inci, format_common_names methods)
- [ ] T018 [US1] Implement API endpoint in app/api/v1/inci.py (GET /api/v1/recipes/{recipe_id}/inci-label with format parameter)
- [ ] T019 [US1] Add error handling for missing INCI names (fallback to common names) in app/services/label_generator.py
- [ ] T020 [US1] Add edge case handling in app/services/label_generator.py (trace ingredients, missing data, essential oils vs fragrance)
- [ ] T021 [US1] Add structured logging for label generation operations in app/api/v1/inci.py

**Checkpoint**: At this point, User Story 1 should be fully functional with all three format variants working independently

---

## Phase 4: User Story 2 - Percentage-Based Sorting (Priority: P2)

**Goal**: Sort all ingredients by percentage in descending order for regulatory compliance

**Independent Test**: API returns ingredients sorted by percentage with accurate calculations for all batch components

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

- [ ] T022 [P] [US2] Unit test for percentage sorting in tests/unit/test_percentage_sorting.py (verify descending order, TDD - write FIRST)
- [ ] T023 [P] [US2] Integration test for complete ingredient breakdown in tests/integration/test_inci_percentage_breakdown.py (oils + water + lye + additives, TDD - write FIRST)
- [ ] T024 [P] [US2] Property-based test for percentage sum validation using Hypothesis in tests/unit/test_percentage_sum.py (sum ≈ 100%, TDD - write FIRST)

### Implementation for User Story 2

- [ ] T025 [US2] Extend percentage calculator in app/services/percentage_calculator.py to handle all ingredient types (oils, water, lye, additives)
- [ ] T026 [US2] Implement sorting logic in app/services/label_generator.py (sort_ingredients_by_percentage method)
- [ ] T027 [US2] Add ingredients_breakdown array to response in app/services/label_generator.py (with percentages, categories, notes)
- [ ] T028 [US2] Integrate percentage-based sorting with format generation in app/services/label_generator.py (apply to all three formats)
- [ ] T029 [US2] Add water percentage calculation from batch data in app/services/percentage_calculator.py
- [ ] T030 [US2] Add lye percentage calculation (NaOH + KOH combined) in app/services/percentage_calculator.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - all formats with proper percentage sorting

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, optimization, and validation improvements affecting multiple stories

- [⚠️] T031 [P] Create integration guide in specs/003-inci-label-generator/quickstart.md with curl/httpx/requests examples (EXISTS but documents WRONG API - POST /inci/generate-label vs. GET /recipes/{id}/inci-label)
- [❌] T032 [P] Generate OpenAPI documentation and verify accuracy against contracts/inci-label.yaml (MISMATCH: contract describes different endpoint than implementation)
- [🔄] T033 Run full test suite with coverage report (target ≥90% coverage per constitution) (BLOCKED: needs docker-compose up -d app)
- [🔄] T034 [P] Run type checking with mypy --strict across all new modules (BLOCKED: needs container environment)
- [🔄] T035 [P] Run linting with Ruff and formatting with Black (BLOCKED: needs container environment)
- [🔄] T036 Performance optimization: Profile label generation for <100ms response time target (BLOCKED: needs profiling setup)
- [🔄] T037 Load testing: Verify 100+ concurrent requests meet <100ms p95 latency requirement (BLOCKED: needs load test script)
- [❌] T038 [P] Add metadata field to response in app/schemas/inci_label.py (total_ingredients, calculation_method, lye_type, superfat_percentage) (NOT IMPLEMENTED - schema missing metadata field)
- [🔄] T039 Security scan with Bandit for vulnerability assessment (BLOCKED: needs bandit install or container)
- [❌] T040 Validate quickstart.md examples work correctly with live API (CANNOT VALIDATE - examples use wrong endpoint/method)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T005) - BLOCKS all user stories
- **User Stories (Phase 3+)**: Both depend on Foundational phase completion (T006-T011)
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2)
- **Polish (Phase 5)**: Depends on both user stories being complete (T012-T030)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - T012-T021 have no dependencies on US2
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - T022-T030 integrate with US1 services but are independently testable

### Within Each User Story

- Tests (T012-T015 for US1, T022-T024 for US2) MUST be written FIRST and FAIL before implementation
- Schemas before services (T016 before T017)
- Services before endpoints (T017 before T018)
- Core implementation before edge cases (T017-T018 before T019-T020)
- Percentage calculation before sorting (T025 before T026 for US2)
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T002, T003, T005) marked [P] can run in parallel after T001
- All Foundational tests (T006, T007, T008) can run in parallel
- Foundational implementations (T009, T010) can run in parallel after tests written
- All US1 tests (T012-T015) can run in parallel
- All US2 tests (T022-T024) can run in parallel
- Once Foundational phase completes, both user stories can start in parallel (if team capacity allows)
- All Polish tasks (T031, T032, T034, T035, T038, T039) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write these FIRST):
Task T012: "Contract test for raw INCI format in tests/integration/test_inci_endpoint_raw.py"
Task T013: "Contract test for saponified INCI format in tests/integration/test_inci_endpoint_saponified.py"
Task T014: "Contract test for common names format in tests/integration/test_inci_endpoint_common.py"
Task T015: "Integration test for format parameter handling in tests/integration/test_inci_format_selection.py"

# After tests written and failing (Red phase), implement:
Task T016: "Create Pydantic schemas in app/schemas/inci_label.py"
Task T017: "Implement label generator service in app/services/label_generator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T012-T021)
4. **STOP and VALIDATE**: Test User Story 1 independently - verify all three formats work
5. Deploy/demo if ready (MVP with multiple format support)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T011)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - three format variants!)
3. Add User Story 2 → Test independently → Deploy/Demo (percentage sorting compliance)
4. Complete Polish → Final production-ready release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T021)
   - Developer B: User Story 2 (T022-T030)
   - Developer C: Can start Polish tasks that don't block others (documentation, OpenAPI validation)
3. Stories complete and integrate independently

---

## TDD Workflow (MANDATORY)

### Red-Green-Refactor Cycle

**Red Phase** (Tests First):
- Write unit tests (T006-T008)
- Write integration tests (T012-T015 for US1, T022-T024 for US2)
- Write property-based tests with Hypothesis (T008, T024)
- **Verify tests FAIL** (no implementation exists yet)

**Green Phase** (Minimal Implementation):
- Implement services (T009-T010, T017, T025-T027)
- Implement API endpoint (T018)
- **Verify tests PASS** (implementation satisfies requirements)

**Refactor Phase** (Optimization):
- Performance optimization (T036)
- Code clarity improvements
- Edge case handling (T019-T020)
- **Verify tests STILL PASS** (refactoring doesn't break functionality)

### Test Coverage Requirements

Per MGA Soap Calculator constitution:
- ✅ Unit test coverage ≥90%
- ✅ Integration tests for all API endpoints
- ✅ Property-based tests for calculation edge cases
- ✅ Type checking with mypy --strict
- ✅ Linting with Ruff and Black

---

## Notes

- [P] tasks = different files, no dependencies, can run concurrently
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **CRITICAL**: Tests MUST be written before implementation per constitution TDD requirement
- Verify tests fail (Red phase) before implementing
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Performance target: <100ms response time (stricter than standard <200ms budget)
- All database operations use SQLAlchemy 2.0 async patterns
- JWT authentication required for recipe access
- Reference data: 37 oils with saponified INCI names
