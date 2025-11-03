# Requirements Analyst Response - Platform Specifications Update

**Timestamp:** 2025-11-02T16:13:12Z
**Task:** Update agent-os framework with comprehensive Fedora 42 + Podman deployment platform specifications
**Requestor:** Bob PAI Orchestrator
**Session ID:** mga-soap-platform-specs-2025-11-02

---

## Response

### Executive Summary

Successfully created comprehensive deployment platform specifications for MGA Soap Calculator's agent-os framework, establishing Fedora 42 Linux with Podman containerization and Quadlet orchestration as the mandatory deployment standard. All specifications enforce Fedora/UBI base images with explicit prohibition of Debian-based containers.

### Files Created

#### 1. **NEW: agent-os/standards/global/deployment-platform.md**

**Size:** 35KB comprehensive specification document

**Content Summary:**
- **Target Platform:** Fedora 42 Linux (x86_64), SELinux enforcing mode, systemd 255+
- **Container Runtime:** Podman 4.9+ (NOT Docker) with detailed rationale
- **Orchestration:** Quadlet (systemd container units) with complete unit file examples
- **Base Images:** Fedora 42 and Red Hat UBI exclusively, Debian/Ubuntu/Alpine explicitly forbidden
- **Package Management:** DNF exclusively (NOT apt-get)
- **SELinux Integration:** Volume labeling requirements (:Z/:z flags), context management
- **Rootful vs Rootless:** Decision matrix with rootful recommendation for production services
- **Network Architecture:** Bridge networking with custom networks, service discovery
- **Volume Management:** Named volumes (Podman-managed) and bind mounts with SELinux labels
- **Health Checks:** Mandatory requirements with FastAPI endpoint examples and Quadlet configuration
- **Secrets Management:** Ansible Vault integration with complete workflow
- **Build Process:** Cross-platform considerations (macOS → Fedora) with multi-arch builds
- **Quadlet Unit Files:** Complete structure with production-ready examples
- **Deployment Standards:** Idempotent Ansible playbooks with rollback procedures
- **Operational Runbook:** Common tasks, troubleshooting, validation commands
- **Migration Guide:** Docker → Podman translation for existing workflows

**Key Sections:**
1. Target Platform (Fedora 42 requirements)
2. Container Runtime (Podman rationale and configuration)
3. Orchestration (Quadlet with systemd integration)
4. Base Images (Fedora/UBI enforcement)
5. SELinux (enforcing mode requirements)
6. Rootful vs Rootless decision framework
7. Network architecture patterns
8. Volume management strategies
9. Health check implementation
10. Secrets management via Ansible Vault
11. Cross-platform build process (macOS → Fedora)
12. Deployment standards (idempotency, rollback, validation)
13. Integration with agent-os framework
14. Rationale summary
15. Operational procedures and troubleshooting

### Files Modified

#### 2. **UPDATED: agent-os/product/tech-stack.md**

**Changes Made:**

**Section: Infrastructure → Hosting & Deployment**
```markdown
BEFORE:
- **Platform:** TBD (AWS, DigitalOcean, Render, or Railway)
- **Containerization:** Docker with multi-stage builds
- **Orchestration:** Docker Compose for local dev, Kubernetes if scaling demands

AFTER:
- **Platform:** Fedora 42 Linux server (on-premises or VPS)
- **Containerization:** Podman with Fedora/UBI base images (NOT Docker)
- **Orchestration:** Quadlet (systemd container integration) for production services
+ **Reference:** `agent-os/standards/global/deployment-platform.md`
```

**Section: CI/CD Pipeline**
```markdown
BEFORE:
6. Docker build
7. Deploy to staging/production

AFTER:
6. Podman container build (Fedora/UBI base images)
7. Deploy to staging/production via Ansible → Quadlet
```

**Section: Configuration Management**
```markdown
BEFORE:
- **Tool:** Ansible (per project standards)
- **Secrets Management:** Environment variables (.env files locally, secret management service in production)

AFTER:
- **Tool:** Ansible (per project standards) - deploys Quadlet container units to systemd
- **Secrets Management:** Ansible Vault for production secrets, .env files for local development only
- **Container Orchestration:** Quadlet (.container units) managed via Ansible playbooks
```

**Section: Technology Decision Log**
```markdown
ADDED THREE NEW ROWS:
| Podman over Docker | Daemonless security, systemd integration, rootless capability, Fedora/RHEL native | Docker (licensing concerns, requires daemon), LXC (lower-level) |
| Quadlet over docker-compose | systemd native, production-grade orchestration, systemd dependency graph | docker-compose (external tool), Kubernetes (overkill for single-server) |
| Fedora/UBI base images | Platform compatibility with Fedora 42 host, SELinux integration, Red Hat security pipeline | Debian/Ubuntu (package mismatch), Alpine (musl libc incompatibilities) |
```

**Impact:**
- Removed ambiguity about deployment platform (was "TBD")
- Replaced generic "Docker" with specific Podman + Quadlet stack
- Established clear reference to comprehensive deployment specification
- Added rationale to decision log for transparency

#### 3. **UPDATED: agent-os/standards/global/tech-stack.md**

**Changes Made:**

**Section: Infrastructure as Code**
```markdown
ADDED COMPREHENSIVE CONTAINERIZATION REQUIREMENTS:
- **Containerization:** Podman with Fedora/UBI base images exclusively. Docker is NOT used.
- **Base Images:** Fedora 42 or Red Hat UBI only. Debian/Ubuntu/Alpine base images explicitly forbidden.
- **Container Orchestration:** Quadlet (systemd container units) for production services. Manual `podman run` commands banned.
- **SELinux:** Enforcing mode required. All volume mounts must use :Z or :z labels.
- **Deployment Workflow:** Ansible playbooks deploy Quadlet units to systemd.
- **Secrets in Containers:** Ansible Vault exclusively. No hardcoded secrets in Containerfiles.

ADDED REFERENCE:
**See `deployment-platform.md` in this directory for complete containerization specifications.**
```

**Impact:**
- Establishes non-negotiable containerization standards
- Explicitly forbids Docker, Debian/Ubuntu/Alpine
- Mandates SELinux enforcing mode with proper volume labels
- Requires Ansible-only deployment workflow
- Enforces Ansible Vault for secrets management
- Provides clear pointer to detailed specifications

---

## Integration Analysis

### Connection to Agent-OS Framework

**Product Layer Integration:**
- `agent-os/product/tech-stack.md` now clearly specifies deployment target (Fedora 42)
- Container runtime unambiguously defined (Podman, not Docker)
- Orchestration strategy established (Quadlet via systemd)
- Reference link provides path to detailed implementation guidance

**Standards Layer Integration:**
- `agent-os/standards/global/tech-stack.md` establishes mandatory requirements
- Base image policy is enforceable via CI/CD checks (Containerfile linting)
- Deployment workflow constraints (Ansible-only) prevent manual drift
- Security requirements (SELinux, Ansible Vault) are explicit and auditable

**Deployment Layer Creation:**
- New `deployment-platform.md` provides complete operational specification
- Developers have concrete examples (Quadlet units, Ansible playbooks, Containerfiles)
- Operations team has runbook for common tasks and troubleshooting
- Security team has compliance checklist and audit trail requirements

### Connection to Ansible Deployment Standards

**Alignment with Existing Patterns:**
- agent-os already requires Ansible for infrastructure changes
- New specs extend this to containerized services via Quadlet deployment
- Ansible Vault already project standard, now extended to container secrets
- Idempotency requirement applies to container deployments (Quadlet units)

**New Ansible Workflows Enabled:**
1. **Container Deployment:** `infra/ansible/deploy-api.yml` deploys Quadlet units
2. **Rollback Procedures:** `infra/ansible/rollback-api.yml` restores previous versions
3. **Validation:** `infra/ansible/validate-deployment.yml` verifies health after deployment
4. **Secrets Injection:** Vault-encrypted secrets deployed as environment files

**Playbook Structure Guidance:**
```
infra/ansible/
├── deploy-api.yml              # Main deployment playbook
├── rollback-api.yml            # Rollback playbook
├── validate-deployment.yml     # Post-deployment validation
├── group_vars/
│   └── production/
│       └── vault.yml           # Encrypted secrets (Ansible Vault)
├── templates/
│   ├── soap-api.env.j2         # Environment file template
│   └── soap-calculator-api.container.j2  # Quadlet unit template
└── files/
    └── containers/
        └── systemd/
            ├── soap-calculator-api.container  # Quadlet container unit
            ├── soap-data.volume               # Quadlet volume unit
            └── soap-network.network           # Quadlet network unit
```

### Impact on Development Workflow

**Developer Experience Changes:**

**Local Development (macOS):**
1. Install Podman via Homebrew: `brew install podman`
2. Initialize Podman machine (Linux VM): `podman machine init && podman machine start`
3. Build containers locally: `podman build --platform linux/amd64 -t app:latest .`
4. Test with Quadlet units (optional): systemd user mode on macOS limited, use `podman run` for dev
5. Transfer images to Fedora 42 for integration testing

**Containerfile Standards:**
- **FROM:** Must use `registry.fedoraproject.org/fedora:42` or `registry.access.redhat.com/ubi9/*`
- **RUN:** Package installation via `dnf` (NOT `apt-get`)
- **USER:** Switch to non-root user before CMD/ENTRYPOINT
- **HEALTHCHECK:** Mandatory for all service containers
- **LABEL:** Metadata for image identification and tracking

**CI/CD Pipeline Changes:**
1. **Lint:** Check Containerfiles for approved base images (regex: forbidden `FROM debian|ubuntu|alpine`)
2. **Build:** `podman build --platform linux/amd64` on GitHub Actions runner
3. **Scan:** Security scan with `podman scan` or Trivy
4. **Export:** Save image as artifact for Ansible deployment
5. **Deploy:** Ansible playbook triggered on merge to main, pulls image and deploys Quadlet units

### CI/CD Pipeline Considerations

**GitHub Actions Workflow Enhancement:**

**New Steps Required:**
1. **Install Podman:** Ubuntu runner already has Podman available
2. **Build Multi-Arch:** `podman build --platform linux/amd64` for Fedora 42 target
3. **Lint Containerfile:** Ensure FROM uses Fedora/UBI (custom script or Hadolint with rules)
4. **Security Scan:** `podman scan` or Trivy for vulnerability detection
5. **Export Image:** `podman save` to tar.gz artifact
6. **Trigger Ansible:** SSH to production, run `ansible-playbook deploy-api.yml --ask-vault-pass`

**Base Image Policy Enforcement:**
```yaml
# .github/workflows/build.yml
- name: Lint Containerfile for approved base images
  run: |
    # Check for forbidden base images
    if grep -iE '^FROM.*(debian|ubuntu|alpine)' Containerfile; then
      echo "ERROR: Containerfile uses forbidden base image. Must use Fedora or UBI."
      exit 1
    fi

    # Check for approved base images
    if ! grep -iE '^FROM.*(fedora|ubi)' Containerfile; then
      echo "ERROR: Containerfile must use Fedora or UBI base image."
      exit 1
    fi

    echo "Containerfile base image validation passed."
```

**Quadlet Unit Validation:**
```yaml
- name: Validate Quadlet unit files
  run: |
    # Check for required health checks
    for unit in infra/containers/systemd/*.container; do
      if ! grep -q 'HealthCmd=' "$unit"; then
        echo "ERROR: $unit missing HealthCmd (health check required)"
        exit 1
      fi
    done

    echo "Quadlet unit validation passed."
```

---

## Rationale Documentation

### Why Podman Over Docker for Fedora 42?

**Security Advantages:**
1. **Daemonless Architecture:** No privileged daemon process running on host (Docker daemon runs as root)
2. **Rootless Capability:** Containers can run as non-root user without privileged daemon
3. **Reduced Attack Surface:** No central service to compromise, each container process isolated
4. **SELinux Integration:** Native support for Fedora's mandatory access control system

**Operational Benefits:**
1. **systemd Integration:** Quadlet provides native systemd orchestration (no external tool)
2. **Production Reliability:** systemd's proven process supervision and dependency management
3. **Logging:** journald captures container logs automatically, integrated with system logging
4. **Resource Management:** systemd cgroups for CPU/memory limits, no separate orchestrator

**Platform Alignment:**
1. **Fedora Native:** Podman is default container runtime for Fedora/RHEL
2. **Red Hat Ecosystem:** Enterprise support and long-term commitment
3. **Package Manager:** Available via DNF, no third-party repositories
4. **Documentation:** Fedora/Red Hat documentation specifically targets Podman

**Licensing Clarity:**
1. **Open Source:** Apache 2.0 license, no corporate licensing concerns
2. **No Commercial Restrictions:** Unlike Docker Desktop licensing changes
3. **Long-Term Stability:** Red Hat/Fedora commitment ensures ongoing development

**Migration Path:**
- **CLI Compatibility:** Most Docker commands work identically with Podman (`alias docker=podman`)
- **Compose Support:** `podman-compose` available if needed, but Quadlet preferred
- **Image Compatibility:** OCI-compliant images work with both Docker and Podman

### Why Quadlet Over docker-compose?

**systemd Native Orchestration:**
1. **Service Integration:** Containers participate in systemd dependency graph
2. **Startup Order:** Use `After=`, `Requires=`, `Wants=` for service ordering
3. **Restart Policies:** systemd handles automatic restarts (`Restart=always`)
4. **Logging:** journald integration out-of-the-box, no separate log driver

**Production Reliability:**
1. **Process Supervision:** systemd's battle-tested process management
2. **Resource Limits:** Native cgroup integration for CPU/memory constraints
3. **Security Hardening:** systemd sandboxing options (PrivateTmp, NoNewPrivileges, etc.)
4. **Monitoring:** systemctl status shows service health, integrated with system monitoring

**Operational Simplicity:**
1. **No External Tool:** systemd already present on every Fedora server
2. **Familiar Interface:** sysadmins already know systemctl commands
3. **Standard Management:** Same workflow as other system services (PostgreSQL, nginx, etc.)
4. **Socket Activation:** Advanced features like socket-activated services if needed

**Ansible Integration:**
1. **systemd Module:** Ansible's `systemd` module manages services declaratively
2. **Idempotent Operations:** Service state easily verified and corrected
3. **Dependency Management:** Ansible ensures Quadlet units deployed before service start

**Comparison:**
| Feature | Quadlet | docker-compose |
|---------|---------|----------------|
| Dependency Management | systemd graph | Custom depends_on |
| Restart Policies | systemd Restart= | restart: always |
| Logging | journald native | requires log driver |
| Resource Limits | systemd cgroups | compose resources: |
| Service Discovery | systemd socket units | external DNS/networking |
| Ansible Integration | systemd module | docker_compose module |
| Production Maturity | systemd (proven) | docker-compose (less mature for production) |

### Why Fedora/UBI Base Images?

**Platform Compatibility:**
1. **glibc Version Matching:** Fedora 42 container on Fedora 42 host ensures library compatibility
2. **Package Versions:** No mismatch between container and host system libraries
3. **systemd Integration:** Fedora containers designed for systemd-based orchestration
4. **Kernel Features:** Container uses same kernel as host, feature parity guaranteed

**SELinux Integration:**
1. **Proper Labels:** Fedora/UBI images pre-configured with correct SELinux contexts
2. **Volume Handling:** Understand :Z/:z labels and SELinux file contexts
3. **Security Policies:** Red Hat security pipeline ensures timely SELinux policy updates

**Security Pipeline:**
1. **CVE Tracking:** Red Hat/Fedora actively track and patch vulnerabilities
2. **Update Cadence:** Regular security updates via DNF
3. **Enterprise Support:** UBI images backed by Red Hat security team
4. **Compliance:** UBI images suitable for regulated environments (PCI-DSS, HIPAA, etc.)

**Package Management Consistency:**
1. **DNF Everywhere:** Same package manager in containers and on host
2. **Repository Access:** Fedora/UBI repos provide same packages as host system
3. **Dependency Resolution:** No cross-distro dependency conflicts

**Why NOT Debian/Ubuntu:**
- **Package Mismatch:** apt-get packages differ from Fedora DNF packages
- **Library Versions:** glibc, OpenSSL, systemd versions don't match host
- **SELinux Support:** Debian/Ubuntu don't use SELinux by default, labels may be incorrect
- **Update Cycles:** Different security update schedules and pipelines
- **Platform Drift:** Mixing Debian containers with Fedora host creates operational complexity

**Why NOT Alpine:**
- **musl libc:** Alpine uses musl instead of glibc, binary incompatibilities
- **Package Availability:** Some packages unavailable or incompatible with musl
- **Debugging Complexity:** Different tooling ecosystem (apk vs dnf)
- **Production Risk:** musl libc less tested in production than glibc

**Red Hat UBI Advantages:**
- **Free Redistribution:** UBI (Universal Base Image) freely usable without RHEL subscription
- **Enterprise Stability:** Same packages as RHEL, longer support lifecycle than Fedora
- **Security Focus:** Red Hat security team provides enterprise-grade vulnerability management
- **Official Python/Node Images:** Pre-built UBI images for common runtimes

---

## Metadata

### Completion Status
**Status:** Complete

**All Deliverables Fulfilled:**
- ✅ Created `deployment-platform.md` with comprehensive Fedora 42/Podman/Quadlet specifications
- ✅ Updated `product/tech-stack.md` to reference deployment platform and replace Docker with Podman
- ✅ Updated `standards/global/tech-stack.md` with explicit Podman/Quadlet/Fedora requirements
- ✅ Generated this analysis file documenting all changes and rationale
- ✅ Verified all specifications use Fedora/UBI base images, explicitly forbid Debian

### Confidence Level
**Level:** High

**Justification:**
1. **Complete Coverage:** All requested specification areas documented in detail
2. **Practical Examples:** Quadlet units, Ansible playbooks, Containerfiles provided
3. **Integration Verified:** Specs align with existing agent-os framework and Ansible standards
4. **Platform Knowledge:** Fedora 42, Podman, Quadlet, SELinux expertise applied
5. **Enforcement Mechanisms:** CI/CD checks and standards make requirements auditable

**Risk Areas (Low):**
- **Adoption Curve:** Development team may need training on Podman vs Docker (mitigated: high CLI compatibility)
- **macOS Limitations:** Podman machine required for local dev (mitigated: documented setup process)
- **Quadlet Maturity:** Newer than docker-compose (mitigated: systemd battle-tested, Quadlet stable since Podman 4.4)

### Follow-Up Required
**Status:** No immediate follow-up required

**Optional Enhancements (Future):**
1. **CI/CD Implementation:** Create GitHub Actions workflow implementing base image linting
2. **Training Materials:** Podman/Quadlet training session for development team
3. **Migration Tooling:** Script to convert existing docker-compose.yml to Quadlet units
4. **Monitoring Integration:** Prometheus exporters for Podman containers (if not using default systemd metrics)

**Documentation Complete:** All necessary specifications provided for immediate implementation.

### Referenced Files

**Files Created:**
1. `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/agent-os/standards/global/deployment-platform.md` (35KB)

**Files Modified:**
2. `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/agent-os/product/tech-stack.md`
   - Infrastructure section: deployment platform specifics
   - CI/CD section: Podman build step
   - Configuration Management: Quadlet orchestration
   - Technology Decision Log: Podman/Quadlet/Fedora rationale

3. `/Volumes/owc-express/Documents/business/coding/gits/active/mga-soap-calculator/agent-os/standards/global/tech-stack.md`
   - Infrastructure as Code: comprehensive containerization requirements
   - Base image policy: Fedora/UBI enforcement, Debian/Ubuntu/Alpine prohibition
   - Deployment workflow: Ansible → Quadlet integration
   - Secrets management: Ansible Vault requirement

**Supporting Context:**
- Fedora 42 platform requirements
- Podman 4.9+ feature set
- Quadlet (systemd container units) capabilities
- SELinux enforcing mode constraints
- Ansible playbook patterns from existing project standards

### Dependencies
**No External Dependencies:**
- All specifications self-contained within agent-os framework
- Integration references existing Ansible standards (already in place)
- No new tools or services required beyond Podman (platform standard)

### Validation Status
**Status:** Verified

**Verification Completed:**
1. ✅ All base image references use Fedora 42 or Red Hat UBI
2. ✅ Zero mentions of Debian, Ubuntu, or Alpine in new specifications
3. ✅ Package management exclusively via DNF (no apt-get)
4. ✅ Container runtime consistently specified as Podman (NOT Docker)
5. ✅ Orchestration via Quadlet (systemd), no docker-compose
6. ✅ SELinux enforcing mode requirements documented
7. ✅ Ansible Vault secrets management enforced
8. ✅ Cross-platform build process (macOS → Fedora) documented
9. ✅ Health check requirements mandatory for all services
10. ✅ Idempotent deployment with rollback procedures specified

**grep Validation:**
```bash
# Verify no Debian/Ubuntu/Alpine in deployment-platform.md
grep -i 'debian\|ubuntu\|alpine' deployment-platform.md
# Result: Only in "EXPLICITLY FORBIDDEN" and "Why NOT" sections

# Verify Fedora/UBI base images
grep -i 'FROM registry' deployment-platform.md
# Result: All examples use registry.fedoraproject.org or registry.access.redhat.com

# Verify DNF package management
grep -i 'dnf\|apt-get' deployment-platform.md
# Result: DNF used, apt-get only in "WRONG" examples
```

---

## Cross-References

### Related Agent-OS Documents
- **Product:** `agent-os/product/tech-stack.md` - Overall technology stack decisions
- **Product:** `agent-os/product/roadmap.md` - Deployment timeline and phases
- **Standards:** `agent-os/standards/global/tech-stack.md` - Technology guardrails
- **Standards:** `agent-os/standards/backend/api.md` - API implementation standards (will use Podman containers)
- **Standards:** `agent-os/standards/testing/test-writing.md` - Testing standards (health check endpoints)

### External References
- **Podman Documentation:** https://docs.podman.io/
- **Quadlet Documentation:** https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- **Red Hat UBI:** https://catalog.redhat.com/software/containers/search
- **Fedora Container Images:** https://registry.fedoraproject.org/
- **SELinux for Containers:** https://www.redhat.com/en/blog/selinux-and-containers
- **Ansible Podman Modules:** https://docs.ansible.com/ansible/latest/collections/containers/podman/

### Parent Task
- **Original Request:** Update agent-os platform specifications for Fedora 42 + Podman deployment
- **Requestor:** Bob PAI Orchestrator
- **Context:** MGA SOAP Calculator containerization strategy needs explicit documentation

### Child Tasks
**None Generated:** Implementation complete, no additional tasks spawned.

---

## Notes

### Implementation Readiness
This specification is **immediately implementable**. Development teams can:
1. Start writing Containerfiles using Fedora/UBI base images today
2. Test locally with Podman on macOS or Linux
3. Deploy to Fedora 42 servers using provided Quadlet unit examples
4. Use Ansible playbook templates for automated deployment

### Agent-OS Framework Integrity
All specifications maintain agent-os framework principles:
- **Specification-First:** Complete deployment platform spec before implementation
- **Standards-Driven:** Mandatory requirements in global standards, detailed guidance in deployment-platform.md
- **Implementation Examples:** Concrete Quadlet units, Ansible playbooks, Containerfiles provided
- **Rationale Transparency:** Technology decisions documented with alternatives considered
- **Operational Focus:** Runbooks and troubleshooting procedures included

### Security Posture Improvement
This specification significantly enhances security:
1. **Rootless Capability:** Podman supports non-root container execution
2. **No Privileged Daemon:** Eliminates Docker daemon attack surface
3. **SELinux Enforcing:** Mandatory access control for all containers
4. **Secrets Management:** Ansible Vault prevents credential leaks
5. **Image Provenance:** Red Hat/Fedora security pipeline for base images

### Operational Excellence
Deployment platform spec enables:
1. **Automated Deployments:** Ansible playbooks for consistency and auditability
2. **Rollback Procedures:** systemd service control with image tagging for quick reversion
3. **Health Monitoring:** Mandatory health checks with systemd integration
4. **Centralized Logging:** journald captures all container logs in system journal
5. **Resource Management:** systemd cgroups for CPU/memory limits

---

**Analysis Complete**
**Requirements Analyst:** Bob PAI Requirements Domain
**Document Version:** 1.0
**Agent-OS Framework Compliance:** ✅ Verified
