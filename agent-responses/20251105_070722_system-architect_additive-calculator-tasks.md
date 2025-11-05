# System Architect - Additive Calculator Tasks Generation

**Timestamp**: 2025-11-05 07:07:22
**Task**: Generate executable tasks.md for Feature 004 - Smart Additive Calculator
**Requestor**: User
**Status**: Complete

---

## Task Summary

Generated comprehensive tasks.md for Smart Additive Calculator feature with:
- **91 total tasks** across 10 phases
- **6 user stories** (US1-US6) with priorities P1, P2, P3
- **TDD workflow** enforced throughout (tests written first, must fail before implementation)
- **Clear dependencies** and parallel execution opportunities marked
- **122 ingredients** to import (19 additives + 24 essential oils + 79 colorants)

---

## File Generated

**Location**: `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/specs/004-additive-calculator/tasks.md`

**Structure**:
- Phase 1: Setup (6 tasks)
- Phase 2: Foundational - Database + TDD Infrastructure (19 tasks) ⚠️ BLOCKS ALL USER STORIES
- Phase 3: US1 - Calculate Additive Amount (P1 - MVP) (9 tasks)
- Phase 4: US2 - Usage Rate Recommendations (P1) (7 tasks)
- Phase 5: US3 - Warning System (P2) (7 tasks)
- Phase 6: US4 - Essential Oil Calculations (P2) (8 tasks)
- Phase 7: US5 - Category Browsing (P3) (6 tasks)
- Phase 8: US6 - Colorant Recommendations (P3) (7 tasks)
- Phase 9: Enhanced Calculate Endpoint (8 tasks)
- Phase 10: Polish & Cross-Cutting Concerns (14 tasks)

---

## Key Design Decisions

### TDD Enforcement

**Every implementation task follows RED-GREEN cycle**:
1. Write tests FIRST (contract + integration + unit)
2. Verify tests FAIL (feature doesn't exist yet)
3. Implement feature
4. Verify tests PASS

**Example from Phase 3 (US1)**:
- T028: Write contract test → MUST FAIL
- T029: Write integration test → MUST FAIL
- T030: Write unit test → MUST FAIL
- T031-T033: Implement feature
- T036: Verify all tests PASS

### Critical Path

**Phase 2 (Foundational) BLOCKS everything**:
- 3 database models (Additive extension, EssentialOil, Colorant)
- 3 Alembic migrations
- 3 import scripts (19 + 24 + 79 ingredients)
- Test infrastructure setup

**NO user story work can begin until Phase 2 is complete.**

Once Phase 2 completes, all 6 user stories can proceed in parallel.

### Parallel Execution Opportunities

**Phase 2 (Foundational)**:
- Model tests (T007-T009) can run in parallel [P]
- Import script tests (T018-T020) can run in parallel [P]
- Migrations (T013-T015) can run in parallel after models [P]

**Phases 3-8 (User Stories)**:
All 6 user stories are independent and can run in parallel after Phase 2:
- US1 (P1): Additive amount calculation
- US2 (P1): Usage rate recommendations
- US3 (P2): Warning system
- US4 (P2): Essential oil calculations
- US5 (P3): Category browsing
- US6 (P3): Colorant recommendations

**Phase 10 (Polish)**:
- Performance validation, documentation, quality checks all parallel [P]

### User Story Independence

Each user story is **independently testable and deliverable**:

**US1 Test**: `curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500"` → Expected: 10g (2% of 500g)

**US2 Test**: Recommendation response includes light/standard/heavy amounts

**US3 Test**: Honey recommendation returns warnings array: ["accelerates trace", "causes overheating"]

**US4 Test**: `curl "http://localhost:8000/api/v1/essential-oils/lavender/recommend?batch_size_g=500"` → Expected: 15g (3% max rate)

**US5 Test**: `curl "http://localhost:8000/api/v1/additives?category=exfoliant"` → Returns coffee grounds, oatmeal, poppy seeds

**US6 Test**: `curl "http://localhost:8000/api/v1/colorants?category=yellow"` → Returns 14 yellow colorants

---

## Implementation Strategies

### MVP First (P1 Stories Only)

**Timeline**: ~4 days
1. Phase 1: Setup (0.5 day)
2. Phase 2: Foundational (2 days)
3. Phase 3-4: US1 + US2 (1.5 days)

**Deliverable**: 19 additives with automatic calculation and light/standard/heavy recommendations

### Incremental Delivery (Full Feature)

**Timeline**: ~9 days (sequential) or ~6.5 days (parallel)
1. Complete MVP (US1 + US2)
2. Add US3: Warning System
3. Add US4: Essential Oil Calculations (24 EOs)
4. Add US5: Category Browsing
5. Add US6: Colorant Recommendations (79 colorants)
6. Phase 9: Enhanced Calculate (integration)
7. Phase 10: Polish

**Deliverable**: 122 ingredients (19 + 24 + 79) with comprehensive calculator features

### Parallel Team Strategy

**With 3 developers after Phase 2**:
- Developer A: US1 + US2 (P1 - MVP critical)
- Developer B: US3 + US4 (P2 - warnings + essential oils)
- Developer C: US5 + US6 (P3 - browsing + colorants)

All converge on Phase 9 + 10 together.

**Timeline Reduction**: 9 days → 6.5 days with parallel execution

---

## Database Schema Summary

### Extended Additive Table (19 items)

**New Fields**:
- `usage_rate_standard_percent` (float) - Recommended usage rate
- `when_to_add` (str) - "to oils", "to lye water", "at trace"
- `preparation_instructions` (text, nullable) - How to prepare additive
- `mixing_tips` (text, nullable) - Best practices for incorporation
- `category` (str) - exfoliant, colorant, lather_booster, hardener, clay, botanical, luxury_additive, skin_benefit
- `accelerates_trace` (bool) - Warning flag
- `causes_overheating` (bool) - Warning flag
- `can_be_scratchy` (bool) - Warning flag
- `turns_brown` (bool) - Warning flag

### Essential Oils Table (24 items)

**Fields**:
- `id`, `name`, `botanical_name`
- `max_usage_rate_pct` (float) - CPSR-validated safe usage limit (0.025% - 3%)
- `scent_profile` (text) - Descriptive scent
- `blends_with` (JSONB array) - Compatible essential oils
- `note` (str) - "Top", "Middle", "Base" for blending
- `category` (str) - citrus, floral, herbal, woodsy, earthy, spice
- `warnings` (text, nullable) - Usage warnings
- `color_effect` (text, nullable) - Effect on soap color
- `confidence_level`, `verified_by_mga`

### Colorants Table (79 items)

**Fields**:
- `id`, `name`, `botanical`
- `category` (str) - yellow, orange, pink, red, green, blue, purple, brown, black (9 color families)
- `usage` (str) - Descriptive usage rates
- `method` (str) - infuse in oil, add to lye, add at trace
- `color_range` (str) - Expected color outcome
- `warnings` (text, nullable) - Fading, staining, texture warnings
- `confidence_level`, `verified_by_mga`

**Category Distribution**:
- Yellow: 14 colorants
- Orange: 10 colorants
- Pink: 6 colorants
- Red: 9 colorants
- Green: 11 colorants
- Blue: 7 colorants
- Purple: 6 colorants
- Brown: 11 colorants
- Black: 5 colorants
- **Total**: 79 colorants

---

## API Endpoints

### New Endpoints (8 total)

**Recommendation Endpoints** (3):
1. `GET /api/v1/additives/{id}/recommend?batch_size_g={size}`
   - Calculate light/standard/heavy amounts
   - Return usage percentages and weights
   - Include when_to_add instructions and warnings

2. `GET /api/v1/essential-oils/{id}/recommend?batch_size_g={size}`
   - Calculate safe amount based on max_usage_rate_pct
   - Return scent profile and blending recommendations
   - Include warnings and note type

3. (Enhanced Calculate integrated into existing endpoint)

**Listing Endpoints** (3):
1. `GET /api/v1/additives?category={category}`
   - Filter by category (exfoliant, lather_booster, hardener, etc.)
   - Pagination support (existing pattern)

2. `GET /api/v1/essential-oils`
   - List all essential oils
   - Search and pagination support

3. `GET /api/v1/colorants?category={color}`
   - Filter by color family (yellow, orange, pink, etc.)
   - Pagination support

**Enhanced Endpoints** (2):
1. `POST /api/v1/calculate` (enhanced)
   - Accept `additives` array in request
   - Return `additives_calculated` array in response
   - Auto-calculate amounts based on usage levels

2. `GET /api/v1/essential-oils` (new list endpoint)
   - Support search, pagination, category filtering

---

## Test Coverage Strategy

### TDD Requirements (Constitution Compliance)

**All tests written FIRST, must FAIL before implementation**:
- Contract tests (API response schemas)
- Integration tests (full user journeys)
- Unit tests (calculation logic, data transformation)

**Coverage Target**: >90% (pytest-cov enforcement)

### Test Files Created

**Unit Tests** (9 files):
- `tests/unit/test_additive_model_extended.py` (T007)
- `tests/unit/test_essential_oil_model.py` (T008)
- `tests/unit/test_colorant_model.py` (T009)
- `tests/unit/test_import_additives_extended.py` (T018)
- `tests/unit/test_import_essential_oils.py` (T019)
- `tests/unit/test_import_colorants.py` (T020)
- `tests/unit/test_calculation_logic.py` (T030)

**Integration Tests** (7 files):
- `tests/integration/test_recommendations_api.py` (T029)
- `tests/integration/test_usage_levels_api.py` (T038)
- `tests/integration/test_warnings_api.py` (T045)
- `tests/integration/test_essential_oils_api.py` (T052)
- `tests/integration/test_category_filtering_api.py` (T060)
- `tests/integration/test_colorants_api.py` (T066)
- `tests/integration/test_calculate_enhanced_api.py` (T073)

**Contract Tests** (7 files):
- `tests/contract/test_additive_recommendation.py` (T028)
- `tests/contract/test_usage_levels.py` (T037)
- `tests/contract/test_warnings.py` (T044)
- `tests/contract/test_essential_oil_recommendation.py` (T051)
- `tests/contract/test_category_filtering.py` (T059)
- `tests/contract/test_colorant_listing.py` (T065)
- `tests/contract/test_calculate_enhanced.py` (T072)

**Total**: 23 test files covering all user stories

---

## Performance Requirements

### Response Time Targets (from spec.md)

**Recommendation Endpoints**: <50ms (p95)
- Additive recommendation
- Essential oil recommendation

**List Endpoints**: <200ms (p95)
- Additives list
- Essential oils list
- Colorants list

**Database Queries**: <50ms
- Indexed by id, name, category

### Load Testing (Phase 10)

**Configuration**:
- Tool: Locust
- Concurrent users: 100
- Duration: 60 seconds
- Endpoints tested: All 8 new endpoints

**Success Criteria**:
- p95 <50ms for recommendations ✅
- p95 <200ms for lists ✅
- Error rate <0.1% ✅

---

## Import Scripts

### Data Sources

**Additives Extended** (19 items):
- Source: `working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json`
- Examples: Coffee grounds, honey, oatmeal, beeswax, salt, clay, etc.
- Fields: name, usage_rate, purpose, how_to_add, category, warnings

**Essential Oils** (24 items):
- Source: `working/user-feedback/essential-oils-usage-reference.json`
- Examples: Lavender, lemongrass, peppermint, tea tree, rose otto, etc.
- Fields: name, botanical_name, max_usage_rate_pct, scent_profile, blends_with, note, category

**Colorants** (79 items):
- Source: `working/user-feedback/natural-colorants-reference.json`
- Examples: Turmeric, annatto, calendula, activated charcoal, indigo, etc.
- Fields: name, botanical, category, usage, method, color_range, warnings
- Categories: 9 color families (yellow, orange, pink, red, green, blue, purple, brown, black)

### Import Script Implementation (Phase 2)

**Scripts Created**:
1. `scripts/import_additives_extended.py` (T021)
2. `scripts/import_essential_oils.py` (T022)
3. `scripts/import_colorants.py` (T023)

**Features**:
- JSON parsing with validation
- Data transformation (tablespoon → percentage)
- Database transaction management
- Idempotency (re-import safe, no duplicates)
- Error handling with rollback

**Execution**:
```bash
python scripts/import_additives_extended.py
python scripts/import_essential_oils.py
python scripts/import_colorants.py
```

**Verification**:
```sql
SELECT COUNT(*) FROM additives;    -- Expected: 19
SELECT COUNT(*) FROM essential_oils; -- Expected: 24
SELECT COUNT(*) FROM colorants;    -- Expected: 79
```

---

## Deployment Strategy

### Ansible Playbook Updates (T089)

**File**: `ansible/playbooks/deploy-soap-calculator.yml`

**Steps Added**:
1. Run Alembic migrations: `alembic upgrade head`
2. Execute import scripts (3 scripts)
3. Restart FastAPI service
4. Run smoke tests (5 curl commands)

### Smoke Tests (Post-Deployment)

**Test 1**: List additives
```bash
curl http://localhost:8000/api/v1/additives | jq '.total_count'
# Expected: 19
```

**Test 2**: Recommend honey amount
```bash
curl "http://localhost:8000/api/v1/additives/honey/recommend?batch_size_g=500" | jq '.recommendations.standard.amount_g'
# Expected: 10.0
```

**Test 3**: List essential oils
```bash
curl http://localhost:8000/api/v1/essential-oils | jq '.total_count'
# Expected: 24
```

**Test 4**: List yellow colorants
```bash
curl "http://localhost:8000/api/v1/colorants?category=yellow" | jq '.total_count'
# Expected: 14
```

**Test 5**: Enhanced calculate with honey
```bash
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

### Rollback Procedure

**If deployment fails**:
1. Rollback migrations: `alembic downgrade -1` (3 times for 3 migrations)
2. Restart service with previous version
3. Verify previous functionality intact

**Data Safety**:
- All migrations include downgrade paths
- Import scripts are idempotent (safe to re-run)
- Database backups before deployment

---

## Documentation Deliverables

### Phase 10 Documentation (T082-T084)

**quickstart.md** (T083):
- 4 test scenarios with example requests/responses
- curl commands for all 8 endpoints
- Expected outputs for verification

**data-model.md** (T084):
- Extended Additive table schema
- EssentialOil table schema
- Colorant table schema
- Relationship diagrams
- Field descriptions and constraints

**contracts/** folder (from plan.md):
- `additives-recommend.md` - Additive recommendation contract
- `essential-oils-list.md` - Essential oil listing contract
- `essential-oils-recommend.md` - Essential oil recommendation contract
- `colorants-list.md` - Colorant listing contract
- `calculate-enhanced.md` - Enhanced calculate contract

**DEPLOYMENT.md** (T090):
- Migration sequence
- Import script execution order
- Rollback procedures
- Smoke test commands
- Troubleshooting guide

---

## Success Metrics

### Definition of Done

**Feature Complete**:
- ✅ All 3 migrations applied (extend additives, create essential_oils, create colorants)
- ✅ All 122 ingredients imported (19 + 24 + 79 verified)
- ✅ All 8 API endpoints functional
- ✅ Test coverage >90%
- ✅ Load testing passes (p95 <50ms recommendations, p95 <200ms lists)
- ✅ All 6 user stories independently testable
- ✅ OpenAPI documentation auto-generated
- ✅ Ansible playbook updated and tested

**Quality Gates**:
- ✅ All tests passing (unit, integration, contract)
- ✅ mypy --strict passing
- ✅ Ruff linting passing
- ✅ Black formatting passing
- ✅ No TODO comments
- ✅ No debugging artifacts

**Documentation Complete**:
- ✅ quickstart.md with 4 scenarios
- ✅ data-model.md with schemas
- ✅ contracts/ with 5 API contracts
- ✅ DEPLOYMENT.md with deployment guide

---

## Risk Mitigation

### Data Import Risks

**Risk**: Import scripts fail due to data format issues
**Mitigation**:
- Comprehensive unit tests (T018-T020)
- Dry-run validation mode
- Transaction rollback on failure
- Manual data inspection before import

### Performance Risks

**Risk**: Recommendation endpoints exceed 50ms target
**Mitigation**:
- Database indexes on category, name, id
- Simple calculation formula (no complex algorithms)
- Load testing before merge (T080)
- EXPLAIN ANALYZE on all queries (T081)

### Migration Risks

**Risk**: Alembic migrations fail or can't be rolled back
**Mitigation**:
- Test migrations locally first (T016-T017)
- Include downgrade paths (T013-T015)
- Database backup before deployment
- Staging environment validation

### Test Coverage Risks

**Risk**: <90% test coverage blocks merge
**Mitigation**:
- TDD enforced from start (tests written first)
- pytest-cov monitoring during development
- 23 test files covering all user stories
- Property-based tests for edge cases (if needed)

---

## Next Steps

1. ✅ **COMPLETE**: Generated tasks.md (this response)
2. ⏳ **TODO**: Begin Phase 1 (Setup - 6 tasks)
3. ⏳ **TODO**: Complete Phase 2 (Foundational - 19 tasks) - CRITICAL PATH
4. ⏳ **TODO**: Implement US1 + US2 (P1 stories - MVP)
5. ⏳ **TODO**: Deploy MVP to staging
6. ⏳ **TODO**: Implement US3-US6 (P2 + P3 stories)
7. ⏳ **TODO**: Complete Phase 9 (Enhanced Calculate integration)
8. ⏳ **TODO**: Complete Phase 10 (Polish + deployment)

---

## Confidence Assessment

**High Confidence**:
- TDD workflow enforced throughout
- Clear dependencies and execution order
- User stories independently testable
- Existing patterns replicated (Oil model, resources API)
- 122 ingredients validated in JSON sources
- Performance targets achievable (simple formula, indexed queries)

**Medium Confidence**:
- Import script complexity (3 different data formats)
- Test coverage >90% target (requires discipline)

**Low Confidence**: None

---

## Metadata

**Status**: Complete
**Confidence**: High
**Follow-up**: Begin implementation with Phase 1 (Setup)
**Files Generated**: 1
  - `/specs/004-additive-calculator/tasks.md` (91 tasks)

**Total Tasks**: 91
**Estimated Timeline**: 9 days (sequential) or 6.5 days (parallel)
**User Stories**: 6 (US1-US6)
**Database Tables**: 3 (1 extended, 2 new)
**API Endpoints**: 8 (3 recommendation, 3 listing, 2 enhanced)
**Test Files**: 23 (9 unit, 7 integration, 7 contract)
**Import Scripts**: 3
**Total Ingredients**: 122 (19 additives + 24 essential oils + 79 colorants)

---

**Generated**: 2025-11-05 07:07:22
**System Architect**: Tasks ready for implementation
**TDD Protocol**: Enforced (tests written first, must fail before implementation)
**Constitution Compliance**: ✅ Verified (TDD, >90% coverage, API-first, performance targets)
