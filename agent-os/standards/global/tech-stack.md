## Tech stack guardrails

- **Primary Languages**: TypeScript for Node/Frontend work, Python for automation and data tooling. Diverge only with written approval and migration plan.
- **Frontend**: React (or compatible meta-framework) + Tailwind CSS unless the spec mandates otherwise. Component libraries must be documented in `tech-stack.md` with upgrade strategy.
- **Backend**: Node.js (LTS) with NestJS/Express patterns, or Python FastAPI when Python is already dominant. Pick one per service and stick to it.
- **Persistence**: PostgreSQL as default relational store, Redis for caching/queues, S3-compatible blob storage. Any deviation requires an ADR.
- **Testing Tooling**: Jest or Vitest for TypeScript, pytest for Python. Code coverage thresholds enforced via CI; falling below redlines blocks merges.
- **Quality Gates**: ESLint + Prettier for TS, Ruff/Black for Python. Static analysis runs in CI and locally before commits.
- **Infrastructure as Code**: All infrastructure changes flow through Ansible playbooks stored in repo under `infra/ansible`. Manual SSH or ad-hoc scripts are banned.
- **Deployment Workflow**: Releases trigger Ansible playbooks via CI, pushing changes through staging before production. Every playbook declares idempotence, rollback steps, and validation commands.
- **CI/CD**: GitHub Actions pipelines run full test suite, lint, type checks, and Ansible syntax checks on every PR.
- **Observability**: OpenTelemetry-compatible logging, metrics via Prometheus/Grafana, error tracking via Sentry. Instrument new features before launch.
- **Secrets Management**: Use environment-specific secret stores (1Password Connect or AWS SSM Parameter Store). `.env` files exist only for local dev and are gitignored.
