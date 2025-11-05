# Tasks: KOH/NaOH Purity Support

**Branch**: `002-lye-purity` | **Input**: Design documents from `/specs/002-lye-purity/`
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/

**⚠️ SAFETY-CRITICAL BREAKING CHANGE**: Default KOH purity changes from 100% to 90%

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3, US4, US5)
- All tasks include exact file paths

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 Create feature branch `002-lye-purity` from main
- [ ] T002 [P] Review spec.md for safety-critical requirements
- [ ] T003 [P] Review plan.md for TDD workflow and file changes
- [ ] T004 [P] Verify constitution compliance checklist in plan.md

**Checkpoint**: Branch created and specification understood

---

## Phase 2: Foundational (TDD Infrastructure)

**Purpose**: Test file structure and base validation - BLOCKS all user story work

**⚠️ CRITICAL**: These tests must exist and FAIL before ANY implementation begins

### Test Infrastructure Setup

- [ ] T010 [P] Create `tests/unit/test_saponification.py` with failing purity test stubs
- [ ] T011 [P] Create `tests/unit/test_purity_validation.py` with failing boundary tests
- [ ] T012 [P] Create `tests/unit/test_purity_warnings.py` with failing warning generation tests
- [ ] T013 [P] Create `tests/property/test_purity_properties.py` with Hypothesis test stubs
- [ ] T014 [P] Create `tests/integration/test_purity_api.py` with failing API tests
- [ ] T015 [P] Create `tests/integration/test_backward_compat.py` with breaking change tests

### Base Schema Enhancement (Enables All Stories)

- [ ] T020 [P] Add `koh_purity` Optional[float] field to LyeConfig in `app/schemas/requests.py` (default=90.0, ge=50.0, le=100.0)
- [ ] T021 [P] Add `naoh_purity` Optional[float] field to LyeConfig in `app/schemas/requests.py` (default=100.0, ge=50.0, le=100.0)
- [ ] T022 Add lye percentage sum validator to LyeConfig in `app/schemas/requests.py`
- [ ] T023 [P] Add purity fields to LyeResult in `app/schemas/responses.py` (koh_purity, naoh_purity)
- [ ] T024 [P] Add pure equivalent fields to LyeResult in `app/schemas/responses.py` (pure_koh_equivalent_g, pure_naoh_equivalent_g)
- [ ] T025 [P] Create WarningMessage schema in `app/schemas/responses.py` (type, message)
- [ ] T026 Add warnings array to CalculationResponse in `app/schemas/responses.py`

### Database Schema (Enables Persistence for All Stories)

- [ ] T030 [P] Add `koh_purity` DECIMAL(5,2) column to Calculation model in `app/models/calculation.py` (nullable=False, default=90.0)
- [ ] T031 [P] Add `naoh_purity` DECIMAL(5,2) column to Calculation model in `app/models/calculation.py` (nullable=False, default=100.0)
- [ ] T032 [P] Add `purity_assumed` BOOLEAN column to Calculation model in `app/models/calculation.py` (nullable=False, default=False)
- [ ] T033 Add CheckConstraint for koh_purity range (50-100) in `app/models/calculation.py`
- [ ] T034 Add CheckConstraint for naoh_purity range (50-100) in `app/models/calculation.py`

### Database Migration (Critical for Deployment)

- [ ] T040 Create Alembic migration `alembic/versions/<timestamp>_add_lye_purity.py`
- [ ] T041 Add purity columns with defaults in migration upgrade()
- [ ] T042 Update existing recipes to koh_purity=100.0 and purity_assumed=true in migration
- [ ] T043 Add database constraints in migration upgrade()
- [ ] T044 Implement migration downgrade() with column removal
- [ ] T045 Test migration in dev environment (upgrade + downgrade)

**Checkpoint**: Foundation complete - ALL tests exist and FAIL - User stories can now implement features in parallel

---

## Phase 3: US1 - Commercial 90% KOH Calculation (Priority: P1) 🎯 MVP

**Goal**: Calculate correct commercial KOH weight for 90% purity (130.1g for 117.1g pure @ 90%)

**Independent Test**: POST /calculate with koh_purity=90 returns koh_weight_g=130.1 ± 0.5g

### Tests for US1 (TDD - Write FIRST) ⚠️

**CRITICAL**: Run these tests, verify they FAIL before implementation

- [ ] T050 [P] [US1] Write unit test `test_purity_adjustment_formula_90_percent_koh` in `tests/unit/test_saponification.py`
- [ ] T051 [P] [US1] Write unit test `test_100_percent_purity_equals_pure_weight` in `tests/unit/test_saponification.py`
- [ ] T052 [P] [US1] Write unit test `test_mixed_lye_independent_purity_adjustment` in `tests/unit/test_saponification.py`
- [ ] T053 [P] [US1] Write property test `test_purity_always_increases_commercial_weight` in `tests/property/test_purity_properties.py`
- [ ] T054 [P] [US1] Write API integration test `test_purity_api_90_percent_koh` in `tests/integration/test_purity_api.py`
- [ ] T055 [US1] Run US1 tests → Verify ALL FAIL (no implementation yet)

### Implementation for US1 (GREEN Phase)

- [ ] T060 [US1] Implement purity adjustment calculation in `app/core/saponification.py` calculate_lye_requirements()
- [ ] T061 [US1] Add koh_purity parameter (default=90.0) to calculate_lye_requirements() in `app/core/saponification.py`
- [ ] T062 [US1] Add naoh_purity parameter (default=100.0) to calculate_lye_requirements() in `app/core/saponification.py`
- [ ] T063 [US1] Calculate commercial_koh_weight = pure_koh_needed / (koh_purity / 100) in `app/core/saponification.py`
- [ ] T064 [US1] Calculate commercial_naoh_weight = pure_naoh_needed / (naoh_purity / 100) in `app/core/saponification.py`
- [ ] T065 [US1] Return purity values in LyeResult from calculate_lye_requirements() in `app/core/saponification.py`
- [ ] T066 [US1] Return pure equivalents in LyeResult from calculate_lye_requirements() in `app/core/saponification.py`
- [ ] T067 [US1] Update calculation_service.py to pass purity from LyeConfig to saponification module
- [ ] T068 [US1] Run US1 tests → Verify ALL PASS ✅

**Checkpoint**: US1 complete - API correctly calculates 90% KOH commercial weight

---

## Phase 4: US2 - Validation Prevents Dangerous Purity Values (Priority: P1) 🎯 SAFETY

**Goal**: Reject purity values <50% or >100% with clear 400 Bad Request errors

**Independent Test**: POST /calculate with koh_purity=49 returns 400 with error message

### Tests for US2 (TDD - Write FIRST) ⚠️

- [ ] T070 [P] [US2] Write test `test_purity_below_50_rejected` in `tests/unit/test_purity_validation.py`
- [ ] T071 [P] [US2] Write test `test_purity_above_100_rejected` in `tests/unit/test_purity_validation.py`
- [ ] T072 [P] [US2] Write test `test_purity_boundaries_accepted` (50%, 100%) in `tests/unit/test_purity_validation.py`
- [ ] T073 [P] [US2] Write test `test_negative_purity_rejected` in `tests/unit/test_purity_validation.py`
- [ ] T074 [P] [US2] Write test `test_zero_purity_rejected` in `tests/unit/test_purity_validation.py`
- [ ] T075 [P] [US2] Write API test `test_purity_validation_rejects_invalid` in `tests/integration/test_purity_api.py`
- [ ] T076 [US2] Run US2 tests → Verify ALL FAIL (no validation yet)

### Implementation for US2 (GREEN Phase)

- [ ] T080 [US2] Implement Pydantic Field constraints (ge=50.0, le=100.0) for koh_purity in `app/schemas/requests.py`
- [ ] T081 [US2] Implement Pydantic Field constraints (ge=50.0, le=100.0) for naoh_purity in `app/schemas/requests.py`
- [ ] T082 [US2] Add custom error messages for out-of-range purity in LyeConfig validators in `app/schemas/requests.py`
- [ ] T083 [US2] Verify FastAPI returns 400 Bad Request for validation failures (automatic via Pydantic)
- [ ] T084 [US2] Run US2 tests → Verify ALL PASS ✅

**Checkpoint**: US2 complete - Dangerous purity values blocked with clear error messages

---

## Phase 5: US3 - Warning for Unusual Purity Values (Priority: P2)

**Goal**: Non-blocking warnings for purity outside commercial ranges (KOH: 85-95%, NaOH: 98-100%)

**Independent Test**: POST /calculate with koh_purity=75 includes warning in response.warnings[]

### Tests for US3 (TDD - Write FIRST) ⚠️

- [ ] T090 [P] [US3] Write test `test_koh_below_85_generates_warning` in `tests/unit/test_purity_warnings.py`
- [ ] T091 [P] [US3] Write test `test_koh_above_95_generates_warning` in `tests/unit/test_purity_warnings.py`
- [ ] T092 [P] [US3] Write test `test_naoh_below_98_generates_warning` in `tests/unit/test_purity_warnings.py`
- [ ] T093 [P] [US3] Write test `test_typical_purity_no_warnings` (90% KOH) in `tests/unit/test_purity_warnings.py`
- [ ] T094 [P] [US3] Write API test `test_warnings_included_in_response` in `tests/integration/test_purity_api.py`
- [ ] T095 [US3] Run US3 tests → Verify ALL FAIL (no warning logic yet)

### Implementation for US3 (GREEN Phase)

- [ ] T100 [US3] Implement @model_validator `generate_purity_warnings` in LyeConfig in `app/schemas/requests.py`
- [ ] T101 [US3] Add KOH <85% warning logic to validator in `app/schemas/requests.py`
- [ ] T102 [US3] Add KOH >95% warning logic to validator in `app/schemas/requests.py`
- [ ] T103 [US3] Add NaOH <98% warning logic to validator in `app/schemas/requests.py`
- [ ] T104 [US3] Store warnings in LyeConfig.__warnings__ custom attribute in `app/schemas/requests.py`
- [ ] T105 [US3] Pass warnings from LyeConfig to CalculationResponse in `app/services/calculation_service.py`
- [ ] T106 [US3] Run US3 tests → Verify ALL PASS ✅

**Checkpoint**: US3 complete - Unusual purity values generate helpful warnings

---

## Phase 6: US4 - Mixed Lye Purity in Same Recipe (Priority: P2)

**Goal**: Independent purity adjustment for KOH and NaOH in dual-lye recipes

**Independent Test**: POST /calculate with koh_purity=90, naoh_purity=98 adjusts each independently

### Tests for US4 (TDD - Write FIRST) ⚠️

- [ ] T110 [P] [US4] Write test `test_mixed_lye_different_purities` in `tests/unit/test_saponification.py`
- [ ] T111 [P] [US4] Write test `test_single_koh_only_purity_adjustment` in `tests/unit/test_saponification.py`
- [ ] T112 [P] [US4] Write test `test_naoh_defaults_to_100_when_omitted` in `tests/unit/test_saponification.py`
- [ ] T113 [P] [US4] Write property test `test_purity_inverse_relationship` in `tests/property/test_purity_properties.py`
- [ ] T114 [US4] Run US4 tests → Verify ALL FAIL or PASS (may already work from US1)

### Implementation for US4 (GREEN Phase)

- [ ] T120 [US4] Verify independent purity adjustment logic in `app/core/saponification.py` (likely already implemented in US1)
- [ ] T121 [US4] Test mixed lye scenario manually via Swagger UI
- [ ] T122 [US4] Run US4 tests → Verify ALL PASS ✅

**Checkpoint**: US4 complete - Mixed lye recipes handle different purities correctly

---

## Phase 7: US5 - Response Schema Clarity (Priority: P3)

**Goal**: Response includes all purity-related fields for transparency and documentation

**Independent Test**: POST /calculate response includes koh_purity, naoh_purity, pure_koh_equivalent_g, pure_naoh_equivalent_g

### Tests for US5 (TDD - Write FIRST) ⚠️

- [ ] T130 [P] [US5] Write test `test_response_includes_purity_fields` in `tests/integration/test_purity_api.py`
- [ ] T131 [P] [US5] Write test `test_response_includes_pure_equivalents` in `tests/integration/test_purity_api.py`
- [ ] T132 [P] [US5] Write test `test_default_90_percent_echoed_in_response` in `tests/integration/test_purity_api.py`
- [ ] T133 [P] [US5] Write test `test_decimal_rounding_to_1_place_in_response` in `tests/integration/test_purity_api.py`
- [ ] T134 [US5] Run US5 tests → Verify ALL FAIL or PASS (may already work from foundational)

### Implementation for US5 (GREEN Phase)

- [ ] T140 [US5] Verify response schema completeness in LyeResult in `app/schemas/responses.py` (likely already complete)
- [ ] T141 [US5] Add JSON encoder for 1 decimal display in LyeResult Config in `app/schemas/responses.py`
- [ ] T142 [US5] Verify OpenAPI documentation auto-generated with purity fields (FastAPI automatic)
- [ ] T143 [US5] Run US5 tests → Verify ALL PASS ✅

**Checkpoint**: US5 complete - Response schema provides full transparency

---

## Phase 8: Backward Compatibility & Breaking Change (CRITICAL)

**Goal**: Verify default 90% KOH behavior and tag legacy recipes

**⚠️ BREAKING CHANGE**: Omitted koh_purity now defaults to 90% (was 100%)

### Tests for Breaking Change (TDD - Write FIRST) ⚠️

- [ ] T150 [P] Write test `test_omitted_koh_purity_defaults_to_90` in `tests/integration/test_backward_compat.py`
- [ ] T151 [P] Write test `test_explicit_100_percent_preserves_legacy` in `tests/integration/test_backward_compat.py`
- [ ] T152 [P] Write test `test_naoh_defaults_to_100_unchanged` in `tests/integration/test_backward_compat.py`
- [ ] T153 [P] Write test `test_legacy_recipes_tagged_with_purity_assumed` in `tests/integration/test_backward_compat.py`
- [ ] T154 Run backward compatibility tests → Verify behavior

### Implementation for Breaking Change

- [ ] T160 Verify koh_purity default=90.0 in LyeConfig in `app/schemas/requests.py` (should be set from foundational)
- [ ] T161 Verify naoh_purity default=100.0 in LyeConfig in `app/schemas/requests.py` (should be set from foundational)
- [ ] T162 Verify migration sets purity_assumed=true for existing recipes in Alembic migration
- [ ] T163 Test migration rollback preserves data integrity
- [ ] T164 Run backward compatibility tests → Verify ALL PASS ✅

**Checkpoint**: Breaking change verified - Migration strategy validated

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and deployment readiness

### Code Quality & Testing

- [ ] T170 [P] Run full test suite: `pytest tests/ --cov=app --cov-report=term-missing`
- [ ] T171 [P] Verify code coverage ≥90% across all purity modules
- [ ] T172 [P] Run property-based tests with 1000+ examples via Hypothesis
- [ ] T173 [P] Extract purity calculation to helper function if needed (refactor)
- [ ] T174 Add inline documentation for purity formulas in `app/core/saponification.py`

### Manual Validation

- [ ] T180 [P] Test 90% KOH scenario via Swagger UI with user feedback recipe (700g oils)
- [ ] T181 [P] Test validation boundaries (49%, 50%, 100%, 101%) via Swagger UI
- [ ] T182 [P] Test warning generation (75% KOH, 98% KOH) via Swagger UI
- [ ] T183 [P] Test mixed lye with different purities via Swagger UI
- [ ] T184 Verify accuracy within 0.5g tolerance for reference test case

### Documentation

- [ ] T190 [P] Verify OpenAPI documentation includes purity parameters (FastAPI auto-generated)
- [ ] T191 [P] Document breaking change in CHANGELOG.md with migration guide
- [ ] T192 [P] Create migration guide for API users in `docs/MIGRATION_v2.0.md`
- [ ] T193 Document purity feature in API reference (minimal prominence per user decision)

### Deployment Preparation

- [ ] T200 Update Ansible playbook for migration execution in `ansible/playbooks/deploy-api.yml`
- [ ] T201 Add migration verification step to Ansible playbook
- [ ] T202 Test Ansible playbook in dev environment
- [ ] T203 Draft user communication email for breaking change (30-day notice)
- [ ] T204 Obtain stakeholder approval for 90% KOH default ⚠️ REQUIRED

### Final Validation (Constitution Compliance)

- [ ] T210 [P] Verify Principle I (API-First): OpenAPI complete, no frontend changes
- [ ] T211 [P] Verify Principle II (Research-Backed): Industry standards documented
- [ ] T212 [P] Verify Principle III (Test-First): TDD followed, all tests pass
- [ ] T213 [P] Verify Principle IV (Data Integrity): Migration tested, ACID compliance
- [ ] T214 [P] Verify Principle V (Performance): <5ms overhead, <200ms p95 response
- [ ] T215 [P] Verify Principle VI (Security): Pydantic validation, fail-safe design
- [ ] T216 [P] Verify Principle VII (Deployment): Ansible playbook ready
- [ ] T217 [P] Verify Principle VIII (Observability): Logging, error tracking configured

**Checkpoint**: Feature complete and ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Setup → BLOCKS all user stories
- **Phase 3-7 (User Stories)**: All depend on Foundational completion
  - US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P3) (priority order)
  - OR work in parallel if team capacity allows (independent stories)
- **Phase 8 (Breaking Change)**: Depends on US1 completion (default behavior validation)
- **Phase 9 (Polish)**: Depends on all desired stories complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - no other story dependencies
- **US2 (P1)**: Foundation only - independent from US1 (validation separate from calculation)
- **US3 (P2)**: Foundation only - independent from US1/US2 (warning generation)
- **US4 (P2)**: Depends on US1 (uses calculation logic) but should be independently testable
- **US5 (P3)**: Depends on Foundation (response schema) - may already work from foundational phase

### TDD Workflow (Within Each Story)

1. Write ALL tests for story (T050-T055 for US1)
2. Run tests → Verify ALL FAIL (RED phase)
3. Implement feature (T060-T067 for US1)
4. Run tests → Verify ALL PASS (GREEN phase)
5. Refactor if needed (optimize, extract helpers)
6. Move to next story

### Parallel Opportunities

**Setup Phase**:
- T002, T003, T004 can run in parallel (different review tasks)

**Foundational Phase**:
- T010-T015 (test file creation) can run in parallel
- T020-T026 (schema fields) can run in parallel
- T030-T034 (database columns) can run in parallel

**Within User Stories**:
- All test writing tasks marked [P] can run in parallel (different test files)
- Model/schema tasks marked [P] can run in parallel (different files)

**Polish Phase**:
- T170-T174 (testing/quality) can run in parallel
- T180-T184 (manual validation) can run in parallel
- T190-T193 (documentation) can run in parallel
- T210-T217 (constitution checks) can run in parallel

**Multiple Stories in Parallel** (if team capacity):
- After Foundational complete, US1 + US2 + US3 can proceed in parallel
- US4 should wait for US1 (depends on calculation logic)
- US5 can proceed after Foundational (may already work)

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

1. Phase 1: Setup (T001-T004)
2. Phase 2: Foundational (T010-T045) → **CRITICAL GATE**
3. Phase 3: US1 only (T050-T068) → **MVP COMPLETE**
4. STOP → Test independently → Validate 90% KOH calculation
5. Deploy if ready, or continue with P1 stories

### Incremental Delivery (All P1 Stories)

1. Setup + Foundational → Foundation ready
2. US1 (90% calculation) → Test → MVP ✅
3. US2 (validation) → Test → Safety ✅
4. Breaking change validation → Ready for production
5. US3-US5 can follow in later releases if needed

### Full Feature Delivery (All Stories)

1. Setup + Foundational (T001-T045)
2. All user stories (T050-T143)
3. Breaking change validation (T150-T164)
4. Polish (T170-T217)
5. Production deployment with migration

---

## Success Criteria

After completing all tasks, verify:

- ✅ SC-001: API calculates 130.1g ± 0.5g for 700g oils recipe with 90% KOH
- ✅ SC-002: All boundary values (49%, 50%, 100%, 101%) validated correctly
- ✅ SC-003: Breaking change documented with migration guide
- ✅ SC-004: Warnings generated for 100% of unusual purity values (75% KOH, 97% NaOH)
- ✅ SC-005: Property-based tests pass for 1000+ random valid purity combinations
- ✅ SC-006: Response includes all purity fields (koh_weight_g, koh_purity, pure_koh_equivalent_g)
- ✅ SC-007: Cost calculations use commercial weights only (not pure equivalents)
- ✅ SC-008: Documentation mentions purity in API reference (minimal prominence)
- ✅ SC-009: Code coverage >90% with comprehensive purity tests
- ✅ SC-010: Zero safety incidents (monitoring post-deployment)
- ✅ SC-011: All existing recipes tagged with purity_assumed=true
- ✅ SC-012: 2 decimal precision accepted, 1 decimal displayed
- ✅ SC-013: Purity >100% rejected with clear error

---

## Notes

- **TDD MANDATORY**: All tests written BEFORE implementation per constitution
- **Safety-Critical**: Zero tolerance for calculation errors (chemical burn risk)
- **Breaking Change**: Requires explicit stakeholder approval before production
- **[P] marker**: Tasks can run in parallel (different files, no dependencies)
- **[Story] label**: Maps task to user story for traceability
- **Constitution**: All 8 principles must pass before production deployment
- **Migration**: Test in dev, validate rollback, backup before production
- Commit after each task or logical group
- Stop at checkpoints to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies

---

**Total Tasks**: 107 (setup → foundational → 5 user stories → breaking change → polish)
**Estimated Time**: 20-27 hours (per plan.md)
**Next Command**: Start with T001 or use `/speckit.implement` for automated execution
