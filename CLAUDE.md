# CLAUDE.md

See [AGENTS.md](AGENTS.md) for full project conventions, skill structure, and agent formats.

## Quick Reference

- **59 skills** in `skills/<name>/SKILL.md` -- each with `references/` directory
- **22 agents** in `claude/agents/<name>.md` (Claude Code) | **19 agents** in `opencode/agents/<name>.md` (OpenCode)
- **Gold standard skill template**: `skills/architecture-review/SKILL.md`
- **Skill format**: 10 mandatory sections (Title, Philosophy, Principles, Workflow, State Block, Templates, Rules, Anti-Patterns, Error Recovery, Integration)
- **Agent format**: 10 mandatory sections (Title, Philosophy, Guardrails, Protocol, Self-Check, Error Recovery, Rules, Session Template, State Block, Completion)
