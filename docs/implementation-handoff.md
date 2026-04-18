# Implementation Handoff: Code Quality & Refactor Campaign

**Created**: 2026-04-17
**Status**: Ready to start (Phase 0)
**Target repo**: `github.com/GreyssonEnterprises/mga-soap-calculator`
**Plan source**: `~/.claude/plans/please-create-a-plan-quiet-raven.md`
**Ideation source**: `docs/audits/2026-04-17-ideation/summary.md`

---

## TL;DR for the Incoming Session

You are picking up a refactor campaign for the MGA Soap Calculator API (FastAPI + SQLAlchemy + PostgreSQL, deployed via Ansible + Quadlet to `grimm-lin`). Static analysis surfaced 27 findings plus 653 pre-existing ruff lint errors blocking CI. The plan is four phases totaling ~2-3 weeks of work.

**Start here:**
1. Read this entire doc (verbose by design — the prior session's context is gone).
2. Read `docs/audits/2026-04-17-ideation/summary.md` for the finding catalog.
3. Read `~/.claude/plans/please-create-a-plan-quiet-raven.md` for the sequenced plan.
4. Run `ruff check . --statistics` to confirm the current ruff state matches what's documented below.
5. Begin **Phase 0 Step 0.1** (fix the one real syntax bug).

**Do NOT:**
- Start Phase 1 before Phase 0 lands and CI is green — you'll be building on a false test signal.
- Make style changes mixed with logic changes. Keep ruff auto-fix in its own commit.
- Trust any "tests pass" claim until CI is green. The test suite has a file that hasn't parsed since November.

---

## Why This Work Exists

The MGA Soap Calculator is a production API serving Shale + Jackie's soap formulation calculations. It deploys to `grimm-lin` (Fedora 42, rootless Podman, Quadlet systemd). It has real users and real data. Recent additions — the smart additive calculator, INCI label generator, oils database import — shipped behavior quickly but accreted technical debt:

- Two different pieces of code both claim ownership of `GET /api/v1/additives` (registered in two routers; one silently shadows the other)
- A 380-line request handler doing validation + DB I/O + math + persistence + serialization in one function
- Four list endpoints that copy-pasted pagination boilerplate instead of extracting a helper (which is how the duplicate route appeared)
- Services that return a mix of hand-rolled classes, dataclasses, and ambiguous 4-tuples
- 100+ AI agent session logs committed to the repo
- Three parallel spec directories (`.specify/`, `agent-os/`, `specs/`) with no canonical location
- CI has been red since November because 653 ruff errors accumulated and nobody fixed them

None of this blocks users today. All of it will slow the next feature.

**Strategic goal**: Kill the bug (CQ-01), retire the debt, and set up the codebase so a future headless calculation library (desktop app? CLI?) is a weekend project instead of a month.

---

## Repo State Right Now (2026-04-17)

### Git

- **Canonical clone**: `/Volumes/owc-express/gdrive-personal/areas/rec/mga/coding/mga-soap-calculator`
  - Branch: `main`
  - HEAD: `f1d6c58` (`docs(claude): track CLAUDE.md with expanded architecture reference`)
  - Remote: `git@github.com:GreyssonEnterprises/mga-soap-calculator.git`
  - Clean working tree
- **NAS mirror**: `/Volumes/public/GreyssonEnterprises/workspaces/rec/mga-brand/coding/mga-soap-calculator`
  - NOT a git repo — the SMB share strips POSIX git metadata
  - Used for read-mostly browsing + editing; commits must go through owc-express
- **GitHub**: `github.com/GreyssonEnterprises/mga-soap-calculator`
  - Default branch `main` at `f1d6c58`
  - CI: **currently failing** (run 24597857867) due to the 653 ruff errors — this is Phase 0's target

### Recent commits (2026-04-17 session)

```
f1d6c58 docs(claude): track CLAUDE.md with expanded architecture reference
2bf3ea9 chore(agent-responses): archive 2026-11-16 ARM64 build investigation logs
2bc07d6 docs(audits): 2026-04-17 code quality + improvements ideation
d6d53ff feat(scripts): add oils database import script
074f236 fix(deploy): x86_64 cross-compile for grimm-lin and correct health check path
d578cc1 updated                           ← previous HEAD before this session
```

### Production

- **URL**: `http://grimm-lin:8000`
- **Health**: `http://grimm-lin:8000/api/v1/health`
- **Running version**: last deployed was v1.4.1 (before this session's commits). The x86_64 build fix + health URL fix (`074f236`) are committed but **not yet deployed**. Next deploy will pick them up.
- **Deploy command**:
  ```fish
  cd ansible
  ansible-playbook playbooks/build-and-deploy.yml \
    -e "app_version=1.X.Y" \
    --vault-password-file ~/.config/pai/secrets/ansible_vault_pw
  ```

---

## The 28 Issue Classes (quick reference)

Full details in `docs/audits/2026-04-17-ideation/summary.md`. Condensed:

### Critical (1)
- **CQ-01**: Duplicate `GET /api/v1/additives` handler in `app/api/v1/resources.py` and `app/api/v1/additives.py`. The resources.py version is registered first in `app/main.py` but the additives.py version owns the `?category=` filter. Active prod issue.

### High (8)
- **CQ-02**: Stray directory `migrations/versions/$(ls -t migrations/` — shell-expansion artifact
- **CQ-03**: Two `pass`-only placeholder functions in `app/services/validation.py:221-249`. Tests import them (`tests/unit/test_validation_logic.py:162-180`) — **don't delete without fixing tests**
- **CQ-04**: Inconsistent `get_db` import path (7 files)
- **CQ-05**: List-endpoint pagination boilerplate copy-pasted 4 times (~100 lines of dupe)
- **CI-01**: Router-to-resource mapping ambiguous (same root cause as CQ-01)
- **CI-02**: Service return types inconsistent (classes, tuples, dicts)
- **CI-03**: No request/service boundary — `calculate.py` does DB access, validation, and math in one function
- **NEW** (from Phase 0 discovery): **`tests/unit/test_essential_oil_import.py:174` has a real parse error** — `class TestBlendsWith ArrayHandling:` has a space in the class name. File has never run.

### Medium (11)
CQ-06, CQ-07, CQ-08, CQ-09, CQ-10, CQ-11, CI-04, CI-05, CI-06, CI-07, CI-08, CI-09, CI-10, CI-12

### Low (5)
CQ-12, CQ-13, CQ-14 (moot — CI does enforce), CI-11, CI-13

---

## The Ruff Situation (Phase 0 detail)

```
145  E501  line-too-long                    (manual or ruff format)
114  I001  unsorted-imports                 (auto-fix)
 94  UP006 non-pep585-annotation            (auto-fix: List → list)
 82  UP045 non-pep604-annotation-optional   (auto-fix: Optional[X] → X | None)
 69  F401  unused-import                    (auto-fix)
 50  UP035 deprecated-import                (semi-auto: typing module)
 36  UP007 non-pep604-annotation-union      (auto-fix: Union[A,B] → A | B)
 14  F541  f-string-missing-placeholders    (auto-fix)
  9  F841  unused-variable                  (manual review — could be dead code)
  8  E721  type-comparison                  (manual: type(x)==Y → isinstance)
  7  UP015 redundant-open-modes             (auto-fix)
  7  UP017 datetime-timezone-utc            (auto-fix)
  6  W292  missing-newline-at-end-of-file   (auto-fix)
  4  [syntax] invalid-syntax                (REAL BUG — 1 file, 4 errors)
  4  E402  module-import-not-at-top         (manual)
  2  E712  true-false-comparison            (manual)
  2  F821  undefined-name                   (false positive — SQLAlchemy forward refs)
```

**Total: 653 errors. 442 auto-fixable.**

### The one real bug
- File: `tests/unit/test_essential_oil_import.py`
- Line 174: `class TestBlendsWith ArrayHandling:` (space in class name)
- Effect: File fails to parse, all 4 invalid-syntax errors come from this single mistake
- Fix: Remove the space. Run the file. Triage whatever real failures emerge underneath.

### The false positives
- File: `app/models/calculation.py:87` — `Mapped["User"]`
- File: `app/models/user.py:92` — `Mapped["Calculation"]`
- Both are valid SQLAlchemy forward-ref strings. Ruff can't see through them.
- Fix: Add `per-file-ignores` in `pyproject.toml`:
  ```toml
  [tool.ruff.lint.per-file-ignores]
  "app/models/*.py" = ["F821"]
  ```

### Note on pyproject.toml
Ruff emits this warning every run:
```
warning: The top-level linter settings are deprecated in favour of their counterparts in the `lint` section.
  - 'ignore' -> 'lint.ignore'
  - 'select' -> 'lint.select'
```
Migrate the ruff config while you're in there. Small change, removes warning noise.

---

## Architecture Primer (for someone new to the codebase)

### Stack
- Python 3.11+, FastAPI, uvicorn
- SQLAlchemy 2.0 async + asyncpg + psycopg2-binary (the sync driver is only for Alembic)
- Alembic migrations
- PostgreSQL 15 (UBI 9 image in prod, postgres:15-alpine in dev)
- pytest + pytest-asyncio (asyncio_mode=auto)
- Podman (Quadlet systemd units) in prod, docker-compose for local dev
- Ansible for orchestration, Ansible Vault for secrets

### Request flow
```
HTTP → app/main.py (FastAPI, custom OpenAPI, CORS, catch-all for missing /v1/)
     → app/api/v1/*.py (routers: auth, calculate, resources, additives,
                         essential_oils, colorants, inci)
     → app/schemas/*.py (Pydantic request/response)
     → app/services/*.py (pure calculation logic — no DB)
     → app/models/*.py (SQLAlchemy async ORM)
     → app/db/base.py (async session via get_db dependency)
```

**Gotcha**: `main.py` registers a catch-all at the end to return friendly 404s for requests missing the `/v1/` prefix. Any new router MUST be `include_router`'d before this catch-all or its routes will be 404'd.

### The service layer is the interesting part
`app/services/` is pure calculation code. Stateless. No DB, no framework. These are called from `calculate.py` but hold no session:

- `lye_calculator.py` — NaOH/KOH saponification math, mixed-lye, purity-adjusted
- `water_calculator.py` — three calculation methods (percent_of_oils, lye_concentration, water:lye ratio)
- `quality_metrics_calculator.py` — base metrics from oils + **additive effect modeling** (the competitive differentiator — no other soap calc does this)
- `fatty_acid_calculator.py` — fatty acid profile, sat:unsat ratio
- `percentage_calculator.py` — Decimal arithmetic with ROUND_HALF_UP
- `validation.py` — percentage sum checks, warnings, rounding
- `inci_naming.py` + `label_generator.py` + `three_format_inci_generator.py` — INCI label generation

When adding calc features: math goes in `app/services/`, imported into the router, unit-tested against the service directly.

### Container startup
`scripts/docker-entrypoint.sh` runs on every start:
1. `pg_isready` poll (30 retries, 60s)
2. `alembic upgrade head` (idempotent)
3. Seed check: if `oils` or `additives` count is 0, run `scripts/seed_database.py`
4. Start uvicorn with 4 workers

Restart is safe. To force reseed: `DELETE FROM oils; DELETE FROM additives;` then restart.

### Deployment
Ansible builds from Dockerfile (not compose), loads into remote Podman via `podman load`, writes Quadlet systemd units from `podman/systemd/*.container`, starts via user-scope systemd. Previous image tarballs kept in `/data/podman-apps/mga-soap-calculator/images/` on grimm-lin for rollback.

`docker-compose.yml` is dev-only. `docker-compose.prod.yml` is **dead code** (CI-10 — delete in Phase 1).

---

## Execution Protocol

### Before any phase

1. Verify you're in the canonical clone:
   ```fish
   cd /Volumes/owc-express/gdrive-personal/areas/rec/mga/coding/mga-soap-calculator
   pwd; git remote -v; git status
   ```
   Must be clean, on main, remote `GreyssonEnterprises/mga-soap-calculator`.

2. Pull latest:
   ```fish
   git pull origin main
   ```

3. Create a feature branch for the phase:
   ```fish
   git checkout -b phase0-ruff-cleanup  # or phase1-*, phase2-*, phase3-*
   ```

### During the phase

- Commit in atomic, logical groups. One auto-fix commit. One per-rule-category commit. One per CQ/CI finding commit.
- Keep style changes out of logic commits. Keep logic changes out of style commits.
- **Never `git commit --no-verify`**. If pre-commit hooks fail, fix the cause. (Bob's global rule.)
- Every commit must end with:
  ```
  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
  ```
  (See any of the 5 commits from the sync session for format examples.)

### After the phase

1. Run the full verification suite documented in the plan phase.
2. Push the branch, open PR against main.
3. Wait for CI green.
4. Merge, version bump per plan (`v1.4.2` after Phase 0, etc.).
5. Deploy if the phase touched production concerns (Phase 1 touches deployment files — deploy it).

### If you get stuck

- Check `docs/audits/2026-04-17-ideation/` for finding details
- Check `~/.claude/plans/please-create-a-plan-quiet-raven.md` for full phase detail
- Check `agent-responses/` for historical investigation logs (specifically the 2026-11-16 ARM64 build investigation if deployment breaks)
- If a test reveals a genuine bug underneath: file it as a new finding, don't try to fix it inside the current phase (scope discipline)

---

## Decisions Already Made (don't re-litigate)

- **Scope**: All 27 findings + ruff cleanup. User confirmed "All, phased" during planning.
- **Agent artifacts**: Move to `.agent-workspace/` gitignored (CI-11). User confirmed.
- **`create_calculation` refactor**: In scope, planned for Phase 3. User confirmed.
- **CLAUDE.md tracking**: Un-gitignored (reversed the `01ea8b1` decision) and committed at `f1d6c58`.
- **NAS vs owc-express**: owc-express is canonical. NAS is read-mostly mirror. Commits go through owc-express.
- **CI enforcement**: Ruff + mypy + pytest all block merges. Phase 0 restores this guarantee.

## Decisions That Need Input

- **Phase 0 commit structure**: Single "big bang" ruff --fix commit, or split by rule category? The plan defaults to split-by-category so bisect works.
- **Migration renaming (CI-08)**: Leave existing sequential names and adopt Alembic-default going forward (lower risk) vs. renaming all 7 to hash-prefixed (uniform but invasive). Plan defaults to the low-risk option.
- **Seed data YAML (CI-07)**: Phase 3 scope. Shape of the YAML (one-oil-per-file vs. single-list) isn't pinned down.

---

## Contact / Context

- **Owner**: Grimm Greysson (principal)
- **Primary AI assistant**: Bob (this session's agent)
- **Shell**: fish (scripts must be fish-compatible)
- **Editor**: Cursor IDE
- **Production host**: grimm-lin (Fedora 42, rootless Podman)
- **Vault password**: `~/.config/pai/secrets/ansible_vault_pw`
- **gh auth**: `grimmolf` account, `repo` + `workflow` scopes (used for this sync)

## First Commands for the Next Session

```fish
# 1. Navigate and verify
cd /Volumes/owc-express/gdrive-personal/areas/rec/mga/coding/mga-soap-calculator
git pull origin main
git log --oneline -5   # should show f1d6c58 at HEAD

# 2. Confirm ruff state matches docs
ruff check . --statistics 2>&1 | tail -25
# Expected: 653 errors, 442 fixable

# 3. Start Phase 0
git checkout -b phase0-ruff-cleanup

# 4. Fix the real bug first
$EDITOR tests/unit/test_essential_oil_import.py   # line 174: remove space in class name
pytest tests/unit/test_essential_oil_import.py -v # see what surfaces

# 5. Fix pyproject.toml ruff config (migrate to lint.*, add per-file-ignores)
$EDITOR pyproject.toml

# 6. Run the auto-fixer
ruff check . --fix --unsafe-fixes
ruff format .
git add -A
git commit -m "style: resolve auto-fixable ruff lints (442 fixes)

Ran ruff check --fix --unsafe-fixes + ruff format across the codebase.
Covers I001, UP006, UP045, UP007, F401, UP015, UP017, W292, F541,
plus format-driven E501 wrapping.

No behavior changes.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

# 7. Iterate on the remaining ~200 manual items per plan Phase 0.4

# 8. Verify green, push, PR
ruff check . && ruff format --check . && pytest -q && mypy app
git push -u origin phase0-ruff-cleanup
gh pr create --title "Phase 0: ruff cleanup + CI green" --body "See docs/implementation-handoff.md"
```

## Reference Links

- Plan: `~/.claude/plans/please-create-a-plan-quiet-raven.md`
- Ideation: `docs/audits/2026-04-17-ideation/summary.md`
- Findings JSON: `docs/audits/2026-04-17-ideation/{code_quality,code_improvements}.json`
- Repo: `https://github.com/GreyssonEnterprises/mga-soap-calculator`
- Failing CI run: https://github.com/GreyssonEnterprises/mga-soap-calculator/actions/runs/24597857867
- CLAUDE.md (architecture primer): `/CLAUDE.md` at repo root

---

**Good luck. The work is scoped, the plan is sequenced, the repo is aligned. Start with Phase 0. Don't skip ahead.**
