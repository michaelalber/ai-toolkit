# Output Templates

The REPORT phase produces these three deliverables. Copy the relevant Markdown block and fill in.
Scenario scoring detail for the risk matrix lives in `migration-risk-matrix.md`; FFI boundary
mechanics live in `ffi-patterns.md`.

## Risk Matrix

```markdown
## Rust Migration Risk Matrix

**Project**: [name]
**Analysis Date**: [date]
**Migration Context**: [C/C++ Rewrite | Rust Modernization | Both]

| Migration Scenario | Effort | Risk | Blocker Potential | Recommended Order |
|-------------------|--------|------|-------------------|-------------------|
| Rust edition upgrade (2015→2018→2021→2024) | Low | Low | No | 1 |
| Deprecated crate replacement | Medium | Medium | Conditional | 2 |
| sync→async migration | High | High | Yes | 3 |
| C/C++ FFI module rewrite | High | High | Yes | 4 |
| Build system migration | Medium | Medium | No | 5 |
```

## Migration Phase Plan

```markdown
## Migration Phase Plan

### Phase 1: [Title]
**Scope**: [what changes]
**Effort**: [S/M/L/XL]
**Risk**: [Low/Medium/High]
**Prerequisites**: [what must be done first]
**Success Criteria**: [how to verify completion]
**Rollback**: [how to undo]
**Tools**: [cargo fix, bindgen, etc.]

### Phase 2: [Title]
[same structure]
```

## FFI Boundary Inventory

```markdown
## FFI Boundary Inventory

| # | Function | File:Line | Direction | Invariants | Risk | Migration Priority |
|---|----------|-----------|-----------|------------|------|-------------------|
| 1 | `c_process_data` | `src/ffi.rs:23` | Rust→C | ptr non-null, len valid | Medium | Phase 2 |
| 2 | `rust_callback` | `src/ffi.rs:87` | C→Rust | called from single thread | High | Phase 1 |
```
