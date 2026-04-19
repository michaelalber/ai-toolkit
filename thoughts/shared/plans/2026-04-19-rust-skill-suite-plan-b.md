# Rust Skill Suite — Implementation Plan (Plan B)

> Prerequisite: Plan A (Python suite) must be implemented and verified before starting Plan B.

## Overview

Create 8 new Rust skills mirroring the .NET suite, each adapted for Rust's ecosystem
(Axum, SQLx, Cargo, Clippy, cargo-audit, etc.). Add corresponding Claude Code and OpenCode
agents for each skill. Rust's ownership model, compile-time safety guarantees, and
systems-programming focus require significant adaptation from both .NET and Python patterns.

## Current state analysis

- 61 skills expected after Plan A; 0 Rust-ecosystem skills exist
- Gold standard template: `skills/architecture-review/SKILL.md` (610 lines, 10 sections)
- Agent format confirmed: Claude uses `skills:` frontmatter array; OpenCode uses `skill()` body calls
- Every skill needs `references/` directory with ≥ 2 `.md` files
- State block XML tags must be unique across all skills (Plan A introduces 7 new tags)
- Rust has no direct analog to `dotnet-architecture-checklist` / `python-arch-review` — `rust-architecture-checklist` is a new skill with Rust-specific patterns (ownership, lifetimes, trait design)

## Desired end state

- 8 new Rust skills, each with full 10-section compliance and ≥ 2 reference files
- 8 new Claude Code agents in `claude/agents/`
- 8 new OpenCode agents in `opencode/agents/`
- Skill count in `AGENTS.md` updated from 61 → 69
- Agent count in `AGENTS.md` updated: Claude 28 → 36, OpenCode 27 → 35
- Skill suites table in `AGENTS.md` updated with new "Rust" suite row

## What we're NOT doing

- Creating a `rust-security-review-federal` skill in this plan — federal overlay requires the base `rust-security-review` to exist and be validated first; add as a follow-on plan
- Modifying any Python or .NET skills
- Fixing existing convention violations (separate task)
- Creating a Rust TDD skill — the existing `tdd-cycle` skill is language-agnostic and covers Rust; a Rust-specific TDD skill would duplicate it without adding value

## Implementation approach

Each phase creates one skill + its references + its two agent files. Phases are independent.
Phase 1 (`rust-architecture-checklist`) is the template-setter — implement it first.

Rust requires more ecosystem explanation than Python or .NET because:
1. Ownership/borrowing is a first-class architectural concern with no .NET/.Python equivalent
2. `async` in Rust requires an explicit runtime (Tokio) — this must be called out in every relevant skill
3. Error handling via `Result<T, E>` and `?` operator is idiomatic and must be enforced
4. Cargo workspaces are the multi-crate equivalent of .NET solutions

---

## Skill mapping: .NET → Rust

| .NET Skill | Rust Skill | Key ecosystem difference |
|---|---|---|
| `dotnet-architecture-checklist` | `rust-architecture-checklist` | Ownership/lifetime design, trait coherence, crate boundaries |
| `dotnet-security-review` | `rust-security-review` | `cargo-audit`, `cargo-deny`, `unsafe` block audit; memory safety is compile-time but logic flaws remain |
| `dotnet-vertical-slice` | `rust-feature-slice` | Axum routers + handler functions + service traits; no DI framework — manual wiring |
| `ef-migration-manager` | `sqlx-migration-manager` | SQLx migrations vs. EF Core; compile-time query verification |
| `legacy-migration-analyzer` | `rust-migration-analyzer` | C/C++ → Rust rewrites, or older Rust edition upgrades (2015→2018→2021) |
| `minimal-api-scaffolder` | `axum-scaffolder` | Axum + Tower middleware vs. ASP.NET Minimal API |
| `nuget-package-scaffold` | `cargo-package-scaffold` | Cargo.toml + crates.io vs. .csproj + NuGet |
| `4d-schema-migration` | *(no analog — excluded)* | 4D targets .NET/SQL Server only |

`dotnet-security-review-federal` → `rust-security-review-federal` deferred to follow-on plan.

---

## Phase 1: `rust-architecture-checklist` skill + agents

### Overview

Rust analog of `dotnet-architecture-checklist`. Reviews Rust codebases against idiomatic
patterns: ownership discipline, trait design, crate boundary hygiene, error handling
conventions, async runtime usage, and `unsafe` block justification. Uses Clippy as the
primary automated checker.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/rust-architecture-checklist/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations:
- Title: "Rust Architecture Checklist"
- Unique state tag: `<rust-arch-checklist-state>`
- Core Philosophy: Checklist executor (not Socratic coach). Detects Rust edition, async runtime, and workspace structure first, then runs checklist. Rust's compiler enforces memory safety — this checklist focuses on what the compiler cannot enforce: API design, trait coherence, error handling discipline, `unsafe` justification, and crate boundary hygiene.
- Non-Negotiable Constraints: Detect before judge (edition 2015/2018/2021, async runtime Tokio/async-std/none, workspace vs. single crate), Clippy must pass with `#![deny(clippy::all)]`, evidence-based findings (file + line), `unsafe` blocks require justification comment
- Domain Principles: Ownership Discipline (no unnecessary `clone()`, `Rc`/`Arc` only when shared ownership is genuinely needed), Trait Coherence (traits define behavior contracts; no "marker trait soup"), Error Handling (`Result<T, E>` everywhere; no `.unwrap()` in library code; `thiserror` for library errors, `anyhow` for application errors), Crate Boundary Hygiene (public API surface minimized; `pub(crate)` by default), Async Runtime Consistency (one runtime per binary; no mixing Tokio and async-std), `unsafe` Justification (every `unsafe` block has a `// SAFETY:` comment explaining the invariant), Dependency Minimization (Cargo.toml dependencies audited; no transitive bloat), Type-State Pattern (use types to encode state machine invariants at compile time), Lifetime Clarity (named lifetimes when anonymous `'_` obscures intent), Test Organization (unit tests in `#[cfg(test)]` modules; integration tests in `tests/`)
- Knowledge Base Lookups: `search_knowledge("Rust ownership borrowing clone Arc Rc design")`, `search_knowledge("Rust trait design coherence orphan rule")`, `search_knowledge("Rust error handling Result thiserror anyhow")`, `search_knowledge("Rust async Tokio runtime executor")`, `search_knowledge("Rust unsafe block safety invariant")`
- Workflow: DETECT (edition, runtime, workspace) → SCAN (Clippy + checklist) → REPORT (graded findings) → RECOMMEND
- Commands: `cargo clippy -- -D warnings`, `cargo test`, `cargo audit`, `cargo deny check`
- Output Templates: graded report (same structure as `dotnet-architecture-checklist`), `unsafe` audit table

#### 2. Create references directory with 2 files
**File**: `skills/rust-architecture-checklist/references/review-checklist.md` (new file)
**Changes**: Rust-specific review checklist. Sections: Ownership & Borrowing, Trait Design, Error Handling, Async Patterns, `unsafe` Audit, Crate Structure, Dependency Health, Test Coverage, Documentation (`///` doc comments on all public items), Performance (avoid unnecessary allocations, `Box<dyn Trait>` vs. generics).

**File**: `skills/rust-architecture-checklist/references/clippy-configuration.md` (new file)
**Changes**: Recommended Clippy lint configuration for production Rust projects. `#![deny(clippy::all)]`, `#![warn(clippy::pedantic)]`, specific lints to enable/disable with rationale. `.clippy.toml` configuration. CI integration pattern.

#### 3. Create Claude Code agent
**File**: `claude/agents/rust-arch-checklist-agent.md` (new file)
**Changes**: `name: rust-arch-checklist-agent`, trigger phrases ("review rust project", "rust architecture checklist", "audit rust code", "check rust patterns", "evaluate rust codebase", "rust code review"), `tools: Read, Bash, Glob, Grep`, `skills: [rust-architecture-checklist]`. State tag: `<rust-arch-checklist-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/rust-arch-checklist-agent.md` (new file)
**Changes**: OpenCode format. `skill()` call for `rust-architecture-checklist`.

### Success criteria

#### Automated verification
- [ ] `ls skills/rust-architecture-checklist/references/` contains ≥ 2 files
- [ ] `grep "<rust-arch-checklist-state>" skills/rust-architecture-checklist/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/rust-architecture-checklist/SKILL.md` returns ≥ 10

**Implementation note**: Complete and verify Phase 1 fully before starting Phase 2. Phase 1 establishes the Rust template pattern.

---

## Phase 2: `rust-security-review` skill + agents

### Overview

Rust analog of `dotnet-security-review`. OWASP baseline adapted for Rust. Rust's memory
safety eliminates entire vulnerability classes (buffer overflows, use-after-free, null
pointer dereference) — the checklist focuses on what Rust does NOT prevent: logic flaws,
injection attacks, cryptographic misuse, `unsafe` block vulnerabilities, and dependency CVEs.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/rust-security-review/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `dotnet-security-review`:
- Title: "Rust Security Review (OWASP Baseline)"
- Unique state tag: `<rust-security-state>`
- Core Philosophy: Rust eliminates memory safety vulnerabilities at compile time — this is a strength, not a reason to skip security review. Logic flaws, injection, cryptographic misuse, and `unsafe` blocks remain real attack surfaces. `cargo-audit` and `cargo-deny` replace NuGet audit. No Telerik equivalent — focus on `unsafe` block audit instead.
- Domain Principles: same 10 OWASP-aligned principles adapted — "unsafe Block Audit" replaces "Telerik Component Security" (every `unsafe` block is a potential memory safety violation; audit each one for invariant correctness)
- Knowledge Base Lookups: `search_knowledge("Rust security cargo-audit cargo-deny CVE")`, `search_knowledge("Rust unsafe block memory safety invariant")`, `search_knowledge("Rust cryptography ring rustls TLS")`, `search_knowledge("Rust injection SQL sqlx parameterized query")`, `search_knowledge("OWASP Top 10 injection broken access control")`
- Workflow: RECONNAISSANCE (edition, async runtime, `unsafe` block count, dependencies) → SCAN (OWASP categories + `unsafe` audit + `cargo-audit`) → REPORT → RECOMMEND
- Commands: `cargo audit`, `cargo deny check`, `grep -rn "unsafe" src/`, `cargo clippy -- -D clippy::all`
- `unsafe` audit: every `unsafe` block must have `// SAFETY:` comment; blocks without comments are automatic High findings
- Output Templates: executive summary + technical findings + `unsafe` audit table

#### 2. Create references directory with 2 files
**File**: `skills/rust-security-review/references/owasp-rust-checklist.md` (new file)
**Changes**: Rust-specific OWASP Top 10 checklist. A01 Broken Access Control (middleware auth, no role bypass), A02 Cryptographic Failures (`ring`/`rustls` for crypto; no `md5`/`sha1` crates for security), A03 Injection (SQLx parameterized queries; no string-concatenated SQL; no `format!()` in SQL), A04 Insecure Design, A05 Security Misconfiguration (no hardcoded secrets; `std::env::var()` for secrets), A06 Vulnerable Components (`cargo audit` output), A07 Auth Failures (JWT validation, session management), A08 Software Integrity (Cargo.lock committed; `cargo verify-project`), A09 Logging Failures (no secrets in `tracing`/`log` output), A10 SSRF (URL validation before outbound requests).

**File**: `skills/rust-security-review/references/unsafe-audit-guide.md` (new file)
**Changes**: Guide for auditing `unsafe` blocks. Categories: FFI calls (C interop), raw pointer dereference, `transmute`, `static mut`, inline assembly. For each: what invariants must hold, common mistakes, how to verify correctness, when to refactor to safe code.

#### 3. Create Claude Code agent
**File**: `claude/agents/rust-security-agent.md` (new file)
**Changes**: `name: rust-security-agent`, trigger phrases ("rust security review", "audit rust code security", "cargo audit", "rust vulnerabilities", "unsafe audit rust", "OWASP rust"), `tools: Read, Bash, Glob, Grep`, `skills: [rust-security-review, supply-chain-audit]`. State tag: `<rust-security-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/rust-security-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `rust-security-review`, `supply-chain-audit`.

### Success criteria

#### Automated verification
- [ ] `ls skills/rust-security-review/references/` contains ≥ 2 files
- [ ] `grep "<rust-security-state>" skills/rust-security-review/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/rust-security-review/SKILL.md` returns ≥ 10

---

## Phase 3: `rust-feature-slice` skill + agents

### Overview

Rust analog of `dotnet-vertical-slice`. Feature-based architecture using Axum routers,
handler functions, and service traits. Rust has no DI framework — dependencies are wired
manually via `Arc<dyn ServiceTrait>` in Axum state. CQRS is a naming convention enforced
by trait design, not a library.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/rust-feature-slice/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `dotnet-vertical-slice`:
- Title: "Rust Feature Slice Architecture"
- Unique state tag: `<rust-feature-slice-state>`
- Core Philosophy: Feature isolation via Rust modules (`features/orders/mod.rs`, `features/users/mod.rs`). No DI framework — use `Arc<dyn Trait>` in Axum `State<AppState>`. CQRS via trait separation: `OrderReader` trait (query methods) and `OrderWriter` trait (command methods) implemented by the same or different structs. Axum `Router` per feature, merged at app startup.
- Non-Negotiable Constraints: Feature module isolation (no `use crate::features::other_feature::` in handlers), service traits defined with `async_trait` or `impl Trait` return types, `Arc<dyn Trait>` for shared state (not `Mutex<ConcreteType>`), `Result<T, AppError>` return type on all handlers, handler functions are thin (delegate to service immediately)
- Domain Principles: Feature Isolation, Service Trait Autonomy, Minimal Trait Surface, State Injection via `Arc`, Read/Write Trait Separation, Immutable Request Types (structs with `#[derive(Deserialize)]`), Explicit Error Types (`thiserror` for domain errors), Validator Co-Location, Handler Thinness, Test Organization (`#[cfg(test)]` + `axum::test`)
- Knowledge Base Lookups: `search_knowledge("Axum router handler state Arc dependency injection")`, `search_knowledge("Rust async trait service layer tokio")`, `search_knowledge("Rust thiserror error handling Result")`, `search_knowledge("Axum testing TestClient integration test")`
- Workflow: DETECT → SCAFFOLD (module + router + service trait + impl + tests) → REGISTER (merge router into app) → VERIFY
- Scaffold template: `src/features/<name>/mod.rs`, `src/features/<name>/router.rs`, `src/features/<name>/service.rs` (trait + impl), `src/features/<name>/models.rs`, `tests/features/<name>/integration_test.rs`

#### 2. Create references directory with 2 files
**File**: `skills/rust-feature-slice/references/feature-module-template.md` (new file)
**Changes**: Complete Rust feature module scaffold template. `mod.rs` (re-exports), `router.rs` (Axum `Router` with state), `service.rs` (trait definition + `Arc<dyn Trait>` pattern), `models.rs` (`serde::Deserialize`/`Serialize` structs), error types with `thiserror`.

**File**: `skills/rust-feature-slice/references/state-injection-patterns.md` (new file)
**Changes**: Axum state injection patterns. `AppState` struct with `Arc<dyn Trait>` fields, `FromRef` for sub-state extraction, `Extension` vs. `State` tradeoffs, testing with mock implementations of service traits.

#### 3. Create Claude Code agent
**File**: `claude/agents/rust-feature-slice-agent.md` (new file)
**Changes**: `name: rust-feature-slice-agent`, trigger phrases ("scaffold rust feature", "axum feature folder", "rust vertical slice", "add rust endpoint", "rust service layer"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [rust-feature-slice, axum-scaffolder]`. State tag: `<rust-feature-slice-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/rust-feature-slice-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `rust-feature-slice`, `axum-scaffolder`.

### Success criteria

#### Automated verification
- [ ] `ls skills/rust-feature-slice/references/` contains ≥ 2 files
- [ ] `grep "<rust-feature-slice-state>" skills/rust-feature-slice/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/rust-feature-slice/SKILL.md` returns ≥ 10

---

## Phase 4: `sqlx-migration-manager` skill + agents

### Overview

Rust analog of `ef-migration-manager`. Manages the full SQLx migration lifecycle using
SQLx's built-in migration system (`sqlx migrate`). Key difference from Alembic/EF Core:
SQLx migrations are plain SQL files (no ORM-generated DDL), and SQLx verifies query
correctness at compile time via `sqlx::query!` macros. Same safety philosophy applies.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/sqlx-migration-manager/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `ef-migration-manager`:
- Title: "SQLx Migration Manager"
- Unique state tag: `<sqlx-migration-state>`
- Core Philosophy: Same 5 non-negotiable constraints. Key Rust-specific addition: SQLx compile-time query verification (`sqlx::query!`) means schema changes can break compilation — migration and code changes must be coordinated. `sqlx prepare` generates the offline query cache; this must be regenerated after every migration.
- Domain Principles: same 10 adapted — "SQL Review Mandatory" is simpler (migrations ARE SQL, no generated DDL to inspect), "Schema Validation" uses `sqlx migrate info` and `sqlx::query!` compilation, "Offline Query Cache" (`sqlx prepare` after every migration — unique to SQLx)
- Knowledge Base Lookups: `search_knowledge("SQLx migration sqlx migrate run revert")`, `search_knowledge("SQLx compile time query verification sqlx prepare")`, `search_knowledge("database migration zero downtime PostgreSQL")`, `search_knowledge("SQLx transaction migration rollback")`
- Workflow: PLAN → CREATE (new `.sql` file in `migrations/`) → REVIEW SQL (read the file directly) → TEST ROLLBACK (`sqlx migrate revert`) → APPLY (`sqlx migrate run`) → REGENERATE CACHE (`sqlx prepare`)
- Commands: `sqlx migrate add <name>`, `sqlx migrate run`, `sqlx migrate revert`, `sqlx migrate info`, `sqlx prepare`
- Output Templates: migration review checklist, rollback verification template (same structure as Alembic version)

#### 2. Create references directory with 2 files
**File**: `skills/sqlx-migration-manager/references/migration-safety-checklist.md` (new file)
**Changes**: Pre-apply checklist adapted for SQLx: SQL reviewed, revert tested, `sqlx prepare` planned post-apply, data loss risk assessed, zero-downtime evaluated, offline cache invalidation noted.

**File**: `skills/sqlx-migration-manager/references/dangerous-operations.md` (new file)
**Changes**: Same dangerous DDL catalog as `alembic-migration-manager/references/dangerous-operations.md` but with SQLx-specific notes: `sqlx::query!` compilation failures after column drops/renames, offline cache staleness, transaction wrapping for DDL (PostgreSQL supports transactional DDL; MySQL does not).

#### 3. Create Claude Code agent
**File**: `claude/agents/sqlx-migration-agent.md` (new file)
**Changes**: `name: sqlx-migration-agent`, trigger phrases ("sqlx migration", "rust database migration", "create migration rust", "sqlx migrate", "sqlx schema change"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [sqlx-migration-manager]`. State tag: `<sqlx-migration-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/sqlx-migration-agent.md` (new file)
**Changes**: OpenCode format. `skill()` call for `sqlx-migration-manager`.

### Success criteria

#### Automated verification
- [ ] `ls skills/sqlx-migration-manager/references/` contains ≥ 2 files
- [ ] `grep "<sqlx-migration-state>" skills/sqlx-migration-manager/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/sqlx-migration-manager/SKILL.md` returns ≥ 10

---

## Phase 5: `rust-migration-analyzer` skill + agents

### Overview

Rust analog of `legacy-migration-analyzer`. Two primary migration paths: (1) C/C++ → Rust
rewrites using incremental FFI-based strangler fig, and (2) Rust edition upgrades
(2015 → 2018 → 2021) and ecosystem modernization (old crates → maintained alternatives).
Does NOT perform the migration — assesses, quantifies risk, and plans.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/rust-migration-analyzer/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `legacy-migration-analyzer`:
- Title: "Rust Migration Analyzer"
- Unique state tag: `<rust-migration-state>`
- Core Philosophy: Same 5 constraints. Two migration contexts: (A) C/C++ → Rust: FFI boundary is the migration seam; rewrite module-by-module behind a C ABI; test the C side before rewriting; (B) Rust modernization: edition upgrades are mechanical (`cargo fix --edition`); crate replacement requires API compatibility analysis.
- Domain Principles: Risk Assessment First, Incremental Migration (FFI strangler fig for C/C++; feature-flag gating for crate replacements), API Compatibility Analysis (`cargo fix --edition --allow-dirty` for edition upgrades; manual API diff for crate replacements), Dependency Audit (`cargo outdated`, `cargo audit`, `cargo tree`), Business Logic Isolation (pure Rust logic migrates trivially; `unsafe` FFI code does not), Test Coverage Gate (characterization tests against C/C++ behavior before rewriting), FFI Safety (every `extern "C"` function is a safety boundary; document invariants), Async Migration (sync → async requires runtime introduction; plan Tokio integration separately), Build System Migration (Makefile/CMake → Cargo workspace), Deployment Pipeline (bare binaries → Docker + CI/CD)
- Knowledge Base Lookups: `search_knowledge("Rust FFI C interop extern unsafe bindgen")`, `search_knowledge("Rust edition migration 2015 2018 2021 cargo fix")`, `search_knowledge("cargo outdated audit dependency update")`, `search_knowledge("Rust async migration Tokio sync to async")`
- Workflow: SCAN → ASSESS (risk scoring) → PLAN (phased migration) → REPORT
- Tooling: `cargo fix --edition`, `cargo outdated`, `cargo audit`, `cargo tree`, `bindgen` (for C header analysis)
- Output Templates: risk matrix, migration phase plan, FFI boundary inventory table

#### 2. Create references directory with 2 files
**File**: `skills/rust-migration-analyzer/references/migration-risk-matrix.md` (new file)
**Changes**: Risk scoring matrix for Rust migration scenarios. Rows: Rust edition upgrade, crate replacement, C/C++ FFI rewrite, sync→async migration, build system migration, `unsafe` reduction. Columns: Effort, Risk, Blocker potential, Recommended order.

**File**: `skills/rust-migration-analyzer/references/ffi-patterns.md` (new file)
**Changes**: FFI strangler fig patterns for C/C++ → Rust migration. `extern "C"` wrapper pattern, `bindgen` usage, `cbindgen` for exposing Rust to C, safety invariant documentation, incremental replacement strategy, testing FFI boundaries.

#### 3. Create Claude Code agent
**File**: `claude/agents/rust-migration-agent.md` (new file)
**Changes**: `name: rust-migration-agent`, trigger phrases ("rust migration", "c to rust", "c++ to rust", "rust edition upgrade", "modernize rust", "rust legacy migration"), `tools: Read, Bash, Glob, Grep`, `skills: [rust-migration-analyzer]`. State tag: `<rust-migration-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/rust-migration-agent.md` (new file)
**Changes**: OpenCode format. `skill()` call for `rust-migration-analyzer`.

### Success criteria

#### Automated verification
- [ ] `ls skills/rust-migration-analyzer/references/` contains ≥ 2 files
- [ ] `grep "<rust-migration-state>" skills/rust-migration-analyzer/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/rust-migration-analyzer/SKILL.md` returns ≥ 10

---

## Phase 6: `axum-scaffolder` skill + agents

### Overview

Rust analog of `minimal-api-scaffolder`. Scaffolds Axum HTTP endpoints with OpenAPI
documentation (`utoipa`), Tower middleware, JWT authentication, rate limiting, and health
checks. Axum does not have built-in OpenAPI — `utoipa` provides derive macros for
documentation generation.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/axum-scaffolder/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `minimal-api-scaffolder`:
- Title: "Axum Scaffolder"
- Unique state tag: `<axum-scaffold-state>`
- Non-Negotiable Constraints: OpenAPI-First (`#[utoipa::path]` on every handler; `utoipa::OpenApi` derive on app), Versioning from Day One (`/api/v1/` prefix on all routers), Security by Default (Tower middleware for JWT validation; anonymous access is explicit), Typed Extractors (all request data via `axum::extract::{Json, Path, Query, State}`; no raw `Request` parsing), Typed Responses (`impl IntoResponse` with explicit status codes; no magic number status codes in handlers)
- Domain Principles: Router Organization (one `Router` per feature, merged at startup), Request/Response Types (`serde::Deserialize`/`Serialize` structs; `#[derive(ToSchema)]` for OpenAPI), Validation (`validator` crate or manual validation in handler; return `422 Unprocessable Entity` for validation failures), OpenAPI Documentation (`utoipa` macros on all handlers), Versioning Strategy (URL prefix), Authorization (Tower middleware layer; `Extension<Claims>` for auth context), Rate Limiting (`tower-governor` or `axum-governor`), Error Handling (custom `AppError` implementing `IntoResponse`; RFC 7807 Problem Details JSON), CORS (`tower-http::cors::CorsLayer`), Health Checks (`/health` route returning 200 OK)
- Knowledge Base Lookups: `search_knowledge("Axum router handler extractor State Tower middleware")`, `search_knowledge("utoipa OpenAPI derive macro Axum documentation")`, `search_knowledge("Axum JWT authentication Tower layer middleware")`, `search_knowledge("Axum error handling IntoResponse AppError")`, `search_knowledge("tower-http CORS rate limiting middleware")`
- Workflow: DETECT → CONFIGURE (Cargo.toml deps, project structure) → SCAFFOLD (router + handlers + models) → SECURE (auth middleware) → DOCUMENT (utoipa) → VERIFY
- Output Templates: scaffold checklist, router template, error type template, OpenAPI setup template

#### 2. Create references directory with 2 files
**File**: `skills/axum-scaffolder/references/router-template.md` (new file)
**Changes**: Complete Axum router scaffold template. `Router` setup with `State<AppState>`, handler function signatures with extractors, `#[utoipa::path]` decoration, `AppError` type with `IntoResponse`, Tower middleware layer stack, health check handler.

**File**: `skills/axum-scaffolder/references/middleware-patterns.md` (new file)
**Changes**: Tower middleware patterns for Axum. JWT validation layer, CORS configuration, rate limiting with `tower-governor`, request tracing with `tower-http::trace`, compression, timeout. Layer ordering (security before business logic).

#### 3. Create Claude Code agent
**File**: `claude/agents/axum-scaffold-agent.md` (new file)
**Changes**: `name: axum-scaffold-agent`, trigger phrases ("scaffold axum", "create axum endpoint", "axum router", "add axum route", "rust rest api", "axum api"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [axum-scaffolder, rust-feature-slice, rust-security-review]`. State tag: `<axum-scaffold-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/axum-scaffold-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `axum-scaffolder`, `rust-feature-slice`, `rust-security-review`.

### Success criteria

#### Automated verification
- [ ] `ls skills/axum-scaffolder/references/` contains ≥ 2 files
- [ ] `grep "<axum-scaffold-state>" skills/axum-scaffolder/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/axum-scaffolder/SKILL.md` returns ≥ 10

---

## Phase 7: `cargo-package-scaffold` skill + agents

### Overview

Rust analog of `nuget-package-scaffold`. Scaffolds production-ready crates for crates.io
with `Cargo.toml` metadata, GitHub Actions publish workflow, test harness, and documentation
(`rustdoc`). Rust's package ecosystem has strong conventions: `#![deny(missing_docs)]`,
`#![warn(clippy::all)]`, and `cargo test` as the quality gate.

### Changes required

#### 1. Create skill directory and SKILL.md
**File**: `skills/cargo-package-scaffold/SKILL.md` (new file)
**Changes**: Full 10-section skill. Key adaptations from `nuget-package-scaffold`:
- Title: "Cargo Package Scaffold"
- Unique state tag: `<cargo-package-state>`
- Non-Negotiable Constraints: No publish without tests, SemVer is law, metadata required (`name`, `version`, `description`, `license`, `authors`, `repository`, `readme`, `keywords`, `categories`), MSRV (Minimum Supported Rust Version) declared in `Cargo.toml` (`rust-version`), `#![deny(missing_docs)]` on library crates
- Domain Principles: Semantic Versioning, API Surface Minimization (`pub(crate)` by default; `pub` by design), MSRV Policy (declare and test against minimum supported Rust version), Documentation (`///` doc comments on all public items; `cargo doc --no-deps` must succeed without warnings), Deterministic Builds (Cargo.lock committed for binaries, not for libraries), Feature Flags (additive features only; no feature that removes functionality), License Compliance (SPDX in `Cargo.toml`; `license-file` for non-SPDX), Dependency Management (conservative version ranges; `cargo outdated` in CI), Backward Compatibility (deprecation via `#[deprecated]` before removal), `no_std` Consideration (evaluate whether the crate can support `no_std` for embedded use)
- Knowledge Base Lookups: `search_knowledge("Cargo.toml package metadata crates.io publish")`, `search_knowledge("semantic versioning Rust crate SemVer")`, `search_knowledge("GitHub Actions Rust publish crates.io workflow")`, `search_knowledge("rustdoc documentation cargo doc missing_docs")`, `search_knowledge("Rust MSRV minimum supported rust version")`
- Workflow: SCAFFOLD (Cargo.toml + src/lib.rs + tests/) → CONFIGURE (metadata, features, MSRV) → TEST (cargo test + clippy + doc test) → PUBLISH (cargo publish --dry-run → cargo publish)
- Output Templates: `Cargo.toml` template, GitHub Actions publish workflow, release checklist

#### 2. Create references directory with 2 files
**File**: `skills/cargo-package-scaffold/references/cargo-toml-template.md` (new file)
**Changes**: Complete `Cargo.toml` template for a library crate. All required and recommended fields: `[package]` (name, version, edition, rust-version, description, license, authors, repository, homepage, documentation, readme, keywords, categories), `[features]`, `[dependencies]`, `[dev-dependencies]`, `[lib]` (crate-type for cdylib if needed).

**File**: `skills/cargo-package-scaffold/references/ci-publish-workflow.md` (new file)
**Changes**: GitHub Actions workflow for crates.io publishing. Test matrix (stable, beta, MSRV), Clippy check, `cargo doc`, `cargo publish --dry-run` on PR, `cargo publish` on tag push with `CARGO_REGISTRY_TOKEN` secret. MSRV verification step.

#### 3. Create Claude Code agent
**File**: `claude/agents/cargo-package-agent.md` (new file)
**Changes**: `name: cargo-package-agent`, trigger phrases ("create rust crate", "scaffold cargo package", "publish rust crate", "crates.io publish", "rust library scaffold", "cargo.toml setup"), `tools: Read, Edit, Write, Bash, Glob, Grep`, `skills: [cargo-package-scaffold, supply-chain-audit]`. State tag: `<cargo-package-agent-state>`.

#### 4. Create OpenCode agent
**File**: `opencode/agents/cargo-package-agent.md` (new file)
**Changes**: OpenCode format. `skill()` calls for `cargo-package-scaffold`, `supply-chain-audit`.

### Success criteria

#### Automated verification
- [ ] `ls skills/cargo-package-scaffold/references/` contains ≥ 2 files
- [ ] `grep "<cargo-package-state>" skills/cargo-package-scaffold/SKILL.md` returns 1 match
- [ ] `grep -c "^## " skills/cargo-package-scaffold/SKILL.md` returns ≥ 10

---

## Phase 8: `AGENTS.md` and suite table updates

### Overview

Update `AGENTS.md` to reflect the new skill count (61 → 69), agent counts (Claude 28 → 36,
OpenCode 27 → 35), and add the Rust suite row to the Skill Suites table.

### Changes required

#### 1. Update skill count
**File**: `AGENTS.md`
**Changes**: Update skill count from `61+` to `69+`. Update Open Loops skill count note.

#### 2. Update agent count parity note
**File**: `AGENTS.md`
**Changes**: Update Claude agent count from 28 → 36 and OpenCode from 27 → 35 in Open Loops.

#### 3. Add Rust suite to Skill Suites table
**File**: `AGENTS.md`
**Changes**: Add new row:
```
| Rust | rust-architecture-checklist, rust-security-review, rust-feature-slice, sqlx-migration-manager, rust-migration-analyzer, axum-scaffolder, cargo-package-scaffold | Rust patterns, migrations, security, scaffolding |
```

#### 4. Update architecture-review Stack-Specific Guidance
**File**: `skills/architecture-review/SKILL.md`
**Changes**: In the "Stack-Specific Guidance" section, add a Rust bullet: "Rust architectures: Cross-reference with `rust-feature-slice` for structural patterns, `axum-scaffolder` for HTTP API architecture, and `rust-architecture-checklist` for ownership and trait design concerns."

### Success criteria

#### Automated verification
- [ ] `grep "69" AGENTS.md` finds the updated skill count
- [ ] `grep "Rust" AGENTS.md` finds the new suite row in the Skill Suites table

**Implementation note**: Phase 8 must run AFTER all skill phases (1–7) are complete.

---

## Testing strategy

Same approach as Plan A. After all phases complete, run the cross-skill uniqueness check:

```bash
grep -r "<.*-state>" skills/*/SKILL.md | grep -oP "<[^>]+-state>" | sort | uniq -d
```

Must return empty.

---

## Rollback plan

Each phase creates new files only until Phase 8.

- **Phases 1–7 rollback**: `rm -rf skills/<skill-name>/` + `rm claude/agents/<agent>.md` + `rm opencode/agents/<agent>.md`
- **Phase 8 rollback**: `git checkout AGENTS.md skills/architecture-review/SKILL.md`
- **Full rollback**: `git clean -fd skills/rust-* skills/sqlx-* skills/axum-* skills/cargo-* claude/agents/rust-* claude/agents/sqlx-* claude/agents/axum-* claude/agents/cargo-* opencode/agents/rust-* opencode/agents/sqlx-* opencode/agents/axum-* opencode/agents/cargo-*`

---

## Notes

- Plan B depends on Plan A being complete (agent counts in Phase 8 build on Plan A's final counts)
- New state tags introduced in this plan: `<rust-arch-checklist-state>`, `<rust-security-state>`, `<rust-feature-slice-state>`, `<sqlx-migration-state>`, `<rust-migration-state>`, `<axum-scaffold-state>`, `<cargo-package-state>`
- New agent state tags: `<rust-arch-checklist-agent-state>`, `<rust-security-agent-state>`, `<rust-feature-slice-agent-state>`, `<sqlx-migration-agent-state>`, `<rust-migration-agent-state>`, `<axum-scaffold-agent-state>`, `<cargo-package-agent-state>`
- `rust-security-review-federal` is deferred — add as Plan C after Plan B is verified
- Rust's `async_trait` crate is being superseded by native async traits in Rust 1.75+ — skills should note both patterns and recommend native async traits for Rust 1.75+
