# OpenCode Global Config

## What this is

`AGENTS.md` is OpenCode's global instruction file. It applies to every project — OpenCode reads it automatically at the start of each session.

`opencode.json` controls providers, MCP servers, permissions, and agent temperature settings.

## Installation

```bash
# Copy to OpenCode's global config directory
cp AGENTS.md ~/.config/opencode/AGENTS.md
cp opencode.json ~/.config/opencode/opencode.json

# Copy commands (user-invoked slash commands)
mkdir -p ~/.config/opencode/commands
cp -r ../../opencode/commands/* ~/.config/opencode/commands/
```

Then edit `opencode.json` — replace `YOUR_USERNAME` with your actual username.

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
- **Language Standards** — .NET, Python, PHP, TypeScript invariants
- **Optional sections** — Snyk, Knowledge Grounding (grounded-code-mcp), Jira (marked inline; remove what you don't use)

---

## The Four Disciplines & Five Primitives

The global instruction file implements Disciplines 1–3 of a four-level prompt engineering framework. Discipline 4 requires project-level files.

| # | Discipline | What it does | Where it lives |
|---|---|---|---|
| 1 | Prompt Craft | Clear instructions, output format, chain-of-thought | Your prompt |
| 2 | Context Engineering | Information environment the agent operates in | `AGENTS.md` |
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
Read AGENTS.md, intent.md, and constraints.md. Then interview me about this task:
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

**Chain-of-thought triggers** — prefix your prompt to change how the model reasons:
- `think: <question>` — reasons before answering
- `think hard: <question>` — deep analysis with edge cases
- `think step: <question>` — numbered breakdown

**Escape hatch** — when the model can't complete accurately, it responds:
> `[CANNOT COMPLETE]: <reason>` then a skeleton with `# VERIFY:` comments

**NOTES.md scratchpad** — for long tasks, tell the model to maintain a `NOTES.md` with current objective, decisions, and next steps. After a context reset, it re-reads the scratchpad before continuing.

**AI-Generated markers** — generated code is wrapped in `<AI-Generated START>` / `<AI-Generated END>` so you can always identify it in diffs.

## opencode.json highlights

- **Permission model** — sensitive files (`.env`, keys, certs) are denied by default; safe read-only git commands are pre-allowed
- **Ollama / local models** — commented-out provider block; see the full Ollama guide below
- **MCP servers** — Snyk, grounded-code-mcp, Semgrep all commented out with install hints; enable what you use

---

## Local inference with Ollama

### Required server configuration

Set these before starting `ollama serve`. Without them you will hit the most common failure: silent 4K context truncation that causes tool calls to silently fail.

```bash
export OLLAMA_FLASH_ATTENTION=1      # required for KV cache quantization
export OLLAMA_KV_CACHE_TYPE=q8_0    # halves KV cache VRAM; negligible quality loss
export OLLAMA_KEEP_ALIVE=30m        # keep model loaded between sessions
export OLLAMA_NUM_PARALLEL=1        # single-user: prevents VRAM contention
```

To persist via systemd (Linux):

```bash
sudo systemctl edit ollama
# Add under [Service]:
# Environment="OLLAMA_FLASH_ATTENTION=1"
# Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
# Environment="OLLAMA_KEEP_ALIVE=30m"
# Environment="OLLAMA_NUM_PARALLEL=1"
sudo systemctl restart ollama
```

### The context window trap (most common failure)

Ollama defaults to **4,096 tokens** of context on GPUs with less than 24 GB VRAM. OpenCode injects tool schemas + system prompt + conversation history into every request — this easily exceeds 4K before the model generates a single token. The result: tool calls silently fail or the model refuses to act.

**Three levers that must all agree:**

| Setting | Where | What it controls |
|---|---|---|
| `OLLAMA_KV_CACHE_TYPE=q8_0` | Ollama server env | Quantizes KV cache — enables larger context within VRAM |
| `num_ctx` in Modelfile | Ollama model | Sets the model's actual context window |
| `options.num_ctx` in opencode.json | OpenCode per-request | Overrides Ollama's default per-request (required — Ollama default is 4096) |
| `limit.context` in opencode.json | OpenCode accounting | Internal token budget — must equal `options.num_ctx` |

`limit.context` alone does **not** set Ollama's context window. If `options.num_ctx` is absent, Ollama uses 4K regardless of what `limit.context` says. Always set both.

Also: if `limit.output` is not set, OpenCode defaults `max_tokens` to 32,000. Local models reject this when their context window is smaller. Always set `limit.output` explicitly.

### Model selection by VRAM

Only models with native tool calling work in OpenCode. Verified as of 2025–2026.

**8 GB VRAM** (e.g., RTX 3070 Mobile, RX 6700M) — with `OLLAMA_KV_CACHE_TYPE=q8_0`:

| Model | VRAM @ 8K ctx | Strengths |
|---|---|---|
| `qwen3:8b` | ~6.3 GB | Best overall code quality sub-10B (HumanEval 76.0) — recommended |
| `qwen2.5-coder:7b` | ~5.9 GB | Code-specialized; highest HumanEval for pure coding tasks |
| `granite3.3:8b` | ~6.5 GB | IBM; designed specifically for agentic/tool-heavy workflows |
| `llama3.1:8b` | ~6.3 GB | Proven stability; broad community testing |

**6 GB VRAM** (e.g., RTX 3060 Mobile, RX 6600M) — with `OLLAMA_KV_CACHE_TYPE=q8_0`:

| Model | VRAM | Notes |
|---|---|---|
| `qwen3:4b` | ~3.5 GB @ 8K | Recommended — best quality/VRAM ratio on 6 GB |
| `qwen2.5-coder:7b` | ~5.0 GB @ 4K | Tight; keep `num_ctx` ≤ 4096 |
| `granite3.3:2b` | ~2.2 GB @ 16K | Lightest tool-capable; good for background/compaction |

### VRAM quick reference

For 7–8B Q4_K_M models (representative of Llama 3.1 8B, Qwen3 8B, etc.). Includes ~0.8 GB overhead. Leave ≥ 1 GB headroom for CUDA workspace during generation.

| Context | KV FP16 | KV Q8_0 | Total (FP16) | Total (Q8_0) |
|---|---|---|---|---|
| 4,096 | 0.5 GB | 0.25 GB | 5.4 GB | 5.1 GB |
| 8,192 | 1.0 GB | 0.5 GB | 6.4 GB | 5.9 GB |
| 16,384 | 2.0 GB | 1.0 GB | 8.4 GB | 7.4 GB |
| 32,768 | 4.0 GB | 2.0 GB | 12.4 GB | 9.4 GB |

`OLLAMA_KV_CACHE_TYPE=q8_0` effectively moves you one column to the left — doubling your usable context at the same VRAM budget.

### Modelfile template (coding assistant)

```dockerfile
FROM qwen3:8b   # or qwen3:4b for 6 GB

# Match num_ctx to options.num_ctx in opencode.json
PARAMETER num_ctx 8192
PARAMETER num_predict 2048    # cap output; prevents context exhaustion in long tool chains
PARAMETER temperature 0.15    # deterministic code output
PARAMETER top_p 0.85
PARAMETER repeat_penalty 1.1

SYSTEM """
You are a coding assistant integrated into a terminal IDE.

Rules:
- Use available tools. Read files before editing or referencing them.
- Be surgical. Change only what is needed. Do not rewrite working code.
- Be concise. No preamble. Respond with the action or answer.
- One step at a time. Complete a step, report the result, then continue.
- When stuck: report the tool name, the error, and what you tried.
- Never invent file paths, function signatures, or library APIs.
"""
```

```bash
# Create the model
ollama create qwen3-8b-coding -f Modelfile

# Reference in opencode.json as:
# "qwen3-8b-coding": { "name": "...", "tools": true, "limit": {...}, "options": { "num_ctx": 8192 } }
```

### Prompting small models effectively

These patterns improve reliability in 7B–14B models acting as coding agents:

- **`think:` triggers work best at ≥ 7B.** On 3–4B models they can produce verbose reasoning that exhausts the output budget. Use sparingly on smaller models.
- **Constrain output format in prompts.** Small models hallucinate less with explicit output shape: *"show only the changed block, not the entire file."*
- **"Read before assuming"** in the system prompt measurably reduces hallucinated file paths and function names — include it in your Modelfile SYSTEM block.
- **Suppress reasoning for tool-only tasks.** For pure file-editing tasks, telling the model *"execute tool calls directly, explain after the result"* improves reliability vs. extended chain-of-thought.

### Known issues

| Issue | Cause | Fix |
|---|---|---|
| Tool calls silently fail | Ollama 4K default context overflows on first request | Set `options.num_ctx` ≥ 8192 in opencode.json |
| `max_tokens` error on generation | `limit.output` unset → defaults to 32K | Always set `limit.output` explicitly |
| Context compaction overflows | Compaction agent uses same model at same context limit | Increase `num_ctx` or compact manually before context fills |
| Qwen 3.5 tool calling broken | Known regression (Ollama issue #14493) | Check Ollama release notes before upgrading Qwen 3.x |
