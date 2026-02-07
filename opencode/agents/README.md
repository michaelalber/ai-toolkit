# OpenCode Agents

OpenCode-compatible agents for the AI Toolkit.

## Installation

Agents must be installed in `~/.config/opencode/agents/` to be available in OpenCode.

### Option 1: Symlink (Recommended)

Symlinks keep the agents in sync with the repository:

```bash
# Create the agents directory if it doesn't exist
mkdir -p ~/.config/opencode/agents

# Symlink all agent files
ln -sf /path/to/ai-toolkit/opencode/agents/*.md ~/.config/opencode/agents/

# Remove the README.md symlink
rm -f ~/.config/opencode/agents/README.md
```

### Option 2: Copy

Copy files directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.config/opencode/agents
cp /path/to/ai-toolkit/opencode/agents/*.md ~/.config/opencode/agents/
```

**Note:** When copying, exclude this README to avoid confusion:

```bash
cp /path/to/ai-toolkit/opencode/agents/tdd-agent.md ~/.config/opencode/agents/
```

### Project-Local Installation

For project-specific agents:

```bash
mkdir -p .opencode/agents
ln -sf /path/to/ai-toolkit/opencode/agents/*.md .opencode/agents/

# Remove the README.md symlink
rm -f .opencode/agents/README.md
```

## Verification

After installation, verify the agents are available:

1. Open OpenCode
2. Press `Tab` to cycle through available agents, or check the agent list
3. The `tdd-agent` should appear as a subagent option

## Available Agents

| Agent | Mode | Description |
|-------|------|-------------|
| `tdd-agent` | subagent | Autonomous TDD with strict guardrails. Drives the complete RED-GREEN-REFACTOR cycle independently. |

## Skills Installation (Required for Full Functionality)

The tdd-agent loads skills on-demand for detailed guidance. **Skills must be installed** for the agent to access reference material like implementation patterns, code smells, and refactoring catalogs.

OpenCode supports Claude-compatible skill paths. Install skills to one of these locations:

```bash
# OpenCode native path
mkdir -p ~/.config/opencode/skills
ln -sf /path/to/ai-toolkit/skills/* ~/.config/opencode/skills/
rm -f ~/.config/opencode/skills/README.md

# Or Claude-compatible path (also supported by OpenCode)
mkdir -p ~/.claude/skills
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/
rm -f ~/.claude/skills/README.md
```

The agent will use the `skill` tool to load:
- `tdd-cycle` - Phase transitions and state management
- `tdd-implementer` - Minimal implementation patterns (Python, TypeScript, .NET)
- `tdd-refactor` - Code smell detection and refactoring catalog
- `tdd-verify` - Compliance scoring and anti-patterns

## Differences from Claude Code Version

| Feature | Claude Code | OpenCode |
|---------|-------------|----------|
| Location | `~/.claude/agents/` | `~/.config/opencode/agents/` |
| Tools format | `tools: Read, Edit, Write...` | `tools:` with `read: true` style |
| Skill injection | `skills: [name, ...]` in frontmatter | On-demand via `skill` tool |
| Mode field | N/A | `mode: subagent` |

The OpenCode version has core TDD knowledge inlined in the agent prompt, with instructions to load detailed skill content on-demand using the `skill` tool.

## Usage

Once installed, invoke the tdd-agent as a subagent:

```
Use tdd-agent to implement a Calculator.add method
```

The agent will operate autonomously, following TDD discipline with explicit state tracking and evidence-based verification.

## Configuration

You can customize the agent by editing the frontmatter:

```yaml
---
description: Autonomous TDD with strict guardrails
mode: subagent
model: anthropic/claude-sonnet-4-20250514  # Change model here
tools:
  read: true
  edit: true
  write: true
  bash: true
  glob: true
  grep: true
---
```

See [OpenCode Agents Documentation](https://opencode.ai/docs/agents/) for all available options.
