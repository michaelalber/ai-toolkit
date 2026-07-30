# Assessment Principles, Knowledge Lookups, and Anti-Patterns

Depth for the SCAN and ASSESS phases of `rust-migration-analyzer`. The SKILL.md carries the
lean workflow; this file carries the judgment that makes an assessment trustworthy.

## Domain Principles

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

## Anti-Patterns

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
