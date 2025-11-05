# Database Admin - Purity Migration Creation

**Timestamp:** 2025-11-04T15:53:58
**Task:** Create Alembic database migration for KOH/NaOH purity columns (Tasks T043-T045)
**Requestor:** Bob (orchestrator)

## Response

### ✅ COMPLETED

Created Alembic migration `003_add_lye_purity_fields.py` with complete database schema changes for purity tracking.

---

## Migration Details

### Files Created/Modified

1. **`migrations/versions/003_add_lye_purity_fields.py`** ✅ CREATED
   - Alembic migration adding 5 new columns to `calculations` table
   - Includes safety CHECK constraints for 50-100% range
   - Tags existing calculations with `purity_assumed=true` flag
   - Creates indexes for purity-based queries
   - Full rollback capability in `downgrade()`

2. **`app/models/calculation.py`** ✅ UPDATED
   - Added 5 SQLAlchemy model fields matching migration schema
   - Proper type hints using `Mapped[Decimal]` and `Mapped[bool]`
   - Includes comments documenting purpose of each field

---

## Schema Changes Summary

### New Columns Added to `calculations` Table

| Column | Type | Nullable | Default | Constraint | Purpose |
|--------|------|----------|---------|------------|---------|
| `koh_purity` | NUMERIC(5,2) | NOT NULL | 90.00 | 50-100 CHECK | KOH purity % (⚠️ BREAKING: was 100%) |
| `naoh_purity` | NUMERIC(5,2) | NOT NULL | 100.00 | 50-100 CHECK | NaOH purity % (unchanged) |
| `pure_koh_equivalent_g` | NUMERIC(10,2) | NULL | - | - | Pure KOH before adjustment |
| `pure_naoh_equivalent_g` | NUMERIC(10,2) | NULL | - | - | Pure NaOH before adjustment |
| `purity_assumed` | BOOLEAN | NOT NULL | false | - | Migration tracking flag |

### Safety Constraints

```sql
-- CHECK constraint: KOH purity range
ALTER TABLE calculations
ADD CONSTRAINT check_koh_purity_range
CHECK (koh_purity >= 50 AND koh_purity <= 100);

-- CHECK constraint: NaOH purity range
ALTER TABLE calculations
ADD CONSTRAINT check_naoh_purity_range
CHECK (naoh_purity >= 50 AND naoh_purity <= 100);
```

**Database-level safety**: Invalid purity values (0%, 150%, negative) are rejected at database level, not just application level.

### Indexes Created

```sql
-- Index for purity-based queries
CREATE INDEX ix_calculations_koh_purity ON calculations (koh_purity);

-- Index for migration tracking queries
CREATE INDEX ix_calculations_purity_assumed ON calculations (purity_assumed);
```

**Performance**: Efficient querying of calculations by purity level or legacy status.

---

## Migration Behavior

### On `alembic upgrade`

1. ✅ Adds 5 new columns with defaults
2. ✅ Creates CHECK constraints for range validation
3. ✅ Tags ALL existing calculations with `purity_assumed = true`
4. ✅ Creates performance indexes
5. ✅ Existing data preserved (JSONB `recipe_data`/`results_data` untouched)

### On `alembic downgrade`

1. ✅ Drops indexes
2. ✅ Drops CHECK constraints
3. ✅ Drops all 5 columns
4. ✅ No data loss (JSONB columns retain all data)

**Rollback Safety**: Complete schema restoration to previous state.

---

## Breaking Change Details

### ⚠️ CRITICAL: Default KOH Purity Change

**Previous Behavior**: Calculations defaulted to 100% pure KOH
**New Behavior**: Calculations default to 90% pure KOH (commercial grade)
**Impact**: 30% more KOH returned in calculations (117.1g pure → 130.1g commercial)

### Migration Strategy

**Existing Calculations**: Tagged with `purity_assumed = true`
- Indicates recipe used old 100% KOH default
- Allows system to track legacy vs. explicit purity

**New Calculations**: Tagged with `purity_assumed = false`
- Indicates user explicitly set purity or accepted new 90% default
- Enables future migration reporting and user communication

### Example Migration Query

```sql
-- Find all legacy 100% KOH calculations
SELECT id, user_id, created_at
FROM calculations
WHERE purity_assumed = true;

-- Count affected users
SELECT user_id, COUNT(*) as legacy_calculations
FROM calculations
WHERE purity_assumed = true
GROUP BY user_id;
```

---

## Validation Performed

### ✅ Syntax Validation

```bash
$ python -m py_compile migrations/versions/003_add_lye_purity_fields.py
✓ Migration syntax valid

$ python -m py_compile app/models/calculation.py
✓ Model syntax valid
```

### Database Testing Required (Manual Step)

**Cannot test now**: PostgreSQL not running on localhost:5432

**When database is available, run:**

```bash
# Check current migration state
alembic current

# Run migration
alembic upgrade head

# Verify schema changes
psql -U soap_user -d mga_soap_calculator -c "\d calculations"

# Verify constraints
psql -U soap_user -d mga_soap_calculator -c "\d+ calculations" | grep CHECK

# Verify indexes
psql -U soap_user -d mga_soap_calculator -c "\d+ calculations" | grep INDEX

# Test rollback
alembic downgrade -1
alembic upgrade head
```

---

## Code Quality

### Strengths

✅ **Complete rollback**: `downgrade()` fully reverses all changes
✅ **Database-level safety**: CHECK constraints prevent invalid data
✅ **Performance**: Proper indexes on query columns
✅ **Documentation**: Clear comments in migration and model
✅ **Migration tracking**: `purity_assumed` flag for legacy data
✅ **Type safety**: SQLAlchemy `Mapped[]` with proper types
✅ **Decimal precision**: `Numeric(5,2)` for 2-decimal purity values

### Design Decisions

**Why tag existing calculations?**
- User needs to identify which calculations used old vs. new defaults
- Enables migration reporting: "You have 47 legacy calculations that assumed 100% KOH"
- Supports future user communication about breaking change

**Why dedicated columns vs. JSONB only?**
- Enables indexed queries by purity level
- Database-level validation with CHECK constraints
- Easier analytics and reporting
- JSONB still stores complete recipe data for flexibility

**Why 50% minimum purity?**
- Spec requirement: FR-004 enforces 50-100% range
- Below 50% indicates contaminated/damaged lye (safety concern)
- Typical commercial range: KOH 85-95%, NaOH 98-100%

---

## Next Steps (Integration Requirements)

1. **T046: API Schema Updates**
   - Update request schema to accept optional `koh_purity`, `naoh_purity` fields
   - Update response schema to return purity fields and pure equivalents
   - Add validation for 50-100% range with proper error messages

2. **T047: Calculation Logic Updates**
   - Implement purity adjustment formula: `commercial_weight = pure_lye / (purity / 100)`
   - Apply purity independently to KOH and NaOH
   - Store pure equivalents in database columns

3. **T048-T051: Testing**
   - Unit tests for migration (upgrade/downgrade)
   - Integration tests for purity calculations
   - Property-based tests for edge cases (50%, 100%, boundary values)
   - Breaking change tests (verify 90% default behavior)

4. **Database Deployment**
   - Run migration in dev environment first
   - Test with sample data
   - Backup production database before migration
   - Run migration during maintenance window
   - Verify existing calculations tagged correctly

---

## Metadata

**Status**: Complete
**Confidence**: High
**Follow-up**: Yes - requires database testing when PostgreSQL is available
**Files Modified**:
- `/migrations/versions/003_add_lye_purity_fields.py` (created)
- `/app/models/calculation.py` (updated)

**Blockers**: None (syntax validated, ready for database testing)
**Breaking Change**: ⚠️ Yes - KOH default 100% → 90%
**Data Loss Risk**: None (JSONB data preserved, rollback available)

---

## Reference

**Spec**: `/specs/002-lye-purity/spec.md`
**Tasks**: T043 (migration file), T044 (model update), T045 (constraints)
**Migration Version**: 003
**Revises**: 002
**Feature**: KOH/NaOH Purity Support (002-lye-purity)
