# Feature Specification: Phase 1 - MVP API Foundation

**Feature Branch**: `001-mvp-api-foundation`
**Created**: 2025-11-04
**Status**: Draft
**Input**: MGA Soap Calculator Phase 1 requirements from agent-os/product/

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Professional Soap Maker Calculates Base Recipe (Priority: P1)

Shale (MGA Automotive soap production) needs to calculate lye requirements and quality metrics for a new olive oil and coconut oil soap recipe to evaluate if it meets their hardness and conditioning standards before production.

**Why this priority**: Core saponification calculations are the foundation. Without accurate lye calculations, soap won't saponify correctly (too caustic or too soft). This is the minimum viable calculator functionality.

**Independent Test**: Can be fully tested by submitting oil percentages via API and receiving correct lye amounts, water ratios, and quality scores. Validates against manual calculations or validated spreadsheets. Delivers immediate value for single-batch recipe evaluation.

**Acceptance Scenarios**:

1. **Given** a recipe with 70% olive oil and 30% coconut oil at 500g total oils with 5% superfat, **When** API calculates saponification, **Then** returns correct NaOH amount (within 0.5g tolerance), water amount, and quality metrics (Hardness, Cleansing, Conditioning, Bubbly, Creamy scores)

2. **Given** an invalid recipe with negative oil percentages, **When** API receives request, **Then** returns 400 Bad Request with clear validation error message indicating which field is invalid

3. **Given** a recipe using oils not in database, **When** API receives request, **Then** returns 404 Not Found with list of unknown oils and available oil names

---

### User Story 2 - Predict Additive Impact on Soap Quality (Priority: P1)

Shale wants to add kaolin clay to a base recipe and understand how it will affect the soap's hardness and lather properties before committing to a production batch.

**Why this priority**: This is our unique competitive advantage - no existing calculator models additive effects on quality metrics. This story validates our core value proposition and research-backed approach.

**Independent Test**: Can be tested by submitting base recipe + additive (e.g., 2% kaolin clay) and comparing quality metrics against base recipe without additives. Research citations must be returned in response metadata. Delivers unique value that differentiates from all competitors.

**Acceptance Scenarios**:

1. **Given** a base recipe with known quality metrics (Hardness: 35, Conditioning: 60), **When** adding 2% kaolin clay via API, **Then** returns modified quality metrics showing increased Hardness and reduced Bubbly Lather with research citation in response metadata

2. **Given** a recipe with 5% sea salt additive, **When** API calculates quality impact, **Then** returns increased Hardness score, modified Cleansing score, and Creamy Lather adjustment with confidence level ("high", "medium", "low") based on research sources

3. **Given** an additive without research-backed coefficients (flagged as "low confidence"), **When** API processes request, **Then** returns quality estimates with warning flag and note that data is preliminary/requires validation

---

### User Story 3 - Save and Retrieve Recipes (Priority: P2)

Shale needs to store tested recipes with cost data and retrieve them later for batch production without recalculating everything manually each time.

**Why this priority**: Recipe persistence enables recipe library building and historical reference. Important for workflow efficiency but base calculations must work first (depends on P1 stories).

**Independent Test**: Can be tested by creating recipe via POST, retrieving via GET, verifying data integrity, and testing recipe versioning (updates create new versions). Delivers workflow value by eliminating manual record-keeping.

**Acceptance Scenarios**:

1. **Given** a calculated recipe with name, oils, additives, and quality metrics, **When** POST to `/recipes` endpoint with authentication, **Then** recipe stored in PostgreSQL with auto-generated UUID, timestamp, and returns 201 Created with recipe ID

2. **Given** authenticated user with stored recipes, **When** GET `/recipes` endpoint, **Then** returns paginated list of user's recipes with summary data (name, created date, base oils, quality scores) in <50ms

3. **Given** an existing recipe with ID, **When** PUT to `/recipes/{id}` with modified oil percentages, **Then** creates new recipe version preserving original, returns 200 OK with new version ID and incremented version number

---

### User Story 4 - Calculate Recipe Costs (Priority: P2)

Shale needs to understand per-batch and per-bar costs for pricing decisions and profit margin analysis when creating new soap products.

**Why this priority**: Cost analysis is critical for business decisions but requires working calculation engine first. Enables data-driven pricing strategy.

**Independent Test**: Can be tested by submitting recipe with ingredient pricing, batch size, and receiving per-batch cost breakdown and per-unit cost. Validates against manual spreadsheet calculations.

**Acceptance Scenarios**:

1. **Given** a recipe with olive oil ($8/lb), coconut oil ($5/lb), and 500g total oils, **When** API calculates costs, **Then** returns per-ingredient costs, total batch cost, and cost per 100g soap bar

2. **Given** a recipe with multiple pricing tiers for bulk ingredients, **When** batch size triggers bulk pricing threshold, **Then** cost calculation automatically applies bulk discount and shows cost savings vs. standard pricing

3. **Given** incomplete ingredient pricing (some oils have prices, others don't), **When** API calculates costs, **Then** returns partial cost breakdown with warning about missing prices and list of ingredients needing price data

---

### User Story 5 - Secure API Access for Production Integration (Priority: P3)

MGA Automotive needs secure API authentication to integrate soap calculator into internal production systems without exposing endpoints to unauthorized access.

**Why this priority**: Security is important but can initially use basic auth or API keys. JWT infrastructure is production-grade requirement but not blocking for initial testing.

**Independent Test**: Can be tested by attempting access without token (receives 401), with valid token (receives data), and with expired token (receives 401 with refresh instructions). Validates auth flow independently.

**Acceptance Scenarios**:

1. **Given** valid user credentials, **When** POST to `/auth/login` with username/password, **Then** returns JWT access token (15min expiry) and refresh token (7 day expiry) with 200 OK

2. **Given** expired access token, **When** making API request, **Then** returns 401 Unauthorized with error message indicating token expiration and instructions to use refresh token

3. **Given** valid API key for service-to-service auth, **When** included in Authorization header as `Bearer {api_key}`, **Then** grants access to endpoints with appropriate scoped permissions (e.g., read-only vs. read-write)

---

### Edge Cases

- What happens when oil percentages don't sum to 100%? (API should normalize or return validation error)
- How does system handle extreme superfat percentages (negative or >20%)? (Validation limits: 0-20%)
- What if additive percentage exceeds physically realistic amounts (e.g., 50% clay)? (Warning flag or validation limit)
- How does system handle database connection failures during recipe save? (Transaction rollback, 503 Service Unavailable response)
- What happens when concurrent requests modify the same recipe? (Optimistic locking with version checks)
- How does API respond to malformed JSON or missing required fields? (400 Bad Request with detailed validation errors via Pydantic)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate NaOH (lye) requirements based on saponification values for each oil with accuracy within 0.5g per 500g batch
- **FR-002**: System MUST calculate quality metrics (Hardness, Cleansing, Conditioning, Bubbly Lather, Creamy Lather) based on fatty acid profiles with scores 0-100
- **FR-003**: System MUST apply research-backed coefficients to model additive effects on quality metrics (kaolin clay, bentonite clay, sea salt, Himalayan salt, oatmeal, coffee grounds, activated charcoal)
- **FR-004**: System MUST store research citations with additive data in JSONB metadata including source, DOI/URL, confidence level
- **FR-005**: System MUST persist recipes in PostgreSQL with version history (immutable audit trail of modifications)
- **FR-006**: System MUST calculate per-batch and per-unit costs based on ingredient pricing with support for bulk pricing tiers
- **FR-007**: System MUST validate all input via Pydantic models rejecting invalid oil percentages, negative values, or missing required fields
- **FR-008**: System MUST authenticate API requests using JWT tokens with 15-minute expiration and refresh token rotation
- **FR-009**: System MUST generate OpenAPI/Swagger documentation automatically via FastAPI for all endpoints
- **FR-010**: System MUST return calculation results in <200ms for standard recipes (5 oils, 2 additives)
- **FR-011**: System MUST calculate fatty acid profiles (lauric, myristic, palmitic, stearic, oleic, linoleic, linolenic) as percentages
- **FR-012**: System MUST support superfat calculations from 0-20% with 0.1% precision
- **FR-013**: System MUST calculate water ratios supporting both percentage-of-oils and lye concentration methods
- **FR-014**: System MUST provide recipe scaling calculations (multiply all ingredients by scale factor while maintaining ratios)

*Clarifications needed:*
- **FR-015**: System MUST handle fragrance oils [NEEDS CLARIFICATION: Phase 1 or Phase 2? Simple percentage input or full fragrance calculator?]
- **FR-016**: System MUST export recipes [NEEDS CLARIFICATION: Phase 1 JSON export only, or Phase 2 with PDF/CSV?]

### Key Entities *(include if feature involves data)*

- **Oil**: Represents base soap-making oils (olive, coconut, palm, etc.) with properties: name, SAP value (NaOH), fatty acid profile, typical cost per weight
- **Additive**: Represents non-fat ingredients (clays, salts, botanicals) with properties: name, quality impact coefficients (JSONB), research citations (JSONB), physical properties (solubility, color)
- **Recipe**: User-created formulation with properties: name, owner ID, oils (list with percentages), additives (list with percentages), superfat %, created/modified timestamps, version number
- **Calculation Result**: Ephemeral calculation output with properties: lye amount, water amount, quality metrics (object with 5 scores), fatty acid profile, cost breakdown, additive warnings
- **User**: API user account with properties: username, hashed password, email, API key (hashed), role (admin/user), created date

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: MGA Automotive using API for all new recipe development within 2 weeks of Phase 1 deployment (measured by API usage logs)
- **SC-002**: Calculation accuracy verified within 1% tolerance against 10 reference recipes from validated spreadsheets (measured by property-based test suite)
- **SC-003**: API response times <200ms for 95th percentile of calculation requests under 100 concurrent users (measured by load testing with Locust)
- **SC-004**: Zero data loss or corruption in recipe storage over 30-day production period (measured by database integrity checks and transaction logs)
- **SC-005**: 100% of additive quality impact coefficients cite peer-reviewed sources or validated testing (measured by database audit of additive metadata)
- **SC-006**: >90% code coverage maintained across calculation engine, API endpoints, and database operations (measured by pytest-cov reports)
- **SC-007**: All 14 functional requirements implemented and passing integration tests (measured by test suite passing in CI/CD)
- **SC-008**: API documentation auto-generated and accessible at `/docs` endpoint with examples for all endpoints (verified manually)
- **SC-009**: Zero security vulnerabilities in dependencies detected by Safety/Bandit scans (measured in CI/CD pipeline)
- **SC-010**: Recipe retrieval queries complete in <50ms for user recipe libraries up to 1000 recipes (measured by EXPLAIN ANALYZE on PostgreSQL queries)

## Technical Architecture Notes

### Calculation Engine Design
- NumPy arrays for fatty acid profile calculations (vectorized operations)
- Pydantic models for input validation and type safety
- Separate calculation modules: `saponification.py`, `quality_metrics.py`, `additive_impact.py`, `cost_analysis.py`
- Property-based testing with Hypothesis for edge case coverage

### Database Schema Highlights
- `oils` table: normalized reference data with SAP values and fatty acid profiles
- `additives` table: JSONB columns for flexible research metadata and quality coefficients
- `recipes` table: version history via `version_number` column and soft-deletes
- `recipe_oils` and `recipe_additives` junction tables for many-to-many relationships
- PostgreSQL indexes on `user_id`, `created_at`, `recipe.name` for query performance

### API Structure
- FastAPI routers: `/calculate`, `/recipes`, `/oils`, `/additives`, `/auth`
- Pydantic schemas for request/response validation
- Dependency injection for database sessions (SQLAlchemy async)
- Exception handlers for consistent error responses

### Security Implementation
- JWT tokens via `python-jose` library with HS256 algorithm
- Password hashing with `bcrypt` (Argon2 considered for Phase 2)
- API keys stored hashed in database with `secrets.compare_digest` for timing-attack resistance
- Rate limiting via FastAPI middleware (100 requests/minute per IP)

### Testing Strategy
- Unit tests: Calculation accuracy, Pydantic validation, cost logic
- Integration tests: API endpoints with httpx, database transactions
- Property-based tests: Hypothesis for saponification math edge cases
- Load tests: Locust scripts simulating 100 concurrent users

### Deployment Pipeline
- Podman container with Fedora base image (FROM fedora:42)
- Quadlet .container unit for systemd integration
- Ansible playbook for deployment automation
- PostgreSQL in separate container with persistent volume

## Out of Scope (Explicitly NOT Phase 1)

- Web UI / Frontend (Phase 3 only)
- INCI name generation (Phase 2)
- Fragrance calculator with blend ratios (Phase 2)
- Advanced batch management and yield tracking (Phase 2)
- Recipe export to PDF or CSV formats (Phase 2 - JSON export only in Phase 1)
- Multi-user team accounts (Phase 3)
- Recipe sharing or community features (Post-Phase 3)
- Mobile applications (Post-Phase 3)
- Real-time collaboration (Post-Phase 3)
- Machine learning predictions (Post-Phase 3)

## Dependencies & Prerequisites

### External Research Required
- **Additive Research Task** (Roadmap Item 1): Must complete literature review and data collection before implementing FR-003 (additive impact modeling)
- Research deliverables: Structured CSV/JSON with additive coefficients, citations, confidence levels
- Estimated research time: 2-4 weeks for initial dataset (kaolin, bentonite, sea salt, Himalayan salt, oatmeal, coffee, activated charcoal)

### Technology Setup
- PostgreSQL 15+ instance (local dev + production)
- Python 3.11+ environment with pip or Poetry
- Fedora 42 server for production deployment
- GitHub Actions for CI/CD
- Sentry account for error tracking

### Team Readiness
- Python/FastAPI development skills
- PostgreSQL database design and query optimization
- Pytest testing framework familiarity
- Basic chemistry understanding (saponification, fatty acids) or willingness to learn

## Success Dependencies

Phase 1 success blocks Phase 2 and Phase 3. If additive modeling is inaccurate or API performance is poor, subsequent phases cannot proceed. Quality gates must be met before expanding scope.

## Integration with Agent-OS

This spec-kit specification integrates with agent-os product documentation:
- **Mission** (`agent-os/product/mission.md`): Validates core value proposition (additive quality modeling)
- **Roadmap** (`agent-os/product/roadmap.md`): Implements Phase 1 items 1-9
- **Tech Stack** (`agent-os/product/tech-stack.md`): Enforces technology constraints
- **Constitution** (`.specify/memory/constitution.md`): Enforces development principles and quality gates

Next Steps:
1. Run `/speckit.plan` to generate implementation plan
2. Begin Phase 0 (Research) for additive data collection
3. Proceed to Phase 1 (Design) for data model and API contracts
4. Start Phase 2 (Implementation) with TDD cycle
