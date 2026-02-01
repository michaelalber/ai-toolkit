# AI Toolkit

A collection of AI coding agent skills and subagents for AI-assisted software development workflows.

Supports [Claude Code](https://claude.ai/code) and [OpenCode](https://opencode.ai/).

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

### Claude Code

```bash
# Skills
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/

# Agents
ln -sf /path/to/ai-toolkit/claude/agents/*.md ~/.claude/agents/
```

See [skills/README.md](skills/README.md) and [claude/agents/README.md](claude/agents/README.md) for details.

### OpenCode

```bash
# Skills (OpenCode supports Claude-compatible paths)
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/

# Agents
ln -sf /path/to/ai-toolkit/opencode/agents/*.md ~/.config/opencode/agents/
```

See [opencode/agents/README.md](opencode/agents/README.md) for details.

## Usage

Skills are invoked automatically based on context or can be triggered with slash commands:

```
/tdd-cycle     # Start a TDD session
/tdd-agent     # Autonomous TDD mode
/tdd-pair      # Collaborative TDD
/tdd-verify    # Audit TDD compliance
/jira-review   # Review a Jira issue
```

## Author

[Michael K Alber](https://github.com/michaelalber)

## License

MIT License - see [LICENSE](LICENSE) for details.
