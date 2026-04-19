# Release Checklist

Pre-publish checklist for Rust crates. Run through every item before tagging a release.

## Pre-Release Checklist

### Metadata
- [ ] `version` bumped correctly (semver: patch/minor/major)
- [ ] `description` is accurate and complete
- [ ] `repository`, `homepage`, `documentation` URLs are valid
- [ ] `keywords` and `categories` are accurate (max 5 keywords)
- [ ] `readme = "README.md"` points to an existing file
- [ ] `include` list is correct — no test fixtures, no `.github/`, no `target/`
- [ ] `rust-version` (MSRV) is declared and tested in CI

### Code Quality
- [ ] `cargo test --all-features` passes on stable
- [ ] `cargo test --all-features` passes on MSRV
- [ ] `cargo clippy -- -D warnings` passes
- [ ] `cargo fmt --check` passes
- [ ] `cargo doc --no-deps --all-features` passes (no missing_docs warnings)
- [ ] All `unsafe` blocks have `// SAFETY:` comments

### Semver
- [ ] `cargo semver-checks` passes (no unintentional breaking changes)
- [ ] If breaking: major version bumped; migration guide in CHANGELOG

### Documentation
- [ ] CHANGELOG.md updated with this version's changes
- [ ] README.md reflects current API
- [ ] At least one example in `examples/` compiles and runs

### Publish Dry Run
- [ ] `cargo publish --dry-run` passes
- [ ] Published file list looks correct (no surprises)

## Release Steps

```bash
# 1. Verify everything passes
cargo test --all-features
cargo clippy -- -D warnings
cargo fmt --check
cargo doc --no-deps --all-features
cargo semver-checks
cargo publish --dry-run

# 2. Update version in Cargo.toml
# Edit version = "X.Y.Z"

# 3. Update CHANGELOG.md
# Move [Unreleased] to [X.Y.Z] - YYYY-MM-DD

# 4. Commit
git add Cargo.toml CHANGELOG.md
git commit -m "chore: release vX.Y.Z"

# 5. Tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main --tags

# 6. CI publishes automatically via release.yml
# OR publish manually:
cargo publish
```

## Yanking Policy

Yank a version **only** for:
- Security vulnerability
- Soundness issue (undefined behavior)
- Accidental publish of credentials

Do **not** yank for:
- API design mistakes (deprecate instead)
- Performance issues (release a new version)
- Missing features (release a new version)

```bash
# Yank a version
cargo yank --version X.Y.Z

# Un-yank (if the issue is resolved)
cargo yank --version X.Y.Z --undo
```

## CHANGELOG.md Format (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-15

### Added
- New `Foo::with_config()` constructor

### Changed
- `Bar::process()` now returns `Result<(), BarError>` instead of `Option<()>`

### Fixed
- Panic when input is empty string

## [0.1.0] - 2025-01-01

### Added
- Initial release

[Unreleased]: https://github.com/org/repo/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/org/repo/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/org/repo/releases/tag/v0.1.0
```

## GitHub Release Workflow (`release.yml`)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    name: Publish to crates.io
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Run tests
        run: cargo test --all-features

      - name: Publish
        run: cargo publish
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

## Required GitHub Secret

Add `CARGO_REGISTRY_TOKEN` to the repository secrets:
1. Generate token at https://crates.io/settings/tokens
2. Scope: `publish-new` and `publish-update`
3. Add to GitHub: Settings → Secrets → Actions → New repository secret
