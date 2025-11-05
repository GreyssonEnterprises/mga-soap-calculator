# MGA Soap Calculator Constitution

## Core Principles

### I. API-First Architecture
**Priority**: CRITICAL | **Enforcement**: All features must expose REST API before UI

- Every feature starts as a REST API endpoint
- FastAPI automatic OpenAPI documentation required for all endpoints
- API endpoints must be fully functional and testable independently
- Web UI is a consumer of the API, never duplicates business logic
- Third-party integration capability is a first-class requirement

**Rationale**: MGA Automotive requires immediate programmatic access for production workflows. API-first enables internal use during UI development and supports future integrations (mobile, third-party tools).

### II. Research-Backed Calculations
**Priority**: CRITICAL | **Enforcement**: All quality impact calculations require documented sources

- Additive quality impact coefficients MUST cite peer-reviewed research or validated testing
- Calculation algorithms MUST include inline citations to research sources
- Database schema MUST store research citations with additive properties (JSONB metadata)
- No "community wisdom" or anecdotal data for quality modeling
- Property-based testing required for calculation accuracy validation

**Rationale**: Our competitive advantage is evidence-based additive quality modeling. Credibility requires scientific foundation, not guesswork.

### III. Test-First Development (NON-NEGOTIABLE)
**Priority**: CRITICAL | **Enforcement**: No code merged without tests

- TDD mandatory: Tests written → User approved → Tests fail → Then implement
- Red-Green-Refactor cycle strictly enforced
- pytest with >90% code coverage requirement (pytest-cov)
- Property-based testing (Hypothesis) for calculation edge cases
- Integration tests (httpx) for all API endpoints

**Rationale**: Calculation accuracy is critical. Test-first ensures correctness and prevents regressions in saponification math, quality metrics, and cost analysis.

### IV. Data Integrity & ACID Compliance
**Priority**: CRITICAL | **Enforcement**: PostgreSQL transactions for all state changes

- Recipe operations MUST use database transactions
- Version history for all recipe modifications (immutable audit trail)
- No eventual consistency patterns - ACID guarantees required
- Foreign key constraints enforced at database level
- Alembic migrations version-controlled and immutable

**Rationale**: Professional soap makers require reliable recipe storage. Data loss or corruption in formulations is unacceptable for production use.

### V. Performance Budgets
**Priority**: HIGH | **Enforcement**: Load testing required before production deployment

- API response time: <200ms for standard saponification calculations
- Database queries: <50ms for recipe retrieval (enforce with EXPLAIN ANALYZE)
- Frontend (Phase 3): First Contentful Paint <1.5s, Time to Interactive <3s
- Calculation throughput: Support 100+ concurrent requests

**Rationale**: Internal MGA production use requires responsive calculations. Slow APIs block production workflows.

### VI. Security & Authentication
**Priority**: HIGH | **Enforcement**: JWT authentication required for all non-public endpoints

- JWT tokens with short expiration (15 minutes) and refresh token rotation
- API keys hashed in database, scoped permissions for service-to-service auth
- Rate limiting enforced (FastAPI middleware or nginx)
- Input validation via Pydantic models for all API requests
- HTTPS/TLS 1.3 mandatory in production

**Rationale**: Recipe data represents business intellectual property. Authentication prevents unauthorized access and API abuse.

### VII. Deployment Platform Standards
**Priority**: CRITICAL | **Enforcement**: Fedora + Podman + Quadlet only

- **Container Runtime**: Podman (NOT Docker) with rootless operation where possible
- **Base Images**: Fedora or UBI (Universal Base Image) only - matches host platform
- **Orchestration**: Quadlet (.container systemd units) for production services
- **Configuration**: Ansible playbooks for deployment automation
- **Secrets**: Ansible Vault for production secrets, never in environment variables

**Rationale**: Fedora 42 host requires platform-compatible containers. Podman provides daemonless security, systemd integration, and SELinux compatibility. See `agent-os/standards/global/deployment-platform.md` for complete specifications.

### VIII. Observability & Monitoring
**Priority**: MEDIUM | **Enforcement**: Structured logging and error tracking required

- Structured JSON logging (Python logging module) with request IDs
- Sentry integration for error tracking and alerting
- Prometheus + Grafana or equivalent APM for performance monitoring
- Uptime monitoring (UptimeRobot/Pingdom) for production availability
- Log aggregation (Loki or CloudWatch) for centralized access

**Rationale**: Production use requires visibility into system health, calculation accuracy, and error patterns.

## Technology Constraints

### Mandatory Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Database**: PostgreSQL 15+, JSONB for flexible metadata
- **Testing**: pytest, Hypothesis, httpx, pytest-cov
- **Deployment**: Podman, Quadlet, Ansible, Fedora/UBI base images
- **CI/CD**: GitHub Actions with automated testing and container builds

### Phase 3 Frontend (When Implemented)
- **Framework**: React 18+, TypeScript, Vite
- **Styling**: Tailwind CSS with Headless UI or Radix UI
- **State Management**: TanStack Query (React Query), React Hook Form
- **Testing**: Vitest, React Testing Library, Playwright (E2E)

### Forbidden Technologies
- **Docker/docker-compose**: Use Podman + Quadlet instead
- **Flask/Django**: Use FastAPI per stack decision
- **MySQL/MongoDB**: Use PostgreSQL per ACID requirements
- **Debian/Ubuntu base images**: Use Fedora/UBI per platform compatibility

## Development Workflow

### Feature Development Process
1. **Specification**: Create spec document in `.specify/specs/[feature]/spec.md`
2. **Planning**: Generate implementation plan with `/speckit.plan`
3. **Research** (Phase 0): Document research findings for additive data if applicable
4. **Design** (Phase 1): Data model, API contracts, quickstart documentation
5. **Implementation** (Phase 2): TDD cycle with tests first, then implementation
6. **Integration Testing**: httpx tests for API endpoints, contract tests for new services
7. **Code Review**: PR with constitution compliance verification
8. **Deployment**: Ansible playbook updates, Quadlet container unit creation

### Branching Strategy
- **Feature branches**: `###-feature-name` (e.g., `001-saponification-calculator`)
- **Main branch**: Protected, requires PR approval and passing CI
- **Conventional Commits**: For changelog generation and semantic versioning

### Code Review Requirements
- Constitution compliance verified (checklist in PR template)
- Test coverage ≥90% maintained
- API documentation updated (OpenAPI/Swagger)
- Calculation accuracy validated (property-based tests)
- Performance budgets respected (load testing for API endpoints)

## Quality Gates

### Pre-Merge Requirements
- ✓ All tests passing (unit, integration, property-based)
- ✓ Code coverage ≥90% (pytest-cov report)
- ✓ Type checking passing (mypy --strict)
- ✓ Linting passing (Ruff, Black)
- ✓ API documentation generated (FastAPI OpenAPI)
- ✓ Calculation accuracy validated (reference implementations or validated spreadsheets)
- ✓ Constitution compliance (constitution-check.md in PR)

### Pre-Production Requirements
- ✓ Integration tests passing (API endpoint tests)
- ✓ Load testing completed (>100 concurrent requests, <200ms p95)
- ✓ Security scan completed (Bandit, Safety for dependencies)
- ✓ Monitoring configured (Sentry, APM, uptime checks)
- ✓ Deployment automation tested (Ansible playbook dry-run)
- ✓ Rollback procedure documented

## Additive Research Standards

### Research Documentation Requirements
- **Source Type**: Peer-reviewed journal articles, industry standards, validated testing
- **Citation Format**: APA style with DOI/URL in database metadata
- **Data Structure**: JSONB column with `{source: "citation", coefficient: value, confidence: "high|medium|low"}`
- **Validation**: Cross-reference multiple sources, flag single-source data
- **Update Cadence**: Annual literature review for new research

### Acceptable Research Sources
- ✓ Peer-reviewed cosmetic chemistry journals
- ✓ Industry standards (ISO, ASTM for soap testing)
- ✓ Validated laboratory testing (documented methodology)
- ✓ Soapmaking equipment manufacturer specifications
- ✗ Blog posts, forum discussions, anecdotal reports (not acceptable)

## Scope Management

### Phase 1 Scope (MVP API)
- Core saponification calculations
- Quality metrics (Hardness, Cleansing, Conditioning, Bubbly, Creamy)
- Fatty acid profile analysis
- Additive quality impact modeling (research-backed)
- Recipe CRUD operations
- Cost calculator
- API authentication (JWT)

### Phase 2 Scope (Enhanced API)
- INCI name generation
- Fragrance calculator
- Advanced batch management
- Recipe export/import
- API versioning
- Performance optimization
- Comprehensive testing (>90% coverage)

### Phase 3 Scope (Public Web)
- User authentication & accounts
- React frontend (recipe builder UI)
- Recipe management dashboard
- Cost analysis interface
- INCI & labeling tools
- Responsive design (mobile-first)
- Production web deployment

### Explicitly Out of Scope (Until Post-Phase 3)
- Mobile native applications
- Community features (recipe sharing, ratings, forums)
- Supply chain integration
- Multi-user team accounts
- Real-time collaboration
- Machine learning predictions

## Governance

### Constitution Authority
This constitution supersedes project documentation conflicts. Technical Stack decisions in `agent-os/product/tech-stack.md` and roadmap priorities in `agent-os/product/roadmap.md` must align with constitution principles.

### Amendment Process
1. Propose amendment in GitHub issue with justification
2. Technical review by maintainers
3. Constitution version bump (semantic versioning: MAJOR.MINOR.PATCH)
4. Migration plan documented if breaking changes
5. Update date stamp and version in constitution header

### Compliance Enforcement
- All PRs must include constitution compliance checklist
- Automated checks in CI/CD for technology constraints
- Manual review for research documentation and quality gates
- Non-compliance blocks merge (no exceptions for deadlines)

### Exception Handling
- **Temporary exceptions**: Require GitHub issue with sunset date
- **Permanent exceptions**: Require constitution amendment
- **No silent deviations**: All divergences must be documented

### Guidance Document
Runtime development guidance stored in `.specify/memory/guidance.md` (created as needed). Constitution defines WHAT, guidance defines HOW for common scenarios.

---

**Version**: 1.0.0
**Ratified**: 2025-11-04
**Last Amended**: 2025-11-04
**Applies To**: MGA Soap Calculator (all phases)
