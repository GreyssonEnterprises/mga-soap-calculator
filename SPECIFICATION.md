# MGA Soap Calculator - Specification Overview

This project uses **spec-kit** for specification-driven development integrated with **agent-os** product documentation.

## Quick Links

### Project Constitution
📜 **[`.specify/memory/constitution.md`](.specify/memory/constitution.md)**

The project constitution defines non-negotiable development principles:
- API-First Architecture (REST before UI)
- Research-Backed Calculations (peer-reviewed sources required)
- Test-First Development (TDD mandatory, >90% coverage)
- ACID Data Integrity (PostgreSQL transactions)
- Performance Budgets (<200ms API responses)
- Security Standards (JWT auth, rate limiting)
- Deployment Platform (Podman + Quadlet + Fedora/UBI)
- Observability Requirements (structured logging, Sentry)

**All development must comply with constitution principles.**

### Phase 1 Specification
📋 **[`.specify/specs/001-mvp-api/spec.md`](.specify/specs/001-mvp-api/spec.md)**

Phase 1 MVP API specification with:
- 5 prioritized user stories (P1: calculations, P2: persistence/cost, P3: auth)
- 14+ functional requirements
- Measurable success criteria
- Technical architecture notes
- Explicit scope boundaries

### Phase 1 Implementation Plan
🗺️ **[`.specify/specs/001-mvp-api/plan.md`](.specify/specs/001-mvp-api/plan.md)**

Detailed implementation plan including:
- Technical context and constraints
- Constitution compliance checklist
- Complete project structure (file-level detail)
- Phase 0: Research & data collection
- Phase 1: Design & architecture
- Phase 2: Implementation (TDD approach)
- Testing strategy (unit, integration, property-based, load)
- Deployment strategy (Podman, Quadlet, Ansible, CI/CD)
- 10-14 week timeline estimate

## Agent-OS Integration

Spec-kit documents integrate with agent-os product documentation:

- **[`agent-os/product/mission.md`](agent-os/product/mission.md)** → Constitution principles, user personas
- **[`agent-os/product/roadmap.md`](agent-os/product/roadmap.md)** → Spec user stories, success criteria
- **[`agent-os/product/tech-stack.md`](agent-os/product/tech-stack.md)** → Constitution tech constraints, deployment details

## Development Workflow

### 1. Review Constitution
Read `.specify/memory/constitution.md` to understand project principles and quality gates.

### 2. Review Specification
Read `.specify/specs/001-mvp-api/spec.md` for Phase 1 requirements and user stories.

### 3. Review Implementation Plan
Read `.specify/specs/001-mvp-api/plan.md` for technical architecture and execution roadmap.

### 4. Begin Phase 0 (Research)
- Literature review for additive quality impact coefficients
- Document findings in `.specify/specs/001-mvp-api/research.md`
- Prepare structured dataset with citations

### 5. Execute Phase 1 (Design)
- Create data model document (`.specify/specs/001-mvp-api/data-model.md`)
- Define API contracts (`.specify/specs/001-mvp-api/api-contracts.md`)
- Write quickstart guide (`.specify/specs/001-mvp-api/quickstart.md`)

### 6. Execute Phase 2 (Implementation)
- Follow TDD cycle (Red-Green-Refactor)
- Implement in order: Database → Calculations → API → Persistence → Cost → Auth
- Maintain >90% test coverage (pytest-cov)
- Run load tests (<200ms p95 response times)

### 7. Deploy to Production
- Build Podman container (Fedora base image)
- Deploy via Ansible playbook
- Configure Quadlet systemd units
- Verify monitoring (Sentry, APM, uptime checks)

## Key Decisions

### Technology Stack (Enforced by Constitution)
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic
- **Database**: PostgreSQL 15+ (JSONB for metadata)
- **Testing**: pytest, Hypothesis, httpx, pytest-cov
- **Deployment**: Podman, Quadlet, Ansible, Fedora/UBI images
- **CI/CD**: GitHub Actions

### Forbidden Technologies
- ❌ Docker/docker-compose (use Podman + Quadlet)
- ❌ Flask/Django (use FastAPI)
- ❌ MySQL/MongoDB (use PostgreSQL)
- ❌ Debian/Ubuntu images (use Fedora/UBI)

### Competitive Differentiator
**Industry-first additive quality modeling**: No existing soap calculator models how non-fat additives (clays, salts, botanicals) affect soap properties. Our research-backed coefficients with peer-reviewed citations provide unique value for professional soap makers.

## Success Metrics

Phase 1 is successful when:
- ✅ MGA Automotive using API for all recipe development (within 2 weeks)
- ✅ Calculation accuracy within 1% of reference implementations
- ✅ API response times <200ms p95 (100+ concurrent users)
- ✅ >90% test coverage (pytest-cov)
- ✅ All additive coefficients cite peer-reviewed sources
- ✅ Zero data loss over 30-day production period

## Project Timeline

**Estimated Duration**: 10-14 weeks

- **Phase 0** (Research): 2-4 weeks
- **Phase 1** (Design): 1 week
- **Phase 2** (Implementation): 4-6 weeks
- **Deployment**: 1 week
- **User Acceptance**: 2 weeks

## Spec-Kit Commands (Future)

Once spec-kit commands are available:
- `/speckit.analyze` - Analyze requirements
- `/speckit.clarify` - Ask clarifying questions
- `/speckit.plan` - Generate implementation plan
- `/speckit.tasks` - Break down into detailed tasks
- `/speckit.implement` - Execute TDD implementation
- `/speckit.checklist` - Generate PR compliance checklist

## Support Files

- **Agent Response**: [`agent-responses/20251104_145729_spec-writer_agent-os-to-speckit.md`](agent-responses/20251104_145729_spec-writer_agent-os-to-speckit.md)
- **Deployment Guide**: `DEPLOYMENT.md` (created in Phase 2)
- **API Documentation**: Auto-generated at `/docs` endpoint (FastAPI)

## Questions?

1. Review constitution for development principles
2. Review specification for feature requirements
3. Review implementation plan for technical details
4. Check agent response file for integration notes

---

**Constitution Version**: 1.0.0 | **Specification Status**: Draft | **Last Updated**: 2025-11-04
