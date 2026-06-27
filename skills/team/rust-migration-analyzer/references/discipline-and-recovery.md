# AI Discipline Rules and Error Recovery

Behavioral guardrails and recovery procedures for `rust-migration-analyzer`. Apply the discipline
rules throughout; consult the recovery procedures when a migration step fails.

## AI Discipline Rules

### CRITICAL: Assess Before Recommending

**WRONG:**
```
You should upgrade to Rust 2021 edition and replace the old crates.
```

**RIGHT:**
```
Assessment findings:
- Edition: 2015 (cargo fix --edition can handle ~90% of the upgrade automatically)
- Deprecated crates: 3 (serde 0.9, tokio 0.2, hyper 0.12)
- Test coverage: 45% (below the 80% gate for safe migration)
- FFI boundaries: 7 (require manual safety documentation)

Recommended migration order:
1. Increase test coverage to 80% (prerequisite for all other phases)
2. Edition upgrade (low risk, mechanical)
3. Crate updates (medium risk, API compatibility analysis required)
4. FFI documentation (prerequisite for any FFI rewrite)
```

### CRITICAL: Characterization Tests Before Rewriting

**WRONG:**
```
Starting the Rust rewrite of the C module.
```

**RIGHT:**
```
Before rewriting the C module, characterization tests are required.
Current test coverage for this module: 0%.

Characterization tests must:
1. Call the C function with representative inputs
2. Assert the outputs match expected behavior
3. Cover edge cases (null inputs, empty arrays, maximum values)

These tests will run against the C implementation now and against the
Rust implementation after the rewrite. They are the migration's safety net.
```

### REQUIRED: Incremental Migration Only

**WRONG:**
```
Rewrite the entire C codebase in Rust.
```

**RIGHT:**
```
Recommended approach: FFI strangler fig
1. Identify the module with the most test coverage and least FFI dependencies
2. Rewrite that module in Rust, exposing the same C ABI
3. Link the Rust implementation into the C/C++ binary
4. Run all existing tests — they should pass unchanged
5. Repeat for the next module
6. When all modules are rewritten, remove the C/C++ wrapper
```

## Error Recovery

### cargo fix --edition Fails

```
Symptoms: cargo fix --edition reports errors it cannot fix automatically

Recovery:
1. Run: cargo fix --edition --allow-dirty (shows what it can fix)
2. Review the unfixed items: cargo fix --edition 2>&1 | grep "error"
3. Common manual fixes:
   - Macro import changes (macro_rules! → use crate::macro_name)
   - Lifetime elision changes
   - Trait object syntax (Box<Trait> → Box<dyn Trait>)
4. Fix manually, then re-run cargo fix --edition
5. Run: cargo test to verify no regressions
```

### Crate Replacement API Incompatibility

```
Symptoms: After updating a crate, cargo build fails with many errors

Recovery:
1. Check the crate's CHANGELOG for breaking changes
2. Check the migration guide (most major crates have one)
3. Estimate the number of call-site changes
4. If > 50 call sites: consider an adapter layer to minimize changes
5. If < 50 call sites: fix each one individually
6. Run: cargo test after each batch of fixes
```

### FFI Boundary Invariant Violation

```
Symptoms: Rust code called from C crashes or produces incorrect results

Recovery:
1. Identify the FFI boundary where the violation occurs
2. Check the SAFETY comment (if it exists) for the invariant
3. Verify the C caller is meeting the invariant
4. Add assertions in the Rust code to catch violations early:
   assert!(!ptr.is_null(), "FFI invariant violated: ptr must be non-null");
5. Document the violation and the fix in the FFI boundary inventory
```
