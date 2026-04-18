# Tech Stack

Current, in-production stack for MGA Soap Calculator as of 2026.4.18. Running version 2026.4.18 on OpenShift SNO.

## Language & runtime

Python 3.11+ (enforced in `pyproject.toml`, target-version = `py311`).

## Web framework

FastAPI with uvicorn (4 workers in production). REST, versioned under `/api/v1/`. Pydantic v2 for request/response validation (`model_validate`, `ConfigDict`). CORS middleware configured.

## Database & ORM

PostgreSQL 15. UBI 9 image in production, `postgres:15-alpine` in local dev. SQLAlchemy 2.0 async with asyncpg driver. psycopg2-binary present for Alembic sync operations only.

## Migrations

Alembic. Applied automatically at container startup by `scripts/docker-entrypoint.sh` — not run manually against production. Seed data idempotent; re-running is safe.

## Auth

Argon2id password hashing (OWASP-recommended). JWT bearer tokens, 24-hour expiry. Calculation ownership enforced server-side via `validate_calculation_ownership`.

## Testing

pytest + pytest-asyncio (`asyncio_mode = auto`) + pytest-cov. Markers enforced (`--strict-markers`): `unit`, `integration`, `e2e`, `slow`. Current suite: 454 passing, 79% coverage.

## Lint / format / types

ruff (line-length 100, target py311) for lint and format. mypy in strict mode (`disallow_untyped_defs = true`). All function signatures typed.

## Package manager

`uv` preferred; `pip` supported. No Poetry, no pipenv.

## Container runtime

Podman (rootless on Fedora for the legacy `grimm-lin` target; CRI-O on OCP in current production). Local dev via `docker-compose` — works with `podman-compose`.

## Deployment platform

OpenShift SNO at `https://mga-soap-calculator.apps.sno.greysson.com`. Resources: Namespace, Secret, Postgres StatefulSet, API Deployment, Service, edge-TLS Route. Image built on-cluster via BuildConfig from the GitHub source.

## Infrastructure as code

Ansible. Role `mga_soap_calculator_ocp` in the `greysson-homelab` repo, using `kubernetes.core.k8s`. Secrets in Ansible Vault (vault password at `~/.config/pai/secrets/ansible_vault_pw`). Previous `grimm-lin` Podman-Quadlet deployment remains in `ansible/` in-repo for reference and emergency fallback.

## CI/CD

GitHub Actions. Workflow stages: Lint → Test Suite → Security Scan → Build & Scan Container (Trivy). Deploy triggered via Ansible playbook against the OCP cluster.

## Source hosting

GitHub: `GreyssonEnterprises/mga-soap-calculator`, `main` branch. IaC lives in a separate `greysson-homelab` repo.

## Versioning scheme

CalVer, as of 2026.4.18.
- User-facing: `YYYY.M.D[-N]` (e.g. `2026.4.18`, `2026.4.18-1` for same-day re-releases)
- PEP 440 canonical form (packaging): `YYYY.M.D[.N]` (e.g. `2026.4.18`, `2026.4.18.1`)

## Frontend

**None yet.** The product is API-first; Swagger docs and curl are the only "UI" in production. Building a frontend is Phase A in `roadmap.md`.

Candidate stack when we build one (per global CLAUDE.md preferences): **TypeScript + Bun** as runtime and package manager. Framework TBD in Phase A planning (likely SvelteKit or Next.js; decide during the frontend spec). Integrate with existing OCP BuildConfig pipeline.

## Observability

**None beyond OCP defaults** (pod metrics, container logs via the cluster). No Sentry, no Prometheus scraping of app metrics, no structured log aggregation. Adding this is a Phase C roadmap item.

---

## Why these choices

Python + FastAPI because the calculation engine is the product and Python's ecosystem (Decimal arithmetic, Pydantic validation, SQLAlchemy async) suits the math-and-persistence profile cleanly. PostgreSQL because recipes are relational data with integrity requirements, and the Greysson homelab already runs it well. `uv` and ruff because they are the current best-in-class Python tools and match the global `~/.claude/CLAUDE.md` preference for modern, fast tooling. Ansible-first for infrastructure because that is the house rule across every Greysson project — manual `oc apply` is not a deployment strategy. OpenShift SNO because the homelab already hosts it, it gives us edge-TLS routes for free, and it keeps the tool owner-operated instead of vendor-operated. When a frontend lands, TypeScript + Bun because that's the global preference for TS work — no npm/yarn, no Create React App, no hand-rolled webpack configs.
