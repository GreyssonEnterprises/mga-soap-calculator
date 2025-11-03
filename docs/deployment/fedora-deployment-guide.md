# MGA SOAP Calculator — Fedora 42 Deployment Guide

**Target Platform:** Fedora 42 with Podman 4.9+ and Quadlet
**Last Updated:** 2025-11-02
**Version:** 1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Deployment Execution](#deployment-execution)
6. [Verification](#verification)
7. [Operations](#operations)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### System Requirements

**Operating System:**
- Fedora 42 Linux (x86_64)
- Kernel 6.x+ with cgroups v2 support
- systemd 255+
- SELinux in enforcing mode

**Software Dependencies:**
```bash
# Verify versions
uname -r                    # Should be 6.x+
systemctl --version          # Should be systemd 255+
getenforce                   # Should return "Enforcing"
podman --version             # Should be 4.9+
ansible --version            # Should be 2.14+
```

**Install Required Packages:**
```bash
sudo dnf install -y \
    podman \
    ansible-core \
    python3-pip \
    curl \
    jq
```

**Install Ansible Podman Collection:**
```bash
ansible-galaxy collection install containers.podman
```

### Build Platform (macOS)

If building container images on macOS:

```bash
# Install Podman on macOS
brew install podman

# Initialize Podman machine
podman machine init --cpus 4 --memory 8192 --disk-size 100
podman machine start
```

### Network Ports

**Required Ports:**
- `8000/tcp` — API HTTP endpoint (published for reverse proxy)
- `5432/tcp` — PostgreSQL (published to 127.0.0.1 only)

**Firewall Configuration:**
```bash
# Allow API port through firewall
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## Architecture Overview

### Container Stack

```
┌─────────────────────────────────────┐
│  Reverse Proxy (nginx/Caddy)       │
│  Ports: 80/443 → localhost:8000    │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  soap-calculator-api Container      │
│  - Image: mga-soap-calculator:latest│
│  - Port: 8000                       │
│  - Network: mga-web                 │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  mga-postgres Container             │
│  - Image: postgres:15-alpine*       │
│  - Port: 5432 (127.0.0.1 only)      │
│  - Network: mga-web                 │
│  - Volume: mga-pgdata               │
└─────────────────────────────────────┘
```

**NOTE:** *Alpine base violates deployment-platform.md standards. Migrate to UBI after initial deployment.

### Network Configuration

**Custom Bridge Network:** `mga-web`
- Subnet: 10.89.0.0/24
- Gateway: 10.89.0.1
- DNS: Automatic container name resolution

### Data Persistence

**PostgreSQL Volume:**
- Name: `mga-pgdata`
- Mount: `/var/lib/postgresql/data`
- SELinux Label: `:Z` (private)

---

## Installation Steps

### Step 1: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/yourusername/mga-soap-calculator.git
cd mga-soap-calculator
```

### Step 2: Configure Ansible Inventory

Create `/opt/mga-soap-calculator/ansible/inventory/production.yml`:

```yaml
all:
  hosts:
    mga_production:
      ansible_host: production-server.example.com
      ansible_user: deploy
      ansible_become: true
      ansible_python_interpreter: /usr/bin/python3
```

### Step 3: Create Ansible Vault

**Initialize Vault:**
```bash
cd ansible
cp group_vars/production/vault.yml.example group_vars/production/vault.yml
```

**Edit vault.yml with real secrets:**
```bash
# Generate secure secrets
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -hex 64)

# Edit vault
vim group_vars/production/vault.yml
```

**vault.yml contents:**
```yaml
---
vault_db_password: "YOUR_SECURE_DB_PASSWORD_HERE"
vault_jwt_secret_key: "YOUR_64_CHAR_HEX_JWT_SECRET_HERE"
```

**Encrypt vault:**
```bash
ansible-vault encrypt group_vars/production/vault.yml
# Enter vault password (store in password manager!)
```

### Step 4: Build Container Image

**On Build Machine (macOS or Linux):**
```bash
cd /opt/mga-soap-calculator

# Build for Linux AMD64 (Fedora 42 target)
podman build \
  --platform linux/amd64 \
  --tag localhost/mga-soap-calculator:latest \
  --file Dockerfile \
  .
```

**Verify architecture:**
```bash
podman inspect localhost/mga-soap-calculator:latest | jq '.[0].Architecture'
# Should output: amd64
```

**Export image for transfer:**
```bash
podman save localhost/mga-soap-calculator:latest | gzip > mga-soap-calculator.tar.gz
```

**Transfer to production server:**
```bash
scp mga-soap-calculator.tar.gz production-server:/tmp/
```

**On production server, load image:**
```bash
ssh production-server
podman load < /tmp/mga-soap-calculator.tar.gz
```

---

## Configuration

### Environment Variables

**PostgreSQL Environment (`/etc/mga-soap-calculator/postgres.env`):**
```bash
POSTGRES_USER=soap_user
POSTGRES_PASSWORD=<from_vault>
POSTGRES_DB=mga_soap_calculator
```

**API Environment (`/etc/mga-soap-calculator/api.env`):**
```bash
ENVIRONMENT=production
JWT_SECRET_KEY=<from_vault>
DATABASE_URL=postgresql+psycopg://soap_user:<password>@mga-postgres:5432/mga_soap_calculator
WORKERS=2
LOG_LEVEL=INFO
```

**NOTE:** These files are created automatically by Ansible from templates.

### SELinux Configuration

SELinux is **required** in enforcing mode:

```bash
# Verify SELinux mode
getenforce
# Should return: Enforcing

# If permissive, enable enforcing:
sudo setenforce 1
sudo sed -i 's/SELINUX=permissive/SELINUX=enforcing/' /etc/selinux/config
```

---

## Deployment Execution

### Initial Deployment

```bash
cd /opt/mga-soap-calculator/ansible

# Run deployment playbook
ansible-playbook \
  -i inventory/production.yml \
  playbooks/deploy-soap-calculator.yml \
  --ask-vault-pass
```

**Playbook Execution Flow:**
1. Creates configuration directories
2. Creates PostgreSQL volume
3. Deploys environment files (with secrets)
4. Deploys Quadlet units
5. Reloads systemd daemon
6. Starts PostgreSQL service
7. Waits for PostgreSQL health check
8. Starts API service
9. Waits for API health check
10. Reports success

**Expected Output:**
```
PLAY RECAP ***************************************************************
mga_production : ok=15   changed=8    unreachable=0    failed=0    skipped=0
```

---

## Verification

### Service Status

```bash
# Check systemd service status
sudo systemctl status mga-postgres.service
sudo systemctl status soap-calculator-api.service

# Verify containers are running
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"
```

**Expected Output:**
```
NAMES            STATUS                     HEALTH
mga-postgres     Up 5 minutes (healthy)     healthy
soap-api         Up 3 minutes (healthy)     healthy
```

### Health Checks

**API Health Endpoint:**
```bash
curl -f http://127.0.0.1:8000/health | jq .
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "mga-soap-calculator-api",
  "timestamp": "2025-11-02T17:30:00.000000",
  "database": "connected"
}
```

**PostgreSQL Health:**
```bash
podman exec mga-postgres pg_isready -U soap_user -d mga_soap_calculator
```

**Expected Output:**
```
/var/run/postgresql:5432 - accepting connections
```

### Network Connectivity

```bash
# Verify network exists
podman network ls | grep mga-web

# Test DNS resolution inside container
podman exec soap-api getent hosts mga-postgres

# Test database connectivity from API
podman exec soap-api curl -f http://mga-postgres:5432
```

### Log Inspection

```bash
# API logs (real-time)
sudo journalctl -u soap-calculator-api.service -f

# PostgreSQL logs
sudo journalctl -u mga-postgres.service -f

# Both services
sudo journalctl -u soap-calculator-api.service -u mga-postgres.service -f
```

### Run Validation Playbook

```bash
cd /opt/mga-soap-calculator/ansible

ansible-playbook \
  -i inventory/production.yml \
  playbooks/validate-deployment.yml \
  --ask-vault-pass
```

---

## Operations

### Common Tasks

#### Restart Services

```bash
# Restart API only
sudo systemctl restart soap-calculator-api.service

# Restart both services
sudo systemctl restart mga-postgres.service soap-calculator-api.service
```

#### View Logs

```bash
# Last 100 lines of API logs
sudo journalctl -u soap-calculator-api.service -n 100

# Follow logs in real-time
sudo journalctl -u soap-calculator-api.service -f

# Export logs for analysis
sudo journalctl -u soap-calculator-api.service --since "2025-11-02" \
  --until "2025-11-03" > /tmp/api-logs-20251102.txt
```

#### Update Configuration

```bash
# Edit vault
cd /opt/mga-soap-calculator/ansible
ansible-vault edit group_vars/production/vault.yml

# Redeploy (only environment files will change)
ansible-playbook \
  -i inventory/production.yml \
  playbooks/deploy-soap-calculator.yml \
  --ask-vault-pass
```

#### Deploy New Image Version

```bash
# On build machine: Build and export new image
podman build --platform linux/amd64 -t localhost/mga-soap-calculator:latest .
podman save localhost/mga-soap-calculator:latest | gzip > mga-soap-calculator-new.tar.gz
scp mga-soap-calculator-new.tar.gz production-server:/tmp/

# On production: Load new image
ssh production-server
podman load < /tmp/mga-soap-calculator-new.tar.gz

# Restart API service to pick up new image
sudo systemctl restart soap-calculator-api.service

# Verify health
curl http://127.0.0.1:8000/health
```

### Backup Procedures

#### Database Backup (Logical)

```bash
# Create backup
pg_dump -Fc -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  > /backups/mga-soap-$(date +%Y%m%d).dump

# Automate with cron (daily at 2am)
echo "0 2 * * * /usr/local/bin/backup-mga-db.sh" | sudo crontab -
```

#### Volume Backup (Snapshot)

```bash
# Export volume to tarball
podman volume export mga-pgdata | gzip > /backups/mga-pgdata-$(date +%Y%m%d).tar.gz
```

#### Restore from Backup

**Logical Backup:**
```bash
pg_restore -U soap_user -h 127.0.0.1 -d mga_soap_calculator \
  --clean --if-exists /backups/mga-soap-20251102.dump
```

**Volume Snapshot:**
```bash
# Stop database
sudo systemctl stop mga-postgres.service

# Remove old volume
podman volume rm -f mga-pgdata

# Create new volume
podman volume create mga-pgdata

# Import backup
gunzip -c /backups/mga-pgdata-20251102.tar.gz | podman volume import mga-pgdata -

# Start database
sudo systemctl start mga-postgres.service
```

---

## Troubleshooting

### Container Won't Start

**Symptoms:**
- Service fails to start
- `systemctl status` shows "failed"

**Diagnosis:**
```bash
# Check systemd status
sudo systemctl status soap-calculator-api.service

# View detailed logs
sudo journalctl -u soap-calculator-api.service -xe

# Verify environment file
cat /etc/mga-soap-calculator/api.env

# Verify image exists
podman images localhost/mga-soap-calculator
```

**Common Fixes:**
- Missing environment file → Redeploy with Ansible
- Missing image → Load image from tarball
- Port conflict → Check `podman ps` for conflicting containers

### SELinux Permission Denied

**Symptoms:**
- "Permission denied" errors in logs
- Container can't write to volumes

**Diagnosis:**
```bash
# Check SELinux denials
sudo ausearch -m avc -ts recent

# Verify volume labels
podman volume inspect mga-pgdata | jq '.[0].Labels'
```

**Fixes:**
```bash
# Ensure :Z label in Quadlet unit
Volume=mga-pgdata:/var/lib/postgresql/data:Z

# Or manually set SELinux context
sudo chcon -R -t container_file_t /var/lib/containers/storage/volumes/mga-pgdata
```

### Health Check Failing

**Symptoms:**
- Container marked as "unhealthy"
- `podman ps` shows "(unhealthy)" status

**Diagnosis:**
```bash
# Run health check manually
podman healthcheck run soap-api

# Test health endpoint inside container
podman exec soap-api curl -f http://127.0.0.1:8000/health

# Check logs
sudo journalctl -u soap-calculator-api.service -n 100
```

**Common Fixes:**
- Database connection failure → Check DATABASE_URL in api.env
- Application error → Review logs for stack traces
- Slow startup → Increase HealthStartPeriod in Quadlet unit

### Database Connection Issues

**Symptoms:**
- API reports database connection errors
- Health check returns "unhealthy"

**Diagnosis:**
```bash
# Test PostgreSQL directly
podman exec mga-postgres pg_isready -U soap_user

# Test from API container
podman exec soap-api psql -U soap_user -h mga-postgres -d mga_soap_calculator -c "SELECT 1;"

# Check network connectivity
podman exec soap-api ping -c 3 mga-postgres
```

**Common Fixes:**
- Wrong password → Update vault and redeploy
- Database not ready → Wait for PostgreSQL health check to pass
- Network issue → Verify both containers on mga-web network

---

## Rollback Procedures

### Rollback to Previous Version

**When to Rollback:**
- New deployment fails health checks
- Critical bugs discovered in new version
- Performance degradation

**Execution:**
```bash
cd /opt/mga-soap-calculator/ansible

# Rollback to "previous" tag
ansible-playbook \
  -i inventory/production.yml \
  playbooks/rollback-api.yml \
  --ask-vault-pass

# Or rollback to specific version
ansible-playbook \
  -i inventory/production.yml \
  playbooks/rollback-api.yml \
  --extra-vars "rollback_tag=v1.2.3-20251102" \
  --ask-vault-pass
```

**Manual Rollback:**
```bash
# Stop API service
sudo systemctl stop soap-calculator-api.service

# Tag current as broken
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:broken-$(date +%s)

# Restore previous version
podman tag localhost/mga-soap-calculator:previous \
  localhost/mga-soap-calculator:latest

# Start service
sudo systemctl start soap-calculator-api.service

# Verify health
curl http://127.0.0.1:8000/health
```

### Image Tagging Strategy

**Before Every Deployment:**
```bash
# Tag current production as "previous"
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:previous

# Tag with version/date for audit trail
podman tag localhost/mga-soap-calculator:latest \
  localhost/mga-soap-calculator:v1.2.3-$(date +%Y%m%d)
```

---

## Best Practices

### Security

- ✅ Keep SELinux in enforcing mode
- ✅ Use Ansible Vault for all secrets
- ✅ Never commit unencrypted secrets to Git
- ✅ Rotate secrets quarterly
- ✅ Apply security updates within 7 days
- ✅ Containers run as non-root internally

### Operations

- ✅ Always use Ansible for deployments (no manual podman commands)
- ✅ Tag images before deployment for rollback capability
- ✅ Test deployments in staging first
- ✅ Maintain daily database backups with 30-day retention
- ✅ Monitor health endpoints continuously
- ✅ Review logs daily for errors

### Monitoring

**Set up alerts for:**
- Container health check failures
- Service restart events
- High memory/CPU usage
- Database connection errors
- API response time degradation

---

## References

- **Deployment Specification:** `agent-os/specs/2025-11-02-containerized-deployment/SPEC.md`
- **Platform Standards:** `agent-os/standards/global/deployment-platform.md`
- **Podman Documentation:** https://docs.podman.io/
- **Quadlet Documentation:** https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- **Ansible Podman Collection:** https://docs.ansible.com/ansible/latest/collections/containers/podman/

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Maintainer:** MGA Infrastructure Team
