# Cargo Package Conventions

Depth behind the Core Philosophy constraints: the full principle set, anti-patterns, discipline
rules, and recovery steps. Load when scaffolding or reviewing a crate's publish-readiness.

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

## Discipline Rules

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
