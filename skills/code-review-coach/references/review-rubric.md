# Code Review Rubric

This rubric defines the five review categories, what to look for in each, common misses by difficulty level, severity guidelines, and the scoring methodology used by the code review coach.


## Review Categories

### 1. Security

Security findings address vulnerabilities that could be exploited by malicious actors or that expose sensitive data.

**What to look for:**

1. **Injection vulnerabilities** -- SQL injection, command injection, LDAP injection, XPath injection. Trace every user-controlled input to where it is consumed.
2. **Authentication and authorization gaps** -- Missing permission checks, broken access control, privilege escalation paths, insecure session handling.
3. **Sensitive data exposure** -- Credentials in code, PII in logs, secrets in error messages, unencrypted sensitive data at rest or in transit.
4. **Input validation failures** -- Missing validation, insufficient validation, validation on the client but not the server, type confusion.
5. **Cryptographic weaknesses** -- Weak algorithms (MD5 for passwords, SHA1 for signatures), hardcoded keys, predictable random values where cryptographic randomness is required.
6. **Deserialization risks** -- Untrusted data deserialized without validation, use of insecure deserialization formats (e.g., Java ObjectInputStream without filtering).
7. **Path traversal** -- User-controlled file paths without sanitization, directory traversal via "../" sequences.
8. **Cross-site scripting (XSS)** -- Unescaped user input rendered in HTML, DOM-based XSS, stored XSS via database round-trips.
9. **Race conditions with security impact** -- Time-of-check to time-of-use (TOCTOU) vulnerabilities, double-spend scenarios, authentication bypass via race.
10. **Dependency vulnerabilities** -- Known-vulnerable library versions, transitive dependency risks, unmaintained dependencies with open CVEs.

**Common misses by difficulty:**

| Difficulty | Commonly Missed |
|------------|----------------|
| Beginner | Hardcoded credentials, string concatenation in SQL queries |
| Intermediate | Missing authorization checks on internal APIs, secrets in log output |
| Advanced | TOCTOU race conditions, second-order injection (stored input used later in unsafe context) |
| Expert | Timing side-channel attacks, subtle type confusion in deserialization, cryptographic oracle attacks |

**Severity guidelines for security:**
- **Critical**: Remote code execution, SQL injection, authentication bypass, direct access to sensitive data without authorization
- **High**: Stored XSS, privilege escalation, insecure direct object references, missing authorization on sensitive endpoints
- **Medium**: Reflected XSS requiring social engineering to exploit, information disclosure (stack traces, version numbers), weak but not broken cryptography
- **Low**: Missing security headers, verbose error messages with non-sensitive internal details
- **Nit**: Security best practice suggestions with no demonstrated attack vector in context


### 2. Correctness

Correctness findings address logic errors, incorrect behavior, and bugs that cause the code to produce wrong results.

**What to look for:**

1. **Off-by-one errors** -- Loop boundaries, array indexing, string slicing, fence-post problems in pagination or range calculations.
2. **Null/undefined handling** -- Missing null checks before dereference, incorrect assumptions about optional values, silent null propagation.
3. **Edge cases** -- Empty collections, zero values, negative numbers, maximum integer values, empty strings, Unicode edge cases.
4. **Logic errors** -- Inverted conditions, wrong boolean operators (AND vs OR), incorrect comparison direction, short-circuit evaluation side effects.
5. **State management bugs** -- Stale state, missing state updates, incorrect initialization, state mutation in unexpected order.
6. **Error handling defects** -- Swallowed exceptions, incorrect catch scope (too broad or too narrow), missing cleanup in error paths, error messages that mislead debugging.
7. **Type errors** -- Implicit coercion surprises (JavaScript "1" + 1), integer overflow, floating-point comparison with equality, signed/unsigned confusion.
8. **Concurrency correctness** -- Data races, deadlock potential, lost updates, non-atomic check-then-act sequences, incorrect lock scope.
9. **API contract violations** -- Returning wrong HTTP status codes, violating function postconditions, breaking interface contracts, inconsistent return types.
10. **Resource leaks** -- Unclosed file handles, database connections not returned to pool, event listener accumulation, unreleased locks.

**Common misses by difficulty:**

| Difficulty | Commonly Missed |
|------------|----------------|
| Beginner | Off-by-one in loops, missing null checks, division by zero |
| Intermediate | Exception swallowing, resource leaks in error paths, incorrect boolean logic |
| Advanced | Race conditions in concurrent code, floating-point comparison errors, integer overflow in edge cases |
| Expert | Subtle state ordering bugs, distributed system consistency issues, linearizability violations |

**Severity guidelines for correctness:**
- **Critical**: Data corruption, silent wrong results in production path, loss of user data
- **High**: Crash on common input, incorrect business logic on non-edge path, resource leak under load
- **Medium**: Crash on edge case input, incorrect handling of rare but valid input, minor data inconsistency
- **Low**: Cosmetic result difference, edge case that only affects internal tooling
- **Nit**: Theoretical correctness issue with no practical trigger in current usage


### 3. Performance

Performance findings address code that is slower, more resource-intensive, or less scalable than it needs to be.

**What to look for:**

1. **Algorithmic complexity** -- O(n^2) where O(n) or O(n log n) is possible, nested loops over growing datasets, repeated linear searches in a collection.
2. **N+1 query patterns** -- Database query inside a loop, lazy loading that triggers per-row queries, missing eager loading or batching.
3. **Unnecessary allocation** -- Creating objects in tight loops, string concatenation in loops (instead of StringBuilder/join), unnecessary copying of large data structures.
4. **Missing caching** -- Repeated expensive computation with same inputs, redundant network calls, re-parsing configuration on every request.
5. **Blocking operations** -- Synchronous I/O in async context, blocking the event loop, holding locks during I/O operations.
6. **Unbounded growth** -- Collections that grow without limit, caches without eviction, log buffers without rotation.
7. **Premature loading** -- Loading entire dataset when only a subset is needed, fetching all columns when only some are required, deserializing full objects for partial use.
8. **Inefficient data structures** -- Using a list for frequent lookups (should be a set or map), using a linked list for indexed access, wrong collection type for the access pattern.
9. **Missing pagination** -- Loading all records for display of a page, unbounded query results, streaming entire files into memory.
10. **Serialization overhead** -- Excessive serialization/deserialization in hot paths, inefficient serialization format for the use case, redundant encoding conversions.

**Common misses by difficulty:**

| Difficulty | Commonly Missed |
|------------|----------------|
| Beginner | String concatenation in loops, loading all records for count, linear search in repeated calls |
| Intermediate | N+1 query pattern, missing index hints, synchronous I/O in async handler |
| Advanced | Subtle O(n^2) from nested iteration over related collections, cache stampede conditions |
| Expert | False sharing in concurrent data structures, GC pressure from allocation patterns, tail latency amplification |

**Severity guidelines for performance:**
- **Critical**: O(n^2) or worse on user-facing path with growing data, memory leak that will cause OOM in production
- **High**: N+1 queries on common page load, blocking I/O in async hot path, unbounded collection growth
- **Medium**: Suboptimal algorithm on non-hot path, missing cache for expensive but infrequent operation
- **Low**: Minor allocation inefficiency, suboptimal data structure choice with small dataset
- **Nit**: Micro-optimization opportunity with no measurable impact


### 4. Maintainability

Maintainability findings address code that is difficult to understand, modify, or extend.

**What to look for:**

1. **Naming clarity** -- Ambiguous variable names (data, result, temp, val), misleading names (isValid returns a string), inconsistent naming conventions within the module.
2. **Function complexity** -- Functions doing more than one thing, excessive cyclomatic complexity, deeply nested conditionals, functions longer than can be understood in one reading.
3. **Coupling** -- Tight coupling between modules, classes that know too much about each other's internals, inappropriate intimacy, feature envy.
4. **Duplication** -- Copy-pasted logic with minor variations, duplicated validation, repeated patterns that should be abstracted. Apply the Rule of Three.
5. **Abstraction level mixing** -- High-level business logic interleaved with low-level I/O, SQL queries embedded in business logic, HTTP concerns in domain model.
6. **Magic values** -- Hardcoded numbers without explanation, string literals used as identifiers, boolean parameters without context ("process(data, true, false)").
7. **Missing or misleading comments** -- Complex logic without explanation, comments that contradict the code, commented-out code left in place.
8. **Poor error messages** -- Generic error strings, missing context in exceptions, errors that do not help the operator diagnose the problem.
9. **Implicit dependencies** -- Global state, singletons used for communication, method behavior that depends on call order, temporal coupling.
10. **Test impediments** -- Untestable design (hardcoded dependencies, static method calls for external services), God objects, hidden side effects.

**Common misses by difficulty:**

| Difficulty | Commonly Missed |
|------------|----------------|
| Beginner | Magic numbers, misleading variable names, commented-out code |
| Intermediate | Feature envy, abstraction level mixing, implicit temporal coupling |
| Advanced | Subtle coupling through shared mutable state, design patterns applied where simpler solutions exist |
| Expert | Systemic coupling that limits future extension, Primitive Obsession across module boundaries, missing domain concepts |

**Severity guidelines for maintainability:**
- **Critical**: Untestable architecture, coupling that prevents independent deployment, code that no one on the team can modify safely
- **High**: Function with cyclomatic complexity above 15, copy-paste duplication across multiple files, abstraction level violations that confuse the domain model
- **Medium**: Long function that should be extracted, missing constants for magic values, naming inconsistency within a module
- **Low**: Minor naming improvement opportunity, comment that could be clearer, slightly verbose implementation
- **Nit**: Stylistic preference about abstraction approach, alternative naming suggestion with no clarity improvement


### 5. Style

Style findings address formatting, convention adherence, and code consistency.

**What to look for:**

1. **Formatting consistency** -- Indentation, brace placement, line length, blank line usage -- consistent with the project's style.
2. **Language idioms** -- Using language-idiomatic constructs (list comprehensions in Python, pattern matching in Rust, streams in Java) where appropriate.
3. **Import organization** -- Unused imports, wildcard imports, import ordering inconsistent with project convention.
4. **Dead code** -- Unreachable code, unused variables, unused function parameters, unused private methods.
5. **Consistency with codebase** -- Following established patterns in the project even if you prefer a different approach.
6. **API design conventions** -- Consistent method signatures, consistent return types, consistent error signaling within the module.
7. **File organization** -- Related code grouped together, logical ordering of methods (public before private, lifecycle order), module-level organization.
8. **Documentation style** -- Docstring format consistent with project, parameter documentation present where needed, return value documented.

**Common misses by difficulty:**

| Difficulty | Commonly Missed |
|------------|----------------|
| Beginner | Unused imports, inconsistent indentation, dead code |
| Intermediate | Non-idiomatic constructs, inconsistency with codebase patterns |
| Advanced | Subtle API design inconsistencies, file organization that hinders discoverability |
| Expert | Style issues are rarely the focus at expert level; they should be automatic |

**Severity guidelines for style:**
- **Critical**: N/A -- style issues are never critical
- **High**: Rarely -- only if style violation causes genuine confusion or hides bugs
- **Medium**: Significant deviation from project standards that affects readability
- **Low**: Minor formatting inconsistency, non-idiomatic but clear code
- **Nit**: Subjective preference, trivial whitespace, import ordering


## Scoring Methodology

### Per-Finding Scoring

Each finding is evaluated on three axes:

1. **Detection**: Did the user identify a real issue? (binary: yes/no)
2. **Category Accuracy**: Did the user assign the correct category? (binary: correct/incorrect)
3. **Severity Accuracy**: Did the user assign appropriate severity? (graded: exact match = 1.0, one level off = 0.5, two or more levels off = 0.0)

### Per-Round Scoring

**Detection Rate:**
```
detection_rate = confirmed_findings / total_expert_findings * 100
```

**False Positive Rate:**
```
false_positive_rate = false_positives / total_user_findings * 100
```

**Severity Accuracy** (over confirmed findings only):
```
severity_accuracy = sum(severity_scores) / confirmed_findings * 100
```

**Category Accuracy** (over confirmed findings only):
```
category_accuracy = correct_categories / confirmed_findings * 100
```

**Overall Round Score** (weighted composite):
```
overall = (detection_rate * 0.50) + (severity_accuracy * 0.20) + (category_accuracy * 0.15) + ((100 - false_positive_rate) * 0.15)
```

Detection is weighted most heavily because finding issues is the foundational skill. Severity and category accuracy are secondary skills that build on detection. False positive avoidance is weighted to discourage shotgun reviewing.

### Per-Session Scoring

Session score is the average of all round scores, with an improvement bonus:

```
session_score = average(round_scores)
improvement_bonus = max(0, final_round_score - first_round_score) * 0.10
adjusted_session_score = session_score + improvement_bonus
```

The improvement bonus rewards learning trajectory, not just absolute performance.

### Category-Level Tracking

Across rounds, track detection rate per category. This reveals the user's review profile:

| Profile Pattern | Meaning | Coaching Action |
|----------------|---------|-----------------|
| High security, low correctness | User has security training but misses logic bugs | Present challenges with subtle correctness issues |
| High style, low everything else | User reviews superficially | Reduce style issues in challenges, increase substantive issues |
| High correctness, low security | User thinks like a developer, not an attacker | Present challenges requiring attacker mindset |
| Flat low across all categories | User is new to code review | Start at beginner difficulty, build one category at a time |
| Flat high across all categories | User is skilled | Increase difficulty, introduce ambiguous and debatable issues |


## Calibration Examples

These examples illustrate how to classify severity consistently.

### Critical

- SQL injection via string concatenation with user input in a query that modifies data
- Authentication bypass: function returns true for authorization without checking credentials
- Infinite loop on production hot path triggered by common input
- Data corruption: concurrent write to shared state without synchronization in a write-heavy path

### High

- Missing authorization check on an endpoint that returns user PII
- Off-by-one error that causes the last item in a paginated result to be skipped
- N+1 query pattern on a page that loads for every logged-in user
- Resource leak: database connection opened but not closed in the error path

### Medium

- Reflected XSS requiring social engineering to exploit
- Exception caught and logged but original stack trace discarded, making debugging difficult
- O(n^2) algorithm on a dataset that is currently small but has no size bound
- Magic number used as a timeout value with no comment explaining the choice

### Low

- Verbose error message that includes internal class names but no sensitive data
- String concatenation in a loop that processes a small, bounded list
- Function with 4 parameters that could be grouped into a configuration object
- Inconsistent method naming within a file (camelCase mixed with snake_case)

### Nit

- Trailing whitespace on a line
- Import that could be more specific (importing the module vs. the specific function)
- Variable named `x` in a 3-line lambda where context makes meaning obvious
- Comment restating what the code does ("increment counter by 1")
