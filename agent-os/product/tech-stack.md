# Tech Stack

Complete technical architecture for MGA Soap Calculator across all phases.

---

## Backend (Phase 1 - MVP)

### Core Framework
- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **API Style:** REST
- **ASGI Server:** Uvicorn (production: Gunicorn + Uvicorn workers)

**Rationale:** FastAPI provides automatic OpenAPI documentation, native async support, type safety with Pydantic, and excellent performance. Python chosen for calculation-heavy logic, scientific computing ecosystem (NumPy, SciPy), and accessibility to soap makers familiar with Python.

### Authentication & Authorization
- **Strategy:** JWT (JSON Web Tokens)
- **Library:** python-jose or PyJWT
- **API Keys:** Custom implementation for service-to-service auth
- **Future (Phase 3):** OAuth 2.0 with social providers (Authlib)

### Calculation Engine
- **Numeric Computing:** NumPy for array operations and mathematical modeling
- **Scientific Functions:** SciPy for advanced calculations if needed
- **Validation:** Pydantic models for input validation and type safety
- **Testing:** pytest with property-based testing (Hypothesis) for calculation accuracy

---

## Database

### Primary Database
- **RDBMS:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0 (async support)
- **Migration Tool:** Alembic
- **Connection Pooling:** SQLAlchemy built-in pool or pgBouncer for high traffic

**Rationale:** PostgreSQL provides ACID compliance for recipe data integrity, JSONB support for flexible additive properties, excellent query performance, and production-ready scalability. Superior to SQLite for multi-user scenarios.

### Schema Design Principles
- **Normalized Structure:** Separate tables for recipes, ingredients, additives, batches, users
- **Version Control:** Recipe revision history with timestamps
- **Flexible Metadata:** JSONB columns for additive properties and research citations
- **Cost Tracking:** Price history tables for ingredient cost trends

### Future Considerations
- **Redis:** Caching layer for frequently-accessed calculations (Phase 2)
- **Elasticsearch:** Full-text search for recipes and ingredients (if needed)

---

## Frontend (Phase 3 - Future)

### Core Framework
- **Library:** React 18+
- **Language:** TypeScript
- **Build Tool:** Vite
- **Package Manager:** npm or pnpm

**Rationale:** React provides component reusability, strong ecosystem, TypeScript adds type safety, Vite offers fast dev server and optimized builds. Matches project standards documented in user preferences.

### Styling & UI
- **CSS Framework:** Tailwind CSS
- **Component Library:** Headless UI or Radix UI (unstyled primitives + Tailwind)
- **Icons:** Heroicons or Lucide React
- **Charts/Visualization:** Recharts or Chart.js for quality metric displays

### State Management
- **Options:** Redux Toolkit, Zustand, or React Context (TBD based on complexity)
- **API Client:** TanStack Query (React Query) for server state management
- **Form Handling:** React Hook Form with Zod validation

### Routing & Navigation
- **Router:** React Router v6
- **Code Splitting:** React.lazy and Suspense for route-based code splitting

### Testing (Frontend)
- **Unit Tests:** Vitest (Vite-native testing framework)
- **Component Tests:** React Testing Library
- **E2E Tests:** Playwright
- **Accessibility Testing:** axe-core via jest-axe or Playwright

---

## Infrastructure

### Hosting & Deployment
- **Platform:** TBD (AWS, DigitalOcean, Render, or Railway)
- **Containerization:** Docker with multi-stage builds
- **Orchestration:** Docker Compose for local dev, Kubernetes if scaling demands (unlikely initially)
- **CDN:** Cloudflare or AWS CloudFront for static asset delivery (Phase 3)

### CI/CD Pipeline
- **Platform:** GitHub Actions
- **Workflow:**
  1. Linting (Ruff, Black, mypy for Python; ESLint, Prettier for TypeScript)
  2. Type checking (mypy, tsc)
  3. Unit tests (pytest, Vitest)
  4. Integration tests (pytest + httpx)
  5. E2E tests (Playwright)
  6. Docker build
  7. Deploy to staging/production

### Configuration Management
- **Tool:** Ansible (per project standards)
- **Secrets Management:** Environment variables (.env files locally, secret management service in production)
- **Feature Flags:** Environment-based or LaunchDarkly/Flagsmith if complex rollouts needed

### Monitoring & Observability
- **Application Monitoring:** Sentry for error tracking
- **Performance Monitoring:** APM tool (New Relic, DataDog, or self-hosted Prometheus + Grafana)
- **Logging:** Structured JSON logging with Python's logging module, aggregated via Loki or CloudWatch
- **Uptime Monitoring:** UptimeRobot or Pingdom

---

## Development Tools

### Version Control
- **VCS:** Git
- **Platform:** GitHub
- **Branch Strategy:** Feature branches with PR reviews, main branch protected
- **Commit Convention:** Conventional Commits for changelog generation

### Python Tooling
- **Package Manager:** pip with requirements.txt or Poetry for dependency management
- **Linting:** Ruff (fast, modern linter replacing Flake8/Black/isort)
- **Formatting:** Black (code formatter)
- **Type Checking:** mypy with strict mode
- **Security Scanning:** Bandit for Python security linting, Safety for dependency vulnerability checks

### TypeScript Tooling (Phase 3)
- **Linting:** ESLint with TypeScript plugin
- **Formatting:** Prettier
- **Type Checking:** TypeScript compiler (tsc)

### API Development Tools
- **API Client:** HTTPie or Postman for manual testing
- **Load Testing:** Locust or k6 for performance testing
- **Documentation:** FastAPI automatic OpenAPI/Swagger UI

### Local Development
- **Environment Management:** pyenv for Python version management, nvm for Node.js
- **Database GUI:** pgAdmin, DBeaver, or Postico for PostgreSQL inspection
- **API Testing:** Postman collections or HTTPie scripts

---

## Testing Strategy

### Backend Testing
- **Unit Tests:** pytest with fixtures and parametrization
- **Integration Tests:** pytest + httpx for API endpoint testing
- **Property-Based Tests:** Hypothesis for calculation accuracy edge cases
- **Coverage Target:** >90% code coverage (pytest-cov)
- **Test Database:** Separate PostgreSQL instance or in-memory SQLite for speed

### Frontend Testing (Phase 3)
- **Unit Tests:** Vitest for component logic
- **Component Tests:** React Testing Library for UI behavior
- **E2E Tests:** Playwright for critical user flows (recipe creation, calculation, cost analysis)
- **Visual Regression:** Percy or Chromatic (optional)
- **Accessibility Tests:** axe-core integration in E2E tests

### Calculation Validation
- **Reference Implementation:** Manual calculations or validated spreadsheets as test fixtures
- **Edge Case Coverage:** Property-based testing for unusual ingredient combinations
- **Regression Suite:** Known-good recipes as test cases to prevent accuracy drift

---

## Security Considerations

### Application Security
- **Input Validation:** Pydantic models for all API inputs, SQL injection prevention via ORM
- **Authentication:** JWT with short expiration times, refresh token rotation
- **HTTPS:** TLS 1.3 enforced in production
- **Rate Limiting:** FastAPI middleware or nginx rate limiting to prevent abuse
- **CORS:** Restricted origins for API access

### Data Security
- **Password Hashing:** Argon2 or bcrypt for user passwords (Phase 3)
- **API Keys:** Hashed storage, scoped permissions
- **Database Encryption:** PostgreSQL TDE (Transparent Data Encryption) if handling sensitive user data
- **Secrets:** Never commit to version control, use environment variables or secret manager

### Dependency Security
- **Scanning:** Dependabot or Snyk for vulnerability alerts
- **Updates:** Regular dependency updates, security patches prioritized
- **Supply Chain:** Lock files (requirements.txt hash mode or Poetry lock) for reproducible builds

---

## Performance Targets

### API Performance
- **Response Time:** <200ms for standard saponification calculations
- **Throughput:** Support 100+ concurrent requests (adequate for internal + small external user base)
- **Database Queries:** <50ms for recipe retrieval, optimized indexes

### Frontend Performance (Phase 3)
- **First Contentful Paint:** <1.5s
- **Time to Interactive:** <3s
- **Bundle Size:** <300KB initial JavaScript bundle (code-split routes)

### Scalability
- **Phase 1-2:** Single server adequate for internal MGA use
- **Phase 3:** Horizontal scaling if user base grows (load balancer + multiple app servers)

---

## Architectural Patterns

### Backend Architecture
- **Pattern:** Layered architecture (routes → services → repositories → database)
- **Dependency Injection:** FastAPI's built-in dependency injection for services
- **Error Handling:** Centralized exception handlers, structured error responses
- **API Versioning:** URL path versioning (/api/v1/, /api/v2/)

### Frontend Architecture (Phase 3)
- **Pattern:** Component-based with feature-based folder structure
- **Data Flow:** Unidirectional data flow (React principles)
- **API Integration:** Centralized API client with TanStack Query for caching and state
- **Routing:** Lazy-loaded route components for code splitting

### Database Patterns
- **Migrations:** Version-controlled with Alembic, immutable migration files
- **Transactions:** ACID guarantees for recipe updates
- **Indexing Strategy:** Indexes on foreign keys, frequently-queried columns (user_id, recipe name)

---

## Rationale Summary

### Why Python/FastAPI?
- **Calculation Focus:** Python excels at numerical computing with NumPy/SciPy
- **Type Safety:** FastAPI + Pydantic provide runtime validation and automatic docs
- **Performance:** Async support for I/O-bound operations (database, external APIs)
- **Ecosystem:** Rich scientific computing libraries, easy integration with research tools
- **Accessibility:** Soap makers familiar with Python can contribute or extend

### Why PostgreSQL?
- **Data Integrity:** ACID compliance critical for recipe version control
- **Scalability:** Handles growth from single-user to thousands without architecture changes
- **JSON Support:** JSONB for flexible additive properties without schema migrations
- **Production-Ready:** Battle-tested, excellent tooling, strong community

### Why React/TypeScript/Tailwind (Phase 3)?
- **Type Safety:** TypeScript prevents runtime errors, improves maintainability
- **Component Reusability:** React's component model for recipe builder UI elements
- **Developer Experience:** Vite provides fast dev server, Tailwind enables rapid styling
- **Project Standards:** Matches user's documented preferences for frontend stack

### Why API-First?
- **Immediate Value:** MGA can integrate into workflows without waiting for web UI
- **Flexibility:** Web, mobile, or third-party integrations all consume same API
- **Testing:** API tests provide confidence before UI development
- **Decoupling:** Frontend and backend teams can work in parallel (if scaling team)

---

## Technology Decision Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| FastAPI over Flask/Django | Automatic docs, async support, type safety | Flask (too minimal), Django (too heavyweight) |
| PostgreSQL over MySQL | JSONB support, better standards compliance | MySQL (less feature-rich), MongoDB (no transactions) |
| SQLAlchemy over raw SQL | ORM safety, migration support, query building | Raw SQL (maintenance burden), Django ORM (framework lock-in) |
| React over Vue/Svelte | Larger ecosystem, team familiarity | Vue (smaller ecosystem), Svelte (newer, less mature) |
| Tailwind over Bootstrap | Utility-first flexibility, smaller bundle | Bootstrap (opinionated design), CSS Modules (more verbose) |
| Vite over Create React App | Faster dev server, better build optimization | CRA (deprecated), Next.js (SSR overkill for this use case) |
| Ansible over Terraform | Project standard, simpler for application deployment | Terraform (infrastructure-focused), manual deployment (not reproducible) |
| GitHub Actions over Jenkins | Integrated with repo, simpler configuration | Jenkins (more setup overhead), GitLab CI (not using GitLab) |

---

## Future Technology Considerations

### Potential Additions (Post-Phase 3)
- **GraphQL API:** If frontend query complexity increases (alternative to REST v2)
- **WebSockets:** Real-time collaboration on recipes (multiplayer editing)
- **Message Queue:** Background job processing for batch calculations (Celery + Redis)
- **Mobile SDKs:** React Native for cross-platform mobile apps
- **Machine Learning:** Recipe quality prediction models (scikit-learn, TensorFlow)
- **Search Engine:** Elasticsearch for advanced recipe search and recommendations

### Technology Review Cadence
- **Annual Review:** Assess if stack choices still align with project goals
- **Dependency Updates:** Quarterly major version updates, monthly security patches
- **Emerging Tech Evaluation:** Quarterly scan of new tools that might improve DX or performance
