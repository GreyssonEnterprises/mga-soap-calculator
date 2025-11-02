## Coding style standards

- **Reality-First Code**: Ship only code that is exercised by real tests or runtime execution. No speculative abstractions, scaffolding, or "future features" without proof of need.
- **Intentional Naming**: Use names that communicate purpose, constraints, and side effects. Ban single-letter identifiers outside of tight algorithmic scopes.
- **Small, Focused Units**: Keep functions and modules narrowly scoped. If you cannot describe a unit's single responsibility in one clause, split it.
- **Automated Formatting**: Enforce consistent formatting (indentation, line length, ordering) via project linters/formatters. Never hand-wave formatting drift.
- **Guard Clauses & Preconditions**: Prefer guard clauses to surface invalid states immediately. Make assumptions explicit at call boundaries.
- **Traceable Decisions**: When code encodes non-obvious trade-offs, document the rationale in concise comments that reference requirements or specs.
- **Delete Dead Weight**: Remove unused code, commented-out experiments, and orphaned imports as soon as they are identified.
- **No Backwards Compatibility by Default**: Only carry legacy branches or compatibility shims when requirements demand it. Otherwise, delete and move forward.
- **Deterministic Side Effects**: Be explicit when functions mutate state or perform I/O. Hide nothing behind "helper" names.