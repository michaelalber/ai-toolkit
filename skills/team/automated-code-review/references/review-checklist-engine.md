# Review Checklist Engine

This reference defines the detailed, per-category review checklists used by the automated code review skill. Each checklist item includes sub-items, pass/fail criteria, severity mapping for failures, and language-specific extensions.

The checklists here expand on the minimum checklists in the SKILL.md. The minimum checklists define the floor; this reference defines the full systematic procedure.


## Checklist Execution Protocol

For each file under review, the agent executes the following:

```
For each category (security, correctness, performance, maintainability, style):
  For each checklist item in the category:
    1. Execute the check (read specific code, trace specific flow)
    2. Record the result: PASS / FAIL / NOT-APPLICABLE
    3. If FAIL: create a finding with evidence
    4. If NOT-APPLICABLE: record why (e.g., "no database access in this file")
```

A checklist item is NOT-APPLICABLE when the code under review does not contain the construct the check targets. A file with no database access has N/A for the SQL injection check. A file with no loops has N/A for the off-by-one check.

A checklist item is PASS when the construct is present and correctly implemented.

A checklist item is FAIL when the construct is present and incorrectly or unsafely implemented.

**Never mark PASS without reading the relevant code. Never mark N/A as a shortcut to skip a check.**


## Security Checklist (Detailed)

### SEC-01: Input Tracing

**Check**: For every function parameter, route handler argument, or data read from external sources (HTTP request, file, environment variable, database, message queue), trace the value to every point where it is used.

**Sub-items**:
- [ ] All function parameters from public/external interfaces identified
- [ ] Each parameter traced through all code paths to terminal use
- [ ] Parameters used in SQL, shell commands, file paths, or HTML output flagged for injection checks
- [ ] Parameters passed to other functions traced transitively

**Pass criteria**: All external inputs are traced, and every terminal use is safe (parameterized, escaped, validated, or the input is trusted by design with that trust documented).

**Fail severity mapping**:
- Used in SQL without parameterization: **Critical**
- Used in shell command without escaping: **Critical**
- Used in file path without traversal check: **High**
- Used in HTML output without escaping: **High**
- Used in log output containing PII: **Medium**

### SEC-02: Authentication and Authorization

**Check**: For every endpoint, route, or public method that accesses or modifies protected resources, verify that authentication and authorization checks are present.

**Sub-items**:
- [ ] Every route/endpoint has an auth requirement (or is explicitly marked public)
- [ ] Authorization checks verify the requesting user has permission for the specific resource
- [ ] Authorization is checked at the resource level, not just the endpoint level (prevents IDOR)
- [ ] Middleware/decorator auth is consistently applied (no gaps in coverage)

**Pass criteria**: No unprotected access to protected resources. Authorization is granular to the resource, not just the action.

**Fail severity mapping**:
- Missing authentication on sensitive endpoint: **Critical**
- Missing authorization (any authenticated user can access any resource): **Critical**
- Inconsistent middleware application (some routes skip auth): **High**
- Authorization checked on read but not write: **High**

### SEC-03: Sensitive Data Handling

**Check**: Verify that sensitive data (credentials, PII, tokens, keys) is not exposed in logs, error messages, HTTP responses, or debug output.

**Sub-items**:
- [ ] Log statements do not include passwords, tokens, or keys
- [ ] Error responses do not include stack traces, internal paths, or sensitive values
- [ ] Debug/verbose modes do not expose credentials
- [ ] Sensitive fields are redacted in serialization

**Pass criteria**: No sensitive data leakage in any output path.

**Fail severity mapping**:
- Credentials in logs: **High**
- PII in error responses: **Medium**
- Stack traces in production error responses: **Low**

### SEC-04: Cryptographic Operations

**Check**: Verify that cryptographic operations use appropriate algorithms and follow best practices.

**Sub-items**:
- [ ] No use of MD5 or SHA1 for security-sensitive hashing (passwords, signatures)
- [ ] Passwords are hashed with bcrypt, scrypt, Argon2, or PBKDF2 with appropriate work factors
- [ ] No hardcoded encryption keys, API keys, or secrets
- [ ] Random number generation uses cryptographically secure sources where required
- [ ] TLS/SSL configuration does not allow deprecated protocols

**Pass criteria**: All cryptographic operations use current, appropriate algorithms with proper key management.

**Fail severity mapping**:
- Hardcoded secrets: **Critical**
- MD5/SHA1 for password hashing: **High**
- Weak random number generation for security tokens: **High**
- Deprecated TLS versions allowed: **Medium**

### SEC-05: Dependency Safety

**Check**: If package manifests or lock files are in scope, check for known vulnerabilities.

**Sub-items**:
- [ ] Package manifest identified (package.json, requirements.txt, Gemfile, pom.xml, etc.)
- [ ] Lock file present and up to date
- [ ] No dependencies with known critical CVEs

**Pass criteria**: Dependencies are declared, locked, and free of known critical vulnerabilities.

**Fail severity mapping**:
- Dependency with known critical RCE: **Critical**
- Dependency with known high-severity vulnerability: **High**
- Missing lock file: **Medium**


## Correctness Checklist (Detailed)

### COR-01: Boundary Conditions

**Check**: For every conditional, loop, array access, and range operation, verify behavior at boundaries.

**Sub-items**:
- [ ] Loop start and end conditions checked for off-by-one
- [ ] Array/list indexing checked for out-of-bounds
- [ ] Range/slice operations checked for empty range
- [ ] Integer operations checked for overflow/underflow
- [ ] Division operations checked for zero divisor

**Pass criteria**: All boundary conditions are handled correctly or are provably unreachable.

**Fail severity mapping**:
- Off-by-one causing data corruption: **High**
- Out-of-bounds causing crash on common input: **High**
- Integer overflow in security-relevant calculation: **Critical**
- Division by zero on rare edge case: **Medium**

### COR-02: Null Safety

**Check**: For every dereference of a value that could be null, nil, undefined, or None, verify that a null check precedes the dereference.

**Sub-items**:
- [ ] Function return values checked for null before use
- [ ] Optional/nullable parameters checked before dereference
- [ ] Database query results checked for "not found" before access
- [ ] Map/dictionary lookups checked for missing key

**Pass criteria**: No null dereference is possible on any reachable code path.

**Fail severity mapping**:
- Null dereference on common path: **High**
- Null dereference on error path: **Medium**
- Null dereference on theoretical edge case: **Low**

### COR-03: Error Handling

**Check**: For every operation that can fail (I/O, network, parsing, database), verify that error handling is present, correct, and complete.

**Sub-items**:
- [ ] Every fallible operation has an error handling path
- [ ] Errors are not silently swallowed (no empty catch blocks)
- [ ] Catch/except clauses are specific, not overly broad
- [ ] Error messages include diagnostic context (what failed, with what input)
- [ ] Resources are cleaned up in error paths (connections, file handles, locks)
- [ ] Errors are propagated or handled, never both ignored and not propagated

**Pass criteria**: Every error path is handled, provides diagnostic information, and cleans up resources.

**Fail severity mapping**:
- Silent exception swallowing hiding data corruption: **Critical**
- Resource leak on error path: **High**
- Overly broad catch masking bugs: **Medium**
- Missing diagnostic context in error message: **Low**

### COR-04: Concurrency Correctness

**Check**: For every piece of shared mutable state accessed from multiple threads, coroutines, or processes, verify synchronization.

**Sub-items**:
- [ ] Shared mutable state identified
- [ ] All access to shared state is synchronized (locks, atomics, channels)
- [ ] Lock ordering is consistent (no deadlock potential)
- [ ] Check-then-act sequences are atomic where required
- [ ] No TOCTOU (time-of-check-to-time-of-use) vulnerabilities

**Pass criteria**: All concurrent access to shared state is correctly synchronized.

**Fail severity mapping**:
- Data race causing corruption: **Critical**
- Deadlock potential: **High**
- Non-atomic check-then-act: **High**
- Missing synchronization on low-contention path: **Medium**


## Performance Checklist (Detailed)

### PERF-01: Algorithmic Complexity

**Check**: For every loop, nested loop, or recursive function, verify that the algorithmic complexity is appropriate for the expected input size.

**Sub-items**:
- [ ] No O(n^2) or worse on user-controlled or unbounded input
- [ ] Nested iterations over related collections checked for quadratic behavior
- [ ] Recursive functions checked for exponential blowup (missing memoization)
- [ ] Sorting, searching, and filtering use appropriate algorithms

**Pass criteria**: Algorithmic complexity matches the expected data volume on the code path.

**Fail severity mapping**:
- O(n^2) on user-facing hot path with growing data: **Critical**
- O(n^2) on backend batch path with bounded data: **Low**
- Missing memoization on exponential recursion: **High**

### PERF-02: Database Access Patterns

**Check**: For every database interaction, verify efficient access patterns.

**Sub-items**:
- [ ] No queries inside loops (N+1 pattern)
- [ ] Batch operations used where multiple records are needed
- [ ] Only required columns selected (no SELECT *)
- [ ] Pagination used for potentially large result sets
- [ ] Indexes implied by query patterns exist (or are noted)

**Pass criteria**: Database access is efficient and bounded.

**Fail severity mapping**:
- N+1 on every page load: **High**
- SELECT * on large table: **Medium**
- Missing pagination on unbounded query: **High**

### PERF-03: Resource Efficiency

**Check**: For memory allocation, I/O operations, and network calls, verify efficiency.

**Sub-items**:
- [ ] No unnecessary object creation in tight loops
- [ ] String building uses appropriate patterns (StringBuilder, join, not concatenation)
- [ ] Large data processed as streams, not loaded entirely into memory
- [ ] No redundant network calls for the same data
- [ ] Caching used where expensive operations repeat with same inputs

**Pass criteria**: Resources are used efficiently relative to the code path's frequency and data volume.

**Fail severity mapping**:
- Memory leak (unbounded growth): **Critical**
- Redundant network calls on every request: **High**
- String concatenation in loop with small, bounded iterations: **Nit**


## Maintainability Checklist (Detailed)

### MAINT-01: Function Clarity

**Check**: Each function has a single, clear responsibility that can be understood without reading the implementation.

**Sub-items**:
- [ ] Function name accurately describes what it does
- [ ] Function does one thing (single responsibility)
- [ ] Cyclomatic complexity is reasonable (below 10 for most functions)
- [ ] Nesting depth does not exceed 3-4 levels
- [ ] Function length allows comprehension in one reading (language-appropriate)

**Pass criteria**: A developer unfamiliar with the codebase can understand the function's purpose from its name and signature.

**Fail severity mapping**:
- God function doing 5+ unrelated things: **High**
- Misleading function name: **Medium**
- Slightly long but clear function: **Low**

### MAINT-02: Naming and Constants

**Check**: Names are descriptive, consistent, and free of magic values.

**Sub-items**:
- [ ] No single-letter variable names outside of tiny lambdas or loop indices
- [ ] No magic numbers or string literals without context
- [ ] Naming convention consistent within the file and with the project
- [ ] Boolean variables/parameters clearly indicate their meaning
- [ ] No misleading names (isValid returning a string, getData that modifies state)

**Pass criteria**: Code can be read without external documentation to understand what values and operations represent.

**Fail severity mapping**:
- Magic number in critical calculation: **Medium**
- Misleading name causing likely maintenance errors: **Medium**
- Minor naming inconsistency: **Nit**

### MAINT-03: Duplication

**Check**: No significant code duplication exists that should be abstracted.

**Sub-items**:
- [ ] No copy-paste blocks with minor variations (Rule of Three)
- [ ] No duplicated validation logic across endpoints
- [ ] No repeated patterns that indicate a missing abstraction

**Pass criteria**: DRY principle applied where it improves maintainability without over-abstracting.

**Fail severity mapping**:
- Same 20-line block copy-pasted 4 times: **High**
- Similar 5-line patterns in 2 places: **Low**
- Near-duplicate with structural differences suggesting different abstractions: **Nit**


## Style Checklist (Detailed)

### STYLE-01: Convention Adherence

**Check**: Code follows the project's detected conventions.

**Sub-items**:
- [ ] Naming convention matches project convention
- [ ] Indentation and formatting match project convention
- [ ] Import organization matches project convention
- [ ] File structure matches project patterns

**Pass criteria**: Code is stylistically consistent with the rest of the project.

**Note**: This checklist is only meaningful after convention detection. Style findings always reference the detected convention, not an external standard.

**Fail severity mapping**:
- Gross inconsistency (different indentation style in same file): **Medium**
- Minor convention deviation: **Nit**

### STYLE-02: Idiomatic Usage

**Check**: Code uses language-idiomatic constructs where they improve clarity.

**Sub-items**:
- [ ] Language-specific idioms used where appropriate (list comprehensions, pattern matching, etc.)
- [ ] No language feature misuse (using exceptions for control flow in languages where this is anti-idiomatic)
- [ ] API usage follows documented patterns

**Pass criteria**: Code reads naturally to a developer experienced in the language.

**Fail severity mapping**:
- Anti-idiomatic pattern causing confusion: **Low**
- Missed idiomatic opportunity with no clarity impact: **Nit**


## Language-Specific Extensions

The checklists above are language-agnostic. The following extensions add language-specific checks:

### JavaScript/TypeScript
- [ ] `===` used instead of `==` (unless intentional type coercion is documented)
- [ ] Promises are awaited or have error handlers (no unhandled rejections)
- [ ] `async` functions are not called without `await` in critical paths
- [ ] TypeScript: no `any` types without justification

### Python
- [ ] Context managers (`with`) used for resource management
- [ ] No mutable default arguments in function signatures
- [ ] f-strings or `.format()` used instead of `%` formatting for new code
- [ ] Type hints present on public function signatures

### Java/Kotlin
- [ ] Resources implement `AutoCloseable` and are used in try-with-resources
- [ ] `equals()` and `hashCode()` are overridden together
- [ ] Stream operations do not have side effects
- [ ] Nullable annotations or Optional used for values that can be absent

### Go
- [ ] Errors are checked, not discarded (`err` is not `_` without comment)
- [ ] `defer` used for resource cleanup
- [ ] Context propagation in request-scoped operations
- [ ] No goroutine leaks (goroutines have termination conditions)

### Rust
- [ ] `unwrap()` and `expect()` are not used in library code without justification
- [ ] Lifetimes are not unnecessarily complex
- [ ] Error types implement `std::error::Error`
- [ ] No `unsafe` blocks without safety documentation comments

### C#/.NET
- [ ] `IDisposable` resources are in `using` statements
- [ ] Async methods are awaited (no fire-and-forget without justification)
- [ ] LINQ queries do not cause multiple enumeration
- [ ] Null-conditional operators used where appropriate
