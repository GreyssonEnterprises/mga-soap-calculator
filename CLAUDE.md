# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- **Python 3.11+** (enforced in `pyproject.toml`), package managed with `uv` or `pip`
- **FastAPI** + **uvicorn** (async web framework)
- **SQLAlchemy 2.0 async** + **asyncpg** (driver) + **psycopg2-binary** (sync for Alembic)
- **Alembic** for migrations
- **PostgreSQL 15** (UBI 9 image in prod, `postgres:15-alpine` in dev)
- **pytest** + `pytest-asyncio` (asyncio_mode=auto) + `pytest-cov`
- **OpenShift SNO** for production (deployment managed from the `greysson-homelab` IaC repo)

## Common Commands

### Local Development

```bash
# Dev stack via docker-compose (works with podman-compose)
docker-compose up -d                             # starts postgres + api
docker-compose down -v                           # teardown + wipe volume

# Run API outside container (requires local Postgres running)
uvicorn app.main:app --reload                    # http://localhost:8000/docs
```

### Tests

```bash
pytest                                            # full suite + coverage
pytest tests/unit                                 # unit only
pytest tests/integration tests/e2e                # API/integration
pytest tests/unit/test_lye_calculator.py          # single file
pytest -k "test_purity_calculation"               # single test by name
pytest -m unit                                    # by marker: unit|integration|e2e|slow
pytest --cov=app --cov-report=html                # coverage report to htmlcov/
```

Note: `pytest.ini` sets `--strict-markers`. Adding a new marker requires adding it to the `markers` section.

### Migrations

```bash
alembic upgrade head                              # apply all
alembic downgrade -1                              # rollback one
alembic revision --autogenerate -m "description"  # new migration
```

Migrations are applied automatically at container startup by `scripts/docker-entrypoint.sh` — do not run them manually against prod.

### Deployment

Deployment is managed via the `greysson-homelab` IaC repo at
`ansible/roles/mga_soap_calculator_ocp/`. See
`greysson-homelab/ansible/playbooks/deploy-mga-soap-calculator.yml`.
Production target is OpenShift SNO.

## Architecture

### Request Flow

```
HTTP → app/main.py (FastAPI app, custom OpenAPI, CORS, catch-all for missing /v1/)
     → app/api/v1/*.py (routers: auth, calculate, resources, additives,
                         essential_oils, colorants, inci)
     → app/schemas/*.py (Pydantic request/response validation)
     → app/services/*.py (pure calculation logic — no DB)
     → app/models/*.py (SQLAlchemy async ORM)
     → app/db/base.py (async session via get_db dependency)
```

All endpoints are mounted under `/api/v1/`. `main.py` registers a catch-all at the end that returns a helpful 404 with `correct_path` if the `/v1/` prefix is missing — **any new router must be `include_router`'d before this catch-all**.

### Service Layer (the interesting part)

`app/services/` contains pure, stateless calculation code. These are called from the `calculate.py` router but hold no DB session and no framework coupling:

- `lye_calculator.py` — NaOH/KOH saponification math, mixed-lye support, purity-adjusted variants (`calculate_lye_with_purity`)
- `water_calculator.py` — three calculation methods: `percent_of_oils`, `lye_concentration`, `water:lye ratio`
- `quality_metrics_calculator.py` — base metrics from oils + **additive effect modeling** (the competitive differentiator: applies research-backed modifiers scaled by usage rate)
- `fatty_acid_calculator.py` — fatty acid profile, sat:unsat ratio
- `percentage_calculator.py` — uses `Decimal` with `ROUND_HALF_UP`; normalization and rounding-to-sum helpers
- `validation.py` — percentage sum checks, superfat warnings, unknown-additive warnings, rounding helpers
- `inci_naming.py` + `label_generator.py` + `three_format_inci_generator.py` — INCI label generation (raw, saponified, common-name formats); reads `app/data/saponified-inci-terms.json`

When adding calculation features: put the math in `app/services/`, import into the router, and unit-test the service directly (see `tests/unit/test_*_calculator.py`). Don't put DB queries or Pydantic models in services.

### Domain Model

- **Oil** — SAP values (NaOH/KOH), fatty acid composition, quality contributions, INCI names (both raw and saponified)
- **Additive** — category (exfoliant/hardener/lather_booster/skin_benefit/clay), confidence level, usage rate recommendations, quality effect modifiers
- **EssentialOil** / **Colorant** — reference data with usage rate guidance
- **Calculation** — persisted recipe + results, owned by User (JWT-enforced via `validate_calculation_ownership`)
- **User** — Argon2id password hashing (OWASP-recommended), JWT with 24h expiry

### Container Startup

`scripts/docker-entrypoint.sh` runs on every container start:

1. `pg_isready` poll (30 retries, 60s budget)
2. `alembic upgrade head` (idempotent)
3. Seed check: counts rows in `oils` and `additives`; if **either** is zero, runs `scripts/seed_database.py` (idempotent — checks existence per-record)
4. Starts uvicorn with 4 workers

This means `podman restart` is safe and won't duplicate seed data. To force a reseed, `DELETE FROM oils;` and `DELETE FROM additives;` (calculations are preserved), then restart.

## Specs & Agent-OS

This project uses spec-driven development. Historical specs are split across three directories:

- `.specify/specs/` — SpeckIt format (current standard, used by `/speckit.*` commands)
- `agent-os/specs/` — Agent-OS format (earlier specs, e.g., core calculation API, containerized deployment)
- `specs/` — working tasks.md files for active features

Constitutional rules live in `.specify/memory/constitution.md`. Coding standards are in `agent-os/standards/` (backend, frontend, global, testing) and mirrored as skills in `.claude/skills/`.

When starting new feature work: check `agent-os/product/roadmap.md` first, then follow the spec workflow (`/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`) or the Agent-OS equivalents under `.claude/commands/agent-os/`.

## Conventions

- **Python style**: ruff (line-length=100, target py311) + mypy strict (`disallow_untyped_defs=true`). All function signatures must be typed.
- **Immutable patterns** in services — prefer returning new objects over mutation.
- **Decimal not float** for percentages and weights in `percentage_calculator.py`; floats are fine inside pure numeric services that feed back into Pydantic.
- **Agent response files**: `.claude/RULES.md` requires every sub-agent delegation to produce a file under `agent-responses/[YYYYMMDD]_[HHMMSS]_[agent-type]_[task].md`. This is why that directory is large.
- **TDD** is expected per `agent-os/standards/testing/test-writing.md`: spec → failing test → implementation → passing test.

## Version History Notes

- v1.0.0: Initial API
- v1.2.0: Auto-seed at container startup (changed CMD→ENTRYPOINT, added `docker-entrypoint.sh`)
- v1.4.x: Smart additive calculator, full ingredient database (137 ingredients), INCI label generator

Check `DEPLOYMENT-HISTORY.md` and `agent-responses/` for detailed change history. Recent spec: `003-inci-label-generator`.

## Git Workflow

- **Canonical git clone**: `/Volumes/owc-express/gdrive-personal/areas/rec/mga/coding/mga-soap-calculator`
- **Remote**: `git@github.com:GreyssonEnterprises/mga-soap-calculator.git` on `main`
- **NAS mirror**: `/Volumes/public/GreyssonEnterprises/workspaces/rec/mga-brand/coding/mga-soap-calculator` — read-mostly working tree. The NAS SMB mount strips POSIX git metadata, so `.git/` cannot live there. Make edits either place, but **commits must be run from the owc-express clone**.

To sync NAS changes back into the repo: copy the changed files into owc-express, then commit there.
