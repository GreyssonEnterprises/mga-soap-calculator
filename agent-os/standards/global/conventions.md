## General development conventions

- **Truth Over Comfort**: Communicate real system status, risks, and failures immediately. No sugar-coating, no "probably fine" guesses, and absolutely no unverified claims.
- **One Feature at a Time**: Work in focused slices. Do not parallelize implementation without explicit approval. A feature is unfinished until code, tests, docs, and verification land together.
- **Spec Discipline**: Keep `requirements.md`, `spec.md`, and `tasks.md` accurate. Update them the moment reality diverges; never leave breadcrumbs for someone else.
- **Version Control Hygiene**: Use short-lived branches, descriptive commit messages, and rebases that preserve narrative clarity. Do not merge without green tests and self-review notes.
- **Environment Stewardship**: Configuration lives in environment variables or dedicated secrets management. Credentials and private data never touch source control.
- **Dependency Skepticism**: Introduce new libraries only with documented justification, security review, and maintenance plan. Remove unused dependencies aggressively.
- **Code Review Contract**: Reviews focus on correctness, test coverage, and long-term maintainability. Reviewers must pull the branch, run tests, and call out unverified assumptions.
- **Fail-Loud Ops**: Instrument everything. Metrics, logs, and alerts must surface regressions quickly. Silent failure is considered a bug.
- **Changelog & Decision Logs**: Maintain human-readable release notes and architectural decision records so decisions stay visible after context fades.
- **Radical Transparency in Documentation**: README and onboarding docs must enumerate limitations, trade-offs, and known debts—not just happy paths.
- **Ansible-Only Deployments**: All configuration drift, environment provisioning, and deployments run through versioned Ansible playbooks. Manual shell work is grounds for rollback and post-mortem.
