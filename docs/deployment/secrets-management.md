# Secrets Management - MGA SOAP Calculator

> **CONFIDENTIAL** - MGA Automotive Client Infrastructure

## Overview

This document describes how production secrets are managed for the MGA SOAP Calculator deployment using Ansible Vault encryption.

## Vault Password Location

**Path**: `~/.config/pai/secrets/ansible_vault_pw`

**Security**:
- File permissions: `600` (owner read/write only)
- Never commit this file to version control
- Backup securely to password manager
- Required for all vault operations

## Vault File Location

**Path**: `ansible/group_vars/production/vault.yml`

**Status**: Encrypted with Ansible Vault (AES256)

**Contents** (encrypted):
- Database password (PostgreSQL)
- JWT secret key
- Database connection URL
- Application secret keys

## Common Operations

### View Vault Contents

To view decrypted vault contents:

```bash
ansible-vault view \
  ansible/group_vars/production/vault.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

### Edit Vault Contents

To modify vault contents:

```bash
ansible-vault edit \
  ansible/group_vars/production/vault.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

This opens the decrypted vault in your default editor (`$EDITOR`). Changes are automatically re-encrypted on save.

### Decrypt Vault (Temporary)

**WARNING**: Use with extreme caution. Only for debugging.

```bash
ansible-vault decrypt \
  ansible/group_vars/production/vault.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

**CRITICAL**: Always re-encrypt immediately:

```bash
ansible-vault encrypt \
  ansible/group_vars/production/vault.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

### Verify Encryption Status

Check if vault is encrypted:

```bash
head -n 1 ansible/group_vars/production/vault.yml
# Should output: $ANSIBLE_VAULT;1.1;AES256
```

## Secret Rotation Procedures

### When to Rotate Secrets

- Quarterly (scheduled)
- After security incident
- When team member with vault access leaves
- After any potential exposure

### Rotation Process

1. **Generate new secrets**:
   ```bash
   # Database password (32 bytes, base64)
   NEW_DB_PASSWORD=$(openssl rand -base64 32)

   # JWT secret key (64 bytes, hex)
   NEW_JWT_SECRET=$(openssl rand -hex 64)

   echo "DB_PASSWORD=$NEW_DB_PASSWORD"
   echo "JWT_SECRET=$NEW_JWT_SECRET"
   ```

2. **Update vault**:
   ```bash
   ansible-vault edit \
     ansible/group_vars/production/vault.yml \
     --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
   ```

3. **Deploy updated secrets**:
   ```bash
   cd ansible
   ansible-playbook playbooks/deploy.yml \
     -i inventory/production.yml \
     --vault-password-file ~/.config/pai/secrets/ansible_vault_pw \
     --tags secrets
   ```

4. **Verify services still functioning**:
   ```bash
   # Check API health
   curl http://grimm-lin:8000/health

   # Check database connectivity
   ansible grimm-lin \
     -i inventory/production.yml \
     -m shell \
     -a "podman exec mga-postgres psql -U postgres -d mga_soap_calculator -c 'SELECT 1;'"
   ```

5. **Document rotation**:
   - Update `docs/deployment/security-audit-log.md`
   - Note date, person, reason for rotation

## Emergency Access Procedures

### Vault Password Lost

If vault password is lost:

1. **DO NOT PANIC** - Data is not lost, just encrypted
2. Contact Bob Patterson immediately
3. Vault password backup exists in secure location
4. Last resort: Regenerate all secrets and re-deploy

### Vault File Corrupted

If vault file is corrupted or accidentally deleted:

1. Restore from backup (automated daily backups in `/var/backups/mga-soap-calculator/`)
2. Check git history (if vault was previously committed encrypted)
3. Last resort: Regenerate secrets and re-deploy

### Vault Accidentally Committed Unencrypted

**CRITICAL SECURITY INCIDENT**

1. **Immediately rotate ALL secrets** in vault
2. **Force push to remove from Git history**:
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch ansible/group_vars/production/vault.yml' \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```
3. **Notify security team**
4. **Review access logs** for potential compromise
5. **Deploy new secrets immediately**

## Security Best Practices

### DO

✅ Keep vault password file permissions at `600`
✅ Always use `--vault-password-file` flag (never type password)
✅ Verify encryption status before committing
✅ Use cryptographically strong secrets (32+ bytes)
✅ Rotate secrets quarterly
✅ Backup vault password securely (password manager)
✅ Document all secret rotations

### DO NOT

❌ Commit unencrypted vault files
❌ Share vault password via email/chat
❌ Store vault password in plaintext files
❌ Decrypt vault in production servers
❌ Use weak or predictable secrets
❌ Skip verification after vault operations
❌ Ignore ansible-vault encryption warnings

## Troubleshooting

### "Decryption failed" Error

**Cause**: Wrong vault password

**Solution**: Verify password file contents:
```bash
cat ~/.config/pai/secrets/ansible_vault_pw
```

Check for trailing newlines or whitespace.

### Vault File Not Encrypted

**Cause**: Encryption failed or was skipped

**Solution**: Encrypt immediately:
```bash
ansible-vault encrypt \
  ansible/group_vars/production/vault.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

### Git Showing Vault as Modified

**Cause**: `.gitignore` not configured correctly

**Solution**: Verify gitignore:
```bash
git check-ignore -v ansible/group_vars/production/vault.yml
# Should show: .gitignore:76:ansible/group_vars/production/vault.yml
```

## Compliance Notes

### MGA Automotive Requirements

- Secrets MUST be encrypted at rest
- Access MUST be logged and auditable
- Rotation MUST occur quarterly minimum
- Incidents MUST be reported within 24 hours

### Red Hat Data Protection

- No customer data in vault (infrastructure secrets only)
- Vault password stored locally only (not in cloud)
- All vault operations use approved local tools

## Audit Log

Maintain security audit log at: `docs/deployment/security-audit-log.md`

**Required entries**:
- Date of secret rotation
- Person performing rotation
- Reason for rotation
- Verification results

## References

- [Ansible Vault Documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [MGA SOAP Calculator Deployment Guide](./README.md)
- [Inventory Security](./inventory-security.md)

---

**Document Classification**: CONFIDENTIAL - MGA Automotive
**Last Updated**: 2025-11-02
**Owner**: Bob Patterson / Greysson Infrastructure
