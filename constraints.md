# AI Toolkit — Constraints
<!-- Discipline 4: Specification Engineering — Primitive 3: Constraint Architecture
     Framework: Four Prompt Disciplines & Five Primitives (Nate B. Jones, v2026.03.2)

     PROJECT-LEVEL FILE — supplements claude/global/CLAUDE.md and opencode/global/AGENTS.md.
     Global standards (security, commit format, code quality) apply unconditionally.
     This file adds constraints specific to contributing to this repository. -->

---

## Must Do

- Read `AGENTS.md` (root), `intent.md`, and this file before beginning any task.
- Follow the 10-section skill template exactly — use `skills/architecture-review/SKILL.md` as the gold standard.
- Follow the 10-section agent template exactly — both Claude Code and OpenCode versions must be present.
- Ensure every new skill has a `references/` directory with at least 2 supporting files.
- Ensure every new state block XML tag is unique across all skills and agents before committing.
- Keep `claude/agents/` and `opencode/agents/` versions in sync — behavior must be identical, formats differ.
- Update skill/agent counts in `AGENTS.md` (root) and `README.md` whenever a skill or agent is added or removed.
- When modifying `project-templates/`, verify the change is backward-compatible with existing user copies or document the breaking change.

---

## Must NOT Do

- Do not leave placeholder text (e.g., "TODO", "[fill in]") in any committed skill or agent file.
- Do not reuse a state block XML tag already in use by another skill or agent.
- Do not add a skill to `claude/agents/` without a matching `opencode/agents/` entry (unless the agent is explicitly marked single-platform with a documented reason).
- Do not modify `claude/global/CLAUDE.md` or `opencode/global/AGENTS.md` without explicit human approval — these are installed globally and affect all user projects.
- Do not move a skill or agent without updating all cross-references in `AGENTS.md`, `README.md`, and any skills that reference it in their Integration section.
- Do not call PyTorch's evaluation mode method in Python code examples — the security hook triggers on this string. Use `model.train(False)` instead.
- Do not create a local `spec.md` — task specs live in Jira / Confluence.

---

## Preferences

- Prefer editing an existing skill over creating a new one when the use case overlaps significantly.
- Prefer adding to a `references/` directory over embedding long reference content inline in `SKILL.md`.
- Prefer the grounded-code-mcp knowledge base over training data for language idioms, framework APIs, and security patterns.
- When both Claude Code and OpenCode versions need updating, update them in the same commit.

---

## Escalate Rather Than Decide

- Any proposal to change the 10-section template structure itself.
- Adding a new skill suite or agent category not currently in `AGENTS.md`.
- Any change to `claude/global/` or `opencode/global/` files.
- Any change to install scripts (`scripts/`) that affects the installation target paths.
- Breaking Claude Code / OpenCode agent parity intentionally.
- Any change to `project-templates/` that would invalidate copies already in users' project roots.

---

## File Architecture Constraints

This project has two levels of context files. Agents must not confuse them:

| Level | Claude Code | OpenCode | Scope |
|-------|-------------|----------|-------|
| **Global** | `claude/global/CLAUDE.md` | `opencode/global/AGENTS.md` | All projects on the user's machine |
| **Project** | `CLAUDE.md` (root) | `AGENTS.md` (root) | This repository only |

- Global files define universal standards — do not duplicate their content in the project-level files.
- Project-level files define what is specific to this repository — the template structure, agent formats, and toolkit conventions.
- `project-templates/` contains templates for users to copy into their own projects — these are neither global nor project-level files for this repo.
