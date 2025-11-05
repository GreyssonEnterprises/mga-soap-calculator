# Testing Migration 003: Purity Fields

## Prerequisites

1. PostgreSQL running on localhost:5432
2. Database `mga_soap_calculator` exists
3. User `soap_user` with password `soap_password` configured
4. Virtual environment activated

## Test Procedure

### 1. Check Current State

```bash
# Activate virtual environment
source .venv/bin/activate

# Check current migration
alembic current
# Expected: 002 (from add_triggers_and_constraints)

# Check table structure BEFORE migration
psql -U soap_user -d mga_soap_calculator -c "\d calculations"
```

### 2. Run Migration

```bash
# Run upgrade
alembic upgrade head

# Verify migration applied
alembic current
# Expected: 003 (add_lye_purity_fields)
```

### 3. Verify Schema Changes

```bash
# Check new columns exist
psql -U soap_user -d mga_soap_calculator -c "\d calculations" | grep purity

# Expected output:
# koh_purity              | numeric(5,2)           | not null | 90.00
# naoh_purity             | numeric(5,2)           | not null | 100.00
# pure_koh_equivalent_g   | numeric(10,2)          |          |
# pure_naoh_equivalent_g  | numeric(10,2)          |          |
# purity_assumed          | boolean                | not null | false
```

### 4. Verify CHECK Constraints

```bash
# List CHECK constraints
psql -U soap_user -d mga_soap_calculator -c "
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'calculations'::regclass
AND contype = 'c';
"

# Expected output includes:
# check_koh_purity_range  | CHECK (koh_purity >= 50 AND koh_purity <= 100)
# check_naoh_purity_range | CHECK (naoh_purity >= 50 AND naoh_purity <= 100)
```

### 5. Verify Indexes

```bash
# List indexes on purity columns
psql -U soap_user -d mga_soap_calculator -c "
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'calculations'
AND indexname LIKE '%purity%';
"

# Expected output:
# ix_calculations_koh_purity         | CREATE INDEX ... ON calculations USING btree (koh_purity)
# ix_calculations_purity_assumed     | CREATE INDEX ... ON calculations USING btree (purity_assumed)
```

### 6. Test Constraint Enforcement

```bash
# Test: Insert with valid purity (should succeed)
psql -U soap_user -d mga_soap_calculator -c "
INSERT INTO calculations (id, user_id, recipe_data, results_data, koh_purity, naoh_purity)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM users LIMIT 1),
  '{}'::jsonb,
  '{}'::jsonb,
  90.00,
  100.00
);
"
# Expected: INSERT 0 1

# Test: Insert with invalid KOH purity (should fail)
psql -U soap_user -d mga_soap_calculator -c "
INSERT INTO calculations (id, user_id, recipe_data, results_data, koh_purity, naoh_purity)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM users LIMIT 1),
  '{}'::jsonb,
  '{}'::jsonb,
  49.99,
  100.00
);
"
# Expected: ERROR: check constraint "check_koh_purity_range" is violated

# Test: Insert with invalid NaOH purity (should fail)
psql -U soap_user -d mga_soap_calculator -c "
INSERT INTO calculations (id, user_id, recipe_data, results_data, koh_purity, naoh_purity)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM users LIMIT 1),
  '{}'::jsonb,
  '{}'::jsonb,
  90.00,
  101.00
);
"
# Expected: ERROR: check constraint "check_naoh_purity_range" is violated
```

### 7. Test Migration Tagging

```bash
# Check if existing calculations were tagged
psql -U soap_user -d mga_soap_calculator -c "
SELECT id, created_at, purity_assumed
FROM calculations
ORDER BY created_at
LIMIT 5;
"
# Expected: All existing calculations should have purity_assumed = true

# Insert new calculation (should get purity_assumed = false by default)
psql -U soap_user -d mga_soap_calculator -c "
INSERT INTO calculations (id, user_id, recipe_data, results_data)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM users LIMIT 1),
  '{}'::jsonb,
  '{}'::jsonb
)
RETURNING id, purity_assumed;
"
# Expected: purity_assumed = false
```

### 8. Test Rollback

```bash
# Downgrade to previous version
alembic downgrade -1

# Verify columns removed
psql -U soap_user -d mga_soap_calculator -c "\d calculations" | grep purity
# Expected: No output (columns should be gone)

# Verify constraints removed
psql -U soap_user -d mga_soap_calculator -c "
SELECT conname
FROM pg_constraint
WHERE conrelid = 'calculations'::regclass
AND conname LIKE '%purity%';
"
# Expected: No rows returned

# Re-apply migration
alembic upgrade head

# Verify everything back
psql -U soap_user -d mga_soap_calculator -c "\d calculations" | grep purity
# Expected: All 5 columns back
```

## Expected Results Summary

✅ Migration applies without errors
✅ 5 new columns added with correct types and defaults
✅ CHECK constraints enforce 50-100% range
✅ Indexes created on koh_purity and purity_assumed
✅ Existing calculations tagged with purity_assumed=true
✅ Invalid purity values rejected by database
✅ Rollback removes all changes cleanly
✅ Re-apply restores all schema changes

## Troubleshooting

### "Connection refused" error
- PostgreSQL not running: `pg_ctl start` or `systemctl start postgresql`
- Wrong host/port: Check .env DATABASE_URL
- Firewall blocking: Check firewall rules

### "relation 'calculations' does not exist"
- Initial schema not applied: Run `alembic upgrade 001`
- Wrong database: Check `psql -l` for database list

### "no such revision '002'"
- Missing previous migration: Apply migrations in order (001 → 002 → 003)

### CHECK constraint violations
- This is expected behavior! Constraints are working correctly
- Only valid purity values (50-100%) should be accepted

## Cleanup (Optional)

```bash
# Remove test calculations
psql -U soap_user -d mga_soap_calculator -c "
DELETE FROM calculations
WHERE recipe_data = '{}'::jsonb;
"
```

## Success Criteria

Migration is considered successful when:
- [x] All 5 columns exist with correct types
- [x] Default values applied (90.00 for KOH, 100.00 for NaOH)
- [x] CHECK constraints enforce 50-100% range
- [x] Indexes created and functional
- [x] Existing data tagged with purity_assumed=true
- [x] Invalid values rejected at database level
- [x] Rollback works cleanly
- [x] Re-apply succeeds without errors
