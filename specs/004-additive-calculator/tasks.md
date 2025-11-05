# Tasks: Smart Additive Calculator (Feature 004)

**Input**: Design documents from `/specs/004-additive-calculator/`
**Prerequisites**: plan.md, spec.md, data sources (3 JSON files with 122 ingredients)

**TDD Protocol**: All tests MUST be written FIRST and FAIL before implementation begins

**Branch**: `004-additive-calculator`

---

## Phase 1: Setup (Foundation)

**Purpose**: Project structure verification and data source validation

- [ ] T001 Review spec.md to understand 6 user stories and their priorities (P1, P2, P3)
- [ ] T002 Review plan.md to understand database schema (3 tables, 8 fields per table)
- [ ] T003 [P] Verify existing Oil model pattern in `app/models/oil.py` for replication
- [ ] T004 [P] Verify existing resources API pattern in `app/api/v1/resources.py` for replication
- [ ] T005 [P] Validate data sources (19 additives + 24 essential oils + 79 colorants = 122 total)
- [ ] T006 Create feature branch `004-additive-calculator` from main

**Checkpoint**: Foundation ready - understand patterns and data structure

---

## Phase 2: Foundational (Database + TDD Infrastructure) ⚠️ BLOCKS ALL USER STORIES

**Purpose**: Core database models, migrations, and test infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models (TDD Cycle: Tests → RED → Implementation → GREEN)

- [ ] T007 [P] Write model tests for Additive extension in `tests/unit/test_additive_model_extended.py`
  - Field validation (usage_rate_standard_percent, when_to_add, category)
  - Warning flags (accelerates_trace, causes_overheating, can_be_scratchy, turns_brown)
  - JSONB fields (preparation_instructions, mixing_tips)
  - Tests MUST FAIL (model not yet extended)

- [ ] T008 [P] Write model tests for EssentialOil in `tests/unit/test_essential_oil_model.py`
  - Required fields (name, botanical_name, max_usage_rate_pct)
  - Optional fields (scent_profile, note, category, warnings)
  - JSONB field (blends_with array)
  - Usage rate validation (0.025% - 3.0%)
  - Tests MUST FAIL (model doesn't exist)

- [ ] T009 [P] Write model tests for Colorant in `tests/unit/test_colorant_model.py`
  - Required fields (name, botanical, category, method, color_range)
  - Optional fields (usage, warnings)
  - Category validation (yellow, orange, pink, red, green, blue, purple, brown, black)
  - Tests MUST FAIL (model doesn't exist)

- [ ] T010 Extend Additive model in `app/models/additive.py` with new calculator fields
  - Add: usage_rate_standard_percent (float)
  - Add: when_to_add (str: "to oils", "to lye water", "at trace")
  - Add: preparation_instructions (text, nullable)
  - Add: mixing_tips (text, nullable)
  - Add: category (str: "exfoliant", "colorant", "lather_booster", "hardener", "clay", "botanical", "luxury_additive", "skin_benefit")
  - Add: accelerates_trace (bool, default False)
  - Add: causes_overheating (bool, default False)
  - Add: can_be_scratchy (bool, default False)
  - Add: turns_brown (bool, default False)
  - Tests MUST NOW PASS (T007)

- [ ] T011 Create EssentialOil model in `app/models/essential_oil.py`
  - Fields: id, name, botanical_name, max_usage_rate_pct (float), scent_profile (text)
  - Fields: blends_with (JSONB array), note (str: "Top", "Middle", "Base")
  - Fields: category (str: "citrus", "floral", "herbal", "woodsy", "earthy", "spice")
  - Fields: warnings (text, nullable), color_effect (text, nullable)
  - Fields: confidence_level, verified_by_mga (from existing pattern)
  - Tests MUST NOW PASS (T008)

- [ ] T012 Create Colorant model in `app/models/colorant.py`
  - Fields: id, name, botanical, category (str: yellow/orange/pink/red/green/blue/purple/brown/black)
  - Fields: usage (str: descriptive usage rates), method (str: infuse/add at trace/add to lye)
  - Fields: color_range (str: expected outcome), warnings (text, nullable)
  - Fields: confidence_level, verified_by_mga
  - Tests MUST NOW PASS (T009)

### Database Migrations

- [ ] T013 Create Alembic migration `alembic/versions/YYYYMMDD_HHMM_extend_additives_table.py`
  - ALTER TABLE additives ADD COLUMN usage_rate_standard_percent FLOAT
  - ALTER TABLE additives ADD COLUMN when_to_add VARCHAR(50)
  - ALTER TABLE additives ADD COLUMN preparation_instructions TEXT
  - ALTER TABLE additives ADD COLUMN mixing_tips TEXT
  - ALTER TABLE additives ADD COLUMN category VARCHAR(50)
  - ALTER TABLE additives ADD COLUMN accelerates_trace BOOLEAN DEFAULT FALSE
  - ALTER TABLE additives ADD COLUMN causes_overheating BOOLEAN DEFAULT FALSE
  - ALTER TABLE additives ADD COLUMN can_be_scratchy BOOLEAN DEFAULT FALSE
  - ALTER TABLE additives ADD COLUMN turns_brown BOOLEAN DEFAULT FALSE
  - Include downgrade migration (DROP COLUMN for rollback)

- [ ] T014 Create Alembic migration `alembic/versions/YYYYMMDD_HHMM_create_essential_oils_table.py`
  - CREATE TABLE essential_oils with all fields from EssentialOil model
  - Add indexes: id (primary), name, category, max_usage_rate_pct
  - Include downgrade migration (DROP TABLE)

- [ ] T015 Create Alembic migration `alembic/versions/YYYYMMDD_HHMM_create_colorants_table.py`
  - CREATE TABLE colorants with all fields from Colorant model
  - Add indexes: id (primary), name, category
  - Include downgrade migration (DROP TABLE)

- [ ] T016 Apply all 3 migrations locally: `alembic upgrade head`
- [ ] T017 Verify schema with `psql` inspection (3 tables, correct fields, indexes)

### Import Scripts (TDD Cycle: Tests → RED → Implementation → GREEN)

- [ ] T018 [P] Write import script tests in `tests/unit/test_import_additives_extended.py`
  - JSON parsing validation (19 additives from `additives-usage-reference.json`)
  - Data transformation tests (tablespoon → percentage conversion)
  - Database insertion tests (SQLAlchemy session management)
  - Idempotency tests (re-import doesn't duplicate)
  - Tests MUST FAIL (script doesn't exist)

- [ ] T019 [P] Write import script tests in `tests/unit/test_import_essential_oils.py`
  - JSON parsing validation (24 EOs from `essential-oils-usage-reference.json`)
  - Max usage rate validation (0.025% to 3.0%)
  - JSONB field handling (blends_with array)
  - Idempotency tests
  - Tests MUST FAIL (script doesn't exist)

- [ ] T020 [P] Write import script tests in `tests/unit/test_import_colorants.py`
  - JSON parsing validation (79 colorants from `natural-colorants-reference.json`)
  - Category distribution tests (9 color families)
  - Idempotency tests
  - Tests MUST FAIL (script doesn't exist)

- [ ] T021 Implement `scripts/import_additives_extended.py`
  - Load JSON from `working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json`
  - Parse 19 additives with new calculator fields
  - Convert usage rates (1 tablespoon PPO = ~2%, 1 teaspoon PPO = ~1%)
  - Map warnings to boolean flags
  - Insert/update database with transaction management
  - Tests MUST NOW PASS (T018)

- [ ] T022 Implement `scripts/import_essential_oils.py`
  - Load JSON from `working/user-feedback/essential-oils-usage-reference.json`
  - Parse 24 essential oils with CPSR-validated max rates
  - Handle blends_with as JSONB array
  - Set confidence_level based on CPSR validation
  - Insert/update database with transaction management
  - Tests MUST NOW PASS (T019)

- [ ] T023 Implement `scripts/import_colorants.py`
  - Load JSON from `working/user-feedback/natural-colorants-reference.json`
  - Parse 79 colorants across 9 color families
  - Organize by category (yellow, orange, pink, red, green, blue, purple, brown, black)
  - Insert/update database with transaction management
  - Tests MUST NOW PASS (T020)

- [ ] T024 Run all 3 import scripts and verify data: `python scripts/import_additives_extended.py && python scripts/import_essential_oils.py && python scripts/import_colorants.py`
- [ ] T025 Verify database counts: 19 additives + 24 essential oils + 79 colorants = 122 total

### Test Infrastructure Setup

- [ ] T026 [P] Create test fixtures in `tests/conftest.py`
  - Sample Additive with calculator fields
  - Sample EssentialOil with max usage rates
  - Sample Colorant with color category
  - Database session fixtures

- [ ] T027 [P] Create integration test base in `tests/integration/base.py`
  - FastAPI TestClient setup
  - Database transaction rollback per test
  - Common assertion helpers

**Checkpoint**: Foundation COMPLETE - All user stories can now begin in parallel

---

## Phase 3: US1 - Calculate Additive Amount (P1 - MVP) 🎯

**Goal**: Auto-calculate additive amounts based on batch size
**Test Criteria**: Honey at 2% for 500g batch = 10g
**Independent Test**: `curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500" | jq '.recommendations.standard.amount_g'` → Expected: 10.0

### Tests for US1 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T028 [P] [US1] Contract test for recommendation response in `tests/contract/test_additive_recommendation.py`
  - Response schema validation (light/standard/heavy amounts)
  - Field presence (amount_g, amount_oz, usage_percentage)
  - Status code validation (200 for found, 404 for not found)
  - Tests MUST FAIL (endpoint doesn't exist)

- [ ] T029 [P] [US1] Integration test for recommendation endpoint in `tests/integration/test_recommendations_api.py`
  - Test honey recommendation: 500g batch → 10g (2% standard)
  - Test sodium lactate: 500g batch → 5g (1% standard)
  - Test batch size variations (100g, 500g, 1000g)
  - Test error cases (invalid additive_id, negative batch_size)
  - Tests MUST FAIL (endpoint doesn't exist)

- [ ] T030 [P] [US1] Unit test for calculation logic in `tests/unit/test_calculation_logic.py`
  - Formula validation: `(batch_size_g × usage_pct) / 100`
  - Rounding validation (1 decimal place)
  - Light/standard/heavy amount calculation
  - Gram to ounce conversion
  - Tests MUST FAIL (logic doesn't exist)

### Implementation for US1

- [ ] T031 [US1] Create recommendation schema in `app/schemas/recommendation.py`
  - AdditiveAmountResponse (amount_g, amount_oz, usage_percentage)
  - AdditiveRecommendationResponse (light, standard, heavy amounts + instructions)
  - Include when_to_add, preparation_instructions, mixing_tips fields

- [ ] T032 [US1] Implement calculation logic in `app/services/calculator.py`
  - Function: `calculate_additive_amount(usage_pct: float, batch_size_g: float) -> float`
  - Formula: `(batch_size_g × usage_pct) / 100`
  - Round to 1 decimal place
  - Convert grams to ounces (divide by 28.35)

- [ ] T033 [US1] Implement recommendation endpoint in `app/api/v1/recommendations.py`
  - Endpoint: `GET /api/v1/additives/{additive_id}/recommend?batch_size_g={size}`
  - Lookup additive by ID
  - Calculate light (usage_rate_min_percent), standard (usage_rate_standard_percent), heavy (usage_rate_max_percent)
  - Return AdditiveRecommendationResponse with all amounts and instructions
  - Handle 404 for invalid additive_id
  - Performance target: <50ms response time

- [ ] T034 [US1] Register recommendation endpoint in `app/main.py` router
- [ ] T035 [US1] Manual test with curl: `curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500"`
- [ ] T036 [US1] Verify all tests pass (T028, T029, T030)

**Checkpoint**: US1 COMPLETE - Additive amount calculation fully functional

---

## Phase 4: US2 - Usage Rate Recommendations (P1 - MVP)

**Goal**: Display light/standard/heavy usage options
**Test Criteria**: Sodium lactate shows 0.5%, 1%, 2% options (light/standard/heavy)
**Independent Test**: Recommendation response includes three usage levels with calculated amounts

### Tests for US2 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T037 [P] [US2] Contract test for usage levels in `tests/contract/test_usage_levels.py`
  - Verify light/standard/heavy structure
  - Verify percentage ranges (light < standard < heavy)
  - Verify all three levels present in response
  - Tests MUST FAIL (usage levels not implemented)

- [ ] T038 [P] [US2] Integration test for usage levels in `tests/integration/test_usage_levels_api.py`
  - Test sodium lactate: light 0.5%, standard 1%, heavy 2%
  - Test honey: light 1%, standard 2%, heavy 3%
  - Test calculation accuracy for all three levels
  - Tests MUST FAIL (usage levels not calculated)

### Implementation for US2

- [ ] T039 [US2] Extend recommendation schema in `app/schemas/recommendation.py`
  - Add usage_level field to AdditiveAmountResponse
  - Ensure light/standard/heavy structure with descriptions

- [ ] T040 [US2] Implement usage level logic in `app/services/calculator.py`
  - Function: `calculate_usage_levels(additive: Additive, batch_size_g: float)`
  - Calculate light: usage_rate_min_percent
  - Calculate standard: usage_rate_standard_percent
  - Calculate heavy: usage_rate_max_percent
  - Return three AdditiveAmountResponse objects

- [ ] T041 [US2] Update recommendation endpoint in `app/api/v1/recommendations.py`
  - Call calculate_usage_levels() for all three amounts
  - Include usage level descriptions ("Light for subtle effect", "Standard recommended", "Heavy for maximum effect")

- [ ] T042 [US2] Manual test with multiple additives (sodium lactate, honey, salt)
- [ ] T043 [US2] Verify all tests pass (T037, T038)

**Checkpoint**: US2 COMPLETE - Usage level recommendations working

---

## Phase 5: US3 - Warning System (P2)

**Goal**: Display warnings for problematic additives
**Test Criteria**: Honey shows "accelerates trace" + "causes overheating" warnings
**Independent Test**: Recommendation response includes warnings array with specific flags

### Tests for US3 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T044 [P] [US3] Contract test for warning structure in `tests/contract/test_warnings.py`
  - Verify warnings array in response
  - Verify warning message format
  - Verify empty warnings array for safe additives
  - Tests MUST FAIL (warnings not implemented)

- [ ] T045 [P] [US3] Integration test for warnings in `tests/integration/test_warnings_api.py`
  - Test honey: returns "accelerates trace", "causes overheating"
  - Test milk powder: returns "causes overheating"
  - Test ground botanicals: returns "can be scratchy", "turns brown"
  - Test salt: returns empty warnings array
  - Tests MUST FAIL (warning logic doesn't exist)

### Implementation for US3

- [ ] T046 [US3] Extend recommendation schema in `app/schemas/recommendation.py`
  - Add warnings: List[str] field to AdditiveRecommendationResponse

- [ ] T047 [US3] Implement warning builder in `app/services/calculator.py`
  - Function: `build_warnings(additive: Additive) -> List[str]`
  - Check accelerates_trace → "May accelerate trace - work quickly"
  - Check causes_overheating → "Can cause overheating - use cold process method"
  - Check can_be_scratchy → "May be scratchy - grind finely or use sparingly"
  - Check turns_brown → "Will turn brown in soap"
  - Return list of applicable warning messages

- [ ] T048 [US3] Update recommendation endpoint in `app/api/v1/recommendations.py`
  - Call build_warnings() for additive
  - Include warnings array in response

- [ ] T049 [US3] Manual test with honey, milk powder, ground herbs, salt
- [ ] T050 [US3] Verify all tests pass (T044, T045)

**Checkpoint**: US3 COMPLETE - Warning system operational

---

## Phase 6: US4 - Essential Oil Calculations (P2)

**Goal**: Calculate EO amounts with max rate validation
**Test Criteria**: Lavender at 3% for 500g = 15g (under 3% max rate)
**Independent Test**: `curl "http://localhost:8000/api/v1/essential-oils/lavender/recommend?batch_size_g=500"`

### Tests for US4 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T051 [P] [US4] Contract test for EO recommendation in `tests/contract/test_essential_oil_recommendation.py`
  - Response schema validation (amount_g, max_usage_rate_pct)
  - Scent profile and blending recommendations
  - Warning field presence
  - Tests MUST FAIL (endpoint doesn't exist)

- [ ] T052 [P] [US4] Integration test for EO endpoint in `tests/integration/test_essential_oils_api.py`
  - Test lavender: 500g batch → 15g (3% max rate)
  - Test rose otto: 500g batch → 0.125g (0.025% max rate - very low)
  - Test peppermint: 500g batch → 10g (2% max rate)
  - Test max rate validation (requested amount > max → warning)
  - Tests MUST FAIL (endpoint doesn't exist)

### Implementation for US4

- [ ] T053 [US4] Create EO recommendation schema in `app/schemas/recommendation.py`
  - EssentialOilRecommendationResponse (amount_g, amount_oz, max_usage_rate_pct)
  - Include scent_profile, blends_with, note, warnings fields

- [ ] T054 [US4] Implement EO calculation in `app/services/calculator.py`
  - Function: `calculate_essential_oil_amount(max_rate_pct: float, batch_size_g: float)`
  - Formula: `(batch_size_g × max_rate_pct) / 100`
  - Round to 1 decimal place
  - Validate requested amount ≤ max safe amount

- [ ] T055 [US4] Implement EO recommendation endpoint in `app/api/v1/recommendations.py`
  - Endpoint: `GET /api/v1/essential-oils/{eo_id}/recommend?batch_size_g={size}`
  - Lookup essential oil by ID
  - Calculate safe amount based on max_usage_rate_pct
  - Return EssentialOilRecommendationResponse with scent info and blending tips
  - Performance target: <50ms

- [ ] T056 [US4] Register EO endpoint in `app/main.py` router
- [ ] T057 [US4] Manual test with lavender, rose otto, peppermint
- [ ] T058 [US4] Verify all tests pass (T051, T052)

**Checkpoint**: US4 COMPLETE - Essential oil calculations working

---

## Phase 7: US5 - Category Browsing (P3)

**Goal**: Filter additives by category
**Test Criteria**: List exfoliants returns coffee grounds, oatmeal, poppy seeds, etc.
**Independent Test**: `curl "http://localhost:8000/api/v1/additives?category=exfoliant"`

### Tests for US5 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T059 [P] [US5] Contract test for category filtering in `tests/contract/test_category_filtering.py`
  - Verify category query parameter support
  - Verify pagination with category filter
  - Verify response structure matches existing resources pattern
  - Tests MUST FAIL (category filtering doesn't exist)

- [ ] T060 [P] [US5] Integration test for category filtering in `tests/integration/test_category_filtering_api.py`
  - Test exfoliant category (coffee grounds, oatmeal, etc.)
  - Test lather_booster category (honey, sugar, milk powder)
  - Test hardener category (beeswax, salt, sodium lactate)
  - Test invalid category returns empty results
  - Tests MUST FAIL (filtering not implemented)

### Implementation for US5

- [ ] T061 [US5] Extend resources API in `app/api/v1/resources.py`
  - Add category query parameter to `GET /api/v1/additives`
  - Filter query: `SELECT * FROM additives WHERE category = ?`
  - Maintain existing pagination pattern (limit, offset, has_more)

- [ ] T062 [US5] Update API schema in `app/schemas/resource.py`
  - Add category field to AdditiveListItem
  - Include category in response

- [ ] T063 [US5] Manual test with multiple categories (exfoliant, lather_booster, hardener)
- [ ] T064 [US5] Verify all tests pass (T059, T060)

**Checkpoint**: US5 COMPLETE - Category browsing functional

---

## Phase 8: US6 - Colorant Recommendations (P3)

**Goal**: Recommend colorants by desired color
**Test Criteria**: Query yellow colorants returns turmeric, calendula, lemon zest, etc.
**Independent Test**: `curl "http://localhost:8000/api/v1/colorants?category=yellow"`

### Tests for US6 (TDD: Write tests FIRST, ensure FAIL)

- [ ] T065 [P] [US6] Contract test for colorant listing in `tests/contract/test_colorant_listing.py`
  - Response schema validation (name, botanical, category, method, color_range)
  - Category filtering support
  - Pagination structure
  - Tests MUST FAIL (endpoint doesn't exist)

- [ ] T066 [P] [US6] Integration test for colorant API in `tests/integration/test_colorants_api.py`
  - Test yellow category (14 colorants: turmeric, calendula, etc.)
  - Test orange category (10 colorants: annatto, paprika, etc.)
  - Test all 9 color families (yellow, orange, pink, red, green, blue, purple, brown, black)
  - Test pagination with colorants
  - Tests MUST FAIL (endpoint doesn't exist)

### Implementation for US6

- [ ] T067 [US6] Create colorant list endpoint in `app/api/v1/resources.py`
  - Endpoint: `GET /api/v1/colorants?category={color}`
  - Query: `SELECT * FROM colorants WHERE category = ?`
  - Use pagination pattern (limit, offset, has_more)
  - Default sort by name

- [ ] T068 [US6] Create colorant schema in `app/schemas/resource.py`
  - ColorantListItem (name, botanical, category, usage, method, color_range, warnings)

- [ ] T069 [US6] Register colorant endpoint in `app/main.py` router
- [ ] T070 [US6] Manual test with multiple color families (yellow, orange, pink)
- [ ] T071 [US6] Verify all tests pass (T065, T066)

**Checkpoint**: US6 COMPLETE - Colorant recommendations working

---

## Phase 9: Enhanced Calculate Endpoint (Integration)

**Goal**: Accept additive selections in recipe calculation
**Test Criteria**: Recipe with honey additive auto-calculates honey amount
**Independent Test**: POST to /api/v1/calculate with additives array

### Tests (TDD: Write tests FIRST, ensure FAIL)

- [ ] T072 [P] Contract test for enhanced calculate in `tests/contract/test_calculate_enhanced.py`
  - Request schema with additives array
  - Response schema with additives_calculated array
  - Additive amount validation
  - Tests MUST FAIL (enhancement doesn't exist)

- [ ] T073 [P] Integration test for enhanced calculate in `tests/integration/test_calculate_enhanced_api.py`
  - Test recipe with single additive (honey at standard)
  - Test recipe with multiple additives (honey + oatmeal)
  - Test recipe with essential oil (lavender)
  - Test additive amount calculation accuracy
  - Tests MUST FAIL (enhancement doesn't exist)

### Implementation

- [ ] T074 Extend calculate request schema in `app/schemas/calculate.py`
  - Add additives: List[AdditiveSelection] (additive_id, usage_level: light/standard/heavy or numeric percent)

- [ ] T075 Extend calculate response schema in `app/schemas/calculate.py`
  - Add additives_calculated: List[CalculatedAdditive] (additive_id, amount_g, usage_percentage, when_to_add, warnings)

- [ ] T076 Implement additive processing in `app/services/calculator.py`
  - Function: `process_additive_selections(additives: List[AdditiveSelection], batch_size_g: float)`
  - For each additive: lookup in database, calculate amount, build warnings
  - Return List[CalculatedAdditive]

- [ ] T077 Update calculate endpoint in `app/api/v1/calculate.py`
  - Accept additives in request
  - Call process_additive_selections()
  - Include additives_calculated in response

- [ ] T078 Manual test with curl: recipe + honey + oatmeal
- [ ] T079 Verify all tests pass (T072, T073)

**Checkpoint**: Enhanced calculate COMPLETE - Full additive integration

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements, documentation, and deployment preparation

### Performance Validation

- [ ] T080 [P] Load test recommendation endpoints with Locust
  - Target: p95 <50ms for additive recommendations
  - Target: p95 <50ms for essential oil recommendations
  - Target: p95 <200ms for list endpoints
  - 100 concurrent users, 60 second duration

- [ ] T081 [P] Database performance validation
  - EXPLAIN ANALYZE on all queries
  - Verify index usage (category, name, id)
  - Add indexes if query plans show sequential scans

### Documentation

- [ ] T082 [P] Update OpenAPI documentation (auto-generated from FastAPI)
- [ ] T083 [P] Create API examples in `specs/004-additive-calculator/quickstart.md`
  - Example 1: Get honey recommendation
  - Example 2: List exfoliant additives
  - Example 3: Calculate lavender essential oil
  - Example 4: Recipe with honey and oatmeal

- [ ] T084 [P] Document data model in `specs/004-additive-calculator/data-model.md`
  - Extended Additive table schema
  - EssentialOil table schema
  - Colorant table schema
  - Relationship diagrams

### Quality Assurance

- [ ] T085 Run full test suite: `pytest tests/ -v --cov=app --cov-report=term-missing`
  - Target: >90% coverage
  - All tests passing

- [ ] T086 [P] Run type checking: `mypy app/ --strict`
- [ ] T087 [P] Run linting: `ruff check app/ tests/`
- [ ] T088 [P] Run formatting: `black --check app/ tests/`

### Deployment Preparation

- [ ] T089 Update Ansible playbook `ansible/playbooks/deploy-soap-calculator.yml`
  - Add migration step: `alembic upgrade head`
  - Add import step: run 3 import scripts
  - Add verification step: smoke tests

- [ ] T090 Create deployment guide in `DEPLOYMENT.md`
  - Migration sequence
  - Import script execution
  - Rollback procedure
  - Smoke test commands

- [ ] T091 Test deployment in local environment
  - Run Ansible playbook locally
  - Verify all 122 ingredients imported
  - Run smoke tests (5 curl commands from plan.md)

**Checkpoint**: Feature COMPLETE - Ready for staging deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - START HERE
- **Phase 2 (Foundational)**: Depends on Phase 1 - ⚠️ BLOCKS ALL USER STORIES
- **Phases 3-8 (User Stories)**: All depend on Phase 2 completion
  - Can proceed in parallel (if team capacity allows)
  - Or sequentially by priority: US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P3) → US6 (P3)
- **Phase 9 (Enhanced Calculate)**: Depends on US1-US4 completion
- **Phase 10 (Polish)**: Depends on all user stories completion

### Within Each Phase

**Phase 2 (Foundational)**:
- T007-T009 (model tests) can run in parallel [P]
- T010-T012 (models) sequential (after tests fail)
- T013-T015 (migrations) can run in parallel after models [P]
- T018-T020 (import tests) can run in parallel [P]
- T021-T023 (import scripts) sequential (after tests fail)

**Phase 3-8 (User Stories)**:
- Contract + integration tests within each story can run in parallel [P]
- Tests MUST FAIL before implementation
- Implementation sequential within story (schema → logic → endpoint)

**Phase 10 (Polish)**:
- T080-T084 (performance + docs) can all run in parallel [P]
- T086-T088 (quality checks) can all run in parallel [P]

### Parallel Opportunities

**Maximum Parallelization** (after Phase 2 completes):
```
Parallel Stream 1: US1 (T028-T036)
Parallel Stream 2: US2 (T037-T043)
Parallel Stream 3: US3 (T044-T050)
Parallel Stream 4: US4 (T051-T058)
Parallel Stream 5: US5 (T059-T064)
Parallel Stream 6: US6 (T065-T071)
```

All 6 user stories can be implemented simultaneously by different developers after Phase 2 foundation is complete.

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (BLOCKS everything)
3. Complete Phase 3: US1 - Calculate Additive Amount
4. Complete Phase 4: US2 - Usage Rate Recommendations
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy MVP to staging

**MVP Scope**: 19 additives with automatic amount calculation + light/standard/heavy recommendations

### Incremental Delivery (Full Feature)

1. Complete MVP (US1 + US2)
2. Add US3: Warning System → Test independently
3. Add US4: Essential Oil Calculations → Test independently
4. Add US5: Category Browsing → Test independently
5. Add US6: Colorant Recommendations → Test independently
6. Complete Phase 9: Enhanced Calculate (integration)
7. Complete Phase 10: Polish (performance + docs)

**Full Scope**: 122 ingredients (19 additives + 24 essential oils + 79 colorants) with comprehensive calculator features

### Parallel Team Strategy

With 3 developers after Phase 2 completes:

**Developer A**: US1 + US2 (P1 stories - MVP critical)
**Developer B**: US3 + US4 (P2 stories)
**Developer C**: US5 + US6 (P3 stories)

All converge on Phase 9 (Enhanced Calculate) and Phase 10 (Polish) together.

---

## Success Criteria

### Definition of Done

**Feature Complete**:
- ✅ All 3 migrations applied successfully (extend additives, create essential_oils, create colorants)
- ✅ All 122 ingredients imported (19 + 24 + 79 verified in database)
- ✅ All 8 API endpoints functional (3 recommendation + 3 listing + 1 enhanced calculate + 1 essential oil list)
- ✅ Test coverage >90% (pytest-cov enforcement)
- ✅ Load testing passes (p95 <50ms for recommendations, p95 <200ms for lists)
- ✅ All 6 user stories independently testable
- ✅ OpenAPI documentation generated
- ✅ Ansible playbook updated and tested

**Quality Gates**:
- ✅ All tests passing (unit, integration, contract)
- ✅ mypy --strict passing
- ✅ Ruff linting passing
- ✅ Black formatting passing
- ✅ No TODO comments in production code
- ✅ No console.log or debugging artifacts

**Documentation Complete**:
- ✅ quickstart.md with 4 test scenarios
- ✅ data-model.md with schema documentation
- ✅ contracts/ folder with 5 API contract files
- ✅ DEPLOYMENT.md with deployment guide

### Post-Deployment Validation

**Smoke Tests** (from plan.md):
```bash
# Test 1: List additives
curl http://localhost:8000/api/v1/additives | jq '.total_count'
# Expected: 19

# Test 2: Recommend honey amount
curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500" | jq '.recommendations.standard.amount_g'
# Expected: 10.0

# Test 3: List essential oils
curl http://localhost:8000/api/v1/essential-oils | jq '.total_count'
# Expected: 24

# Test 4: List yellow colorants
curl "http://localhost:8000/api/v1/colorants?category=yellow" | jq '.total_count'
# Expected: 14

# Test 5: Enhanced calculate with honey
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "oils": [{"oil_id": "olive", "percent": 70}, {"oil_id": "coconut", "percent": 30}],
    "water_percent": 38,
    "superfat_percent": 5,
    "batch_size_g": 500,
    "additives": [{"additive_id": "honey", "usage_level": "standard"}]
  }' | jq '.additives_calculated[0].amount_g'
# Expected: 10.0
```

---

## Timeline Estimate

**Total Duration**: ~9 days (per plan.md)

- Phase 1: Setup (0.5 day)
- Phase 2: Foundational (2.5 days) - CRITICAL PATH
- Phases 3-8: User Stories (3 days if parallel, 5 days if sequential)
- Phase 9: Enhanced Calculate (1 day)
- Phase 10: Polish (2 days)

**Critical Path**: Phase 2 → US1 → US2 → Enhanced Calculate → Deployment

**Parallelization Opportunity**: After Phase 2, all 6 user stories can proceed in parallel, reducing timeline to 6.5 days total if team capacity allows.

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US6) maps task to specific user story for traceability
- TDD CRITICAL: Tests MUST FAIL before implementation begins
- Each user story independently completable and testable
- Commit after each task completion or logical group
- Stop at checkpoints to validate story independence
- Performance target: <50ms for recommendation endpoints (spec requirement)
- Test coverage target: >90% (constitution requirement)
- 122 total ingredients: 19 additives + 24 essential oils + 79 colorants

**TDD Enforcement**: If you skip writing tests first, you're violating the constitution. No exceptions.
