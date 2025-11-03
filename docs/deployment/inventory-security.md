# Inventory Security - MGA SOAP Calculator

> **CONFIDENTIAL** - MGA Automotive Client Infrastructure

## Overview

This document describes security practices for managing Ansible inventory files containing production server configurations.

## Why Inventory is Gitignored

**Production inventory contains sensitive information**:
- Server hostnames (infrastructure topology)
- IP addresses (network architecture)
- SSH usernames (access patterns)
- Network configurations (security boundaries)
- Resource allocations (capacity planning)

**Security Risk**: Exposing this information provides attackers with:
- Infrastructure mapping for targeted attacks
- User enumeration for credential attacks
- Network topology for lateral movement planning
- Capacity information for DoS attack planning

**Solution**: `.gitignore` prevents accidental commits of production inventory.

## Inventory File Locations

### Gitignored (Production)

**Files**:
- `ansible/inventory/production.yml` - Production server configuration
- `ansible/inventory/staging.yml` - Staging server configuration
- `ansible/inventory/*.yml` - All environment-specific inventories

**Status**: ❌ **NOT tracked by Git**

**Reason**: Contains actual server details for deployed infrastructure

### Version Controlled (Templates)

**Files**:
- `ansible/inventory/production.yml.example` - Template with placeholders
- `ansible/inventory/README.md` - Inventory documentation

**Status**: ✅ **Tracked by Git**

**Reason**: Provides structure without exposing actual infrastructure

## Current Production Configuration

### grimm-lin Server

**Hostname**: `grimm-lin`
**Environment**: Production
**Role**: MGA SOAP Calculator API + Database

**Why hostname instead of IP**:
- **Resilience**: IP addresses can change (DHCP, network reconfiguration)
- **Flexibility**: Hostname resolution allows infrastructure changes without code updates
- **DNS**: Leverages DNS for service discovery and failover

**SSH Configuration**:
- **User**: `grimm`
- **Authentication**: SSH key-based (no passwords)
- **Sudo**: Passwordless sudo enabled
- **Python**: `/usr/bin/python3`

## Updating Server Configuration

### Safe Update Procedure

1. **Backup current inventory**:
   ```bash
   cp ansible/inventory/production.yml \
      ansible/inventory/production.yml.backup.$(date +%Y%m%d-%H%M%S)
   ```

2. **Edit inventory**:
   ```bash
   $EDITOR ansible/inventory/production.yml
   ```

3. **Validate syntax**:
   ```bash
   ansible-inventory -i ansible/inventory/production.yml --list
   ```

4. **Test connectivity**:
   ```bash
   ansible grimm-lin \
     -i ansible/inventory/production.yml \
     -m ping
   ```

5. **Verify configuration**:
   ```bash
   ansible grimm-lin \
     -i ansible/inventory/production.yml \
     -m setup \
     | grep ansible_hostname
   ```

### What Can Be Changed Safely

✅ **Safe Changes**:
- Resource limits (memory, CPU)
- Application configuration (ports, workers)
- Monitoring settings
- Backup schedules
- Log rotation settings

⚠️ **Requires Planning**:
- Network configuration (subnets, IPs)
- Container image tags
- Database parameters
- Security settings (firewall rules)

❌ **High Risk** (Coordinate first):
- Server hostname/IP changes
- SSH user changes
- Deployment paths
- Database credentials (use vault.yml)

## Backup Procedures

### Automated Backups

Production inventory is automatically backed up:

**Location**: `~/.config/pai/backups/mga-soap-calculator/inventory/`

**Schedule**:
- Before every deployment
- Daily at 2 AM
- On manual request

**Retention**: 90 days

### Manual Backup

Create manual backup before risky changes:

```bash
BACKUP_DIR=~/.config/pai/backups/mga-soap-calculator/inventory
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR
cp ansible/inventory/production.yml \
   $BACKUP_DIR/production.yml.$TIMESTAMP

echo "Backup created: $BACKUP_DIR/production.yml.$TIMESTAMP"
```

### Restore from Backup

If inventory becomes corrupted or misconfigured:

```bash
BACKUP_DIR=~/.config/pai/backups/mga-soap-calculator/inventory

# List available backups
ls -lh $BACKUP_DIR/

# Restore specific backup
cp $BACKUP_DIR/production.yml.20251102-143000 \
   ansible/inventory/production.yml

# Verify restoration
ansible-inventory -i ansible/inventory/production.yml --list
```

## Adding New Servers

### Template for New Production Server

```yaml
all:
  children:
    mga_production:
      hosts:
        new-server-hostname:
          # SSH Connection
          ansible_host: new-server-hostname
          ansible_user: deployment-user
          ansible_become: true
          ansible_python_interpreter: /usr/bin/python3

          # Environment
          server_role: production
          deployment_environment: production

          # [Copy remaining configuration from grimm-lin]
```

### Validation Checklist

Before adding new server to inventory:

- [ ] SSH key authentication configured
- [ ] Sudo privileges verified
- [ ] Python 3 installed
- [ ] Network connectivity tested
- [ ] Firewall rules configured
- [ ] Hostname resolves correctly
- [ ] Passwordless sudo enabled

### Test New Server Connection

```bash
# Test SSH connectivity
ssh deployment-user@new-server-hostname "echo Connection successful"

# Test Ansible ping
ansible new-server-hostname \
  -i ansible/inventory/production.yml \
  -m ping

# Test privilege escalation
ansible new-server-hostname \
  -i ansible/inventory/production.yml \
  -m shell \
  -a "whoami" \
  --become
```

## Security Best Practices

### DO

✅ Backup before making changes
✅ Validate syntax after edits
✅ Test connectivity before deployment
✅ Use hostnames instead of IPs
✅ Document all changes
✅ Keep SSH keys secure
✅ Use SSH key authentication only
✅ Review firewall rules regularly

### DO NOT

❌ Commit production inventory to Git
❌ Share inventory files via email/chat
❌ Store inventory in cloud services
❌ Use password authentication
❌ Hardcode credentials in inventory
❌ Skip validation after changes
❌ Make changes directly in production

## Disaster Recovery

### Inventory File Lost/Corrupted

**Recovery Steps**:

1. **Check automated backups**:
   ```bash
   ls -lh ~/.config/pai/backups/mga-soap-calculator/inventory/
   ```

2. **Restore latest backup**:
   ```bash
   cp ~/.config/pai/backups/mga-soap-calculator/inventory/production.yml.latest \
      ansible/inventory/production.yml
   ```

3. **If no backups exist**, reconstruct from template:
   ```bash
   cp ansible/inventory/production.yml.example \
      ansible/inventory/production.yml
   ```

4. **Update with known values**:
   - Hostname: `grimm-lin`
   - User: `grimm`
   - Other settings from deployment documentation

5. **Verify reconstruction**:
   ```bash
   ansible grimm-lin -i ansible/inventory/production.yml -m ping
   ```

### Infrastructure Changes Requiring Inventory Updates

**Scenario**: Server IP address changed

**Impact**: Low (using hostnames)

**Action Required**: None (DNS handles resolution)

---

**Scenario**: Server hostname changed

**Impact**: High

**Action Required**:
1. Update `ansible_host` in inventory
2. Update DNS records
3. Update monitoring configurations
4. Update documentation
5. Notify team of change

---

**Scenario**: SSH user changed

**Impact**: High

**Action Required**:
1. Configure new user with SSH keys
2. Verify sudo privileges
3. Update `ansible_user` in inventory
4. Test connectivity
5. Remove old user access

---

**Scenario**: Network reconfiguration

**Impact**: Medium

**Action Required**:
1. Update network-related variables
2. Update firewall rules
3. Test connectivity
4. Verify service accessibility
5. Update documentation

## Compliance Notes

### MGA Automotive Requirements

- Inventory MUST NOT be committed to public repositories
- Infrastructure details MUST be protected as confidential
- Changes MUST be documented and auditable
- Access MUST be restricted to authorized personnel

### Red Hat Data Protection

- No customer data in inventory (infrastructure only)
- Inventory stored locally only (not in cloud)
- Access controlled via file permissions
- Changes logged for audit trail

## Troubleshooting

### Git Shows Inventory as Untracked

**Cause**: `.gitignore` not working correctly

**Solution**:
```bash
# Verify gitignore pattern
git check-ignore -v ansible/inventory/production.yml

# Should output:
# .gitignore:81:ansible/inventory/production.yml

# If not working, verify .gitignore contains:
grep "ansible/inventory/production.yml" .gitignore
```

### Ansible Cannot Connect to Server

**Cause**: Hostname not resolving or SSH key issues

**Solution**:
```bash
# Test hostname resolution
ping -c 3 grimm-lin

# Test SSH connection directly
ssh grimm@grimm-lin "echo SSH working"

# Check SSH key
ssh-add -l

# Verbose Ansible connection test
ansible grimm-lin -i ansible/inventory/production.yml -m ping -vvv
```

### "Permission Denied" During Deployment

**Cause**: User lacks sudo privileges or wrong user

**Solution**:
```bash
# Verify sudo access
ansible grimm-lin \
  -i ansible/inventory/production.yml \
  -m shell \
  -a "sudo whoami"

# Should output: root

# Check ansible_user setting
ansible-inventory -i ansible/inventory/production.yml --list \
  | grep ansible_user
```

## References

- [Ansible Inventory Documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- [MGA SOAP Calculator Deployment Guide](./README.md)
- [Secrets Management](./secrets-management.md)

---

**Document Classification**: CONFIDENTIAL - MGA Automotive
**Last Updated**: 2025-11-02
**Owner**: Bob Patterson / Greysson Infrastructure
