# Rust Migration Risk Matrix

Risk scoring matrix for Rust migration scenarios. Use during the ASSESS phase
of the rust-migration-analyzer workflow.

---

## Scoring Dimensions

Each migration scenario is scored on four dimensions:

| Dimension | Low | Medium | High | Blocker |
|-----------|-----|--------|------|---------|
| **Effort** | < 1 day | 1-5 days | 1-4 weeks | > 1 month |
| **Risk** | Mechanical, reversible | API changes, some manual work | Behavioral changes, hard to test | Undefined behavior possible |
| **Blocker Potential** | Can proceed without | Slows other phases | Blocks other phases | Must complete first |
| **Recommended Order** | Do first (quick wins) | Do second | Do third | Do last (most complex) |

---

## Scenario 1: Rust Edition Upgrade (2015 → 2018 → 2021)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | Low | `cargo fix --edition` handles ~90% automatically |
| Risk | Low | Compiler enforces correctness; no behavioral changes |
| Blocker Potential | No | Can proceed without; other phases benefit from modern edition |
| Recommended Order | 1 | Do first — unlocks modern idioms for all subsequent work |

### What cargo fix --edition Handles Automatically
- `extern crate` declarations → removed (2018 edition)
- `macro_rules!` imports → `use crate::macro_name` (2018 edition)
- Anonymous lifetime elision improvements (2018 edition)
- Disjoint capture in closures (2021 edition)
- `IntoIterator` for arrays (2021 edition)

### What Requires Manual Intervention
- Trait object syntax: `Box<Trait>` → `Box<dyn Trait>` (some cases)
- Lifetime annotations in complex generic bounds
- Macro hygiene changes
- `dyn Trait` in function signatures

### Commands
```bash
# Check what can be fixed automatically
cargo fix --edition --allow-dirty

# Apply fixes
cargo fix --edition

# Verify
cargo test
cargo clippy -- -D warnings
```

---

## Scenario 2: Deprecated Crate Replacement

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | Medium | Depends on API compatibility and usage breadth |
| Risk | Medium | API changes may require widespread call-site updates |
| Blocker Potential | Conditional | Blocks if the deprecated crate has CVEs |
| Recommended Order | 2 | After edition upgrade; before async migration |

### Common Crate Replacements

| Deprecated Crate | Replacement | API Compatibility | Notes |
|-----------------|-------------|-------------------|-------|
| `tokio 0.x` | `tokio 1.x` | Breaking | Major API redesign; migration guide available |
| `hyper 0.x` | `hyper 1.x` | Breaking | Major API redesign |
| `actix-web 1/2` | `actix-web 4` | Breaking | Significant changes |
| `serde 0.x` | `serde 1.x` | Breaking | Stable since 2017; upgrade is old |
| `failure` | `thiserror` + `anyhow` | Breaking | `failure` is unmaintained |
| `error-chain` | `thiserror` + `anyhow` | Breaking | `error-chain` is unmaintained |
| `lazy_static` | `std::sync::OnceLock` (1.70+) or `once_cell` | API change | `lazy_static` still works but `OnceLock` is stdlib |
| `chrono` (old) | `chrono` (current) | Minor | Check for DST handling changes |
| `rand 0.6` | `rand 0.8` | Breaking | API changes in `Rng` trait |

### Assessment Process
1. Run `cargo outdated` to identify outdated crates
2. For each outdated crate: check the CHANGELOG for breaking changes
3. Estimate call-site changes: `grep -rn "use <crate>::\|<crate>::" src/`
4. Prioritize: CVE-affected crates first, then most-used crates

---

## Scenario 3: sync → async Migration

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | High | Pervasive change throughout the call chain |
| Risk | High | Behavioral changes; blocking-in-async is a subtle bug |
| Blocker Potential | Yes | Blocks HTTP framework adoption (Axum requires async) |
| Recommended Order | 3 | After crate updates; requires Tokio introduction |

### Migration Steps
1. Add Tokio to `Cargo.toml`: `tokio = { version = "1", features = ["full"] }`
2. Add `#[tokio::main]` to `main()`
3. Identify all I/O operations: file, network, database
4. Convert from the bottom up (leaf functions first, then callers)
5. Replace blocking I/O with async equivalents:
   - `std::fs::read` → `tokio::fs::read`
   - `std::thread::sleep` → `tokio::time::sleep`
   - `std::net::TcpStream` → `tokio::net::TcpStream`
6. Add `.await` at each async call site
7. Convert function signatures: `fn foo()` → `async fn foo()`

### Blocking-in-Async Detection
```bash
# Find potential blocking calls in async contexts
grep -rn "thread::sleep\|std::fs::\|std::net::" src/ --include="*.rs"
```

### Effort Estimation
- Count async conversion points: `grep -rn "fn " src/ | wc -l`
- Estimate: ~15 minutes per function for simple I/O conversion
- Add 50% for testing and debugging

---

## Scenario 4: C/C++ FFI Module Rewrite

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | High | Depends on module complexity and FFI boundary count |
| Risk | High | Behavioral correctness must be verified against C/C++ |
| Blocker Potential | Yes | Requires characterization tests before starting |
| Recommended Order | 4 | After all Rust modernization; requires stable Rust foundation |

### Pre-Rewrite Requirements
- [ ] Characterization tests exist for the module (≥80% coverage)
- [ ] FFI boundary invariants are documented
- [ ] Build system can link Rust into the C/C++ binary
- [ ] CI runs tests against both C/C++ and Rust implementations

### Module Selection Criteria (start with the easiest)
1. Highest test coverage
2. Fewest FFI dependencies (calls to other C functions)
3. Pure computation (no global state, no I/O)
4. Smallest surface area (fewest exported functions)

### FFI Tooling
```bash
# Generate Rust bindings from C headers
bindgen header.h -o src/bindings.rs

# Generate C headers from Rust code (for exposing Rust to C)
cbindgen --config cbindgen.toml --crate my_crate --output include/my_crate.h
```

---

## Scenario 5: Build System Migration (Makefile/CMake → Cargo)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | Medium | Depends on build complexity |
| Risk | Medium | Build-time code generation and custom linker scripts require `build.rs` |
| Blocker Potential | No | Can run hybrid (Cargo + Makefile) during transition |
| Recommended Order | 5 | After code migration; last step |

### Common Build System Translations

| Makefile/CMake | Cargo Equivalent |
|----------------|-----------------|
| Custom code generation | `build.rs` with `println!("cargo:rerun-if-changed=...")` |
| Custom linker flags | `build.rs` with `println!("cargo:rustc-link-lib=...")` |
| Platform-specific compilation | `#[cfg(target_os = "linux")]` or `build.rs` |
| Multiple binaries | `[[bin]]` sections in `Cargo.toml` |
| Shared libraries | `[lib]` with `crate-type = ["cdylib"]` |
| Static libraries | `[lib]` with `crate-type = ["staticlib"]` |

---

## Overall Migration Sequence

```
Phase 0: Assessment (this document)
  ↓
Phase 1: Test Coverage Gate (≥80% before proceeding)
  ↓
Phase 2: Edition Upgrade (cargo fix --edition)
  ↓
Phase 3: Dependency Updates (one crate at a time)
  ↓
Phase 4: sync→async Migration (if needed)
  ↓
Phase 5: FFI Module Rewrites (one module at a time)
  ↓
Phase 6: Build System Migration
  ↓
Phase 7: Final Verification (cargo audit, clippy, test)
```
