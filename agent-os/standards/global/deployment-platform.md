# Deployment Platform Standards

Complete deployment platform specifications for MGA Soap Calculator containerized services.

---

## Target Platform

### Production Environment
- **Operating System:** Fedora 42 Linux
- **Architecture:** x86_64 (AMD64)
- **Kernel:** Linux 6.x+ with cgroups v2 support
- **Init System:** systemd 255+
- **Security:** SELinux in enforcing mode

### Development Environment
- **Build Platform:** macOS (Apple Silicon or Intel)
- **Target Compatibility:** All containers must be platform-independent or multi-arch
- **Testing:** Local Podman testing before production deployment

---

## Container Runtime

### Podman (NOT Docker)

**Primary Container Runtime:** Podman 4.9+

**Rationale:**
- **Daemonless Architecture:** No central daemon process, improved security
- **Rootless Support:** Run containers as non-root user without privileged daemon
- **systemd Integration:** Native integration via Quadlet for production-grade orchestration
- **OCI Compliance:** Full compatibility with OCI (Open Container Initiative) standards
- **Drop-in Replacement:** Compatible with Docker CLI syntax, minimal migration friction
- **SELinux Integration:** First-class support for Fedora's SELinux enforcing mode
- **Red Hat Ecosystem:** Primary container runtime for RHEL/Fedora, enterprise-ready
- **Security:** Runs containers without requiring root privileges (rootless mode)

**Explicitly NOT Docker Because:**
- Docker requires privileged daemon (security concern)
- Docker licensing changes create uncertainty for production use
- Podman is Fedora/RHEL native and better integrated with systemd
- Docker-compose compatibility exists via podman-compose if needed

### Container Engine Configuration

**Podman Configuration** (`/etc/containers/storage.conf`):
```toml
[storage]
driver = "overlay"
graphroot = "/var/lib/containers/storage"

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

**Container Registry Configuration** (`/etc/containers/registries.conf`):
```toml
unqualified-search-registries = ["docker.io", "quay.io", "registry.fedoraproject.org"]

[[registry]]
location = "docker.io"
insecure = false

[[registry]]
location = "quay.io"
insecure = false
```

---

## Orchestration: Quadlet (systemd Integration)

### Quadlet Overview

**Orchestration Method:** Quadlet (Podman's systemd generator)

**Rationale:**
- **systemd Native:** Containers managed as systemd units (services, not external orchestrator)
- **Production Reliability:** Systemd's proven process supervision and dependency management
- **Service Integration:** Containers participate in systemd dependency graph
- **Logging Integration:** Journald captures container logs automatically
- **Resource Management:** systemd cgroups for CPU/memory limits
- **Automatic Restart:** systemd handles container restart policies
- **No External Dependencies:** No Docker Compose, Kubernetes, or Swarm needed for single-server deployment

**NOT Using docker-compose Because:**
- Quadlet provides native systemd integration
- systemd is already present and proven on Fedora
- Better system-level orchestration (restart, dependencies, ordering)
- podman-compose exists if compose syntax needed, but Quadlet preferred

### Quadlet Unit File Structure

**Location:** `/etc/containers/systemd/` or `~/.config/containers/systemd/` (rootless)

**File Extension:** `.container` for container units, `.volume` for volumes, `.network` for networks

**Example Quadlet Container Unit** (`soap-calculator-api.container`):
```ini
[Unit]
Description=MGA Soap Calculator API Service
After=postgresql.service
Requires=postgresql.service
Wants=network-online.target
After=network-online.target

[Container]
Image=localhost/mga-soap-calculator:latest
ContainerName=soap-api
PublishPort=8000:8000
Environment=DATABASE_URL=postgresql://user:pass@db:5432/soap_calc
Volume=soap-data:/app/data:Z
HealthCmd=/usr/bin/curl -f http://localhost:8000/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
AutoUpdate=registry
PodmanArgs=--log-driver=journald --security-opt=label=type:container_runtime_t

[Service]
Restart=always
RestartSec=10
TimeoutStartSec=300
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Quadlet Volume Unit** (`soap-data.volume`):
```ini
[Volume]
VolumeName=soap-data
Label=app=soap-calculator
```

**Activation:**
```bash
# System-wide (rootful)
sudo systemctl daemon-reload
sudo systemctl enable --now soap-calculator-api.service

# User (rootless)
systemctl --user daemon-reload
systemctl --user enable --now soap-calculator-api.service
```

---

## Base Images: Fedora/UBI ONLY

### Approved Base Images

**CRITICAL REQUIREMENT:** All containers MUST use Fedora or Red Hat Universal Base Images (UBI).

**Approved Base Images:**
1. **Fedora Official** (`registry.fedoraproject.org/fedora:42`)
   - Latest Fedora release for maximum compatibility with deployment platform
   - Use for services requiring cutting-edge packages

2. **Red Hat UBI 9** (`registry.access.redhat.com/ubi9/ubi:latest`)
   - Enterprise stability, longer support lifecycle
   - Use for production services prioritizing stability

3. **Python UBI** (`registry.access.redhat.com/ubi9/python-311:latest`)
   - Python 3.11+ with UBI base
   - Preferred for FastAPI backend services

4. **Node.js UBI** (`registry.access.redhat.com/ubi9/nodejs-20:latest`)
   - Node.js 20 LTS with UBI base
   - Use for any Node.js services

**EXPLICITLY FORBIDDEN:**
- ❌ Debian-based images (`debian:*`, `ubuntu:*`)
- ❌ Alpine Linux (`alpine:*`) - musl libc incompatibilities
- ❌ Generic `python:*` images (usually Debian-based)
- ❌ Generic `node:*` images (usually Debian-based)

**Rationale:**
- **Platform Compatibility:** Fedora containers run natively on Fedora 42 host
- **Package Manager Consistency:** DNF everywhere, no apt-get confusion
- **SELinux Labels:** Fedora/UBI images properly configured for SELinux
- **Dependency Matching:** glibc, OpenSSL, systemd versions match host
- **Security Updates:** Red Hat/Fedora security pipeline
- **Enterprise Support:** UBI images backed by Red Hat

### Package Manager: DNF (NOT apt-get)

**Container Package Management:**
```dockerfile
# CORRECT: DNF for Fedora/UBI images
RUN dnf install -y python3-pip python3-devel && dnf clean all

# WRONG: apt-get (indicates wrong base image)
# RUN apt-get update && apt-get install -y python3-pip
```

**Python Dependency Installation:**
```dockerfile
# Install system dependencies via DNF
RUN dnf install -y gcc python3-devel postgresql-devel && dnf clean all

# Install Python packages via pip
RUN pip install --no-cache-dir -r requirements.txt
```

---

## SELinux: Enforcing Mode

### SELinux Configuration

**Enforcement Mode:** Enforcing (production requirement)

**Podman SELinux Integration:**
Podman automatically applies SELinux labels to containers. Volume mounts require explicit labeling.

**Volume Label Flags:**
- `:Z` (private unshared) - Relabel volume for exclusive container access
- `:z` (shared) - Relabel volume for shared multi-container access

**Example Volume Mounts:**
```bash
# Private volume (recommended for single-container data)
podman run -v /host/data:/container/data:Z my-image

# Shared volume (multiple containers access same data)
podman run -v /shared/data:/container/data:z my-image
```

**Quadlet Volume Labeling:**
```ini
[Container]
Volume=/host/path:/container/path:Z  # Private label
Volume=/shared:/container/shared:z    # Shared label
```

**Debugging SELinux Issues:**
```bash
# Check AVC denials
sudo ausearch -m avc -ts recent

# Temporarily set SELinux to permissive (development only)
sudo setenforce 0

# Check SELinux context on host path
ls -Z /host/data

# Set SELinux context manually if needed
sudo chcon -R -t container_file_t /host/data
```

---

## Rootful vs Rootless Decision

### Default: Rootful (System Services)

**Recommendation:** Rootful Podman for production API services

**Rationale:**
- **Privileged Ports:** Bind to ports <1024 (8000 mapped to 80/443 via reverse proxy, but systemd socket activation simpler)
- **systemd Integration:** Cleaner integration with system-level services (PostgreSQL, nginx)
- **Resource Limits:** Better cgroup management for production workloads
- **Persistence:** System services survive user logout
- **Backup/Monitoring:** System-level tools have full access

**Configuration:**
- Containers run as root initially, then drop privileges internally (non-root user in container)
- SELinux provides mandatory access control regardless of user
- Security hardening via systemd sandboxing options (PrivateTmp, NoNewPrivileges, etc.)

**Rootless Use Cases:**
- Development/testing on shared systems
- User-specific services (personal development containers)
- Multi-tenant environments where isolation from root is required

### Container Internal Security

**CRITICAL:** Even with rootful Podman, containers should run as non-root internally.

**Dockerfile Best Practice:**
```dockerfile
FROM registry.access.redhat.com/ubi9/python-311:latest

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install dependencies as root
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Switch to non-root user
USER appuser
WORKDIR /app

# Copy application (owned by appuser)
COPY --chown=appuser:appuser . /app/

# Run as non-root
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Network Architecture

### Container Networking Strategy

**Default Network Mode:** Bridge networking with custom networks

**Network Configuration:**

**Create Custom Network (Quadlet):**
```ini
# /etc/containers/systemd/soap-network.network
[Network]
NetworkName=soap-network
Driver=bridge
Subnet=10.89.0.0/24
Gateway=10.89.0.1
IPv6=false

[Network.Options]
com.docker.network.bridge.name=br-soap
```

**Attach Containers to Network:**
```ini
[Container]
Network=soap-network
```

**Service Discovery:**
- Containers on same network resolve each other by container name
- `postgresql` container accessible as `postgresql:5432` from API container

**Host Network (Avoid):**
```ini
# Avoid unless necessary (debugging, performance critical)
[Container]
Network=host  # Container uses host's network namespace
```

**Port Publishing:**
```ini
[Container]
PublishPort=8000:8000  # host:container
PublishPort=127.0.0.1:5432:5432  # Localhost-only PostgreSQL
```

**Reverse Proxy Integration:**
- nginx/Caddy on host listens on 80/443
- Proxies to `localhost:8000` (API container published port)
- TLS termination at reverse proxy layer

---

## Volume Management

### Persistent Data Strategy

**Volume Types:**
1. **Named Volumes** (Podman-managed, preferred for databases)
2. **Bind Mounts** (Host directories, for configuration/logs)

**Quadlet Volume Definitions:**

**Named Volume (Podman-managed):**
```ini
# /etc/containers/systemd/postgres-data.volume
[Volume]
VolumeName=postgres-data
Label=app=soap-calculator
Label=component=database
```

**Usage in Container:**
```ini
[Container]
Volume=postgres-data:/var/lib/postgresql/data:Z
```

**Bind Mount (Host Directory):**
```ini
[Container]
Volume=/etc/soap-calculator:/app/config:ro,Z  # Read-only config
Volume=/var/log/soap-calculator:/app/logs:Z   # Writable logs
```

**Volume Backup Strategy:**
```bash
# Backup named volume
podman volume export postgres-data > postgres-data-backup.tar

# Restore named volume
podman volume import postgres-data postgres-data-backup.tar

# Backup bind mount
rsync -av /var/log/soap-calculator/ /backup/logs/
```

**Volume Inspection:**
```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect postgres-data

# Find volume location on host
podman volume inspect postgres-data | grep Mountpoint
```

---

## Health Checks

### Mandatory Health Check Requirements

**All Services Must Implement Health Checks**

**Health Check Types:**
1. **Liveness Probe:** Is the container alive? (restart if failing)
2. **Readiness Probe:** Is the service ready to accept traffic?

**Quadlet Health Check Configuration:**
```ini
[Container]
HealthCmd=/usr/bin/curl -f http://localhost:8000/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=60s
```

**Health Endpoint Requirements (FastAPI):**
```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Kubernetes/Podman liveness probe endpoint.
    Returns 200 OK if service is alive.
    """
    try:
        # Check database connectivity
        await check_database()

        return JSONResponse({
            "status": "healthy",
            "service": "soap-calculator-api",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness probe: Service ready to accept traffic.
    """
    # Check all dependencies (DB, cache, external APIs)
    return {"status": "ready"}
```

**Health Check Monitoring:**
```bash
# Check container health status
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# Inspect health check history
podman inspect soap-api | jq '.[0].State.Health'

# systemd integration
systemctl status soap-calculator-api.service
```

---

## Secrets Management

### Ansible Vault Integration

**Secret Storage:** All secrets encrypted with Ansible Vault

**Secret Types:**
- Database credentials
- API keys for external services
- JWT signing secrets
- TLS certificates/keys

**Ansible Vault Workflow:**

**1. Create Encrypted Secrets File:**
```bash
# Create vault-encrypted secrets
ansible-vault create infra/ansible/group_vars/production/vault.yml
```

**vault.yml Content:**
```yaml
---
vault_database_password: "secure_postgres_password"
vault_api_secret_key: "random_secret_key_for_jwt"
vault_external_api_key: "third_party_api_key"
```

**2. Reference in Playbook:**
```yaml
---
- name: Deploy Soap Calculator API
  hosts: production
  become: true
  vars_files:
    - group_vars/production/vault.yml

  tasks:
    - name: Create systemd environment file with secrets
      template:
        src: soap-api.env.j2
        dest: /etc/soap-calculator/api.env
        owner: root
        group: root
        mode: '0600'  # Readable only by root
```

**3. Environment File Template (soap-api.env.j2):**
```jinja2
# Generated by Ansible - DO NOT EDIT MANUALLY
DATABASE_URL=postgresql://soap_user:{{ vault_database_password }}@localhost:5432/soap_calc
SECRET_KEY={{ vault_api_secret_key }}
EXTERNAL_API_KEY={{ vault_external_api_key }}
ENVIRONMENT=production
```

**4. Quadlet Container Unit:**
```ini
[Container]
EnvironmentFile=/etc/soap-calculator/api.env
```

**Vault Operations:**
```bash
# Edit encrypted file
ansible-vault edit infra/ansible/group_vars/production/vault.yml

# View encrypted file
ansible-vault view infra/ansible/group_vars/production/vault.yml

# Encrypt existing file
ansible-vault encrypt secrets.yml

# Decrypt file (temporary, re-encrypt after)
ansible-vault decrypt secrets.yml

# Run playbook with vault password
ansible-playbook deploy.yml --ask-vault-pass

# Use vault password file
ansible-playbook deploy.yml --vault-password-file ~/.vault_pass
```

**Security Best Practices:**
- Never commit unencrypted secrets to Git
- `.env` files gitignored on development machines
- Production secrets only exist in Ansible Vault
- Vault password stored in secure password manager (1Password, Bitwarden)
- Rotate secrets quarterly or after personnel changes

---

## Build Process: Cross-Platform Considerations

### Building on macOS for Fedora 42 Deployment

**Challenge:** macOS (Darwin) → Linux (Fedora 42) cross-platform builds

**Solution:** Multi-architecture container images

**Buildah/Podman Build on macOS:**

**Install Podman on macOS:**
```bash
brew install podman

# Initialize Podman machine (Linux VM)
podman machine init --cpus 4 --memory 8192 --disk-size 100
podman machine start
```

**Containerfile (Multi-Arch):**
```dockerfile
# Use Red Hat UBI Python base
FROM registry.access.redhat.com/ubi9/python-311:latest AS base

# Platform-independent build
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies
RUN dnf install -y \
    gcc \
    python3-devel \
    postgresql-devel \
    && dnf clean all

# Create application user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build Multi-Arch Image:**
```bash
# Build for Linux AMD64 (Fedora 42 target)
podman build \
  --platform linux/amd64 \
  --tag localhost/mga-soap-calculator:latest \
  --file Containerfile \
  .

# Build multi-arch (AMD64 + ARM64)
podman build \
  --platform linux/amd64,linux/arm64 \
  --manifest localhost/mga-soap-calculator:latest \
  --file Containerfile \
  .
```

**Verify Build:**
```bash
# Inspect image architecture
podman inspect localhost/mga-soap-calculator:latest | jq '.[0].Architecture'

# Should output: amd64
```

**Image Transfer to Production:**

**Option 1: Export/Import (No Registry):**
```bash
# On macOS: Export image
podman save localhost/mga-soap-calculator:latest | gzip > soap-calculator.tar.gz

# Transfer to production
scp soap-calculator.tar.gz production-server:/tmp/

# On Fedora 42: Import image
podman load < /tmp/soap-calculator.tar.gz
```

**Option 2: Local Registry (Recommended):**
```bash
# On production: Run local registry container
podman run -d -p 5000:5000 --name registry registry:2

# On macOS: Tag and push
podman tag localhost/mga-soap-calculator:latest production-server:5000/mga-soap-calculator:latest
podman push production-server:5000/mga-soap-calculator:latest

# On Fedora 42: Pull from local registry
podman pull production-server:5000/mga-soap-calculator:latest
podman tag production-server:5000/mga-soap-calculator:latest localhost/mga-soap-calculator:latest
```

**CI/CD Integration (GitHub Actions):**
```yaml
name: Build Container Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman

      - name: Build image
        run: |
          podman build \
            --platform linux/amd64 \
            --tag localhost/mga-soap-calculator:${{ github.sha }} \
            --file Containerfile \
            .

      - name: Export image artifact
        run: |
          podman save localhost/mga-soap-calculator:${{ github.sha }} \
            | gzip > soap-calculator-${{ github.sha }}.tar.gz

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: container-image
          path: soap-calculator-${{ github.sha }}.tar.gz
```

---

## Deployment Standards

### Idempotent Ansible Playbooks

**Principle:** Playbooks can be run multiple times without adverse effects

**Example Deployment Playbook (infra/ansible/deploy-api.yml):**
```yaml
---
- name: Deploy MGA Soap Calculator API Container
  hosts: production
  become: true
  vars_files:
    - group_vars/production/vault.yml

  vars:
    api_image: localhost/mga-soap-calculator:latest
    api_container_name: soap-api
    config_dir: /etc/soap-calculator
    log_dir: /var/log/soap-calculator

  tasks:
    - name: Ensure configuration directory exists
      file:
        path: "{{ config_dir }}"
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Ensure log directory exists
      file:
        path: "{{ log_dir }}"
        state: directory
        owner: root
        group: root
        mode: '0755'
        setype: container_file_t  # SELinux type

    - name: Deploy API environment file
      template:
        src: soap-api.env.j2
        dest: "{{ config_dir }}/api.env"
        owner: root
        group: root
        mode: '0600'
      notify: restart api container

    - name: Deploy Quadlet container unit
      template:
        src: soap-calculator-api.container.j2
        dest: /etc/containers/systemd/soap-calculator-api.container
        owner: root
        group: root
        mode: '0644'
      notify: reload systemd and restart api

    - name: Pull latest container image
      command: podman pull {{ api_image }}
      register: pull_result
      changed_when: "'Downloaded newer image' in pull_result.stdout"
      notify: restart api container

    - name: Enable and start API service
      systemd:
        name: soap-calculator-api.service
        enabled: true
        state: started
        daemon_reload: true

  handlers:
    - name: reload systemd and restart api
      systemd:
        name: soap-calculator-api.service
        state: restarted
        daemon_reload: true

    - name: restart api container
      systemd:
        name: soap-calculator-api.service
        state: restarted

    - name: Wait for health check
      uri:
        url: http://localhost:8000/health
        status_code: 200
        timeout: 60
      retries: 12
      delay: 5
```

**Idempotency Checks:**
- `file` module: Creates if missing, no-op if exists
- `template`: Only changes if content differs
- `systemd`: Only reloads/restarts if state changed
- `podman pull`: Only reports change if new image downloaded

---

### Rollback Procedures

**Systemd Rollback (Quick):**
```bash
# Stop failing service
sudo systemctl stop soap-calculator-api.service

# Tag current image as broken
podman tag localhost/mga-soap-calculator:latest localhost/mga-soap-calculator:broken

# Pull previous working image (from backup or registry)
podman tag localhost/mga-soap-calculator:previous localhost/mga-soap-calculator:latest

# Restart service
sudo systemctl start soap-calculator-api.service

# Verify health
curl http://localhost:8000/health
```

**Ansible Rollback Playbook (infra/ansible/rollback-api.yml):**
```yaml
---
- name: Rollback API Container to Previous Version
  hosts: production
  become: true

  vars:
    rollback_tag: previous  # or specific version tag

  tasks:
    - name: Stop API service
      systemd:
        name: soap-calculator-api.service
        state: stopped

    - name: Tag current as broken
      command: podman tag localhost/mga-soap-calculator:latest localhost/mga-soap-calculator:broken-{{ ansible_date_time.epoch }}
      ignore_errors: true

    - name: Restore previous version
      command: podman tag localhost/mga-soap-calculator:{{ rollback_tag }} localhost/mga-soap-calculator:latest

    - name: Start API service
      systemd:
        name: soap-calculator-api.service
        state: started

    - name: Wait for health check
      uri:
        url: http://localhost:8000/health
        status_code: 200
      retries: 12
      delay: 5

    - name: Report rollback success
      debug:
        msg: "Rollback to {{ rollback_tag }} completed successfully"
```

**Image Tagging Strategy:**
```bash
# Before deployment, tag current as previous
podman tag localhost/mga-soap-calculator:latest localhost/mga-soap-calculator:previous

# Deploy new image
podman pull new-image
podman tag new-image localhost/mga-soap-calculator:latest

# If rollback needed
podman tag localhost/mga-soap-calculator:previous localhost/mga-soap-calculator:latest
```

---

### Validation Commands

**Post-Deployment Validation Playbook (infra/ansible/validate-deployment.yml):**
```yaml
---
- name: Validate API Deployment
  hosts: production
  become: true

  tasks:
    - name: Check API service status
      systemd:
        name: soap-calculator-api.service
      register: service_status
      failed_when: service_status.status.ActiveState != 'active'

    - name: Check API health endpoint
      uri:
        url: http://localhost:8000/health
        status_code: 200
        return_content: true
      register: health_check
      failed_when: health_check.json.status != 'healthy'

    - name: Verify database connectivity
      uri:
        url: http://localhost:8000/api/v1/health/db
        status_code: 200
      register: db_check

    - name: Check container logs for errors
      command: journalctl -u soap-calculator-api.service -n 50 --no-pager
      register: logs
      failed_when: "'ERROR' in logs.stdout or 'CRITICAL' in logs.stdout"

    - name: Report deployment validation
      debug:
        msg: "Deployment validated successfully. API healthy, DB connected, no errors in logs."
```

**Manual Validation Commands:**
```bash
# Service status
systemctl status soap-calculator-api.service

# Container status
podman ps --filter name=soap-api

# Health check
curl -f http://localhost:8000/health

# View logs
journalctl -u soap-calculator-api.service -f

# Check resource usage
podman stats soap-api

# Inspect container
podman inspect soap-api

# Network connectivity
podman exec soap-api curl -f http://postgresql:5432
```

---

## Integration with Existing agent-os Framework

### Connection to Product Tech Stack

This deployment platform specification complements `agent-os/product/tech-stack.md`:
- **Backend (Python/FastAPI):** Containerized with Fedora/UBI Python base
- **Database (PostgreSQL):** Runs in separate Podman container with persistent volume
- **Infrastructure:** Ansible playbooks deploy Quadlet units per `tech-stack.md` standards

### Connection to Global Standards

Aligns with `agent-os/standards/global/tech-stack.md`:
- **Infrastructure as Code:** All changes via Ansible (required)
- **Deployment Workflow:** Ansible triggers Quadlet deployments
- **CI/CD:** GitHub Actions builds images, Ansible deploys to production

### Standards Enforcement

Development teams must:
1. Use Fedora/UBI base images exclusively (reviewable in Containerfile)
2. Define health checks for all services (enforceable via CI)
3. Document Quadlet units in `infra/containers/systemd/`
4. Deploy via Ansible playbooks only (no manual `podman run`)
5. Test deployments on Fedora 42 before production (CI environment)

---

## Rationale Summary

### Why This Stack?

**Podman + Quadlet + Fedora 42:**
- **Security:** Rootless capability, SELinux integration, no privileged daemon
- **Reliability:** systemd battle-tested process supervision, automatic restarts
- **Simplicity:** No external orchestrator (Kubernetes, Swarm) needed for single-server
- **Platform Native:** Podman is Fedora/RHEL default, first-class citizen
- **Ansible Integration:** Infrastructure as Code with existing Ansible expertise

**Fedora/UBI Base Images:**
- **Compatibility:** Match production OS (Fedora 42), identical package versions
- **Security:** Red Hat/Fedora security pipeline, CVE tracking
- **Support:** Enterprise-ready with Red Hat backing (UBI)
- **Performance:** No cross-distro library mismatches (glibc, OpenSSL, etc.)

**SELinux Enforcing:**
- **Mandatory Access Control:** Even compromised container cannot access host
- **Compliance:** Required for many security standards (PCI-DSS, NIST)
- **Defense in Depth:** Complements containerization boundaries

---

## Migration from Docker

If migrating from Docker-based development:

**Docker → Podman Command Translation:**
```bash
# Alias for compatibility
alias docker=podman

# Most commands work identically
podman run -d -p 8000:8000 my-image
podman ps
podman logs container-name
podman exec -it container-name /bin/bash

# docker-compose → podman-compose (optional)
pip install podman-compose
podman-compose up -d

# Preferred: Migrate to Quadlet
# Convert docker-compose.yml to Quadlet .container files
```

**Dockerfile → Containerfile:**
- Syntax identical, rename for clarity
- Update `FROM` lines to Fedora/UBI images
- Replace `apt-get` with `dnf`

**docker-compose.yml → Quadlet Units:**
- Manual conversion, service-by-service
- Quadlet units are more explicit but simpler for systemd integration

---

## Operational Runbook

### Common Tasks

**Deploy New Version:**
```bash
cd infra/ansible
ansible-playbook deploy-api.yml --ask-vault-pass
```

**View Logs:**
```bash
journalctl -u soap-calculator-api.service -f
```

**Restart Service:**
```bash
sudo systemctl restart soap-calculator-api.service
```

**Rollback:**
```bash
cd infra/ansible
ansible-playbook rollback-api.yml --ask-vault-pass
```

**Update Image:**
```bash
podman pull localhost/mga-soap-calculator:latest
sudo systemctl restart soap-calculator-api.service
```

**Backup Database Volume:**
```bash
podman volume export postgres-data | gzip > /backup/postgres-$(date +%Y%m%d).tar.gz
```

**Inspect Container:**
```bash
podman inspect soap-api
podman exec -it soap-api /bin/bash
```

---

## Future Enhancements

### Potential Improvements

- **Podman Auto-Update:** Automatic image pulls and container restarts on new image availability
- **Systemd Templates:** Parameterized units for multi-instance deployments
- **Pod Networking:** Group related containers (API + sidecar) in Podman pods
- **Container Metrics:** Prometheus exporters for container monitoring
- **Backup Automation:** Automated volume snapshots with retention policies
- **Blue-Green Deployments:** Zero-downtime deployments with traffic switching

---

## Compliance & Security

### Security Checklist

- [ ] All containers use Fedora/UBI base images
- [ ] Containers run as non-root user internally
- [ ] SELinux enforcing mode on host
- [ ] Volume mounts use `:Z` or `:z` labels
- [ ] Health checks defined for all services
- [ ] Secrets managed via Ansible Vault
- [ ] No hardcoded credentials in images or Containerfiles
- [ ] TLS certificates rotated quarterly
- [ ] Security updates applied within 7 days of release

### Audit Trail

- All deployments via Ansible (logged in Ansible output)
- systemd journal captures container lifecycle
- Image build history tracked in Git (Containerfile versions)
- Configuration changes in Git (Quadlet units, playbooks)

---

## Support & Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check systemd status
systemctl status soap-calculator-api.service

# View detailed logs
journalctl -u soap-calculator-api.service -xe

# Check SELinux denials
sudo ausearch -m avc -ts recent

# Verify image exists
podman images | grep soap-calculator
```

**Permission Denied on Volume:**
```bash
# Add :Z label to volume mount in Quadlet unit
Volume=/host/path:/container/path:Z

# Or manually set SELinux context
sudo chcon -R -t container_file_t /host/path
```

**Health Check Failing:**
```bash
# Test health endpoint manually
podman exec soap-api curl -f http://localhost:8000/health

# Check application logs
journalctl -u soap-calculator-api.service -n 100

# Verify database connectivity
podman exec soap-api env | grep DATABASE_URL
```

---

## References

- **Podman Documentation:** https://docs.podman.io/
- **Quadlet Documentation:** https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- **Red Hat UBI:** https://catalog.redhat.com/software/containers/search
- **Fedora Container Images:** https://registry.fedoraproject.org/
- **SELinux for Containers:** https://www.redhat.com/en/blog/selinux-and-containers
- **Ansible Podman Modules:** https://docs.ansible.com/ansible/latest/collections/containers/podman/

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Owner:** MGA Soap Calculator Infrastructure Team
