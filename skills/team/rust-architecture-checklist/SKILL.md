---
name: rust-architecture-checklist
audience: team
description: >
  Grades an existing Rust codebase. Detects Rust edition, async runtime, and workspace
  structure, then checks ownership discipline, trait coherence, error-handling conventions,
  unsafe-block justification, and crate-boundary hygiene with file:line evidence. Use to review
  or grade a Rust codebase. Not for Socratic critique (architecture-review), security audits
  (rust-security-review), or new test-first code (tdd).
---

# Rust Architecture Checklist

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> — Atul Gawande

## Core Architectural Values

Shared across the `dotnet` / `python` / `php` / `rust` architecture checklists — same values, language-specific checks.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Detect before judge** | Determine version/framework/structure before applying any item; context decides what is idiomatic. |
| 2 | **Evidence over opinion** | Every finding cites `file:line` and the offending pattern. "Overuses clone" is not a finding; "`handlers/order.rs:47` clones a `Vec<OrderItem>` that could be borrowed" is. |
| 3 | **Feature cohesion** | Organized by business capability, not technical layer. Cross-feature coupling is a violation. |
| 4 | **Dependencies point inward** | Domain logic does not depend on I/O or framework crates. Boundaries are explicit (`pub(crate)` by default). |
| 5 | **Explicit error handling** | Failures handled at the right layer; no silent swallowing; errors carry diagnostic context. |
| 6 | **Config & secrets hygiene** | No hardcoded secrets; configuration injected, not reached for globally; secrets from env / secret-manager. |
| 7 | **Version awareness** | Recommendations are gated to the detected edition; never suggest an idiom that does not exist there. |
| 8 | **Tests gate change** | Untested code is a finding; high-risk modules without tests are prioritized. |
| 9 | **Graded, actionable output** | A letter grade (A–F) from counted findings, plus prioritized, edition-correct recommendations. |

## Workflow

Shared skeleton: `DETECT → SCAN → REPORT → RECOMMEND`.

```
DETECT     Rust edition (Cargo.toml `edition`), async runtime (Tokio/async-std/none), and structure
           (workspace vs single crate). Record findings; edition changes what is idiomatic.

SCAN       Run the Rust Checklist below section by section. Gather evidence with tooling:
             cargo clippy -- -D warnings   # baseline — must pass before the checklist
             cargo audit                   # CVEs in the dependency tree
             grep -rn "unsafe" src/        # enumerate unsafe blocks for the audit
           Every violation becomes a finding with file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Edition-gate every recommendation.
```

## Rust Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Ownership discipline** — no `.clone()`/`.to_owned()` where a borrow suffices; `Rc`/`Arc` only for genuine shared ownership | High |
| 2 | **Trait coherence** — trait impls have clear semantic purpose; no "marker-trait soup" to satisfy generic bounds | Medium |
| 3 | **Error handling** — `thiserror` for library errors, `anyhow` for application; no `.unwrap()`/`.expect()` outside `#[cfg(test)]`; consistent `?` | High |
| 4 | **`unsafe` justification** — every `unsafe` block carries a correct `// SAFETY:` comment; blocks without one are automatic High findings | Critical |
| 5 | **Crate boundary hygiene** — `pub(crate)` is the default; `pub` is a deliberate API decision; internal types do not leak | High |
| 6 | **Async runtime consistency** — exactly one runtime per binary; no blocking calls (`std::thread::sleep`, sync I/O) inside `async fn` | High |
| 7 | **Dependency discipline** — `cargo audit` clean; `cargo deny` for licenses/duplicates; minimal version constraints | Medium |
| 8 | **Test organization** — unit tests in `#[cfg(test)]`, integration tests in `tests/`; behavioral, not structure-coupled | High |

Clippy config: [clippy configuration](references/clippy-configuration.md). Full section-by-section list (with the `unsafe` audit table): [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: rust
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
detected: [edition | runtime | workspace/single | tests:yes/no]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</arch-checklist-state>
```

## Output Template

Shared across all four architecture checklists.

```markdown
## Architecture Checklist: [crate] (Rust)
**Edition**: [2021] | **Runtime**: [Tokio/async-std/none] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Ownership / Traits / Errors / unsafe / Boundaries / Async / Tests | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (unjustified `unsafe`, runtime conflict, library `.unwrap()` everywhere).

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [edition-gated fix] |

**`unsafe` audit**: | location | SAFETY comment | quality | risk |
**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Clippy must pass first.** `cargo clippy -- -D warnings` is the baseline; report failures before the architectural checklist.
- **Evidence or it is not a finding.** Cite `file:line`; show the grep/clippy output. Never grade on vibes.
- **Edition-gate recommendations.** Do not flag 2015-era patterns in a 2015 crate, or suggest 2021 idioms for an older edition.
- **Architecture, not security.** Memory-safety-as-vulnerability and crypto findings belong to `rust-security-review` — note them and route there.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`rust-security-review`** — Companion for the security dimension (`unsafe` audit for memory-safety vulns, `cargo-audit`).
- **`rust-feature-slice`** — Correct-pattern reference when the checklist flags structural violations.
- **`tdd`** — Methodology for adding tests the checklist flags as missing, and for driving any refactor.
- **`dotnet` / `python` / `php`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
