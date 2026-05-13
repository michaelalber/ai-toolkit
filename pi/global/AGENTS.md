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

## Knowledge Grounding (grounded-code-mcp)

A local knowledge base of vetted documentation is available via the `grounded-code-mcp` CLI. **Search it before relying on training data for any covered domain.**

When the grounded-code-mcp extension is active, its tools call the CLI automatically. When running without the extension, invoke the CLI directly:

```bash
grounded-code-mcp search "query" --collection python --json
grounded-code-mcp search-code "query" --language python --json
grounded-code-mcp list-sources --json
grounded-code-mcp source-info <path> --json
grounded-code-mcp query-graph <concept> --depth 2 --json
```

Pass the bare collection suffix — the server prepends `grounded_` automatically:

| `--collection` | What lives here |
|---|---|
| `internal` | XP, TDD, CI/CD, DDD, Clean Architecture, OWASP, NIST AI; technical writing |
| `patterns` | GoF, CQRS, DDD, Clean Architecture, DI, MADR |
| `architecture` | DDIA, SRE, 12-Factor, AOSA, C4, arc42, distributed systems |
| `systems_thinking` | Meadows leverage points, feedback loops, chaos engineering |
| `ui_ux` | Laws of UX, Nielsen, WCAG 2.2, ARIA, USWDS, GOV.UK Design System |
| `dotnet` | EF Core in Action, DI in .NET, Telerik UI for Blazor/MVC/Reporting |
| `python` | Python 3.13, FastAPI, FastMCP, Pydantic v2, pytest, cosmicpython |
| `databases` | SQL, PostgreSQL indexing, relational theory |
| `edge_ai` | RAG, embeddings, LLM application design, AI agents; LangSmith |
| `automation` | PLC, OPC UA, MODBUS, ICS security, Raspberry Pi, NIST 800-82 |
| `4d_legacy` | 4D v18/v20 — source reference for 4D → .NET migration |
| `php` | PHP manual, Laravel 5.5 / 6.x / 12.x |
| `javascript` | JS/TS: Definitive Guide, TypeScript Handbook, Vue 2/3, ECMAScript 2024 |
| `gov` | NIST 800-53/171/218, DOE, Zero Trust, AI RMF, CUI |
| `robotics` | ROS 2, MuJoCo, Isaac Lab, LeRobot, Spinning Up in Deep RL, VLA models |
| `rust` | Rust ownership, async/Tokio, Cargo, error handling, Axum |
| `api_design` | Zalando guidelines, Google AIP, Microsoft REST API guidelines |

Run `grounded-code-mcp list-sources --json` for the authoritative runtime list.

---

## AI-Generated Code Markers

Wrap generated blocks with `<AI-Generated START>` / `<AI-Generated END>` using the language-appropriate comment syntax.
