# OWASP Top 10 — Rust Security Checklist

Rust-specific OWASP Top 10 (2025) checklist. Apply during security reviews of Rust
web applications, APIs, and services.

---

## Pre-Review Commands

```bash
cargo audit                          # Check for CVEs in dependencies
cargo deny check                     # License and dependency policy (if configured)
grep -rn "unsafe" src/ | wc -l      # Count unsafe blocks
grep -rn "unsafe" src/ | grep -v "// SAFETY:"  # Find unsafe without SAFETY comments
grep -rn "format!" src/ | grep -i "sql\|query"  # Find potential SQL injection
grep -rn "\.unwrap()\|\.expect(" src/ | grep -v "#\[cfg(test)\]"  # Find unwrap in production
```

---

## A01 — Broken Access Control

### Authentication Middleware
- [ ] Every protected route group has authentication middleware applied
- [ ] Auth middleware is applied at the router level, not per-handler
- [ ] No route accidentally excluded from auth middleware
- [ ] Admin/internal endpoints require elevated privileges

```bash
# For Axum: check that Router::new() calls include auth layer
grep -rn "Router::new\|\.layer(\|\.route_layer(" src/ --include="*.rs"
```

### Authorization
- [ ] Resource ownership is verified before access (not just authentication)
- [ ] User ID from auth token is used for data access, not from request body/params
- [ ] No direct object references that expose other users' data
- [ ] Role-based access control is enforced consistently

### JWT/Token Validation
- [ ] JWT signature is verified (not just decoded)
- [ ] JWT expiration (`exp` claim) is checked
- [ ] JWT audience (`aud` claim) is validated
- [ ] JWT issuer (`iss` claim) is validated
- [ ] Tokens are invalidated on logout (if stateful sessions)

```bash
grep -rn "decode\|verify\|Claims" src/ --include="*.rs"
```

---

## A02 — Cryptographic Failures

### Password Hashing
- [ ] Passwords are hashed with `argon2`, `bcrypt`, or `scrypt` (NOT `sha256`, `md5`, `sha1`)
- [ ] Password hashing uses a unique salt per password
- [ ] Hash parameters (memory, iterations) are appropriate for the threat model

```bash
grep -rn "argon2\|bcrypt\|scrypt\|sha256\|md5\|sha1" Cargo.toml src/ --include="*.rs"
```

### TLS/Transport Security
- [ ] TLS is configured with `rustls` or `native-tls`
- [ ] TLS minimum version is 1.2 (prefer 1.3)
- [ ] No `danger_accept_invalid_certs` or equivalent in production code
- [ ] HTTP-only endpoints are not used for sensitive data

```bash
grep -rn "danger_accept_invalid\|accept_invalid_certs\|verify_none" src/ --include="*.rs"
```

### Cryptographic Crates
- [ ] `ring` or `aws-lc-rs` used for general cryptography (not `openssl` bindings unless required)
- [ ] No `md5` crate used for security purposes
- [ ] No `sha1` crate used for security purposes (SHA-1 is broken for collision resistance)
- [ ] Random number generation uses `ring::rand::SystemRandom` or `rand::rngs::OsRng`

```bash
grep -rn "^md5\|^sha1\|^sha-1" Cargo.toml
```

### Secrets Management
- [ ] No hardcoded API keys, passwords, or tokens in source code
- [ ] Secrets loaded from environment variables or a secrets manager
- [ ] `.env` files are in `.gitignore`
- [ ] No secrets in `Cargo.toml` or `config.toml`

```bash
grep -rn "api_key\|api_secret\|password\|token\|secret" src/ --include="*.rs" | grep -v "env::var\|config\.\|test"
```

---

## A03 — Injection

### SQL Injection
- [ ] All SQL queries use parameterized queries (SQLx `query!` macro or `query()` with bind parameters)
- [ ] No `format!()` used to construct SQL strings
- [ ] No string concatenation in SQL queries
- [ ] Diesel ORM queries use typed query builder (not raw SQL)

```bash
grep -rn "format!" src/ --include="*.rs" | grep -i "sql\|select\|insert\|update\|delete\|where"
grep -rn "query_as\|query(" src/ --include="*.rs" | grep "format!"
```

### Command Injection
- [ ] `std::process::Command` arguments are not constructed from user input without sanitization
- [ ] Shell execution (`Command::new("sh").arg("-c")`) with user input is absent
- [ ] File paths from user input are validated and canonicalized

```bash
grep -rn "Command::new\|process::Command" src/ --include="*.rs"
```

### Template Injection
- [ ] Template engines (Tera, Handlebars, Askama) do not render user-controlled template strings
- [ ] User input is escaped before rendering in templates

---

## A04 — Insecure Design

### Rate Limiting
- [ ] Authentication endpoints have rate limiting
- [ ] API endpoints have rate limiting (Tower middleware: `tower-governor` or similar)
- [ ] Rate limits are enforced per-IP or per-user, not globally

### Input Validation
- [ ] All user input is validated at the API boundary
- [ ] Validation errors return 422 Unprocessable Entity with details
- [ ] File upload size limits are enforced
- [ ] Request body size limits are configured

### Audit Logging
- [ ] Authentication events (login, logout, failed login) are logged
- [ ] Authorization failures are logged
- [ ] Sensitive data access is logged
- [ ] Logs include: timestamp, user ID, action, resource, outcome

---

## A05 — Security Misconfiguration

### CORS
- [ ] CORS is configured explicitly (not `allow_any_origin()` in production)
- [ ] Allowed origins are a specific allowlist, not a wildcard
- [ ] CORS credentials mode is not enabled with wildcard origins

```bash
grep -rn "allow_any_origin\|CorsLayer\|cors" src/ --include="*.rs"
```

### Security Headers
- [ ] `X-Content-Type-Options: nosniff` is set
- [ ] `X-Frame-Options: DENY` is set (or `Content-Security-Policy: frame-ancestors 'none'`)
- [ ] `Strict-Transport-Security` is set for HTTPS deployments
- [ ] `Content-Security-Policy` is configured

### Debug/Admin Endpoints
- [ ] Debug endpoints (`/debug`, `/metrics`, `/admin`) require authentication
- [ ] Stack traces are not returned to clients in production
- [ ] Error messages do not leak internal implementation details

```bash
grep -rn "debug\|/metrics\|/admin\|/health" src/ --include="*.rs"
```

---

## A06 — Vulnerable Components

### cargo audit
- [ ] `cargo audit` returns clean (no known CVEs)
- [ ] Any suppressed advisories are documented with justification in `audit.toml`

```bash
cargo audit
cargo audit --ignore RUSTSEC-XXXX-XXXX  # Only with documented justification
```

### cargo deny
- [ ] `deny.toml` is configured with `[advisories]`, `[licenses]`, `[bans]`
- [ ] `cargo deny check` passes in CI
- [ ] Duplicate dependencies are minimized

```bash
cargo deny check
cargo tree -d  # Show duplicate dependencies
```

### Dependency Freshness
- [ ] `cargo outdated` shows no critical security-relevant outdated packages
- [ ] `Cargo.lock` is committed (for application crates)

---

## A07 — Authentication Failures

### Session Management
- [ ] Session tokens are generated with cryptographically secure randomness
- [ ] Session tokens have appropriate expiration
- [ ] Sessions are invalidated on logout
- [ ] Session fixation is prevented (new token on privilege escalation)

### Brute Force Protection
- [ ] Login endpoints have rate limiting
- [ ] Account lockout after N failed attempts (or CAPTCHA)
- [ ] Timing-safe comparison used for credential verification

```bash
grep -rn "constant_time_eq\|timing_safe\|subtle::" src/ --include="*.rs"
```

---

## A08 — Software and Data Integrity

### Build Integrity
- [ ] `Cargo.lock` is committed for application crates
- [ ] `cargo verify-project` passes
- [ ] CI pipeline does not allow `--locked` to be bypassed
- [ ] Dependencies are pinned to specific versions in `Cargo.toml`

### Artifact Integrity
- [ ] Release binaries are signed
- [ ] Docker images are built from a pinned base image
- [ ] CI/CD pipeline has branch protection and required reviews

---

## A09 — Logging and Monitoring Failures

### What NOT to Log
- [ ] No passwords or password hashes in logs
- [ ] No API keys, tokens, or secrets in logs
- [ ] No PII (email, SSN, credit card) in logs without explicit requirement
- [ ] No full request bodies in logs (may contain sensitive data)

```bash
grep -rn "tracing::\|log::\|info!\|debug!\|warn!\|error!" src/ --include="*.rs" | grep -i "password\|token\|secret\|key"
```

### What to Log
- [ ] Authentication events (success and failure)
- [ ] Authorization failures
- [ ] Input validation failures (for security monitoring)
- [ ] Unexpected errors (with correlation IDs, not stack traces)

---

## A10 — `unsafe` Block Audit

### SAFETY Comment Presence
- [ ] Every `unsafe` block has a `// SAFETY:` comment
- [ ] SAFETY comments explain the invariant, not just restate the code

```bash
# Find unsafe blocks — manually verify each has a SAFETY comment above it
grep -n "unsafe {" src/**/*.rs
grep -n "unsafe fn" src/**/*.rs
grep -n "unsafe impl" src/**/*.rs
```

### unsafe Categories and Required Invariants

| Category | Check |
|----------|-------|
| Raw pointer dereference | Pointer is non-null, aligned, valid, and not aliased mutably |
| `transmute` | Same size, same alignment, valid bit pattern for target type |
| FFI call | C function preconditions met; no UB in the ABI boundary |
| `static mut` | Access is synchronized (Mutex/atomic) or provably single-threaded |
| Inline assembly | Register constraints correct; no clobbered callee-saved registers |
| `extern "C"` fn | Rust function called from C meets C ABI requirements |

### unsafe Minimization
- [ ] `unsafe` blocks are as small as possible
- [ ] Safe abstractions wrap `unsafe` internals
- [ ] `unsafe impl Send`/`Sync` is justified by actual thread-safety properties

---

## Final Security Verification

```bash
cargo audit                          # No CVEs
cargo deny check                     # Policy compliance
cargo clippy -- -D warnings          # No Clippy warnings
grep -rn "unsafe" src/ | grep -v "// SAFETY:"  # No unsafe without SAFETY
grep -rn "format!" src/ | grep -i "sql"  # No SQL injection candidates
grep -rn "unwrap()" src/ | grep -v "#\[cfg(test)\]"  # No unwrap in production
```
