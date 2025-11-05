# MGA Soap Calculator - Deployment Guide

**Version**: 1.2.0 (Auto-Seed)
**Last Updated**: 2025-11-04

---

## Quick Start

### Local Development

```bash
# Start with fresh database
podman-compose down -v
podman-compose up

# Watch auto-seed process in logs
# Expected: [3/4] Checking for seed data... → Database is empty → Loading seed data
```

### Production Deployment

```bash
# Deploy via Ansible (recommended)
cd ansible
ansible-playbook playbooks/build-and-deploy.yml \
    --extra-vars "app_version=1.2.0" \
    --vault-password-file ~/.config/pai/secrets/ansible_vault_pw

# Manual deployment
podman build -t mga-soap-calculator:v1.2.0 .
podman stop mga-soap-calculator
podman rm mga-soap-calculator
podman run -d \
    --name mga-soap-calculator \
    -p 8000:8000 \
    --env-file .env.production \
    mga-soap-calculator:v1.2.0
```

---

## Auto-Seed Behavior

### Container Startup Sequence

1. **Database Readiness** (30 retries, 60s total)
   - Waits for PostgreSQL with `pg_isready`
   - Exits if database unavailable

2. **Database Migrations** (idempotent)
   - Runs `alembic upgrade head`
   - Exits on migration failure

3. **Seed Data Check** (query-based)
   - Counts existing oils and additives
   - Seeds if either count is zero
   - Skips if data exists

4. **Application Start**
   - Starts uvicorn with 4 workers
   - Ready for requests

### Seed Decision Logic

```
COUNT(oils) == 0 OR COUNT(additives) == 0?
├─ YES → Load seed data (11 oils, 14 additives)
└─ NO  → Skip seed (data already present)
```

**Idempotent**: Safe to restart container without creating duplicates.

---

## Common Operations

### Force Re-Seed

```bash
# Option 1: Fresh database (destroys all data)
podman-compose down -v  # Remove volume
podman-compose up       # Auto-seeds on startup

# Option 2: Delete seed data only (keeps calculations)
podman exec -it mga-postgresql psql -U soap_user -d soap_calculator
DELETE FROM additives;
DELETE FROM oils;
\q

podman restart mga-soap-calculator  # Auto-seeds missing data
```

### Manual Seed (Legacy)

```bash
# No longer required, but still works
podman exec -it mga-soap-calculator python scripts/seed_database.py

# Output:
# 📦 Processing 11 oils...
#   ⏭ Olive Oil (already exists)
#   ⏭ Coconut Oil (already exists)
#   ...
# ✓ No new data to add
```

### Verify Seed Data

```bash
# Via API
curl http://localhost:8000/api/v1/oils | jq '. | length'
# Expected: 11

curl http://localhost:8000/api/v1/additives | jq '. | length'
# Expected: 14

# Via Database
podman exec -it mga-postgresql psql -U soap_user -d soap_calculator -c "SELECT COUNT(*) FROM oils;"
# Expected: 11
```

---

## Troubleshooting

### Container Exits Immediately

**Symptom**: `podman ps` shows no running container

**Check Logs**:
```bash
podman logs mga-soap-calculator
```

**Common Causes**:

1. **Database Not Ready**
   ```
   ✗ Database not ready after 30 attempts
   ```
   - **Fix**: Verify PostgreSQL is running
   - **Fix**: Check DATABASE_URL in .env

2. **Migration Failure**
   ```
   ✗ Migration failed
   ```
   - **Fix**: Check database permissions
   - **Fix**: Verify migrations/versions/ directory

3. **Seed Failure**
   ```
   ✗ Seed data loading failed
   ```
   - **Fix**: Check database schema (migrations applied?)
   - **Fix**: Verify scripts/seed_data.py is valid

### Slow Startup

**Symptom**: Container takes 30+ seconds to become ready

**Check Logs**:
```bash
podman logs mga-soap-calculator | grep -A5 "Waiting for database"
```

**Likely Cause**: Database connection issues
- Network latency
- PostgreSQL not responding
- DNS resolution delay

**Fix**:
```bash
# Use IP instead of hostname
DATABASE_URL=postgresql+asyncpg://soap_user:password@192.168.1.100:5432/soap_calculator

# Or verify network
podman network inspect mga-network
```

### Data Missing After Restart

**Symptom**: GET /api/v1/oils returns empty array

**Check Volume**:
```bash
podman volume ls | grep postgres
# Expected: mga-postgresql-data

# Verify volume mounted
podman inspect mga-postgresql | jq '.[0].Mounts'
```

**Fix**: Ensure volume in podman-compose.yml:
```yaml
volumes:
  postgresql-data:
    driver: local
```

---

## Version History

### v1.2.0 (2025-11-04) - Auto-Seed

**New**:
- Automatic database seeding on container startup
- Intelligent seed detection (query-based)
- Idempotent seed operations
- Database readiness checking

**Changes**:
- Added `scripts/docker-entrypoint.sh`
- Enhanced `scripts/seed_database.py` with duplicate detection
- Dockerfile uses ENTRYPOINT instead of CMD

**Migration**:
- No breaking changes
- Drop-in replacement for v1.0.0

### v1.0.0 (2025-11-01) - Initial Release

**Features**:
- Core calculation API
- JWT authentication
- Manual seed script

---

## Configuration

### Environment Variables

**Required**:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
SECRET_KEY=your-secret-key-here
```

**Optional**:
```bash
ENVIRONMENT=production
APP_VERSION=1.2.0
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
```

**Future** (not yet implemented):
```bash
SKIP_AUTO_SEED=false      # Disable auto-seed
SEED_TIMEOUT=60           # Seed operation timeout
DB_READY_RETRIES=30       # Database readiness retries
```

---

## Health Checks

### Container Health

```bash
# Docker/Podman health check
podman inspect mga-soap-calculator | jq '.[0].State.Health'

# Expected:
# {
#   "Status": "healthy",
#   "FailingStreak": 0,
#   "Log": [...]
# }
```

### API Health Endpoint

```bash
curl http://localhost:8000/api/v1/health

# Expected:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "environment": "production"
# }
```

### Seed Data Verification

```bash
# Quick check
curl http://localhost:8000/api/v1/oils | jq '. | length'  # Should be 11
curl http://localhost:8000/api/v1/additives | jq '. | length'  # Should be 14

# Detailed check
curl http://localhost:8000/api/v1/oils | jq '.[0]'
# Expected: Olive Oil with complete profile
```

---

## Monitoring

### Key Metrics

**Startup Time**:
- Fresh database: ~4-8 seconds
- Existing data: ~3-7 seconds

**Seed Operation**:
- Fresh: ~500ms (25 records)
- Skip: ~50ms (count query)

**Health Check**:
- Interval: 30 seconds
- Timeout: 10 seconds
- Start period: 15 seconds

### Log Monitoring

**Successful Startup**:
```
[1/4] Waiting for PostgreSQL database...
✓ Database is ready
[2/4] Running database migrations...
✓ Migrations applied successfully
[3/4] Checking for seed data...
✓ Seed data already present (oils=11,additives=14)
  Skipping seed to prevent duplicates
[4/4] Starting MGA Soap Calculator API...
Ready to accept requests
```

**Fresh Database**:
```
[3/4] Checking for seed data...
  Database is empty (oils=0,additives=0)
  Loading seed data...
✓ Seed data loaded successfully
  - 11 oils added
  - 14 additives added (including Shale-validated data)
```

---

## Testing

### Local Testing

```bash
# Test 1: Fresh database
podman-compose down -v
podman-compose up
# Verify: Auto-seed runs, 11 oils + 14 additives

# Test 2: Restart with data
podman-compose restart
# Verify: Seed skipped, fast startup

# Test 3: Idempotency
python scripts/test_seed_idempotent.py
# Expected: All tests pass
```

### Production Validation

```bash
# After deployment
ssh grimm-lin "podman logs mga-soap-calculator | grep -A10 'seed data'"

# Verify API
curl http://grimm-lin.local:8000/api/v1/oils | jq '. | length'
# Expected: 11

# Check health
curl http://grimm-lin.local:8000/api/v1/health
# Expected: {"status": "healthy", ...}
```

---

## Rollback Procedure

### Emergency Rollback to v1.0.0

```bash
# Stop current version
podman stop mga-soap-calculator
podman rm mga-soap-calculator

# Start previous version
podman run -d \
    --name mga-soap-calculator \
    -p 8000:8000 \
    --env-file .env.production \
    mga-soap-calculator:v1.0.0

# Manual seed (required for v1.0.0)
podman exec -it mga-soap-calculator bash scripts/init_db.sh
```

### Verify Rollback

```bash
# Check version in logs
podman logs mga-soap-calculator | head -20

# Verify API works
curl http://localhost:8000/api/v1/health
```

---

## Best Practices

### Development

- Use `podman-compose down -v` for clean slate testing
- Monitor logs during first run with new migrations
- Test idempotency with `scripts/test_seed_idempotent.py`
- Verify seed data via API, not just database

### Production

- Always use Ansible for deployment (consistent, auditable)
- Monitor first startup logs after deployment
- Keep previous image tagged for quick rollback
- Backup database before major version upgrades

### Monitoring

- Set up alerts for container health check failures
- Monitor startup time (spike = database issues)
- Track seed operation results in logs
- Alert on seed failures (manual intervention needed)

---

## Support

### Debug Commands

```bash
# View all logs
podman logs mga-soap-calculator

# Follow logs in real-time
podman logs -f mga-soap-calculator

# Check container status
podman inspect mga-soap-calculator | jq '.[0].State'

# Database connection test
podman exec mga-postgresql pg_isready -U soap_user

# Manual SQL check
podman exec -it mga-postgresql psql -U soap_user -d soap_calculator
```

### Common Fixes

**Issue**: Container won't start
**Fix**: Check logs, verify DATABASE_URL, ensure PostgreSQL running

**Issue**: Seed data missing
**Fix**: Delete volumes, restart container, watch logs

**Issue**: Duplicates created
**Fix**: Run `scripts/test_seed_idempotent.py` to verify bug

---

## Additional Resources

- **Implementation Report**: `agent-responses/20251104_130116_deployment-engineer_container-autoseed-implementation.md`
- **Test Suite**: `scripts/test_seed_idempotent.py`
- **Entrypoint Script**: `scripts/docker-entrypoint.sh`
- **Seed Data**: `scripts/seed_data.py`

---

**Maintainer**: Bob Patterson (PAI)
**Last Updated**: 2025-11-04
**Version**: 1.2.0
