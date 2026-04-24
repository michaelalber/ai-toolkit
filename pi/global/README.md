# Pi Global Config

## What this is

`AGENTS.md` is Pi's global instruction file. Pi loads it automatically from `~/.pi/agent/` at the start of each session, along with any `AGENTS.md` found in the current directory and parent directories.

`SYSTEM.md` is a per-project file that replaces or appends to Pi's default system prompt. Copy it into your project root — Pi picks it up automatically.

## Installation

```bash
# Copy to Pi's global agent directory
cp AGENTS.md ~/.pi/agent/AGENTS.md
```

Or use the install script from the repo root:

```bash
bash scripts/install-pi.sh
```

For per-project system prompt customization:

```bash
# Copy to your project root
cp SYSTEM.md /path/to/your-project/SYSTEM.md
```

Then edit `SYSTEM.md` — remove sections you don't use (every token counts).

## What's in AGENTS.md

- **Session Boot Ritual** — context confirmation gate before any work begins
- **Core Philosophy** — engineering values baked into every session
- **Intent Engineering** — universal value hierarchy, tradeoff defaults, escalation boundaries
- **Prompting Patterns** — prefix triggers (`think:`, `think hard:`, `think step:`) and the `[CANNOT COMPLETE]` escape hatch
- **Context Management** — just-in-time loading, NOTES.md scratchpad
- **Project File Architecture** — the `.md` context stack for non-trivial projects
- **AI Agent Obligations** — TDD discipline enforced via prompt
- **Evaluation Design** — acceptance criteria and evals as safety infrastructure
- **Security-By-Design** — OWASP-aligned guardrails
- **Code Quality Gates** — cyclomatic complexity, coverage targets
- **Language Standards** — .NET, Python, TypeScript invariants
- **Optional sections** — Snyk (marked inline; remove if unused)

## What's in SYSTEM.md

A concise system prompt template covering session boot, engineering principles, coding discipline, security guardrails, and escalation rules. Customize for your project and place in the project root.

Pi reads `SYSTEM.md` per-project, making it useful for:
- Injecting project-specific identity ("You are working on a medical records API — apply HIPAA guardrails")
- Overriding default Pi behavior for a specific codebase
- Adding project-specific escalation rules

---

## Pi AGENTS.md Loading Order

Pi discovers and merges `AGENTS.md` files from multiple locations (most specific wins on conflicts):

| Priority | Location |
|----------|----------|
| 1 (highest) | Current working directory |
| 2 | Parent directories (walking up) |
| 3 (lowest) | `~/.pi/agent/` (global) |

This means global standards in `~/.pi/agent/AGENTS.md` apply everywhere, and project-level `AGENTS.md` files can override or extend them without touching the global file.

---

## The Four Disciplines & Five Primitives

The global instruction file implements Disciplines 1–3 of a four-level prompt engineering framework. Discipline 4 requires project-level files.

| # | Discipline | What it does | Where it lives |
|---|---|---|---|
| 1 | Prompt Craft | Clear instructions, output format, chain-of-thought | Your prompt |
| 2 | Context Engineering | Information environment the agent operates in | `AGENTS.md` |
| 3 | Intent Engineering | What the agent should optimize for | `intent.md` |
| 4 | Specification Engineering | Autonomous execution blueprint | `spec.md`, `constraints.md`, `evals.md` |

### Project File Architecture

For non-trivial or multi-session projects, drop these files into the project root:

```
project/
├── AGENTS.md          ← Project-level context (Pi auto-discovers this)
├── SYSTEM.md          ← Pi system prompt override (Pi-specific)
├── intent.md          ← Discipline 3: what the agent optimizes for
├── constraints.md     ← Discipline 4: musts, must-nots, preferences, escalation triggers
├── evals.md           ← Discipline 4: test cases, known-good outputs, regression checks
└── domain-memory.md   ← Agent state: backlog + progress log (multi-session only)
```

**Minimum set for a coding harness:** `AGENTS.md` + `intent.md` + `constraints.md` + `evals.md`.

---

## Optional Dependencies

| Section | What you need |
|---|---|
| Snyk security scanning | [Snyk CLI](https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli) |
| grounded-code-mcp (RAG grounding) | [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) running locally |

Remove any section you don't use — it costs tokens every session.

## Key Learnable Tricks

**Chain-of-thought triggers** — prefix your prompt to change how Pi reasons:
- `think: <question>` — reasons before answering
- `think hard: <question>` — deep analysis with edge cases
- `think step: <question>` — numbered breakdown

**Escape hatch** — when Pi can't complete accurately, it responds:
> `[CANNOT COMPLETE]: <reason>` then a skeleton with `# VERIFY:` comments

**NOTES.md scratchpad** — for long tasks, tell Pi to maintain a `NOTES.md` with current objective, decisions, and next steps. After a context reset, it re-reads the scratchpad before continuing.

**AI-Generated markers** — generated code is wrapped in `<AI-Generated START>` / `<AI-Generated END>` so you can always identify it in diffs.
