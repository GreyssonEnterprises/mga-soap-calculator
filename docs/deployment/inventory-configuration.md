# Ansible Inventory Configuration Guide

## Overview

The MGA SOAP Calculator uses Ansible for infrastructure-as-code deployment management. This guide explains how to configure the inventory files for production and staging environments.

## Directory Structure

```
ansible/
├── inventory/
│   ├── production.yml          # Production environment inventory
│   ├── staging.yml             # Staging environment inventory
│   └── group_vars/
│       └── all.yml             # Common variables across all environments
├── group_vars/
│   └── production/
│       └── vault.yml           # Encrypted secrets (Ansible Vault)
└── playbooks/
    └── deploy-soap-calculator.yml  # Main deployment playbook
```

## Inventory Files

### Production Inventory (`inventory/production.yml`)

Primary inventory file for production deployment. Defines the production server configuration and all deployment parameters.

**Host Group**: `mga_production`
**Primary Host**: `mga-production-server`

### Staging Inventory (`inventory/staging.yml`)

Mirrors production structure but with reduced resource allocations for testing deployments before production rollout.

**Host Group**: `mga_staging`
**Primary Host**: `mga-staging-server`

### Common Variables (`inventory/group_vars/all.yml`)

Shared variables across all environments including:
- Container base images
- Application identity
- Directory structure standards
- Security defaults
- Performance tuning parameters

## Configuration Steps

### 1. Configure SSH Access

**Requirements**:
- SSH key-based authentication configured
- User with sudo privileges
- Python 3 installed on target server

**Setup Steps**:

```bash
# Generate SSH key if not exists
ssh-keygen -t ed25519 -C "ansible-deployment"

# Copy public key to production server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@production-server-ip

# Test connection
ssh -i ~/.ssh/id_ed25519 user@production-server-ip

# Configure passwordless sudo (on production server)
echo "deployuser ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible-deploy
```

### 2. Update Production Inventory

Edit `ansible/inventory/production.yml`:

```yaml
# Replace these PLACEHOLDER values:

ansible_host: "192.168.1.100"  # Your production server IP
ansible_user: "deployuser"      # Your deployment user
container_registry_username: "your-ghcr-username"

# Optional: Customize resource limits
api_workers: 4                  # Based on server CPU cores
postgres_memory_limit: "2g"     # Based on available RAM
```

### 3. Configure Secrets with Ansible Vault

**Create Encrypted Vault File**:

```bash
# Navigate to ansible directory
cd ansible/group_vars/production

# Copy vault template
cp vault.yml.example vault.yml

# Edit with your secrets
nano vault.yml

# Encrypt the file
ansible-vault encrypt vault.yml

# Verify encryption
cat vault.yml  # Should show encrypted content
```

**Generate Secure Secrets**:

```bash
# PostgreSQL password
openssl rand -base64 32

# JWT secret key
openssl rand -hex 64

# Container registry password (use your GHCR personal access token)
```

**Vault File Contents**:

```yaml
---
vault_db_password: "your-secure-db-password-here"
vault_jwt_secret_key: "your-64-char-hex-jwt-secret-here"
vault_registry_password: "your-ghcr-token-here"
```

### 4. Verify Ansible Connection

```bash
# Test connectivity
ansible -i inventory/production.yml mga_production -m ping

# Test sudo access
ansible -i inventory/production.yml mga_production -m command -a "whoami" --become

# Gather system facts
ansible -i inventory/production.yml mga_production -m setup | grep ansible_distribution
```

### 5. Review Firewall Requirements

**Required Ports**:
- **SSH (22/tcp)**: Ansible management
- **API (8000/tcp)**: Application access
- **HTTPS (443/tcp)**: If using reverse proxy (future)

**Firewall Configuration** (on production server):

```bash
# Allow SSH
sudo firewall-cmd --permanent --add-service=ssh

# Allow API port
sudo firewall-cmd --permanent --add-port=8000/tcp

# Reload firewall
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-all
```

## Variable Reference

### Critical Variables

| Variable | Description | Example | Location |
|----------|-------------|---------|----------|
| `ansible_host` | Production server IP/hostname | `192.168.1.100` | production.yml |
| `ansible_user` | Deployment user with sudo | `deployuser` | production.yml |
| `vault_db_password` | PostgreSQL password | (encrypted) | vault.yml |
| `vault_jwt_secret_key` | JWT authentication secret | (encrypted) | vault.yml |
| `api_workers` | Uvicorn worker processes | `4` | production.yml |
| `postgres_memory_limit` | PostgreSQL RAM limit | `1g` | production.yml |

### Resource Allocation Guidelines

**Small Server (2 CPU, 4GB RAM)**:
```yaml
api_workers: 2
api_memory_limit: "512m"
postgres_memory_limit: "1g"
```

**Medium Server (4 CPU, 8GB RAM)**:
```yaml
api_workers: 4
api_memory_limit: "1g"
postgres_memory_limit: "2g"
```

**Large Server (8 CPU, 16GB RAM)**:
```yaml
api_workers: 8
api_memory_limit: "2g"
postgres_memory_limit: "4g"
```

### Network Configuration

**Default Podman Network**:
```yaml
podman_network_name: "mga-web"
podman_network_subnet: "10.89.0.0/24"
podman_network_gateway: "10.89.0.1"
```

**Custom Network** (if conflicts with existing infrastructure):
```yaml
podman_network_name: "mga-custom"
podman_network_subnet: "10.100.0.0/24"
podman_network_gateway: "10.100.0.1"
```

## Environment-Specific Customization

### Production Environment

**Characteristics**:
- High availability requirements
- Resource allocation prioritized
- Automatic backups enabled
- Monitoring and alerting configured
- Conservative log levels (INFO)

**Recommended Settings**:
```yaml
api_log_level: "INFO"
backup_enabled: true
backup_retention_days: 30
monitoring_enabled: true
auto_updates_enabled: true
```

### Staging Environment

**Characteristics**:
- Testing and validation focus
- Reduced resource allocation
- Verbose logging for debugging
- Test data refresh capabilities
- Debug endpoints enabled

**Recommended Settings**:
```yaml
api_log_level: "DEBUG"
backup_retention_days: 7
enable_api_debug_endpoints: true
enable_performance_profiling: true
```

## Security Best Practices

### 1. SSH Security

```yaml
# Use SSH keys, never passwords
ansible_ssh_private_key_file: "~/.ssh/mga_production_key"

# Disable password authentication (on server)
# /etc/ssh/sshd_config:
# PasswordAuthentication no
# PubkeyAuthentication yes
```

### 2. Ansible Vault

```bash
# Always encrypt sensitive data
ansible-vault encrypt group_vars/production/vault.yml

# Use vault password file (secure location)
echo "your-vault-password" > ~/.ansible/vault_password
chmod 600 ~/.ansible/vault_password

# Reference in ansible.cfg
vault_password_file = ~/.ansible/vault_password
```

### 3. Secret Rotation

```bash
# Rotate database password
1. Edit vault.yml with new password
2. Re-encrypt: ansible-vault encrypt vault.yml
3. Deploy: ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml
4. Verify: Check application health
```

### 4. Access Control

- Limit SSH access to deployment host IPs
- Use bastion/jump host for production access
- Enable audit logging for all privileged operations
- Regular security updates via auto-updates

## Testing Inventory Configuration

### Syntax Validation

```bash
# Check YAML syntax
ansible-inventory -i inventory/production.yml --list --yaml

# Verify variable inheritance
ansible-inventory -i inventory/production.yml --host mga-production-server
```

### Connection Testing

```bash
# Ping test
ansible -i inventory/production.yml mga_production -m ping

# Check Python availability
ansible -i inventory/production.yml mga_production -m command -a "python3 --version"

# Verify Podman installation
ansible -i inventory/production.yml mga_production -m command -a "podman --version"
```

### Dry Run Deployment

```bash
# Dry run deployment (check mode)
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml --check

# Diff mode (show what would change)
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml --check --diff
```

## Troubleshooting

### Connection Issues

**Problem**: "Permission denied (publickey)"
```bash
# Solution: Verify SSH key and user
ssh -v -i ~/.ssh/id_ed25519 user@server-ip

# Check authorized_keys on server
cat ~/.ssh/authorized_keys
```

**Problem**: "sudo: a password is required"
```bash
# Solution: Configure passwordless sudo
echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible
```

### Inventory Variable Issues

**Problem**: Variables not being applied
```bash
# Check variable precedence
ansible-inventory -i inventory/production.yml --host mga-production-server --yaml

# Verify group_vars loaded
ansible-inventory -i inventory/production.yml --list --yaml | grep -A 20 mga_production
```

### Vault Decryption Issues

**Problem**: "ERROR! Decryption failed"
```bash
# Verify vault password
ansible-vault view group_vars/production/vault.yml

# Re-encrypt with correct password
ansible-vault rekey group_vars/production/vault.yml
```

## Multi-Environment Deployment

### Deploying to Staging

```bash
ansible-playbook -i inventory/staging.yml playbooks/deploy-soap-calculator.yml
```

### Deploying to Production

```bash
# With confirmation prompt
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml

# With vault password prompt
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml --ask-vault-pass
```

### Targeting Specific Hosts

```bash
# Deploy to specific host
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml --limit mga-production-server

# Deploy to subset of hosts
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml --limit "mga-production-server,mga-backup-server"
```

## Advanced Configuration

### Custom SSH Configuration

Create `~/.ssh/config`:

```
Host mga-production
    HostName 192.168.1.100
    User deployuser
    IdentityFile ~/.ssh/mga_production_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

Then use in inventory:
```yaml
ansible_host: "mga-production"
```

### Dynamic Inventory

For cloud environments, consider dynamic inventory:

```python
# inventory/dynamic_inventory.py
#!/usr/bin/env python3
# Fetch inventory from cloud provider API
```

### Inventory Plugins

Use Ansible inventory plugins for advanced scenarios:

```yaml
# inventory/production.yml
plugin: constructed
strict: false
compose:
  ansible_host: server_ip
  deployment_environment: environment_tag
```

## Maintenance

### Regular Updates

```bash
# Update server packages (via Ansible)
ansible -i inventory/production.yml mga_production -m yum -a "name=* state=latest" --become

# Update Podman
ansible -i inventory/production.yml mga_production -m yum -a "name=podman state=latest" --become
```

### Backup Inventory

```bash
# Version control (recommended)
git add ansible/inventory/
git commit -m "Update production inventory configuration"

# Manual backup
tar -czf inventory-backup-$(date +%Y%m%d).tar.gz ansible/inventory/
```

### Inventory Auditing

```bash
# List all hosts
ansible-inventory -i inventory/production.yml --graph

# Export inventory to JSON
ansible-inventory -i inventory/production.yml --list > inventory-audit.json

# Check for undefined variables
ansible-playbook --syntax-check -i inventory/production.yml playbooks/deploy-soap-calculator.yml
```

## References

- [Ansible Inventory Documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- [Ansible Vault Best Practices](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [Podman System Service](https://docs.podman.io/en/latest/markdown/podman-system-service.1.html)
- [Fedora Server Documentation](https://docs.fedoraproject.org/en-US/fedora-server/)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Ansible logs: `/var/log/ansible.log`
3. Verify server logs: `journalctl -u mga-postgres.service -u soap-calculator-api.service`
4. Contact infrastructure team
