---
name: rust-migration-analyzer
description: >
  Analyzes Rust migration paths: C/C++ to Rust rewrites using incremental FFI-based
  strangler fig, and Rust modernization (edition upgrades 2015→2018→2021, deprecated
  crate replacement, sync-to-async migration). Assesses risk, quantifies effort, and
  produces a phased migration plan. Does NOT perform the migration — assesses, plans,
  and guides. Use when migrating C or C++ code to Rust, upgrading Rust editions,
  modernizing legacy Rust codebases, replacing deprecated crates, or planning
  sync-to-async migrations.
  Triggers on: "rust migration", "c to rust", "c++ to rust", "rust edition upgrade",
  "modernize rust", "rust legacy migration", "rust rewrite", "cargo fix edition".
  Do NOT use when you want to execute the migration — this skill produces an
  assessment artifact only; Do NOT use when the codebase is already on current
  stable Rust with no legacy patterns.
---

# Rust Migration Analyzer

> "The best migration is the one that never happens. The second best is the one that is incremental, reversible, and tested at every step."
> -- Migration Principle

> "Rust's FFI is the seam. Rewrite module by module, behind a C ABI, with tests on both sides."
> -- C/C++ to Rust Migration Principle

## Core Philosophy

Rust migration analysis covers two distinct contexts:

**Context A: C/C++ → Rust Rewrite**
The FFI boundary is the migration seam. The strangler fig pattern applies: rewrite one module at a time, expose it through a C ABI, and let the C/C++ codebase call the Rust implementation. The C/C++ side does not know it is calling Rust. Tests run against the C/C++ behavior before rewriting; the same tests run against the Rust implementation after. When all modules are rewritten, the C/C++ wrapper is removed.

**Context B: Rust Modernization**
Edition upgrades (2015→2018→2021) are largely mechanical — `cargo fix --edition` handles most of the work. Crate replacements require API compatibility analysis. Sync-to-async migration requires introducing a Tokio runtime and converting function signatures throughout the call chain.

This skill assesses, quantifies risk, and produces a phased migration plan. It does NOT perform the migration. The plan produced by this skill is the input to the implementation phase.

**Non-Negotiable Constraints:**

1. **Assess before plan** — understand the full scope before recommending a migration path. A partial assessment produces a partial plan.
2. **Characterization tests before rewriting** — for C/C++ rewrites, characterization tests against the existing behavior must exist before any Rust code is written.
3. **Incremental migration only** — no big-bang rewrites. Every migration step must be independently deployable and reversible.
4. **FFI safety is explicit** — every `extern "C"` boundary must be documented with the invariants that make it safe.
5. **Edition upgrades are mechanical** — `cargo fix --edition` handles most of the work. Manual intervention is required only for the cases it cannot handle.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Risk Assessment First** | Before recommending a migration path, quantify the risk. How much code? How many FFI boundaries? How many tests? What is the business impact of a regression? | Scan the codebase, count lines of code, count FFI boundaries, count test coverage, assess business criticality. |
| 2 | **Incremental Migration** | For C/C++ rewrites: use the FFI strangler fig — rewrite module by module behind a C ABI. For crate replacements: use feature flags to gate the new implementation. For edition upgrades: `cargo fix --edition` then manual fixes. | Never recommend a big-bang rewrite. Every step must be independently deployable. |
| 3 | **API Compatibility Analysis** | For crate replacements, the new crate's API must be compatible with the existing usage. Incompatible APIs require adapter layers or widespread call-site changes. | Analyze the existing crate's usage patterns; compare with the replacement crate's API; estimate the number of call-site changes. |
| 4 | **Dependency Audit** | Before migrating, audit all dependencies. `cargo outdated` shows outdated crates. `cargo audit` shows CVEs. `cargo tree` shows the dependency graph. Migrating to a modern edition while keeping vulnerable dependencies is incomplete. | Run `cargo outdated`, `cargo audit`, `cargo tree -d` as part of the assessment. |
| 5 | **Business Logic Isolation** | Pure Rust logic (no FFI, no `unsafe`, no platform-specific code) migrates trivially. `unsafe` FFI code does not. Identify the boundary between pure logic and FFI code early. | Categorize code by migration difficulty: pure logic (easy), safe Rust with outdated APIs (medium), `unsafe` FFI code (hard). |
| 6 | **Test Coverage Gate** | For C/C++ rewrites: characterization tests against the C/C++ behavior are required before rewriting. For crate replacements: existing tests must pass with the new crate. For edition upgrades: `cargo test` must pass before and after. | Measure test coverage before migration. Require ≥80% coverage of the code being migrated before starting. |
| 7 | **FFI Safety Documentation** | Every `extern "C"` function is a safety boundary. The invariants that make the FFI call safe must be documented before the migration, not after. | For each FFI boundary, document: what the C function does, what invariants must hold, what happens if they are violated. |
| 8 | **Async Migration Planning** | Sync-to-async migration requires introducing a Tokio runtime and converting function signatures throughout the call chain. This is a pervasive change — plan it as a separate migration phase. | Identify all sync I/O operations; estimate the scope of async conversion; plan Tokio runtime introduction as a dedicated phase. |
| 9 | **Build System Migration** | C/C++ projects often use Makefile or CMake. Migrating to Cargo workspace requires understanding the build graph and translating it to Cargo's model. | Analyze the existing build system; identify build-time code generation, custom linker scripts, and platform-specific flags; translate to Cargo build scripts (`build.rs`). |
| 10 | **Deployment Pipeline** | The migration plan must include deployment pipeline changes. Bare binaries → Docker + CI/CD is a separate concern from the code migration. | Assess the current deployment pipeline; identify what changes are needed; plan as a separate phase from the code migration. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Rust FFI C interop extern unsafe bindgen")` | During FFI analysis — verify FFI patterns and bindgen usage |
| `search_knowledge("Rust edition migration 2015 2018 2021 cargo fix")` | During edition upgrade — verify cargo fix behavior |
| `search_knowledge("cargo outdated audit dependency update")` | During dependency audit — verify tooling |
| `search_knowledge("Rust async migration Tokio sync to async")` | During async migration planning — verify conversion patterns |
| `search_knowledge("Rust strangler fig FFI incremental rewrite")` | During C/C++ rewrite planning — verify strangler fig pattern |

## Workflow

```
SCAN (understand the current state)
    [ ] Identify migration context: C/C++ rewrite OR Rust modernization
    [ ] Count lines of code by category (pure Rust, unsafe, FFI, tests)
    [ ] Run: cargo outdated (for Rust modernization)
    [ ] Run: cargo audit (for Rust modernization)
    [ ] Run: grep -rn "unsafe\|extern" src/ (for FFI analysis)
    [ ] Measure test coverage: cargo tarpaulin or cargo llvm-cov
    [ ] Identify Rust edition (for modernization)
    [ ] Identify async runtime (for async migration)

        |
        v

ASSESS (risk scoring)
    [ ] Score each migration scenario by: Effort, Risk, Blocker potential
    [ ] Identify dependencies between migration steps
    [ ] Identify the critical path
    [ ] Identify quick wins (low effort, high value)

        |
        v

PLAN (phased migration)
    [ ] Define migration phases in dependency order
    [ ] For each phase: scope, effort estimate, risk, success criteria
    [ ] Define rollback plan for each phase
    [ ] Identify test requirements for each phase

        |
        v

REPORT
    [ ] Risk matrix (scenarios × dimensions)
    [ ] Migration phase plan
    [ ] FFI boundary inventory (for C/C++ rewrites)
    [ ] Dependency update plan (for Rust modernization)
    [ ] Recommended tooling
```

**Exit criteria:** Risk matrix produced; phased migration plan delivered; FFI inventory complete (if applicable).

## State Block

```
<rust-migration-state>
phase: SCAN | ASSESS | PLAN | REPORT | COMPLETE
migration_context: c_cpp_rewrite | rust_modernization | both | unknown
rust_edition: 2015 | 2018 | 2021 | unknown
async_runtime: tokio | async-std | none | unknown
loc_total: [N]
loc_unsafe: [N]
loc_ffi: [N]
test_coverage: [percentage | unknown]
cargo_audit_status: clean | N CVEs | not-run
cargo_outdated_count: [N | not-run]
ffi_boundary_count: [N]
migration_phases_planned: [N]
last_action: [description]
next_action: [description]
</rust-migration-state>
```

## Output Templates

### Risk Matrix

```markdown
## Rust Migration Risk Matrix

**Project**: [name]
**Analysis Date**: [date]
**Migration Context**: [C/C++ Rewrite | Rust Modernization | Both]

| Migration Scenario | Effort | Risk | Blocker Potential | Recommended Order |
|-------------------|--------|------|-------------------|-------------------|
| Rust edition upgrade (2015→2021) | Low | Low | No | 1 |
| Deprecated crate replacement | Medium | Medium | Conditional | 2 |
| sync→async migration | High | High | Yes | 3 |
| C/C++ FFI module rewrite | High | High | Yes | 4 |
| Build system migration | Medium | Medium | No | 5 |
```

### Migration Phase Plan

```markdown
## Migration Phase Plan

### Phase 1: [Title]
**Scope**: [what changes]
**Effort**: [S/M/L/XL]
**Risk**: [Low/Medium/High]
**Prerequisites**: [what must be done first]
**Success Criteria**: [how to verify completion]
**Rollback**: [how to undo]
**Tools**: [cargo fix, bindgen, etc.]

### Phase 2: [Title]
[same structure]
```

### FFI Boundary Inventory

```markdown
## FFI Boundary Inventory

| # | Function | File:Line | Direction | Invariants | Risk | Migration Priority |
|---|----------|-----------|-----------|------------|------|-------------------|
| 1 | `c_process_data` | `src/ffi.rs:23` | Rust→C | ptr non-null, len valid | Medium | Phase 2 |
| 2 | `rust_callback` | `src/ffi.rs:87` | C→Rust | called from single thread | High | Phase 1 |
```

## AI Discipline Rules

### CRITICAL: Assess Before Recommending

**WRONG:**
```
You should upgrade to Rust 2021 edition and replace the old crates.
```

**RIGHT:**
```
Assessment findings:
- Edition: 2015 (cargo fix --edition can handle ~90% of the upgrade automatically)
- Deprecated crates: 3 (serde 0.9, tokio 0.2, hyper 0.12)
- Test coverage: 45% (below the 80% gate for safe migration)
- FFI boundaries: 7 (require manual safety documentation)

Recommended migration order:
1. Increase test coverage to 80% (prerequisite for all other phases)
2. Edition upgrade (low risk, mechanical)
3. Crate updates (medium risk, API compatibility analysis required)
4. FFI documentation (prerequisite for any FFI rewrite)
```

### CRITICAL: Characterization Tests Before Rewriting

**WRONG:**
```
Starting the Rust rewrite of the C module.
```

**RIGHT:**
```
Before rewriting the C module, characterization tests are required.
Current test coverage for this module: 0%.

Characterization tests must:
1. Call the C function with representative inputs
2. Assert the outputs match expected behavior
3. Cover edge cases (null inputs, empty arrays, maximum values)

These tests will run against the C implementation now and against the
Rust implementation after the rewrite. They are the migration's safety net.
```

### REQUIRED: Incremental Migration Only

**WRONG:**
```
Rewrite the entire C codebase in Rust.
```

**RIGHT:**
```
Recommended approach: FFI strangler fig
1. Identify the module with the most test coverage and least FFI dependencies
2. Rewrite that module in Rust, exposing the same C ABI
3. Link the Rust implementation into the C/C++ binary
4. Run all existing tests — they should pass unchanged
5. Repeat for the next module
6. When all modules are rewritten, remove the C/C++ wrapper
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Big-Bang Rewrite** | Rewriting everything at once creates a long period where nothing works. The rewrite takes longer than expected. The original keeps getting features. | Use the strangler fig pattern. Rewrite incrementally, one module at a time. |
| 2 | **Rewriting Without Tests** | Without characterization tests, you cannot verify the Rust implementation matches the C/C++ behavior. | Write characterization tests against the C/C++ implementation before rewriting. |
| 3 | **Ignoring Edition Upgrade** | Running Rust 2015 edition in 2024 means missing 6 years of ergonomic improvements. `cargo fix --edition` is mostly automatic. | Run `cargo fix --edition` as the first modernization step. |
| 4 | **Updating All Crates at Once** | Updating 20 crates simultaneously makes it impossible to identify which update caused a regression. | Update one crate at a time. Run tests after each update. |
| 5 | **Async Migration Without Planning** | Converting sync code to async is pervasive — it propagates up the call chain. Starting without a plan creates a half-async codebase that is worse than either. | Plan the async migration as a dedicated phase. Identify the full call chain before starting. |
| 6 | **FFI Without Safety Documentation** | `unsafe` FFI code without documented invariants is a maintenance and security liability. | Document every FFI boundary before migrating. The documentation is the migration's safety net. |
| 7 | **Skipping cargo audit** | Migrating to a modern edition while keeping vulnerable dependencies is incomplete modernization. | Run `cargo audit` as part of the assessment. Fix CVEs before or during the migration. |
| 8 | **Ignoring Build System** | Migrating Rust code without migrating the build system leaves the project in a hybrid state. | Plan build system migration as a dedicated phase. |
| 9 | **No Rollback Plan** | A migration without a rollback plan is a one-way door. | Define rollback for each phase before starting. |
| 10 | **Migrating Under Feature Pressure** | Migrating while adding features creates a moving target. | Freeze feature development during migration phases. |

## Error Recovery

### cargo fix --edition Fails

```
Symptoms: cargo fix --edition reports errors it cannot fix automatically

Recovery:
1. Run: cargo fix --edition --allow-dirty (shows what it can fix)
2. Review the unfixed items: cargo fix --edition 2>&1 | grep "error"
3. Common manual fixes:
   - Macro import changes (macro_rules! → use crate::macro_name)
   - Lifetime elision changes
   - Trait object syntax (Box<Trait> → Box<dyn Trait>)
4. Fix manually, then re-run cargo fix --edition
5. Run: cargo test to verify no regressions
```

### Crate Replacement API Incompatibility

```
Symptoms: After updating a crate, cargo build fails with many errors

Recovery:
1. Check the crate's CHANGELOG for breaking changes
2. Check the migration guide (most major crates have one)
3. Estimate the number of call-site changes
4. If > 50 call sites: consider an adapter layer to minimize changes
5. If < 50 call sites: fix each one individually
6. Run: cargo test after each batch of fixes
```

### FFI Boundary Invariant Violation

```
Symptoms: Rust code called from C crashes or produces incorrect results

Recovery:
1. Identify the FFI boundary where the violation occurs
2. Check the SAFETY comment (if it exists) for the invariant
3. Verify the C caller is meeting the invariant
4. Add assertions in the Rust code to catch violations early:
   assert!(!ptr.is_null(), "FFI invariant violated: ptr must be non-null");
5. Document the violation and the fix in the FFI boundary inventory
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rust-architecture-checklist` | After migration, run `rust-architecture-checklist` to verify the migrated code follows Rust idioms. |
| `rust-security-review` | After migration, run `rust-security-review` to verify the migrated code is secure. |
| `sqlx-migration-manager` | If the migration includes database schema changes, use `sqlx-migration-manager` for the database migration lifecycle. |
| `legacy-migration-analyzer` | Parallel skill for .NET Framework → .NET 10 migrations. Same assessment philosophy; different ecosystem. |
| `supply-chain-audit` | When `cargo audit` finds CVEs during the assessment, `supply-chain-audit` provides deeper analysis. |
