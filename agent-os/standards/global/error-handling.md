## Error handling standards

- **Loud Failures**: Never swallow errors. Raise, log, and surface them with enough context to debug without guesswork.
- **Specific Exception Types**: Use precise exception classes so handlers can differentiate user error, system failure, and dependency timeouts.
- **Actionable Messaging**: Users get plain-language guidance; operators get structured logs with correlation IDs, stack traces, and payload fingerprints.
- **Boundary Handling**: Centralize error translation at module boundaries. Inside a module, let errors bubble until you can add context once.
- **Graceful Degradation with Alerts**: When you fallback, emit telemetry that makes the degradation obvious. Silent fallback equals hidden bug.
- **Retry with Guards**: Only retry idempotent operations, with bounded attempts and jitter. Record retries so runbooks can spot chronic pain.
- **Resource Hygiene**: Always release resources in success and failure paths. Leaks are production incidents waiting to happen.
- **Post-Mortem Ready**: Capture enough context (request ids, user ids, feature flags) that we can build timelines without reproducing the crash.
