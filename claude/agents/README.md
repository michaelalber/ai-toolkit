# Claude Code Agents

Shareable Claude Code agents for the AI Toolkit.

## Installation

Agents must be installed in `~/.claude/agents/` to be available in Claude Code.

### Option 1: Symlink (Recommended)

Symlinks keep the agents in sync with the repository:

```bash
# Create the agents directory if it doesn't exist
mkdir -p ~/.claude/agents

# Symlink all agent files
ln -sf /path/to/ai-toolkit/claude/agents/*.md ~/.claude/agents/

# Remove the README.md symlink
rm -f ~/.claude/agents/README.md
```

### Option 2: Copy

Copy files directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.claude/agents
cp /path/to/ai-toolkit/claude/agents/*.md ~/.claude/agents/
```

## Verification

After installation, verify the agents are available:

1. Open Claude Code
2. Run `/agents`
3. Your installed agents should appear in the list

## Skill Dependencies

Some agents depend on skills from this repository. If an agent references skills (like `tdd-cycle`, `tdd-implementer`, etc.), you must also install those skills:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink all skills
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/

# Remove the README.md symlink
rm -f ~/.claude/skills/README.md
```

## Available Agents

### Development Workflow

| Agent | Description | Skills |
|-------|-------------|--------|
| `tdd-agent` | Autonomous TDD with strict guardrails. Drives the complete RED-GREEN-REFACTOR cycle independently. | tdd-cycle, tdd-implementer, tdd-refactor, tdd-verify |
| `code-review-agent` | Autonomous code review — security, correctness, performance, maintainability, and style analysis with structured findings. | code-review-coach, security-review-trainer, pr-feedback-writer, automated-code-review |
| `test-generation-agent` | Autonomous test generation using TDD patterns. Analyzes code, identifies gaps, generates tests with proper naming and mocking. | tdd-implementer, tdd-cycle, dotnet-vertical-slice, test-scaffold |
| `documentation-agent` | Autonomous documentation sync — detects staleness, generates XML docs, updates READMEs, and maintains ADRs. | architecture-journal, doc-sync |
| `dependency-audit-agent` | Autonomous dependency auditing — vulnerability scanning, license compliance, and upgrade path analysis. | dependency-mapper, technical-debt-assessor, supply-chain-audit |

### DevOps / Infrastructure

| Agent | Description | Skills |
|-------|-------------|--------|
| `migration-orchestrator` | Semi-autonomous migration orchestration — EF Core and .NET Framework migrations with approval gates. | ef-migration-manager, legacy-migration-analyzer |
| `environment-health-agent` | Autonomous environment health monitoring — Docker, services, connections, and recovery for dev environments. | environment-health |

### Edge AI / IoT

| Agent | Description | Skills |
|-------|-------------|--------|
| `model-optimization-agent` | Autonomous model optimization — quantization, format conversion, and accuracy/latency benchmarking for edge deployment. | edge-cv-pipeline, jetson-deploy, model-optimization |
| `sensor-anomaly-agent` | Autonomous sensor anomaly detection — statistical outlier detection, drift monitoring, and recalibration recommendations. | sensor-integration, anomaly-detection |
| `fleet-deployment-agent` | Semi-autonomous fleet deployment — canary, staged rollout, health gates, and rollback across edge device fleets. | jetson-deploy, fleet-management |

### Knowledge / RAG

| Agent | Description | Skills |
|-------|-------------|--------|
| `research-agent` | Autonomous research — multi-source investigation, credibility scoring, cross-referencing, and structured briefings. | rag-pipeline, research-synthesis |
| `context-builder-agent` | Autonomous context assembly — git change summarization, ADR matching, dependency mapping for session starts. | architecture-journal, dependency-mapper, session-context |

### Meta / Orchestration

| Agent | Description | Skills |
|-------|-------------|--------|
| `task-decomposition-agent` | Meta-orchestrator — decomposes complex goals into sub-tasks and assigns to specialized agents. Does NOT execute tasks itself. | task-decomposition |

## Usage

Once installed, agents can be invoked by the Task tool or referenced in Claude Code conversations. For example:

```
Use tdd-agent to implement a Calculator.add method
Use code-review-agent to review the latest changes
Use migration-orchestrator to plan the EF Core migration
Use research-agent to investigate WebSocket vs SSE for real-time updates
```

Each agent operates autonomously with explicit state tracking, guardrails, and evidence-based verification.
