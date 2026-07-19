# Cargo Scaffold Templates

Code and report templates emitted by the scaffold. The `Cargo.toml` template lives in
`cargo-metadata-reference.md`; the `release.yml` workflow and CHANGELOG format live in
`release-checklist.md`.

## lib.rs Template

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

## CI Workflow Template (`.github/workflows/ci.yml`)

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
        rust: [stable, "1.85"]  # stable + MSRV
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ matrix.rust }}
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
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
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features
        env:
          RUSTDOCFLAGS: "-D warnings"

  publish-dry-run:
    name: Publish Dry Run
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo publish --dry-run
# <AI-Generated END>
```

Add a `semver` job (`cargo semver-checks`, PRs only) when the crate has a published baseline to
diff against.

## Progress Report Template

Use this to report scaffold progress to the user.

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
- Fill in crate-specific documentation
```
