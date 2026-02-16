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

**Note:** When copying, exclude this README to avoid confusion. Copy only the `.md` agent files you need.

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
3. Your installed agents should appear as subagent options

## Available Agents

### Development Workflow

| Agent | Mode | Description |
|-------|------|-------------|
| `tdd-agent` | subagent | Autonomous TDD with strict guardrails. Drives the complete RED-GREEN-REFACTOR cycle independently. |
| `code-review-agent` | subagent | Autonomous code review — security, correctness, performance, maintainability, and style analysis. |
| `test-generation-agent` | subagent | Autonomous test generation using TDD patterns with proper naming and mocking. |
| `documentation-agent` | subagent | Autonomous documentation sync — staleness detection, XML docs, README sync, ADR maintenance. |
| `dependency-audit-agent` | subagent | Autonomous dependency auditing — vulnerability scanning, license compliance, upgrade paths. |

### DevOps / Infrastructure

| Agent | Mode | Description |
|-------|------|-------------|
| `migration-orchestrator` | subagent | Semi-autonomous migration orchestration with approval gates for EF Core and .NET migrations. |
| `environment-health-agent` | subagent | Autonomous environment health monitoring for Docker, services, and connections. |

### Edge AI / IoT

| Agent | Mode | Description |
|-------|------|-------------|
| `model-optimization-agent` | subagent | Autonomous model optimization — quantization, conversion, and benchmarking for edge. |
| `sensor-anomaly-agent` | subagent | Autonomous sensor anomaly detection — statistical outliers, drift, and recalibration. |
| `fleet-deployment-agent` | subagent | Semi-autonomous fleet deployment — canary, staged rollout, and rollback for edge fleets. |

### Knowledge / RAG

| Agent | Mode | Description |
|-------|------|-------------|
| `research-agent` | subagent | Autonomous research — multi-source investigation, credibility scoring, and structured briefings. |
| `context-builder-agent` | subagent | Autonomous context assembly — git changes, ADR matching, and dependency mapping. |

### Meta / Orchestration

| Agent | Mode | Description |
|-------|------|-------------|
| `task-decomposition-agent` | subagent | Meta-orchestrator — decomposes goals into sub-tasks and assigns to specialized agents. |

## Skills Installation (Required for Full Functionality)

Agents load skills on-demand for detailed guidance. **Skills must be installed** for agents to access reference material.

Install skills to the OpenCode skills directory:

```bash
mkdir -p ~/.config/opencode/skills
ln -sf /path/to/ai-toolkit/skills/* ~/.config/opencode/skills/
rm -f ~/.config/opencode/skills/README.md
```

Each agent's "Available Skills" section lists the skills it loads on-demand via the `skill` tool.

## Differences from Claude Code Version

| Feature | Claude Code | OpenCode |
|---------|-------------|----------|
| Location | `~/.claude/agents/` | `~/.config/opencode/agents/` |
| Tools format | `tools: Read, Edit, Write...` | `tools:` with `read: true` style |
| Skill injection | `skills: [name, ...]` in frontmatter | On-demand via `skill` tool |
| Mode field | N/A | `mode: subagent` |

The OpenCode version has core TDD knowledge inlined in the agent prompt, with instructions to load detailed skill content on-demand using the `skill` tool.

## Usage

Once installed, invoke agents as subagents:

```
Use tdd-agent to implement a Calculator.add method
Use code-review-agent to review the latest changes
Use migration-orchestrator to plan the EF Core migration
Use research-agent to investigate WebSocket vs SSE for real-time updates
```

Each agent operates autonomously with explicit state tracking, guardrails, and evidence-based verification.

## Configuration

You can customize the agent by editing the frontmatter:

```yaml
---
description: Autonomous TDD with strict guardrails
mode: subagent
tools:
  read: true
  edit: true
  write: true
  bash: true
  glob: true
  grep: true
---
```

The agents inherit the model configured in your OpenCode settings, so no `model` field is needed. To override for a specific agent, add `model: provider/model-name` to the frontmatter.

See [OpenCode Agents Documentation](https://opencode.ai/docs/agents/) for all available options.
