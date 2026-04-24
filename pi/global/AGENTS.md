# Coding Agent — Project Overlay

> Place in your project root as `AGENTS.md` when using 20B+ models.
> Pi merges this with the global AGENTS-lite.md automatically — do not duplicate rules already in the global file.
> For 7B models: skip this file; the global baseline is sufficient.

---

## Intent Engineering

When no `intent.md` exists, apply these defaults:

**Value hierarchy:** Correctness → Security → Maintainability → Performance → Delivery speed

**Decide autonomously:** Formatting, naming within established conventions, read-only tool selection, refactoring within approved scope.

**Always escalate:** Irreversible actions, external-facing output, scope changes beyond the stated task, when acceptance criteria cannot be met.

---

## AI Agent Obligations

- Tests first, always. Never generate production code without a failing test.
- Red-Green-Refactor: green = minimum code to pass; refactor only after green.
- Every test: Arrange → Act → Assert. Fast, isolated, deterministic. Test behavior, not implementation.
- Match existing conventions. Read project code before writing. No new patterns without discussion.
- Simple Design (priority order): passes tests → reveals intent → no duplication → fewest elements.

---

## Evaluation Design

Write acceptance criteria before starting any significant task:
- Specific and measurable — not "looks reasonable"
- Binary — pass/fail, not "mostly done"
- Verifiable without prior context

A passing test suite ≠ done. Tests verify code correctness; evals verify the output is actually good.

---

## Security-By-Design

- Validate all inputs at system boundaries — never trust external data
- Parameterized queries only — no string-concatenated SQL
- No hardcoded secrets — environment variables or secrets manager
- Never log sensitive data (passwords, tokens, PII)
- Pin dependency versions; flag all new dependencies for review

---

## Architecture & Design

- Group code by **feature/vertical slice**, not by technical layer
- Keep modules cohesive and loosely coupled; prefer flat, composable structures
- YAGNI: start with the simplest thing that works; no speculative abstractions
- Add interfaces only when multiple concrete implementations exist today
- Add enforced layer boundaries (Onion / Hexagonal) only when domain logic must be tested independently of infrastructure

---

## Code Quality Gates

| Metric | Target |
|--------|--------|
| Cyclomatic Complexity (method) | < 10 |
| Code Coverage (business logic) | ≥ 80% |
| Code Coverage (security-critical) | ≥ 95% |
| Code Duplication | ≤ 3% |

---

## Language Standards

### .NET / C#
- Target .NET 10; enable nullable reference types; treat warnings as errors
- `async`/`await` end-to-end — never `.Result` or `.Wait()`
- Propagate `CancellationToken` through all async chains

### Python
- Python 3.10+; type hints on all function signatures
- Pydantic v2 for validation; `pyproject.toml` for dependencies
- Context managers for all resource lifecycle (files, HTTP sessions, DB connections)

### TypeScript
- Enable `strict` mode in `tsconfig.json`; no `any` without justification
- `const` by default; `let` only when reassignment required; never `var`
- `async`/`await` over raw Promises or callbacks

---

## AI-Generated Code Markers

Wrap generated blocks with `<AI-Generated START>` / `<AI-Generated END>` using the language-appropriate comment syntax.
