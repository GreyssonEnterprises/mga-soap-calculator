# MGA Soap Calculator — Ideation Summary

**Generated**: 2026-04-17
**Scope**: Code Quality + Code Improvements
**Method**: RepoPrompt static analysis (no LLM post-processing)

Full findings in `.ideation/code_quality.json` and `.ideation/code_improvements.json`. IDs prefixed `CQ-*` are code quality, `CI-*` are architectural code improvements.

---

## Top 5 Fix-Now Items

| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| **CQ-01** | critical | Two handlers registered for `GET /api/v1/additives` (resources.py vs additives.py) | S |
| **CQ-02** | high | Stray `$(ls -t migrations` directory inside `migrations/versions/` | XS |
| **CQ-03** | high | Two `pass`-only placeholder functions in `services/validation.py` (misleading dead code) | XS |
| **CQ-04** | high | Inconsistent `get_db` import path — 6 files one way, 1 file the other | S |
| **CQ-07** | medium | Bare `except Exception` in `/calculate`, `verify_password`, and `/health` — silent-failure pattern | S |

These are all low-effort and correctness-affecting. Do them this week.

---

## Structural Themes

### 1. List-endpoint boilerplate (CQ-05, CQ-06, CI-01)
Four routers copy-paste ~100 lines of pagination + search + sort. This is where CQ-01 (duplicate additives handler) came from — someone copied an existing file instead of extracting a helper. Extract `app/api/_pagination.py` before any more list endpoints are added.

### 2. Fat request handler (CQ-08, CI-03)
`create_calculation()` is 380 lines in one function, doing validation + DB fetches + math + persistence + serialization. It's untestable without FastAPI and DB. Split into `_resolve_inputs → _compute_recipe → _persist_calculation`. This is the single highest-leverage refactor in the codebase — it unblocks CQ-07 (narrow exceptions) and CI-03 (headless calculation library).

### 3. Service return types are a zoo (CI-02)
Services return hand-rolled classes, tuples, and dicts. Standardize on Pydantic or frozen dataclasses. The `three_format_inci_generator` returning `Tuple[Optional[str], Optional[str], Optional[str], List[Dict]]` is the worst case — callers have to remember positional meaning.

### 4. Two database-access styles (CI-06)
Ingestion scripts split between raw psycopg2 (`import_oils.py`) and async SQLAlchemy. Kill the psycopg2 path. Fewer deps, fewer injection surfaces.

### 5. Three deployment paths (CI-10)
`docker-compose.yml`, `docker-compose.prod.yml`, and Ansible+Quadlet all coexist with no lane separation. Pick one per environment.

### 6. Repo pollution (CI-11)
`agent-responses/` has 100+ files. `claudedocs/`, `working/`, and `.ideation/` should not be in the product repo. Move to `.agent-workspace/` (gitignored) or a sibling repo.

---

## Counts

- **app/ Python lines**: 5,173 across 42 files
- **Tests**: ~16k lines — test suite is larger than the app, which is good, but it also contains copy-paste (two 500+ line test files for resource endpoints)
- **Migrations**: 12 (mixed sequential + hash naming, plus one stray directory)
- **agent-responses/**: 100+ files committed

---

## Not-Issues (investigated, dismissed)

- **No TODO/FIXME/HACK comments** anywhere in `app/` or `scripts/`. Clean.
- **No `print()` calls** in `app/` production code. Clean.
- **Argon2id + 24h JWT expiry** is correctly configured; the silent-failure in `verify_password` is the only auth smell (CQ-07).
- **Dockerfile is solid** — multi-stage, UBI9, non-root user 1001, healthcheck, explicit entrypoint. No findings.

---

## Suggested Sprint

**Week 1 (mechanical cleanup, ~1 day total)**
- CQ-01: delete duplicate additives handler from resources.py
- CQ-02: rm stray directory
- CQ-03: delete dead placeholders in validation.py
- CQ-04: standardize `from app.db import get_db`
- CQ-10: delete Dockerfile.debian-backup
- CQ-13: fix MGA Automotive → Midnight Garden Apothecary branding
- CQ-11: remove coverage from default pytest addopts

**Week 2 (structural, ~2-3 days)**
- CQ-05 + CQ-06: extract pagination helper, convert from_orm → model_validate
- CQ-07: narrow exception handlers, add logging (pairs with CI-12)
- CI-04: derive sync URL from async URL
- CI-05: add pool_pre_ping to engine

**Week 3+ (architecture, plan carefully)**
- CQ-08 + CI-03: split create_calculation into pipeline stages
- CI-02: standardize service return types
- CI-07: move seed data to YAML fixtures

---

## Files Generated

- `.ideation/code_quality.json` (14 findings)
- `.ideation/code_improvements.json` (13 findings)
- `.ideation/index.json` (project metadata)
- `.ideation/summary.md` (this file)
