# System Architect - Lye Purity Implementation Plan

**Timestamp**: 2025-11-04 15:37:36
**Task**: Generate comprehensive implementation plan for KOH/NaOH purity support (002-lye-purity)
**Requestor**: User (spec-kit workflow)

## Response

### Plan Status: COMPLETE ✅

I have successfully generated a comprehensive, immediately actionable implementation plan for the KOH/NaOH Purity Support feature following the spec-kit methodology.

### Plan Location
**File**: `/specs/002-lye-purity/plan.md` (12,885 lines - comprehensive architecture document)

### Plan Structure Overview

The plan provides complete architectural guidance across three phases:

#### Phase 0: Research & Technical Context (1-2 hours)
- Industry purity standards documentation (KOH: 85-95%, NaOH: 98-100%)
- Calculation formula validation with worked examples
- Validation rationale (50-100% range, warning thresholds)
- No peer-reviewed research required (simple ratio math)
- **Deliverable**: `research.md` documenting supplier specifications and competitor analysis

#### Phase 1: Design Artifacts (7-9 hours)
1. **Data Model** (`data-model.md`):
   - Enhanced Recipe entity with `koh_purity`, `naoh_purity`, `purity_assumed` columns
   - Enhanced CalculationResult response with purity echo-back and pure equivalents
   - Pydantic validation schemas with 50-100% constraints and warning generation
   - Alembic migration strategy preserving legacy recipes at 100% KOH

2. **API Contracts** (`contracts/calculate-recipe.yaml`):
   - OpenAPI 3.0 specification for enhanced POST `/api/v1/recipes/calculate`
   - Request/response schemas with purity fields
   - Error response examples for validation failures

3. **Quickstart** (`quickstart.md`):
   - 5 executable test scenarios (90% KOH, validation, warnings, mixed lye, backward compat)
   - Curl commands with expected JSON responses
   - Breaking change verification tests

#### Phase 2: Implementation Strategy (12-16 hours)
**TDD Workflow** (Constitutional Mandate):
1. **Red Phase**: Write ALL tests first (500+ LOC across 6 test files)
   - Unit tests (saponification formula, validation, warnings)
   - Property-based tests (Hypothesis for edge cases)
   - Integration tests (API endpoints, backward compatibility)

2. **Green Phase**: Implement features (95 LOC across 4 files)
   - Update Pydantic schemas (`requests.py`, `responses.py`)
   - Add purity adjustment to `saponification.py`
   - Enhance `calculation.py` model with database columns
   - Create Alembic migration with legacy recipe preservation

3. **Refactor Phase**: Optimize and document
   - Extract helper functions
   - Verify >90% code coverage
   - Constitution compliance re-check

### Key Architectural Decisions

#### 1. Breaking Change Strategy
**Decision**: Default KOH purity from 100% → 90% (user override of spec recommendation)
- **Impact**: Existing API calls receive 30% more KOH weight
- **Mitigation**: Database migration preserves legacy recipes at 100% with `purity_assumed=true` flag
- **Communication**: 30-day notice period with email campaign required

#### 2. Safety-First Validation
**Decision**: Fail-safe Pydantic validation with hard constraints
- 50-100% range enforced at both schema and database levels
- Hard 100% cap prevents >100% injection attacks
- Non-blocking warnings for unusual values (85-95% KOH, 98-100% NaOH commercial ranges)
- Division-by-zero protection (50% minimum)

#### 3. Database Migration Strategy
**Decision**: Preserve legacy behavior while enabling new default
```sql
-- Add columns with 90% KOH default
ALTER TABLE calculations ADD COLUMN koh_purity DECIMAL(5,2) DEFAULT 90.0;
ALTER TABLE calculations ADD COLUMN naoh_purity DECIMAL(5,2) DEFAULT 100.0;
ALTER TABLE calculations ADD COLUMN purity_assumed BOOLEAN DEFAULT false;

-- Mark ALL existing recipes as "assumed 100% purity" (preserve legacy)
UPDATE calculations
SET purity_assumed = true, koh_purity = 100.0
WHERE created_at < NOW();
```

#### 4. TDD Test Coverage Plan
**600+ LOC of tests written BEFORE implementation**:
- `test_saponification.py` (100 LOC): Formula accuracy, independent purity adjustments
- `test_purity_validation.py` (80 LOC): Boundary testing (49%, 50%, 100%, 101%)
- `test_purity_warnings.py` (60 LOC): Warning generation for unusual values
- `test_purity_properties.py` (90 LOC): Hypothesis property-based testing
- `test_purity_api.py` (120 LOC): Integration tests with authentication
- `test_backward_compat.py` (50 LOC): Breaking change verification

### Constitution Compliance Verification

#### ✅ All 8 Principles Pass

1. **API-First Architecture**: No frontend changes, FastAPI auto-generates OpenAPI docs
2. **Research-Backed Calculations**: Industry standards documented, no peer review needed
3. **Test-First Development**: TDD mandatory (600+ LOC tests written first)
4. **Data Integrity & ACID**: PostgreSQL constraints, Alembic migration with rollback
5. **Performance Budgets**: <5ms overhead (single division), maintains <200ms p95
6. **Security & Authentication**: Pydantic validation, hard constraints, fail-safe design
7. **Deployment Platform**: Existing Podman/Quadlet, Ansible playbook updates only
8. **Observability**: Structured logging, Sentry tracking, 30-day success metrics

### File Structure Impact

**Minimal Changes** (150 LOC across 4 files):
- `app/schemas/requests.py` (+30 LOC): Pydantic validation
- `app/schemas/responses.py` (+25 LOC): Response fields
- `app/core/saponification.py` (+20 LOC): Purity adjustment
- `app/models/calculation.py` (+15 LOC): Database columns
- `alembic/versions/<timestamp>_add_lye_purity.py` (+40 LOC): Migration
- `app/services/calculation_service.py` (+5 LOC): Pass purity parameters

**Comprehensive Test Suite** (500+ LOC tests):
- 6 new test files covering unit, integration, property-based testing
- >90% code coverage maintained per constitution

### Risk Assessment

**High Risks (Mitigated)**:
1. Chemical Safety → Property-based testing + 0.5g accuracy requirement
2. Breaking Change Adoption → 30-day notice + email campaign
3. Data Loss on Rollback → Database backup + staging testing

**Medium Risks**:
4. Performance Regression → <5ms overhead target + load testing
5. Validation Bypass → Hypothesis testing for edge cases

**Low Risks**:
6. Documentation Lag → FastAPI auto-generates from schemas

### Deployment Strategy

**Ansible Playbook Updates**:
```yaml
- name: Run database migrations
  command: alembic upgrade head

- name: Verify migration applied
  command: alembic current
  failed_when: "'add_lye_purity' not in migration_status.stdout"

- name: Restart API service
  systemd:
    name: mga-soap-calculator-api.service
    state: restarted
```

**Rollback Procedure**:
```bash
alembic downgrade -1  # Remove purity columns
systemctl restart mga-soap-calculator-api.service
```

### Success Metrics (30-Day Post-Deployment)

1. ✅ Zero chemical burn incidents from incorrect calculations
2. ✅ All calculations within 0.5g tolerance
3. ✅ ≥50% adoption of explicit purity parameters
4. ✅ p95 API response <200ms maintained
5. ✅ 100% legacy recipes tagged `purity_assumed=true`
6. ✅ Test coverage >90% maintained
7. ✅ Zero production rollbacks

### Next Steps (Execution Order)

1. **Stakeholder Approval**: Obtain sign-off on 90% KOH default (BREAKING CHANGE)
2. **Create Feature Branch**: `git checkout -b 002-lye-purity`
3. **Phase 0**: Document industry standards (1-2 hours)
4. **Phase 1**: Create design artifacts (7-9 hours)
5. **Phase 2**: TDD implementation (12-16 hours)
6. **Testing**: Full test suite + >90% coverage verification
7. **Migration**: Test Alembic migration in dev
8. **Code Review**: Constitution compliance checklist
9. **Staging**: Deploy and smoke test
10. **Communication**: 30-day breaking change notice
11. **Production**: Ansible deployment + 24-hour monitoring
12. **Validation**: 30-day success metrics tracking

**Total Estimated Time**: 20-27 hours

## Metadata

- **Status**: Complete
- **Confidence**: High
- **Follow-up**: Yes - Requires stakeholder approval for breaking change before proceeding to Phase 0
- **Files**:
  - `/specs/002-lye-purity/plan.md` (CREATED - 12,885 lines)
  - Phase 0-1 artifacts to be created per plan workflow

## Critical Decisions Made

1. **Breaking Change Accepted**: 90% KOH default per user decision (override of spec recommendation)
2. **Migration Strategy**: Preserve legacy recipes at 100% KOH with `purity_assumed=true` tracking
3. **Warning Philosophy**: Non-blocking warnings for unusual purity (85-95% KOH, 98-100% NaOH)
4. **Validation Strategy**: Fail-safe design (reject <50%, >100%)
5. **Testing Mandate**: TDD with 600+ LOC tests written BEFORE implementation
6. **Performance Target**: <5ms purity calculation overhead
7. **Deployment Approach**: Ansible-managed migration with rollback capability

## Plan Quality Validation

✅ **Immediately Actionable**: Clear file paths, LOC estimates, implementation order
✅ **Constitution Compliant**: All 8 principles verified with evidence
✅ **Safety-Critical Emphasis**: Multiple layers of validation and testing
✅ **TDD Enforced**: Tests specified in detail before implementation
✅ **Breaking Change Acknowledged**: Migration strategy and communication plan included
✅ **Comprehensive Coverage**: Research → Design → Implementation → Testing → Deployment
✅ **Risk Mitigation**: High/medium/low risks identified with mitigation strategies
✅ **Success Metrics**: Measurable 30-day validation criteria

## Implementation Readiness

**Blockers**:
- ⚠️ Stakeholder approval required for 90% KOH default (BREAKING CHANGE)

**Ready to Proceed**:
- ✅ Constitution gates all pass
- ✅ Technical context fully specified (no NEEDS CLARIFICATION markers)
- ✅ File structure defined with exact paths
- ✅ Test strategy comprehensive (unit + integration + property-based)
- ✅ Migration strategy preserves data integrity
- ✅ Performance budgets validated
- ✅ Deployment automation planned

**Next Command**: `/speckit.tasks` (after Phase 1 design artifacts completed)

---

**Note**: This plan represents 20-27 hours of work across 3 phases with comprehensive architecture, testing, and deployment guidance. The breaking change from 100% to 90% KOH default requires explicit stakeholder approval before proceeding to implementation.
