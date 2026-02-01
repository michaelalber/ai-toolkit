# AI Toolkit

A collection of Claude Code skills for AI-assisted software development workflows.

## Skills

### TDD Suite

A comprehensive set of skills for Test-Driven Development with AI assistance. Based on Kent Beck's TDD principles and the 12 Test Desiderata.

| Skill | Description |
|-------|-------------|
| `tdd-cycle` | Orchestrates the RED-GREEN-REFACTOR cycle. Maintains phase state and enforces transitions. |
| `tdd-implementer` | GREEN phase specialist. Implements minimal code to make failing tests pass using Fake It, Obvious Implementation, or Triangulation strategies. |
| `tdd-refactor` | REFACTOR phase specialist. Safely improves code structure while keeping tests green. Includes code smell detection and refactoring recipes. |
| `tdd-agent` | Fully autonomous TDD mode. AI drives all phases with strict guardrails and explicit verification at each step. |
| `tdd-pair` | Collaborative TDD with role-based pairing. Supports Ping-Pong, Navigator, and Teaching modes. |
| `tdd-verify` | Audits code for TDD compliance. Detects anti-patterns, scores test quality, and generates compliance reports. |

### Jira Review

| Skill | Description |
|-------|-------------|
| `jira-review` | Automatically reviews Jira issues for implementation readiness. Parses acceptance criteria, scores complexity, and recommends clarification or planning mode when needed. |

## Installation

Copy the desired skill directories from `skills/` into your Claude Code skills location:
- User skills: `~/.claude/skills/`
- Project skills: `.claude/skills/` in your repository

## Usage

Skills are invoked automatically based on context or can be triggered with slash commands:

```
/tdd-cycle     # Start a TDD session
/tdd-agent     # Autonomous TDD mode
/tdd-pair      # Collaborative TDD
/tdd-verify    # Audit TDD compliance
/jira-review   # Review a Jira issue
```

## License

MIT License - see [LICENSE](LICENSE) for details.
