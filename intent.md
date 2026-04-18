# AI Toolkit — Intent
<!-- Discipline 3: Intent Engineering (v2026.03.2)
     Framework: Four Prompt Disciplines & Five Primitives (Nate B. Jones)

     PROJECT-LEVEL FILE — supplements claude/global/CLAUDE.md and opencode/global/AGENTS.md.
     This file tells the agent what to OPTIMIZE FOR when working on this repository.
     Project context (what to know) lives in the root CLAUDE.md / AGENTS.md. -->

---

## Agent Architecture

**This project uses:** Coding harness

**Reason:** Contributors work task-by-task with human review at each step. Skills and agents are discrete, independently testable units — no multi-session autonomous execution is needed.

---

## Primary Goal

Enable software development teams to immediately install and use high-quality AI coding agent skills and autonomous agents that improve the correctness, consistency, and velocity of AI-assisted development workflows.

---

## Values (What We Optimize For)

1. **Quality** — every skill and agent must be correct, complete, and follow the 10-section template exactly
2. **Consistency** — conventions are enforced uniformly; no one-offs without documented rationale
3. **Usability** — skills and agents must work out of the box; no configuration guessing
4. **Completeness** — Claude Code and OpenCode versions stay in sync; references directories are populated
5. **Speed of delivery** — lowest priority; never trade quality or consistency for it

---

## Tradeoff Rules

| Conflict | Resolution |
|---|---|
| Speed vs. quality | Quality wins. A skill that ships fast but breaks the template creates debt for every future contributor. |
| Completeness vs. brevity | Completeness wins for skill/agent bodies. Brevity wins for frontmatter descriptions and comments. |
| New feature vs. fixing existing | Fix existing first. A broken skill is worse than a missing one. |
| Claude Code vs. OpenCode parity | Keep both versions. If parity is temporarily broken, document it explicitly in the agent file. |

---

## Decision Boundaries

### Decide Autonomously

- Formatting and structure within the 10-section template
- Selecting which references to include in a `references/` directory
- Wording of skill descriptions and trigger phrases
- File naming within established conventions

### Escalate to Human

- Adding a new skill suite or agent category not currently represented
- Changing the 10-section template structure itself
- Breaking Claude Code / OpenCode parity intentionally
- Modifying install scripts or global context files (`claude/global/` or `opencode/global/`)
- Any change to `project-templates/` that would invalidate existing user copies

---

## What "Good" Looks Like

A good output for this project:

- A new skill that passes all 10-section completeness checks, has 2+ reference files, and has a unique state block XML tag
- An agent that exists in both `claude/agents/` and `opencode/agents/` with consistent behavior and correct frontmatter format for each platform
- A project-template file that a developer can copy into a new project and fill in within 15 minutes, without needing to read external documentation

---

## Anti-Patterns (What Bad Looks Like)

- A skill with placeholder sections left unfilled ("TODO: add anti-patterns")
- An agent added to `claude/agents/` without a matching `opencode/agents/` version (unless explicitly noted as single-platform)
- A state block XML tag that duplicates one already in use
- A `references/` directory with fewer than 2 files
- A project-template file that references concepts from the global files without explaining them locally

---

## Persistent Decisions

<!-- Architectural and product decisions that are settled — agent must not re-litigate them.
     Canonical list lives in AGENTS.md. Add entries there; cross-reference here only if
     a decision directly affects intent or tradeoff resolution. -->

See `AGENTS.md` § Persistent Decisions.

---

## Open Loops

<!-- Unresolved questions the agent should surface proactively.
     Canonical list lives in AGENTS.md. -->

See `AGENTS.md` § Open Loops.
