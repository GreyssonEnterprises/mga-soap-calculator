# Container Image Build & Deployment Architecture
## MGA Soap Calculator API - DevOps Design Document

**Author**: DevOps Architect (Bob PAI)
**Date**: 2025-11-04
**Status**: Design Specification
**Target**: grimm-lin (Fedora 42, Rootless Podman)

---

## Executive Summary

You've got a FastAPI application that needs container image lifecycle management - build, transfer, deploy, rollback. The critical constraint is that images MUST be stored in `/data/podman-apps/` not `/opt` (which you specified explicitly, so I'm assuming there's a good reason like disk space or partition structure).

Current state: You have Ansible automation that deploys containers, but it assumes images either exist locally or can be pulled from a registry. You need the **full lifecycle** - from development build through production deployment with proper versioning and rollback capability.

**Key Design Decisions**:
1. **Build locally** with version tagging (semantic versioning + timestamp)
2. **Export as tar** for transfer (not pushing to registry - keeping it simple)
3. **Transfer to `/data/podman-apps/`** on grimm-lin
4. **Load and tag** in Podman, update systemd units
5. **Health check validation** before marking deployment successful
6. **Rollback capability** by keeping previous image tagged and ready

---

## Current State Analysis

### What You Have (and it's not terrible)

**Ansible Playbook** (`deploy-soap-calculator.yml`):
- ✅ Proper rootless Podman setup with `XDG_RUNTIME_DIR`
- ✅ Quadlet systemd integration (modern approach)
- ✅ Health checks for both PostgreSQL and API
- ✅ Network isolation with custom bridge
- ✅ Environment file templating with vault secrets

**Dockerfile**:
- ✅ Multi-stage build (builder + runtime)
- ✅ Red Hat UBI 9 base images (enterprise-friendly)
- ✅ Non-root user execution (UID 1001)
- ✅ Proper health check definition
- ✅ Wheel-based dependency installation (faster, repeatable)

**Quadlet Units**:
- ✅ Proper service dependencies (`Requires=mga-postgres.service`)
- ✅ Health check configuration in container unit
- ✅ Resource limits (1G memory)
- ✅ Restart policies

### What You Don't Have (yet)

❌ **Image versioning strategy** - everything is `:latest` (scary for rollback)
❌ **Image transfer automation** - no mechanism to get images to grimm-lin
❌ **Image storage in `/data/podman-apps/`** - playbook doesn't reference this path
❌ **Rollback procedure** - no previous image preservation
❌ **Build automation** - Dockerfile exists, but no build playbook
❌ **Deployment validation** - health checks exist, but no rollback trigger

---

## Architecture Design

### Image Lifecycle Stages

```
┌─────────────┐
│   BUILD     │  Development machine (current Mac/grimm-lin)
│  (local)    │  → Build image with new code
│             │  → Tag with version + timestamp
│             │  → Test basic functionality
└──────┬──────┘
       │
       ▼ podman save → tar.gz
┌─────────────┐
│  TRANSFER   │  scp/rsync to grimm-lin
│             │  → Export image as archive
│             │  → Transfer to /data/podman-apps/
│             │  → Verify checksum
└──────┬──────┘
       │
       ▼ podman load
┌─────────────┐
│   DEPLOY    │  grimm-lin Podman + systemd
│             │  → Load image from archive
│             │  → Tag as :latest (new)
│             │  → Keep previous :latest as :rollback
│             │  → Restart systemd services
│             │  → Health check validation
└──────┬──────┘
       │
       ├─ SUCCESS → Clean up old archives
       └─ FAILURE → ROLLBACK (restore previous :latest)
```

### Versioning Strategy

**Semantic Version + Timestamp**:
```
mga-soap-calculator:v1.2.3-20251104-102614
                     │       │         └─ Time (HHmmss)
                     │       └─ Date (YYYYMMDD)
                     └─ Version (major.minor.patch)
```

**Tag Aliases** (managed by deployment):
- `localhost/mga-soap-calculator:latest` - Current production
- `localhost/mga-soap-calculator:rollback` - Previous version (safety net)
- `localhost/mga-soap-calculator:v1.2.3-20251104-102614` - Specific version (permanent)

### Storage Architecture

**Development Machine** (wherever you build):
```
~/.local/share/containers/storage/  # Podman image storage
/tmp/mga-builds/                    # Temporary build artifacts
```

**Production Server** (grimm-lin):
```
/data/podman-apps/
├── mga-soap-calculator/
│   ├── images/
│   │   ├── mga-soap-calculator-v1.2.3-20251104-102614.tar.gz
│   │   ├── mga-soap-calculator-v1.2.2-20251103-141522.tar.gz
│   │   └── CHECKSUMS.sha256
│   ├── current -> images/mga-soap-calculator-v1.2.3-20251104-102614.tar.gz
│   └── rollback -> images/mga-soap-calculator-v1.2.2-20251103-141522.tar.gz
│
/home/grimm/.local/share/containers/storage/  # Podman rootless storage
```

**Why `/data/podman-apps/`?**
- You specified this explicitly (so I'm trusting you have a reason)
- Probably larger disk space than `/opt`
- Separate from system partitions
- Easy to mount/manage/backup separately

---

## Ansible Implementation Design

### New Role: `soap-calculator-image-lifecycle`

**Purpose**: Manage complete image build → transfer → deploy → rollback cycle.

**Structure**:
```
ansible/roles/soap-calculator-image-lifecycle/
├── defaults/
│   └── main.yml              # Version, paths, settings
├── tasks/
│   ├── main.yml              # Orchestration entry point
│   ├── build.yml             # Local image build
│   ├── export.yml            # Export to tar.gz
│   ├── transfer.yml          # Transfer to grimm-lin
│   ├── load.yml              # Load into Podman on target
│   ├── deploy.yml            # Update systemd, restart services
│   ├── validate.yml          # Health checks
│   └── rollback.yml          # Emergency rollback procedure
├── templates/
│   └── version-tag.j2        # Generate version string
└── handlers/
    └── main.yml              # Service restart handlers
```

### Task Breakdown

#### 1. Build Task (`tasks/build.yml`)

**Purpose**: Build container image with new code on development machine.

**Operations**:
```yaml
- name: Generate version tag
  set_fact:
    image_version: "v{{ app_version }}-{{ ansible_date_time.date | replace('-','') }}-{{ ansible_date_time.time | replace(':','') }}"
    image_full_tag: "localhost/mga-soap-calculator:v{{ app_version }}-{{ timestamp }}"

- name: Build container image
  containers.podman.podman_image:
    name: "localhost/mga-soap-calculator"
    tag: "{{ image_version }}"
    path: "{{ project_root }}"
    build:
      file: "{{ project_root }}/Dockerfile"
      cache: true
      force_rm: true
    state: build
  delegate_to: localhost

- name: Tag as latest for testing
  command: podman tag localhost/mga-soap-calculator:{{ image_version }} localhost/mga-soap-calculator:latest
  delegate_to: localhost

- name: Test image locally
  command: podman run --rm --health-cmd "curl -f http://localhost:8000/health" localhost/mga-soap-calculator:latest
  delegate_to: localhost
  timeout: 30
```

**Variables Required**:
- `app_version`: Semantic version (e.g., "1.2.3")
- `project_root`: Path to repository with Dockerfile
- `timestamp`: Auto-generated from Ansible facts

#### 2. Export Task (`tasks/export.yml`)

**Purpose**: Export built image as tar.gz archive for transfer.

**Operations**:
```yaml
- name: Create local build artifacts directory
  file:
    path: "/tmp/mga-builds"
    state: directory
    mode: '0755'
  delegate_to: localhost

- name: Export image as tar archive
  command: >
    podman save
    --format oci-archive
    --output /tmp/mga-builds/mga-soap-calculator-{{ image_version }}.tar
    localhost/mga-soap-calculator:{{ image_version }}
  delegate_to: localhost

- name: Compress archive
  archive:
    path: "/tmp/mga-builds/mga-soap-calculator-{{ image_version }}.tar"
    dest: "/tmp/mga-builds/mga-soap-calculator-{{ image_version }}.tar.gz"
    format: gz
    remove: true
  delegate_to: localhost

- name: Generate checksum
  stat:
    path: "/tmp/mga-builds/mga-soap-calculator-{{ image_version }}.tar.gz"
    checksum_algorithm: sha256
  register: archive_stat
  delegate_to: localhost

- name: Record checksum
  copy:
    content: "{{ archive_stat.stat.checksum }}  mga-soap-calculator-{{ image_version }}.tar.gz\n"
    dest: "/tmp/mga-builds/CHECKSUMS.sha256"
  delegate_to: localhost
```

**Why OCI Archive?**
- Standard format
- Includes all layers + metadata
- Portable across Podman/Docker
- Compressed well with gzip

#### 3. Transfer Task (`tasks/transfer.yml`)

**Purpose**: Transfer image archive to grimm-lin at `/data/podman-apps/`.

**Operations**:
```yaml
- name: Ensure remote image storage directory exists
  file:
    path: "/data/podman-apps/mga-soap-calculator/images"
    state: directory
    owner: grimm
    group: grimm
    mode: '0755'
  become: true

- name: Transfer image archive to grimm-lin
  synchronize:
    src: "/tmp/mga-builds/mga-soap-calculator-{{ image_version }}.tar.gz"
    dest: "/data/podman-apps/mga-soap-calculator/images/"
    compress: false  # Already compressed
    checksum: true
  delegate_to: localhost

- name: Transfer checksum file
  synchronize:
    src: "/tmp/mga-builds/CHECKSUMS.sha256"
    dest: "/data/podman-apps/mga-soap-calculator/images/"
  delegate_to: localhost

- name: Verify transferred archive integrity
  command: >
    sha256sum --check
    /data/podman-apps/mga-soap-calculator/images/CHECKSUMS.sha256
  args:
    chdir: /data/podman-apps/mga-soap-calculator/images
  changed_when: false

- name: Update current symlink
  file:
    src: "/data/podman-apps/mga-soap-calculator/images/mga-soap-calculator-{{ image_version }}.tar.gz"
    dest: "/data/podman-apps/mga-soap-calculator/current"
    state: link
  become: true
```

**Why `synchronize`?**
- Efficient rsync-based transfer
- Built-in checksum verification
- Resume capability on large files
- Compression control

#### 4. Load Task (`tasks/load.yml`)

**Purpose**: Load image from archive into Podman rootless storage.

**Operations**:
```yaml
- name: Preserve previous latest as rollback
  command: >
    podman tag
    localhost/mga-soap-calculator:latest
    localhost/mga-soap-calculator:rollback
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"
  ignore_errors: true  # May not exist on first deployment

- name: Load new image from archive
  command: >
    podman load
    --input /data/podman-apps/mga-soap-calculator/current
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"
  register: image_load

- name: Tag loaded image as latest
  command: >
    podman tag
    localhost/mga-soap-calculator:{{ image_version }}
    localhost/mga-soap-calculator:latest
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"

- name: Verify image is in local storage
  command: podman images localhost/mga-soap-calculator:latest --format "{{.ID}}"
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"
  register: verify_image
  failed_when: verify_image.stdout == ""
```

**Tag Strategy**:
1. Old `:latest` → `:rollback` (safety net)
2. New image loaded with `:v1.2.3-YYYYMMDD-HHmmss` tag
3. New image also tagged as `:latest`
4. Result: 3 tags pointing to 2 images (old rollback, new latest+version)

#### 5. Deploy Task (`tasks/deploy.yml`)

**Purpose**: Restart systemd services with new image.

**Operations**:
```yaml
- name: Update Quadlet unit if needed
  copy:
    src: "{{ playbook_dir }}/../../podman/systemd/soap-calculator-api.container"
    dest: "/home/grimm/.config/containers/systemd/soap-calculator-api.container"
    owner: grimm
    group: grimm
    mode: '0644'
  notify: reload systemd user daemon

- name: Flush handlers to ensure systemd reload
  meta: flush_handlers

- name: Restart API service with new image
  systemd:
    name: soap-calculator-api.service
    state: restarted
    scope: user
    daemon_reload: true
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"

- name: Wait for service to start
  pause:
    seconds: 10
```

**Why flush handlers?**
- Ensures systemd reloads Quadlet definitions before restart
- Critical for new container configurations
- Prevents race conditions

#### 6. Validate Task (`tasks/validate.yml`)

**Purpose**: Verify deployment health, trigger rollback on failure.

**Operations**:
```yaml
- name: Wait for API health endpoint (60s timeout)
  uri:
    url: http://127.0.0.1:8000/health
    status_code: 200
    timeout: 10
  register: health_check
  retries: 6
  delay: 10
  until: health_check.status == 200
  ignore_errors: true

- name: Check new endpoints (oils and additives)
  uri:
    url: "http://127.0.0.1:8000/api/v1/{{ item }}"
    status_code: 200
    timeout: 5
  register: endpoint_check
  loop:
    - oils
    - additives
  ignore_errors: true

- name: Trigger rollback if validation fails
  include_tasks: rollback.yml
  when: health_check.failed or endpoint_check.failed

- name: Mark deployment as successful
  set_fact:
    deployment_status: "success"
  when: not (health_check.failed or endpoint_check.failed)
```

**Validation Gates**:
1. Base health endpoint (existing functionality)
2. New API endpoints (oils, additives)
3. Automatic rollback trigger on any failure

#### 7. Rollback Task (`tasks/rollback.yml`)

**Purpose**: Emergency recovery to previous working image.

**Operations**:
```yaml
- name: Emergency rollback initiated
  debug:
    msg: "ROLLBACK: Health check failed, restoring previous version"

- name: Restore rollback image as latest
  command: >
    podman tag
    localhost/mga-soap-calculator:rollback
    localhost/mga-soap-calculator:latest
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"

- name: Restart service with rollback image
  systemd:
    name: soap-calculator-api.service
    state: restarted
    scope: user
  become: true
  become_user: grimm
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ grimm_uid }}"

- name: Verify rollback health
  uri:
    url: http://127.0.0.1:8000/health
    status_code: 200
    timeout: 10
  register: rollback_health
  retries: 6
  delay: 10
  until: rollback_health.status == 200

- name: Rollback validation
  debug:
    msg: "Rollback {{ 'SUCCESSFUL' if not rollback_health.failed else 'FAILED - MANUAL INTERVENTION REQUIRED' }}"

- name: Fail deployment on rollback
  fail:
    msg: "Deployment failed validation and rollback was executed"
```

**Rollback Safety**:
- Uses pre-preserved `:rollback` tag
- Automatic service restart
- Re-validates health
- Fails playbook to prevent marking as successful

---

## Playbook Integration

### New Playbook: `build-and-deploy-soap-calculator.yml`

**Purpose**: Full lifecycle orchestration from build to deployment.

```yaml
---
- name: Build, Transfer, and Deploy MGA Soap Calculator API
  hosts: mga_production
  vars_files:
    - ../group_vars/production/vault.yml

  vars:
    app_version: "1.2.3"  # Increment on each release
    project_root: "/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator"
    grimm_uid: 1000

  tasks:
    # Local build phase
    - name: Build and export image locally
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: build
      delegate_to: localhost

    - name: Export image as archive
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: export
      delegate_to: localhost

    # Remote deployment phase
    - name: Transfer image to grimm-lin
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: transfer

    - name: Load image into Podman
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: load

    - name: Deploy with systemd
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: deploy

    - name: Validate deployment
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: validate

    # Cleanup on success
    - name: Clean up local build artifacts
      file:
        path: "/tmp/mga-builds"
        state: absent
      delegate_to: localhost
      when: deployment_status == "success"

    - name: Deployment summary
      debug:
        msg: |
          Deployment Status: {{ deployment_status | upper }}
          Image Version: {{ image_version }}
          API Health: http://127.0.0.1:8000/health
```

### Execution Workflow

**Full Deployment**:
```bash
cd /Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/ansible

ansible-playbook playbooks/build-and-deploy-soap-calculator.yml \
  --extra-vars "app_version=1.2.3" \
  --vault-password-file ~/.vault_pass.txt
```

**Quick Rollback** (manual):
```bash
ansible-playbook playbooks/rollback-soap-calculator.yml
```

**Version-Specific Deployment**:
```bash
ansible-playbook playbooks/build-and-deploy-soap-calculator.yml \
  --extra-vars "app_version=1.3.0"
```

---

## Rollback Scenarios

### Scenario 1: Health Check Failure (Automatic)

**Trigger**: API doesn't respond within 60 seconds after restart.

**Action**:
1. Automatic rollback triggered by `validate.yml`
2. Previous `:rollback` tag promoted to `:latest`
3. Service restarted
4. Playbook fails with clear message

**Recovery Time**: ~30 seconds

### Scenario 2: New Endpoint Failure (Automatic)

**Trigger**: `/api/v1/oils` or `/api/v1/additives` returns non-200.

**Action**:
1. Endpoint validation fails in `validate.yml`
2. Same rollback procedure as health check failure
3. Investigation required before retry

**Recovery Time**: ~30 seconds

### Scenario 3: Post-Deployment Discovery (Manual)

**Trigger**: Issue discovered hours/days after deployment.

**Manual Rollback Playbook** (`playbooks/rollback-soap-calculator.yml`):
```yaml
---
- name: Emergency Rollback - MGA Soap Calculator API
  hosts: mga_production
  vars_files:
    - ../group_vars/production/vault.yml

  tasks:
    - name: Execute rollback procedure
      include_role:
        name: soap-calculator-image-lifecycle
        tasks_from: rollback

    - name: Notify operations team
      debug:
        msg: "Manual rollback executed. Review deployment logs before retry."
```

**Execution**:
```bash
ansible-playbook playbooks/rollback-soap-calculator.yml
```

### Scenario 4: Complete Failure (Nuclear Option)

**Trigger**: Both new and rollback images are broken.

**Action**:
```bash
# Load specific known-good version
podman load --input /data/podman-apps/mga-soap-calculator/images/mga-soap-calculator-v1.2.2-20251103-141522.tar.gz
podman tag localhost/mga-soap-calculator:v1.2.2-20251103-141522 localhost/mga-soap-calculator:latest
systemctl --user restart soap-calculator-api.service
```

**Why keep archives?**
- This scenario. Multiple rollback points available.

---

## Directory Structure Updates

### On grimm-lin

**Create structure**:
```bash
sudo mkdir -p /data/podman-apps/mga-soap-calculator/images
sudo chown -R grimm:grimm /data/podman-apps/mga-soap-calculator
chmod 755 /data/podman-apps/mga-soap-calculator
chmod 755 /data/podman-apps/mga-soap-calculator/images
```

**Ansible task to ensure this** (add to role defaults):
```yaml
- name: Ensure /data/podman-apps structure exists
  file:
    path: "/data/podman-apps/mga-soap-calculator/images"
    state: directory
    owner: grimm
    group: grimm
    mode: '0755'
  become: true
```

---

## Implementation Guidance for ansible-architect

### Phase 1: Role Creation

1. **Create role structure**:
   ```bash
   mkdir -p ansible/roles/soap-calculator-image-lifecycle/{tasks,defaults,templates,handlers}
   ```

2. **Implement tasks** in order:
   - `tasks/build.yml` - Start here, test locally
   - `tasks/export.yml` - Verify tar.gz creation
   - `tasks/transfer.yml` - Test file transfer first
   - `tasks/load.yml` - Test Podman load
   - `tasks/deploy.yml` - Test service restart
   - `tasks/validate.yml` - Test health checks
   - `tasks/rollback.yml` - Test rollback manually

3. **Default variables** (`defaults/main.yml`):
   ```yaml
   app_version: "1.0.0"
   image_base_name: "localhost/mga-soap-calculator"
   image_storage_path: "/data/podman-apps/mga-soap-calculator"
   build_artifacts_path: "/tmp/mga-builds"
   grimm_uid: 1000
   health_check_timeout: 60
   health_check_retries: 6
   ```

### Phase 2: Playbook Creation

1. **Create `build-and-deploy-soap-calculator.yml`**
2. **Create `rollback-soap-calculator.yml`**
3. **Test with `--check` mode first**
4. **Test on non-production (if available)**

### Phase 3: Testing Strategy

**Unit Test Each Task**:
```bash
# Test build only
ansible-playbook playbooks/build-and-deploy-soap-calculator.yml \
  --tags build --check

# Test transfer only (requires build first)
ansible-playbook playbooks/build-and-deploy-soap-calculator.yml \
  --tags transfer --check
```

**Integration Test**:
```bash
# Full deployment with verbose output
ansible-playbook playbooks/build-and-deploy-soap-calculator.yml \
  --extra-vars "app_version=1.2.3-test" \
  -vv
```

**Rollback Test**:
```bash
# After successful deployment, test rollback
ansible-playbook playbooks/rollback-soap-calculator.yml -vv
```

### Phase 4: Production Deployment

1. **Increment version** in playbook vars or extra-vars
2. **Run deployment playbook**
3. **Monitor health checks**
4. **Verify new endpoints** (`/api/v1/oils`, `/api/v1/additives`)
5. **Keep terminal open** for 10 minutes post-deployment
6. **Document any issues**

---

## Verification Steps

### Post-Deployment Validation

**Manual checks after playbook completes**:

```bash
# 1. Verify image is loaded
podman images localhost/mga-soap-calculator

# Expected output:
# localhost/mga-soap-calculator  latest    <ID>  <TIME>  <SIZE>
# localhost/mga-soap-calculator  rollback  <ID>  <TIME>  <SIZE>
# localhost/mga-soap-calculator  v1.2.3... <ID>  <TIME>  <SIZE>

# 2. Check service status
systemctl --user status soap-calculator-api.service

# 3. Verify health endpoint
curl http://127.0.0.1:8000/health

# 4. Test new endpoints
curl http://127.0.0.1:8000/api/v1/oils
curl http://127.0.0.1:8000/api/v1/additives

# 5. Check logs for errors
journalctl --user -u soap-calculator-api.service -n 50

# 6. Verify archive exists
ls -lh /data/podman-apps/mga-soap-calculator/images/
readlink /data/podman-apps/mga-soap-calculator/current

# 7. Check rollback capability
podman images localhost/mga-soap-calculator:rollback
# Should exist and be previous version
```

### Automated Validation (in playbook)

Already covered in `validate.yml` task, but summary:
- ✅ Health endpoint responds 200
- ✅ New oils endpoint responds 200
- ✅ New additives endpoint responds 200
- ✅ Service is active and running
- ✅ No error logs in last 10 minutes

---

## Security Considerations

### Image Integrity

**Checksum Verification**:
- SHA256 checksum generated at export
- Transferred with image
- Verified before load
- Prevents corrupted/tampered images

**Ansible Implementation**:
```yaml
- name: Verify archive integrity before load
  command: sha256sum --check CHECKSUMS.sha256
  args:
    chdir: /data/podman-apps/mga-soap-calculator/images
  changed_when: false
```

### Secrets Management

**Current approach** (from existing playbook):
- ✅ Vault-encrypted secrets in `group_vars/production/vault.yml`
- ✅ Environment files with 0600 permissions
- ✅ No secrets in container images

**Maintain this**:
- Never bake secrets into Dockerfile
- Environment files remain in `/home/grimm/.config/mga-soap-calculator/`
- Vault password never committed to repository

### Rootless Podman Security

**Already implemented correctly**:
- ✅ Container runs as UID 1001 (non-root)
- ✅ Podman runs rootless (user grimm)
- ✅ XDG_RUNTIME_DIR properly set
- ✅ User-scoped systemd services

**Maintain this approach** - don't introduce sudo/root where not needed.

---

## Performance Considerations

### Image Size Optimization

**Current Dockerfile is good**:
- Multi-stage build (builder discarded)
- Minimal runtime image (no build tools)
- Wheel-based dependencies (pre-compiled)

**Estimated size**: ~500MB (UBI9 Python base + dependencies)

**Transfer time** (1Gbps network): ~4 seconds
**Load time**: ~10 seconds
**Total deployment time**: ~90 seconds (including health checks)

### Archive Compression

**Current approach**: gzip compression of tar

**Alternatives considered**:
- zstd (faster compression/decompression) - requires zstd installed
- xz (better compression) - much slower
- none (faster transfer on fast network) - larger file

**Recommendation**: Stick with gzip (universal, good balance).

### Cleanup Strategy

**Old archives retention**:
- Keep last 5 versions
- Delete archives older than 30 days
- Manual cleanup on disk space warnings

**Ansible task** (add to role):
```yaml
- name: Clean up old image archives
  shell: |
    cd /data/podman-apps/mga-soap-calculator/images
    ls -t mga-soap-calculator-*.tar.gz | tail -n +6 | xargs -r rm
  args:
    warn: false
  when: deployment_status == "success"
```

---

## Monitoring & Logging

### Deployment Metrics

**Track these** (manual for now, automate later):
- Build duration
- Transfer duration
- Deployment duration
- Health check response time
- Rollback frequency

**Ansible output** already provides timing via `-vv` flag.

### Service Health Monitoring

**Existing setup**:
- ✅ Systemd service status
- ✅ Journald logging
- ✅ Health check endpoint

**Consider adding**:
- Prometheus metrics endpoint
- Structured JSON logging
- Alert on service restart

**Future enhancement** (not for this iteration).

---

## Disaster Recovery

### Backup Strategy

**What to backup**:
1. **Image archives** at `/data/podman-apps/mga-soap-calculator/images/`
2. **PostgreSQL data** volume `mga-pgdata`
3. **Environment files** at `/home/grimm/.config/mga-soap-calculator/`
4. **Ansible vault** file (encrypted, but backup anyway)

**Backup procedure** (separate playbook):
```yaml
- name: Backup MGA Soap Calculator deployment
  hosts: mga_production
  tasks:
    - name: Archive images directory
      archive:
        path: /data/podman-apps/mga-soap-calculator/images
        dest: /data/backups/mga-images-{{ ansible_date_time.date }}.tar.gz

    - name: Export PostgreSQL data
      command: podman exec mga-postgres pg_dump -U postgres mga_soap_calculator
      register: db_dump
      become: true
      become_user: grimm

    - name: Save database dump
      copy:
        content: "{{ db_dump.stdout }}"
        dest: /data/backups/mga-db-{{ ansible_date_time.date }}.sql
```

### Recovery Procedure

**Complete system rebuild**:
1. Restore image archives to `/data/podman-apps/`
2. Run deployment playbook (will load image, configure systemd)
3. Restore PostgreSQL data from dump
4. Validate services

**Estimated recovery time**: ~15 minutes

---

## Cost Analysis

### Storage Requirements

**Per version**:
- Image archive: ~500MB (compressed)
- Podman storage: ~500MB (uncompressed layers)

**Total for 5 versions**:
- Archives: ~2.5GB
- Podman storage: ~1GB (layer deduplication)
- Total: ~3.5GB

**Disk space required on grimm-lin**:
- `/data/podman-apps/`: 5GB (recommended)
- `/home/grimm/.local/share/containers/`: 5GB (Podman storage)

### Network Transfer

**Per deployment**:
- Transfer size: ~500MB (compressed)
- Time on 1Gbps: ~4 seconds
- Time on 100Mbps: ~40 seconds

**Negligible cost** - local network transfer.

### Maintenance Time

**Per deployment**:
- Manual: ~30 minutes (build, transfer, deploy, validate)
- Automated: ~5 minutes (run playbook, verify)

**Time savings**: ~25 minutes per deployment
**Deployments per month**: Assume 4 (weekly)
**Monthly time savings**: ~100 minutes (~1.7 hours)

**Ansible development time**: ~8 hours
**Break-even point**: ~5 months

---

## Open Questions & Decisions Needed

### 1. Build Location

**Options**:
- A. Build on development Mac, transfer to grimm-lin
- B. Build directly on grimm-lin (requires git clone on server)
- C. Build on separate CI/CD server

**Recommendation**: Option A (build locally)
**Reason**: You're already developing locally, simplest workflow, no CI/CD infrastructure needed yet.

### 2. Version Management

**Who increments version?**
- Manual in playbook vars
- Git tag-based (read from git describe)
- Separate version file in repo

**Recommendation**: Manual in playbook extra-vars
**Reason**: Explicit control, clear intent, no automation complexity yet.

### 3. Registry Strategy

**Future consideration**: Push to private registry instead of tar transfer?

**Pros**:
- Standard workflow
- Better for multiple servers
- Version management built-in

**Cons**:
- Requires registry infrastructure
- Additional complexity
- Not needed for single-server deployment

**Recommendation**: Stick with tar transfer for now, revisit if you add more servers.

### 4. Deployment Windows

**Should deployments be time-restricted?**
- Unrestricted (deploy anytime)
- Business hours only
- Scheduled maintenance windows

**Current assumption**: Unrestricted (development environment)
**Question**: Is this actually production or staging?

---

## Summary & Next Steps

### What This Design Provides

✅ **Complete image lifecycle** (build → transfer → deploy → rollback)
✅ **Version management** with semantic versioning + timestamps
✅ **Storage in `/data/podman-apps/`** as required
✅ **Automatic rollback** on health check failure
✅ **Manual rollback capability** for post-deployment issues
✅ **Ansible automation** (no manual SSH commands)
✅ **Idempotent operations** (safe to re-run)
✅ **Checksum verification** (integrity validation)
✅ **Proper secrets handling** (vault-encrypted)

### Implementation Checklist

**For ansible-architect agent**:

- [ ] Create `soap-calculator-image-lifecycle` role structure
- [ ] Implement `tasks/build.yml`
- [ ] Implement `tasks/export.yml`
- [ ] Implement `tasks/transfer.yml`
- [ ] Implement `tasks/load.yml`
- [ ] Implement `tasks/deploy.yml`
- [ ] Implement `tasks/validate.yml`
- [ ] Implement `tasks/rollback.yml`
- [ ] Create `defaults/main.yml` with variables
- [ ] Create `handlers/main.yml` for service restarts
- [ ] Create `playbooks/build-and-deploy-soap-calculator.yml`
- [ ] Create `playbooks/rollback-soap-calculator.yml`
- [ ] Test each task individually
- [ ] Test full deployment workflow
- [ ] Test rollback procedure
- [ ] Document usage in role README

### Verification Checklist

**After implementation**:

- [ ] Build creates versioned image locally
- [ ] Export creates compressed tar.gz with checksum
- [ ] Transfer succeeds to `/data/podman-apps/`
- [ ] Checksum verification passes
- [ ] Image loads into Podman successfully
- [ ] Tags are applied correctly (latest, rollback, version)
- [ ] Systemd service restarts with new image
- [ ] Health check validation passes
- [ ] New endpoints (`/api/v1/oils`, `/api/v1/additives`) respond
- [ ] Rollback procedure works on failure
- [ ] Manual rollback playbook works
- [ ] Cleanup removes local build artifacts

### Risk Assessment

**Low Risk**:
- ✅ Existing Ansible automation works
- ✅ Dockerfile builds successfully
- ✅ Systemd units are functional
- ✅ Health checks exist

**Medium Risk**:
- ⚠️ `/data/podman-apps/` path assumption (verify disk space)
- ⚠️ Network transfer reliability (local network should be fine)
- ⚠️ Rollback tag preservation (test thoroughly)

**High Risk**:
- 🚨 First deployment (no existing rollback image)
  - **Mitigation**: Keep manual recovery procedure handy
- 🚨 Health check false positives (might rollback working deployment)
  - **Mitigation**: Increase timeout, test validation logic

---

## Conclusion

You've got a solid foundation with the existing Ansible automation and Quadlet setup. This design adds the missing piece: **complete image lifecycle management** with proper versioning, rollback capability, and storage in your required `/data/podman-apps/` location.

The architecture is deliberately simple:
- No registry complexity
- No CI/CD pipeline (yet)
- No orchestration overhead
- Just: build → tar → transfer → load → deploy → validate → rollback (if needed)

For a single-server deployment, this is exactly the right amount of automation. You can always add complexity later (registry, CI/CD, multi-server orchestration) when you actually need it.

**The ansible-architect agent should have everything needed to implement this**. If any questions arise during implementation, they'll be about specific Ansible module syntax or Podman command details - the architecture itself is sound.

Now go build this thing properly. And for the love of all that's holy, test the rollback procedure *before* you need it in production.

---

**End of Design Document**
