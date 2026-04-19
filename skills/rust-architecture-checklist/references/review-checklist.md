# Rust Architecture Review Checklist

A systematic checklist for reviewing Rust codebases. Use alongside `cargo clippy` and `cargo audit`.

---

## Pre-Review Setup

```bash
# Run these before starting the checklist
cargo clippy -- -D warnings          # Must pass before proceeding
cargo audit                           # Check for CVEs
cargo test                            # Baseline test suite
grep -rn "unsafe" src/ | wc -l       # Count unsafe blocks
cat Cargo.toml | grep edition         # Identify Rust edition
```

---

## Section 1: Ownership & Borrowing

### 1.1 Clone Usage
- [ ] No `.clone()` on non-trivial types (Vec, HashMap, String) where a reference would suffice
- [ ] `.clone()` calls in hot paths are justified by a comment
- [ ] No `.to_owned()` or `.to_string()` in loops without justification

```bash
# Find clone calls
grep -rn "\.clone()" src/ --include="*.rs"
grep -rn "\.to_owned()" src/ --include="*.rs"
```

### 1.2 Shared Ownership
- [ ] `Rc<T>` is used only in single-threaded contexts
- [ ] `Arc<T>` is used only when shared ownership across threads is required
- [ ] `Arc<Mutex<T>>` is not used as a default for all shared state
- [ ] `RefCell<T>` usage is documented with the invariant that prevents borrow panics at runtime

```bash
grep -rn "Arc<" src/ --include="*.rs"
grep -rn "Rc<" src/ --include="*.rs"
grep -rn "RefCell<" src/ --include="*.rs"
```

### 1.3 Move Semantics
- [ ] Large types that are moved frequently are either `Copy` or passed by reference
- [ ] No unnecessary moves of types that implement `Copy`

---

## Section 2: Trait Design

### 2.1 Trait Definitions
- [ ] Each trait has a clear, single semantic purpose
- [ ] Trait methods have documentation comments (`///`)
- [ ] Traits with only one method are justified (not just a workaround for function pointers)
- [ ] `Default` is implemented for types where a sensible default exists

### 2.2 Trait Implementations
- [ ] No blanket implementations that exist only to satisfy compiler bounds
- [ ] `Display` and `Debug` are both implemented for public error types
- [ ] `From`/`Into` conversions are implemented for natural type conversions
- [ ] `Iterator` implementations are correct (especially `size_hint`)

### 2.3 Object Safety
- [ ] Traits used as `dyn Trait` are object-safe (no generic methods, no `Self` return types)
- [ ] `dyn Trait` vs. `impl Trait` vs. generics choice is intentional and documented

---

## Section 3: Error Handling

### 3.1 unwrap/expect Usage
- [ ] No `.unwrap()` outside `#[cfg(test)]` blocks in library crates
- [ ] No `.expect()` outside `#[cfg(test)]` blocks in library crates (or has a meaningful message)
- [ ] `.unwrap()` in application code is justified by a comment explaining the invariant

```bash
# Find unwrap/expect outside test modules
grep -rn "\.unwrap()\|\.expect(" src/ --include="*.rs" | grep -v "#\[cfg(test)\]"
```

### 3.2 Error Types
- [ ] Library crates define error types with `thiserror`
- [ ] Application crates use `anyhow` for error propagation
- [ ] Error types implement `std::error::Error`
- [ ] Error variants have descriptive names and messages
- [ ] No `Box<dyn Error>` in library public APIs

### 3.3 Error Propagation
- [ ] `?` operator is used consistently (not mixed with `match` on `Result` for no reason)
- [ ] Error context is added with `.context()` (anyhow) or `.map_err()` at appropriate boundaries
- [ ] Errors are not silently swallowed with `let _ = result;`

```bash
grep -rn "let _ =" src/ --include="*.rs"
```

---

## Section 4: Async Patterns

### 4.1 Runtime Consistency
- [ ] Only one async runtime is used per binary (Tokio OR async-std, not both)
- [ ] Runtime is initialized once at the top level (`#[tokio::main]` or `tokio::runtime::Runtime::new()`)
- [ ] No nested runtime creation

```bash
grep -rn "tokio\|async.std\|smol" Cargo.toml
```

### 4.2 Blocking in Async
- [ ] No `std::thread::sleep()` inside `async fn` (use `tokio::time::sleep()`)
- [ ] No synchronous file I/O inside `async fn` (use `tokio::fs`)
- [ ] CPU-intensive work uses `tokio::task::spawn_blocking()`
- [ ] No `std::sync::Mutex` held across `.await` points (use `tokio::sync::Mutex`)

```bash
grep -rn "thread::sleep\|std::fs::" src/ --include="*.rs"
```

### 4.3 Task Management
- [ ] `tokio::spawn` tasks have their `JoinHandle` handled (not silently dropped)
- [ ] Cancellation is handled gracefully (tasks check for cancellation at yield points)
- [ ] No unbounded channels that can grow without limit

---

## Section 5: `unsafe` Audit

### 5.1 SAFETY Comments
- [ ] Every `unsafe` block has a `// SAFETY:` comment
- [ ] SAFETY comments explain the invariant, not just restate the code
- [ ] SAFETY comments are accurate (not copy-pasted from elsewhere)

```bash
# Find unsafe blocks without SAFETY comments
grep -n "unsafe" src/**/*.rs | grep -v "// SAFETY:"
```

### 5.2 unsafe Categories
For each `unsafe` block, verify:

| Category | Required Invariant |
|----------|--------------------|
| Raw pointer dereference | Pointer is non-null, aligned, and points to valid memory |
| `transmute` | Source and target types have the same size and alignment; bit pattern is valid for target type |
| FFI call | Called function's preconditions are met; no undefined behavior in the C ABI |
| `static mut` | Access is synchronized or provably single-threaded |
| Inline assembly | Register constraints are correct; no clobber of callee-saved registers without restoration |

### 5.3 unsafe Minimization
- [ ] `unsafe` blocks are as small as possible (wrap only the unsafe operation, not surrounding safe code)
- [ ] Safe abstractions are provided over `unsafe` internals
- [ ] `unsafe impl` for `Send`/`Sync` is justified by the type's actual thread-safety properties

---

## Section 6: Crate Boundary Hygiene

### 6.1 Visibility
- [ ] Internal types use `pub(crate)` not `pub`
- [ ] Internal modules use `pub(crate)` not `pub`
- [ ] `pub use` re-exports are intentional (not accidental leakage)
- [ ] The public API is documented in `lib.rs` or `mod.rs`

```bash
grep -rn "^pub " src/ --include="*.rs" | grep -v "pub fn\|pub struct\|pub enum\|pub trait\|pub type\|pub use\|pub mod"
```

### 6.2 API Surface
- [ ] Public types implement `Debug`
- [ ] Public types implement `Clone` only if cloning is a meaningful operation
- [ ] Public functions have `///` doc comments
- [ ] `#![deny(missing_docs)]` is set for library crates

### 6.3 Workspace Structure (if applicable)
- [ ] Crate boundaries reflect domain boundaries, not technical layers
- [ ] Shared types live in a dedicated `common` or `types` crate
- [ ] No circular dependencies between workspace crates

---

## Section 7: Dependency Health

### 7.1 cargo audit
- [ ] `cargo audit` returns clean (no known CVEs)
- [ ] Any suppressed advisories are documented with justification

### 7.2 Dependency Minimization
- [ ] No dependencies that duplicate `std` functionality
- [ ] `serde` features are specified (`features = ["derive"]` not the full crate)
- [ ] `tokio` features are specified (not `features = ["full"]` in library crates)
- [ ] No duplicate transitive dependencies at different versions (check with `cargo tree -d`)

```bash
cargo tree -d          # Show duplicate dependencies
cargo outdated         # Show outdated dependencies
```

### 7.3 Feature Flags
- [ ] Feature flags are additive (enabling a feature adds functionality; disabling removes it)
- [ ] No feature that changes behavior without adding/removing code
- [ ] `default` features are minimal

---

## Section 8: Type-State Pattern Opportunities

### 8.1 State Machine Identification
- [ ] Domain entities with lifecycle states are identified (e.g., Order: Draft → Submitted → Fulfilled)
- [ ] State transitions are enforced at compile time where feasible
- [ ] Runtime state checks (`if order.status == Status::Draft`) are candidates for type-state

### 8.2 Builder Pattern
- [ ] Complex object construction uses the builder pattern
- [ ] Required fields are enforced at compile time (not runtime panics)
- [ ] Builder `build()` returns `Result<T, E>` for fallible construction

---

## Section 9: Lifetime Clarity

### 9.1 Lifetime Annotations
- [ ] Functions with more than 2 named lifetime parameters are candidates for redesign
- [ ] Named lifetimes are used when the relationship between lifetimes is non-obvious
- [ ] `'static` bounds are justified (not used to avoid lifetime complexity)

### 9.2 Self-Referential Structures
- [ ] No self-referential structs without `Pin` (use `ouroboros` or redesign)
- [ ] `Pin<Box<T>>` usage is documented with the pinning invariant

---

## Section 10: Test Organization

### 10.1 Unit Tests
- [ ] Unit tests are in `#[cfg(test)]` modules in the same file as the code under test
- [ ] Test functions are named `test_<what>_<condition>_<expected>` or similar descriptive pattern
- [ ] Tests cover error paths, not just happy paths

### 10.2 Integration Tests
- [ ] Integration tests are in `tests/` directory
- [ ] Integration tests test the public API only (no `use crate::internal::*`)
- [ ] Integration tests have their own fixtures and helpers

### 10.3 Doc Tests
- [ ] Public API items have doc tests (`///` code blocks that compile and run)
- [ ] `cargo test --doc` passes
- [ ] Doc tests use `# use crate::*;` to reduce boilerplate where appropriate

```bash
cargo test --doc
cargo test --test '*'   # Run integration tests only
```

---

## Final Verification

```bash
cargo clippy -- -D warnings    # Zero warnings
cargo test                      # All tests pass
cargo audit                     # No CVEs
cargo fmt --check               # Formatted correctly
cargo doc --no-deps             # Documentation builds without warnings
```
