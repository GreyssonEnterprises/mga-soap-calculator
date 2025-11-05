# MGA Soap Calculator - Deployment Quick Reference

## TL;DR - Deploy Now

```bash
cd /Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/ansible

# Full deployment (change version number!)
ansible-playbook playbooks/build-and-deploy.yml \
  --extra-vars "app_version=1.0.0" \
  --vault-password-file ~/.vault_pass.txt

# Watch for "Deployment Status: SUCCESS"
```

## Common Commands

### Deploy New Version
```bash
ansible-playbook playbooks/build-and-deploy.yml \
  --extra-vars "app_version=1.2.3" \
  --vault-password-file ~/.vault_pass.txt
```

### Emergency Rollback
```bash
ansible-playbook playbooks/rollback-deployment.yml
```

### Dry Run / Test
```bash
ansible-playbook playbooks/build-and-deploy.yml --check
```

### Verbose Output (Debugging)
```bash
ansible-playbook playbooks/build-and-deploy.yml -vv
```

## Quick Verification

```bash
# Health check
curl http://grimm-lin:8000/health

# New endpoints
curl http://grimm-lin:8000/api/v1/oils
curl http://grimm-lin:8000/api/v1/additives

# Service status
ssh grimm-lin "systemctl --user status soap-calculator-api.service"

# Recent logs
ssh grimm-lin "journalctl --user -u soap-calculator-api.service -n 50"

# Images
ssh grimm-lin "podman images localhost/mga-soap-calculator"
```

## Troubleshooting

### Deployment Failed?
Check the error message - automatic rollback should have triggered.
Verify rollback worked: `curl http://grimm-lin:8000/health`

### Health Check Timing Out?
Increase timeout in `ansible/roles/soap-calculator-image-lifecycle/defaults/main.yml`:
```yaml
health_check_retries: 12  # 120s total instead of 60s
```

### Out of Disk Space?
Clean old archives:
```bash
ssh grimm-lin "cd /data/podman-apps/mga-soap-calculator/images && ls -t mga-soap-calculator-*.tar.gz | tail -n +3 | xargs rm"
```

## File Locations

- **Role**: `ansible/roles/soap-calculator-image-lifecycle/`
- **Playbooks**: `ansible/playbooks/build-and-deploy.yml` & `rollback-deployment.yml`
- **Images**: `/data/podman-apps/mga-soap-calculator/images/` on grimm-lin
- **Config**: `/home/grimm/.config/mga-soap-calculator/` on grimm-lin
- **Logs**: `journalctl --user -u soap-calculator-api.service` on grimm-lin

## Version Management

**Increment Version**:
- Minor fixes: 1.0.0 → 1.0.1
- New features: 1.0.1 → 1.1.0
- Breaking changes: 1.1.0 → 2.0.0

**Version Format**: `v1.0.0-YYYYMMDD-HHmmss` (timestamp auto-generated)

## Documentation

Full docs: `ansible/roles/soap-calculator-image-lifecycle/README.md`
Implementation details: `agent-responses/20251104_103330_devops-architect_deployment-automation-implementation.md`
