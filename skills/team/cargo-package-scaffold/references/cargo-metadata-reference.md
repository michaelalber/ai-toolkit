# Cargo.toml Metadata Reference

Complete reference for Cargo.toml fields required for crates.io publishing.

## Required Fields

```toml
[package]
name = "crate-name"          # Unique on crates.io; lowercase, hyphens
version = "0.1.0"            # Semver: MAJOR.MINOR.PATCH
edition = "2021"             # Rust edition: 2015 | 2018 | 2021
description = "..."          # One sentence; shown on crates.io search
license = "MIT OR Apache-2.0" # SPDX expression; dual-license is idiomatic Rust
```

## Strongly Recommended Fields

```toml
repository = "https://github.com/org/repo"
homepage = "https://github.com/org/repo"
documentation = "https://docs.rs/crate-name"
readme = "README.md"
keywords = ["keyword1", "keyword2"]   # Max 5; used for crates.io search
categories = ["category1"]            # Must match crates.io category slugs
rust-version = "1.75"                 # MSRV; tested in CI
```

## Include / Exclude

```toml
# Explicit include is safer than exclude
include = [
  "src/**/*",
  "tests/**/*",
  "examples/**/*",
  "README.md",
  "CHANGELOG.md",
  "LICENSE-MIT",
  "LICENSE-APACHE",
]
```

## Features

```toml
[features]
default = []                    # Minimal by default
full = ["dep:serde", "dep:tokio"]
serde = ["dep:serde"]
async = ["dep:tokio"]

[dependencies]
serde = { version = "1", optional = true }
tokio = { version = "1", features = ["rt"], optional = true }
```

## Workspace Metadata Inheritance

```toml
# workspace Cargo.toml
[workspace.package]
version = "0.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"
repository = "https://github.com/org/repo"
rust-version = "1.75"

# member Cargo.toml
[package]
name = "crate-name"
version.workspace = true
edition.workspace = true
license.workspace = true
repository.workspace = true
rust-version.workspace = true
description = "Crate-specific description."
```

## Categories Reference (Common)

| Category Slug | Use For |
|---|---|
| `algorithms` | Data structures, algorithms |
| `api-bindings` | Bindings to external APIs |
| `asynchronous` | Async runtimes, utilities |
| `command-line-utilities` | CLI tools |
| `cryptography` | Crypto primitives |
| `database` | DB drivers, ORMs |
| `development-tools` | Build tools, code gen |
| `embedded` | No-std, embedded targets |
| `network-programming` | HTTP, TCP, protocols |
| `parser-implementations` | Parsers, lexers |
| `web-programming` | Web frameworks, clients |
| `web-programming::http-server` | HTTP servers |

Full list: https://crates.io/category_slugs

## Semver Rules

| Change Type | Version Bump | Example |
|---|---|---|
| Bug fix, no API change | Patch (0.0.X) | Fix panic in edge case |
| New public item (additive) | Minor (0.X.0) | Add new method |
| Remove public item | Major (X.0.0) | Remove deprecated fn |
| Change public signature | Major (X.0.0) | Change return type |
| Add required trait bound | Major (X.0.0) | Add `Send` bound |
| Change behavior (breaking) | Major (X.0.0) | Change default value |

**0.x.y special rule:** For `0.x.y`, minor bumps (`0.x+1.0`) are allowed to be breaking. Stabilize at `1.0.0` when the API is ready.
