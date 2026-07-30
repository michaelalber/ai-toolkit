# FFI Strangler Fig Patterns for C/C++ → Rust Migration

Patterns for incrementally replacing C/C++ code with Rust using the strangler fig
approach. Each pattern maintains a working system throughout the migration.

---

## The Strangler Fig Pattern for FFI

The strangler fig pattern applied to C/C++ → Rust migration:

1. **Identify the seam** — the FFI boundary between the module to rewrite and its callers
2. **Write characterization tests** — tests that call the C/C++ implementation and assert its behavior
3. **Implement in Rust** — write the Rust implementation behind the same C ABI
4. **Link Rust into the C/C++ binary** — the C/C++ callers call the Rust implementation without knowing
5. **Run characterization tests** — they should pass unchanged
6. **Remove the C/C++ implementation** — once all tests pass
7. **Repeat** for the next module

---

## Pattern 1: Rust Function Called from C

Expose a Rust function through a C ABI so C/C++ code can call it.

### Rust Side (`src/lib.rs`)

```rust
// <AI-Generated START>
/// Process data buffer — exposed to C callers.
///
/// # Safety
/// - `data` must be a valid pointer to at least `len` bytes
/// - `data` must remain valid for the duration of this call
/// - `len` must accurately reflect the number of bytes at `data`
/// - This function is not thread-safe; callers must synchronize externally
#[no_mangle]
pub extern "C" fn rust_process_data(data: *const u8, len: usize) -> i32 {
    // SAFETY: The caller guarantees data is valid for len bytes.
    // We create a slice for the duration of this function only.
    let slice = unsafe {
        if data.is_null() {
            return -1; // Error: null pointer
        }
        std::slice::from_raw_parts(data, len)
    };

    // Safe Rust from here
    match process_data_safe(slice) {
        Ok(result) => result as i32,
        Err(_) => -1,
    }
}

fn process_data_safe(data: &[u8]) -> Result<usize, ProcessError> {
    // Pure Rust implementation
    Ok(data.len())
}
// <AI-Generated END>
```

### C Header (`include/my_lib.h`)

```c
// <AI-Generated START>
#ifndef MY_LIB_H
#define MY_LIB_H

#include <stdint.h>
#include <stddef.h>

/**
 * Process data buffer.
 * @param data Pointer to data buffer. Must not be NULL.
 * @param len  Number of bytes in the buffer.
 * @return     Number of bytes processed, or -1 on error.
 */
int32_t rust_process_data(const uint8_t* data, size_t len);

#endif // MY_LIB_H
// <AI-Generated END>
```

### `Cargo.toml` for Static Library

```toml
# <AI-Generated START>
[lib]
name = "my_lib"
crate-type = ["staticlib", "cdylib"]
# staticlib: for linking into C/C++ binaries
# cdylib: for dynamic linking
# <AI-Generated END>
```

### `cbindgen.toml` for Header Generation

```toml
# <AI-Generated START>
language = "C"
include_guard = "MY_LIB_H"
documentation = true
documentation_style = "doxy"

[export]
include = ["rust_process_data"]
# <AI-Generated END>
```

---

## Pattern 2: C Function Called from Rust

Call an existing C function from Rust using `bindgen`-generated bindings.

### Generate Bindings

```bash
# Install bindgen
cargo install bindgen-cli

# Generate bindings from C header
bindgen include/legacy_lib.h \
    --output src/bindings.rs \
    --allowlist-function "legacy_.*" \
    --allowlist-type "LegacyConfig"
```

### Use Generated Bindings

```rust
// <AI-Generated START>
// src/ffi.rs
#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]

include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
// OR if using pre-generated bindings:
// mod bindings;
// use bindings::*;

/// Safe wrapper around the legacy C function.
pub fn process_legacy(config: &LegacyConfig, data: &[u8]) -> Result<i32, LegacyError> {
    // SAFETY: config is a valid LegacyConfig (Rust-owned, properly initialized).
    // data.as_ptr() is valid for data.len() bytes.
    // legacy_process does not retain the pointers after returning.
    let result = unsafe {
        legacy_process(
            config as *const LegacyConfig,
            data.as_ptr(),
            data.len() as u32,
        )
    };

    if result < 0 {
        Err(LegacyError::from_code(result))
    } else {
        Ok(result)
    }
}
// <AI-Generated END>
```

### `build.rs` for Automatic Binding Generation

```rust
// <AI-Generated START>
// build.rs
fn main() {
    // Tell cargo to re-run if the header changes
    println!("cargo:rerun-if-changed=include/legacy_lib.h");

    // Link the legacy C library
    println!("cargo:rustc-link-lib=static=legacy_lib");
    println!("cargo:rustc-link-search=native=lib/");

    // Generate bindings
    let bindings = bindgen::Builder::default()
        .header("include/legacy_lib.h")
        .allowlist_function("legacy_.*")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks::new()))
        .generate()
        .expect("Unable to generate bindings");

    let out_path = std::path::PathBuf::from(std::env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .expect("Couldn't write bindings");
}
// <AI-Generated END>
```

---

## Pattern 3: Characterization Tests

Tests that capture the existing C/C++ behavior before rewriting.

```rust
// <AI-Generated START>
// tests/characterization/legacy_behavior.rs
//
// These tests document the behavior of the C/C++ implementation.
// They run against the C implementation now and against the Rust
// implementation after the rewrite. They must pass in both cases.

#[cfg(test)]
mod characterization {
    use super::*;

    // Document: what does the function return for empty input?
    #[test]
    fn test_process_empty_input_returns_zero() {
        let result = process_legacy_c(&[], &default_config());
        assert_eq!(result, 0, "Empty input should return 0");
    }

    // Document: what does the function return for null-like input?
    #[test]
    fn test_process_single_byte_returns_one() {
        let result = process_legacy_c(&[0x42], &default_config());
        assert_eq!(result, 1, "Single byte should return 1");
    }

    // Document: what is the maximum input size?
    #[test]
    fn test_process_max_size_input() {
        let data = vec![0u8; 65535];
        let result = process_legacy_c(&data, &default_config());
        assert!(result >= 0, "Max size input should not return error");
    }

    // Document: what happens with invalid config?
    #[test]
    fn test_process_invalid_config_returns_error() {
        let result = process_legacy_c(&[0x01], &invalid_config());
        assert_eq!(result, -1, "Invalid config should return -1");
    }
}
// <AI-Generated END>
```

---

## Pattern 4: Incremental Module Replacement

Step-by-step process for replacing one C/C++ module with Rust.

```
Step 1: Identify the module boundary
  - Which C functions does this module export?
  - Which C functions does this module call?
  - What data structures does it use?

Step 2: Write characterization tests
  - Test every exported function
  - Cover: happy path, error cases, edge cases, boundary values
  - Target: ≥80% coverage of the module's behavior

Step 3: Create the Rust implementation
  - Implement the same C ABI (same function signatures, same return codes)
  - Use safe Rust internally; unsafe only at the FFI boundary
  - Write unit tests for the Rust implementation

Step 4: Link Rust into the C/C++ binary
  - Build Rust as a static library
  - Link it into the C/C++ build
  - Replace the C object file with the Rust static library

Step 5: Run characterization tests
  - All tests must pass unchanged
  - If any fail: the Rust implementation has a behavioral difference
  - Fix the Rust implementation until all tests pass

Step 6: Remove the C/C++ implementation
  - Delete the C/C++ source file
  - Update the build system to remove the C/C++ compilation step
  - Run all tests again

Step 7: Refactor the Rust implementation
  - Now that the C ABI is no longer required, refactor to idiomatic Rust
  - Remove the `#[no_mangle]` and `extern "C"` if the callers are now Rust
  - Run tests again
```

---

## FFI Safety Invariant Documentation Template

For each FFI boundary, document the invariants before migrating.

```rust
// <AI-Generated START>
/// [Function name] — [one-line description]
///
/// # C ABI Contract
/// This function is called from C/C++ code. The following invariants
/// must hold at every call site:
///
/// ## Preconditions (caller's responsibility)
/// - `data`: Must be a valid pointer to at least `len` bytes of initialized memory.
///           Must not be NULL. Must remain valid for the duration of this call.
/// - `len`:  Must accurately reflect the number of bytes at `data`.
///           Must be ≤ 65535.
/// - Thread safety: This function is NOT thread-safe. The caller must ensure
///                  no concurrent calls with the same `data` pointer.
///
/// ## Postconditions (this function's guarantees)
/// - Returns the number of bytes processed (0 to len) on success.
/// - Returns -1 on error (null pointer, len > 65535, invalid data format).
/// - Does NOT retain the `data` pointer after returning.
/// - Does NOT modify the memory at `data`.
///
/// ## Error Codes
/// - -1: Null pointer or invalid arguments
/// - -2: Data format error
/// - -3: Internal error (should not occur in normal operation)
#[no_mangle]
pub extern "C" fn documented_function(data: *const u8, len: u32) -> i32 {
    // SAFETY: Preconditions documented above. Caller guarantees data is valid
    // for len bytes and remains valid for the duration of this call.
    todo!()
}
// <AI-Generated END>
```
