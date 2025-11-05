# Ansible Vault Setup Guide

## Overview

The `build-and-deploy.yml` playbook references an encrypted vault file for sensitive credentials. For deployments where the vault isn't actively used, you have two options:

## Option 1: Temporary Vault Bypass (Quick)

**For image lifecycle deployments that don't need vault secrets:**

```bash
# Edit the playbook temporarily
nano ansible/playbooks/build-and-deploy.yml

# Comment out the vault reference:
# vars_files:
#   - ../group_vars/production/vault.yml

# Run deployment
ansible-playbook playbooks/build-and-deploy.yml -e "app_version=X.Y.Z"

# Restore the vault reference after deployment
```

## Option 2: Vault Password File (Proper)

**For full vault support:**

### 1. Create Vault Password File

```bash
# Create password file (NEVER commit this!)
echo "your-vault-password-here" > ~/.vault_pass.txt
chmod 600 ~/.vault_pass.txt
```

### 2. Update Ansible Configuration

```bash
# Edit ansible.cfg
nano ansible/ansible.cfg

# Add vault password file path
[defaults]
vault_password_file = ~/.vault_pass.txt
```

### 3. Deploy with Vault

```bash
cd ansible
ansible-playbook playbooks/build-and-deploy.yml -e "app_version=X.Y.Z"
```

## Current Vault Contents

The vault file (`ansible/group_vars/production/vault.yml`) is encrypted with AES256.

To view/edit:
```bash
# View vault contents
ansible-vault view ansible/group_vars/production/vault.yml

# Edit vault
ansible-vault edit ansible/group_vars/production/vault.yml

# Create new vault
ansible-vault create ansible/group_vars/production/vault.yml
```

## Security Notes

**NEVER:**
- Commit `~/.vault_pass.txt` to git
- Share vault password in plain text
- Store vault password in project directory

**ALWAYS:**
- Keep vault password in secure password manager
- Add `*.vault_pass*` to `.gitignore`
- Use different vault passwords for prod/staging
- Rotate vault password periodically

## What the Image Lifecycle Needs

The `soap-calculator-image-lifecycle` role does **NOT** actually require vault secrets for:
- Building container images
- Transferring images to servers
- Loading images into Podman
- Restarting systemd services

Secrets are managed on the target server via systemd environment files, not Ansible variables.

## Why the Vault Reference Exists

The vault reference in `build-and-deploy.yml` is a placeholder for future use cases:
- Container registry authentication
- Database credentials for backup operations
- API keys for monitoring services
- SSH keys for deployment automation

Currently, the image lifecycle operates without needing these secrets.

## Deployment Without Vault (Current State)

Since the v1.1.0-purity deployment, we've confirmed that:
1. ✅ Image builds locally without vault
2. ✅ Image transfers to grimm-lin without vault
3. ✅ Podman loads and starts container without vault
4. ✅ Database migrations run via container entrypoint
5. ✅ Application starts with systemd-managed environment

**Conclusion:** For pure image lifecycle operations, the vault is referenced but not used.

## Recommended Approach

**For Now:**
- Use Option 1 (temporary bypass) for deployments
- Document that vault isn't needed for current operations

**For Future:**
- Set up proper vault when adding features that need secrets:
  - Container registry authentication
  - Backup automation with credentials
  - Monitoring service integration
  - Multi-environment secret management

## Quick Reference

```bash
# Deploy without vault (temporary)
# 1. Comment out vault reference in playbook
# 2. Run deployment
ansible-playbook playbooks/build-and-deploy.yml -e "app_version=1.1.0-purity"

# Deploy with vault (proper setup)
ansible-playbook playbooks/build-and-deploy.yml \
  -e "app_version=1.1.0-purity" \
  --vault-password-file ~/.vault_pass.txt

# Alternative: Prompt for password
ansible-playbook playbooks/build-and-deploy.yml \
  -e "app_version=1.1.0-purity" \
  --ask-vault-pass
```
