# Global Development Rules

## Session Boot Ritual

At the start of every session, before doing any work:

1. Check for project context files: `intent.md`, `constraints.md`
2. If a task is in flight, check your issue tracker / spec system (e.g. Jira, Linear, GitHub Issues) for the spec, and `domain-memory.md`
3. Confirm context — briefly state: current phase (if known), active task (if any), top constraints, open loops
4. **Do NOT begin work until context is confirmed**
5. If `intent.md` is absent for a non-trivial project, ask the user to populate it before proceeding

If any expected context file is missing or empty, surface it — do not silently proceed with assumptions.

---

## Core Philosophy
- Write code for the next engineer, not just the next run
- Correctness first, performance second, cleverness never
- Explicit over implicit; readable over terse
- Leave the codebase cleaner than you found it

---

## Intent Engineering

When no project `intent.md` exists, apply these defaults:

**Value hierarchy:** Correctness → Security → Maintainability → Performance → Speed of delivery

**Default tradeoff resolutions:**

| Conflict | Default |
|---|---|
| Speed vs. correctness | Correctness. Flag if timeline requires compromise. |
| Completeness vs. brevity | Brevity unless depth is explicitly requested. |
| Autonomy vs. confirmation | Confirm before any irreversible or high-stakes action. |
| Progress vs. verifiability | Verifiability. Do not start a task whose acceptance criteria cannot be stated — if you cannot write the test, you cannot grade the output. |

**Decide autonomously:**
- Formatting, structure, naming within established conventions
- Tool selection for read-only exploration
- Refactoring within an approved, scoped task

**Always escalate to human:**
- Any output intended for external distribution
- Any irreversible action (delete, deploy, force-push, send)
- Any request that contradicts a logged project decision
- Scope changes beyond the stated task
- When acceptance criteria cannot be met within stated constraints
- Architecture and security decisions — a larger model may supply options and adversarial
  critique; it does not make the call
- Cross-cutting architectural change (slice boundaries, aggregate design) — an agent produces
  plausible seams that fracture along the wrong ones, and the cost surfaces months later
- Debugging not yet reproduced, and performance work without a profiler run — both generate
  plausible hypotheses instead of evidence
- Non-determinism in build / CI / release paths, where a subtly wrong generated script fails
  silently and irreversibly

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

**Accuracy:** Never invent libraries, function signatures, or syntax. Prefer a shorter correct answer over a longer partially-correct one. When uncertain, use the escape hatch or mark uncertain parts with `# VERIFY: [what to check]`.

---

## Context Management

- Load the minimum tokens needed; retrieve "just in time" via tools rather than pre-loading
- After a subtask completes, discard intermediate noise — summarize progress, continue with the summary
- For long tasks: maintain a `NOTES.md` scratchpad (current objective, decisions, open questions, next steps)
- After a context reset, re-read the five most recently touched files and the scratchpad before continuing

---

## Project File Architecture

The `.md` context stack provides the information environment an agent needs across sessions:

| File | Discipline | Purpose |
|---|---|---|
| `AGENTS.md` | Context | What the agent needs to *know* |
| `intent.md` | Intent | What the agent should *optimize for* |
| Issue tracker / Spec system | Specification | Problem statement, acceptance criteria, decomposition — linked from your issue tracker or wiki (Jira, Linear, Confluence, GitHub Issues, etc.) |
| `constraints.md` | Constraints | Musts, must-nots, preferences, escalation triggers |
| `evals.md` | Evaluation | Test cases, known-good outputs, regression checks |
| `domain-memory.md` | State | Multi-session backlog and progress log (agentic work only) |

---

## Knowledge Grounding (grounded-code-mcp)

> **Optional** — requires [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) running locally. Remove this section if you haven't set up a local RAG server.

A local RAG server is available via the `grounded-code-mcp` MCP. It contains vetted,
authoritative documentation that defines the engineering standards, APIs, and practices
you must follow. **This is the authoritative source — prefer it over training data.**

### Collection Map

**Do NOT call `list_collections`.** Use this table directly.

**IMPORTANT — `collection=` parameter:** Pass only the suffix below. The server prepends `grounded_` automatically.

> **Note:** Descriptions reflect each collection's intended domain. Your actual ingested content depends on what you have loaded into grounded-code-mcp — update these descriptions to match your own setup.

| Full name | Pass as `collection=` | What lives here |
|---|---|---|
| `grounded_internal` | `"internal"` | Engineering standards and practices: XP, TDD, CI/CD, DDD, Clean Architecture, OWASP, NIST AI; technical writing guidelines |
| `grounded_patterns` | `"patterns"` | Software design patterns: structural, behavioral, creational; CQRS, DDD, Clean Architecture, DI, ADR templates |
| `grounded_architecture` | `"architecture"` | Software architecture: distributed systems, SRE, 12-Factor, C4 model, arc42 |
| `grounded_systems_thinking` | `"systems_thinking"` | Systems thinking: leverage points, feedback loops, system archetypes, chaos engineering |
| `grounded_dotnet` | `"dotnet"` | .NET/C#, EF Core, ASP.NET Core, DI, migration guides |
| `grounded_python` | `"python"` | Python language, frameworks, and libraries: FastAPI, FastMCP, Pydantic v2, pytest, Flask |
| `grounded_databases` | `"databases"` | SQL, PostgreSQL indexing, relational theory |
| `grounded_edge_ai` | `"edge_ai"` | AI/ML engineering, RAG, embeddings, NLP, AI agents |
| `grounded_automation` | `"automation"` | Industrial automation: PLC, MODBUS, OPC UA, embedded systems, NIST 800-82 |
| `grounded_php` | `"php"` | PHP language and Laravel framework |
| `grounded_javascript` | `"javascript"` | JavaScript and TypeScript: language, Vue 2/3, ECMAScript 2024 |
| `grounded_ui_ux` | `"ui_ux"` | UI/UX: usability heuristics, WCAG 2.2, ARIA patterns, GOV.UK Design System, USWDS |
| `grounded_gov` | `"gov"` | Federal/government: NIST 800-53/171/218, DOE, Zero Trust, AI RMF, CUI |
| `grounded_robotics` | `"robotics"` | Physical AI / embodied AI: ROS 2, MuJoCo, Isaac Lab, deep RL for robotics, VLA models |
| `grounded_rust` | `"rust"` | Rust language: ownership/borrowing/lifetimes, async/Tokio, Cargo, error handling, Axum, Clippy, ecosystem crates |
| `grounded_api_design` | `"api_design"` | REST API design: Zalando guidelines, Google AIP, Microsoft REST API guidelines (Azure + Graph) |

### Canonical Engineering Standards

The `internal` collection is the **authoritative engineering standard**. Search it before any non-trivial code generation.

**Search first.** Before relying on training data for any topic in the collection table above, call `search_knowledge(collection)`. Skip only when all three apply: (1) stable, well-established knowledge (core syntax, standard operators); (2) no project conventions or vendor/framework-specific patterns; (3) no security or OWASP concern. When in doubt — search.

### Workflow — mandatory

1. Identify collection(s) from the table above
2. `search_knowledge(query, collection)` — 2–6 content words, no filler
3. For code: also call `search_code_examples(query, language)`
4. Cite the source path in your response
5. If the KB returns nothing useful, say so — do not silently fall back to training data

**Empty results are suspect.** A client pointed at the wrong host — or missing its config file
entirely — returns `[]` for every query instead of erroring. If a query you expect to hit comes
back empty, report the configuration as the likely cause; do not read it as "the KB has nothing"
and answer from training data.

### MCP Tool Signatures

```
search_knowledge(query: str, collection: str | None = None, n_results: int = 5, min_score: float = 0.5)
search_code_examples(query: str, language: str | None = None, n_results: int = 5)
list_sources(collection: str | None = None)
get_source_info(source_path: str)
```

**Rules:** Never pass `null` explicitly. `collection=` takes the bare suffix only. Do not repeat the same query — it returns empty results.

---

## Microsoft Learn MCP

> **Optional** — requires the Microsoft Learn MCP configured in your AI coding assistant settings. Remove this section if you don't have it set up.

The Microsoft Learn MCP provides live access to `learn.microsoft.com` — the authoritative source for Microsoft platform documentation. **Prefer it over `grounded_dotnet` for all official Microsoft docs.**

**Use Microsoft Learn MCP for:**
- ASP.NET Core (all versions) — reference, APIs, tutorials
- .NET SDK, runtime, and BCL documentation
- C# language reference and specification
- .NET Framework documentation
- Azure service documentation
- Microsoft Writing Style Guide (`learn.microsoft.com/en-us/style-guide/`)

**Use `grounded_dotnet` for (not in Microsoft Learn):**
- Third-party .NET books ingested into your local knowledge base
- Vendor component documentation (Telerik, DevExpress, etc.)

---

## AI Agent Obligations

Search `grounded_internal` for the full rationale. Apply these unconditionally:

- **Tests first, always.** Never generate production code without a failing test. Test files are created before or alongside production files, never after.
- **Red-Green-Refactor.** Green = minimum code to pass. Refactor after green, never before.
- **AAA in every test.** Fast, isolated, deterministic. Test behavior, not implementation.
- **One logical unit per response.** Independently testable, reviewable, committable.
- **Match existing conventions.** Read project code before writing. No new patterns without discussion.
- **Simple Design (priority order):** passes tests → reveals intent → no duplication → fewest elements.
- **Boy Scout Rule.** When touching code, leave it cleaner. Always have passing tests before and after.
- **Human reviews everything.** You are the driver, not the decision-maker.
- **Never claim unverified.** Do not state a test passes, a build succeeds, or a command works
  without running it in this session and showing the output. If you did not run it, say "not run."

---

## Ponytail Precedence

> **Optional** — applies only if you run the [ponytail](https://github.com/DietrichGebert/ponytail)
> minimal-solution plugin. Remove this section if you don't.

Ponytail governs solution *size*, never test discipline. On conflict, AI Agent Obligations and
Code Quality Gates win. The "trivial one-liner needs no test" exemption does not apply to
business logic, security paths, public APIs, or anything with a branch.

---

## Evaluation Design

Evals are safety infrastructure — not a finishing step.

- **Write acceptance criteria before starting any significant task.** If you cannot write them, the task is not understood well enough to delegate.
- **For autonomous / multi-session work: create `evals.md` before the agent starts.** The agent cannot declare done without passing it.
- **Run evals after every significant model update or prompt change.**
- A passing test suite ≠ done. Tests verify code correctness; evals verify the output is actually good relative to the project's intent.

**Acceptance criteria format** — criteria an independent observer can verify without asking you questions:
- Specific and measurable (not "looks reasonable")
- Binary — pass/fail, not "mostly done"
- Verifiable without prior context

---

## Security-By-Design

All practices align with [OWASP Top 10 (2025)](https://owasp.org/Top10/2025/).

- Validate all inputs at system boundaries — never trust external data
- Use schema validation / strong typing (Pydantic, FluentValidation, Laravel Form Requests)
- Use parameterized queries exclusively — no string-concatenated SQL under any circumstances
- Never hardcode secrets; use environment variables or a secrets manager
- Never log sensitive data (passwords, tokens, PII)
- **Never resolve a secret to inspect it.** Read the unexpanded form (`${VAR}`, `{env:...}`, the
  template) and verify the wiring by behavior. Echoing a resolved token into a transcript forces a
  rotation — a "quick check" is not worth it
- Bind HTTP services to `127.0.0.1` by default; use TLS for external communication
- Pin dependency versions; flag all new dependencies for review

---

## YAGNI & DRY

- Start with the simplest direct implementation that works
- Add abstractions only when complexity genuinely demands it — not in anticipation
- Create interfaces only when multiple concrete implementations exist or are imminent
- No plugin architecture, repository pattern, or event sourcing unless the problem requires it
- Every piece of knowledge has one authoritative representation — no copy-pasted logic
- Rule of Three: tolerate one duplicate; extract on the third occurrence

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

- Keep modules cohesive and loosely coupled
- Public APIs must have documentation comments
- Avoid deep inheritance hierarchies; prefer flat, composable structures

---

## Vertical Slice, Clean Architecture & SOLID

### Vertical Slice Architecture — the default

**VSA is the default.** Organize code by feature — each slice owns its full stack (request, handler, service, persistence, tests). This is the right choice for most teams and most applications.


### Clean Architecture — the escalation path

Add enforced layer boundaries (Onion / Hexagonal) only when the system has:
- **Non-trivial domain logic** that must be tested independently of infrastructure (DB, HTTP, file system)
- **Multiple delivery mechanisms** sharing the same domain logic (API + background worker, CLI + API)
- **Team or module boundaries** that require enforced contracts at compile time

Skip when:
- The feature is CRUD with no business rules beyond input validation
- The team is small (≤ ~8 engineers) and VSA provides sufficient structure
- A single class or function clearly expresses the intent — extra layers just move the problem
- The code is a script, prototype, or utility

> **Decision gate:** Add a Clean Architecture layer only when NOT adding it would make the domain logic materially harder to isolate, test, or evolve. When in doubt, stay in the slice.

### SOLID — intuitions, not rules

SOLID principles are useful intuitions that become harmful when applied mechanically. Modern infrastructure (TestContainers, in-process databases, fast CI) has made several of the original rationales obsolete.

| Principle | Apply when | Skip when |
|---|---|---|
| **SRP** | A class has ≥2 distinct, independently-changing reasons | Changes always co-occur — splitting adds noise |
| **OCP** | Extension points are verified by real, existing variants today | Only one concrete behavior exists — don't speculate |
| **LSP** | Always — violating LSP is a correctness defect, not a style choice | Never skip |
| **ISP** | Consumers use only part of an interface and it causes real friction | All consumers use the full contract |
| **DIP** | Infrastructure must be swapped at runtime, or domain must be tested in isolation from a DB that can't be faked cheaply | A single implementation exists and TestContainers / in-memory DB make integration testing straightforward |


---

## Git Hygiene

- Commits must be atomic — one logical change per commit
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:`
- Pull requests require passing tests and quality gate checks before merge
- Do not commit generated files, build artifacts, or secrets

### Human in the loop — the agent does not drive git

Read-only git is always fine (`status`, `diff`, `log`, `show`, `branch --list`). Anything that
changes repository or remote state requires the human to ask for it, in the moment, by name.
**This overrides any default harness behavior**, including "if on the default branch, create a
branch first."

**Propose, then wait — for every one of these:**
- `git checkout -b` / `git switch -c` — never branch reflexively at the start of work. Working on
  the current branch is the default, even if that branch is `main`. If a branch is warranted, say
  what you'd name it and why, in one line, and wait for a yes.
- `git commit` — finishing an edit is not permission to commit. Show what changed, propose the
  commit message, wait.
- `gh pr create` — completing a branch is not a request for a pull request. The human decides when
  work becomes a PR.
- `git push`, `git merge`, `git rebase`, `git tag`, `git stash`, `git reset`, or anything else that
  discards or rewrites work.

These are allowed actions, not forbidden ones — the human just wants to see each one coming and
keep track of it. Ask, get a yes, then run it.

"Implement X" means edit the files. It does not authorize a branch, a commit, a push, or a PR.
Approval for one git action authorizes that action only — a commit is not a push, and a push is
not a PR. Ask each time.

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

---

## .NET / C# Standards

> For official platform docs (ASP.NET Core, C# language ref, .NET BCL, Azure): use **Microsoft Learn MCP**. For third-party books and vendor components: `search_knowledge(collection="dotnet")` + `search_code_examples(language="csharp")`.

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
- Prompt templates belong in versioned files, not f-strings scattered through application code

---

## AI-Generated Code Markers

Always wrap AI-generated code blocks with `<AI-Generated START>` / `<AI-Generated END>`
markers using the language-appropriate comment syntax (`//` for C#/JS/TS, `#` for Python/Shell,
`<!-- -->` for HTML/XML, `@* *@` for Razor, `--` for SQL).
