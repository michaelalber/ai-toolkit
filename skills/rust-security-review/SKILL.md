---
name: rust-security-review
description: >
  OWASP-based security review for Rust applications. Rust eliminates memory safety
  vulnerabilities at compile time, but logic flaws, injection attacks, cryptographic
  misuse, unsafe block vulnerabilities, and dependency CVEs remain real attack surfaces.
  Generates manager-friendly reports with risk explanations and remediation priorities.
  Use when asked to review Rust security, audit Rust code for vulnerabilities, check
  OWASP compliance in Rust, assess Rust security risks, find Rust security issues,
  scan for CVEs in Rust dependencies, or audit unsafe blocks for security implications.
  Triggers on: "rust security review", "audit rust code security", "cargo audit",
  "rust vulnerabilities", "unsafe audit rust", "OWASP rust", "rust security scan".
---

# Rust Security Review (OWASP Baseline)

> "Rust eliminates memory safety vulnerabilities. It does not eliminate logic flaws, injection attacks, or cryptographic misuse. The compiler is your ally, not your security team."
> -- Rust Security Principle

> "Every unsafe block is a promise to the compiler. Audit every promise."
> -- Adapted from the Rustonomicon

## Core Philosophy

Rust's ownership system and borrow checker eliminate entire vulnerability classes at compile time: buffer overflows, use-after-free, null pointer dereferences, data races. This is a profound security advantage. But it creates a dangerous misconception: that Rust code is inherently secure.

Rust does NOT prevent:
- **Logic flaws** — incorrect business logic, authorization bypasses, race conditions in application logic
- **Injection attacks** — SQL injection via string concatenation, command injection via `std::process::Command`
- **Cryptographic misuse** — using MD5 for password hashing, hardcoded secrets, weak random number generation
- **`unsafe` block vulnerabilities** — memory safety violations in `unsafe` code are still possible and still exploitable
- **Dependency CVEs** — vulnerable third-party crates are as dangerous as vulnerable npm packages
- **Insecure configuration** — hardcoded secrets, missing TLS, overly permissive CORS

This skill applies the OWASP Top 10 (2025) to Rust codebases, with Rust-specific adaptations. The `unsafe` block audit replaces the Telerik component security section from the .NET version — `unsafe` blocks are Rust's equivalent of "code that requires special scrutiny."

**Non-Negotiable Constraints:**

1. **`unsafe` without SAFETY comment = High finding** — no exceptions, no context required.
2. **`cargo audit` before checklist** — CVEs in dependencies are findings regardless of whether the vulnerable code path is exercised.
3. **Evidence-based findings** — every finding cites a file, line, and the specific vulnerable pattern.
4. **No false reassurance** — "Rust is memory safe" does not mean "this code is secure." State this explicitly.
5. **Manager-friendly output** — the executive summary must be readable by a non-technical stakeholder.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Broken Access Control (A01)** | Authorization logic must be enforced at every request boundary. Rust's type system can encode authorization state, but only if the developer uses it. Missing middleware, bypassed auth checks, and insecure direct object references are as possible in Rust as in any language. | Audit middleware stack for auth enforcement; check that every protected route has auth middleware; verify no direct object references expose unauthorized data. |
| 2 | **Cryptographic Failures (A02)** | Rust has excellent cryptographic libraries (`ring`, `rustls`, `argon2`) but also has dangerous ones (`md5`, `sha1` crates used for security). The choice of crate matters as much as the algorithm. | Audit `Cargo.toml` for cryptographic crates; verify password hashing uses `argon2` or `bcrypt`; verify TLS uses `rustls` or `native-tls`; check for hardcoded secrets. |
| 3 | **Injection (A03)** | SQL injection via string concatenation is possible in Rust. `std::process::Command` with user input enables command injection. `format!()` in SQL queries is a red flag. SQLx's compile-time query verification (`sqlx::query!`) prevents SQL injection when used correctly. | Grep for `format!()` in SQL contexts; check `Command::new()` calls with user input; verify SQLx parameterized queries are used. |
| 4 | **Insecure Design (A04)** | Architectural security flaws that no amount of implementation can fix. Missing rate limiting, no audit logging, insecure session management, and missing input validation are design-level issues. | Check for rate limiting middleware; verify audit logging for sensitive operations; check session token generation uses cryptographically secure randomness. |
| 5 | **Security Misconfiguration (A05)** | Hardcoded secrets in source code, debug endpoints in production, overly permissive CORS, missing security headers, and default credentials. | Grep for hardcoded secrets; check CORS configuration; verify security headers are set; check that debug/admin endpoints require authentication. |
| 6 | **Vulnerable Components (A06)** | Outdated or vulnerable crates in `Cargo.toml`. `cargo audit` is the primary tool. `cargo deny` enforces dependency policies. | Run `cargo audit`; run `cargo deny check`; check `cargo tree` for duplicate dependencies at different versions. |
| 7 | **Authentication Failures (A07)** | Weak session tokens, missing token expiration, insecure password storage, missing brute-force protection. | Verify JWT validation (signature, expiration, audience); check password hashing algorithm; verify session tokens use `rand::thread_rng()` or `ring::rand`. |
| 8 | **Software and Data Integrity (A08)** | `Cargo.lock` must be committed for applications (not libraries). Dependency integrity is verified by Cargo's hash checking. Build pipeline integrity requires signed artifacts. | Verify `Cargo.lock` is committed; check that `cargo verify-project` passes; verify CI pipeline does not allow arbitrary dependency injection. |
| 9 | **Logging and Monitoring Failures (A09)** | Sensitive data in logs, missing audit trails for security events, insufficient logging for incident response. | Grep for secrets/tokens in `tracing`/`log` calls; verify authentication events are logged; check that error messages do not leak internal details to users. |
| 10 | **`unsafe` Block Audit** | Every `unsafe` block is a potential memory safety violation. Unlike the other OWASP categories, this is Rust-specific. `unsafe` blocks without `// SAFETY:` comments are unverifiable. `unsafe` blocks with incorrect invariants are exploitable. | List every `unsafe` block; verify `// SAFETY:` comment presence and correctness; categorize by risk (FFI, raw pointer, transmute, static mut, inline asm). |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Rust security cargo-audit cargo-deny CVE")` | During dependency audit — ground CVE findings |
| `search_knowledge("Rust unsafe block memory safety invariant")` | During unsafe audit — verify safety invariant requirements |
| `search_knowledge("Rust cryptography ring rustls TLS argon2")` | During cryptographic review — verify correct crate choices |
| `search_knowledge("Rust injection SQL sqlx parameterized query")` | During injection review — verify SQLx parameterization |
| `search_knowledge("OWASP Top 10 injection broken access control")` | During OWASP category review — ground findings in OWASP |
| `search_knowledge("Rust JWT authentication axum tower middleware")` | During auth review — verify JWT validation patterns |

## Workflow

```
RECONNAISSANCE (before any checklist items)
    [ ] Identify Rust edition and async runtime (Cargo.toml)
    [ ] Count unsafe blocks: grep -rn "unsafe" src/ | wc -l
    [ ] Run: cargo audit (capture all CVEs)
    [ ] Run: cargo deny check (if cargo-deny is configured)
    [ ] Run: grep -rn "unsafe" src/ | grep -v "// SAFETY:" (find unsafe without comments)
    [ ] Identify HTTP framework (Axum, Actix, Rocket, Warp)
    [ ] Identify database access pattern (SQLx, Diesel, raw SQL)
    [ ] Identify cryptographic crates in Cargo.toml

        |
        v

SCAN (OWASP categories + unsafe audit)
    For each OWASP category:
        [ ] Run category-specific checks
        [ ] Collect findings with file:line evidence
        [ ] Assign severity (Critical/High/Medium/Low)
    
    unsafe audit:
        [ ] List all unsafe blocks with locations
        [ ] Check each for // SAFETY: comment
        [ ] Categorize by type (FFI, raw pointer, transmute, static mut, asm)
        [ ] Assess correctness of SAFETY comments

        |
        v

REPORT
    [ ] Executive summary (non-technical, 1 paragraph)
    [ ] Technical findings table (by OWASP category and severity)
    [ ] unsafe audit table
    [ ] Dependency CVE list (from cargo audit)

        |
        v

RECOMMEND
    [ ] Prioritized remediation list (Critical first)
    [ ] cargo-deny configuration recommendation
    [ ] Security CI pipeline checklist
```

## State Block

```
<rust-security-state>
phase: RECONNAISSANCE | SCAN | REPORT | RECOMMEND | COMPLETE
edition: [2015 | 2018 | 2021 | unknown]
async_runtime: [tokio | async-std | none | mixed]
http_framework: [axum | actix | rocket | warp | none | unknown]
db_access: [sqlx | diesel | raw | none | unknown]
unsafe_block_count: [N]
unsafe_without_safety_comment: [N]
cargo_audit_status: [clean | N CVEs | not-run]
categories_scanned: [comma-separated OWASP categories]
findings_critical: [N]
findings_high: [N]
findings_medium: [N]
findings_low: [N]
last_action: [description]
next_action: [description]
</rust-security-state>
```

## Output Templates

### Executive Summary

```markdown
## Rust Security Review — Executive Summary

**Project**: [name]
**Review Date**: [date]
**Overall Risk Level**: [Critical | High | Medium | Low]

Rust's memory safety guarantees eliminate buffer overflows, use-after-free vulnerabilities,
and data races at compile time. This review focuses on the security concerns Rust does not
prevent: [list 2-3 top concerns found].

**Key Findings:**
- [N] Critical findings requiring immediate attention
- [N] High findings to address before production
- [N] unsafe blocks audited; [N] require attention

**Top Priority Actions:**
1. [Most critical action]
2. [Second action]
3. [Third action]
```

### Technical Findings Report

```markdown
## Technical Findings

### Summary

| OWASP Category | Critical | High | Medium | Low |
|----------------|----------|------|--------|-----|
| A01 Broken Access Control | [N] | [N] | [N] | [N] |
| A02 Cryptographic Failures | [N] | [N] | [N] | [N] |
| A03 Injection | [N] | [N] | [N] | [N] |
| A04 Insecure Design | [N] | [N] | [N] | [N] |
| A05 Security Misconfiguration | [N] | [N] | [N] | [N] |
| A06 Vulnerable Components | [N] | [N] | [N] | [N] |
| A07 Authentication Failures | [N] | [N] | [N] | [N] |
| A08 Software Integrity | [N] | [N] | [N] | [N] |
| A09 Logging Failures | [N] | [N] | [N] | [N] |
| unsafe Audit | [N] | [N] | [N] | [N] |

### Critical Findings

#### [RS-001] [Title]
**OWASP**: [category]
**Severity**: Critical
**Location**: `[file]:[line]`
**Description**: [what the vulnerability is]
**Evidence**: [code snippet or command output]
**Impact**: [what an attacker can do]
**Remediation**: [specific fix with code example if applicable]
```

### `unsafe` Audit Table

```markdown
## `unsafe` Block Audit

| # | Location | Type | Has SAFETY Comment | Comment Quality | Risk |
|---|----------|------|--------------------|-----------------|------|
| 1 | `src/ffi.rs:23` | FFI call | Yes | Adequate | Low |
| 2 | `src/buffer.rs:87` | Raw pointer | No | — | **High** |
| 3 | `src/codec.rs:134` | transmute | Yes | Insufficient | **Medium** |
```

## AI Discipline Rules

### CRITICAL: Never Say "Rust Is Safe" Without Qualification

**WRONG:**
```
Rust's memory safety means this code is not vulnerable to buffer overflows or
use-after-free. The codebase is secure.
```

**RIGHT:**
```
Rust's memory safety eliminates buffer overflows and use-after-free in safe code.
However, this review found [N] findings in other categories: [list]. The unsafe
blocks at [locations] require manual verification of their safety invariants.
```

### CRITICAL: unsafe Without SAFETY Comment Is Always High

**WRONG:**
```
The unsafe block at src/ffi.rs:87 looks correct, so I'll mark it Low.
```

**RIGHT:**
```
RS-007 (High): unsafe block without // SAFETY: comment at src/ffi.rs:87
The absence of a SAFETY comment means the invariant cannot be verified by
code review. This is a High finding regardless of apparent correctness.
Add: // SAFETY: [explain the invariant that makes this safe]
```

### CRITICAL: cargo audit CVEs Are Findings

**WRONG:**
```
cargo audit found a CVE in the `time` crate, but we don't use the vulnerable
function, so I'll skip it.
```

**RIGHT:**
```
RS-012 (High): CVE-2020-26235 in `time` crate (CVSS 7.5)
cargo audit reports a vulnerability in `time` v0.1.44. Even if the vulnerable
code path is not directly called, the crate version should be updated.
Run: cargo update time
If update is blocked by a dependency, check: cargo tree -i time
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **"Rust Is Safe" Complacency** | Memory safety ≠ application security. Logic flaws, injection, and crypto misuse are still possible. | Apply OWASP Top 10 to every Rust project regardless of memory safety guarantees. |
| 2 | **format!() in SQL** | `format!("SELECT * FROM users WHERE id = {}", user_id)` is SQL injection. | Use SQLx parameterized queries: `sqlx::query!("SELECT * FROM users WHERE id = $1", user_id)`. |
| 3 | **md5/sha1 for Security** | The `md5` and `sha1` crates are not suitable for password hashing or HMAC in security contexts. | Use `argon2` for password hashing; `ring` for HMAC and general cryptography. |
| 4 | **Hardcoded Secrets** | `const API_KEY: &str = "sk-..."` in source code is a credential leak. | Use `std::env::var("API_KEY")` and document required environment variables. |
| 5 | **Missing Auth Middleware** | Forgetting to add auth middleware to a route group leaves endpoints unprotected. | Apply auth middleware at the router level, not per-handler. Audit every route group. |
| 6 | **rand::random() for Tokens** | `rand::random::<u64>()` is not cryptographically secure for session tokens. | Use `ring::rand::SystemRandom` or `rand::rngs::OsRng` for security-sensitive randomness. |
| 7 | **Cargo.lock Not Committed** | Not committing `Cargo.lock` for applications means builds are not reproducible and dependency versions can change silently. | Commit `Cargo.lock` for application crates. Libraries should not commit it. |
| 8 | **Secrets in Logs** | `tracing::info!("Auth token: {}", token)` leaks credentials to log aggregators. | Never log secrets, tokens, passwords, or PII. Log event types and IDs only. |
| 9 | **unsafe transmute for Type Punning** | `std::mem::transmute` between types with different layouts is undefined behavior. | Use safe alternatives: `bytemuck::cast` for POD types, or redesign to avoid type punning. |
| 10 | **Missing cargo-deny** | `cargo audit` checks CVEs but not license compliance or duplicate dependencies. | Add `cargo deny` with a `deny.toml` configuration to enforce dependency policies in CI. |

## Error Recovery

### cargo audit Reports Critical CVEs

```
Symptoms: cargo audit finds CVSS 9.0+ vulnerabilities

Recovery:
1. List the CVE with: crate name, CVE ID, CVSS score, description, affected versions
2. Check if a patched version exists: cargo update <crate>
3. Check if the vulnerable code path is used: cargo tree -i <crate>
4. If no patch exists: check for alternative crates or apply a Cargo.toml patch
5. Mark as Critical finding — do not downgrade based on "we don't use that function"
6. Recommend: add cargo-deny to CI to prevent future vulnerable dependency introduction
```

### Many unsafe Blocks Without SAFETY Comments

```
Symptoms: grep finds 10+ unsafe blocks without // SAFETY: comments

Recovery:
1. List all locations in the unsafe audit table
2. Mark each as High finding
3. Do NOT attempt to write SAFETY comments — requires author knowledge
4. Recommend: author adds SAFETY comments as a prerequisite to security sign-off
5. Note: this is a blocking finding for any security certification or audit
```

### HTTP Framework Not Recognized

```
Symptoms: Cannot identify the HTTP framework from Cargo.toml

Recovery:
1. Check for: axum, actix-web, rocket, warp, tide, hyper in Cargo.toml
2. If none found: check src/main.rs for framework initialization
3. If still unclear: report "HTTP framework not identified" and proceed with
   framework-agnostic checks (injection, crypto, logging, unsafe)
4. Note the limitation in the report
```

### No Database Access Detected

```
Symptoms: No sqlx, diesel, or raw SQL patterns found

Recovery:
1. Confirm: grep for "SELECT\|INSERT\|UPDATE\|DELETE" in src/
2. If no SQL found: note "No database access detected" and skip injection checks
3. If SQL found without a recognized ORM: flag as High — raw SQL requires manual
   parameterization verification
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rust-architecture-checklist` | Architectural complement. Run `rust-architecture-checklist` first for code quality; run this skill for security. The `unsafe` audit overlaps — this skill focuses on security implications; the checklist focuses on correctness. |
| `supply-chain-audit` | When `cargo audit` finds CVEs, `supply-chain-audit` provides deeper dependency analysis, license compliance, and remediation guidance. |
| `axum-scaffolder` | When this review finds missing auth middleware or insecure route configuration, `axum-scaffolder` provides the correct Tower middleware patterns. |
| `sqlx-migration-manager` | When this review finds raw SQL or missing parameterization, `sqlx-migration-manager` provides the safe migration and query patterns. |
| `dotnet-security-review` | Parallel skill for .NET codebases. Same OWASP structure; different ecosystem tools. |
