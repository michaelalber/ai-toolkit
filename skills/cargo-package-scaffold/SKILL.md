---
name: cargo-package-scaffold
description: >
  Cargo crate creation with CI/CD pipeline setup, test harness, and crates.io publish
  workflow. Use when creating new Rust crates, configuring Cargo.toml metadata, setting
  up GitHub Actions for Rust CI, or publishing to crates.io.
  Triggers on: "scaffold cargo crate", "create rust crate", "new rust library",
  "publish to crates.io", "cargo package", "rust ci pipeline", "cargo workspace",
  "rust crate metadata", "cargo publish workflow".
  Do NOT use when the crate is internal-only and not intended for crates.io
  publication; Do NOT use when the target is a binary application — this skill
  targets library crates.
---

# Cargo Package Scaffold

> "A crate is a promise. Its Cargo.toml is the contract. Its tests are the proof."

> "Publish nothing you would not stake your reputation on. Semver is a social contract."

## Core Philosophy

Publishing a Rust crate is a commitment. Once a version is on crates.io, it cannot be deleted — only yanked. This skill enforces the practices that make crates trustworthy: complete metadata, semver discipline, a CI gate that blocks broken publishes, and a test harness that covers the public API surface.

The scaffold is opinionated by default and configurable by exception. Every generated crate starts with `deny(unsafe_code)`, `#![warn(missing_docs)]`, and a CI pipeline that runs `cargo test`, `cargo clippy`, `cargo fmt --check`, and `cargo publish --dry-run` on every push.

**Non-negotiable constraints:**

- Semver must be respected. Breaking changes require a major version bump.
- `cargo publish --dry-run` must pass in CI before any release.
- Every public item must have a doc comment.
- `deny(unsafe_code)` is the default; unsafe requires explicit justification and a safety comment.

## Domain Principles

| # | Principle | Priority | Description | Applied As |
|---|-----------|----------|-------------|------------|
| 1 | Semver Discipline | Critical | Breaking changes = major bump. Additive = minor. Fixes = patch. | Enforced via `cargo semver-checks` in CI |
| 2 | Complete Metadata | Critical | name, version, description, license, repository, keywords, categories | Validated in CI with `cargo publish --dry-run` |
| 3 | Documentation First | High | Every public item has a doc comment before merge | `#![warn(missing_docs)]` + `cargo doc --no-deps` in CI |
| 4 | Safe by Default | High | `#![deny(unsafe_code)]` unless the crate's purpose requires unsafe | Frontmatter flag in scaffold |
| 5 | Feature Flags | High | Optional dependencies behind feature flags; default features minimal | `[features]` section scaffolded with `default = []` |
| 6 | MSRV Declaration | Medium | Minimum Supported Rust Version declared and tested in CI | `rust-version` field in Cargo.toml |
| 7 | Workspace Awareness | Medium | Detect workspace root; inherit shared metadata via `[workspace.package]` | Read Cargo.toml before writing |
| 8 | Changelog Discipline | Medium | CHANGELOG.md updated on every release; follows Keep a Changelog format | Template generated; updated on release |
| 9 | Example Coverage | Medium | At least one example in `examples/` that compiles and runs | Scaffolded with `cargo run --example` in CI |
| 10 | Yanking Policy | Low | Yank only for security or soundness issues; deprecate for API changes | Documented in CONTRIBUTING.md |

## Workflow

### Phase 1: DETECT

**Goal:** Understand the project context before writing anything.

- Read workspace `Cargo.toml` if present
- Check for existing `[workspace.package]` metadata to inherit
- Identify existing CI workflows (`.github/workflows/`)
- Check for existing `deny.toml` (cargo-deny configuration)
- Report findings

**Exit criteria:** Project context documented; no files written.

### Phase 2: SCAFFOLD

**Goal:** Create the crate skeleton.

```
<crate-root>/
├── Cargo.toml          # Complete metadata
├── src/
│   └── lib.rs          # #![deny(unsafe_code)], #![warn(missing_docs)], module structure
├── tests/
│   └── integration.rs  # Integration test stubs for public API
├── examples/
│   └── basic.rs        # Minimal working example
├── CHANGELOG.md        # Keep a Changelog format
└── README.md           # Crate description, install, quick start
```

**Exit criteria:** `cargo build` passes; `cargo test` passes; `cargo doc --no-deps` passes.

### Phase 3: CI

**Goal:** Create GitHub Actions workflow.

Pipeline jobs:
1. `test` — `cargo test --all-features` on stable + MSRV
2. `lint` — `cargo clippy -- -D warnings` + `cargo fmt --check`
3. `docs` — `cargo doc --no-deps --all-features`
4. `semver` — `cargo semver-checks` (on PRs only)
5. `publish-dry-run` — `cargo publish --dry-run`

**Exit criteria:** Workflow file created; all jobs defined.

### Phase 4: RELEASE

**Goal:** Configure the release workflow.

- `release.yml` triggered on `v*` tags
- Runs full CI gate first
- Publishes to crates.io via `CARGO_REGISTRY_TOKEN` secret
- Creates GitHub Release with CHANGELOG excerpt

**Exit criteria:** Release workflow created; token secret documented.

### Phase 5: VERIFY

**Goal:** Confirm the scaffold is complete and correct.

- `cargo build` — no errors
- `cargo test` — all tests pass
- `cargo clippy -- -D warnings` — no warnings
- `cargo fmt --check` — formatted
- `cargo doc --no-deps` — no missing docs warnings
- `cargo publish --dry-run` — passes

**Exit criteria:** All verification commands pass.

## State Block

```
<cargo-package-scaffold-state>
phase: DETECT | SCAFFOLD | CI | RELEASE | VERIFY | COMPLETE
crate_name: [name]
crate_type: lib | bin | proc-macro
workspace: true | false
workspace_metadata_inherited: true | false
msrv: [version]
unsafe_allowed: true | false
features: [comma-separated]
ci_created: true | false
release_workflow_created: true | false
build_status: pass | fail | not-run
last_action: [description]
next_action: [description]
</cargo-package-scaffold-state>
```

## Output Templates

### Cargo.toml Template

```toml
[package]
name = "crate-name"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"
description = "One sentence description."
license = "MIT OR Apache-2.0"
repository = "https://github.com/org/repo"
homepage = "https://github.com/org/repo"
documentation = "https://docs.rs/crate-name"
keywords = ["keyword1", "keyword2"]
categories = ["category1"]
readme = "README.md"
include = ["src/**/*", "tests/**/*", "examples/**/*", "README.md", "CHANGELOG.md", "LICENSE*"]

[features]
default = []

[dependencies]

[dev-dependencies]
```

### lib.rs Template

```rust
// <AI-Generated START>
#![deny(unsafe_code)]
#![warn(missing_docs)]

//! # crate-name
//!
//! One sentence description.
//!
//! ## Quick Start
//!
//! ```rust
//! use crate_name::Foo;
//!
//! let foo = Foo::new();
//! ```

/// A placeholder type. Replace with your actual public API.
pub struct Foo;

impl Foo {
    /// Creates a new `Foo`.
    pub fn new() -> Self {
        Self
    }
}

impl Default for Foo {
    fn default() -> Self {
        Self::new()
    }
}
// <AI-Generated END>
```

### CI Workflow Template

```yaml
# <AI-Generated START>
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always
  RUST_BACKTRACE: 1

jobs:
  test:
    name: Test (${{ matrix.rust }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        rust: [stable, "1.75"]  # stable + MSRV
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ matrix.rust }}
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt
      - uses: Swatinem/rust-cache@v2
      - run: cargo clippy -- -D warnings
      - run: cargo fmt --check

  docs:
    name: Docs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"

  publish-dry-run:
    name: Publish Dry Run
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo publish --dry-run
# <AI-Generated END>
```

## AI Discipline Rules

**WRONG:** Publishing without `cargo publish --dry-run` passing in CI.
**RIGHT:** `publish-dry-run` job is a required CI gate; release workflow depends on it.

**WRONG:** `version = "0.1.0"` with no `rust-version` field.
**RIGHT:** Always declare MSRV. Test it in CI with a matrix entry.

**WRONG:** `unsafe` block with no safety comment.
**RIGHT:**
```rust
// SAFETY: [explain why this is sound]
unsafe { ... }
```

**WRONG:** `default-features = true` pulling in heavy transitive dependencies.
**RIGHT:** `default = []` in `[features]`. Users opt in to what they need.

**WRONG:** Missing `include` field — publishes `.github/`, `target/`, test fixtures.
**RIGHT:** Explicit `include` list in Cargo.toml.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|--------------|--------------|-----------------|
| 1 | No MSRV declared | Users on older Rust get cryptic errors | Declare `rust-version`; test in CI matrix |
| 2 | `default-features` pulls everything | Bloats compile times for users who need one feature | `default = []`; explicit opt-in features |
| 3 | No `include` in Cargo.toml | Publishes `.github/`, `target/`, test fixtures | Explicit `include` list |
| 4 | Missing `repository` field | Users can't find source; docs.rs can't link | Always set `repository` |
| 5 | `unsafe` without safety comment | Unsound code ships silently | `// SAFETY:` comment required; `deny(unsafe_code)` default |
| 6 | Breaking change as minor bump | Breaks downstream users silently | `cargo semver-checks` in CI; major bump for breaking |
| 7 | No `cargo publish --dry-run` in CI | Broken publish discovered at release time | Dry-run job on every push |
| 8 | Yanking for API changes | Yank breaks users who pinned the version | Yank only for security/soundness; deprecate for API |
| 9 | No examples | Users can't understand the API without reading source | At least one `examples/basic.rs` |
| 10 | `pub use` re-exports without docs | Public API surface is undocumented | Every re-export has a doc comment |

## Error Recovery

**`cargo publish --dry-run` fails with "missing field":**
- Check Cargo.toml for required fields: `name`, `version`, `edition`, `description`, `license`, `repository`
- Run `cargo metadata --no-deps` to see what Cargo sees
- Add missing fields; re-run dry-run

**`cargo semver-checks` reports breaking change:**
- Identify the breaking change (removed item, changed signature, sealed trait)
- If intentional: bump major version, update CHANGELOG
- If unintentional: revert the change or add a compatibility shim

**CI fails on MSRV matrix entry:**
- Identify which feature/dependency requires a newer Rust version
- Either raise the MSRV (update `rust-version` and CI matrix) or pin the dependency to an older version
- Document the MSRV bump in CHANGELOG

**`cargo doc` fails with "missing documentation":**
- Run `cargo doc --no-deps 2>&1 | grep "warning\[missing_docs\]"` to list undocumented items
- Add doc comments to all flagged public items
- Re-run until clean

## Session Template

Use this template to report scaffold progress to the user.

```
## Cargo Package Scaffold

**Crate**: [name]
**Type**: [lib | bin | proc-macro]
**Workspace**: [yes | no]
**MSRV**: [version]

### Detection
- Workspace metadata: [inherited | standalone]
- Existing CI: [yes at path | no]
- deny.toml: [yes | no]

### Files Created
[List of created files]

### Verification
- cargo build: [PASS | FAIL]
- cargo test: [PASS | FAIL]
- cargo clippy -- -D warnings: [PASS | FAIL]
- cargo fmt --check: [PASS | FAIL]
- cargo doc --no-deps: [PASS | FAIL]
- cargo publish --dry-run: [PASS | FAIL]

### Next Steps
- Add `CARGO_REGISTRY_TOKEN` secret to GitHub repository
- Update CORS allowlist / API URLs in README
- Fill in crate-specific documentation
```

## Integration with Other Skills

- **rust-architecture-checklist** — run after scaffold to verify the crate's internal architecture
- **rust-security-review** — run before first publish to audit for security issues
- **rust-migration-analyzer** — use when migrating an existing crate to a new Rust edition
- **supply-chain-audit** — audit crate dependencies for CVEs and license compliance before publish
