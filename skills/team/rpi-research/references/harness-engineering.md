# Harness Engineering Reference

Source: HumanLayer's "Skill Issue" blog post (March 2026) and
Viv Trivedy's harness engineering posts.

## What is Harness Engineering?

```
coding agent = AI model(s) + harness
```

The harness is everything outside the model that shapes its behavior:
system prompt, tools/MCPs, context injection, sub-agents, hooks, and
back-pressure mechanisms.

Harness engineering is the practice of configuring these surfaces to
systematically improve agent reliability. It's a subset of context
engineering focused specifically on coding agent configuration.

## The Six Configuration Surfaces

### 1. AGENTS.md / CLAUDE.md (System Prompt Extension)
- Injected into every session's system prompt
- Highest leverage point — for better or worse
- **Keep it under 60 lines.** Universally applicable rules only.
- **Don't auto-generate it.** Hand-craft for best results.
- **Use progressive disclosure**: point to skills/references instead of
  inlining everything

### 2. Skills (Instruction Modules / Progressive Disclosure)
- Loaded on-demand, not always in context
- Each skill should have < 40 instructions
- Perfect for phase-specific prompts (research, plan, implement)
- Skills are "the coding agent equivalent of a function call"

### 3. MCP Servers (Tools)
- Extend agent capabilities beyond file I/O and bash
- Tool descriptions consume system prompt budget
- **Fewer is better**: every tool description is an instruction the agent
  must process without benefit if unused
- If a CLI exists in training data, prefer the CLI over an MCP server
  (GitHub CLI > GitHub MCP, Docker CLI > Docker MCP)
- Disable MCP servers you're not actively using in this session

### 4. Sub-Agents (Context Firewalls)
- Isolate discrete tasks in separate context windows
- Parent agent orchestrates; child agents execute
- Prevents intermediate noise from accumulating
- Key pattern: smart model orchestrates, dumb model executes,
  smart model verifies

### 5. Hooks (Deterministic Control Flow)
- Pre/post execution hooks for automated checks
- Linting, formatting, test runs after changes
- Build verification before committing
- "Anytime the agent makes a mistake, engineer a hook so it never
  makes that mistake again"

### 6. Back-Pressure Mechanisms
- Token budget limits per phase
- Verification gates between phases
- Human approval checkpoints for high-risk operations
- Context window utilization monitoring (aim for 40-60%)

## Instruction Budget

Count your total instructions across all surfaces:

| Surface | Typical Count |
|---------|--------------|
| Agent harness system prompt (Claude Code/OpenCode) | ~50 |
| Your AGENTS.md (count imperative sentences) | variable |
| Active skills (count instructions per skill loaded) | ~40/skill |
| MCP tool descriptions (tools × ~2 instructions each) | variable |

**Target: < 150 total for frontier thinking models. Less for smaller models.**

The budget is shared — loading 4 skills at once may push you over the limit.
Use skills selectively: load only the skill for the current phase.

## Context Window Utilization Zones

After a typical session, check how much of the context window is used:

| Utilization | Zone | Guidance |
|------------|------|----------|
| < 40% | Under-used | Good. Room for complex tasks. |
| 40–60% | Optimal | Sweet spot per HumanLayer findings. |
| 60–80% | Degrading | Consider splitting into sub-agents. |
| > 80% | Dumb Zone | Model stops following instructions reliably. Compact now. |

**Frequent Intentional Compaction**: actively summarize and reset context
within a session to stay in the 40–60% zone. RPI phase isolation is the
structural version of this — each phase starts with a clean context.

## Practical Audit for Your Setup

### MCP Server Audit
For each connected MCP server, ask:
1. Am I using this in most sessions? → Keep
2. Is there a CLI that does the same thing? → Prefer CLI, disable MCP
3. How many tools does it expose? → If >10, consider a wrapper CLI
4. Does it duplicate another server's functionality? → Remove duplicate

### AGENTS.md Audit
1. Count the imperative sentences (rules, constraints, requirements)
2. If count > 40: extract into skills and reference them instead
3. Every rule in AGENTS.md fires in every session — be selective

## Applying to This Stack (OpenCode + Claude Sonnet via GitHub Copilot)

### General Projects
- AGENTS.md is the primary harness config point
- Layered AGENTS.md files: root + per-project
- Skills via ai-toolkit repo
- MCP stack: audit Atlassian, Telerik, MS Learn, Semgrep, grounded-code-mcp
  for per-session relevance — disable what you're not using today

### For .NET Projects
- AGENTS.md should include: build commands, test commands, coding conventions
- Skills to load: RPI phase skill for current phase, `ef-migration-manager` when
  migrations are involved, `dotnet-vertical-slice` when adding new slices
- MCP: Atlassian for ticket context, grounded-code-mcp for codebase RAG
- Consider disabling MS Learn MCP when not actively looking up APIs

### For Legacy .NET Framework 4.8 Projects
- Separate AGENTS.md for legacy patterns (no vertical slices)
- Research phase is EXTRA critical — legacy migration patterns are unusual
- Keep Telerik MCP active (heavy UI framework usage)
- `harness-engineering.md` insight: unusual legacy patterns mean the model's
  training data may be wrong — grounded-code-mcp with the relevant collection
  is essential

## Key Takeaway

Every time your agent fails, ask: "Is this a model problem or a
configuration problem?" In HumanLayer's experience across dozens of
enterprise projects, it's almost always configuration.
