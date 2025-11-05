# Deployment Engineer - Additive Vault Deployment
**Timestamp:** 2025-11-05T13:00:00Z
**Task:** Document vault password location and deploy additive calculator fix
**Requestor:** Bob

## Response

### Part 1: Documentation Complete

Created project-specific `CLAUDE.md` with:
- Ansible vault password location: `~/.config/pai/secrets/ansible_vault_pw`
- Deployment command examples
- Project context and tech stack overview
- Reference to full deployment documentation

Updated `.gitignore` to exclude `CLAUDE.md` (prevents accidental commit of sensitive paths).

### Part 2: Deployment Executed

**Deployment Command:**
```bash
cd ansible
ansible-playbook playbooks/build-and-deploy.yml \
  -e "app_version=1.4.1" \
  -e "run_migration=false" \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
```

**Initial Issue:** First deployment used `image_tag` parameter which was ignored - ansible role defaults to `app_version=1.0.0`.

**Resolution:** Redeployed with correct `app_version=1.4.1` parameter.

**Build Results:**
- Image ID: 8b47148b6865
- Archive: /tmp/mga-builds/mga-soap-calculator-1.4.1.tar.gz
- Size: 423.63 MB
- SHA256: da8cf6fb235236970980cf3f8e9834dc59c05e7092897709f6b1070537109296

**Deployment Status:** SUCCESS
- Health check: PASSED
- API endpoints validated: oils, additives
- Version tag: 1.4.1
- Container running on grimm-lin

**Note:** Deployment succeeded but cleanup task failed due to undefined `keep_archives_count` variable. This is non-critical - application is running correctly.

### Part 3: Verification Results

**Health Check:**
```bash
curl http://grimm-lin:8000/api/v1/health
```
Result: `{"status":"healthy","database":"connected","version":"1.0.0"}`

**Note:** Version reports "1.0.0" because `app/main.py:28` hardcodes OpenAPI version. This is documentation metadata only and does not reflect actual deployed code version.

**Ingredient Counts:**
- Additives: 30 ✅
- Essential Oils: 39 ✅
- Colorants: 79 ✅
- **Total: 148 ingredients** (target was 137+)

**Recommendation Calculations - WORKING:**

Test 1 - Sodium Lactate (1000g batch):
```json
{
  "light": {"amount_g": 10.0, "amount_oz": 0.35, "usage_percentage": 1.0},
  "standard": {"amount_g": 20.0, "amount_oz": 0.71, "usage_percentage": 2.0},
  "heavy": {"amount_g": 30.0, "amount_oz": 1.06, "usage_percentage": 3.0}
}
```

Test 2 - Honey (500g batch):
```json
{
  "light": {"amount_g": 5.0, "amount_oz": 0.18, "usage_percentage": 1.0},
  "standard": {"amount_g": 10.0, "amount_oz": 0.35, "usage_percentage": 2.0},
  "heavy": {"amount_g": 15.0, "amount_oz": 0.53, "usage_percentage": 3.0}
}
```

**Calculations Verified:** All three usage levels (light/standard/heavy) calculate correctly based on:
- Light: `(batch_size_g * min_percent) / 100`
- Standard: `(batch_size_g * avg_percent) / 100`
- Heavy: `(batch_size_g * max_percent) / 100`

### Deployment Architecture Notes

**Container Runtime:**
- Using Podman with systemd Quadlet
- Service: `soap-calculator-api.service`
- Container name: `soap-api`
- Image: `localhost/mga-soap-calculator:latest` (pointing to 8b47148b6865)

**Issue Discovered:** Quadlet `.container` file hardcoded previous image tag (`v1.4.0-additives`). Updated to use `latest` tag for future deployments to pick up new images automatically.

**Fixed via:**
```bash
sed -i 's/Image=localhost\/mga-soap-calculator:v1.4.0-additives/Image=localhost\/mga-soap-calculator:latest/' \
  ~/.config/containers/systemd/soap-calculator-api.container
systemctl --user daemon-reload
systemctl --user restart soap-calculator-api.service
```

### Future Deployment Considerations

**Ansible Role Enhancement Needed:**
The `soap-calculator-image-lifecycle` role should update the Quadlet `.container` file with the new image version during deployment, not just restart the service. Currently it:
1. Builds image with version tag
2. Tags as `latest`
3. Restarts service

But the Quadlet file maintains its hardcoded image reference.

**Recommended Fix:**
Add task to role to update Quadlet file:
```yaml
- name: Update Quadlet image reference
  lineinfile:
    path: "{{ ansible_env.HOME }}/.config/containers/systemd/soap-calculator-api.container"
    regexp: '^Image='
    line: "Image=localhost/mga-soap-calculator:latest"
  notify: Reload systemd and restart service
```

**Variable Naming Clarity:**
- `app_version` (used by ansible role) != `image_tag` (not recognized)
- Consider standardizing on single variable name

## Metadata
- Status: Complete
- Confidence: High
- Follow-up: Update ansible role to manage Quadlet file references
- Files:
  - CLAUDE.md (new)
  - .gitignore (updated)
  - Deployed v1.4.1 to grimm-lin

## Summary

✅ **CLAUDE.md created** with vault password documentation
✅ **.gitignore updated** (CLAUDE.md excluded)
✅ **Deployed to grimm-lin** successfully (v1.4.1)
✅ **Recommendations calculate** correctly (smart additive calculator FIXED)
✅ **All 148 ingredients** accessible via API
✅ **Health checks passing**

**Production URL:** http://grimm-lin:8000

The additive calculator fix (Feature 004) is now live in production with working recommendation calculations. Vault password documented for future automated deployments.
