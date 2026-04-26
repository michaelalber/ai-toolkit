# Root Cause Taxonomy

Common root cause categories for bug triage. Use these to classify the probable
failure point and route to the right team.

## Categories

### Input validation / boundary
Cause: unexpected input not handled — null, empty, out-of-range, wrong type, wrong encoding.
Signals: NullReferenceException, IndexOutOfRange, parse errors, 400 responses from internal services.
Owner: the layer that first receives the input.

### State / race condition
Cause: code assumes state that isn't guaranteed — timing, ordering, concurrency.
Signals: intermittent failures, works in isolation but fails under load, fixes itself on retry.
Owner: service or module managing the shared state.

### Integration / contract mismatch
Cause: two systems disagree on data format, API contract, or protocol version.
Signals: serialization errors, 4xx from external services, field missing or renamed.
Owner: the integration layer or API client.

### Configuration / environment
Cause: missing or wrong config value, environment variable, feature flag, or secret.
Signals: works locally, fails in staging/prod; error message references a config key.
Owner: platform/infra team or the service that reads the config.

### Data / migration
Cause: existing data doesn't match the new schema or assumptions.
Signals: fails only on records created before a certain date or migration.
Owner: the team that ran the migration.

### Logic error
Cause: algorithm or business rule is implemented incorrectly.
Signals: consistently wrong output for a specific input range, off-by-one, wrong formula.
Owner: the feature team.

### Dependency regression
Cause: a library, service, or platform version changed behavior.
Signals: started failing after a dependency upgrade; changelog has a breaking change.
Owner: the team that upgraded the dependency.

### Resource exhaustion
Cause: memory leak, connection pool exhausted, disk full, rate limit hit.
Signals: works initially, degrades over time; errors reference limits or quotas.
Owner: platform/infra team with feature team input on resource usage patterns.
