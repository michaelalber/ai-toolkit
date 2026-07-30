# Fitness Functions — Rust (cargo-deny + dependency-direction test)

Two complementary gates. **cargo-deny** enforces dependency *policy* (advisories, license, bans,
sources). A **dependency-direction test** enforces *internal* crate/module boundaries by reading
the `cargo metadata` graph. For coupling *metrics*, defer to `dependency-mapper`.

## 1a. Dependency policy — cargo-deny

```toml
# deny.toml  — gates ADR-0005: no copyleft deps, no known-vuln deps.
[advisories]
yanked = "deny"
[bans]
multiple-versions = "warn"
deny = [{ name = "openssl" }]   # ADR mandates rustls
[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]
```

Install: `cargo install cargo-deny`. Check: `cargo deny check` (exits non-zero on any violation).

## 1b. Internal layering — dependency-direction test

A workspace integration test that asserts the `domain` crate depends on nothing internal
(enforces a hexagonal-core ADR). It parses the resolved graph emitted by `cargo metadata`:

```rust
// tests/architecture.rs — gates ADR-0006: domain crate has no internal deps.
#[test]
fn domain_crate_has_no_internal_dependencies() {
    let out = std::process::Command::new(env!("CARGO"))
        .args(["metadata", "--format-version", "1", "--no-deps"])
        .output()
        .expect("run cargo metadata");
    let meta: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap();
    let members: Vec<String> = meta["workspace_members"].as_array().unwrap().iter()
        .map(|m| m.as_str().unwrap().split(' ').next().unwrap().to_string())
        .collect();
    let domain = meta["packages"].as_array().unwrap().iter()
        .find(|p| p["name"] == "domain").unwrap();
    let internal: Vec<String> = domain["dependencies"].as_array().unwrap().iter()
        .map(|d| d["name"].as_str().unwrap().to_string())
        .filter(|n| members.contains(n))
        .collect();
    assert!(internal.is_empty(), "domain depends on internal crates: {internal:?}");
}
```

`serde_json` as a dev-dependency parses the metadata; the static args carry no injection surface.

## 2. CI wiring (GitHub Actions)

```yaml
# .github/workflows/ci.yml
  - name: Dependency policy (gates ADR-0005)
    run: cargo deny check
  - name: Architecture fitness functions (gates ADR-0006)
    run: cargo test --test architecture
```

## 3. Prove it gates

1. `cargo deny check` and `cargo test --test architecture` → both PASS today.
2. Deliberate violations: add `openssl` to a `Cargo.toml`, and add an internal dep to the `domain`
   crate. Re-run → cargo-deny fails on the ban; the test fails listing the internal dep.
3. Revert both. Commit only the green state.

## Other ready-made Rust fitness functions

- **Lint gate:** `cargo clippy -- -D warnings` fails on any lint (treat warnings as errors).
- **Coverage:** `cargo llvm-cov --fail-under-lines 80`.
