# Implementation Plan: Comprehensive Oils Database Import

**Branch**: `005-oils-database-import` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)

## Summary

Import 147 comprehensive oils from JSON to PostgreSQL, establishing **53% more coverage than leading competitors**. This is a FOUNDATIONAL feature blocking additive calculator (#006) and INCI generator (#008).

**Key Insight**: NO SCHEMA CHANGES NEEDED - existing Oil model already contains all required fields. This is purely a data import operation extending the proven `scripts/seed_database.py` pattern.

**Technical Approach**: TDD with pre-import validation, idempotent duplicate detection, and single-transaction ACID compliance.

---

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 15+
**Storage**: PostgreSQL with existing Oil model - NO MIGRATION REQUIRED
**Testing**: pytest with async support, property-based validation tests
**Target Platform**: Fedora Linux server (Podman/Quadlet deployment)
**Project Type**: Backend API (single project structure)

**Performance Goals**:
- Import <5 minutes for 147 oils (~2s per oil with validation)
- Database transaction ACID compliance
- Idempotent re-run capability

**Constraints**:
- 147 oils from 4117-line JSON file
- SAP value ranges: NaOH 0.100-0.300, KOH 0.140-0.420
- Fatty acids must sum to 95-100% (5% tolerance)
- Special cases: Pine Tar (zero fatty acids), Meadowfoam (C20/C22 approximation)

**Scale/Scope**:
- 1236% increase from current 11 seed oils to 158 total
- Complete fatty acid profiles (8 acids per oil)
- Complete quality metrics (7 metrics per oil)
- Partial INCI names (some oils have empty INCI)

---

## Constitution Check

**GATE: All checks must pass before implementation**

✅ **I. API-First Architecture**: PASS
- Import populates database for existing `/v1/oils` API endpoint
- No new API endpoints required
- OpenAPI docs automatically include new oils

✅ **II. Research-Backed Calculations**: PASS
- SAP values validated against ASTM D5558 ranges
- Fatty acid profiles validated for scientific completeness (95-100% sum)
- Quality metrics already research-backed in existing Oil model

✅ **III. Test-First Development**: PASS
- TDD approach: validation tests → implementation → integration tests
- Property-based testing for validation rules (Hypothesis)
- Idempotent re-run tests following `scripts/test_seed_idempotent.py` pattern
- Target: ≥90% code coverage (pytest-cov)

✅ **IV. Data Integrity & ACID Compliance**: PASS
- Single PostgreSQL transaction for all 147 oils (all-or-nothing)
- Automatic rollback on validation failure
- Idempotent duplicate detection (safe re-execution)
- No foreign key constraints needed (Oil is independent entity)

✅ **V. Performance Budgets**: PASS
- Target: <5 minutes for 147 oils
- Batch commit strategy (single transaction)
- Progress logging every 10 oils (not every oil)
- Connection pooling via existing async engine

✅ **VI. Security & Authentication**: N/A
- Internal script operation, no API authentication needed
- Database credentials from existing `app/core/config.py` settings

✅ **VII. Deployment Platform Standards**: PASS
- Script runs on Fedora server via Python 3.11
- No container changes needed
- Database connection via existing async engine

✅ **VIII. Observability & Monitoring**: PASS
- Structured progress logging with counts and summaries
- Error messages include specific oil name and validation failure reason
- Non-zero exit code on failure for CI/CD integration

**Constitution Compliance: 8/8 PASS** ✅

---

## Project Structure

### Documentation (this feature)

```text
specs/005-oils-database-import/
├── spec.md              # Feature specification (EXISTING)
├── plan.md              # This file (GENERATED)
├── data-model.md        # Phase 1: Data validation rules
├── quickstart.md        # Phase 1: Test scenarios and verification
├── contracts/
│   └── import-process.md    # Phase 1: Import algorithm and error handling
└── tasks.md             # Phase 2: Implementation tasks (/speckit.tasks command)
```

### Source Code (repository root)

```text
scripts/
├── import_oils_database.py      # NEW: Main import script
├── validate_oils_data.py         # NEW: Pre-import validation CLI
├── seed_database.py              # EXISTING: Pattern reference
└── test_seed_idempotent.py       # EXISTING: Idempotency test pattern

tests/
├── unit/
│   ├── test_oils_import.py       # NEW: Import logic unit tests
│   └── test_oils_validation.py   # NEW: Validation rules unit tests
└── integration/
    ├── test_oils_data_integrity.py  # NEW: Data integrity integration tests
    └── test_oils_import_idempotent.py  # NEW: Idempotency integration tests

working/user-feedback/oils-db-additions/
└── complete-oils-database.json   # EXISTING: Source data (147 oils, 4117 lines)

app/models/
└── oil.py                        # EXISTING: NO CHANGES NEEDED
```

**Structure Decision**: Single project backend structure. Import script extends existing `scripts/` pattern. Tests follow existing `tests/unit/` and `tests/integration/` organization.

---

## Complexity Tracking

**No Constitution Violations** - No complexity justification needed.

All requirements met within existing architecture:
- Single project structure (no multi-project complexity)
- Extends existing patterns (`scripts/seed_database.py`)
- No new dependencies required
- No architectural changes
- Simple data import operation with validation

---

## Implementation Phases

### Phase 0: Research (COMPLETE)

**Research Requirements**: SATISFIED - No additional research needed.

**Validation Ranges** (from ASTM D5558 and Kevin Dunn's "Scientific Soapmaking"):
- SAP NaOH: 0.100-0.300 g/g
- SAP KOH: 0.140-0.420 g/g (KOH factor ~1.403x NaOH)
- Fatty acids sum: 95-100% (5% tolerance for rounding and trace components)
- Iodine value: 0-200 typical range
- INS value: 0-350 typical range

**Special Cases Documented**:
1. **Pine Tar**: Zero fatty acids allowed (contains resin acids, not traditional fatty acids)
2. **Meadowfoam**: C20/C22 long-chain fatty acids approximated as oleic acid

**INCI Standards**: Empty INCI names acceptable per spec (not all oils have standardized INCI names).

### Phase 1: Design Artifacts

#### 1.1 Data Model (`data-model.md`)

**Entity: Oil** (existing model at `app/models/oil.py` - NO CHANGES):

```python
class Oil(Base):
    id: Mapped[str]                      # Primary key (e.g., "olive_oil")
    common_name: Mapped[str]              # Display name
    inci_name: Mapped[str]                # INCI cosmetic ingredient name (may be empty)
    sap_value_naoh: Mapped[float]         # NaOH saponification value (0.100-0.300)
    sap_value_koh: Mapped[float]          # KOH saponification value (0.140-0.420)
    iodine_value: Mapped[float]           # Unsaturation measure (0-200)
    ins_value: Mapped[float]              # Hardness indicator (0-350)
    fatty_acids: Mapped[dict]             # JSONB: 8 fatty acids (sum 95-100%)
    quality_contributions: Mapped[dict]   # JSONB: 7 quality metrics (0-99)
    created_at: Mapped[datetime]          # Auto timestamp
    updated_at: Mapped[datetime]          # Auto timestamp
```

**JSON Data Structure** (from `complete-oils-database.json`):

Maps 1:1 to Oil model - NO TRANSFORMATION NEEDED:

```json
{
  "oil_id": {
    "id": "oil_id",
    "common_name": "Oil Name",
    "inci_name": "",
    "sap_value_naoh": 0.135,
    "sap_value_koh": 0.190,
    "iodine_value": 81.0,
    "ins_value": 109.0,
    "fatty_acids": {
      "lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 4,
      "oleic": 71, "linoleic": 10, "linolenic": 1, "ricinoleic": 0
    },
    "quality_contributions": {
      "hardness": 17.0, "cleansing": 0.0, "conditioning": 82.0,
      "bubbly_lather": 0.0, "creamy_lather": 17.0,
      "longevity": 17.0, "stability": 82.0
    }
  }
}
```

**Validation Rules**:

```yaml
sap_value_naoh:
  range: [0.100, 0.300]
  error: "SAP NaOH {value} outside scientific range [0.100, 0.300]"

sap_value_koh:
  range: [0.140, 0.420]
  error: "SAP KOH {value} outside scientific range [0.140, 0.420]"

fatty_acids:
  required_keys: [lauric, myristic, palmitic, stearic, oleic, linoleic, linolenic, ricinoleic]
  sum_range: [95, 100]
  special_case_zero: ["pine_tar"]  # Allow zero sum for resin-based materials
  error: "Fatty acids sum {sum}% outside range [95, 100]%"

quality_contributions:
  required_keys: [hardness, cleansing, conditioning, bubbly_lather, creamy_lather, longevity, stability]
  value_range: [0, 99]
  error: "Quality metric {metric} value {value} outside range [0, 99]"
```

#### 1.2 Import Process Contract (`contracts/import-process.md`)

**Algorithm**:

1. **Load JSON**: `json.load()` → dict of 147 oils
2. **Validate All**: Check all oils before database operations (fail fast)
3. **Database Transaction**:
   - For each oil: Check existence → Skip if exists, Insert if new
   - Single commit for all oils (ACID compliance)
4. **Progress Logging**: Report every 10 oils
5. **Summary**: Report added/skipped counts and import time

**Validation Function**:

```python
def validate_oil_data(oil_id: str, oil_data: dict) -> Tuple[bool, str]:
    """
    Validate oil data against scientific ranges and completeness rules.
    Returns: (is_valid, error_message)
    """
    # SAP ranges, fatty acid sum, quality metrics, required fields
    # Special case: pine_tar can have zero fatty acids
    # Returns (True, "Valid") or (False, "Specific error message")
```

**Duplicate Detection**:

```python
async def is_oil_exists(session: AsyncSession, oil_id: str) -> bool:
    """Check if oil already exists via SELECT query"""
    result = await session.execute(select(Oil).where(Oil.id == oil_id))
    return result.scalar_one_or_none() is not None
```

**Error Handling**:

- **JSON Parse Error**: Abort import, exit code 1
- **Validation Error**: Log all failures, abort import, exit code 1
- **Database Error**: Rollback transaction, exit code 2

#### 1.3 Quickstart (`quickstart.md`)

**Test Scenario 1: Import All 147 Oils**

```bash
python scripts/import_oils_database.py

# Expected: 147 oils added, 0 skipped, <5 minutes runtime
# Verification: SELECT COUNT(*) FROM oils; → 158 (11 existing + 147 new)
```

**Test Scenario 2: Re-Import Idempotently**

```bash
python scripts/import_oils_database.py  # Run again

# Expected: 0 oils added, 147 skipped, faster runtime (~1 minute)
# Verification: Still 158 oils, no duplicates
```

**Test Scenario 3: Validation Catches Bad Data**

```bash
python scripts/validate_oils_data.py /tmp/test_invalid_oils.json

# Expected: Validation errors logged, exit code 1
```

### Phase 2: TDD Implementation

**RED Phase**: Write failing tests

```python
# tests/unit/test_oils_validation.py
def test_validate_sap_naoh_range():
    """SAP NaOH must be in [0.100, 0.300]"""
    # Test valid and invalid SAP values

def test_validate_fatty_acids_sum():
    """Fatty acids must sum to 95-100%"""
    # Test valid sum (99%), invalid sum (80%)

def test_pine_tar_special_case():
    """Pine Tar can have zero fatty acids"""
    # Test special case handling

# tests/unit/test_oils_import.py
async def test_load_json_data():
    """Load and parse 147 oils from JSON"""

async def test_duplicate_detection():
    """Skip oils that already exist"""
```

**GREEN Phase**: Implement to pass tests

```python
# scripts/import_oils_database.py
def load_oils_from_json(json_path: str) -> Dict[str, dict]:
    """Load oils from JSON with error handling"""

def validate_oil_data(oil_id: str, oil_data: dict) -> Tuple[bool, str]:
    """Validate against scientific ranges"""

async def import_oils_database(json_path: str, dry_run: bool = False):
    """Main import function with transaction safety"""
```

**REFACTOR Phase**: Integration tests

```python
# tests/integration/test_oils_import_idempotent.py
async def test_import_idempotency():
    """Run import twice, verify no duplicates"""

async def test_partial_import():
    """Delete some oils, re-import, verify restoration"""

# tests/integration/test_oils_data_integrity.py
async def test_sap_values_in_range():
    """Query database, verify all SAP values valid"""

async def test_fatty_acids_completeness():
    """Verify all oils have 95-100% fatty acid sum"""

async def test_special_cases():
    """Verify Pine Tar and Meadowfoam handled correctly"""
```

### Phase 3: Verification

**Quality Gates**:

1. **All Tests Pass**: `pytest tests/unit/ tests/integration/ -v`
2. **Coverage ≥90%**: `pytest --cov=scripts/import_oils_database --cov-report=term-missing`
3. **Import Execution**: `python scripts/import_oils_database.py` (success)
4. **Database Verification**: Manual SQL queries confirm data integrity
5. **API Verification**: `curl http://localhost:8000/v1/oils | jq '. | length'` → 158

---

## Performance Budget

**Target**: <5 minutes for 147 oils

**Strategy**:
- Batch commit (single transaction for all oils)
- Progress logging every 10 oils (not every oil)
- Connection pooling via existing async engine
- Validation before database operations (fail fast)

**Expected**: ~2-3 minutes actual (well under budget)

---

## Risk Assessment

**Risk Level**: LOW ✅

**Mitigations**:
1. **Data Quality**: Pre-import validation catches all issues before database commit
2. **Idempotency**: Duplicate detection prevents data corruption on re-run
3. **Transaction Safety**: Single PostgreSQL transaction with automatic rollback
4. **Performance**: 147 oils well within 5-minute target
5. **Backward Compatibility**: No schema changes, existing API unchanged

**Rollback Plan**:
- Import failure: Transaction automatically rolls back
- Bad data: Delete imported oils by created_at timestamp filter
- Migration issues: N/A - no migration required

---

## Next Steps

**Phase 1 Deliverables** (ready for `/speckit.tasks`):
- ✅ Technical Context documented
- ✅ Constitution Check passed (8/8)
- ✅ Research requirements satisfied
- ✅ Data Model documented
- ✅ Import Process Contract documented
- ✅ Quickstart scenarios documented

**Generate Tasks**: Execute `/speckit.tasks` to create `tasks.md` with dependency-ordered implementation tasks.

**Estimated Time**:
- Phase 1 (Design Artifacts): 2-3 hours
- Phase 2 (TDD Implementation): 6-8 hours
- Testing & Verification: 2-3 hours
- **Total**: 10-14 hours

**Priority**: CRITICAL (blocks features #006 and #008)

---

**Plan Generated**: 2025-11-05
**Ready for Task Generation**: YES ✅
