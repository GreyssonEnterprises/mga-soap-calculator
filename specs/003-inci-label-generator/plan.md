# Implementation Plan: INCI Label Generator

**Branch**: `003-inci-label-generator` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.specify/specs/003-inci-label-generator/spec.md`

## Summary

Generate professional INCI ingredient labels in three formats (raw oils, saponified salts, common names) with regulatory-compliant percentage-based sorting. API-first endpoint returns copy-ready labels sorted by ingredient percentage in descending order, including proper saponified nomenclature for post-saponification labeling requirements.

**Technical Approach**: Extend Oil model with `saponified_inci_name` field populated from reference data (saponified-inci-terms.json), implement percentage calculation service for all batch ingredients, create FastAPI endpoint following existing resources.py patterns for format-specific label generation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic, PostgreSQL driver (asyncpg)
**Storage**: PostgreSQL 15+ with JSONB for structured metadata
**Testing**: pytest, Hypothesis (property-based), httpx (async client), pytest-cov
**Target Platform**: Linux server (Fedora 42 with Podman + Quadlet deployment)
**Project Type**: Web API (backend-only feature, no frontend in this phase)
**Performance Goals**: <100ms API response time for label generation (lighter than standard <200ms budget)
**Constraints**: <200ms p95 latency, ACID transaction guarantees, >90% test coverage
**Scale/Scope**: Support 100+ concurrent requests, handle recipes with 20+ ingredients efficiently

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. API-First Architecture** (CRITICAL)
- Feature starts as REST API endpoint: GET `/api/v1/recipes/{recipe_id}/inci-label`
- FastAPI automatic OpenAPI documentation included
- No UI component in this phase - pure API functionality
- Status: **COMPLIANT**

✅ **II. Research-Backed Calculations** (CRITICAL)
- Saponified INCI naming based on reference data from saponified-inci-terms.json (industry standard nomenclature)
- Percentage calculations use documented batch weight formulas (oils + water + lye + additives)
- No quality impact calculations in this feature (only label generation)
- Status: **COMPLIANT** (nomenclature is industry standard, not research-dependent)

✅ **III. Test-First Development** (CRITICAL)
- TDD mandatory: Write tests for percentage calculations BEFORE implementation
- Property-based testing for edge cases (trace ingredients, mixed lye types, missing INCI names)
- Integration tests for API endpoint with httpx
- Target: >90% coverage
- Status: **COMPLIANT**

✅ **IV. Data Integrity & ACID Compliance** (CRITICAL)
- Read-only database operations (no state changes in this feature)
- Oil model extension uses Alembic migration for schema change
- Foreign key constraints maintained
- Status: **COMPLIANT**

✅ **V. Performance Budgets** (HIGH)
- Target: <100ms response time (stricter than standard <200ms)
- Database query optimization required for recipe + oils join
- Calculation efficiency critical (sorting algorithms, percentage precision)
- Status: **COMPLIANT** (design includes performance considerations)

✅ **VI. Security & Authentication** (HIGH)
- JWT authentication required for recipe access (recipes are user-owned data)
- Rate limiting via existing FastAPI middleware
- Input validation via Pydantic (recipe_id path parameter)
- Status: **COMPLIANT**

✅ **VII. Deployment Platform Standards** (CRITICAL)
- No deployment changes required (existing Podman + Quadlet infrastructure)
- Fedora/UBI base images maintained
- Status: **COMPLIANT**

✅ **VIII. Observability & Monitoring** (MEDIUM)
- Structured logging for label generation operations
- Error tracking via existing Sentry integration
- Status: **COMPLIANT**

### Technology Constraints Compliance

✅ **Mandatory Stack**
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async: ✓
- PostgreSQL 15+ with JSONB: ✓
- pytest, Hypothesis, httpx, pytest-cov: ✓
- Alembic for migrations: ✓
- Status: **COMPLIANT**

✅ **Forbidden Technologies**
- No Docker (Podman only): ✓
- No Flask/Django (FastAPI): ✓
- No MySQL/MongoDB (PostgreSQL): ✓
- Status: **COMPLIANT**

### Quality Gates Compliance

**Pre-Merge Requirements**:
- Tests written first (TDD cycle)
- Coverage ≥90%
- Type checking (mypy --strict)
- Linting (Ruff, Black)
- OpenAPI docs auto-generated
- Calculation accuracy validated (reference INCI label examples)

**Pre-Production Requirements**:
- Load testing (>100 concurrent requests, <100ms p95)
- Security scan (Bandit)
- Integration tests passing

## Project Structure

### Documentation (this feature)

```text
.specify/specs/003-inci-label-generator/
├── plan.md              # This file
├── research.md          # Phase 0: Saponified INCI naming research
├── data-model.md        # Phase 1: Oil model extension design
├── quickstart.md        # Phase 1: API integration guide
├── contracts/           # Phase 1: OpenAPI contract
│   └── inci-label.yaml
└── tasks.md             # Phase 2: (Generated by /speckit.tasks - NOT in plan output)
```

### Source Code (repository root)

```text
app/
├── models/
│   └── oil.py                          # Extended with saponified_inci_name field
├── schemas/
│   └── inci_label.py                   # New: INCI label response schemas
├── services/
│   ├── inci_naming.py                  # New: Saponified name generation logic
│   └── label_generator.py              # New: Label formatting and sorting service
├── api/v1/
│   └── inci.py                         # New: INCI label endpoint
└── data/
    └── saponified-inci-terms.json      # New: Reference data for 37 oils

alembic/versions/
└── 003_add_saponified_inci_name.py     # New: Migration for Oil model

tests/
├── unit/
│   ├── test_inci_naming.py             # New: Saponified name generation tests
│   ├── test_label_generator.py         # New: Label sorting and formatting tests
│   └── test_percentage_calculation.py  # New: Batch percentage calculation tests
├── integration/
│   └── test_inci_endpoint.py           # New: API endpoint integration tests
└── fixtures/
    └── sample_recipes.py               # New: Test recipe data with known INCI labels
```

**Structure Decision**: Single project structure maintained (existing `app/` directory). New services layer created for business logic (inci_naming.py, label_generator.py) following separation of concerns. API endpoint follows existing v1 pattern in `app/api/v1/`. Data directory added for reference JSON file (saponified-inci-terms.json).

## Complexity Tracking

> **No violations** - All constitution requirements met without exceptions.

## Phase 0: Research (Deliverable: research.md)

**Objective**: Document saponified INCI naming patterns, percentage calculation approach, and reference data structure design.

**Research Questions**:
1. What are the standard saponified INCI name patterns for NaOH vs KOH soaps?
2. How should mixed-lye soaps (both NaOH and KOH) be represented in INCI labels?
3. What edge cases exist in saponified nomenclature (e.g., Castor Oil alternatives)?
4. How to calculate ingredient percentages for regulatory compliance (total batch weight components)?
5. What is the optimal reference data structure for saponified-inci-terms.json?

**Deliverables**:
- `research.md`: Saponified INCI naming conventions, calculation methodology, edge case handling strategies, reference data schema design

## Phase 1: Design (Deliverables: data-model.md, contracts/, quickstart.md)

**Objective**: Define data model extension, API contract, and integration documentation.

### Data Model Design (data-model.md)
- Oil model extension: Add `saponified_inci_name` field (String(200), nullable=True)
- Alembic migration strategy for backfilling existing oils
- JSONB structure for future multi-lye scenarios (if needed)
- Index considerations for INCI name searches

### API Contract (contracts/inci-label.yaml)
- OpenAPI 3.0 specification for GET `/api/v1/recipes/{recipe_id}/inci-label`
- Request parameters: recipe_id (path), format_type (query: optional, default="all")
- Response schema: Three label formats + ingredients_breakdown array
- Error responses: 404 (recipe not found), 401 (unauthorized), 422 (validation error)

### Integration Guide (quickstart.md)
- Endpoint usage examples (curl, httpx, requests)
- Format type selection (raw_inci, saponified_inci, common_names, all)
- Response interpretation guide
- Percentage breakdown explanation
- Edge case behavior documentation

## Phase 2: Implementation (Deliverable: tasks.md via /speckit.tasks)

**TDD Workflow**:
1. Write property-based tests for saponified name generation
2. Write unit tests for percentage calculations
3. Write integration tests for API endpoint
4. Implement services (inci_naming.py, label_generator.py)
5. Implement API endpoint (inci.py)
6. Run tests (should fail initially - Red phase)
7. Implement logic (Green phase)
8. Refactor for clarity and performance

**Implementation Order**:
1. Database migration (add saponified_inci_name field)
2. Load reference data (saponified-inci-terms.json parsing)
3. INCI naming service (saponified name generation)
4. Label generator service (percentage calculation + sorting)
5. API endpoint (FastAPI route handler)
6. Integration tests (httpx client tests)
7. Performance testing (load testing for <100ms target)

## Phase 3: Validation & Deployment

**Validation Steps**:
- Run full test suite (pytest with coverage report)
- Type checking (mypy --strict)
- Linting (Ruff, Black)
- Load testing (100+ concurrent requests)
- Calculate reference INCI labels manually, compare to API output

**Deployment**:
- No infrastructure changes (existing Podman + Quadlet)
- Database migration applied via Alembic
- Service restart to load new endpoint
- Monitoring: Track endpoint latency and error rates

## Success Criteria

✅ **Functional**:
- API endpoint returns three INCI label formats correctly
- Ingredients sorted by percentage in descending order
- Saponified INCI names generated accurately for 37 reference oils
- Edge cases handled gracefully (missing data, trace ingredients, mixed lye)

✅ **Performance**:
- <100ms p95 response time under 100+ concurrent requests
- Efficient database queries (<50ms for recipe + oils join)

✅ **Quality**:
- Test coverage ≥90%
- All property-based tests passing (Hypothesis)
- Integration tests validate complete endpoint behavior
- OpenAPI documentation auto-generated and accurate

✅ **Constitution Compliance**:
- TDD workflow followed strictly
- API-first architecture maintained
- ACID guarantees preserved
- Performance budgets met
