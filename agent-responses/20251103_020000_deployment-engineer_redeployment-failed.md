# Deployment Engineer Response - MGA SOAP Calculator Redeployment FAILED

**Timestamp:** 2025-11-03T02:00:00-08:00
**Task:** Complete MGA SOAP Calculator redeployment on grimm-lin (Fedora 42 rootless Podman)
**Requestor:** Bob PAI Orchestrator
**Session ID:** mga-redeployment-20251103

## Response

### DEPLOYMENT FAILED - ROOT CAUSE IDENTIFIED

The redeployment failed because **the Ansible playbook itself has NOT been corrected for rootless Podman**. The claimed "fixes applied" were NOT present in the actual deployment configuration.

## Execution Log

### Phase 1: Cleanup (SUCCESSFUL)

**Stopped broken services:**
```
ssh grimm@grimm-lin "systemctl --user stop mga-postgres.service mga-api.service"
```

**Result:**
- mga-postgres.service: stopped (was in activating/auto-restart loop)
- mga-api.service: stopped (was inactive)
- mga-network-network.service: not found (incorrect naming)

**Removed incorrect Quadlet files:**
```
ansible grimm-lin -m shell -a "rm -f /etc/containers/systemd/*.{container,network}" --become
```

**Files removed from /etc/containers/systemd/:**
- mga-network.network
- mga-postgres.container
- soap-calculator-api.container

**Daemon reload:**
```
ssh grimm@grimm-lin "systemctl --user daemon-reload && sudo systemctl daemon-reload"
```

**Result:** Both user and system daemons reloaded successfully

### Phase 2: Deployment (FAILED)

**Command executed:**
```bash
cd /Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/ansible
ansible-playbook -i inventory/production.yml playbooks/deploy-soap-calculator.yml \
  --vault-password-file ~/.config/pai/secrets/ansible_vault_pw -v
```

**Playbook execution:**
```
PLAY [Deploy MGA SOAP Calculator (API + PostgreSQL Containers)] ****************

TASK [Gathering Facts] *********************************************************
ok: [grimm-lin]

TASK [Ensure configuration directory exists] ***********************************
ok: [grimm-lin]

TASK [Ensure PostgreSQL data volume exists] ************************************
ok: [grimm-lin]

TASK [Deploy PostgreSQL environment file] **************************************
changed: [grimm-lin]

TASK [Deploy API environment file] *********************************************
changed: [grimm-lin]

TASK [Deploy Quadlet network unit] *********************************************
changed: [grimm-lin] => dest: /etc/containers/systemd/mga-network.network

TASK [Deploy Quadlet PostgreSQL container unit] ********************************
changed: [grimm-lin] => dest: /etc/containers/systemd/mga-postgres.container

TASK [Deploy Quadlet API container unit] ***************************************
changed: [grimm-lin] => dest: /etc/containers/systemd/soap-calculator-api.container

TASK [Reload systemd daemon to recognize new Quadlet units] ********************
RUNNING HANDLER [daemon-reload] ************************************************
ok: [grimm-lin]

RUNNING HANDLER [restart postgres service] *************************************
fatal: [grimm-lin]: FAILED!
  Module failed: Unable to restart service mga-postgres.service
  Job for mga-postgres.service failed because the control process exited with error code.
```

**FAILURE POINT:** System-level systemd cannot start rootless containers

### Root Cause Analysis

**The playbook `deploy-soap-calculator.yml` has INCORRECT configuration:**

1. **Wrong scope:** `become: true` (line 4) - operates at root/system level
2. **Wrong Quadlet directory:** `quadlet_dir: "/etc/containers/systemd"` (line 14) - should be `/home/grimm/.config/containers/systemd`
3. **Wrong systemd invocation:** Uses system systemd, not `systemd_scope: user`
4. **Wrong volume location:** Creates system volumes, not user volumes
5. **Wrong UID assumption:** Code references UID 501, but actual user is UID 1000

**What the playbook SHOULD be:**
```yaml
- name: Deploy MGA SOAP Calculator (API + PostgreSQL Containers)
  hosts: mga_production
  become: false  # MUST be false for rootless
  vars:
    quadlet_dir: "/home/grimm/.config/containers/systemd"  # User location
    config_dir: "/home/grimm/.config/mga-soap-calculator"   # User config

  tasks:
    - name: Ensure loginctl enable-linger
      command: loginctl enable-linger grimm
      become: true  # This ONE task needs root

    - name: Deploy Quadlet files
      copy:
        dest: "{{ quadlet_dir }}/..."
        owner: grimm
        group: grimm

    - name: Reload user systemd
      systemd:
        scope: user  # CRITICAL
        daemon_reload: true

    - name: Start services
      systemd:
        scope: user  # CRITICAL
        name: mga-postgres.service
        state: started
```

### Current State

**Services:**
- mga-postgres.service: FAILED (system scope, can't start rootless container)
- mga-api.service: NOT STARTED (blocked by postgres failure)
- mga-network.service: NOT CREATED (wrong Quadlet location)

**Quadlet files:**
- Location: /etc/containers/systemd/ (WRONG - should be ~/.config/containers/systemd/)
- Scope: System (WRONG - should be user)

**Containers:**
```
ssh grimm@grimm-lin "podman ps -a"
CONTAINER ID  IMAGE  COMMAND  CREATED  STATUS  PORTS  NAMES
(none - no containers running or exist)
```

**User environment:**
- User: grimm
- UID: 1000 (NOT 501 as assumed in requirements)
- HOME: /home/grimm
- XDG_RUNTIME_DIR: /run/user/1000

### Required Fixes

**The deployment playbook needs COMPLETE REWRITE for rootless:**

1. Remove `become: true` from play level
2. Change `quadlet_dir` to `/home/grimm/.config/containers/systemd`
3. Change `config_dir` to `/home/grimm/.config/mga-soap-calculator`
4. Add `loginctl enable-linger grimm` task (with become: true)
5. Add `scope: user` to ALL systemd module invocations
6. Change file ownership to `grimm:grimm` (UID 1000)
7. Use `XDG_RUNTIME_DIR=/run/user/1000` for systemd bus
8. Create user-scoped volumes: `podman --remote=false volume create`

### Truth Assessment

**CLAIMED:** "Fixes applied: All Ansible roles updated for user systemd"
**REALITY:** The playbook has NOT been updated. It's still system-scoped.

**CLAIMED:** "Network subnet changed to 10.90.0.0/24"
**REALITY:** Cannot verify - deployment never reached network creation

**CLAIMED:** "Configuration: Fedora 42 rootless Podman, user grimm (UID 501)"
**REALITY:** User grimm is UID 1000, not 501

## Metadata
- **Completion Status:** FAILED - Playbook not corrected for rootless Podman
- **Confidence Level:** HIGH - Root cause clearly identified
- **Processing Time:** ~10 minutes
- **Token Usage:** ~88K tokens
- **Follow-up Required:** YES - Complete playbook rewrite needed
- **Referenced Files:**
  - ansible/playbooks/deploy-soap-calculator.yml (INCORRECT)
  - ansible/inventory/production.yml
  - podman/systemd/*.{container,network}
- **Dependencies:** Ansible playbook must be corrected before redeployment possible
- **Validation Status:** FAILED - Cannot proceed to validation phases

## Cross-References
- **Parent Task:** MGA SOAP Calculator redeployment orchestration
- **Blocking Issue:** Playbook architecture incompatible with rootless Podman
- **Required Action:** Rewrite ansible/playbooks/deploy-soap-calculator.yml

## Critical Findings

### 1. Systematic Scope Mismatch
The entire playbook operates at system level (`become: true`, system paths, system systemd) while attempting to manage rootless user containers. This is architecturally impossible.

### 2. Incorrect Requirements
The original task requirements stated "fixes applied" but no fixes exist in the codebase. The playbook has never been adapted for rootless operation.

### 3. UID Mismatch
Documentation references UID 501, actual user is UID 1000. This suggests the requirements were written for a different system or user.

### 4. Path Confusion
Mixing system paths (`/etc/containers/systemd`) with rootless container operations creates an unresolvable conflict. System-level Quadlet files cannot manage user-scoped containers.

## Recommendations

**IMMEDIATE ACTION REQUIRED:**

1. **Rewrite playbook** for rootless architecture:
   - Remove system-level operations
   - Use user paths and user systemd scope
   - Correct UID references (1000, not 501)

2. **Test playbook changes** in development before production

3. **Update documentation** to reflect actual system configuration

4. **Verify all assumptions** before claiming "fixes applied"

## Notes

This failure exemplifies the importance of brutal honesty in infrastructure operations. Claiming "fixes applied" when the playbook has not been modified creates false confidence and wastes deployment time.

The deployment did not fail due to execution errors - it failed due to fundamental architectural incompatibility between system-scoped Ansible operations and rootless Podman requirements.

**DEPLOYMENT STATUS: FAILED**
**SYSTEM STATE: Partially configured (env files deployed, Quadlet files in wrong location)**
**NEXT STEP: Correct playbook architecture, do NOT attempt redeployment until playbook rewritten**
