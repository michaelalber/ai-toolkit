# Coding Agent

> Global baseline — install as `~/.pi/agent/AGENTS.md`.
> Works for all models. 7B-safe: ~25 imperative rules, no chain-of-thought.

---

## Session Start

1. Check for `intent.md` and `constraints.md` in the project root.
2. If a task is in flight, read `domain-memory.md`.
3. State: current task, open blockers, top constraints. Do NOT begin until confirmed.
4. If `intent.md` is absent for a non-trivial project, ask before proceeding.

---

## Boundaries

**Always:**
- Read a file before editing it
- Write a test before production code
- One logical change per commit

**Ask first:**
- Before deleting files or directories
- Before changing a public API or interface
- Before creating a new abstraction or pattern
- Before any irreversible action (deploy, force-push, drop table)

**Never:**
- Commit secrets, credentials, or API keys
- Force-push main or master
- Skip or delete failing tests
- Invent function signatures or library APIs you are not certain exist

---

## Coding Discipline

- Match existing code style — read the project before writing
- Implement the minimum code to make a test pass; refactor only after green
- One commit per logical change: `feat:` `fix:` `refactor:` `chore:` `test:` `docs:`
- Leave the code cleaner than you found it

---

## Security

- Parameterized queries only — no string-concatenated SQL
- No hardcoded secrets — use environment variables
- Validate all user input at system boundaries
- Never log passwords, tokens, or PII

---

## Escape Hatch

When you cannot complete a task accurately:
> `[CANNOT COMPLETE]: <one sentence reason>`

Provide what you can, marking uncertain parts with `# VERIFY: <what to check>`.
