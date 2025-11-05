# Implementation Plan: Phase 1 - MVP API Foundation

**Branch**: `001-mvp-api-foundation` | **Date**: 2025-11-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.specify/specs/001-mvp-api/spec.md`

## Summary

Build API-first soap formulation calculator with research-backed additive quality modeling. Core value: industry's first calculator modeling non-fat additive effects on soap properties. Technical approach: FastAPI + PostgreSQL + NumPy calculation engine with TDD, deployed via Podman + Quadlet to Fedora 42.

Primary deliverables: REST API for saponification calculations, quality metrics, additive impact modeling, recipe persistence, cost analysis, JWT authentication. Target: <200ms response times, >90% test coverage, production deployment for MGA Automotive internal use.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), SQLAlchemy 2.0 (async ORM), Alembic (migrations), NumPy (calculations), Pydantic (validation), python-jose (JWT), httpx (testing), pytest + Hypothesis (testing)
**Storage**: PostgreSQL 15+ (recipe persistence, version history, JSONB for additive metadata)
**Testing**: pytest (unit tests), Hypothesis (property-based testing), httpx (integration tests), pytest-cov (coverage >90%), Locust (load testing)
**Target Platform**: Fedora 42 Linux server (production), Podman containerization, Quadlet systemd integration
**Project Type**: Single backend API (web application split comes in Phase 3)
**Performance Goals**: <200ms API response (p95), <50ms database queries, 100+ concurrent requests
**Constraints**: ACID transactions required (no eventual consistency), JWT 15min expiry, TLS 1.3 mandatory, >90% test coverage gate
**Scale/Scope**: Internal MGA use initially (single user), scales to hundreds of users in Phase 3, ~1000 recipes per user max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Passing Gates

- **API-First Architecture**: All features expose REST endpoints before any UI (Phase 3)
- **Research-Backed Calculations**: Additive coefficients will cite peer-reviewed sources (Phase 0 research task)
- **Test-First Development**: TDD mandatory with >90% coverage requirement
- **Data Integrity**: PostgreSQL transactions for all recipe operations
- **Performance Budgets**: <200ms target with load testing required
- **Security**: JWT authentication implemented for all endpoints
- **Deployment Platform**: Podman + Quadlet + Fedora/UBI base images (no Docker)
- **Observability**: Structured logging + Sentry error tracking required

### 🚨 Potential Violations Requiring Justification

None identified. Project structure aligns with constitution principles.

### 📋 Constitution Compliance Checklist

- [ ] Phase 0 research includes peer-reviewed citations for all additive coefficients
- [ ] Tests written and approved before implementation (TDD)
- [ ] pytest-cov reports ≥90% coverage before merge
- [ ] Load testing validates <200ms p95 response times
- [ ] PostgreSQL transactions wrap all recipe state changes
- [ ] Podman + Quadlet used (Docker explicitly forbidden)
- [ ] Ansible playbook created for deployment automation
- [ ] FastAPI OpenAPI docs auto-generated at `/docs` endpoint
- [ ] Sentry integration configured for error tracking

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-mvp-api/
├── plan.md              # This file (implementation plan)
├── spec.md              # Feature specification (user stories, requirements)
├── research.md          # Phase 0: Additive research findings (citations, coefficients)
├── data-model.md        # Phase 1: Database schema design
├── api-contracts.md     # Phase 1: API endpoint specifications (OpenAPI excerpts)
├── quickstart.md        # Phase 1: Developer setup and usage guide
└── tasks.md             # Phase 2: Implementation task breakdown (NOT created yet)
```

### Source Code (repository root)

```text
mga-soap-calculator/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management (env vars)
│   ├── database.py                # SQLAlchemy async session management
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── oil.py                 # Oil reference data model
│   │   ├── additive.py            # Additive model (JSONB metadata)
│   │   ├── recipe.py              # Recipe model (version history)
│   │   ├── user.py                # User authentication model
│   │   └── associations.py        # Junction tables (recipe_oils, recipe_additives)
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── oil.py                 # Oil input/output schemas
│   │   ├── additive.py            # Additive schemas
│   │   ├── recipe.py              # Recipe schemas (create, update, response)
│   │   ├── calculation.py         # Calculation request/response schemas
│   │   └── auth.py                # Authentication schemas (login, token)
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── saponification.py     # SAP value calculations, lye amounts
│   │   ├── quality_metrics.py    # Fatty acid → quality scores
│   │   ├── additive_impact.py    # Research-backed additive modeling
│   │   ├── cost_analysis.py      # Batch and per-unit cost calculations
│   │   └── auth_service.py       # JWT generation, validation
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── oil_repository.py     # Oil CRUD operations
│   │   ├── additive_repository.py
│   │   ├── recipe_repository.py  # Recipe versioning logic
│   │   └── user_repository.py
│   │
│   └── api/                       # FastAPI routers (endpoints)
│       ├── __init__.py
│       ├── v1/                    # API version 1
│       │   ├── __init__.py
│       │   ├── calculate.py       # POST /calculate endpoint
│       │   ├── recipes.py         # CRUD /recipes endpoints
│       │   ├── oils.py            # GET /oils reference data
│       │   ├── additives.py       # GET /additives reference data
│       │   └── auth.py            # POST /auth/login, /auth/refresh
│       └── dependencies.py        # FastAPI dependency injection (DB session, auth)
│
├── tests/
│   ├── conftest.py                # pytest fixtures (DB setup, test client)
│   ├── unit/                      # Unit tests (calculation logic, services)
│   │   ├── test_saponification.py
│   │   ├── test_quality_metrics.py
│   │   ├── test_additive_impact.py
│   │   ├── test_cost_analysis.py
│   │   └── test_auth_service.py
│   │
│   ├── integration/               # API endpoint tests (httpx)
│   │   ├── test_calculate_endpoint.py
│   │   ├── test_recipes_endpoint.py
│   │   ├── test_oils_endpoint.py
│   │   └── test_auth_endpoint.py
│   │
│   └── property/                  # Property-based tests (Hypothesis)
│       ├── test_saponification_properties.py
│       └── test_quality_metrics_properties.py
│
├── migrations/                    # Alembic database migrations
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_additive_metadata.py
│   │   └── 003_recipe_versioning.py
│   └── env.py
│
├── scripts/                       # Utility scripts
│   ├── seed_oils.py              # Populate oil reference data
│   ├── seed_additives.py         # Populate additive data from research
│   └── load_test.py              # Locust load testing script
│
├── ansible/                       # Deployment automation
│   ├── playbooks/
│   │   ├── deploy-api.yml        # Main deployment playbook
│   │   └── rollback.yml          # Rollback procedure
│   ├── roles/
│   │   ├── soap-api/             # Application deployment role
│   │   └── postgres/             # Database setup role
│   └── inventory/
│       ├── production.ini
│       └── staging.ini
│
├── .quadlet/                      # Quadlet systemd container units
│   ├── soap-api.container        # Application container unit
│   └── soap-postgres.container   # Database container unit
│
├── Containerfile                  # Podman container build (Fedora base)
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata (if using Poetry)
├── .env.example                   # Environment variable template
├── alembic.ini                    # Alembic configuration
└── README.md                      # Project documentation
```

**Structure Decision**: Single project layout (Option 1) selected because Phase 1 is API-only with no frontend. Backend and frontend will be separated in Phase 3 when React UI is introduced. Current structure groups code by layer (models, schemas, services, repositories, API routers) following FastAPI conventions and layered architecture pattern.

## Complexity Tracking

> No constitution violations requiring justification.

## Phase 0: Research & Data Collection

**Goal**: Establish evidence-based foundation for additive quality impact modeling.

**Deliverables**:
- `research.md` document with literature review findings
- Structured additive dataset (CSV/JSON) with coefficients and citations
- Confidence scoring methodology for research sources

**Research Tasks**:
1. Literature review of peer-reviewed cosmetic chemistry journals
2. Search industry standards (ISO, ASTM) for soap testing methodologies
3. Collect saponification values for 20+ common soap-making oils
4. Document additive quality impact coefficients for 7 initial additives:
   - Kaolin clay (quality effects on Hardness, Lather, Conditioning)
   - Bentonite clay
   - Sea salt
   - Himalayan pink salt
   - Oatmeal (colloidal)
   - Coffee grounds
   - Activated charcoal
5. Create citation format: APA style with DOI/URL
6. Define confidence levels: High (multiple peer-reviewed sources), Medium (industry standard or single peer-reviewed source), Low (validated testing or manufacturer data)

**Research Output Schema**:
```json
{
  "additive_name": "Kaolin Clay",
  "typical_usage_range": "1-5%",
  "quality_impacts": {
    "hardness": {"coefficient": 1.15, "source": "Citation 1", "confidence": "high"},
    "cleansing": {"coefficient": 1.0, "source": "Citation 1", "confidence": "high"},
    "conditioning": {"coefficient": 0.95, "source": "Citation 2", "confidence": "medium"},
    "bubbly_lather": {"coefficient": 0.90, "source": "Citation 1", "confidence": "high"},
    "creamy_lather": {"coefficient": 1.05, "source": "Citation 2", "confidence": "medium"}
  },
  "citations": [
    {
      "id": 1,
      "reference": "Smith, J. et al. (2020). Effects of Clay Additives...",
      "doi": "10.1234/example",
      "confidence": "high"
    }
  ]
}
```

**Acceptance Criteria**:
- All 7 additives have documented quality impact coefficients
- Each coefficient cites at least one peer-reviewed or industry standard source
- Research document includes methodology for selecting sources
- Dataset ready for database import (scripts/seed_additives.py)

## Phase 1: Design & Architecture

**Goal**: Define database schema, API contracts, and development quickstart.

**Deliverables**:
- `data-model.md`: PostgreSQL schema design with ER diagram
- `api-contracts.md`: OpenAPI specification excerpts for all endpoints
- `quickstart.md`: Developer setup guide (local dev environment)

### Data Model Design (`data-model.md`)

**Key Tables**:
- `oils`: Reference data (name, SAP_value_NaOH, fatty_acid_profile JSONB)
- `additives`: Reference data (name, quality_coefficients JSONB, research_citations JSONB)
- `users`: Authentication (username, email, password_hash, api_key_hash, role)
- `recipes`: User formulations (id UUID, user_id FK, name, superfat, version_number, created_at, updated_at)
- `recipe_oils`: Junction table (recipe_id FK, oil_id FK, percentage DECIMAL)
- `recipe_additives`: Junction table (recipe_id FK, additive_id FK, percentage DECIMAL)

**Key Relationships**:
- recipes.user_id → users.id (one-to-many)
- recipe_oils.recipe_id → recipes.id (many-to-many via junction)
- recipe_oils.oil_id → oils.id
- recipe_additives.recipe_id → recipes.id (many-to-many via junction)
- recipe_additives.additive_id → additives.id

**Version History Strategy**:
- recipes.version_number increments on update
- Soft delete with deleted_at timestamp (preserve history)
- Unique constraint on (user_id, name, version_number)

**Indexes**:
- recipes(user_id, created_at DESC) for user recipe list queries
- recipes(name) for search functionality
- recipe_oils(recipe_id), recipe_additives(recipe_id) for joins

### API Contracts Design (`api-contracts.md`)

**Core Endpoints**:

```yaml
POST /api/v1/calculate
  Request: { oils: [{name, percentage}], additives: [{name, percentage}], superfat: 5 }
  Response: { lye_amount, water_amount, quality_metrics: {hardness, cleansing, conditioning, bubbly, creamy}, fatty_acids: {...}, cost_breakdown: {...} }
  Status: 200 OK, 400 Bad Request (validation), 404 Not Found (unknown oil/additive)

GET /api/v1/recipes
  Query: ?page=1&limit=20
  Response: { recipes: [{id, name, created_at, quality_summary}], pagination: {page, total} }
  Status: 200 OK, 401 Unauthorized

POST /api/v1/recipes
  Request: { name, oils, additives, superfat, notes }
  Response: { id, version_number, created_at }
  Status: 201 Created, 400 Bad Request, 401 Unauthorized

GET /api/v1/recipes/{id}
  Response: { id, name, oils, additives, superfat, quality_metrics, cost, version_number }
  Status: 200 OK, 404 Not Found, 401 Unauthorized

PUT /api/v1/recipes/{id}
  Request: { oils, additives, superfat } (partial update)
  Response: { id, version_number: incremented }
  Status: 200 OK, 404 Not Found, 401 Unauthorized

GET /api/v1/oils
  Response: { oils: [{id, name, sap_value, fatty_acids}] }
  Status: 200 OK

GET /api/v1/additives
  Response: { additives: [{id, name, typical_usage, quality_coefficients}] }
  Status: 200 OK

POST /api/v1/auth/login
  Request: { username, password }
  Response: { access_token, refresh_token, expires_in }
  Status: 200 OK, 401 Unauthorized

POST /api/v1/auth/refresh
  Request: { refresh_token }
  Response: { access_token, expires_in }
  Status: 200 OK, 401 Unauthorized
```

### Quickstart Guide (`quickstart.md`)

**Local Development Setup**:
1. Prerequisites: Python 3.11+, PostgreSQL 15+, Podman (optional for containers)
2. Clone repository, create virtual environment, install dependencies
3. Configure `.env` file (DATABASE_URL, JWT_SECRET_KEY)
4. Run Alembic migrations: `alembic upgrade head`
5. Seed reference data: `python scripts/seed_oils.py && python scripts/seed_additives.py`
6. Start dev server: `uvicorn app.main:app --reload`
7. Access API docs: http://localhost:8000/docs
8. Run tests: `pytest --cov=app --cov-report=html`

**Testing Workflow**:
1. Write test in `tests/unit/` or `tests/integration/`
2. Run specific test: `pytest tests/unit/test_saponification.py -v`
3. Verify coverage: `pytest --cov=app --cov-report=term-missing`
4. Property-based testing: `pytest tests/property/ -v --hypothesis-show-statistics`

## Phase 2: Implementation

**Goal**: TDD implementation of all functional requirements from spec.

**Approach**: Test-first development cycle (Red-Green-Refactor).

**Implementation Order** (follows user story priorities):

### 2.1 Database Foundation
- [ ] Alembic migrations: Create initial schema (oils, additives, users, recipes, junctions)
- [ ] SQLAlchemy models: Define ORM models with relationships
- [ ] Seed scripts: Populate oils and additives from Phase 0 research
- [ ] Database tests: Verify ACID transactions, foreign key constraints

### 2.2 Calculation Engine (P1 User Stories 1-2)
- [ ] **TDD**: Write tests for saponification calculations (SAP values, lye amounts, water ratios)
- [ ] Implement `services/saponification.py` with NumPy calculations
- [ ] **TDD**: Write tests for quality metrics (fatty acid → quality scores)
- [ ] Implement `services/quality_metrics.py` with scoring algorithms
- [ ] **TDD**: Write property-based tests (Hypothesis) for edge cases (negative values, extreme percentages)
- [ ] **TDD**: Write tests for additive impact modeling (coefficient application)
- [ ] Implement `services/additive_impact.py` with research-backed coefficients
- [ ] Integration: Combine saponification + quality + additive logic in unified calculation flow

### 2.3 REST API Endpoints (P1 User Stories 1-2)
- [ ] **TDD**: Write httpx tests for POST /calculate endpoint (valid request, validation errors, unknown oils)
- [ ] Implement FastAPI router `api/v1/calculate.py` with Pydantic schemas
- [ ] **TDD**: Write tests for GET /oils and GET /additives endpoints
- [ ] Implement reference data routers with repository layer
- [ ] Verify OpenAPI docs auto-generation at `/docs`

### 2.4 Recipe Persistence (P2 User Story 3)
- [ ] **TDD**: Write tests for recipe repository (create, read, update with versioning)
- [ ] Implement `repositories/recipe_repository.py` with SQLAlchemy async
- [ ] **TDD**: Write httpx tests for recipe CRUD endpoints (POST, GET, PUT)
- [ ] Implement FastAPI routers `api/v1/recipes.py`
- [ ] **TDD**: Test transaction rollback on database errors
- [ ] Implement error handling and 503 responses for DB failures

### 2.5 Cost Calculator (P2 User Story 4)
- [ ] **TDD**: Write tests for cost analysis (per-batch, per-unit, bulk pricing tiers)
- [ ] Implement `services/cost_analysis.py` with pricing logic
- [ ] Integrate cost calculation into POST /calculate response
- [ ] **TDD**: Test partial pricing (missing ingredient prices)

### 2.6 Authentication (P3 User Story 5)
- [ ] **TDD**: Write tests for JWT generation, validation, expiration
- [ ] Implement `services/auth_service.py` with python-jose
- [ ] **TDD**: Write tests for password hashing (bcrypt)
- [ ] Implement `repositories/user_repository.py`
- [ ] **TDD**: Write httpx tests for auth endpoints (login, refresh, unauthorized access)
- [ ] Implement FastAPI routers `api/v1/auth.py`
- [ ] Add authentication dependency to protected endpoints

### 2.7 Performance & Load Testing
- [ ] Write Locust script (`scripts/load_test.py`) simulating 100 concurrent users
- [ ] Run load tests: Verify <200ms p95 response times
- [ ] Profile slow queries: Use EXPLAIN ANALYZE on PostgreSQL queries
- [ ] Optimize: Add database indexes if queries exceed 50ms
- [ ] Re-run tests to validate improvements

### 2.8 Observability & Monitoring
- [ ] Configure structured JSON logging (Python logging module)
- [ ] Add request IDs to logs for tracing
- [ ] Integrate Sentry SDK for error tracking
- [ ] Create deployment monitoring dashboard (Prometheus/Grafana or APM equivalent)
- [ ] Set up uptime monitoring (UptimeRobot/Pingdom)

### 2.9 Deployment Automation
- [ ] Write Containerfile (Podman build with Fedora base image)
- [ ] Create Quadlet .container units (soap-api.container, soap-postgres.container)
- [ ] Write Ansible playbook (`ansible/playbooks/deploy-api.yml`)
- [ ] Configure Ansible Vault for production secrets (JWT key, DB password)
- [ ] Test deployment to staging environment
- [ ] Write rollback playbook (`ansible/playbooks/rollback.yml`)
- [ ] Document deployment procedure in `DEPLOYMENT.md`

## Testing Strategy

### Unit Tests (`tests/unit/`)
- **Coverage Target**: >95% for calculation services
- **Tools**: pytest, pytest-cov
- **Focus**: Saponification math, quality metrics, cost logic, auth service
- **Approach**: Isolated tests with mocked dependencies, fast execution (<5s total)

### Integration Tests (`tests/integration/`)
- **Coverage Target**: 100% of API endpoints
- **Tools**: pytest, httpx (async HTTP client)
- **Focus**: API contracts, database transactions, error responses
- **Approach**: Test database with migrations, realistic request/response cycles

### Property-Based Tests (`tests/property/`)
- **Coverage Target**: Edge cases for calculation accuracy
- **Tools**: Hypothesis (property-based testing library)
- **Focus**: Saponification calculations (e.g., "lye amount never negative", "quality scores 0-100")
- **Approach**: Generate random valid inputs, verify mathematical invariants

### Load Tests (`scripts/load_test.py`)
- **Coverage Target**: Performance budgets (<200ms p95, 100+ concurrent users)
- **Tools**: Locust (Python load testing framework)
- **Focus**: POST /calculate, GET /recipes, database query performance
- **Approach**: Ramp up from 10 to 100 users over 5 minutes, measure p95 latency

## Deployment Strategy

### Containerization (Podman)
- **Base Image**: `FROM fedora:42` (matches host platform)
- **Multi-stage build**: Builder stage for dependencies, runtime stage for app
- **Security**: Rootless Podman where possible, SELinux labels configured
- **Volumes**: Persistent volume for PostgreSQL data

### Orchestration (Quadlet)
- **systemd Integration**: Quadlet .container units managed by systemd
- **Dependencies**: soap-api.container depends on soap-postgres.container
- **Restart Policy**: `Restart=always` for production resilience
- **Health Checks**: Periodic HTTP health endpoint checks

### Configuration Management (Ansible)
- **Playbook Structure**: Roles for application deployment and database setup
- **Secrets**: Ansible Vault for JWT keys, database passwords
- **Idempotency**: Playbooks safely re-runnable without side effects
- **Rollback**: Separate playbook to revert to previous container version

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Python 3.11
      - Install dependencies
      - Run pytest (unit + integration + property tests)
      - Check coverage ≥90% (pytest-cov)
      - Run linting (Ruff, Black, mypy)
      - Run security scans (Bandit, Safety)

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - Build Podman container
      - Tag with commit SHA
      - Push to container registry

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - Run Ansible playbook (deploy-api.yml)
      - Verify deployment health checks
      - Notify Sentry of release
```

## Risk Mitigation

### Technical Risks
- **Risk**: Additive research insufficient for accurate modeling
  - **Mitigation**: Phase 0 research gate, confidence levels in API responses, user feedback loop
- **Risk**: Database performance degrades with large recipe libraries
  - **Mitigation**: Early load testing, PostgreSQL query optimization, database indexes
- **Risk**: Calculation accuracy errors in production
  - **Mitigation**: Property-based testing, reference implementation validation, comprehensive test coverage

### Operational Risks
- **Risk**: Deployment failures on Fedora 42 host
  - **Mitigation**: Staging environment testing, Ansible playbook dry-run mode, rollback procedure
- **Risk**: Security vulnerabilities in dependencies
  - **Mitigation**: Automated security scans (Bandit, Safety), Dependabot alerts, regular updates
- **Risk**: Data loss or corruption
  - **Mitigation**: PostgreSQL ACID transactions, database backups, Alembic migration testing

### Schedule Risks
- **Risk**: Phase 0 research takes longer than estimated (2-4 weeks)
  - **Mitigation**: Start with subset of additives (3-4), expand dataset in Phase 2
- **Risk**: TDD slows initial development
  - **Mitigation**: Front-load test infrastructure setup, reuse test fixtures, property-based tests catch more bugs faster

## Success Metrics

### Development Metrics
- ✅ All 14 functional requirements implemented and tested
- ✅ Test coverage ≥90% (measured by pytest-cov)
- ✅ Zero high/critical security vulnerabilities (Bandit, Safety scans)
- ✅ API documentation complete and accurate (OpenAPI at `/docs`)

### Performance Metrics
- ✅ API response times <200ms p95 (load tested with Locust)
- ✅ Database queries <50ms (EXPLAIN ANALYZE verified)
- ✅ Supports 100+ concurrent users without degradation

### Quality Metrics
- ✅ Calculation accuracy within 1% of reference implementations (10+ validated recipes)
- ✅ All additive coefficients cite peer-reviewed sources (database audit)
- ✅ Zero data loss over 30-day production period (transaction integrity verified)

### Operational Metrics
- ✅ Successful deployment to production (Ansible playbook completes)
- ✅ MGA Automotive using API within 2 weeks (usage logs)
- ✅ Monitoring and alerting operational (Sentry, APM, uptime checks)

## Next Steps

1. **Constitution Re-Check**: Verify all gates still passing after design phase
2. **Phase 0 Execution**: Begin additive research literature review (2-4 weeks)
3. **Phase 1 Execution**: Complete data model, API contracts, quickstart documentation (1 week)
4. **Phase 2 Execution**: TDD implementation following task order (4-6 weeks)
5. **Production Deployment**: Ansible playbook execution, monitoring verification (1 week)
6. **User Acceptance**: MGA Automotive validation and feedback collection (2 weeks)

**Total Estimated Timeline**: 10-14 weeks from start to production deployment

---

**Phase 0 Start Date**: TBD (awaiting constitution approval)
**Phase 1 Target Completion**: TBD
**Phase 2 Target Completion**: TBD
**Production Deployment Target**: TBD
