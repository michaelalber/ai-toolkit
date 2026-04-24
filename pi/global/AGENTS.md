# Global Development Rules

## Security Scanning (Snyk)

> **Optional** — requires Snyk CLI + MCP tool. Remove this section if you don't use Snyk.

- Always run `snyk_code_scan` for new first-party code generated in a Snyk-supported language.
- If security issues are found in newly introduced or modified code or dependencies, fix them using the Snyk results context.
- Rescan after fixing to confirm the issues are resolved and no new ones were introduced.
- Repeat until no new issues are found.

---

## Session Boot Ritual

At the start of every session, before doing any work:

1. Check for project context files: `intent.md`, `constraints.md`
2. If a task is in flight, check the Jira issue or Confluence page for the spec, and `domain-memory.md`
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

**Accuracy:** Never invent libraries, function signatures, or syntax. When uncertain, use the escape hatch above.

---

## Context Management

- Load the minimum tokens needed; retrieve "just in time" via tools rather than pre-loading
- After a subtask completes, discard intermediate noise — summarize progress, continue with the summary
- For long tasks: maintain a `NOTES.md` scratchpad (current objective, decisions, open questions, next steps)
- After a context reset, re-read the five most recently touched files and the scratchpad before continuing

---

## Project File Architecture

| File | Discipline | Purpose |
|---|---|---|
| `AGENTS.md` | Context | What the agent needs to *know* |
| `intent.md` | Intent | What the agent should *optimize for* |
| Jira / Confluence | Specification | Problem statement, acceptance criteria, decomposition |
| `constraints.md` | Constraints | Musts, must-nots, preferences, escalation triggers |
| `evals.md` | Evaluation | Test cases, known-good outputs, regression checks |
| `domain-memory.md` | State | Multi-session backlog and progress log (agentic work only) |
| `SYSTEM.md` | Prompt | Pi-specific: replaces or appends to the default system prompt |

---

## AI Agent Obligations

Apply these unconditionally:

- **Tests first, always.** Never generate production code without a failing test. Test files are created before or alongside production files, never after.
- **Red-Green-Refactor.** Green = minimum code to pass. Refactor after green, never before.
- **AAA in every test.** Fast, isolated, deterministic. Test behavior, not implementation.
- **One logical unit per response.** Independently testable, reviewable, committable.
- **Match existing conventions.** Read project code before writing. No new patterns without discussion.
- **Simple Design (priority order):** passes tests → reveals intent → no duplication → fewest elements.
- **Boy Scout Rule.** When touching code, leave it cleaner. Always have passing tests before and after.
- **Human reviews everything.** You are the driver, not the decision-maker.

---

## Evaluation Design

- **Write acceptance criteria before starting any significant task.**
- **For autonomous / multi-session work: create `evals.md` before the agent starts.**
- **Run evals after every significant model update or prompt change.**
- A passing test suite ≠ done. Tests verify code correctness; evals verify the output is good relative to intent.

**Acceptance criteria format** — criteria an independent observer can verify:
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

## Vertical Slice Architecture — the default

Organize code by feature — each slice owns its full stack (request, handler, service, persistence, tests).

```
features/
  create-order/
    CreateOrderCommand   ← handler, validator, tests co-located
  get-order/
    GetOrderQuery        ← handler, tests co-located
```

Add enforced layer boundaries (Onion / Hexagonal) only when the system has non-trivial domain logic that must be tested independently of infrastructure, multiple delivery mechanisms sharing the same domain, or team boundaries requiring enforced contracts at compile time.

---

## Git Hygiene

- Commits must be atomic — one logical change per commit
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:`
- Pull requests require passing tests and quality gate checks before merge
- Do not commit generated files, build artifacts, or secrets

---

## Language Standards

### .NET / C#
- Target .NET 10 unless constrained otherwise
- Enable nullable reference types; treat warnings as errors
- Prefer `async`/`await` end-to-end — never `.Result` or `.Wait()`
- Always propagate `CancellationToken` through async call chains

### Python
- Target Python 3.10+
- Use type hints on all function signatures
- Use `pydantic` v2 for data validation and settings management
- Manage dependencies with `pyproject.toml`

### JavaScript / TypeScript
- Prefer TypeScript; enable `strict` mode in `tsconfig.json`
- Use `const` by default; `let` only when reassignment required; never `var`
- Prefer `async`/`await` over raw Promises or callbacks

---

## AI-Generated Code Markers

Always wrap AI-generated code blocks with `<AI-Generated START>` / `<AI-Generated END>` markers using the language-appropriate comment syntax.

---

## Key Learnable Tricks

**Chain-of-thought triggers** — prefix your prompt to change how the model reasons:
- `think: <question>` — reasons before answering
- `think hard: <question>` — deep analysis with edge cases
- `think step: <question>` — numbered breakdown

**Escape hatch** — when the model can't complete accurately, it responds:
> `[CANNOT COMPLETE]: <reason>` then a skeleton with `# VERIFY:` comments

**NOTES.md scratchpad** — for long tasks, tell the model to maintain a `NOTES.md` with current objective, decisions, and next steps. After a context reset, it re-reads the scratchpad before continuing.

**SYSTEM.md** — Pi-specific: place a `SYSTEM.md` in your project root to replace or append to Pi's default system prompt with project-specific identity or context.
