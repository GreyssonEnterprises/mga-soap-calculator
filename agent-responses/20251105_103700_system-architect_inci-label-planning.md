# System Architect - INCI Label Generator Planning

**Timestamp:** 2025-11-05T10:37:00-08:00
**Task:** Generate complete implementation plan with Phase 0 research and Phase 1 design artifacts
**Requestor:** Bob

## Response

Successfully generated complete planning documentation for INCI Label Generator feature (spec 003):

### Artifacts Created

1. **plan.md** - Implementation plan with:
   - Technical context: Python 3.11+, FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15+
   - Constitution compliance: All 8 principles validated and compliant
   - Project structure: Concrete paths for models, services, API endpoints, tests
   - Performance target: <100ms API response (stricter than standard <200ms)
   - TDD approach explicitly required

2. **research.md** (Phase 0) - Research findings:
   - Saponified INCI naming patterns (NaOH → Sodium Xate, KOH → Potassium Xate)
   - Percentage calculation methodology with formulas
   - Edge case handling (Castor Oil dual names, missing INCI, trace ingredients, mixed lye)
   - Reference data structure for 37 oils
   - Regulatory compliance sorting rules

3. **data-model.md** (Phase 1) - Data model design:
   - Oil model extension: `saponified_inci_name` field (String(200), nullable)
   - Complete Alembic migration script
   - Backfill strategy with Python script
   - Pattern generation fallback
   - Validation rules

4. **contracts/inci-label.yaml** (Phase 1) - OpenAPI 3.0 specification:
   - GET `/api/v1/recipes/{recipe_id}/inci-label` endpoint
   - Request/response schemas with complete examples
   - Three format support: raw_inci, saponified_inci, common_names
   - Query parameters: format, include_percentages, line_by_line
   - Error responses: 401, 404, 422, 500

5. **quickstart.md** (Phase 1) - Integration guide:
   - JWT authentication setup
   - curl examples for all formats
   - Python integration (httpx async + requests sync)
   - TypeScript integration with types
   - Error handling patterns
   - Real-world use cases

### Key Design Decisions

**Architecture Pattern:**
- Service layer separation: `inci_naming.py`, `label_generator.py`
- Follows existing patterns from `resources.py` and `oil.py`
- Reference data in JSON file (saponified-inci-terms.json)
- Pattern generation fallback for missing oils

**Constitution Compliance:**
- ✅ API-First: Pure API endpoint feature
- ✅ Research-Backed: Industry standard INCI nomenclature
- ✅ TDD: Mandatory with >90% coverage, property-based testing
- ✅ ACID: Read operations with proper transaction handling
- ✅ Performance: <100ms target (stricter than standard)
- ✅ Security: JWT authentication per existing patterns
- ✅ Deployment: Podman + Quadlet maintained
- ✅ Observability: Structured logging with Sentry

**Technical Stack:**
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async
- PostgreSQL 15+ with JSONB for oil metadata
- pytest, Hypothesis (property-based), httpx, pytest-cov
- Alembic for schema migrations

**Edge Cases Handled:**
- Castor Oil dual nomenclature (Castorate/Ricinoleate)
- Missing INCI names (fallback to common names)
- Trace ingredients (<1% still included)
- Mixed NaOH/KOH lye (both salts listed proportionally)
- Generic pattern generation for oils without reference data

## Metadata

- **Status:** Complete
- **Confidence:** High
- **Follow-up:** Ready for Phase 2 task breakdown (/speckit.tasks)
- **Files Created:**
  - specs/003-inci-label-generator/plan.md
  - specs/003-inci-label-generator/research.md
  - specs/003-inci-label-generator/data-model.md
  - specs/003-inci-label-generator/quickstart.md
  - specs/003-inci-label-generator/contracts/inci-label.yaml

**Next Steps:**
1. Run `/speckit.tasks` to generate task breakdown (tasks.md)
2. Execute implementation via `/speckit.implement` with TDD approach
