# RPI / HumanLayer Resource Index

Essential reading for the RPI workflow and harness engineering methodology.

## Reading Order (Recommended)

### Foundational (Start Here)

1. **12 Factor Agents** — The theoretical framework
   - Blog: https://www.humanlayer.dev/blog/12-factor-agents
   - Repo: https://github.com/humanlayer/12-factor-agents
   - Key takeaway: LLMs are stateless functions. Context window = only lever.

2. **Writing a Good CLAUDE.md** — Harness config best practices
   - Blog: https://www.humanlayer.dev/blog/writing-a-good-claude-md
   - Key takeaway: Under 60 lines. No auto-generation. Progressive disclosure.

### Core Methodology

3. **Advanced Context Engineering for Coding Agents** — The RPI deep-dive
   - Repo: https://github.com/humanlayer/advanced-context-engineering-for-coding-agents
   - File: `ace-fca.md` is the main document
   - Key takeaway: Research → Plan → Implement with "thoughts" as persistent artifacts.

4. **Skill Issue: Harness Engineering** (March 2026) — Latest synthesis
   - Blog: https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents
   - Key takeaway: Sub-agents as context firewalls. CLI wrappers > MCP servers.
     Skills for progressive disclosure. AGENTS.md instruction budget matters.

### Practical Implementation

5. **Goose RPI Tutorial** — Best step-by-step walkthrough of RPI in practice
   - Tutorial: https://block.github.io/goose/docs/tutorials/rpi/
   - Key takeaway: Real example of research → plan → implement with actual output
     files. Shows the "course correction" pattern during research.

6. **HumanLayer `.claude/commands/`** — Actual production slash commands
   - Research: https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/research_codebase.md
   - Plan: https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/create_plan.md
   - Implement: https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/implement_plan.md
   - Commands dir: https://github.com/humanlayer/humanlayer/tree/main/.claude/commands

7. **riptide-rpi** — Publishable RPI skills for skill marketplaces
   - Repo: https://github.com/humanlayer/riptide-rpi
   - Smithery: https://smithery.ai/skills/humanlayer/rpi-setup-humanlayer
   - LobeHub: https://lobehub.com/skills/humanlayer-riptide-rpi-rpi-setup-humanlayer

### Talks & Interviews

8. **Heavybit Interview** (March 2026) — RPI → QRSPI evolution, team scaling
   - Article: https://www.heavybit.com/library/article/whats-missing-to-make-ai-agents-mainstream

9. **Dev Interrupted Podcast** (February 2026) — Ralph loops, RPI, agentic economics
   - Podcast: https://linearb.io/dev-interrupted/podcast/dex-horthy-humanlayer-rpi-methodology-ralph-loop
   - Blog companion: https://linearb.io/blog/dex-horthy-humanlayer-rpi-methodology-ralph-loop

10. **YC Talk** (August 2025) — Original "No Vibes Allowed" presentation
    - Referenced on: https://www.humanlayer.dev/

11. **Maven Course: Advanced Context Engineering** — Paid deep-dive course
    - https://maven.com/p/6cbf01/advanced-context-engineering

### Adjacent Resources

12. **awesome-claude-code** — Community-curated list of skills, hooks, commands
    - https://github.com/hesreallyhim/awesome-claude-code

13. **claudelayer** — Sub-agent recursion patterns with Claude Code
    - https://github.com/humanlayer/claudelayer

14. **HumanLayer SDK** — Human-in-the-loop approval workflows for agents
    - Docs: https://www.humanlayer.dev/docs/introduction
    - YC page: https://www.ycombinator.com/companies/humanlayer

15. **CodeLayer** — HumanLayer's IDE built on Claude Code (open source, Apache 2)
    - https://github.com/humanlayer/humanlayer (main repo)
    - Install: `brew install --cask --no-quarantine humanlayer/humanlayer/codelayer`
    - Note: macOS only currently

## Key Concepts Glossary

| Term | Definition | Source |
|------|-----------|--------|
| Context Engineering | Superset of prompt engineering; systematic management of everything that goes into an LLM's context window | Dex Horthy, 12 Factor Agents (April 2025) |
| Harness Engineering | Subset of context engineering focused on coding agent configuration surfaces | Viv Trivedy, HumanLayer (2026) |
| RPI | Research → Plan → Implement workflow for complex brownfield tasks | HumanLayer (2025) |
| QRSPI | Questions → Research → Design → Structure → Plan → Worktree → Implement (7-phase RPI evolution) | HumanLayer (2025-2026) |
| Context Firewall | Sub-agent pattern that isolates task context to prevent noise accumulation | HumanLayer (2026) |
| Instruction Budget | ~150 instructions that frontier LLMs can reliably follow; shared across system prompt, AGENTS.md, tools, and user messages | HumanLayer (2026) |
| Dumb Zone | >80% context window utilization where instruction-following degrades significantly | HumanLayer (2025) |
| Thoughts | Git-backed directory of persistent research, plans, and design artifacts that survive across sessions | HumanLayer (2025) |
| Frequent Intentional Compaction | Actively summarizing and resetting context within a session to stay in the 40–60% utilization sweet spot | HumanLayer (2025) |
| Ralph Loop | Simple autonomous implementation loop: execute → verify → fix → repeat. Named after a hackathon meme. Key insight: simplicity beats complex multi-agent orchestration | Community / HumanLayer (2025) |

## When to Apply RPI

### Good Fit
- Brownfield features in an established codebase
- Changes touching 5+ files
- Features requiring understanding of existing patterns before planning
- Any task where a wrong assumption in planning would require significant rework

### Poor Fit — Skip RPI, Work Directly
- Greenfield projects (no codebase to research)
- Single-file changes with clear requirements
- Bug fixes with a clear reproduction path
- Formatting, linting, or mechanical refactors
- Tasks where you already fully understand the codebase area

The cost of RPI (3 phases, 3 sessions) is worth it when the cost of rework
from a wrong assumption exceeds ~30 minutes. For small tasks, it's overhead.
