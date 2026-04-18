# OpenCode Global Config

## What this is

`AGENTS.md` is OpenCode's global instruction file. It applies to every project — OpenCode reads it automatically at the start of each session.

`opencode.json` controls providers, MCP servers, permissions, and agent temperature settings.

## Installation

```bash
# Copy to OpenCode's global config directory
cp AGENTS.md ~/.opencode/AGENTS.md
cp opencode.json ~/.opencode/opencode.json
```

Then edit both files — replace `YOUR_USERNAME` with your actual username.

## Which AGENTS.md to use?

| File | Use when |
|---|---|
| `AGENTS.md` | Standard setup — no RAG server |
| `AGENTS-with-grounded-code-mcp.md` | You have [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) running locally |

Copy whichever applies to `~/.opencode/AGENTS.md`.

## What's in AGENTS.md

- **Core Philosophy** — engineering values baked into every session
- **Prompting Patterns** — prefix triggers (`think:`, `think hard:`, `think step:`) and the `[CANNOT COMPLETE]` escape hatch
- **AI Agent Obligations** — TDD discipline enforced via prompt
- **Security-By-Design** — OWASP-aligned guardrails
- **Code Quality Gates** — cyclomatic complexity, coverage targets
- **Language Standards** — .NET, Python, PHP, TypeScript invariants
- **Optional sections** — Snyk, grounded-code-mcp, Jira (marked inline; remove what you don't use)

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
- **Ollama / local models** — commented-out provider block; uncomment and adjust context limits to match your GPU VRAM
- **MCP servers** — Snyk, grounded-code-mcp, Semgrep all commented out with install hints; enable what you use
