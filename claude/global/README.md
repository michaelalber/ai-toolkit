# Claude Global Config

## What this is

`CLAUDE.md` is Claude Code's global instruction file. It applies to **every project** you open — Claude reads it automatically at the start of each session.

`settings.json` installs deterministic hooks (credential stop, shell-exec-chain stop, bash audit log, post-write build/lint gates) and wires up the status line. The hook bodies live in `hooks/` as standalone scripts — `settings.json` only references them.
`settings.local.json` controls Claude Code's permissions and tool allowlist.
`statusline.sh` renders token count and context window usage below the prompt (e.g. `57.5k (6.0%)`).

## Installation

Two steps — the script handles per-session content (agents, skills, commands), and you copy the global config manually so you can edit `YOUR_USERNAME` before it takes effect.

```bash
# 1. Install agents, skills, and commands (idempotent — re-run to refresh)
bash ../../scripts/install-claude.sh

# 2. Copy the global config (one-time; edit YOUR_USERNAME after)
cp CLAUDE.md ~/.claude/CLAUDE.md
cp settings.json ~/.claude/settings.json
cp settings.local.json ~/.claude/settings.local.json

# 3. Install the hook scripts referenced by settings.json (they must be executable)
mkdir -p ~/.claude/hooks
cp hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

Then edit `~/.claude/settings.local.json` — replace `YOUR_USERNAME` with your actual username.

The hooks require `jq` (they read tool input as JSON on stdin). The post-write gates are
best-effort: they no-op silently when `dotnet` or `ruff`/`uvx` is not installed.

**Verify the hooks are live.** A misconfigured hook fails silently — it never runs and nothing
warns you — so confirm rather than assume:

```bash
# Bash audit hook: run any Bash command in a session, then
tail -1 ~/.claude/logs/bash-audit.log   # should show the command you just ran

# Shell-exec-chain guard: runnable self-check (exits non-zero on any failure)
bash hooks/tests/guard-bash-exec.test.sh                                     # repo copy
bash hooks/tests/guard-bash-exec.test.sh ~/.claude/hooks/guard-bash-exec.sh  # installed copy

# Installed hooks match this repo? Silent output = in sync; any diff = re-copy.
diff -r --exclude=tests claude/global/hooks ~/.claude/hooks
```

Run the `diff` after every `git pull` — hooks are copied, not symlinked, so a fixed guard in the
repo does nothing until you re-copy it. `--exclude=tests` skips the repo-only test directory,
leaving silence as the pass condition.

The exec-chain check covers both directions: real chains (pipe-to-shell, `find -exec bash`) must
be blocked, and quoted look-alikes — a grep pattern, a `sed` substitution using pipe delimiters,
prose about the guard itself — must not be. The second half is the one that matters in practice:
a guard that fires during ordinary editing trains you to ignore it. `hooks/tests/` is a
subdirectory precisely so `cp hooks/*.sh` never copies a test into a live hooks directory.

> **Known limitation.** The guard strips single- and double-quoted spans before matching, but not
> backticks (which are real command substitution — stripping them would hide genuine chains) and
> not heredoc bodies. So a command whose heredoc contains a pipe-to-shell *example* still trips it.
> Write those through `Write`/`Edit` rather than a shell heredoc.

For the credential guard, ask Claude to write a file assigning a quoted dummy secret to a
variable named `api_key`. The write must be **blocked**. If it succeeds, the hook is not wired up.

> Note: the credential guard inspects the content being written, so it also fires on
> documentation and test fixtures containing credential-shaped literals. That is intended —
> it fails closed. Write such literals by hand, or stage them outside a guarded tool call.

> `statusline.sh` is copied automatically by `install-claude.sh` in step 1 — no manual copy needed.

## What's in CLAUDE.md

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
- **Language Standards** — .NET, Python, PHP, TypeScript invariants
- **Optional sections** — Snyk, grounded-code-mcp, Jira (marked inline; remove what you don't use)

---

## The Four Disciplines & Five Primitives

The global instruction file implements Disciplines 1–3 of a four-level prompt engineering framework. Discipline 4 requires project-level files.

| # | Discipline | What it does | Where it lives |
|---|---|---|---|
| 1 | Prompt Craft | Clear instructions, output format, chain-of-thought | Your prompt |
| 2 | Context Engineering | Information environment the agent operates in | `CLAUDE.md` |
| 3 | Intent Engineering | What the agent should optimize for | `intent.md` |
| 4 | Specification Engineering | Autonomous execution blueprint | `spec.md`, `constraints.md`, `evals.md` |

### Diagnose first: Task or Job?

**Task** — context provided upfront; a well-crafted prompt suffices. Examples: refactor this function, write tests for this module.

**Job** — requires organizational context, decisions held across sessions, judgment calls. Examples: implement a feature end-to-end, run a dark-factory build loop. Jobs need the full `.md` stack.

If you can't write acceptance criteria for it, it's a job — not a task.

### Agent Architecture Selection

Before writing a spec, identify which architecture applies:

| Architecture | Description | When to use |
|---|---|---|
| Coding harness | Single agent, human as quality gate | Task-level work |
| Dark factory | Autonomous spec-to-eval loop; human at spec and eval only | Project-scale software |
| Auto research | LLM optimizer against a metric; needs dataset + measurable target | Metric-shaped problems |
| Orchestration | Role-specialized agents with handoff contracts | Multi-domain workflows |

Diagnostic: is the problem **software-shaped** (needs working code or documents) or **metric-shaped** (needs a rate or measure optimized)?

### Project File Architecture

For non-trivial or multi-session projects, drop these files into the project root:

```
project/
├── intent.md          ← Discipline 3: what the agent optimizes for
├── spec.md            ← Discipline 4: problem statement + acceptance criteria + decomposition
├── constraints.md     ← Discipline 4: musts, must-nots, preferences, escalation triggers
├── evals.md           ← Discipline 4: test cases, known-good outputs, regression checks
└── domain-memory.md   ← Agent state: backlog + progress log (multi-session only)
```

### File Templates

<details>
<summary><strong>intent.md</strong></summary>

```markdown
# Intent

## Primary Goal
<!-- What is this project ultimately trying to achieve? Write as an outcome, not a task. -->

## Value Hierarchy
<!-- Rank these or describe the tradeoff resolution order. -->
- [Highest priority]
- [Second priority]
- [Third priority]

## Tradeoff Rules
| Conflict | Resolution |
|---|---|
| Speed vs. quality | [e.g., Default to quality. Flag if timeline requires compromise.] |
| Completeness vs. brevity | [e.g., Prefer brevity unless depth is requested.] |

## Decision Boundaries

### Decide Autonomously
- [e.g., Formatting and structure choices]

### Escalate to Human
- [e.g., Any output sent externally]
- [e.g., Decisions that affect scope or timeline]

## What "Good" Looks Like
<!-- Describe a top-quality output for this project. -->
- [Quality dimension 1]
- [Quality dimension 2]

## Anti-Patterns
<!-- What would a technically correct but wrong output look like? -->
- [e.g., Recommendations that optimize for speed at the expense of correctness]
```

</details>

<details>
<summary><strong>constraints.md</strong></summary>

```markdown
# Constraints

## Must Do
- Load and confirm intent.md and constraints.md before every session.
- Read spec.md before beginning any in-flight task.
- Write acceptance criteria before delegating any significant subtask.
- Confirm understanding before executing any irreversible action.
- [PROJECT-SPECIFIC MUSTS]

## Must NOT Do
- Do not begin a task that has no acceptance criteria.
- Do not re-litigate decisions already logged in intent.md.
- Do not exceed the scope in spec.md without explicit approval.
- [PROJECT-SPECIFIC PROHIBITIONS]

## Preferences
- Prefer asking one clarifying question over assuming.
- Prefer flagging a problem before executing a workaround.
- [PROJECT-SPECIFIC PREFERENCES]

## Escalate Rather Than Decide
- Any output intended for external distribution.
- Any action that conflicts with a logged decision.
- Any request where acceptance criteria cannot be met within stated constraints.
- [PROJECT-SPECIFIC ESCALATION TRIGGERS]
```

</details>

<details>
<summary><strong>spec.md</strong></summary>

```markdown
# Active Specification

## Problem Statement
<!-- Self-contained. State the problem as if the agent has never seen your project.
Describe: the situation, the gap, and why it matters. -->

## Desired Outcome
<!-- The RESULT, not the steps. What does the world look like when this is done? -->

## Acceptance Criteria
- [ ] [Criterion 1 — specific, measurable, binary]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Decomposition
| # | Subtask | Input | Output | Pass Condition |
|---|---------|-------|--------|----------------|
| 1 | | | | |
| 2 | | | | |

## Inputs Available
-

## Out of Scope
-

---
Created: YYYY-MM-DD | Status: [Draft / Active / Complete]
```

</details>

<details>
<summary><strong>evals.md</strong></summary>

```markdown
# Evals

## Eval Philosophy
Evals are safety infrastructure. Write them before the agent starts. The agent cannot
declare done without passing evals. Run after every significant model update.

## Test Cases

### Test Case 1: [Task Type]
- **Input / Prompt:** [The exact input used]
- **Known-Good Output:** [What a correct, high-quality response looks like]
- **Pass Criteria:** [Specific, binary checks]
- **Last Run:** YYYY-MM-DD | **Result:** [Pass / Fail]

## Taste Rules
| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | | | |

## Rejection Log
### YYYY-MM-DD — [Task Description]
- **What was generated:**
- **What was wrong:**
- **Rule extracted:**
```

</details>

<details>
<summary><strong>domain-memory.md</strong> (multi-session agentic work only)</summary>

```markdown
# Domain Memory

## Project Goal
<!-- Single clear statement. Read on every boot. -->

## Feature / Task Backlog
| ID  | Task | Status | Pass Condition | Notes |
|-----|------|--------|----------------|-------|
| T01 | | ❌ Failing | | |

*Status: ❌ Failing | ✅ Passing | 🔄 In Progress | ⏸ Blocked | ➡ Deferred*

## Scaffolding
- How to run:
- How to test:

## Progress Log
### Run: YYYY-MM-DD HH:MM
- **Session intent:**
- **Items completed:**
- **Items failed:**
- **Next steps:**

## Worker Boot Ritual
1. Read this file completely.
2. Read constraints.md.
3. Summarize: passing items, failing items, open blockers.
4. Select ONE failing item (lowest ID).
5. Work on it. Test it. Do NOT move on until it passes or is Blocked.
6. Update backlog status and append a progress log entry. Exit.
```

</details>

### Bootstrap Prompt

Run this at the start of any non-trivial project to populate `intent.md` and `constraints.md`:

```
Read all .md files in this project. Then interview me — ask up to 5 targeted questions
to fill in intent.md and constraints.md for this specific project. Dig into tradeoffs,
escalation rules, and what "good" looks like. Don't ask obvious questions. After I answer,
update both files. Do not begin any project work yet.
```

### Spec-Building Prompt

Run this when starting a task that warrants full delegation:

```
Read CLAUDE.md, intent.md, and constraints.md. Then interview me about this task:
[TASK DESCRIPTION]. Ask about implementation, edge cases, tradeoffs, and constraints.
Keep asking until you have enough to write a complete spec.md. Then write it.
Do not begin execution until I approve the spec.
```

---

## Optional dependencies

| Section | What you need |
|---|---|
| Snyk security scanning | [Snyk CLI](https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli) + MCP tool |
| grounded-code-mcp (RAG grounding) | [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) running locally |
| Jira issue management | Jira MCP or API access |

Remove any section you don't use — it costs tokens every session.

## Key learnable tricks

These are non-obvious patterns you can start using immediately:

**Chain-of-thought triggers** — prefix your prompt to change how Claude reasons:
- `think: <question>` — reasons before answering
- `think hard: <question>` — deep analysis with edge cases
- `think step: <question>` — numbered breakdown

**Escape hatch** — when Claude can't complete accurately, it responds:
> `[CANNOT COMPLETE]: <reason>` then a skeleton with `# VERIFY:` comments

**NOTES.md scratchpad** — for long tasks, tell Claude to maintain a `NOTES.md` with current objective, decisions, and next steps. After a context reset, it re-reads the scratchpad before continuing.

**AI-Generated markers** — generated code is wrapped in `<AI-Generated START>` / `<AI-Generated END>` so you can always identify it in diffs.
