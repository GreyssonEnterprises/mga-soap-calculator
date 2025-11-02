# MGA Soap Calculator - Podman Deployment Guide for Fedora 42

## Overview

This guide covers deploying the MGA Soap Calculator API using Podman with Quadlet systemd integration on Fedora 42.

**Key Features:**
- Rootless container deployment (no root daemon required)
- Native systemd integration via Quadlet
- SELinux-compatible configuration
- Automatic service restart and boot persistence

## Prerequisites

### System Requirements
- Fedora 42 (or compatible RHEL-based system)
- Podman 5.x or later
- systemd (user services enabled)
- 2GB RAM minimum
- 10GB disk space

### Install Podman
```bash
sudo dnf install -y podman podman-compose
```

### Verify Installation
```bash
podman --version
# Should show: podman version 5.x or later
```

## Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/grimmolf/mga-soap-calculator.git
cd mga-soap-calculator

# 2. Configure environment
cp podman/env.production /etc/mga-calculator/env.production
cp podman/postgres.env /etc/mga-calculator/postgres.env

# Edit passwords and secrets
nano /etc/mga-calculator/env.production
nano /etc/mga-calculator/postgres.env

# 3. Deploy
./podman/deploy.sh

# 4. Verify
systemctl --user status mga-api
curl http://localhost:8000/api/v1/health
```

## Detailed Deployment Steps

### Step 1: Environment Configuration

Create configuration directory:
```bash
sudo mkdir -p /etc/mga-calculator
sudo chown $USER:$USER /etc/mga-calculator
```

Copy and edit environment files:
```bash
cp podman/env.production /etc/mga-calculator/env.production
cp podman/postgres.env /etc/mga-calculator/postgres.env
```

**Generate secure secrets:**
```bash
# Generate SECRET_KEY (32 bytes hex)
openssl rand -hex 32

# Generate PostgreSQL password
openssl rand -base64 24
```

Update `/etc/mga-calculator/env.production`:
```bash
DATABASE_URL=postgresql://soap_user:YOUR_PG_PASSWORD@mga-postgres:5432/soap_calculator
SECRET_KEY=YOUR_GENERATED_SECRET_KEY
ENVIRONMENT=production
LOG_LEVEL=info
```

Update `/etc/mga-calculator/postgres.env`:
```bash
POSTGRES_USER=soap_user
POSTGRES_PASSWORD=YOUR_PG_PASSWORD
POSTGRES_DB=soap_calculator
```

### Step 2: Build Container Image

```bash
cd /path/to/mga-soap-calculator
podman build -t localhost/mga-soap-calculator:latest .
```

Verify image:
```bash
podman images | grep mga-soap-calculator
```

### Step 3: Install Quadlet Units

Copy systemd unit files:
```bash
mkdir -p ~/.config/containers/systemd
cp podman/systemd/*.container ~/.config/containers/systemd/
cp podman/systemd/*.network ~/.config/containers/systemd/
```

Verify installation:
```bash
ls -la ~/.config/containers/systemd/
# Should show: mga-api.container, mga-postgres.container, mga-network.network
```

### Step 4: Create Persistent Volumes

```bash
podman volume create mga-pgdata
podman volume create mga-logs
```

Verify:
```bash
podman volume ls | grep mga-
```

### Step 5: Start Services

Reload systemd:
```bash
systemctl --user daemon-reload
```

Enable and start network:
```bash
systemctl --user enable --now mga-network
```

Enable and start PostgreSQL:
```bash
systemctl --user enable --now mga-postgres
```

Wait for PostgreSQL initialization (10-15 seconds), then start API:
```bash
systemctl --user enable --now mga-api
```

### Step 6: Initialize Database

The API will need database tables created:

```bash
# Option 1: Using init script in running container
podman exec mga-api alembic upgrade head
podman exec mga-api python scripts/seed_database.py

# Option 2: Run locally if you have Python environment
alembic upgrade head
python scripts/seed_database.py
```

### Step 7: Enable Service Persistence

Enable linger so services persist after logout:
```bash
loginctl enable-linger $USER
```

Verify:
```bash
loginctl show-user $USER | grep Linger
# Should show: Linger=yes
```

## Service Management

### Check Service Status
```bash
systemctl --user status mga-api
systemctl --user status mga-postgres
systemctl --user status mga-network
```

### View Logs
```bash
# API logs
journalctl --user -u mga-api -f

# PostgreSQL logs
journalctl --user -u mga-postgres -f

# All MGA services
journalctl --user -u 'mga-*' -f
```

### Restart Services
```bash
systemctl --user restart mga-api
systemctl --user restart mga-postgres
```

### Stop Services
```bash
systemctl --user stop mga-api
systemctl --user stop mga-postgres
systemctl --user stop mga-network
```

### Disable Services
```bash
systemctl --user disable mga-api
systemctl --user disable mga-postgres
systemctl --user disable mga-network
```

## Health Verification

### API Health Check
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"database":"connected"}
```

### Database Health Check
```bash
podman exec mga-postgres pg_isready -U soap_user
# Expected: /var/run/postgresql:5432 - accepting connections
```

### Container Status
```bash
podman ps
# Should show: mga-api and mga-postgres containers running
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
journalctl --user -u mga-api --since "5 minutes ago"
```

Common issues:
- **PostgreSQL not ready:** Wait longer, increase TimeoutStartSec
- **Environment file missing:** Verify /etc/mga-calculator/ exists with correct ownership
- **Image not found:** Re-run `podman build`

### SELinux Denials

Check for AVC denials:
```bash
sudo ausearch -m AVC -ts recent | grep mga
```

If denials found:
```bash
# Generate custom policy (if needed)
sudo audit2allow -a -M mga-custom
sudo semodule -i mga-custom.pp
```

Volume labels should prevent denials (`:Z` in .container files).

### Database Connection Errors

Verify PostgreSQL is running:
```bash
systemctl --user status mga-postgres
podman exec mga-postgres psql -U soap_user -d soap_calculator -c "SELECT 1;"
```

Check DATABASE_URL in env.production matches postgres.env credentials.

### Permission Issues

Rootless Podman requires:
```bash
# Verify subuid/subgid ranges
cat /etc/subuid | grep $USER
cat /etc/subgid | grep $USER

# Should show ranges like: username:100000:65536
```

### Port Already in Use

If port 8000 is busy:
```bash
# Find process using port
ss -tulpn | grep :8000

# Change port in mga-api.container
PublishPort=8080:8000  # External:Internal
```

## Performance Tuning

### Resource Limits

Edit `~/.config/containers/systemd/mga-api.container`:
```ini
[Service]
MemoryMax=512M
CPUQuota=50%
```

Reload and restart:
```bash
systemctl --user daemon-reload
systemctl --user restart mga-api
```

### PostgreSQL Tuning

Edit postgres.env:
```bash
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_WORK_MEM=4MB
```

## Security Hardening

### Network Isolation

Containers communicate only via mga-network (10.88.0.0/24). No host network access.

### Read-Only Filesystem

Application code is read-only. Only logs volume is writable.

### SELinux Enforcement

All containers run with `container_runtime_t` context. Volumes use `:Z` private labeling.

### Secret Management

**Never commit secrets to Git:**
- Use `/etc/mga-calculator/` for production secrets (owned by user, mode 600)
- Rotate SECRET_KEY and PostgreSQL password regularly
- Use Ansible Vault for automated deployments

## Backup & Recovery

### Database Backup
```bash
# Create backup
podman exec mga-postgres pg_dump -U soap_user soap_calculator > backup.sql

# Restore from backup
podman exec -i mga-postgres psql -U soap_user soap_calculator < backup.sql
```

### Volume Backup
```bash
# Backup PostgreSQL data volume
podman volume export mga-pgdata -o mga-pgdata-backup.tar

# Restore
podman volume import mga-pgdata mga-pgdata-backup.tar
```

## Upgrading

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild image
podman build -t localhost/mga-soap-calculator:latest .

# Restart service (systemd pulls new image)
systemctl --user restart mga-api
```

### Update PostgreSQL
```bash
# Stop services
systemctl --user stop mga-api
systemctl --user stop mga-postgres

# Backup data first!
podman exec mga-postgres pg_dump -U soap_user soap_calculator > pre-upgrade-backup.sql

# Update postgres.env with new image version
# Edit mga-postgres.container: Image=docker.io/library/postgres:16-alpine

# Reload and start
systemctl --user daemon-reload
systemctl --user start mga-postgres
systemctl --user start mga-api
```

## Monitoring

### Service Status Dashboard
```bash
# All MGA services
systemctl --user list-units 'mga-*' --all

# Resource usage
podman stats mga-api mga-postgres
```

### Log Aggregation
```bash
# Combined logs with timestamps
journalctl --user -u mga-api -u mga-postgres --since today -o short-iso
```

### Health Monitoring Script
```bash
#!/bin/bash
# Save as: scripts/health-check.sh

if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ API healthy"
else
    echo "❌ API unhealthy - check logs"
    exit 1
fi
```

## Uninstall

```bash
# Stop and disable services
systemctl --user disable --now mga-api
systemctl --user disable --now mga-postgres
systemctl --user disable --now mga-network

# Remove Quadlet files
rm ~/.config/containers/systemd/mga-*

# Remove volumes (WARNING: deletes all data)
podman volume rm mga-pgdata mga-logs

# Remove image
podman rmi localhost/mga-soap-calculator:latest

# Reload systemd
systemctl --user daemon-reload
```

## Production Checklist

Before deploying to production:

- [ ] Change all default passwords in environment files
- [ ] Generate secure SECRET_KEY with `openssl rand -hex 32`
- [ ] Configure firewall rules if exposing externally
- [ ] Setup reverse proxy (nginx/Caddy) for HTTPS
- [ ] Enable service monitoring and alerting
- [ ] Test backup and restore procedures
- [ ] Verify loginctl linger enabled
- [ ] Document rollback procedure
- [ ] Create admin user account
- [ ] Load complete oil and additive databases

## Support

For issues, check:
1. Service logs: `journalctl --user -u mga-api -f`
2. SELinux denials: `sudo ausearch -m AVC -ts recent`
3. Container status: `podman ps -a`
4. Network connectivity: `podman network inspect mga-network`

**Documentation:** See `docs/DEPLOYMENT.md` for general deployment guide.
