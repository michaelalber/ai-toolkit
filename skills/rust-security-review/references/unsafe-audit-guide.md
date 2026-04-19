# `unsafe` Block Audit Guide for Rust Security Reviews

A systematic guide for auditing `unsafe` blocks in Rust codebases. Every `unsafe` block
is a promise to the compiler that the developer has verified the invariants that make the
code safe. This guide helps verify those promises.

---

## Why `unsafe` Matters for Security

Rust's safety guarantees are conditional: they hold for safe code. `unsafe` blocks opt out
of those guarantees. A bug in an `unsafe` block can cause:

- **Memory corruption** — buffer overflows, use-after-free, double-free
- **Undefined behavior** — code that appears to work but has unpredictable behavior
- **Security vulnerabilities** — exploitable memory safety violations identical to C/C++ bugs

The Rust compiler cannot verify `unsafe` code. The developer must. This guide provides
the framework for that verification.

---

## Finding `unsafe` Blocks

```bash
# All unsafe blocks (including unsafe fn and unsafe impl)
grep -rn "unsafe" src/ --include="*.rs"

# Only unsafe blocks (not fn or impl)
grep -rn "unsafe {" src/ --include="*.rs"

# Unsafe functions
grep -rn "unsafe fn" src/ --include="*.rs"

# Unsafe trait implementations
grep -rn "unsafe impl" src/ --include="*.rs"

# Find unsafe blocks WITHOUT SAFETY comments (security finding)
# This is approximate — manual verification required
grep -B1 "unsafe {" src/**/*.rs | grep -v "// SAFETY:"
```

---

## Category 1: Raw Pointer Dereference

### Pattern
```rust
// <AI-Generated START>
let ptr: *const T = some_pointer();
// SAFETY: ptr is non-null (checked above), properly aligned for T,
// points to a valid T that is not being mutably aliased, and the
// pointed-to T lives at least as long as this reference.
let value = unsafe { &*ptr };
// <AI-Generated END>
```

### Required Invariants
1. **Non-null**: The pointer is not null. Check: `!ptr.is_null()` before the unsafe block.
2. **Aligned**: The pointer is properly aligned for type `T`. Check: `ptr.align_offset(align_of::<T>()) == 0`.
3. **Valid memory**: The pointer points to valid, initialized memory of type `T`.
4. **No mutable aliasing**: No `&mut T` reference to the same memory exists simultaneously.
5. **Lifetime**: The pointed-to memory lives at least as long as the reference created.

### Common Mistakes
- Dereferencing a pointer after the memory it points to has been freed
- Creating `&mut T` from a pointer while a `&T` reference exists
- Dereferencing a pointer to uninitialized memory (`MaybeUninit<T>` without `assume_init`)

### Audit Questions
- Is there a null check before the dereference?
- Where was this pointer obtained? Is it guaranteed to be valid?
- Is there any code path that could free the memory before this dereference?
- Are there any other references (especially mutable) to this memory?

---

## Category 2: `std::mem::transmute`

### Pattern
```rust
// <AI-Generated START>
// SAFETY: [u8; 4] and u32 have the same size (4 bytes) and alignment (1 and 4 bytes
// respectively — u32 alignment is satisfied because bytes is 4-byte aligned).
// The bit pattern of any [u8; 4] is a valid u32.
let value: u32 = unsafe { std::mem::transmute(bytes) };
// <AI-Generated END>
```

### Required Invariants
1. **Same size**: `size_of::<Src>() == size_of::<Dst>()`. Verified at compile time by transmute.
2. **Valid bit pattern**: Every possible bit pattern of `Src` is a valid value of `Dst`.
3. **Alignment**: If transmuting references, the alignment requirements of `Dst` are met.
4. **No invalid values**: `Dst` has no invalid bit patterns (e.g., `bool` only allows 0 and 1).

### Common Mistakes
- Transmuting to `bool` (only 0 and 1 are valid; other values are UB)
- Transmuting to an enum (only discriminant values are valid)
- Transmuting between types with different alignment requirements
- Transmuting references with different lifetimes (use `std::mem::transmute_copy` for size-checked copies)

### Safer Alternatives
- `bytemuck::cast::<Src, Dst>(value)` — safe transmute for POD types with compile-time checks
- `bytemuck::cast_slice::<Src, Dst>(slice)` — safe slice reinterpretation
- `u32::from_le_bytes(bytes)` — safe byte-to-integer conversion

### Audit Questions
- What types are being transmuted? Are they both POD (no padding, no invalid bit patterns)?
- Is `bytemuck` available? Could this be replaced with a safe alternative?
- Is the SAFETY comment specific about why every bit pattern of the source is valid for the destination?

---

## Category 3: FFI Calls (`extern "C"`)

### Pattern
```rust
// <AI-Generated START>
extern "C" {
    fn c_function(ptr: *const u8, len: usize) -> i32;
}

// SAFETY: `data` is a valid slice with length `data.len()`. The C function
// reads exactly `len` bytes from `ptr` and does not retain the pointer after
// returning. The function is thread-safe per its documentation.
let result = unsafe { c_function(data.as_ptr(), data.len()) };
// <AI-Generated END>
```

### Required Invariants
1. **Preconditions met**: All preconditions documented in the C function's API are satisfied.
2. **Pointer validity**: Any pointers passed are valid for the duration of the call.
3. **No aliasing violations**: The C function does not violate Rust's aliasing rules.
4. **Thread safety**: The C function is safe to call from the current thread context.
5. **No retained pointers**: The C function does not store pointers that outlive the call (unless documented).

### Common Mistakes
- Passing a Rust `String` pointer without null-termination (C expects null-terminated strings)
- Passing a slice pointer without the length (C functions often need both)
- Calling a non-thread-safe C function from multiple threads
- Assuming C functions handle null pointers gracefully

### Audit Questions
- Is the C function's documentation available? Are all preconditions listed?
- Are all pointer arguments valid for the duration of the call?
- Does the C function store any pointers? If so, what is their lifetime?
- Is this C function thread-safe? Is it called from multiple threads?

---

## Category 4: `static mut`

### Pattern
```rust
// <AI-Generated START>
static mut GLOBAL_STATE: Option<State> = None;

// SAFETY: This function is called exactly once during program initialization,
// before any threads are spawned. No concurrent access is possible.
unsafe fn initialize(state: State) {
    GLOBAL_STATE = Some(state);
}
// <AI-Generated END>
```

### Required Invariants
1. **Synchronized access**: All accesses are protected by a mutex, or access is provably single-threaded.
2. **No data races**: No two threads can access the static simultaneously without synchronization.
3. **Initialization order**: The static is initialized before it is read.

### Common Mistakes
- Accessing `static mut` from multiple threads without synchronization (data race = UB)
- Reading a `static mut` before it is initialized
- Using `static mut` when `std::sync::OnceLock` or `lazy_static` would be safer

### Safer Alternatives
- `std::sync::OnceLock<T>` — safe lazy initialization
- `std::sync::Mutex<T>` wrapped in `static` — safe mutable global state
- `std::sync::atomic::AtomicUsize` — safe atomic global counter

### Audit Questions
- Is this accessed from multiple threads? If so, is access synchronized?
- Could `OnceLock` or `Mutex` replace this `static mut`?
- Is the initialization order guaranteed?

---

## Category 5: Inline Assembly (`asm!`)

### Pattern
```rust
// <AI-Generated START>
// SAFETY: This assembly reads the CPU cycle counter (RDTSC instruction).
// It does not modify any memory or registers other than the output operands.
// The output is a u64 timestamp; no invariants of the Rust abstract machine
// are violated.
let tsc: u64;
unsafe {
    std::arch::asm!(
        "rdtsc",
        "shl rdx, 32",
        "or rax, rdx",
        out("rax") tsc,
        out("rdx") _,
        options(nostack, nomem, preserves_flags)
    );
}
// <AI-Generated END>
```

### Required Invariants
1. **Register constraints**: All modified registers are declared as outputs or clobbers.
2. **Stack alignment**: Stack is properly aligned if calling conventions require it.
3. **Memory safety**: Assembly does not read/write Rust-managed memory unsafely.
4. **Options correctness**: `nostack`, `nomem`, `preserves_flags` are only set when true.

### Audit Questions
- Are all modified registers declared?
- Does the assembly modify memory? Is `nomem` incorrectly set?
- Is this assembly portable across the target architectures?
- Could this be replaced with a safe intrinsic from `std::arch`?

---

## `unsafe impl Send` and `unsafe impl Sync`

### When These Are Needed
- `Send`: The type can be transferred to another thread. Required when the type contains raw pointers or non-`Send` types but is actually safe to send.
- `Sync`: The type can be shared between threads. Required when the type contains interior mutability that is externally synchronized.

### Required Invariants for `unsafe impl Send`
- The type does not contain any thread-local state
- All raw pointers in the type point to memory that is safe to access from another thread
- The type's destructor is safe to run on any thread

### Required Invariants for `unsafe impl Sync`
- All shared references to the type are safe to use concurrently
- Any interior mutability is protected by synchronization (Mutex, atomic, etc.)

### Audit Questions
- Why does this type not automatically implement `Send`/`Sync`?
- What raw pointers or non-`Send`/`Sync` types does it contain?
- Is the SAFETY comment specific about the synchronization mechanism?

---

## Audit Output Template

```markdown
## `unsafe` Block Audit Results

**Total unsafe blocks**: [N]
**Blocks with SAFETY comments**: [N]
**Blocks without SAFETY comments**: [N] — all are High findings

### Audit Table

| # | File:Line | Category | SAFETY Comment | Comment Quality | Risk | Notes |
|---|-----------|----------|----------------|-----------------|------|-------|
| 1 | src/ffi.rs:23 | FFI call | Yes | Adequate | Low | Preconditions verified |
| 2 | src/buffer.rs:87 | Raw pointer | No | — | **High** | Missing SAFETY comment |
| 3 | src/codec.rs:134 | transmute | Yes | Insufficient | **Medium** | Comment doesn't address alignment |
| 4 | src/init.rs:12 | static mut | Yes | Good | Low | Single-threaded init verified |

### Findings

#### [RS-U01] Missing SAFETY comment at src/buffer.rs:87
**Severity**: High
**Description**: unsafe block dereferences a raw pointer without a // SAFETY: comment.
**Recommendation**: Add // SAFETY: comment explaining: (1) pointer is non-null,
(2) pointer is aligned, (3) memory is valid and not aliased.

#### [RS-U02] Insufficient SAFETY comment at src/codec.rs:134
**Severity**: Medium
**Description**: transmute SAFETY comment addresses size but not alignment or bit pattern validity.
**Recommendation**: Expand SAFETY comment to address all three transmute invariants.
Consider replacing with bytemuck::cast() for a safe alternative.
```
