# MGA SOAP Calculator — Containerized Deployment Tasks

**Specification:** 2025-11-02-containerized-deployment
**Created:** 2025-11-02
**Status:** Ready for Implementation
**Agent-OS Phase:** create-tasks (Phase 3)

---

## Task Overview

Implementation tasks broken down from containerization specification, addressing all 5 critical issues identified in architectural review.

### Task Groups
1. **Dockerfile Fixes** (3 tasks) — UBI base image migration, package manager fixes, build logic correction
2. **Database Standardization** (2 tasks) — Database naming, volume creation
3. **Quadlet Configuration** (3 tasks) — Health checks, resource limits, environment files
4. **Ansible Playbook** (4 tasks) — Volume management, health validation, secret management, network setup
5. **Testing & Validation** (3 tasks) — Integration tests, health checks, deployment validation
6. **Deployment Execution** (2 tasks) — Staging deployment, production rollout

**Total Tasks:** 17
**Estimated Duration:** 3-4 days (with staging validation)

---

## Group 1: Dockerfile Fixes

### Task 1.1: Migrate to UBI Base Image
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Medium
**Dependencies:** None
**Estimated Time:** 2 hours

**Description:**
Replace Debian-based `python:3.11-slim` with Red Hat UBI 9 Python image to ensure platform compatibility and policy compliance.

**Acceptance Criteria:**
- [ ] Dockerfile uses `registry.access.redhat.com/ubi9/python-311:latest` as base
- [ ] Both builder and runtime stages use UBI base
- [ ] Image builds successfully without errors
- [ ] Image architecture is `linux/amd64`
- [ ] No references to Debian/Alpine remain in Dockerfile

**Implementation Steps:**
1. Update `FROM` statements in both stages to UBI Python 311
2. Remove all `apt-get` commands
3. Verify base image pulls successfully
4. Build image and inspect architecture
5. Test container startup locally

**Files Modified:**
- `Dockerfile` (or `Containerfile`)

**Testing:**
```bash
podman build --platform linux/amd64 -t localhost/mga-soap-calculator:test .
podman inspect localhost/mga-soap-calculator:test | jq '.[0].Architecture'
```

---

### Task 1.2: Replace apt-get with DNF Package Manager
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Small
**Dependencies:** Task 1.1
**Estimated Time:** 1 hour

**Description:**
Convert all package installation commands from Debian `apt-get` to Red Hat `dnf`.

**Acceptance Criteria:**
- [ ] All `apt-get` commands replaced with `dnf`
- [ ] Package names updated for RHEL equivalents
- [ ] Build dependencies use RHEL package names
- [ ] Runtime dependencies use RHEL package names
- [ ] `dnf clean all` used to minimize image size

**Package Mapping:**
- `build-essential` → `gcc`, `make`
- `libpq-dev` → `postgresql-devel`
- `libpq5` → `postgresql-libs`

**Implementation Steps:**
1. Replace `apt-get update` with no-op (DNF repos pre-configured)
2. Update builder stage package installation to DNF
3. Update runtime stage package installation to DNF
4. Verify all packages install correctly
5. Test build process end-to-end

**Files Modified:**
- `Dockerfile`

**Testing:**
```bash
podman build -t localhost/mga-soap-calculator:test .
podman run --rm localhost/mga-soap-calculator:test dnf list installed | grep postgresql
```

---

### Task 1.3: Fix Dockerfile Build Logic (Application Code Before pip wheel)
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Small
**Dependencies:** Task 1.2
**Estimated Time:** 30 minutes

**Description:**
Fix build failure by copying application code BEFORE running `pip wheel -e .` so package source is available.

**Acceptance Criteria:**
- [ ] Application directories (`app/`, `src/`) copied before `pip wheel`
- [ ] `README.md` copied before `pip wheel`
- [ ] Build completes without "package not found" errors
- [ ] Wheels created successfully for project and dependencies
- [ ] Application code ownership set to `appuser:appuser`

**Implementation Steps:**
1. Move `COPY app ./app` before `pip wheel` command in builder stage
2. Move `COPY src ./src` before `pip wheel` command
3. Ensure `COPY README.md` before `pip wheel`
4. Keep `pyproject.toml` copy at top for layer caching
5. Test full build process

**Files Modified:**
- `Dockerfile`

**Testing:**
```bash
podman build -t localhost/mga-soap-calculator:test .
# Should complete without errors
podman run --rm localhost/mga-soap-calculator:test ls -la /app
```

---

## Group 2: Database Standardization

### Task 2.1: Standardize Database Name to mga_soap_calculator
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Medium
**Dependencies:** None
**Estimated Time:** 1.5 hours

**Description:**
Establish `mga_soap_calculator` as canonical database name and document migration path for existing deployments.

**Acceptance Criteria:**
- [ ] All Quadlet units use `mga_soap_calculator` as database name
- [ ] Ansible templates use `{{ db_name | default('mga_soap_calculator') }}` variable
- [ ] Environment file templates reference correct database name
- [ ] Migration procedure documented for existing `soap_calculator` databases
- [ ] Rollback procedure documented

**Implementation Steps:**
1. Update `postgres.env.j2` template with correct default
2. Update `api.env.j2` DATABASE_URL with correct database name
3. Update Quadlet HealthCmd to use `mga_soap_calculator`
4. Create migration documentation (SQL rename + pg_dump/restore)
5. Test migration procedure in local environment

**Files Modified:**
- `ansible/templates/postgres.env.j2`
- `ansible/templates/api.env.j2`
- `ansible/files/mga-postgres.container`
- `agent-os/specs/2025-11-02-containerized-deployment/MIGRATION.md` (new)

**Migration Commands (for documentation):**
```bash
# Option 1: SQL Rename (fast, downtime required)
podman exec -it mga-postgres psql -U postgres -c "ALTER DATABASE soap_calculator RENAME TO mga_soap_calculator;"

# Option 2: Dump and Restore (safer)
pg_dump -Fc -U soap_user -h 127.0.0.1 -d soap_calculator > backup.dump
createdb -U soap_user mga_soap_calculator
pg_restore -U soap_user -d mga_soap_calculator backup.dump
```

---

### Task 2.2: Create PostgreSQL Volume in Ansible Playbook
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Small
**Dependencies:** None
**Estimated Time:** 1 hour

**Description:**
Add explicit PostgreSQL volume creation task using `containers.podman.podman_volume` module to prevent startup failures.

**Acceptance Criteria:**
- [ ] Volume `mga-pgdata` created before PostgreSQL service starts
- [ ] Volume has proper labels (`app: mga-soap-calculator`, `component: database`)
- [ ] Volume creation is idempotent (no-op if exists)
- [ ] Task runs early in playbook (before service deployment)
- [ ] Volume inspection confirms creation

**Implementation Steps:**
1. Add volume creation task in Ansible playbook
2. Position task before Quadlet unit deployment
3. Add labels for identification
4. Ensure `containers.podman` collection installed
5. Test playbook execution

**Files Modified:**
- `ansible/playbooks/deploy_mga_soap_calculator.yml` (or create if missing)

**Task Implementation:**
```yaml
- name: Ensure PostgreSQL data volume exists
  containers.podman.podman_volume:
    name: mga-pgdata
    state: present
    labels:
      app: mga-soap-calculator
      component: database
```

**Testing:**
```bash
ansible-playbook deploy_mga_soap_calculator.yml --check
podman volume inspect mga-pgdata
```

---

## Group 3: Quadlet Configuration Updates

### Task 3.1: Implement Proper Health Checks
**Priority:** HIGH (Must-have for MVP)
**Complexity:** Medium
**Dependencies:** Task 2.1
**Estimated Time:** 2 hours

**Description:**
Replace arbitrary sleep commands with proper health check validation using Podman health check commands.

**Acceptance Criteria:**
- [ ] PostgreSQL Quadlet uses `pg_isready` for health check
- [ ] API Quadlet uses `curl /health` for health check
- [ ] Ansible playbook uses `podman healthcheck run` instead of `pause: 10s`
- [ ] Health checks have proper intervals, timeouts, retries configured
- [ ] Health start period accounts for initialization time

**PostgreSQL Health Check:**
```ini
HealthCmd=/usr/bin/sh -lc 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} -h 127.0.0.1 -p 5432'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s
```

**API Health Check:**
```ini
HealthCmd=/usr/bin/curl -fsS http://127.0.0.1:8000/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=60s
```

**Ansible Health Validation:**
```yaml
- name: Wait for PostgreSQL to be healthy
  command: podman healthcheck run mga-postgres
  register: pg_health
  retries: 30
  delay: 2
  until: pg_health.rc == 0
  changed_when: false
```

**Files Modified:**
- `ansible/files/mga-postgres.container`
- `ansible/files/soap-calculator-api.container`
- `ansible/playbooks/deploy_mga_soap_calculator.yml`

**Testing:**
```bash
podman healthcheck run mga-postgres
podman healthcheck run soap-api
```

---

### Task 3.2: Add Resource Limits to Quadlet Units
**Priority:** HIGH (Must-have for MVP)
**Complexity:** Small
**Dependencies:** None
**Estimated Time:** 45 minutes

**Description:**
Configure Memory and CPU resource limits in Quadlet units to prevent resource exhaustion.

**Acceptance Criteria:**
- [ ] PostgreSQL has `Memory=1G`, `MemorySwap=2G`, `CpuQuota=200%`
- [ ] API has `Memory=1G`, `MemorySwap=2G`, `CpuQuota=200%`
- [ ] Limits documented in specification
- [ ] Containers respect limits after deployment
- [ ] Resource usage monitored during testing

**Implementation Steps:**
1. Add resource limit directives to PostgreSQL Quadlet
2. Add resource limit directives to API Quadlet
3. Document rationale for chosen limits
4. Test limits enforcement with `podman stats`
5. Verify containers don't exceed limits under load

**Files Modified:**
- `ansible/files/mga-postgres.container`
- `ansible/files/soap-calculator-api.container`

**Resource Limit Configuration:**
```ini
[Container]
Memory=1G
MemorySwap=2G
CpuQuota=200%
```

**Testing:**
```bash
podman stats mga-postgres soap-api
# Verify limits respected under load
```

---

### Task 3.3: Create Environment File Templates
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Medium
**Dependencies:** Task 2.1
**Estimated Time:** 1.5 hours

**Description:**
Create Ansible Jinja2 templates for PostgreSQL and API environment files with proper vault integration.

**Acceptance Criteria:**
- [ ] `postgres.env.j2` template created with vault variables
- [ ] `api.env.j2` template created with vault variables
- [ ] Templates reference `vault_db_password` and `vault_jwt_secret_key`
- [ ] Deployed files have mode `0600` (root-only readable)
- [ ] Templates use `{{ db_name | default('mga_soap_calculator') }}` variable

**PostgreSQL Template (`templates/postgres.env.j2`):**
```jinja2
POSTGRES_USER=soap_user
POSTGRES_PASSWORD={{ vault_db_password }}
POSTGRES_DB={{ db_name | default('mga_soap_calculator') }}
```

**API Template (`templates/api.env.j2`):**
```jinja2
# Generated by Ansible - DO NOT EDIT MANUALLY
ENVIRONMENT=production
JWT_SECRET_KEY={{ vault_jwt_secret_key }}
DATABASE_URL=postgresql+psycopg://soap_user:{{ vault_db_password }}@mga-postgres:5432/{{ db_name | default('mga_soap_calculator') }}
WORKERS={{ api_workers | default(2) }}
LOG_LEVEL={{ log_level | default('INFO') }}
```

**Files Created:**
- `ansible/templates/postgres.env.j2`
- `ansible/templates/api.env.j2`

**Testing:**
```bash
ansible-playbook deploy_mga_soap_calculator.yml --check
ls -l /etc/mga-soap-calculator/*.env
# Should show mode 0600
```

---

## Group 4: Ansible Playbook Completion

### Task 4.1: Fix Network Error Handling
**Priority:** HIGH (Must-have for MVP)
**Complexity:** Small
**Dependencies:** None
**Estimated Time:** 30 minutes

**Description:**
Replace `failed_when: false` with proper conditional error handling for network connection tasks.

**Acceptance Criteria:**
- [ ] Network connection task uses conditional `failed_when` instead of `failed_when: false`
- [ ] Task allows "already exists" errors but fails on real errors
- [ ] Error messages properly surfaced for troubleshooting
- [ ] Task is idempotent (no-op if network already connected)

**Implementation:**
```yaml
- name: Connect PostgreSQL to mga-network if needed
  ansible.builtin.command:
    cmd: podman network connect mga-network mga-postgres
  register: network_connect
  changed_when: "'already exists' not in network_connect.stderr"
  failed_when:
    - network_connect.rc != 0
    - "'already exists' not in network_connect.stderr"
```

**Files Modified:**
- `ansible/playbooks/deploy_mga_soap_calculator.yml`

**Testing:**
```bash
# First run should succeed
ansible-playbook deploy_mga_soap_calculator.yml
# Second run should be no-op (already connected)
ansible-playbook deploy_mga_soap_calculator.yml
```

---

### Task 4.2: Add JWT Secret to Vault
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Small
**Dependencies:** Task 3.3
**Estimated Time:** 30 minutes

**Description:**
Ensure `vault_jwt_secret_key` exists in Ansible Vault to prevent authentication failures.

**Acceptance Criteria:**
- [ ] `vault_jwt_secret_key` defined in `group_vars/production/vault.yml`
- [ ] Secret is cryptographically random (256-bit minimum)
- [ ] Vault file encrypted with `ansible-vault`
- [ ] Secret referenced in `api.env.j2` template
- [ ] API container receives secret via environment file

**Implementation Steps:**
1. Generate secure random key (Python secrets module or openssl)
2. Edit vault file: `ansible-vault edit group_vars/production/vault.yml`
3. Add `vault_jwt_secret_key: "generated_key"`
4. Verify template references variable
5. Test deployment with vault password

**Files Modified:**
- `ansible/group_vars/production/vault.yml` (encrypted)

**Secret Generation:**
```bash
# Generate 256-bit random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# or
openssl rand -base64 32
```

**Testing:**
```bash
ansible-vault view group_vars/production/vault.yml | grep jwt_secret_key
ansible-playbook deploy_mga_soap_calculator.yml --ask-vault-pass --check
```

---

### Task 4.3: Create Podman Network Quadlet Unit
**Priority:** HIGH (Must-have for MVP)
**Complexity:** Small
**Dependencies:** None
**Estimated Time:** 45 minutes

**Description:**
Create Quadlet network unit for `mga-network` to ensure network exists before container startup.

**Acceptance Criteria:**
- [ ] `mga-network.network` file created in Ansible files
- [ ] Network uses `10.89.0.0/24` subnet
- [ ] Bridge name set to `br-mga`
- [ ] IPv6 disabled
- [ ] File deployed to `/etc/containers/systemd/`
- [ ] Network created automatically by systemd generator

**Network Unit (`files/mga-network.network`):**
```ini
[Network]
NetworkName=mga-network
Driver=bridge
Subnet=10.89.0.0/24
Gateway=10.89.0.1
IPv6=false

[Network.Options]
com.docker.network.bridge.name=br-mga
```

**Files Created:**
- `ansible/files/mga-network.network`

**Ansible Deployment:**
```yaml
- name: Deploy Quadlet network unit
  copy:
    src: files/mga-network.network
    dest: /etc/containers/systemd/mga-network.network
    owner: root
    group: root
    mode: '0644'
  notify: daemon-reload
```

**Testing:**
```bash
systemctl daemon-reload
podman network inspect mga-network
ip link show br-mga
```

---

### Task 4.4: Complete Ansible Playbook Structure
**Priority:** HIGH (Must-have for MVP)
**Complexity:** Large
**Dependencies:** Tasks 2.2, 3.1, 3.3, 4.1, 4.2, 4.3
**Estimated Time:** 3 hours

**Description:**
Create complete Ansible playbook integrating all tasks: volume creation, Quadlet deployment, health checks, service activation.

**Acceptance Criteria:**
- [ ] Playbook creates configuration directory `/etc/mga-soap-calculator`
- [ ] Playbook creates PostgreSQL volume
- [ ] Playbook deploys environment files with proper permissions
- [ ] Playbook deploys Quadlet units (network, postgres, api)
- [ ] Playbook performs daemon-reload
- [ ] Playbook enables and starts services in correct order
- [ ] Playbook validates health checks
- [ ] Playbook is idempotent (safe to re-run)
- [ ] Handlers properly trigger service restarts

**Playbook Structure:**
```yaml
---
- name: Deploy MGA SOAP Calculator (API + PostgreSQL Containers)
  hosts: mga_production
  become: true
  vars_files:
    - group_vars/production/vault.yml
  vars:
    db_name: "mga_soap_calculator"
    api_image: "localhost/mga-soap-calculator:latest"
    api_workers: 2

  tasks:
    - name: Ensure configuration directory exists
    - name: Ensure PostgreSQL data volume exists
    - name: Deploy environment files from templates
    - name: Deploy Quadlet container units
    - name: Reload systemd daemon
    - name: Enable and start PostgreSQL service
    - name: Wait for PostgreSQL to be healthy
    - name: Enable and start API service
    - name: Wait for API health endpoint
    - name: Verify deployment success

  handlers:
    - name: daemon-reload
    - name: restart services
```

**Files Created:**
- `ansible/playbooks/deploy_mga_soap_calculator.yml`
- `ansible/inventories/production/hosts.yml` (if missing)
- `ansible/group_vars/production/vars.yml` (if missing)

**Testing:**
```bash
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml --check
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml --ask-vault-pass
```

---

## Group 5: Testing & Validation

### Task 5.1: Create Integration Test Suite
**Priority:** MEDIUM (Should-have for production)
**Complexity:** Medium
**Dependencies:** Task 4.4
**Estimated Time:** 2.5 hours

**Description:**
Create pytest-based integration tests to validate containerized deployment functionality.

**Acceptance Criteria:**
- [ ] Test verifies API health endpoint responds correctly
- [ ] Test verifies database connectivity from API
- [ ] Test verifies saponification calculation endpoint works
- [ ] Test verifies container resource limits enforced
- [ ] Tests executable against staging environment
- [ ] All tests pass before production deployment

**Test File Structure:**
```
tests/integration/
├── __init__.py
├── conftest.py
├── test_containerized_deployment.py
└── test_health_checks.py
```

**Key Tests:**
```python
def test_health_endpoint():
    """Verify API health endpoint responds correctly."""
    response = requests.get(f"{STAGING_API_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_database_connectivity():
    """Verify database accessible and schema correct."""
    # Connect and verify PostgreSQL 15

def test_api_calculation_endpoint():
    """Verify saponification calculation API works."""
    # Submit calculation request and verify response
```

**Files Created:**
- `tests/integration/test_containerized_deployment.py`
- `tests/integration/test_health_checks.py`
- `tests/integration/conftest.py`

**Testing:**
```bash
pytest tests/integration/ -v --tb=short
```

---

### Task 5.2: Create Validation Playbook
**Priority:** MEDIUM (Should-have for production)
**Complexity:** Small
**Dependencies:** Task 4.4
**Estimated Time:** 1.5 hours

**Description:**
Create Ansible playbook for post-deployment validation to verify all services healthy and operational.

**Acceptance Criteria:**
- [ ] Playbook checks systemd service status
- [ ] Playbook verifies API health endpoint
- [ ] Playbook verifies database connectivity
- [ ] Playbook inspects container logs for errors
- [ ] Playbook reports deployment validation success/failure
- [ ] Playbook executable after main deployment

**Validation Checks:**
```yaml
- name: Check PostgreSQL service status
  systemd:
    name: mga-postgres.service
  register: pg_status
  failed_when: pg_status.status.ActiveState != 'active'

- name: Verify API health endpoint
  uri:
    url: http://127.0.0.1:8000/health
    status_code: 200
    return_content: true
  register: health_check
  failed_when: health_check.json.status != 'healthy'

- name: Inspect container logs for errors
  command: journalctl -u soap-calculator-api.service -n 50 --no-pager
  register: logs
  failed_when: "'ERROR' in logs.stdout or 'CRITICAL' in logs.stdout"
```

**Files Created:**
- `ansible/playbooks/validate_deployment.yml`

**Testing:**
```bash
ansible-playbook -i inventories/production playbooks/validate_deployment.yml
```

---

### Task 5.3: Create Rollback Playbook
**Priority:** MEDIUM (Should-have for production)
**Complexity:** Medium
**Dependencies:** Task 4.4
**Estimated Time:** 2 hours

**Description:**
Create Ansible playbook for rolling back to previous API version if deployment fails.

**Acceptance Criteria:**
- [ ] Playbook stops API service
- [ ] Playbook tags current image as broken
- [ ] Playbook restores previous image to latest
- [ ] Playbook starts API service
- [ ] Playbook validates health after rollback
- [ ] Playbook supports rollback to specific version tag
- [ ] Rollback tested in staging environment

**Rollback Procedure:**
```yaml
- name: Stop API service
  systemd:
    name: soap-calculator-api.service
    state: stopped

- name: Tag current as broken
  command: >
    podman tag localhost/mga-soap-calculator:latest
    localhost/mga-soap-calculator:broken-{{ ansible_date_time.epoch }}

- name: Restore previous version to latest
  command: >
    podman tag localhost/mga-soap-calculator:{{ rollback_tag }}
    localhost/mga-soap-calculator:latest

- name: Start API service
  systemd:
    name: soap-calculator-api.service
    state: started

- name: Wait for API health check
  uri:
    url: http://127.0.0.1:8000/health
    status_code: 200
  retries: 20
  delay: 3
```

**Files Created:**
- `ansible/playbooks/rollback_mga_api.yml`

**Testing:**
```bash
# Test rollback to previous
ansible-playbook rollback_mga_api.yml --ask-vault-pass

# Test rollback to specific version
ansible-playbook rollback_mga_api.yml \
  --extra-vars "rollback_tag=v1.2.3-20251102" \
  --ask-vault-pass
```

---

## Group 6: Deployment Execution & Cleanup

### Task 6.1: Deploy to Staging Environment
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Large
**Dependencies:** All Group 1-4 tasks, Tasks 5.1, 5.2
**Estimated Time:** 4 hours (includes troubleshooting)

**Description:**
Execute full deployment to staging environment, validate all components, run integration tests.

**Acceptance Criteria:**
- [ ] Dockerfile builds successfully on staging
- [ ] Ansible playbook executes without errors
- [ ] All services start and reach healthy state
- [ ] Integration tests pass (100%)
- [ ] Validation playbook passes
- [ ] Performance baseline captured
- [ ] No errors in container logs
- [ ] Resource limits enforced
- [ ] Staging environment stable for 24 hours

**Deployment Steps:**
1. Build container image on build server
2. Transfer image to staging server (or use local registry)
3. Execute Ansible deployment playbook
4. Run validation playbook
5. Execute integration test suite
6. Capture performance baseline (k6 or Locust)
7. Monitor for 24 hours
8. Document any issues encountered

**Commands:**
```bash
# Build image
podman build --platform linux/amd64 -t localhost/mga-soap-calculator:staging .

# Deploy to staging
ansible-playbook -i inventories/staging playbooks/deploy_mga_soap_calculator.yml \
  --ask-vault-pass

# Validate deployment
ansible-playbook -i inventories/staging playbooks/validate_deployment.yml

# Run integration tests
pytest tests/integration/ -v --staging
```

**Success Metrics:**
- Build time: < 5 minutes
- Deployment time: < 10 minutes
- Health check pass time: < 2 minutes
- Integration test pass rate: 100%
- Zero ERROR or CRITICAL log entries
- Resource usage within limits (Memory < 1GB, CPU < 200%)

**Files Modified:**
- None (execution only)

**Deliverables:**
- Staging deployment report
- Performance baseline metrics
- Issue log (if any problems encountered)

---

### Task 6.2: Production Deployment & Cleanup
**Priority:** CRITICAL (Must-have for MVP)
**Complexity:** Large
**Dependencies:** Task 6.1 (successful staging deployment)
**Estimated Time:** 3 hours

**Description:**
Execute production deployment, validate functionality, clean up old deployment artifacts.

**Acceptance Criteria:**
- [ ] Pre-deployment backup of database created
- [ ] Current production image tagged as 'previous'
- [ ] Ansible playbook executes without errors
- [ ] All production services healthy
- [ ] Validation playbook passes
- [ ] Smoke tests pass (calculation endpoint works)
- [ ] Rollback playbook tested (verify can rollback if needed)
- [ ] Old temporary files cleaned up
- [ ] Documentation updated with deployment date/version

**Pre-Deployment Checklist:**
- [ ] Staging deployment stable for 24+ hours
- [ ] All integration tests passing
- [ ] Rollback playbook tested in staging
- [ ] Database backup verified restorable
- [ ] Vault password accessible
- [ ] Production inventory file updated
- [ ] Change window scheduled (low-traffic period)
- [ ] Rollback decision criteria defined

**Deployment Steps:**
1. Create pre-deployment database backup
2. Tag current production image as 'previous'
3. Build production container image
4. Transfer image to production server
5. Execute Ansible deployment playbook
6. Run validation playbook
7. Execute smoke tests
8. Monitor for initial stability (30 minutes)
9. Clean up old images/containers
10. Update deployment documentation

**Commands:**
```bash
# Pre-deployment backup
pg_dump -Fc -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  > /backups/mga-soap-pre-deployment-$(date +%Y%m%d).dump

# Tag current as previous
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:previous

# Deploy to production
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml \
  --ask-vault-pass

# Validate
ansible-playbook -i inventories/production playbooks/validate_deployment.yml

# Smoke tests
ansible-playbook -i inventories/production playbooks/smoke_test_production.yml
```

**Rollback Criteria:**
- Health checks failing after 5 minutes
- Database connectivity errors
- API returns 500 errors
- Critical functionality broken
- Resource usage exceeds limits

**Post-Deployment Cleanup:**
```bash
# Remove old stopped containers
podman container prune -f

# Remove old untagged images
podman image prune -f

# Keep last 3 tagged versions only
# (Manual inspection and removal)

# Verify volume backups exist
ls -lh /backups/mga-*
```

**Files Modified:**
- `agent-os/specs/2025-11-02-containerized-deployment/DEPLOYMENT.md` (deployment record)

**Deliverables:**
- Production deployment report
- Post-deployment validation report
- Backup verification confirmation
- Updated runbook with lessons learned

---

## Task Dependencies Graph

```
Group 1 (Dockerfile):
1.1 (UBI Base) → 1.2 (DNF) → 1.3 (Build Fix)
                                    ↓
Group 2 (Database):                 ↓
2.1 (DB Name) ←←←←←←←←←←←←←←←←←←←←←←←+
    ↓                               ↓
2.2 (Volume) → → → → → → → → → → → +
                                    ↓
Group 3 (Quadlet):                  ↓
3.1 (Health) ←←← 2.1                ↓
3.2 (Resources)                     ↓
3.3 (Env Files) ←←← 2.1             ↓
    ↓           ↓           ↓       ↓
Group 4 (Ansible):                  ↓
4.1 (Network Fix)                   ↓
4.2 (JWT Vault) → 3.3               ↓
4.3 (Network Quadlet)               ↓
    ↓           ↓           ↓       ↓
4.4 (Complete Playbook) ← ALL Above +
                    ↓
Group 5 (Testing):  ↓
5.1 (Integration Tests) ← 4.4
5.2 (Validation) ← 4.4
5.3 (Rollback) ← 4.4
         ↓       ↓       ↓
Group 6 (Deploy):
6.1 (Staging) ← ALL Group 5
         ↓
6.2 (Production) ← 6.1
```

---

## Priority Summary

### CRITICAL (Must-have for MVP) — 10 tasks
- Task 1.1: UBI Base Image Migration
- Task 1.2: DNF Package Manager
- Task 1.3: Build Logic Fix
- Task 2.1: Database Name Standardization
- Task 2.2: Volume Creation
- Task 3.3: Environment File Templates
- Task 4.2: JWT Secret Vault
- Task 6.1: Staging Deployment
- Task 6.2: Production Deployment

### HIGH (Must-have for MVP) — 4 tasks
- Task 3.1: Proper Health Checks
- Task 3.2: Resource Limits
- Task 4.1: Network Error Handling
- Task 4.3: Network Quadlet Unit
- Task 4.4: Complete Playbook

### MEDIUM (Should-have for production) — 3 tasks
- Task 5.1: Integration Test Suite
- Task 5.2: Validation Playbook
- Task 5.3: Rollback Playbook

---

## Execution Plan

### Phase 1: Core Infrastructure (Day 1)
**Time Estimate:** 6-8 hours
- Task 1.1, 1.2, 1.3: Dockerfile fixes (3.5 hours)
- Task 2.1, 2.2: Database standardization (2.5 hours)
- Task 3.2: Resource limits (0.75 hours)
- Task 4.3: Network Quadlet (0.75 hours)

**Deliverable:** Working Dockerfile, database standardization complete

### Phase 2: Configuration & Health (Day 2)
**Time Estimate:** 6-7 hours
- Task 3.1: Health checks (2 hours)
- Task 3.3: Environment templates (1.5 hours)
- Task 4.1: Network error handling (0.5 hours)
- Task 4.2: JWT vault secret (0.5 hours)
- Task 4.4: Complete Ansible playbook (3 hours)

**Deliverable:** Complete Ansible automation, all Quadlet units configured

### Phase 3: Testing & Validation (Day 2-3)
**Time Estimate:** 6 hours
- Task 5.1: Integration tests (2.5 hours)
- Task 5.2: Validation playbook (1.5 hours)
- Task 5.3: Rollback playbook (2 hours)

**Deliverable:** Comprehensive test suite, validation automation

### Phase 4: Deployment (Day 3-4)
**Time Estimate:** 7 hours + 24-hour soak
- Task 6.1: Staging deployment (4 hours)
- 24-hour stability monitoring
- Task 6.2: Production deployment (3 hours)

**Deliverable:** Production-ready containerized deployment

---

## Risk Assessment

### High Risks
1. **Database migration breaking existing deployments**
   - Mitigation: Comprehensive migration documentation, tested rollback procedure
   - Contingency: Keep old database name as option, document both approaches

2. **SELinux permission issues in production**
   - Mitigation: Test SELinux enforcing mode in staging first
   - Contingency: Document SELinux troubleshooting, have `ausearch` commands ready

3. **Health checks failing due to timing issues**
   - Mitigation: Conservative timeouts, proper start periods
   - Contingency: Increase retries/delays if needed, monitor logs

### Medium Risks
1. **Ansible collection dependencies missing**
   - Mitigation: Document required collections, install in staging first
   - Contingency: Manual Podman commands if Ansible fails

2. **Image architecture mismatch (arm64 vs amd64)**
   - Mitigation: Explicit `--platform linux/amd64` flag in builds
   - Contingency: Rebuild with correct architecture

### Low Risks
1. **JWT secret rotation complexity**
   - Mitigation: Clear vault documentation, tested template deployment
   - Contingency: Manual environment file update if template fails

---

## Success Criteria

**MVP Deployment Complete When:**
- [ ] All CRITICAL tasks (10) completed
- [ ] All HIGH tasks (5) completed
- [ ] Staging deployment stable for 24+ hours
- [ ] Integration tests 100% pass rate
- [ ] Production deployment successful
- [ ] All 5 architectural review issues resolved
- [ ] Zero ERROR/CRITICAL log entries in production
- [ ] Resource limits enforced and validated
- [ ] Rollback tested and documented

**Production Ready When:**
- [ ] All MVP criteria met
- [ ] All MEDIUM tasks (3) completed
- [ ] Performance baseline captured
- [ ] Monitoring configured (optional but recommended)
- [ ] Documentation complete and reviewed
- [ ] Team trained on deployment/rollback procedures

---

## Notes

**Architecture Review Resolution:**
This task breakdown addresses all 5 issues identified in architectural review:
1. ✅ Debian base image → UBI base (Tasks 1.1, 1.2)
2. ✅ Database naming mismatch → Standardized (Task 2.1)
3. ✅ Missing volume creation → Explicit task (Task 2.2)
4. ✅ Network error masking → Proper handling (Task 4.1)
5. ✅ Health check timing → Proper validation (Task 3.1)

Additional improvements beyond review:
- Resource limits (Task 3.2)
- JWT secret vault (Task 4.2)
- Comprehensive testing (Group 5)
- Rollback automation (Task 5.3)

**Agent-OS Workflow:**
- Phase 3 (create-tasks): ✅ Complete (this document)
- Next Phase: /orchestrate-tasks (parallel execution of independent tasks)

---

**Document Version:** 1.0
**Created:** 2025-11-02
**Status:** Ready for Orchestration
**Total Tasks:** 17
**Estimated Duration:** 3-4 days
