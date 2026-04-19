---
name: rust-architecture-checklist
description: >
  Checklist executor for Rust architecture reviews. Detects Rust edition, async runtime,
  and workspace structure, then runs a systematic checklist covering ownership discipline,
  trait design, error handling conventions, unsafe block justification, and crate boundary
  hygiene. Use when asked to review a Rust project, audit Rust code quality, check for
  anti-patterns, evaluate Rust architecture, run Clippy checks, or grade a Rust codebase.
  Triggers on phrases like "review rust project", "rust architecture checklist",
  "audit rust code", "check rust patterns", "evaluate rust codebase", "rust code review",
  "clippy review", "rust ownership review".
  Do NOT use when a security review is the goal — use rust-security-review;
  this checklist covers correctness and structure, not security implications.
---

# Rust Architecture Checklist

> "Rust's ownership system is not a constraint — it is a design tool. Code that fights the borrow checker is code that has not yet found its correct shape."
> -- Adapted from the Rust community

> "The compiler enforces memory safety. The architect enforces everything else."
> -- Rust Architecture Principle

## Core Philosophy

Rust's compiler enforces memory safety at compile time, eliminating entire vulnerability classes that plague C, C++, and even garbage-collected languages. This is a profound strength — but it creates a false sense of security. The compiler cannot enforce API design, trait coherence, error handling discipline, `unsafe` block correctness, or crate boundary hygiene. Those are architectural concerns, and they are what this checklist addresses.

This skill is a **checklist executor**, not a Socratic coach. It detects the project's context (Rust edition, async runtime, workspace structure), runs a systematic checklist, produces graded findings with file and line evidence, and recommends concrete improvements. The goal is a codebase that is not just memory-safe but also maintainable, idiomatic, and operationally sound.

**Non-Negotiable Constraints:**

1. **Detect before judge** — Identify Rust edition (2015/2018/2021), async runtime (Tokio/async-std/none), and workspace vs. single-crate structure before running any checklist items. Context changes what is idiomatic.
2. **Clippy must pass** — `cargo clippy -- -D warnings` is the baseline. A project that fails Clippy has not met the minimum bar. Report Clippy failures before running the architectural checklist.
3. **Evidence-based findings** — Every finding must cite a specific file and line number. "The codebase overuses `clone()`" is not a finding. "`src/handlers/order.rs:47` calls `.clone()` on a `Vec<OrderItem>` that could be borrowed" is a finding.
4. **`unsafe` blocks require justification** — Every `unsafe` block must have a `// SAFETY:` comment explaining the invariant that makes the code safe. Blocks without this comment are automatic High findings.
5. **Edition-aware idioms** — Rust 2021 idioms differ from Rust 2015. Do not flag 2015-era patterns as violations in a 2015-edition crate without noting the edition context.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Ownership Discipline** | Unnecessary `clone()` calls are a code smell indicating the author fought the borrow checker instead of working with it. `Rc`/`Arc` should appear only when shared ownership is genuinely required — not as a workaround for lifetime complexity. | Scan for `.clone()` calls on non-trivial types; scan for `Rc`/`Arc` usage and verify each is justified by shared ownership semantics. |
| 2 | **Trait Coherence** | Traits define behavior contracts. "Marker trait soup" — implementing many traits on a type to satisfy generic bounds without clear semantic meaning — creates coupling and confusion. Trait implementations should be intentional and documented. | Check that trait implementations have clear semantic purpose; flag blanket implementations that exist only to satisfy compiler requirements without adding meaning. |
| 3 | **Error Handling Discipline** | `.unwrap()` and `.expect()` in library code are bugs waiting to happen. `thiserror` is the idiomatic choice for library error types; `anyhow` is appropriate for application-level error propagation. The `?` operator should be used consistently. | Scan for `.unwrap()` and `.expect()` outside of `#[cfg(test)]` blocks; verify error types use `thiserror` (library) or `anyhow` (application); check `?` operator usage. |
| 4 | **Crate Boundary Hygiene** | The public API surface of a crate should be the minimum necessary. `pub(crate)` is the correct default for internal items; `pub` is a deliberate API decision. Leaking internal types through the public API creates coupling that is hard to break. | Audit `pub` declarations; verify that types exposed in the public API are intentional; check that `pub(crate)` is used for internal items. |
| 5 | **Async Runtime Consistency** | Mixing Tokio and async-std in the same binary causes runtime conflicts. Every async binary should use exactly one runtime. Blocking calls inside async contexts (`std::thread::sleep`, synchronous I/O) starve the executor. | Verify one runtime per binary; scan for blocking calls inside `async fn`; check that `tokio::spawn` and `async_std::task::spawn` are not mixed. |
| 6 | **`unsafe` Justification** | Every `unsafe` block is a promise to the compiler: "I have verified the invariants that make this safe." Without a `// SAFETY:` comment, that promise is unverifiable. `unsafe` without justification is not just a style issue — it is a correctness issue. | Every `unsafe` block without a `// SAFETY:` comment is a High finding. Review `// SAFETY:` comments for correctness, not just presence. |
| 7 | **Dependency Minimization** | Rust's compile times are sensitive to dependency count. More importantly, every dependency is a supply chain risk. `Cargo.toml` dependencies should be audited: is each one necessary? Is there a lighter alternative? Is `cargo-audit` clean? | Run `cargo audit`; check for duplicate dependencies with `cargo tree`; flag dependencies that could be replaced with `std` functionality. |
| 8 | **Type-State Pattern** | Rust's type system can encode state machine invariants at compile time, making illegal state transitions impossible to express. When a domain has clear states (e.g., `Unvalidated`, `Validated`, `Submitted`), the type-state pattern eliminates entire classes of runtime errors. | Identify state machines in the domain; check whether invalid state transitions are prevented at compile time or only at runtime. |
| 9 | **Lifetime Clarity** | Anonymous lifetimes (`'_`) are appropriate when the lifetime is obvious from context. Named lifetimes are required when the relationship between lifetimes needs to be explicit. Overly complex lifetime annotations are a signal that the data structure needs redesign. | Flag functions with more than 2 named lifetime parameters as candidates for redesign; check that named lifetimes are used when anonymous lifetimes would obscure intent. |
| 10 | **Test Organization** | Unit tests belong in `#[cfg(test)]` modules in the same file as the code under test. Integration tests belong in `tests/`. Doc tests belong in `///` comments on public API items. Mixing these creates confusion about what is being tested and at what boundary. | Verify test organization follows Rust conventions; check that integration tests in `tests/` test the public API only; verify doc tests compile and pass. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground findings in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Rust ownership borrowing clone Arc Rc design")` | During ownership discipline checks — ground clone/Arc/Rc findings |
| `search_knowledge("Rust trait design coherence orphan rule")` | During trait coherence checks — verify trait design principles |
| `search_knowledge("Rust error handling Result thiserror anyhow")` | During error handling checks — verify idiomatic error patterns |
| `search_knowledge("Rust async Tokio runtime executor blocking")` | During async pattern checks — verify runtime consistency rules |
| `search_knowledge("Rust unsafe block safety invariant comment")` | During unsafe audit — verify SAFETY comment requirements |
| `search_knowledge("Rust crate public API visibility pub crate")` | During crate boundary checks — verify visibility conventions |
| `search_knowledge("Rust type state pattern compile time safety")` | During type-state checks — verify pattern applicability |

## Workflow

```
DETECT (before any checklist items)
    [ ] Identify Rust edition: grep `edition` in Cargo.toml (2015/2018/2021)
    [ ] Identify async runtime: grep for `tokio`, `async-std`, `smol` in Cargo.toml
    [ ] Identify workspace vs. single crate: check for `[workspace]` in root Cargo.toml
    [ ] Count unsafe blocks: grep -rn "unsafe" src/
    [ ] Run baseline: cargo clippy -- -D warnings (report failures before proceeding)
    [ ] Run: cargo audit (report CVEs before proceeding)

        |
        v

SCAN (systematic checklist execution)
    For each checklist category (Ownership, Traits, Errors, Async, Unsafe, Crate Boundaries,
    Dependencies, Type-State, Lifetimes, Tests):
        [ ] Run category-specific checks
        [ ] Collect findings with file:line evidence
        [ ] Assign severity (Critical/High/Medium/Low)

        |
        v

REPORT (graded findings)
    [ ] Produce summary table (findings by category and severity)
    [ ] List Critical findings first with full evidence
    [ ] List High findings
    [ ] List Medium and Low findings
    [ ] Produce unsafe audit table

        |
        v

RECOMMEND
    [ ] Top 3 highest-impact improvements
    [ ] Clippy configuration recommendation
    [ ] CI integration checklist
```

**Exit criteria:** All checklist categories scanned; graded report produced; unsafe audit table complete.

## State Block

```
<rust-arch-checklist-state>
phase: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
edition: 2015 | 2018 | 2021 | unknown
async_runtime: tokio | async-std | smol | none | mixed
workspace: true | false
unsafe_block_count: [N]
clippy_status: pass | fail | not-run
categories_scanned: [comma-separated list]
findings_critical: [N]
findings_high: [N]
findings_medium: [N]
findings_low: [N]
last_action: [what was just done]
next_action: [what should happen next]
</rust-arch-checklist-state>
```

## Output Templates

### Detection Report

```markdown
## Rust Architecture Checklist — Detection Phase

**Edition**: [2015 | 2018 | 2021]
**Async Runtime**: [tokio | async-std | none | mixed]
**Structure**: [workspace with N crates | single crate]
**Unsafe Blocks**: [N] (locations: [list of files])
**Clippy Status**: [PASS | FAIL — N warnings/errors]
**cargo audit Status**: [CLEAN | N CVEs found]

Proceeding to systematic checklist scan.
```

### Graded Findings Report

```markdown
## Rust Architecture Review — Findings

**Project**: [name]
**Review Date**: [date]
**Edition**: [edition] | **Runtime**: [runtime]

### Summary

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Ownership & Borrowing | [N] | [N] | [N] | [N] |
| Trait Design | [N] | [N] | [N] | [N] |
| Error Handling | [N] | [N] | [N] | [N] |
| Async Patterns | [N] | [N] | [N] | [N] |
| `unsafe` Audit | [N] | [N] | [N] | [N] |
| Crate Boundaries | [N] | [N] | [N] | [N] |
| Dependencies | [N] | [N] | [N] | [N] |
| Type-State | [N] | [N] | [N] | [N] |
| Lifetimes | [N] | [N] | [N] | [N] |
| Test Organization | [N] | [N] | [N] | [N] |

### Critical Findings

#### [R-001] [Title]
**Category**: [category]
**Severity**: Critical
**Location**: `[file]:[line]`
**Description**: [what the issue is]
**Evidence**: [code snippet or grep output]
**Impact**: [what goes wrong if not addressed]
**Recommendation**: [specific fix]

### `unsafe` Audit Table

| Location | Has SAFETY Comment | Comment Quality | Risk Level |
|----------|--------------------|-----------------|------------|
| `src/ffi.rs:23` | Yes | Adequate | Low |
| `src/buffer.rs:87` | No | — | **High** |
```

### Recommendations

```markdown
## Top Recommendations

1. **[Highest impact item]** — [one sentence description] — estimated effort: [S/M/L]
2. **[Second item]** — [one sentence description] — estimated effort: [S/M/L]
3. **[Third item]** — [one sentence description] — estimated effort: [S/M/L]

## CI Integration Checklist

- [ ] `cargo clippy -- -D warnings` in CI (fail on any warning)
- [ ] `cargo test` in CI
- [ ] `cargo audit` in CI (fail on high/critical CVEs)
- [ ] `cargo deny check` in CI (license and duplicate dependency enforcement)
- [ ] `cargo fmt --check` in CI
```

## AI Discipline Rules

### CRITICAL: Evidence Before Findings

**WRONG:**
```
The codebase overuses clone() and has poor error handling.
```

**RIGHT:**
```
Finding R-003 (Medium): Unnecessary clone() at src/handlers/order.rs:47
The Vec<OrderItem> is cloned to pass to process_order(), but process_order()
only reads the items. Changing the signature to accept &[OrderItem] eliminates
the allocation.

Evidence: grep -n "\.clone()" src/handlers/order.rs
47:    let items = order.items.clone();
```

### CRITICAL: Edition Context Before Judgment

**WRONG:**
```
This code uses the old-style extern crate syntax — this is a violation.
```

**RIGHT:**
```
This crate uses Rust 2015 edition (Cargo.toml: edition = "2015").
The extern crate syntax is required in 2015 edition and is not a violation.
If upgrading to 2021 edition is feasible, `cargo fix --edition` can automate
the migration. See rust-migration-analyzer for edition upgrade guidance.
```

### CRITICAL: unsafe Without SAFETY Is Always High

**WRONG:**
```
This unsafe block looks fine, so I'll mark it as Low.
```

**RIGHT:**
```
Finding R-007 (High): unsafe block without SAFETY comment at src/ffi.rs:112
Every unsafe block requires a // SAFETY: comment explaining the invariant
that makes the code correct. The absence of this comment means the safety
guarantee is unverifiable, regardless of whether the code appears correct.
```

### REQUIRED: Clippy Before Checklist

**WRONG:** Running the architectural checklist on a project that fails `cargo clippy`.

**RIGHT:** Report all Clippy failures first. State: "The following Clippy failures must be resolved before the architectural checklist is meaningful." Then list them. Proceed with the checklist only after the user acknowledges.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Clone-Driven Development** | Cloning to avoid borrow checker errors hides design problems. The borrow checker is telling you the ownership model is wrong. | Redesign ownership: pass references, use lifetimes, or restructure data to make ownership clear. |
| 2 | **Arc Everywhere** | Using `Arc<Mutex<T>>` as a default for shared state adds overhead and can cause deadlocks. | Use `Arc` only when shared ownership is genuinely required. Prefer passing owned values or references. |
| 3 | **unwrap() in Library Code** | `.unwrap()` panics on `None` or `Err`. In library code, panicking is almost never correct — the caller should decide how to handle errors. | Return `Result<T, E>` or `Option<T>` from library functions. Reserve `.unwrap()` for tests and cases where the invariant is provably true (document it). |
| 4 | **Stringly-Typed Errors** | `Result<T, String>` or `Result<T, Box<dyn Error>>` in library code loses type information and makes error handling impossible for callers. | Use `thiserror` to define typed error enums for library crates. Use `anyhow` for application-level error propagation. |
| 5 | **Mixed Async Runtimes** | Mixing Tokio and async-std in the same binary causes runtime panics or undefined behavior. | Choose one runtime per binary. If a dependency requires a different runtime, use a compatibility shim or replace the dependency. |
| 6 | **Blocking in Async** | `std::thread::sleep()`, synchronous file I/O, or CPU-intensive work inside `async fn` blocks the executor thread, starving other tasks. | Use `tokio::time::sleep()`, `tokio::fs`, and `tokio::task::spawn_blocking()` for blocking work. |
| 7 | **Pub Everything** | Making all types and functions `pub` to avoid thinking about API design creates an unstable, leaky API surface. | Default to `pub(crate)`. Promote to `pub` only when the item is part of the intentional public API. |
| 8 | **Trait Soup** | Implementing 10 traits on a type to satisfy generic bounds without clear semantic purpose creates coupling and makes the type's contract unclear. | Each trait implementation should have a clear semantic reason. If a trait is implemented only to satisfy a bound, reconsider the bound. |
| 9 | **Lifetime Avoidance via Clone** | Cloning data to avoid writing lifetime annotations is a performance and design smell. | Learn to write lifetime annotations. If lifetimes are genuinely complex, consider restructuring ownership. |
| 10 | **Test-Only unwrap() Leakage** | Using `.unwrap()` freely in tests is acceptable, but test helper functions that use `.unwrap()` and are called from production code are not. | Keep test utilities in `#[cfg(test)]` modules. Never call test-only helpers from production paths. |

## Error Recovery

### Clippy Fails with Many Warnings

```
Symptoms: cargo clippy -- -D warnings produces 20+ warnings

Recovery:
1. Group warnings by category (unused imports, dead code, style, correctness)
2. Report the count by category to the user
3. Recommend: cargo clippy --fix for auto-fixable warnings
4. For correctness warnings (not just style): escalate — these may indicate real bugs
5. Do NOT proceed with the architectural checklist until the user acknowledges
   the Clippy failures and decides how to handle them
```

### cargo audit Reports CVEs

```
Symptoms: cargo audit finds one or more CVEs in dependencies

Recovery:
1. List each CVE with: crate name, CVE ID, severity, description
2. Check if the vulnerable code path is actually used: cargo tree -i <crate>
3. Check if a patched version is available: cargo update <crate>
4. If no patch exists, check for alternative crates
5. Report findings before proceeding — CVEs in dependencies are High findings
   regardless of whether the vulnerable code path is exercised
```

### unsafe Blocks Without SAFETY Comments Are Numerous

```
Symptoms: grep finds 10+ unsafe blocks without // SAFETY: comments

Recovery:
1. List all locations in the unsafe audit table
2. Mark each as High finding
3. Do NOT attempt to write SAFETY comments — that requires understanding
   the invariants, which requires the original author's knowledge
4. Recommend: the author adds SAFETY comments as a prerequisite to
   any further architectural work
5. Note: this is a blocking finding for library crates; less severe for
   application code where the unsafe is isolated
```

### Project Uses Rust 2015 Edition

```
Symptoms: Cargo.toml shows edition = "2015" or no edition field

Recovery:
1. Note the edition in the detection report
2. Apply 2015-era idioms when evaluating (extern crate, macro_rules! imports, etc.)
3. Do NOT flag 2015-era patterns as violations without noting the edition context
4. Recommend edition upgrade as a Medium finding: cargo fix --edition
5. Cross-reference rust-migration-analyzer for edition upgrade guidance
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rust-security-review` | Security-focused complement to this checklist. Run after this checklist passes. This skill covers architecture; `rust-security-review` covers OWASP and `unsafe` security implications. |
| `rust-feature-slice` | When this checklist identifies poor module organization, `rust-feature-slice` provides the structural pattern to fix it. |
| `axum-scaffolder` | When this checklist identifies HTTP layer issues (missing middleware, poor error handling in handlers), `axum-scaffolder` provides the correct patterns. |
| `sqlx-migration-manager` | When this checklist identifies database access issues (raw SQL strings, missing compile-time query verification), `sqlx-migration-manager` provides the migration safety protocol. |
| `rust-migration-analyzer` | When this checklist identifies an outdated Rust edition or deprecated crates, `rust-migration-analyzer` provides the upgrade path. |
| `supply-chain-audit` | When `cargo audit` finds CVEs, `supply-chain-audit` provides deeper dependency analysis and remediation guidance. |
| `architecture-review` | This skill is a checklist executor (what the compiler cannot enforce). `architecture-review` is a Socratic coach (architectural tradeoffs and design decisions). Use both for a complete review. |
