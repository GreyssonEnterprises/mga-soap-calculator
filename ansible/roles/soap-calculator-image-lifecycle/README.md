# Soap Calculator Image Lifecycle Role

Complete container image lifecycle management for MGA Soap Calculator API deployment to grimm-lin.

## Overview

This Ansible role automates the full deployment lifecycle:
- **Build**: Create versioned container images locally
- **Transfer**: Copy image archives to `/data/podman-apps/` on grimm-lin
- **Deploy**: Load images into Podman and restart systemd services
- **Validate**: Health check verification with automatic rollback
- **Rollback**: Emergency recovery to previous working version

## Requirements

- Ansible 2.15+
- `containers.podman` collection
- Podman installed on both build machine and grimm-lin
- SSH access to grimm-lin with sudo privileges
- `/data/podman-apps/` directory on grimm-lin

## Role Variables

### Required Variables
```yaml
app_version: "1.0.0"  # Semantic version for release
grimm_uid: 1000       # UID for grimm user
```

### Optional Variables (with defaults)
```yaml
image_base_name: "localhost/mga-soap-calculator"
image_storage_path: "/data/podman-apps/mga-soap-calculator"
health_check_timeout: 10
health_check_retries: 6
keep_archives_count: 5
```

See `defaults/main.yml` for complete variable list.

## Usage

### Full Deployment

```bash
cd ansible

# Deploy with specific version
ansible-playbook playbooks/build-and-deploy.yml \
  --extra-vars "app_version=1.2.3" \
  --vault-password-file ~/.vault_pass.txt

# Dry run (check mode)
ansible-playbook playbooks/build-and-deploy.yml --check

# Verbose output
ansible-playbook playbooks/build-and-deploy.yml -vv
```

### Manual Rollback

```bash
ansible-playbook playbooks/rollback-deployment.yml
```

## Deployment Phases

### 1. Build Phase (Local)
- Generates timestamp version tag (v1.0.0-YYYYMMDD-HHmmss)
- Builds container image from Dockerfile
- Exports as OCI archive (.tar.gz)
- Generates SHA256 checksum

### 2. Transfer Phase
- Creates `/data/podman-apps/mga-soap-calculator/images/` if needed
- Transfers archive and checksum to grimm-lin
- Verifies integrity via checksum
- Updates `current` symlink

### 3. Deploy Phase
- Preserves previous `:latest` as `:rollback`
- Loads new image from archive
- Tags as `:latest`
- Restarts `soap-calculator-api.service`

### 4. Validation Phase
- Tests health endpoint (http://127.0.0.1:8000/health)
- Validates new API endpoints (/api/v1/oils, /api/v1/additives)
- Triggers automatic rollback if any checks fail

### 5. Cleanup Phase (Success Only)
- Removes local build artifacts
- Deletes old archives (keeps last 5 versions)

## Health Checks

The role validates deployment by checking:
- Primary health endpoint responds with 200 status
- New oils endpoint is accessible
- New additives endpoint is accessible
- Service is active in systemd

**Failure Handling**: Any failed check triggers automatic rollback.

## Rollback Mechanism

### Automatic Rollback
Triggered when validation fails:
1. Previous `:rollback` image promoted to `:latest`
2. Service restarted with old image
3. Health check verification
4. Deployment marked as failed

### Manual Rollback
Use `rollback-deployment.yml` playbook for post-deployment issues.

## Storage Structure

```
/data/podman-apps/mga-soap-calculator/
├── images/
│   ├── mga-soap-calculator-v1.0.0-20251104-102614.tar.gz
│   ├── mga-soap-calculator-v1.0.1-20251105-141522.tar.gz
│   └── CHECKSUMS.sha256
├── current -> images/mga-soap-calculator-v1.0.1-20251105-141522.tar.gz
└── rollback -> images/mga-soap-calculator-v1.0.0-20251104-102614.tar.gz
```

## Verification Commands

After deployment, verify manually:

```bash
# Check images
podman images localhost/mga-soap-calculator

# Service status
systemctl --user status soap-calculator-api.service

# Health check
curl http://127.0.0.1:8000/health

# New endpoints
curl http://127.0.0.1:8000/api/v1/oils
curl http://127.0.0.1:8000/api/v1/additives

# Recent logs
journalctl --user -u soap-calculator-api.service -n 50

# Archive storage
ls -lh /data/podman-apps/mga-soap-calculator/images/
readlink /data/podman-apps/mga-soap-calculator/current
```

## Security Considerations

- Checksum verification prevents corrupted/tampered images
- Images stored in user-owned `/data/podman-apps/` (not system paths)
- Rootless Podman execution (user grimm, UID 1001 container user)
- Secrets managed via Ansible Vault (not in images)
- Environment files: 0600 permissions

## Troubleshooting

### Build Fails
- Verify Dockerfile exists at repository root
- Check Podman build logs: `podman images`
- Ensure sufficient disk space in `/tmp/mga-builds`

### Transfer Fails
- Check SSH connectivity to grimm-lin
- Verify `/data/podman-apps/` exists and is writable
- Check network bandwidth for large archives

### Deployment Fails
- Check Podman load: `podman load --input /data/podman-apps/mga-soap-calculator/current`
- Verify systemd service: `systemctl --user status soap-calculator-api.service`
- Check logs: `journalctl --user -u soap-calculator-api.service -f`

### Health Check Fails
- Verify PostgreSQL is running: `systemctl --user status mga-postgres.service`
- Check API logs for startup errors
- Increase health_check_retries if slow startup
- Test manually: `curl -v http://127.0.0.1:8000/health`

### Rollback Fails
- Check rollback image exists: `podman images localhost/mga-soap-calculator:rollback`
- If no rollback image, load specific version from archives
- Manual recovery: `podman load --input /data/podman-apps/mga-soap-calculator/images/<specific-version>.tar.gz`

## Performance

- **Build time**: ~2-3 minutes (depends on code changes, layer caching)
- **Archive size**: ~500MB compressed
- **Transfer time**: ~4-10 seconds (local gigabit network)
- **Load time**: ~10-15 seconds
- **Service restart**: ~10 seconds
- **Total deployment**: ~5 minutes end-to-end

## License

Proprietary - MGA Automotive

## Author

Bob PAI (DevOps Architect)
