# Skills

Shareable skills for Claude Code and [OpenCode](https://opencode.ai/).

## Installation

### Claude Code

Skills must be installed in `~/.claude/skills/` to be available in Claude Code.

#### Option 1: Symlink (Recommended)

Symlinks keep the skills in sync with the repository:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink all skill folders
ln -sf /path/to/ai-toolkit/skills/* ~/.claude/skills/

# Remove the README.md symlink
rm -f ~/.claude/skills/README.md
```

#### Option 2: Copy

Copy folders directly (won't auto-update when repo changes):

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/ai-toolkit/skills/!(README.md) ~/.claude/skills/
```

#### Verification

After installation, verify the skills are available:

1. Open Claude Code
2. Type `/` to see available slash commands
3. Your installed skills should appear (e.g., `/tdd-cycle`, `/tdd-verify`)

### OpenCode

[OpenCode](https://opencode.ai/) supports Claude-compatible skill locations, so these skills work out of the box.

OpenCode searches for skills in these locations:

| Location | Path |
|----------|------|
| Project-local (OpenCode) | `.opencode/skills/<name>/SKILL.md` |
| Project-local (Claude) | `.claude/skills/<name>/SKILL.md` |
| Global (OpenCode) | `~/.config/opencode/skills/<name>/SKILL.md` |
| Global (Claude) | `~/.claude/skills/<name>/SKILL.md` |

#### Option 1: Symlink to OpenCode config (Recommended)

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.config/opencode/skills

# Symlink all skill folders
ln -sf /path/to/ai-toolkit/skills/* ~/.config/opencode/skills/

# Remove the README.md symlink
rm -f ~/.config/opencode/skills/README.md
```

#### Option 2: Symlink to Claude location

If you already have skills installed for Claude Code, OpenCode will find them automatically:

```bash
# If you've already set up Claude Code skills, OpenCode will use them
# No additional setup required!
```

#### Option 3: Copy

```bash
mkdir -p ~/.config/opencode/skills
cp -r /path/to/ai-toolkit/skills/!(README.md) ~/.config/opencode/skills/
```

#### Verification

After installation, verify the skills are available:

1. Open OpenCode
2. Type `/` to see available slash commands
3. Your installed skills should appear (e.g., `/tdd-cycle`, `/tdd-verify`)

## Available Skills

### TDD Suite

| Skill | Description |
|-------|-------------|
| `tdd-agent` | Fully autonomous TDD with strict guardrails |
| `tdd-cycle` | Core RED-GREEN-REFACTOR cycle guidance |
| `tdd-implementer` | Minimal implementation strategies (Fake It, Obvious, Triangulation) |
| `tdd-pair` | Collaborative TDD pair programming mode |
| `tdd-refactor` | Safe refactoring patterns and code smell detection |
| `tdd-verify` | TDD compliance verification and scoring |

### Enterprise .NET Suite

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator + Telerik Blazor UI |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks and rollback |
| `nuget-package-scaffold` | NuGet package creation with CI/CD and test harness |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis and upgrade patterns |
| `dotnet-architecture-checklist` | .NET Blazor architecture review checklist with CQRS/FreeMediator validation |
| `dotnet-security-review` | OWASP-based .NET security review with Telerik specialization |
| `dotnet-security-review-federal` | Federal compliance overlay (NIST 800-53, DOE, CUI) for .NET security |
| `minimal-api-scaffolder` | .NET 10 minimal API scaffolding with OpenAPI and versioning |
| `shared-kernel-generator` | Shared kernel module generation for DenaliDataSystems patterns |
| `4d-schema-migration` | 4D database to SQL Server/EF Core migration specialist |

### Edge/IoT/Robotics Suite

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson/Pi |
| `jetson-deploy` | Jetson Orin Nano deployment and TensorRT optimization |
| `sensor-integration` | Sensor data pipeline with I2C/SPI/UART/GPIO protocols |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X |

### AI/ML Bridge Suite

| Skill | Description |
|-------|-------------|
| `rag-pipeline-python` | RAG scaffold with Ollama/cloud embeddings and vector stores (Python/LangChain/LlamaIndex) |
| `rag-pipeline-dotnet` | RAG implementation with Microsoft Semantic Kernel (.NET) |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP and testing |
| `ollama-model-workflow` | Local LLM management with Modelfile and benchmarking |

### Coaching & Learning Suite

| Skill | Description |
|-------|-------------|
| `architecture-review` | Devil's advocate architecture critic with Socratic questioning |
| `pattern-tradeoff-analyzer` | Pattern selection coach with explicit tradeoff analysis |
| `system-design-kata` | Domain-calibrated design exercises with critique rubrics |
| `dependency-mapper` | Coupling visualization with Robert C. Martin metrics |
| `code-review-coach` | Deliberate practice for code review with scoring |
| `refactor-challenger` | Refactoring prioritization by business impact |
| `security-review-trainer` | Progressive security challenges with difficulty levels |
| `pr-feedback-writer` | Review communication coach for constructive feedback |
| `technical-debt-assessor` | Debt quantification and business case building |
| `architecture-journal` | ADR templates with 30/90/180-day retrospectives |

### Agent Support Suite

Skills that provide domain knowledge and execution protocols for autonomous agents.

| Skill | Description | Used By |
|-------|-------------|---------|
| `automated-code-review` | Autonomous review execution checklists for security, correctness, performance, maintainability, style | code-review-agent |
| `test-scaffold` | Test generation conventions, AAA naming, mock patterns for FreeMediator/repositories | test-generation-agent |
| `doc-sync` | Documentation staleness detection, XML doc generation, README sync | documentation-agent |
| `supply-chain-audit` | NuGet/npm/pip vulnerability scanning, license matrix, CVE correlation | dependency-audit-agent |
| `environment-health` | Docker health checks, service monitoring, container lifecycle, connection validation | environment-health-agent |
| `model-optimization` | Quantization workflows, TensorRT/TFLite conversion, accuracy/latency benchmarking | model-optimization-agent |
| `anomaly-detection` | Statistical anomaly detection, drift algorithms, alert/log/calibrate decision trees | sensor-anomaly-agent |
| `fleet-management` | Rolling deployment strategies, multi-device coordination, rollback triggers | fleet-deployment-agent |
| `research-synthesis` | Multi-source cross-referencing, source credibility scoring, briefing formats | research-agent |
| `session-context` | Git change summarization, ADR relevance matching, pattern applicability | context-builder-agent |
| `task-decomposition` | Goal breakdown heuristics, dependency DAGs, sub-agent assignment protocols | task-decomposition-agent |

### Other Skills

| Skill | Description |
|-------|-------------|
| `python-arch-review` | Python architecture review with TDD, YAGNI, and code quality gates |
| `jira-review` | Jira ticket review with complexity scoring and requirements extraction |

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md           # Main skill definition with frontmatter
└── references/        # Supporting documentation
    ├── reference1.md
    └── reference2.md
```

## Usage

Skills can be invoked as slash commands:

```
/tdd-cycle                  # Start a TDD session
/dotnet-vertical-slice      # Scaffold a vertical slice feature
/ef-migration-manager       # Manage EF Core migrations safely
/edge-cv-pipeline           # Build an edge CV pipeline
/rag-pipeline-python        # Scaffold a RAG pipeline (Python)
/rag-pipeline-dotnet        # Scaffold a RAG pipeline (.NET Semantic Kernel)
/mcp-server-scaffold        # Create a custom MCP server
/architecture-review        # Challenge a design with Socratic questioning
/code-review-coach          # Practice deliberate code review
/security-review-trainer    # Progressive security challenge training
/architecture-journal       # Record and review architecture decisions
```

Or referenced by agents that depend on them.
