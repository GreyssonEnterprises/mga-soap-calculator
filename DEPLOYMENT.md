# MGA Soap Calculator — Deployment

Deployment is managed from the `greysson-homelab` IaC repo. Do not deploy
from this repo.

- **Role**: `greysson-homelab/ansible/roles/mga_soap_calculator_ocp/`
- **Playbook**: `greysson-homelab/ansible/playbooks/deploy-mga-soap-calculator.yml`
- **Target**: OpenShift SNO

The previous grimm-lin / Podman-Quadlet deployment has been retired. The
`ansible/` directory and `podman/deploy.sh` that used to live here were
removed; see commit history on branch
`chore/remove-stale-deployment-artifacts` for details.

## Local development

Local dev still uses `docker-compose.yml` (works with `docker-compose` or
`podman-compose`):

```bash
docker-compose up -d     # start postgres + api
docker-compose down -v   # teardown + wipe volume
```

See `CLAUDE.md` for the full development workflow.

## Container startup

`scripts/docker-entrypoint.sh` runs inside the container on every start:

1. `pg_isready` poll (30 retries, 60s budget)
2. `alembic upgrade head` (idempotent)
3. Seed check: if `oils` or `additives` tables are empty, runs
   `scripts/seed_database.py` (idempotent per-record)
4. Starts uvicorn with 4 workers

This is unchanged across deployment targets and is the contract the
OpenShift deployment relies on.
