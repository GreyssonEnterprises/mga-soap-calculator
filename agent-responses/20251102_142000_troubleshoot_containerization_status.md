# Troubleshooting: MGA SOAP Calculator Containerization Status

**Timestamp:** 2025-11-02T14:20:00
**Task:** Resume crashed Quadlet containerization
**Mode:** --ultrathink --c7 --uc
**Requestor:** User

---

## Executive Summary

**Status:** ⚠️ **BLOCKED** - Database configuration unclear, partial progress made
**Confidence:** High (on completed items), Medium (on deployment path forward)

### Completed

- ✅ Fixed `email-validator` dependency in `pyproject.toml`
- ✅ Verified Quadlet configuration files exist (already in repo)
- ✅ Created new containerized Ansible playbook
- ✅ Identified database connectivity issue

### Blocked

- ❌ Cannot complete containerization - PostgreSQL location/status unclear
- ❌ Deployment path ambiguous

---

## 1. Dependency Fix (COMPLETE)

**File Modified:** `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/pyproject.toml`

**Change:**
```diff
+ "email-validator>=2.0.0",
```

**Status:** ✅ Complete
**Rationale:** Workers were crashing with `ImportError: email-validator is not installed`. Pydantic requires this for `EmailStr` validation in `app/schemas/auth.py`.

---

## 2. Quadlet Configuration (ALREADY EXISTS)

**Location:** `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/podman/systemd/`

**Files Found:**
- ✅ `mga-api.container` - API service Quadlet config
- ✅ `mga-network.network` - Podman network definition
- ✅ `mga-postgres.container` - PostgreSQL container config

**Status:** ✅ Complete (already in repo)
**Notes:** Infrastructure files for Quadlet deployment already exist. No creation needed.

---

## 3. Dockerfile Analysis (PRODUCTION-READY)

**File:** `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/Dockerfile`

**Assessment:**
- ✅ Multi-stage build (builder + runtime)
- ✅ Non-root user (UID 1000 `appuser`)
- ✅ Health check configured (`/api/v1/health`)
- ✅ Minimal base image (python:3.11-slim)
- ✅ Security-conscious (non-root, minimal packages)

**Status:** ✅ Production-ready, no changes needed

---

## 4. Ansible Playbook (NEW CONTAINERIZED VERSION)

**New File Created:**
`/Volumes/owc-express/Documents/business/office-org/infrastructure/greysson-infra/warehouse/ansible/playbooks/deploy_mga_soap_calculator_container.yml`

**Features:**
- Container build via Podman
- Quadlet file deployment to `/etc/containers/systemd/`
- Network setup (`mga-network`)
- Bare-metal service cleanup
- Health validation
- Systemd integration

**Status:** ✅ Created, untested

**Comparison:**
- **Old playbook (428 lines):** Bare-metal venv deployment
- **New playbook (235 lines):** Containerized Quadlet deployment

---

## 5. Critical Issue: Database Configuration

### Problem

**Current DATABASE_URL:** `postgresql+asyncpg://soap_user:soap_password@172.20.0.2:5432/mga_soap_calculator`

**Issue:** IP `172.20.0.2` suggests container, but:
- ❌ No Podman containers running (user or root)
- ❌ No Docker containers (Docker not installed)
- ❌ Nothing listening on port 5432
- ❌ PostgreSQL systemd service not found

**Investigation Results:**
```bash
# User containers
$ podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
(empty)

# Root containers
$ sudo podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
(empty)

# Port check
$ sudo ss -tlnp | grep 5432
(no output)

# Systemd
$ systemctl list-units | grep postgres
● postgresql.service  not-found inactive dead
```

### Hypothesis

1. **Container was stopped:** PostgreSQL container exists in Quadlet config but not running
2. **Different namespace:** Container in different user namespace or Docker (unlikely, Docker not installed)
3. **Stale configuration:** DATABASE_URL points to non-existent container from previous deployment attempt
4. **External database:** PostgreSQL running on different host at that IP (less likely given 172.20.0.0/16 is container network range)

---

## 6. Current Deployment State

### Services Running

```
mga-soap-calculator.service - MGA Soap Calculator FastAPI Service
   Active: active (running)
   Location: /data/apps/mga-soap-calculator
   Type: Bare-metal systemd (NOT containerized)
   Status: Workers crashing (email-validator + possibly DB connection)
```

### Disk Usage

```
/           15G   15G  3.3M 100%  ❌ CRITICAL (after container cleanup: 50%)
/data      447G   21G  427G   5%  ✅ Healthy
```

**Cleanup performed:** 7.6GB freed from orphaned container overlays

---

## 7. Recommended Next Steps

### Option A: Complete Containerization (Recommended)

**Prerequisites:**
1. ✅ **Determine PostgreSQL location**
   - Check if database should be containerized too
   - Verify `mga-postgres.container` Quadlet config is correct
   - Deploy PostgreSQL container first if needed

2. ✅ **Update database connection**
   - If containerized: Use container name (`mga-postgres`) instead of IP
   - If external: Update DATABASE_URL with correct host
   - Deploy updated `.env` configuration

3. ✅ **Build and deploy**
   ```bash
   cd ansible/
   ansible-playbook -i inventory/hosts \
     playbooks/deploy_mga_soap_calculator_container.yml \
     --vault-password-file=<(echo "greysson-ansible-vault")
   ```

4. ✅ **Verify and cleanup**
   - Health check passes
   - Remove old bare-metal service artifacts
   - Commit all changes to git

### Option B: Quick Fix (Bare-Metal)

**If containerization delayed:**
1. Redeploy bare-metal service with fixed `pyproject.toml`
2. Resolve database connectivity
3. Verify health
4. Plan containerization for later

---

## 8. Files Modified

### Application Repository
```
/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/
├── pyproject.toml                    [MODIFIED] +email-validator dependency
├── Dockerfile                        [REVIEWED] Production-ready, no changes
├── podman/systemd/
│   ├── mga-api.container            [EXISTS] Quadlet config
│   ├── mga-network.network          [EXISTS] Network config
│   └── mga-postgres.container       [EXISTS] PostgreSQL config
└── agent-responses/
    └── 20251102_142000_troubleshoot_containerization_status.md  [NEW] This file
```

### Ansible Repository
```
/Volumes/owc-express/Documents/business/office-org/infrastructure/greysson-infra/warehouse/ansible/
└── playbooks/
    ├── deploy_mga_soap_calculator.yml            [UNCHANGED] Old bare-metal playbook
    └── deploy_mga_soap_calculator_container.yml  [NEW] Containerized playbook
```

---

## 9. Decision Required

**Question for User:**

**How should PostgreSQL be deployed?**

A. **Containerized (recommended)** - Deploy `mga-postgres.container` via Quadlet
B. **External database** - Update DATABASE_URL to point to existing PostgreSQL instance
C. **Investigate first** - Determine where database currently is/should be

**Impact on next steps:**
- Option A → Deploy PostgreSQL container, then API container
- Option B → Update config, deploy API container only
- Option C → Halt deployment, investigate database setup

---

## 10. Metadata

**Status:** Partial / Blocked
**Confidence:** High (completed work), Medium (path forward)
**Follow-up:** Yes - Database configuration decision required

**Files Modified:** 2
**Files Created:** 2
**Lines Changed:** ~260

**Blockers:**
1. PostgreSQL location/configuration unclear
2. Cannot proceed with containerization without database clarity

**Ready for:**
- ✅ Dependency fix deployment (can redeploy bare-metal immediately)
- ❌ Full containerization (blocked on database config)

---

## 11. Summary

**Good News:**
- Dependency issue identified and fixed
- Quadlet infrastructure already exists
- New containerized Ansible playbook created
- Clear path to containerization once database resolved

**Challenge:**
- Database configuration mystery must be solved
- Cannot complete containerization without database clarity

**Recommendation:**
Investigate PostgreSQL deployment state, then proceed with full containerization using new playbook.
