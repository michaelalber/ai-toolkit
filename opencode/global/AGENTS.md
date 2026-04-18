# Global Development Rules

## Security Scanning (Snyk)

> **Optional** — requires Snyk CLI + MCP tool. Remove this section if you don't use Snyk.

- Always run `snyk_code_scan` for new first-party code generated in a Snyk-supported language.
- If security issues are found in newly introduced or modified code or dependencies, fix them using the Snyk results context.
- Rescan after fixing to confirm the issues are resolved and no new ones were introduced.
- Repeat until no new issues are found.

---

## Core Philosophy
- Write code for the next engineer, not just the next run
- Correctness first, performance second, cleverness never
- Explicit over implicit; readable over terse
- Leave the codebase cleaner than you found it

---

## Prompting Patterns

Prefix triggers that change how the model reasons:

| Prefix | Effect |
|---|---|
| `think:` | Reason through before answering |
| `think hard:` | Deep analysis — requirements, edge cases, alternatives |
| `think step:` | Numbered step-by-step breakdown |

**Escape hatch** — when a task cannot be completed accurately:
> `[CANNOT COMPLETE]: <one sentence reason>` — then complete what's possible with `# VERIFY:` comments on uncertain parts.

---

## Context Management

- Load the minimum tokens needed; retrieve "just in time" via tools rather than pre-loading
- After a subtask completes, discard intermediate noise — summarize progress, continue with the summary
- For long tasks: maintain a `NOTES.md` scratchpad (current objective, decisions, open questions, next steps)
- After a context reset, re-read the five most recently touched files and the scratchpad before continuing

---

## AI Agent Obligations

- **Tests first, always.** Never generate production code without a failing test. Test files are created before or alongside production files, never after.
- **Red-Green-Refactor.** Green = minimum code to pass. Refactor after green, never before.
- **AAA in every test.** Fast, isolated, deterministic. Test behavior, not implementation.
- **One logical unit per response.** Independently testable, reviewable, committable.
- **Match existing conventions.** Read project code before writing. No new patterns without discussion.
- **Simple Design (priority order):** passes tests → reveals intent → no duplication → fewest elements.
- **Boy Scout Rule.** When touching code, leave it cleaner. Always have passing tests before and after.
- **Human reviews everything.** You are the driver, not the decision-maker.

---

## Security-By-Design

All practices align with [OWASP Top 10 (2025)](https://owasp.org/Top10/2025/).

- Validate all inputs at system boundaries — never trust external data
- Use schema validation / strong typing (Pydantic, FluentValidation, Laravel Form Requests)
- Use parameterized queries exclusively — no string-concatenated SQL under any circumstances
- Never hardcode secrets; use environment variables or a secrets manager
- Never log sensitive data (passwords, tokens, PII)
- Bind HTTP services to `127.0.0.1` by default; use TLS for external communication
- Pin dependency versions; flag all new dependencies for review

---

## YAGNI

- Start with the simplest direct implementation that works
- Add abstractions only when complexity genuinely demands it — not in anticipation
- Create interfaces only when multiple concrete implementations exist or are imminent
- No plugin architecture, repository pattern, or event sourcing unless the problem requires it

---

## Code Quality Gates

| Metric | Target |
|---|---|
| Cyclomatic Complexity (method) | < 10 |
| Cyclomatic Complexity (class) | < 20 |
| Code Coverage (business logic) | ≥ 80% |
| Code Coverage (security-critical) | ≥ 95% |
| Maintainability Index | ≥ 70 |
| Code Duplication | ≤ 3% |

---

## Architecture & Design

- Group code by **feature/vertical slice**, not by technical layer
- Keep modules cohesive and loosely coupled
- Public APIs must have documentation comments
- Avoid deep inheritance hierarchies; prefer flat, composable structures

---

## Git Hygiene

- Commits must be atomic — one logical change per commit
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:`
- Pull requests require passing tests and quality gate checks before merge
- Do not commit generated files, build artifacts, or secrets

---

## Jira Issue Management

> **Optional** — adapt to your issue tracker (Linear, GitHub Issues, YouTrack, etc.) or remove this section entirely.

**Never autonomously move a Jira issue to `Done` or `Closed`.**

| Status | When to use |
|---|---|
| `To Do` | Not yet started |
| `In Progress` | Actively being worked on |
| `In Review` / `Code Review` | PR open; awaiting peer review |
| `Done` | QA verified — **human sets this only** |
| `Closed` | Abandoned/cancelled — **human sets this only** |

- When implementation is finished, transition to `In Review` and notify the user
- You **may** move `To Do` → `In Progress` when the user asks you to start work
- Add a comment summarising what was done on every status transition
- Passing tests ≠ Done. The user must QA and confirm before `Done` is set

---

## AI Behavior

### Accuracy Over Completion

Never invent libraries, function signatures, or syntax. If uncertain, say so explicitly. See **Prompting Patterns** above for the `[CANNOT COMPLETE]` escape hatch and `think:` triggers.

**Local model addendum:** When running on a local Ollama model — prioritize clarity over completeness. A shorter correct answer beats a longer partially-hallucinated one. Do not infer unstated requirements. Write `# VERIFY: [what to check]` rather than guessing function signatures.

---

## .NET / C# Standards

> Ground first: `search_knowledge(collection="dotnet")` + `search_code_examples(language="csharp")`.

Invariants:
- Target .NET 10 unless the project context specifies otherwise
- Enable nullable reference types; treat warnings as errors
- Prefer `async`/`await` end-to-end — never `.Result` or `.Wait()` on async methods
- Always propagate `CancellationToken` through async call chains
- Use `using` / `await using` for all `IDisposable`/`IAsyncDisposable` resources
- Follow vertical slice architecture: feature folders, not layer folders
- CQRS: commands mutate state, queries return data — never mix

---

## Python Standards

> Ground first: `search_knowledge(collection="python")` + `search_code_examples(language="python")`.

Invariants:
- Target Python 3.10+ unless constrained by the runtime environment
- Use type hints on all function signatures
- Prefer `pathlib.Path` over `os.path`
- Use `async def` / `asyncio` for I/O-bound work; `ProcessPoolExecutor` for CPU-bound
- Manage dependencies with `pyproject.toml` (not `setup.py`)
- Use `pydantic` v2 for data validation and settings management
- Prefer context managers for resource lifecycle — file handles, HTTP sessions, DB connections

---

## PHP Standards

> Ground first: `search_knowledge(collection="php")` + `search_code_examples(language="php")`.

Invariants:
- Use strict types (`declare(strict_types=1)`) in every file
- Type-hint all function parameters and return types
- Use Laravel Form Requests for input validation — never trust raw `$request->input()`
- Use Eloquent ORM or the Query Builder with bound parameters — never raw string-concatenated SQL
- Store secrets in `.env` (gitignored) and access via `config()` helpers, never `env()` directly in code
- Follow PSR-12 coding style; enforce with a linter (PHP-CS-Fixer / PHP_CodeSniffer)
- Prefer service classes and dependency injection over `static` facades in business logic

---

## JavaScript / TypeScript Standards

> Ground first: `search_knowledge(collection="javascript")` + `search_code_examples(language="javascript")` (or `"typescript"`).

Invariants:
- Prefer TypeScript over plain JavaScript for all new projects
- Enable `strict` mode in `tsconfig.json`; no `any` without explicit justification
- Use `const` by default; `let` only when reassignment is required; never `var`
- Prefer `async`/`await` over raw Promises or callback chains
- Sanitize all DOM output — never set `innerHTML` from untrusted data
- Use a bundler-managed environment (Vite, esbuild) — no hand-rolled script tags in new projects
- Pin `devDependencies` and `dependencies` exactly in `package.json`; audit with `npm audit`

---

## AI / ML Coding Standards

- Never hardcode model names as bare strings — use a config constant; models are deprecated without notice
- For Ollama/local LLM calls: note when behavior depends on a specific model family (tool calling support varies significantly)
- Prompt templates belong in versioned files, not f-strings scattered through application code

---

## AI-Generated Code Markers

Always wrap AI-generated code blocks with `<AI-Generated START>` / `<AI-Generated END>`
markers using the language-appropriate comment syntax (`//` for C#/JS/TS, `#` for Python/Shell,
`<!-- -->` for HTML/XML, `@* *@` for Razor, `--` for SQL).
