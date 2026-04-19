# Clippy Configuration for Production Rust Projects

Recommended Clippy lint configuration for production Rust codebases. Apply these settings
to enforce idiomatic Rust and catch common mistakes automatically.

---

## Crate-Level Lint Attributes

Add to `src/lib.rs` (library crates) or `src/main.rs` (binary crates):

```rust
// <AI-Generated START>
// Deny all Clippy lints — treat warnings as errors
#![deny(clippy::all)]

// Warn on pedantic lints — review each before promoting to deny
#![warn(clippy::pedantic)]

// Warn on nursery lints — these are experimental but often catch real issues
#![warn(clippy::nursery)]

// Deny missing documentation on public items (library crates only)
#![deny(missing_docs)]

// Deny unsafe code at the crate level (remove if unsafe is intentionally used)
// #![deny(unsafe_code)]  // Uncomment if the crate should be entirely safe

// Warn on missing Debug implementations for public types
#![warn(missing_debug_implementations)]
// <AI-Generated END>
```

---

## `.clippy.toml` Configuration

Place in the project root (same directory as `Cargo.toml`):

```toml
# <AI-Generated START>
# Maximum complexity before Clippy warns
cognitive-complexity-threshold = 15

# Maximum number of lines in a function before Clippy warns
too-many-lines-threshold = 60

# Maximum number of arguments before Clippy warns
too-many-arguments-threshold = 7

# Minimum characters for a type name abbreviation to be acceptable
min-ident-chars-threshold = 3

# Allow single-character names in specific contexts
allow-one-letter-params-in-short-closures = true
# <AI-Generated END>
```

---

## Specific Lints to Enable

### Correctness Lints (deny these)

```rust
// <AI-Generated START>
#![deny(clippy::correctness)]  // Already in clippy::all, but explicit is better

// Specific high-value correctness lints:
#![deny(clippy::unwrap_used)]           // No .unwrap() in production code
#![deny(clippy::expect_used)]           // No .expect() in production code (use in tests only)
#![deny(clippy::panic)]                 // No panic!() in library code
#![deny(clippy::indexing_slicing)]      // No unchecked indexing (use .get())
#![deny(clippy::integer_arithmetic)]    // No unchecked integer arithmetic (use checked_add etc.)
// <AI-Generated END>
```

> **Note:** `clippy::unwrap_used`, `clippy::expect_used`, and `clippy::panic` are in
> `clippy::restriction`, not `clippy::all`. They must be explicitly enabled.

### Performance Lints (warn on these)

```rust
// <AI-Generated START>
#![warn(clippy::perf)]  // Already in clippy::all

// Specific performance lints:
#![warn(clippy::large_stack_arrays)]    // Large arrays on the stack
#![warn(clippy::large_enum_variant)]    // Large enum variants (consider Box<T>)
#![warn(clippy::clone_on_ref_ptr)]      // Cloning Arc/Rc (usually unnecessary)
#![warn(clippy::inefficient_to_string)] // Inefficient string conversions
// <AI-Generated END>
```

### Style Lints (warn on these)

```rust
// <AI-Generated START>
#![warn(clippy::style)]  // Already in clippy::all

// Specific style lints worth enabling explicitly:
#![warn(clippy::missing_errors_doc)]    // Document what errors a function can return
#![warn(clippy::missing_panics_doc)]    // Document when a function can panic
#![warn(clippy::must_use_candidate)]    // Functions that should be #[must_use]
// <AI-Generated END>
```

---

## Lints to Disable (with Rationale)

Some pedantic lints produce too many false positives for most projects:

```rust
// <AI-Generated START>
// In lib.rs or main.rs, after #![warn(clippy::pedantic)]:

// Allow: module_name_repetition — common in Rust (e.g., MyError in my_module)
#![allow(clippy::module_name_repetitions)]

// Allow: must_use_candidate — too aggressive for internal functions
#![allow(clippy::must_use_candidate)]

// Allow: missing_errors_doc — enforce only on public APIs, not all functions
// (Remove this if you want strict documentation enforcement)
#![allow(clippy::missing_errors_doc)]
// <AI-Generated END>
```

---

## Per-File and Per-Function Overrides

For specific cases where a lint should be suppressed:

```rust
// <AI-Generated START>
// Suppress for a specific function with justification
#[allow(clippy::too_many_arguments)]
// CLIPPY-ALLOW: This function is a constructor that requires all fields.
// Refactoring to a builder would add complexity without clarity benefit.
pub fn new(a: A, b: B, c: C, d: D, e: E, f: F, g: G) -> Self { ... }

// Suppress for a specific expression
let result = some_vec[index]; // This is safe because index is bounds-checked above
#[allow(clippy::indexing_slicing)]

// Suppress for a test module (tests use unwrap freely)
#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests { ... }
// <AI-Generated END>
```

---

## CI Integration

### GitHub Actions

```yaml
# <AI-Generated START>
name: Clippy

on: [push, pull_request]

jobs:
  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - name: Run Clippy
        run: cargo clippy --all-targets --all-features -- -D warnings
# <AI-Generated END>
```

### Makefile Target

```makefile
# <AI-Generated START>
.PHONY: lint
lint:
	cargo clippy --all-targets --all-features -- -D warnings
	cargo fmt --check
	cargo audit
# <AI-Generated END>
```

---

## Clippy Lint Categories Reference

| Category | Description | Recommended Setting |
|----------|-------------|---------------------|
| `clippy::correctness` | Code that is almost certainly wrong | `deny` |
| `clippy::suspicious` | Code that is probably wrong | `deny` |
| `clippy::style` | Code that should be written differently | `warn` |
| `clippy::complexity` | Unnecessarily complex code | `warn` |
| `clippy::perf` | Code that could be faster | `warn` |
| `clippy::pedantic` | Opinionated lints, some false positives | `warn` (with selective `allow`) |
| `clippy::nursery` | Experimental lints | `warn` |
| `clippy::restriction` | Lints that restrict Rust features | Selective `deny` (e.g., `unwrap_used`) |

---

## Checking Clippy Lint Details

```bash
# List all available lints
cargo clippy -- -W clippy::all --help 2>&1 | grep "clippy::"

# Check what a specific lint does
cargo clippy -- -W clippy::unwrap_used 2>&1

# Run with all lints enabled (for exploration)
cargo clippy -- -W clippy::all -W clippy::pedantic -W clippy::nursery
```
