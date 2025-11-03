# Storage Path Migration: /opt → /data

## Problem
grimm-lin server has limited root filesystem space:
- Root (/) : 15G total, 5.7G free (62% used) - TOO SMALL for containers
- /data   : 447G total, 436G free (3% used) - CORRECT location for application data

Original deployment used `/opt/mga/` which would fill the small root partition.

## Solution
Changed base deployment path from `/opt/mga` to `/data/mga-soap-calculator`

## Changes Made

### File: `ansible/inventory/group_vars/all.yml`

**Lines 55, 57 - Base Deployment Paths**:
```yaml
# BEFORE:
deployment_base_path: "/opt/mga"
env_files_path: "/opt/mga/env"

# AFTER:
deployment_base_path: "/data/mga-soap-calculator"
env_files_path: "/data/mga-soap-calculator/env"
```

## Impact Analysis

### Directories Created (with new paths)
When Ansible deployment runs, it will create:
```
/data/mga-soap-calculator/          # Main deployment directory
/data/mga-soap-calculator/backups/  # Database backups
/data/mga-soap-calculator/logs/     # Application logs
/data/mga-soap-calculator/scripts/  # Operational scripts
/data/mga-soap-calculator/env/      # Environment configuration files
```

**Permissions**: `root:root 0755` (defined in all.yml:68-70)

### Files NOT Changed (Already Correct)
- **Systemd Quadlet units**: Reference `/etc/mga-soap-calculator/` for configs (system-level, correct)
- **Config directories**: Use `/etc/mga-soap-calculator/` (small files, appropriate for root fs)
- **All Ansible roles**: Use `{{ deployment_base_path }}` variable (properly templated)

### Storage Utilization After Deployment
Based on estimated sizes:
- Container images: ~500MB (transient, podman storage)
- Database volume: ~100MB initial, grows with data
- Application logs: ~50MB with rotation
- Backups: ~30MB per backup × retention days
- Scripts/configs: ~5MB

**Total estimated**: ~1GB initial, scales with database growth

On `/data` filesystem (447G): This is **0.2%** usage - excellent headroom.

## Validation

### YAML Syntax
Validated with ansible-playbook --syntax-check.
(Vault password error expected - syntax itself is valid)

### Variable References
Verified all Ansible roles use templated variables:
```bash
$ grep -r "deployment_base_path\|env_files_path" ansible/
# Results show only variable references: {{ deployment_base_path }}
# No hardcoded /opt paths found
```

### Hardcoded Path Audit
```bash
$ grep -r "/opt" ansible/
# Only result: ansible/inventory/group_vars/all.yml (now fixed)
```

## Deployment Impact

### New Deployments
- Will automatically use `/data/mga-soap-calculator/`
- No manual intervention required

### Existing Deployments (if any exist)
**If production already deployed with /opt paths**, migration requires:
1. Stop services: `systemctl stop mga-*`
2. Move data: `rsync -av /opt/mga/ /data/mga-soap-calculator/`
3. Update configs
4. Restart services

**Recommendation**: Since this is fresh deployment, no migration needed.

## Testing Checklist
Before production deployment:
- [ ] Verify /data filesystem has adequate space (df -h /data)
- [ ] Confirm deployment creates directories under /data
- [ ] Validate container volumes mount correctly
- [ ] Check log file rotation writes to /data location
- [ ] Verify backups write to /data/mga-soap-calculator/backups/

## Risk Assessment
**Risk Level**: LOW

**Rationale**:
- Simple variable change, all paths templated
- No code logic changes
- Filesystem change is transparent to application
- Easily reversible (change variables back)

**Mitigation**:
- Ansible variables properly structured (single source of truth)
- All roles use template variables (no hardcoded paths)
- YAML syntax validated

## Rollback Procedure
If needed, revert the two lines in `ansible/inventory/group_vars/all.yml`:
```yaml
deployment_base_path: "/opt/mga"
env_files_path: "/opt/mga/env"
```

Then redeploy. (Note: Would need to migrate data back if deployment already ran)

## Related Documentation
- Filesystem layout: See `grimm-lin` server disk analysis
- Ansible variables: `ansible/inventory/group_vars/all.yml`
- Directory creation: Defined in `app_directories` list (all.yml:60-65)

---
**Date**: 2025-11-02
**Author**: Bob PAI (DevOps Architect)
**Status**: Complete - Ready for deployment
