# Subagents

Shareable Claude Code subagents for the AI Toolkit.

## Installation

Subagents must be installed in `~/.claude/agents/` to be available in Claude Code.

### Option 1: Symlink (Recommended)

Symlinks keep the agents in sync with the repository:

```bash
# Create the agents directory if it doesn't exist
mkdir -p ~/.claude/agents

# Symlink all subagent files
ln -sf /path/to/ai-toolkit/subagents/*.md ~/.claude/agents/
```

### Option 2: Copy

Copy files directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.claude/agents
cp /path/to/ai-toolkit/subagents/*.md ~/.claude/agents/
```

## Verification

After installation, verify the agents are available:

1. Open Claude Code
2. Run `/agents`
3. Your installed agents should appear in the list

## Skill Dependencies

Some subagents depend on skills from this repository. If a subagent references skills (like `tdd-cycle`, `tdd-implementer`, etc.), you must also install those skills:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink all skills
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/
```

## Available Subagents

| Agent | Description |
|-------|-------------|
| `tdd-agent` | Autonomous TDD with strict guardrails. Drives the complete RED-GREEN-REFACTOR cycle independently. |

## Usage

Once installed, subagents can be invoked by the Task tool or referenced in Claude Code conversations. For example:

```
Use tdd-agent to implement a Calculator.add method
```

The agent will operate autonomously, following TDD discipline with explicit state tracking and evidence-based verification.
