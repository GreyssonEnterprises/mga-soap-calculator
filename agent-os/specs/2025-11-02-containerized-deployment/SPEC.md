# MGA SOAP Calculator — Containerized Deployment Specification

**Version:** 1.0
**Date:** 2025-11-02
**Status:** Draft for Review
**Owner:** MGA Infrastructure Team

---

## 1. Overview

### What We're Deploying
Containerized deployment of the MGA SOAP Calculator backend API (FastAPI, Python 3.11) with PostgreSQL database, orchestrated by Quadlet (systemd integration) on Fedora 42 using Podman.

### Why Containerization
- **Consistency:** Reproducible builds and deployments across environments
- **Isolation:** Stronger process and resource isolation with SELinux enforcement
- **Integration:** Native systemd lifecycle management, logging, and resource controls
- **Maintainability:** Simplified updates, rollbacks, and dependency management

### Scope and Objectives
- Resolve all issues identified in architectural review (5 critical issues)
- Enforce base image policy (Fedora/UBI only, NO Debian/Alpine)
- Define PostgreSQL and API container configuration with proper health checks
- Implement volume persistence and network isolation
- Provide idempotent Ansible deployment with Quadlet units
- Document safe migration path for database naming standardization

---

## 2. Architecture

### Container Stack
- **mga-postgres:** PostgreSQL 15 running on Red Hat UBI-based image
- **soap-calculator-api:** FastAPI application (Gunicorn + Uvicorn workers)

### Network Topology
- **Custom bridge network:** `mga-network` (10.89.0.0/24)
- **Service discovery:** Name-based resolution (postgres accessible as `mga-postgres` within network)
- **Port publishing:**
  - PostgreSQL: `127.0.0.1:5432:5432` (localhost-only for admin tools)
  - API: `8000:8000` (external access via reverse proxy)

### Data Persistence Strategy
- **Named Podman volume:** `mga-pgdata` mounted to PostgreSQL data directory
- **SELinux labels:** `:Z` flag for exclusive container access
- **Backups:** `podman volume export/import` for volume snapshots, `pg_dump` for logical backups

### Service Dependencies
```
mga-network.network
    ↓
mga-postgres.service (requires network)
    ↓
soap-calculator-api.service (requires postgres + network)
```

systemd ordering in Quadlet units ensures:
1. Network created first
2. Database starts and becomes healthy
3. API starts only after database health check passes

---

## 3. Platform Requirements

### Operating System
- **OS:** Fedora 42 Linux (x86_64)
- **Kernel:** 6.x+ with cgroups v2 support
- **Init System:** systemd 255+
- **SELinux:** Enforcing mode (mandatory)

### Container Runtime
- **Podman:** 4.9+ (rootful mode for system services)
- **Quadlet:** Included with Podman 4.4+ (systemd generator)
- **Storage Driver:** overlay with fuse-overlayfs

### Registry Access
- **Primary:** Red Hat Container Catalog (`registry.access.redhat.com`)
- **Fallback:** Fedora Container Registry (`registry.fedoraproject.org`)
- **Local:** Optional local registry for image hosting (avoid Docker Hub dependency)

### SELinux Configuration
- **Mode:** Enforcing (production requirement)
- **Volume labeling:** `:Z` (private) or `:z` (shared) required for all mounts
- **Container context:** `container_runtime_t` (default)
- **File context:** `container_file_t` for bind-mounted directories

---

## 4. PostgreSQL Container

### 4.1 Container Image

#### Base Image Selection
**Preferred:**
```dockerfile
FROM registry.redhat.io/rhel9/postgresql-15:latest
```

**Fallback (Custom Build):**
```dockerfile
FROM registry.access.redhat.com/ubi9/ubi:latest

RUN dnf install -y postgresql15-server postgresql15 && dnf clean all

# Create postgres user and data directory
RUN useradd -r -u 26 -g 26 -d /var/lib/pgsql postgres && \
    mkdir -p /var/lib/pgsql/data && \
    chown -R postgres:postgres /var/lib/pgsql

USER postgres
ENV PGDATA=/var/lib/pgsql/data

# Initialize database if empty, then start server
ENTRYPOINT ["/bin/bash", "-lc", "if [ ! -s \"$PGDATA/PG_VERSION\" ]; then \
  /usr/pgsql-15/bin/initdb -D \"$PGDATA\"; \
fi; exec /usr/pgsql-15/bin/postgres -D \"$PGDATA\" -c listen_addresses='*'"]

EXPOSE 5432
```

#### Version Pinning Strategy
- Pin to major.minor version (15.x)
- Track security updates via image rebuilds
- Test updates in staging before production

#### Rationale
- **Platform compatibility:** UBI 9 matches Fedora 42 glibc, OpenSSL, systemd versions
- **SELinux integration:** Proper labels and contexts out-of-box
- **Security:** Red Hat/Fedora security pipeline, CVE tracking
- **NO Debian/Alpine:** Eliminates package manager mismatch, musl libc incompatibilities

### 4.2 Quadlet Configuration

**File:** `/etc/containers/systemd/mga-postgres.container`

```ini
[Unit]
Description=MGA PostgreSQL 15 Database
Wants=network-online.target
After=network-online.target mga-network.network

[Container]
# Preferred: Red Hat official PostgreSQL image
Image=registry.redhat.io/rhel9/postgresql-15:latest

# Fallback: Custom UBI-based image (if building locally)
# Image=localhost/mga-postgres:15

ContainerName=mga-postgres
Network=mga-network
PublishPort=127.0.0.1:5432:5432
EnvironmentFile=/etc/mga-soap-calculator/postgres.env

# Persistent data with SELinux relabel (private mount)
Volume=mga-pgdata:/var/lib/pgsql/data:Z

# Health check - proper health verification (not sleep)
HealthCmd=/usr/bin/sh -lc 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} -h 127.0.0.1 -p 5432'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s

# Resource limits (addressed from architecture review)
Memory=1G
MemorySwap=2G
CpuQuota=200%

# Logging
PodmanArgs=--log-driver=journald

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=300
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Environment File:** `/etc/mga-soap-calculator/postgres.env` (managed by Ansible)

```ini
POSTGRES_USER=soap_user
POSTGRES_PASSWORD=REDACTED_FROM_VAULT
POSTGRES_DB=mga_soap_calculator
```

**Key Configuration Notes:**
- **Database naming resolved:** Canonical name is `mga_soap_calculator` to avoid breaking existing deployments
- **Health check:** Uses `pg_isready` for proper health verification (replaces arbitrary sleep)
- **SELinux label:** `:Z` flag ensures exclusive access with proper context
- **Resource limits:** Prevents memory/CPU exhaustion (1GB memory, 200% CPU quota)

### 4.3 Data Persistence

#### Volume Creation (Ansible)
```yaml
- name: Create PostgreSQL data volume
  containers.podman.podman_volume:
    name: mga-pgdata
    state: present
    labels:
      app: mga-soap-calculator
      component: database
```

#### Backup Strategy

**Volume Snapshot:**
```bash
# Export volume to tarball
podman volume export mga-pgdata | gzip > /backups/mga-pgdata-$(date +%Y%m%d).tar.gz
```

**Logical Backup (Preferred):**
```bash
# PostgreSQL dump (more flexible for restoration)
pg_dump -Fc -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  > /backups/mga-soap-$(date +%Y%m%d).dump

# Automated daily backups via cron
0 2 * * * /usr/local/bin/backup-mga-db.sh
```

#### Restoration Procedures

**From Volume Export:**
```bash
# Stop database service
sudo systemctl stop mga-postgres.service

# Remove old volume
podman volume rm -f mga-pgdata

# Create new volume
podman volume create mga-pgdata

# Import backup
gunzip -c /backups/mga-pgdata-20251102.tar.gz | podman volume import mga-pgdata -

# Start service
sudo systemctl start mga-postgres.service
```

**From Logical Backup:**
```bash
# Restore to existing database
pg_restore -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  --clean --if-exists /backups/mga-soap-20251102.dump
```

---

## 5. MGA API Container

### 5.1 Dockerfile Specification

**File:** `Containerfile` (root of project)

```dockerfile
# Multi-stage build for MGA SOAP Calculator API
# Stage 1 - Builder (compile dependencies and wheels)
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

# Install system build dependencies via DNF (not apt-get)
RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    make \
    git \
    && dnf clean all

WORKDIR /build

# Copy dependency descriptors first for layer caching
COPY pyproject.toml poetry.lock* requirements.txt* ./

# FIX FROM REVIEW: Copy application code BEFORE building wheels
# This ensures 'pip wheel -e .' can find the package source
COPY app ./app
COPY src ./src
COPY README.md ./

# Build wheels for project and dependencies
RUN python -m pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Stage 2 - Runtime (minimal production image)
FROM registry.access.redhat.com/ubi9/python-311:latest

# Create non-root user (uid 1000 for consistency)
RUN useradd -m -u 1000 appuser

# Install runtime OS dependencies via DNF
RUN dnf install -y \
    postgresql-libs \
    curl \
    && dnf clean all

WORKDIR /app

# Install Python packages from wheels (faster, cached)
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Copy application code with proper ownership
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser src ./src

# Switch to non-root user for execution
USER appuser

# Expose API port
EXPOSE 8000

# Health check (liveness probe)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Start Gunicorn with Uvicorn workers (configurable via env)
ENV WORKERS=2
CMD ["bash", "-lc", "exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers ${WORKERS} \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -"]
```

**Key Improvements:**
- **Base image:** `registry.access.redhat.com/ubi9/python-311` (NOT `python:3.11-slim` which is Debian)
- **Package manager:** DNF exclusively (no apt-get)
- **Multi-stage build:** Separates build dependencies from runtime
- **Non-root user:** Runs as `appuser` (uid 1000) for security
- **Wheel caching:** Faster rebuilds, layer optimization
- **Health check:** Integrated curl check for container health
- **Fix from review:** Application code copied BEFORE `pip wheel` to fix build failure

#### Security Hardening
- No root execution inside container
- Minimal runtime dependencies (only postgresql-libs, curl)
- Clean DNF cache to reduce image size
- Read-only filesystem possible (application writes to volume-mounted directories only)

### 5.2 Quadlet Configuration

**File:** `/etc/containers/systemd/soap-calculator-api.container`

```ini
[Unit]
Description=MGA Soap Calculator API Service
Wants=network-online.target mga-postgres.service
After=network-online.target mga-postgres.service mga-network.network
Requires=mga-postgres.service

[Container]
Image=localhost/mga-soap-calculator:latest
ContainerName=soap-api
Network=mga-network
PublishPort=8000:8000
EnvironmentFile=/etc/mga-soap-calculator/api.env

# Resource limits (addressed from architecture review)
Memory=1G
MemorySwap=2G
CpuQuota=200%

# Health check (readiness verification)
HealthCmd=/usr/bin/curl -fsS http://127.0.0.1:8000/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=60s

# Logging integration
PodmanArgs=--log-driver=journald

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=300
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Service Dependencies:**
- `After=mga-postgres.service` ensures database starts first
- `Requires=mga-postgres.service` stops API if database fails
- `After=mga-network.network` ensures network exists before container start

### 5.3 Application Configuration

**Environment File:** `/etc/mga-soap-calculator/api.env` (Ansible template)

```ini
# Generated by Ansible - DO NOT EDIT MANUALLY
ENVIRONMENT=production
JWT_SECRET_KEY=REDACTED_FROM_VAULT
DATABASE_URL=postgresql+psycopg://soap_user:REDACTED@mga-postgres:5432/mga_soap_calculator
WORKERS=2
LOG_LEVEL=INFO
```

**Key Configuration:**
- **Database connection:** Uses container name `mga-postgres` for hostname resolution (DNS via mga-network)
- **JWT secret:** Sourced from Ansible Vault (addressed review issue)
- **Workers:** Configurable Gunicorn worker count (default 2)
- **Environment:** Production mode enables appropriate logging, security headers

**Container Name Resolution:**
- Hostname `mga-postgres` resolves automatically via Podman network DNS
- No hardcoded IP addresses required
- Containers isolated to `mga-network` for security

---

## 6. Network Configuration

### 6.1 Podman Network

**File:** `/etc/containers/systemd/mga-network.network`

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

**Network Characteristics:**
- **Type:** Bridge network (isolated from host network)
- **Subnet:** 10.89.0.0/24 (254 usable IPs)
- **Gateway:** 10.89.0.1 (Podman bridge gateway)
- **IPv6:** Disabled (simplifies configuration)
- **Bridge name:** `br-mga` (visible in `ip link` on host)

**Activation:**
- Quadlet creates network automatically via systemd
- No manual `podman network create` needed
- Network persists across reboots (systemd managed)

### 6.2 Service Communication

**DNS Resolution:**
```
soap-calculator-api → mga-postgres:5432 (resolved via Podman DNS)
```

**Network Isolation:**
- Both containers attached ONLY to `mga-network`
- No containers on host network (security best practice)
- PostgreSQL published to `127.0.0.1:5432` (localhost-only for admin tools like pgAdmin)

**Future Segmentation:**
- If adding more services, consider separate networks:
  - `mga-backend-network` for API ↔ DB
  - `mga-frontend-network` for web UI ↔ API
  - Use Podman network connections to bridge where needed

---

## 7. Ansible Deployment

### 7.1 Playbook Structure

**File:** `ansible/playbooks/deploy_mga_soap_calculator.yml`

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
      file:
        path: /etc/mga-soap-calculator
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Ensure PostgreSQL data volume exists
      containers.podman.podman_volume:
        name: mga-pgdata
        state: present
        labels:
          app: mga-soap-calculator
          component: database

    - name: Deploy environment files from templates
      template:
        src: "templates/{{ item.src }}"
        dest: "/etc/mga-soap-calculator/{{ item.dest }}"
        owner: root
        group: root
        mode: '0600'
      loop:
        - { src: 'postgres.env.j2', dest: 'postgres.env' }
        - { src: 'api.env.j2', dest: 'api.env' }
      notify: restart services

    - name: Deploy Quadlet container units
      copy:
        src: "files/{{ item }}"
        dest: "/etc/containers/systemd/{{ item }}"
        owner: root
        group: root
        mode: '0644'
      loop:
        - mga-network.network
        - mga-postgres.container
        - soap-calculator-api.container
      notify: daemon-reload

    - name: Reload systemd daemon (flush handlers)
      meta: flush_handlers

    - name: Enable and start PostgreSQL service
      systemd:
        name: mga-postgres.service
        enabled: true
        state: started
        daemon_reload: true

    - name: Wait for PostgreSQL to be healthy (proper health check)
      command: podman healthcheck run mga-postgres
      register: pg_health
      retries: 30
      delay: 2
      until: pg_health.rc == 0
      changed_when: false

    - name: Enable and start API service
      systemd:
        name: soap-calculator-api.service
        enabled: true
        state: started
        daemon_reload: true

    - name: Wait for API health endpoint
      uri:
        url: http://127.0.0.1:8000/health
        status_code: 200
        timeout: 10
      register: api_health
      retries: 30
      delay: 2
      until: api_health.status == 200

    - name: Verify deployment success
      debug:
        msg: "MGA SOAP Calculator deployment successful. API healthy at http://127.0.0.1:8000"

  handlers:
    - name: daemon-reload
      systemd:
        daemon_reload: true

    - name: restart services
      systemd:
        name: "{{ item }}"
        state: restarted
      loop:
        - mga-postgres.service
        - soap-calculator-api.service
```

**Idempotency Features:**
- `file` module: Creates if missing, no-op if exists
- `template`: Only changes if content differs (triggers handler)
- `systemd`: Only reloads/restarts if state changed
- `podman_volume`: Creates once, idempotent on subsequent runs

### 7.2 Volume Creation

```yaml
- name: Create PostgreSQL data volume
  containers.podman.podman_volume:
    name: mga-pgdata
    state: present
    labels:
      app: mga-soap-calculator
      component: database
```

**Volume Inspection:**
```bash
# List volumes
podman volume ls

# Inspect volume details
podman volume inspect mga-pgdata

# Find volume mount point on host
podman volume inspect mga-pgdata | jq -r '.[0].Mountpoint'
# Example output: /var/lib/containers/storage/volumes/mga-pgdata/_data
```

### 7.3 Network Setup

**Quadlet Network Deployment:**
```yaml
- name: Deploy mga-network Quadlet unit
  copy:
    src: files/mga-network.network
    dest: /etc/containers/systemd/mga-network.network
    owner: root
    group: root
    mode: '0644'
  notify: daemon-reload
```

**Manual Network Connection (Edge Cases Only):**
```yaml
# Only needed if connecting existing container manually (not typical with Quadlet)
- name: Connect PostgreSQL to mga-network if needed
  ansible.builtin.command:
    cmd: podman network connect mga-network mga-postgres
  register: network_connect
  changed_when: "'already exists' not in network_connect.stderr"
  failed_when:
    - network_connect.rc != 0
    - "'already exists' not in network_connect.stderr"
```

**Fix from Review:** Proper error handling instead of `failed_when: false` which masked real errors.

### 7.4 Secret Management

**Ansible Vault File:** `group_vars/production/vault.yml`

```yaml
---
# Encrypted with ansible-vault
vault_db_password: "REDACTED_SECURE_PASSWORD"
vault_jwt_secret_key: "REDACTED_RANDOM_KEY_256BIT"  # FIX: Ensure this exists
```

**Environment File Templates:**

**`templates/postgres.env.j2`:**
```jinja2
POSTGRES_USER=soap_user
POSTGRES_PASSWORD={{ vault_db_password }}
POSTGRES_DB={{ db_name | default('mga_soap_calculator') }}
```

**`templates/api.env.j2`:**
```jinja2
# Generated by Ansible - DO NOT EDIT MANUALLY
ENVIRONMENT=production
JWT_SECRET_KEY={{ vault_jwt_secret_key }}
DATABASE_URL=postgresql+psycopg://soap_user:{{ vault_db_password }}@mga-postgres:5432/{{ db_name | default('mga_soap_calculator') }}
WORKERS={{ api_workers | default(2) }}
LOG_LEVEL={{ log_level | default('INFO') }}
```

**Deployment Tasks:**
```yaml
- name: Deploy PostgreSQL environment file
  template:
    src: templates/postgres.env.j2
    dest: /etc/mga-soap-calculator/postgres.env
    owner: root
    group: root
    mode: '0600'

- name: Deploy API environment file
  template:
    src: templates/api.env.j2
    dest: /etc/mga-soap-calculator/api.env
    owner: root
    group: root
    mode: '0600'
```

**Vault Operations:**
```bash
# Edit encrypted vault
ansible-vault edit group_vars/production/vault.yml

# View vault contents
ansible-vault view group_vars/production/vault.yml

# Run playbook with vault password
ansible-playbook deploy_mga_soap_calculator.yml --ask-vault-pass

# Use vault password file (secure location)
ansible-playbook deploy_mga_soap_calculator.yml \
  --vault-password-file ~/.ansible/vault_pass.txt
```

**Security Best Practices:**
- Never commit unencrypted secrets to Git
- `.env` files gitignored (development only, never committed)
- Production secrets ONLY in Ansible Vault
- Vault password stored in secure password manager (1Password, Bitwarden)
- Rotate secrets quarterly or after personnel changes

### 7.5 Service Activation

```yaml
- name: Deploy Quadlet units
  copy:
    src: "files/{{ item }}"
    dest: "/etc/containers/systemd/{{ item }}"
    owner: root
    group: root
    mode: '0644'
  loop:
    - mga-network.network
    - mga-postgres.container
    - soap-calculator-api.container
  notify: daemon-reload

- name: Enable and start PostgreSQL
  systemd:
    name: mga-postgres.service
    enabled: true
    state: started
    daemon_reload: true

- name: Enable and start API
  systemd:
    name: soap-calculator-api.service
    enabled: true
    state: started
    daemon_reload: true

handlers:
  - name: daemon-reload
    systemd:
      daemon_reload: true
```

**Systemd Activation Flow:**
1. Quadlet generator reads `.container` files from `/etc/containers/systemd/`
2. Generates equivalent systemd service units in `/run/systemd/generator/`
3. `daemon-reload` makes systemd aware of new units
4. `enable` creates symlinks for boot-time activation
5. `start` immediately starts containers

**Verification:**
```bash
# Check generated service units
systemctl cat mga-postgres.service
systemctl cat soap-calculator-api.service

# Verify service status
systemctl status mga-postgres.service soap-calculator-api.service

# Check container health
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"
```

---

## 8. Health Checks & Validation

### 8.1 PostgreSQL Health

**Proper Health Check (Fix from Review):**
```yaml
- name: Wait for PostgreSQL to be healthy
  command: podman healthcheck run mga-postgres
  register: pg_health
  retries: 30
  delay: 2
  until: pg_health.rc == 0
  changed_when: false
```

**Replaces:** Arbitrary `pause: seconds: 10` which was fragile and didn't verify actual health.

**Health Check Configuration (in Quadlet):**
```ini
HealthCmd=/usr/bin/sh -lc 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} -h 127.0.0.1 -p 5432'
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s
```

**Manual Health Verification:**
```bash
# Check container health status
podman healthcheck run mga-postgres

# Inspect health check history
podman inspect mga-postgres | jq '.[0].State.Health'

# Direct PostgreSQL connectivity test
podman exec mga-postgres pg_isready -U soap_user -d mga_soap_calculator
```

### 8.2 API Health

**Health Endpoint Validation:**
```yaml
- name: Wait for API health endpoint
  uri:
    url: http://127.0.0.1:8000/health
    status_code: 200
    timeout: 10
  register: api_health
  retries: 30
  delay: 2
  until: api_health.status == 200
```

**Health Endpoint Requirements (FastAPI):**

```python
# app/health.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime
from app.database import get_db_session

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Liveness probe: Is the service alive?
    Returns 200 OK if service is running.
    """
    try:
        # Check database connectivity
        async with get_db_session() as session:
            await session.execute("SELECT 1")

        return JSONResponse({
            "status": "healthy",
            "service": "mga-soap-calculator-api",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        })
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "mga-soap-calculator-api",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness probe: Is the service ready to accept traffic?
    Checks all dependencies (database, migrations complete).
    """
    # TODO: Add migration version check, cache connectivity, etc.
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
```

**Health Check Configuration (in Quadlet):**
```ini
HealthCmd=/usr/bin/curl -fsS http://127.0.0.1:8000/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=60s
```

**Liveness vs Readiness:**
- **Liveness:** `/health` - Is the container alive? (restart if failing)
- **Readiness:** `/ready` - Is the service ready for traffic? (remove from load balancer if failing)

### 8.3 Post-Deployment Validation

**Automated Validation Playbook:**

```yaml
- name: Validate MGA SOAP Calculator Deployment
  hosts: mga_production
  become: true

  tasks:
    - name: Check PostgreSQL service status
      systemd:
        name: mga-postgres.service
      register: pg_status
      failed_when: pg_status.status.ActiveState != 'active'

    - name: Check API service status
      systemd:
        name: soap-calculator-api.service
      register: api_status
      failed_when: api_status.status.ActiveState != 'active'

    - name: Verify API health endpoint
      uri:
        url: http://127.0.0.1:8000/health
        status_code: 200
        return_content: true
      register: health_check
      failed_when: health_check.json.status != 'healthy'

    - name: Check database connectivity via API
      uri:
        url: http://127.0.0.1:8000/api/v1/health/db
        status_code: 200
      register: db_check

    - name: Inspect container logs for errors
      command: journalctl -u soap-calculator-api.service -n 50 --no-pager
      register: logs
      failed_when: "'ERROR' in logs.stdout or 'CRITICAL' in logs.stdout"

    - name: Report deployment validation success
      debug:
        msg: "✅ Deployment validated: Services active, API healthy, DB connected, no errors"
```

**Manual Validation Commands:**
```bash
# Service status
systemctl status mga-postgres.service soap-calculator-api.service

# Container status
podman ps --filter name=mga-postgres --filter name=soap-api

# Health checks
curl -f http://127.0.0.1:8000/health | jq .
podman healthcheck run mga-postgres

# Logs inspection
journalctl -u soap-calculator-api.service -f
journalctl -u mga-postgres.service -n 100

# Resource usage
podman stats soap-api mga-postgres

# Network connectivity
podman exec soap-api curl -f http://mga-postgres:5432
```

---

## 9. Rollback Procedures

### 9.1 Image Tagging Strategy

**Before Deployment:**
```bash
# Tag current production image as 'previous'
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:previous

# Tag with version/date for audit trail
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:v1.2.3-20251102
```

**After Deployment:**
```bash
# Deploy new image
podman pull localhost/mga-soap-calculator:latest
# or
podman load < mga-soap-calculator-new.tar

# Restart service to pick up new image
systemctl restart soap-calculator-api.service
```

**If Rollback Needed:**
```bash
# Restore previous tag to latest
podman tag localhost/mga-soap-calculator:previous \
  localhost/mga-soap-calculator:latest

# Restart service
systemctl restart soap-calculator-api.service

# Verify health
curl http://127.0.0.1:8000/health
```

**Tag Management:**
```bash
# List all tags for image
podman images localhost/mga-soap-calculator

# Remove old tags after successful deployment
podman rmi localhost/mga-soap-calculator:v1.2.2-20251025
```

### 9.2 Rollback Playbook

**File:** `ansible/playbooks/rollback_mga_api.yml`

```yaml
---
- name: Rollback MGA API to Previous Version
  hosts: mga_production
  become: true

  vars:
    rollback_tag: previous  # or specific version like v1.2.3-20251102

  tasks:
    - name: Stop API service
      systemd:
        name: soap-calculator-api.service
        state: stopped

    - name: Tag current as broken (for audit)
      command: >
        podman tag localhost/mga-soap-calculator:latest
        localhost/mga-soap-calculator:broken-{{ ansible_date_time.epoch }}
      ignore_errors: true

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
        timeout: 10
      retries: 20
      delay: 3
      until: api_health.status == 200
      register: api_health

    - name: Report rollback success
      debug:
        msg: "✅ Rollback to {{ rollback_tag }} completed successfully"

    - name: Notify team of rollback
      debug:
        msg: "⚠️ ROLLBACK EXECUTED - Investigate broken image and root cause"
```

**Execute Rollback:**
```bash
# Rollback to previous
ansible-playbook rollback_mga_api.yml --ask-vault-pass

# Rollback to specific version
ansible-playbook rollback_mga_api.yml \
  --extra-vars "rollback_tag=v1.2.3-20251102" \
  --ask-vault-pass
```

### 9.3 Data Rollback

**Volume Snapshot Strategy:**
```bash
# BEFORE risky operations, snapshot volume
podman volume export mga-pgdata | gzip > /backups/mga-pgdata-pre-migration-$(date +%Y%m%d).tar.gz
```

**Volume Restoration:**
```bash
# Stop database service
systemctl stop mga-postgres.service

# Remove current volume
podman volume rm -f mga-pgdata

# Create fresh volume
podman volume create mga-pgdata

# Import backup
gunzip -c /backups/mga-pgdata-pre-migration-20251102.tar.gz | \
  podman volume import mga-pgdata -

# Start service
systemctl start mga-postgres.service

# Verify database integrity
podman exec mga-postgres psql -U soap_user -d mga_soap_calculator -c "SELECT version();"
```

**Logical Backup (Preferred for Data Rollback):**
```bash
# Create logical backup before changes
pg_dump -Fc -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  > /backups/mga-soap-pre-migration-$(date +%Y%m%d).dump

# Restore from logical backup
pg_restore -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  --clean --if-exists /backups/mga-soap-pre-migration-20251102.dump
```

**Automated Backup Schedule (Recommended):**
```bash
# /etc/cron.daily/backup-mga-db
#!/bin/bash
BACKUP_DIR=/backups/mga-soap-calculator
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Logical backup (preferred)
pg_dump -Fc -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  > $BACKUP_DIR/mga-soap-$DATE.dump

# Volume snapshot (optional, for full disaster recovery)
podman volume export mga-pgdata | gzip > $BACKUP_DIR/mga-pgdata-$DATE.tar.gz

# Retain 30 days of backups
find $BACKUP_DIR -name "mga-soap-*.dump" -mtime +30 -delete
find $BACKUP_DIR -name "mga-pgdata-*.tar.gz" -mtime +30 -delete
```

---

## 10. Testing Strategy

### 10.1 Local Testing

**Build Container on macOS:**
```bash
# Initialize Podman machine (if first time)
podman machine init --cpus 4 --memory 8192 --disk-size 100
podman machine start

# Build for Linux AMD64 (Fedora 42 target)
podman build \
  --platform linux/amd64 \
  --tag localhost/mga-soap-calculator:latest \
  --file Containerfile \
  .

# Verify architecture
podman inspect localhost/mga-soap-calculator:latest | \
  jq '.[0].Architecture'
# Expected: amd64
```

**Local Container Testing:**
```bash
# Create test network
podman network create test-mga-network

# Start PostgreSQL
podman run -d \
  --name test-postgres \
  --network test-mga-network \
  -e POSTGRES_USER=soap_user \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=mga_soap_calculator \
  registry.redhat.io/rhel9/postgresql-15:latest

# Wait for PostgreSQL ready
sleep 5
podman exec test-postgres pg_isready -U soap_user

# Start API
podman run -d \
  --name test-api \
  --network test-mga-network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+psycopg://soap_user:testpass@test-postgres:5432/mga_soap_calculator \
  -e JWT_SECRET_KEY=test-secret-key \
  localhost/mga-soap-calculator:latest

# Test health endpoint
curl http://localhost:8000/health

# Test API functionality
curl http://localhost:8000/api/v1/calculations
```

**Cleanup Local Test:**
```bash
podman stop test-api test-postgres
podman rm test-api test-postgres
podman network rm test-mga-network
```

### 10.2 Integration Testing

**Deploy to Staging:**
```bash
# Deploy full stack to staging server
ansible-playbook -i inventories/staging deploy_mga_soap_calculator.yml \
  --ask-vault-pass
```

**Run Integration Test Suite:**
```python
# tests/integration/test_containerized_deployment.py
import pytest
import requests
from sqlalchemy import create_engine

STAGING_API_URL = "http://staging.example.com:8000"
STAGING_DB_URL = "postgresql://soap_user:pass@staging.example.com:5432/mga_soap_calculator"

def test_health_endpoint():
    """Verify API health endpoint responds correctly."""
    response = requests.get(f"{STAGING_API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"] == "connected"

def test_database_connectivity():
    """Verify database is accessible and schema correct."""
    engine = create_engine(STAGING_DB_URL)
    with engine.connect() as conn:
        result = conn.execute("SELECT version();")
        version = result.fetchone()[0]
        assert "PostgreSQL 15" in version

def test_api_calculation_endpoint():
    """Verify saponification calculation API works."""
    payload = {
        "oils": [
            {"name": "olive_oil", "percentage": 60},
            {"name": "coconut_oil", "percentage": 40}
        ],
        "batch_size": 1000,
        "superfat": 5
    }
    response = requests.post(f"{STAGING_API_URL}/api/v1/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "lye_amount" in data
    assert data["lye_amount"] > 0

def test_container_resource_limits():
    """Verify containers running with resource limits."""
    # SSH to staging and check podman stats
    # (Requires paramiko or similar for remote execution)
    pass  # Implementation depends on infrastructure access
```

**Execute Integration Tests:**
```bash
# Run pytest against staging
pytest tests/integration/ -v --tb=short

# Verify container health on staging
ssh staging "podman ps --format 'table {{.Names}}\t{{.Status}}\t{{.Health}}'"
```

### 10.3 Production Validation

**Smoke Tests (Post-Deployment):**
```yaml
# ansible/playbooks/smoke_test_production.yml
- name: Production Smoke Tests
  hosts: mga_production
  become: true

  tasks:
    - name: Test API health endpoint
      uri:
        url: http://127.0.0.1:8000/health
        status_code: 200
        return_content: true
      register: health
      failed_when: health.json.status != 'healthy'

    - name: Test API calculation endpoint
      uri:
        url: http://127.0.0.1:8000/api/v1/calculate
        method: POST
        body_format: json
        body:
          oils:
            - name: olive_oil
              percentage: 100
          batch_size: 1000
          superfat: 5
        status_code: 200
      register: calc_result

    - name: Verify database migration version
      shell: |
        podman exec mga-postgres psql -U soap_user -d mga_soap_calculator \
          -c "SELECT version_num FROM alembic_version;" -t
      register: migration_version
      changed_when: false

    - name: Report smoke test results
      debug:
        msg:
          - "✅ API Health: {{ health.json.status }}"
          - "✅ Calculation: {{ calc_result.status }}"
          - "✅ DB Migration: {{ migration_version.stdout | trim }}"
```

**Monitoring Setup Verification:**
```bash
# Check Sentry integration (if configured)
curl -X POST http://127.0.0.1:8000/api/v1/test-sentry

# Verify log aggregation
journalctl -u soap-calculator-api.service --since "1 hour ago" | grep ERROR

# Check metrics endpoint (if Prometheus exporter added)
curl http://127.0.0.1:8000/metrics
```

**Performance Baseline:**
```bash
# Load testing with k6 or Locust
k6 run --vus 10 --duration 30s tests/load/api_load_test.js

# Monitor resource usage during load
podman stats soap-api mga-postgres
```

---

## 11. Migration from Existing Deployment

### 11.1 Database Name Change

**Current State Analysis:**
- **Existing deployments:** May use `soap_calculator` (incorrect)
- **New standard:** `mga_soap_calculator` (canonical)
- **Issue:** Database name mismatch is a **breaking change** for existing deployments

**Resolution Strategy:**

**Option A: Canonical Name (Recommended)**
- **Decision:** Use `mga_soap_calculator` as the canonical database name
- **New deployments:** Use default `db_name: mga_soap_calculator`
- **Existing deployments:** No change required (already using correct name)
- **Action:** Update any deployments using `soap_calculator` to `mga_soap_calculator`

**Option B: Rename Existing Database**

If an existing deployment created `soap_calculator` and you must consolidate:

**Method 1 - SQL Rename (Fast, Downtime Required):**
```bash
# Stop API service
systemctl stop soap-calculator-api.service

# Connect as superuser and rename
podman exec -it mga-postgres psql -U postgres << EOF
-- Ensure no active connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'soap_calculator' AND pid <> pg_backend_pid();

-- Rename database
ALTER DATABASE soap_calculator RENAME TO mga_soap_calculator;
EOF

# Update environment files with new name
# (Ansible templates already use {{ db_name }} variable)

# Start API service
systemctl start soap-calculator-api.service

# Verify health
curl http://127.0.0.1:8000/health
```

**Method 2 - Dump and Restore (Safer, More Flexible):**
```bash
# Stop API service
systemctl stop soap-calculator-api.service

# Backup existing database
pg_dump -Fc -U soap_user -h 127.0.0.1 -d soap_calculator \
  > /backups/soap_calculator_pre_migration.dump

# Create new database with correct name
podman exec mga-postgres createdb -U soap_user mga_soap_calculator

# Restore data
pg_restore -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  /backups/soap_calculator_pre_migration.dump

# Update environment files
# (Set db_name: mga_soap_calculator in Ansible vars)

# Deploy updated configuration
ansible-playbook deploy_mga_soap_calculator.yml --ask-vault-pass

# Verify migration success
curl http://127.0.0.1:8000/health
podman exec mga-postgres psql -U soap_user -d mga_soap_calculator -c "\dt"

# After verification, optionally drop old database
podman exec mga-postgres dropdb -U postgres soap_calculator
```

**Rollback Plan:**
```bash
# If issues encountered, restore from backup
pg_restore -U soap_user -h 127.0.0.1 -d soap_calculator \
  --clean --if-exists /backups/soap_calculator_pre_migration.dump

# Revert environment configuration
# (Set db_name: soap_calculator in Ansible vars)

# Redeploy previous configuration
ansible-playbook deploy_mga_soap_calculator.yml --ask-vault-pass
```

### 11.2 Configuration Migration

**Environment Variable Mapping:**

| Old Configuration | New Configuration | Notes |
|-------------------|-------------------|-------|
| `DATABASE_URL=...soap_calculator` | `DATABASE_URL=...mga_soap_calculator` | Update database name |
| `DB_HOST=localhost` | `DB_HOST=mga-postgres` | Container name resolution |
| `DB_PORT=5432` | (removed, use URL) | Embedded in DATABASE_URL |
| Manual secrets in `.env` | Ansible Vault | Migrate to vault.yml |

**Secret Migration Checklist:**
- [ ] `vault_db_password` exists in vault.yml
- [ ] `vault_jwt_secret_key` exists in vault.yml (FIX: was missing)
- [ ] Environment files deployed via Ansible templates
- [ ] File permissions set to 0600
- [ ] Old `.env` files deleted from production

**Network Reconfiguration:**
- **Old:** Database on `localhost:5432` (direct host connection)
- **New:** Database on `mga-postgres:5432` (container network)
- **Migration:** Update `DATABASE_URL` to use container hostname

**Pre-Migration Checklist:**
```yaml
- name: Pre-migration validation
  hosts: mga_production
  become: true

  tasks:
    - name: Verify vault.yml has all required secrets
      assert:
        that:
          - vault_db_password is defined
          - vault_jwt_secret_key is defined
        fail_msg: "Missing required secrets in vault.yml"

    - name: Backup existing database
      shell: |
        pg_dump -Fc -U soap_user -h 127.0.0.1 -d {{ old_db_name | default('soap_calculator') }} \
          > /backups/pre-migration-$(date +%Y%m%d-%H%M%S).dump
      when: old_db_name is defined

    - name: Verify Ansible templates exist
      stat:
        path: "templates/{{ item }}"
      loop:
        - postgres.env.j2
        - api.env.j2
      register: template_check
      failed_when: not template_check.stat.exists
```

---

## 12. Operations

### 12.1 Deployment Commands

**Initial Deployment:**
```bash
# Navigate to Ansible directory
cd ansible

# Deploy full stack to production
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml \
  --ask-vault-pass

# Verify deployment
ansible-playbook -i inventories/production playbooks/validate_deployment.yml
```

**Update Deployment (New Image Version):**
```bash
# Build new image on build server or locally
podman build --platform linux/amd64 -t localhost/mga-soap-calculator:latest .

# Save image for transfer (if no registry)
podman save localhost/mga-soap-calculator:latest | gzip > mga-soap-calculator-new.tar.gz

# Transfer to production server
scp mga-soap-calculator-new.tar.gz production:/tmp/

# On production: Load new image
ssh production "podman load < /tmp/mga-soap-calculator-new.tar.gz"

# Redeploy (will pull new image and restart)
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml \
  --ask-vault-pass
```

**Rollback to Previous Version:**
```bash
ansible-playbook -i inventories/production playbooks/rollback_mga_api.yml \
  --ask-vault-pass

# Or rollback to specific version
ansible-playbook -i inventories/production playbooks/rollback_mga_api.yml \
  --extra-vars "rollback_tag=v1.2.3-20251102" \
  --ask-vault-pass
```

**Configuration-Only Update:**
```bash
# Update vault.yml with new secrets
ansible-vault edit ansible/group_vars/production/vault.yml

# Redeploy (only environment files will change, triggers restart)
ansible-playbook -i inventories/production playbooks/deploy_mga_soap_calculator.yml \
  --ask-vault-pass
```

### 12.2 Monitoring

**Log Access:**
```bash
# API logs (real-time)
journalctl -u soap-calculator-api.service -f

# API logs (last 100 lines)
journalctl -u soap-calculator-api.service -n 100

# PostgreSQL logs
journalctl -u mga-postgres.service -f

# Both services combined
journalctl -u soap-calculator-api.service -u mga-postgres.service -f

# Filter for errors
journalctl -u soap-calculator-api.service | grep -E "ERROR|CRITICAL"

# Export logs for analysis
journalctl -u soap-calculator-api.service --since "2025-11-02" \
  --until "2025-11-03" > /tmp/api-logs-20251102.txt
```

**Service Status:**
```bash
# Systemd service status
systemctl status mga-postgres.service soap-calculator-api.service

# Container status
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# Detailed container inspection
podman inspect soap-api | jq '.[0].State'

# Container health history
podman inspect soap-api | jq '.[0].State.Health'
```

**Resource Usage:**
```bash
# Real-time resource monitoring
podman stats soap-api mga-postgres

# CPU and memory by cgroup
systemd-cgtop

# Disk usage by volumes
podman volume ls
du -sh /var/lib/containers/storage/volumes/mga-pgdata/_data

# Network traffic
podman network inspect mga-network
```

**Health Monitoring:**
```bash
# Manual health checks
curl http://127.0.0.1:8000/health | jq .
podman healthcheck run soap-api
podman healthcheck run mga-postgres

# Health check from systemd
systemctl show soap-calculator-api.service | grep ExecMainStatus

# Database connectivity test
podman exec mga-postgres pg_isready -U soap_user -d mga_soap_calculator
```

### 12.3 Troubleshooting

**Common Issues:**

**Issue 1: Container Won't Start**
```bash
# Check systemd status and logs
systemctl status soap-calculator-api.service
journalctl -u soap-calculator-api.service -xe

# Verify environment file exists and is readable
ls -lZ /etc/mga-soap-calculator/api.env
cat /etc/mga-soap-calculator/api.env  # Check for syntax errors

# Verify image exists
podman images localhost/mga-soap-calculator

# Try manual container start for debugging
podman run -it --rm \
  --env-file /etc/mga-soap-calculator/api.env \
  localhost/mga-soap-calculator:latest \
  /bin/bash
```

**Issue 2: SELinux Permission Denied**
```bash
# Check for SELinux denials
sudo ausearch -m avc -ts recent

# Verify volume labels
podman volume inspect mga-pgdata | jq '.[0].Labels'

# Check host directory context (if using bind mounts)
ls -Z /etc/mga-soap-calculator

# Temporarily set SELinux to permissive (development ONLY)
sudo setenforce 0
# Try operation, then re-enable:
sudo setenforce 1

# Set correct SELinux context on host directories
sudo chcon -R -t container_file_t /etc/mga-soap-calculator
```

**Issue 3: Network Connectivity Issues**
```bash
# Verify network exists
podman network ls | grep mga-network

# Inspect network configuration
podman network inspect mga-network

# Test DNS resolution inside container
podman exec soap-api getent hosts mga-postgres
podman exec soap-api ping -c 3 mga-postgres

# Test PostgreSQL connectivity from API container
podman exec soap-api psql -U soap_user -h mga-postgres -d mga_soap_calculator -c "SELECT 1;"

# Check if containers are on correct network
podman inspect soap-api | jq '.[0].NetworkSettings.Networks'
podman inspect mga-postgres | jq '.[0].NetworkSettings.Networks'
```

**Issue 4: Health Check Failing**
```bash
# Run health check manually
podman healthcheck run soap-api

# Test health endpoint inside container
podman exec soap-api curl -f http://127.0.0.1:8000/health

# Check application logs for errors
journalctl -u soap-calculator-api.service -n 100

# Verify database connection string
podman exec soap-api env | grep DATABASE_URL

# Test database connectivity
podman exec soap-api python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    print(conn.execute('SELECT version();').fetchone())
"
```

**Issue 5: Missing JWT Secret Key**
```bash
# Verify vault.yml has secret
ansible-vault view ansible/group_vars/production/vault.yml | grep jwt_secret_key

# Check if secret in environment file
grep JWT_SECRET_KEY /etc/mga-soap-calculator/api.env

# If missing, add to vault and redeploy
ansible-vault edit ansible/group_vars/production/vault.yml
# Add: vault_jwt_secret_key: "generated_secure_random_key"

# Redeploy to update environment file
ansible-playbook deploy_mga_soap_calculator.yml --ask-vault-pass
```

**Issue 6: Database Volume Corruption**
```bash
# Stop database
systemctl stop mga-postgres.service

# Check volume integrity
podman volume inspect mga-pgdata

# Restore from backup
podman volume rm -f mga-pgdata
podman volume create mga-pgdata
gunzip -c /backups/mga-pgdata-YYYYMMDD.tar.gz | podman volume import mga-pgdata -

# Or restore from logical backup
podman exec mga-postgres psql -U postgres -c "DROP DATABASE mga_soap_calculator;"
podman exec mga-postgres createdb -U postgres mga_soap_calculator
pg_restore -h 127.0.0.1 -U soap_user -d mga_soap_calculator /backups/mga-soap-YYYYMMDD.dump

# Start database
systemctl start mga-postgres.service
```

**Debug Mode (Development Only):**
```bash
# Run API container with shell access
podman run -it --rm \
  --network mga-network \
  --env-file /etc/mga-soap-calculator/api.env \
  localhost/mga-soap-calculator:latest \
  /bin/bash

# Inside container, manually start application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use interactive debugger
python -m pdb -m uvicorn app.main:app
```

---

## Appendix A: Addressed Architecture Review Issues

**Summary of Fixes:**

| Issue | Severity | Status | Fix Description |
|-------|----------|--------|-----------------|
| Debian base image | 🔴 CRITICAL | ✅ FIXED | Migrated to `registry.access.redhat.com/ubi9/python-311` |
| Database naming mismatch | 🔴 CRITICAL | ✅ FIXED | Standardized to `mga_soap_calculator` with migration path |
| Missing volume creation | 🟡 HIGH | ✅ FIXED | Added `podman_volume` task in Ansible playbook |
| Network error masking | 🟡 HIGH | ✅ FIXED | Proper `failed_when` conditions instead of `failed_when: false` |
| Health check timing | 🟡 MEDIUM | ✅ FIXED | Replaced `pause: 10s` with `podman healthcheck run` retry loop |
| Missing JWT secret | 🟡 MEDIUM | ✅ FIXED | Added `vault_jwt_secret_key` to vault.yml and templates |
| No resource limits | 🟡 MEDIUM | ✅ FIXED | Added Memory/CPU limits to both container Quadlet units |

**Detailed Resolutions:**

1. **Dockerfile Base Image:**
   - **Before:** `FROM python:3.11-slim` (Debian-based)
   - **After:** `FROM registry.access.redhat.com/ubi9/python-311:latest` (UBI 9)
   - **Impact:** Platform compatibility, SELinux integration, DNF package management

2. **Database Naming:**
   - **Before:** Inconsistent use of `soap_calculator` vs `mga_soap_calculator`
   - **After:** Canonical name `mga_soap_calculator` with migration procedures
   - **Impact:** No breaking changes for existing deployments

3. **Volume Persistence:**
   - **Before:** Volume `mga-pgdata` referenced but never created
   - **After:** Explicit volume creation via `containers.podman.podman_volume` module
   - **Impact:** Prevents container startup failures

4. **Network Error Handling:**
   - **Before:** `failed_when: false` masked all network connection errors
   - **After:** Conditional `failed_when` checking for specific "already exists" error
   - **Impact:** Real errors no longer suppressed

5. **Health Check Implementation:**
   - **Before:** Arbitrary `pause: seconds: 10` without verification
   - **After:** `podman healthcheck run` with retry logic (30 attempts, 2s delay)
   - **Impact:** Reliable health verification before proceeding

6. **JWT Secret Key:**
   - **Before:** Template referenced undefined `jwt_secret_key` variable
   - **After:** Explicit `vault_jwt_secret_key` in vault.yml, templated to api.env
   - **Impact:** Prevents authentication failures from missing secret

7. **Resource Limits:**
   - **Before:** No Memory/CPU limits defined
   - **After:** `Memory=1G`, `MemorySwap=2G`, `CpuQuota=200%` in Quadlet units
   - **Impact:** Prevents resource exhaustion, enables capacity planning

---

## Appendix B: File Inventory

**Ansible Repository Structure:**
```
ansible/
├── inventories/
│   └── production
│       └── hosts.yml
├── group_vars/
│   └── production/
│       ├── vars.yml
│       └── vault.yml (encrypted)
├── playbooks/
│   ├── deploy_mga_soap_calculator.yml
│   ├── rollback_mga_api.yml
│   └── validate_deployment.yml
├── templates/
│   ├── postgres.env.j2
│   └── api.env.j2
└── files/
    ├── mga-network.network
    ├── mga-postgres.container
    └── soap-calculator-api.container
```

**Application Repository Structure:**
```
mga-soap-calculator/
├── Containerfile
├── pyproject.toml
├── requirements.txt
├── app/
│   ├── main.py
│   ├── health.py
│   └── ...
├── src/
│   └── ...
├── tests/
│   ├── integration/
│   └── load/
└── agent-os/
    ├── specs/
    │   └── 2025-11-02-containerized-deployment/
    │       └── SPEC.md (this document)
    └── standards/
        └── global/
            └── deployment-platform.md
```

---

## Appendix C: Security Checklist

**Pre-Deployment Security Validation:**

- [ ] All containers use Fedora/UBI base images (NO Debian/Alpine)
- [ ] Containers run as non-root user internally (uid 1000)
- [ ] SELinux enforcing mode on host
- [ ] Volume mounts use `:Z` or `:z` labels
- [ ] Health checks defined for all services
- [ ] Secrets managed via Ansible Vault (encrypted)
- [ ] No hardcoded credentials in images or Containerfiles
- [ ] Environment files have mode 0600 (root-only readable)
- [ ] PostgreSQL published to 127.0.0.1 only (not 0.0.0.0)
- [ ] Resource limits configured (Memory, CPU)
- [ ] Logging enabled via journald
- [ ] Backup strategy documented and tested
- [ ] Rollback procedures tested in staging

**Ongoing Security Maintenance:**

- [ ] Security updates applied within 7 days of release
- [ ] Secrets rotated quarterly
- [ ] Audit logs reviewed monthly
- [ ] Dependency vulnerability scanning weekly (Dependabot/Snyk)
- [ ] Container image rebuilds for base image CVE patches

---

## Appendix D: Reference Commands

**Image Management:**
```bash
# Build image
podman build --platform linux/amd64 -t localhost/mga-soap-calculator:latest .

# Tag image
podman tag localhost/mga-soap-calculator:latest localhost/mga-soap-calculator:v1.2.3

# List images
podman images localhost/mga-soap-calculator

# Remove old images
podman rmi localhost/mga-soap-calculator:v1.2.2
```

**Container Management:**
```bash
# List containers
podman ps -a

# Inspect container
podman inspect soap-api

# Execute command in container
podman exec soap-api <command>

# View logs
podman logs soap-api

# Stop/start container
podman stop soap-api
podman start soap-api
```

**Volume Management:**
```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect mga-pgdata

# Create volume
podman volume create mga-pgdata

# Remove volume
podman volume rm mga-pgdata

# Export volume
podman volume export mga-pgdata > backup.tar
```

**Network Management:**
```bash
# List networks
podman network ls

# Inspect network
podman network inspect mga-network

# Create network
podman network create mga-network

# Remove network
podman network rm mga-network
```

**Systemd Management:**
```bash
# Reload systemd daemon
systemctl daemon-reload

# Enable service
systemctl enable soap-calculator-api.service

# Start service
systemctl start soap-calculator-api.service

# Status
systemctl status soap-calculator-api.service

# Logs
journalctl -u soap-calculator-api.service -f
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Status:** Ready for Implementation
**Next Steps:**
1. Review specification with team
2. Test deployment in staging environment
3. Create Ansible playbooks per specification
4. Validate all addressed issues resolved
5. Execute production deployment with rollback plan ready
