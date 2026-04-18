# Claude Global Config

## What this is

`CLAUDE.md` is Claude Code's global instruction file. It applies to **every project** you open — Claude reads it automatically at the start of each session.

`settings.local.json` controls Claude Code's permissions and tool allowlist.

## Installation

```bash
# Copy to Claude's global config directory
cp CLAUDE.md ~/.claude/CLAUDE.md
cp settings.local.json ~/.claude/settings.local.json
```

Then edit both files — replace `YOUR_USERNAME` with your actual username.

## What's in CLAUDE.md

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

**Chain-of-thought triggers** — prefix your prompt to change how Claude reasons:
- `think: <question>` — reasons before answering
- `think hard: <question>` — deep analysis with edge cases
- `think step: <question>` — numbered breakdown

**Escape hatch** — when Claude can't complete accurately, it responds:
> `[CANNOT COMPLETE]: <reason>` then a skeleton with `# VERIFY:` comments

**NOTES.md scratchpad** — for long tasks, tell Claude to maintain a `NOTES.md` with current objective, decisions, and next steps. After a context reset, it re-reads the scratchpad before continuing.

**AI-Generated markers** — generated code is wrapped in `<AI-Generated START>` / `<AI-Generated END>` so you can always identify it in diffs.
