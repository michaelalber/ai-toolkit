# rust-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Rust Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Ownership discipline** — no `.clone()`/`.to_owned()` where a borrow suffices; `Rc`/`Arc` only for genuine shared ownership | High |
| 2 | **Trait coherence** — trait impls have clear semantic purpose; no "marker-trait soup" to satisfy generic bounds | Medium |
| 3 | **Error handling** — `thiserror` for library errors, `anyhow` for application; no `.unwrap()`/`.expect()` outside `#[cfg(test)]`; consistent `?` | High |
| 4 | **`unsafe` justification** — every `unsafe` block carries a correct `// SAFETY:` comment; blocks without one are automatic High findings | Critical |
| 5 | **Crate boundary hygiene** — `pub(crate)` is the default; `pub` is a deliberate API decision; internal types do not leak | High |
| 6 | **Async runtime consistency** — exactly one runtime per binary; no blocking calls (`std::thread::sleep`, sync I/O) inside `async fn` | High |
| 7 | **Dependency discipline** — `cargo audit` clean; `cargo deny` for licenses/duplicates; minimal version constraints | Medium |
| 8 | **Test organization** — unit tests in `#[cfg(test)]`, integration tests in `tests/`; behavioral, not structure-coupled | High |

Clippy config: [clippy configuration](references/clippy-configuration.md). Full section-by-section list (with the `unsafe` audit table) + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Clippy must pass first.** `cargo clippy -- -D warnings` is the baseline; report failures before the architectural checklist.
- **Evidence or it is not a finding.** Cite `file:line`; show the grep/clippy output. Never grade on vibes.
- **Edition-gate recommendations.** Do not flag 2015-era patterns in a 2015 crate, or suggest 2024-edition idioms (e.g. RPIT lifetime capture, unsafe-attribute syntax) for an older edition.
- **Architecture, not security.** Memory-safety-as-vulnerability and crypto findings belong to `rust-security-review` — note them and route there.
