# Implementation Plan: Smart Additive Calculator

**Branch**: `004-additive-calculator` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-additive-calculator/spec.md`

## Summary

Automatic additive amount calculations with intelligent usage recommendations. Extends existing Additive model and adds two new entities (EssentialOil, Colorant) to accommodate 122 ingredients total (19 additives + 24 essential oils + 79 colorants). Simple percentage-based calculation formula delivers <50ms response times with light/standard/heavy usage level recommendations.

**Technical Approach**: Database extension via 3 Alembic migrations, new recommendation endpoints following existing pagination patterns, enhanced recipe calculation accepting additive selections with auto-calculation, import scripts for validated JSON data sources.

**Complexity**: MEDIUM | **Risk**: LOW | **Timeline**: ~9 days

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 15+
**Storage**: PostgreSQL with JSONB for flexible metadata
**Testing**: pytest, pytest-cov (>90% coverage), httpx (integration tests)
**Target Platform**: Linux server (Fedora 42, Podman/Quadlet deployment)
**Project Type**: Single backend API (Phase 1 - no frontend)

**Performance Goals**:
- Recommendation endpoint: <50ms response time (spec requirement)
- Database queries: <50ms for ingredient lookups
- Concurrent load: Support 100+ requests
- Calculation throughput: Simple formula `(batch_size_g × usage_pct) / 100`

**Constraints**:
- 122 ingredients pre-populated from validated JSON sources
- Usage rates sourced from supplier guidelines and CPSR data
- Safety warnings required for all problematic ingredient behaviors
- Backward compatible extension (no breaking changes to existing Additive model)

**Scale/Scope**:
- 19 additives (extended fields)
- 24 essential oils (new table)
- 79 colorants (new table)
- 8 new API endpoints (3 recommendation, 3 listing, 2 enhanced calculate)

---

## Constitution Check

### ✅ I. API-First Architecture
**Status**: COMPLIANT

All features expose REST API endpoints with automatic OpenAPI documentation. No UI implementation in Phase 1 scope. Endpoints fully testable via httpx integration tests.

**Endpoints**:
- `GET /api/v1/additives/{id}/recommend` - Additive recommendations
- `GET /api/v1/essential-oils` - List essential oils
- `GET /api/v1/essential-oils/{id}/recommend` - EO recommendations
- `GET /api/v1/colorants?category={color}` - List colorants
- `POST /api/v1/calculate` - Enhanced with additive selections

### ✅ II. Research-Backed Calculations
**Status**: COMPLIANT

Usage rates sourced from:
- `additives-usage-reference.json` (19 ingredients, supplier-validated)
- `essential-oils-usage-reference.json` (24 EOs, CPSR-validated max rates 0.025%-3%)
- `natural-colorants-reference.json` (79 colorants, method-specific rates)

Database tracking: `confidence_level` field (high/medium/low), botanical names, `verified_by_mga` boolean for empirically tested ingredients.

Property-based tests validate edge cases, usage boundaries, and warning thresholds.

### ✅ III. Test-First Development
**Status**: COMPLIANT

TDD cycle enforced:
1. Model tests → Implement models
2. Import script tests → Implement imports
3. API endpoint tests → Implement endpoints
4. Calculation tests → Implement logic
5. Property-based tests (Hypothesis) for edge cases

Coverage target: >90% (pytest-cov enforcement)

### ✅ IV. Data Integrity & ACID Compliance
**Status**: COMPLIANT

**Migrations**:
- Migration 1: Extend `additives` table (ALTER TABLE, backward compatible)
- Migration 2: Create `essential_oils` table
- Migration 3: Create `colorants` table

Import scripts use database transactions (rollback on failure). Foreign key constraints enforced. Alembic migrations version-controlled and immutable.

### ✅ V. Performance Budgets
**Status**: COMPLIANT

Targets:
- Recommendation response: <50ms (spec requirement)
- Database queries: <50ms (indexed by id, common_name, category)
- List endpoints: <200ms (pagination pattern from existing `list_oils()`)
- Concurrent load: 100+ requests (async SQLAlchemy)

Load testing with Locust validates performance before merge.

### ✅ VI. Security & Authentication
**Status**: COMPLIANT

Resource discovery endpoints: **No authentication** (public reference data)
- `/api/v1/oils`, `/api/v1/additives`, `/api/v1/essential-oils`, `/api/v1/colorants`
- Recommendation endpoints public (usage rates are public knowledge)

Recipe calculation: **JWT required** (per existing `/api/v1/calculate`)

Input validation: Pydantic models for all requests, query parameter validation, usage percentage bounds (0.0-100.0).

### ✅ VII. Deployment Platform Standards
**Status**: COMPLIANT

Fedora + Podman + Quadlet deployment. No new containers required (extends existing FastAPI service). Ansible playbook updated with migration and import steps.

Deployment steps:
1. Run Alembic migrations
2. Run import scripts (3 data sources)
3. Restart FastAPI service
4. Verify endpoints

### ✅ VIII. Observability & Monitoring
**Status**: COMPLIANT

Structured JSON logs with request IDs. Sentry integration for exceptions. Prometheus metrics: response_time, request_count, error_rate per endpoint.

Alert thresholds:
- Response time p95 >100ms (target <50ms)
- Error rate >1% (target <0.1%)

---

## Project Structure

### Documentation (this feature)

```text
specs/004-additive-calculator/
├── plan.md              # This file
├── research.md          # SKIP (data sources validated)
├── data-model.md        # Phase 1 (database design)
├── quickstart.md        # Phase 1 (API usage examples)
├── contracts/           # Phase 1 (API contracts)
│   ├── additives-recommend.md
│   ├── essential-oils-list.md
│   ├── essential-oils-recommend.md
│   ├── colorants-list.md
│   └── calculate-enhanced.md
└── tasks.md             # Phase 2 (/speckit.tasks command)
```

### Source Code (repository root)

```text
app/
├── models/
│   ├── additive.py           # EXTEND (add calculator fields)
│   ├── essential_oil.py      # NEW (EO entity)
│   └── colorant.py           # NEW (colorant entity)
│
├── schemas/
│   ├── resource.py           # EXTEND (add EO/Colorant schemas)
│   ├── recommendation.py     # NEW (recommendation responses)
│   └── calculate.py          # EXTEND (accept additive selections)
│
├── api/v1/
│   ├── resources.py          # EXTEND (EO/colorant endpoints)
│   ├── recommendations.py    # NEW (recommendation logic)
│   └── calculate.py          # EXTEND (process additive selections)
│
└── services/
    └── calculator.py         # EXTEND (additive calculation logic)

scripts/
├── import_additives_extended.py   # NEW (19 additives with new fields)
├── import_essential_oils.py       # NEW (24 EOs)
└── import_colorants.py            # NEW (79 colorants)

tests/
├── unit/
│   ├── test_additive_model.py       # EXTEND (new field validation)
│   ├── test_essential_oil_model.py  # NEW
│   ├── test_colorant_model.py       # NEW
│   ├── test_import_additives.py     # NEW
│   ├── test_import_eos.py           # NEW
│   └── test_import_colorants.py     # NEW
│
├── integration/
│   ├── test_resources_api.py        # EXTEND (EO/colorant endpoints)
│   ├── test_recommendations_api.py  # NEW
│   └── test_calculate_enhanced.py   # NEW
│
└── contract/
    └── test_recommendation_contracts.py  # NEW

alembic/versions/
├── YYYYMMDD_HHMM_extend_additives_table.py       # Migration 1
├── YYYYMMDD_HHMM_create_essential_oils_table.py  # Migration 2
└── YYYYMMDD_HHMM_create_colorants_table.py       # Migration 3
```

**Structure Decision**: Single project architecture (existing pattern). Extends current FastAPI backend with new models, endpoints, and services. No new infrastructure required.

---

## Complexity Tracking

**No constitution violations requiring justification.**

All implementation follows existing patterns:
- Model extension pattern (from Oil model)
- Pagination pattern (from `list_oils()` endpoint)
- Calculation logic (simple formula, no complex algorithms)
- Database seeding (from existing `seed_database.py`)

---

## Implementation Phases

### Phase 0: Research
**Status**: COMPLETED

Data sources validated:
- 19 additives from `additives-usage-reference.json`
- 24 essential oils from `essential-oils-usage-reference.json`
- 79 colorants from `natural-colorants-reference.json`

Constitution compliance verified. No research.md required.

---

### Phase 1: Design Artifacts

**Deliverables**:
1. `data-model.md` - Extended Additive + new EssentialOil + Colorant entities
2. `contracts/` - 5 API contract files (endpoint specifications)
3. `quickstart.md` - 4 test scenarios with example requests/responses

**Duration**: 1 day

**Key Design Decisions**:
- Extend Additive model with calculator fields (backward compatible ALTER TABLE)
- EssentialOil entity with max_usage_rate_pct (CPSR-validated 0.025%-3%)
- Colorant entity with category-based organization (9 color families)
- Recommendation formula: `(batch_size_g × usage_pct) / 100`
- Warning system: Boolean flags for problematic behaviors

**Data Model Highlights**:
```python
# Extended Additive
usage_rate_standard_percent: float  # Recommended usage
when_to_add: str                    # "to oils", "to lye water", "at trace"
preparation_instructions: str       # "Disperse in water", "Melt first"
mixing_tips: str                    # Best practices
category: str                       # "exfoliant", "lather_booster", etc.
accelerates_trace: bool             # Warning flag
causes_overheating: bool            # Warning flag
can_be_scratchy: bool               # Warning flag
turns_brown: bool                   # Warning flag

# EssentialOil (NEW)
max_usage_rate_pct: float          # Safe usage limit (0.025%-3%)
scent_profile: str
blends_with: list[str] (JSONB)
note: str                          # "Top", "Middle", "Base"
category: str                      # "floral", "citrus", "herbal"
warnings: str (nullable)

# Colorant (NEW)
category: str                      # Color family (yellow, orange, pink, etc.)
usage: str                         # Descriptive usage rates
method: str                        # Application method
color_range: str                   # Expected color outcome
warnings: str (nullable)
```

---

### Phase 2: Implementation

**Duration**: 5 days

**TDD Implementation Order**:

**Day 1: Database Schema**
- Write model tests (field validation, constraints)
- Implement models (Additive extension, EssentialOil, Colorant)
- Write migration scripts (3 migrations)
- Apply migrations locally
- Verify schema with psql

**Day 2: Import Scripts**
- Write import script tests (JSON parsing, data transformation, database insertion)
- Implement import scripts (3 scripts for 122 ingredients)
- Test idempotency (re-import doesn't duplicate)
- Verify all ingredients imported correctly

**Day 3: Recommendation Endpoints**
- Write API endpoint tests (recommendation responses, error cases)
- Implement recommendation logic (calculate light/standard/heavy amounts)
- Implement warning system (build warnings list from boolean flags)
- Test with httpx integration tests

**Day 4: List Endpoints + Enhanced Calculate**
- Write list endpoint tests (pagination, filtering, search)
- Implement list endpoints (EO and colorant listing)
- Write enhanced calculate tests (additive selections processing)
- Implement enhanced calculate (process additives + EOs)

**Day 5: Integration + Property-Based Tests**
- Write property-based tests (Hypothesis for edge cases)
- Test usage rate boundaries, warning thresholds, rounding
- End-to-end integration tests (full workflow scenarios)
- Verify >90% test coverage (pytest-cov)

---

### Phase 3: Testing & Optimization

**Duration**: 2 days

**Day 6: Load Testing**
- Locust load testing setup (100 concurrent users)
- Target endpoints: recommendation (p95 <50ms), list (p95 <200ms)
- Database performance validation (EXPLAIN ANALYZE)
- Add indexes if needed (category, common_name)

**Day 7: Documentation & Review**
- Review all API contracts
- Update OpenAPI documentation
- Code review (constitution compliance)
- Verify all test scenarios in quickstart.md

---

### Phase 4: Deployment

**Duration**: 1 day

**Day 8: Staging Deployment**
- Update Ansible playbook (migration + import steps)
- Deploy to staging environment
- Run smoke tests (5 curl commands)
- Performance validation (Locust against staging)

**Production Deployment** (after staging validation):
- Ansible playbook execution
- Database migration (alembic upgrade head)
- Import scripts execution (3 data imports)
- Service restart (systemctl --user restart soap-calculator)
- Smoke tests + monitoring validation

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Data Import Errors** | HIGH | MEDIUM | Comprehensive tests, dry-run validation, rollback plan |
| **Performance Degradation** | MEDIUM | LOW | Load testing before merge, database indexes |
| **Migration Rollback Failures** | MEDIUM | LOW | Test downgrade migrations, backup before deploy |
| **Incomplete Test Coverage** | HIGH | LOW | >90% enforcement, property-based tests |
| **Warning System Gaps** | MEDIUM | MEDIUM | Manual review of all 122 ingredients |

**Mitigation Strategies**:
- Dry-run mode for import scripts (no database changes)
- Sentry custom metrics for slow recommendations (>50ms warning)
- Comprehensive property-based tests (Hypothesis)
- Manual validation of warning flags against source data

---

## Success Metrics

### Definition of Done

**Feature Complete**:
- ✅ All 3 migrations applied successfully
- ✅ All 122 ingredients imported (19 + 24 + 79)
- ✅ All 8 API endpoints functional
- ✅ Test coverage >90% (pytest-cov)
- ✅ Load testing passes (<50ms p95 for recommendations)
- ✅ OpenAPI documentation generated
- ✅ Ansible playbook updated and tested

**Quality Gates**:
- ✅ All tests passing (unit, integration, property-based)
- ✅ mypy --strict type checking passing
- ✅ Ruff linting passing
- ✅ Black formatting passing

**Documentation Complete**:
- ✅ API contracts (5 files)
- ✅ Quickstart guide (4 test scenarios)
- ✅ Data model documentation
- ✅ Migration guide (upgrade/downgrade)

---

### Post-Deployment Validation

**Smoke Tests**:
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

# Test 4: List colorants (yellow)
curl "http://localhost:8000/api/v1/colorants?category=yellow" | jq '.total_count'
# Expected: 14

# Test 5: Enhanced calculate with additives
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

**Performance Validation**:
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=60s --headless
# Expected: p95 <50ms, error rate <0.1%
```

---

## Timeline Estimate

**Total Duration**: ~9 days (1.8 weeks)

- Phase 0: Research (COMPLETED) ✅
- Phase 1: Design (1 day)
- Phase 2: Implementation (5 days)
- Phase 3: Testing & Optimization (2 days)
- Phase 4: Deployment (1 day)

**Critical Path**: Database migrations → Import scripts → API endpoints → Testing → Deployment

**Parallelization Opportunities**:
- Model tests and import script tests can be written in parallel
- API endpoint tests and calculation tests can be written in parallel
- Documentation can be written during testing phase

---

## Next Steps

1. ✅ Generate this implementation plan (`/speckit.plan`)
2. 🔄 Generate `tasks.md` via `/speckit.tasks` command
3. ⏳ Begin Phase 2 implementation (TDD cycle)
4. ⏳ Deploy to staging after passing all tests
5. ⏳ Production deployment after smoke tests

**Response File**: See `/agent-responses/20251105_095043_system-architect_additive-calculator-plan.md` for comprehensive implementation details including:
- Complete API contract specifications
- Database schema with field definitions
- Import script implementation details
- Test strategy breakdown
- Load testing configuration
- Ansible playbook updates

---

**Plan Status**: COMPLETE - Ready for task generation
**Generated**: 2025-11-05 09:50:43
**System Architect**: Plan approved for implementation
