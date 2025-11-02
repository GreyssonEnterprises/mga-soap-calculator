## Validation standards

- **Fail Before Work Begins**: Validate requirements, inputs, and preconditions before allocating compute or calling dependencies. Reject invalid states immediately.
- **Symmetric Validation**: Mirror validation rules across clients, APIs, background jobs, and CLIs so data cannot sneak around guardrails.
- **Edge-Case Coverage**: Design validators from real-world boundary data—empty strings, nulls, extremes, race conditions—not just happy paths.
- **Structured Error Payloads**: Return machine- and human-readable validation errors that include field, constraint, and remediation guidance.
- **Allowlist Mindset**: Define what is valid and reject everything else. Blocklists are last resort for legacy patches only.
- **Contextual Business Rules**: Keep domain validations in the domain layer so they evolve with requirements. Configuration belongs in code, not tribal knowledge.
- **Auditability**: Log validation failures with identifiers and user context (minus secrets) so we can trace patterns and abuse attempts.
- **Sanitize & Escape**: Apply input sanitization and output escaping appropriate to the sink (SQL, HTML, shell) even after validation succeeds.
- **Contract Tests**: Treat validation rules as API contracts. Write explicit tests for required fields, optional fields, and mutually exclusive combinations.
