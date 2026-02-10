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

### Enterprise .NET Suite

Skills for .NET enterprise development patterns, migrations, and UI components.

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator. Feature folder patterns and pipeline behaviors. |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks, data loss detection, SQL review, and rollback verification. |
| `nuget-package-scaffold` | NuGet package creation with multi-targeting, CI/CD pipelines, and semantic versioning. |
| `blazor-telerik-component` | Telerik Blazor UI patterns for grids, forms, dialogs, and CRUD workflows. |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis with risk scoring and incremental strategies. |

### Edge/IoT/Robotics Suite

Skills for edge computing, computer vision, sensor integration, and robotics.

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson and Raspberry Pi with model conversion and profiling. |
| `jetson-deploy` | Jetson Orin Nano deployment with TensorRT optimization, containerization, and power management. |
| `sensor-integration` | Sensor data pipeline with I2C, SPI, UART, and GPIO protocols. Calibration and anomaly detection. |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X. Subsumption architecture and behavior trees. |

### AI/ML Bridge Suite

Skills for RAG pipelines, MCP servers, and local LLM management. Python-focused.

| Skill | Description |
|-------|-------------|
| `rag-pipeline` | RAG scaffold with Ollama/cloud embeddings, chunking strategies, and vector store patterns. |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP (Python), testing patterns, and protocol reference. |
| `ollama-model-workflow` | Local LLM management with Modelfile configuration, quantization, and benchmarking. |

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
/tdd-cycle                  # Start a TDD session
/tdd-agent                  # Autonomous TDD mode
/tdd-pair                   # Collaborative TDD
/tdd-verify                 # Audit TDD compliance
/dotnet-vertical-slice      # Scaffold a vertical slice feature
/ef-migration-manager       # Manage EF Core migrations safely
/edge-cv-pipeline           # Build an edge CV pipeline
/rag-pipeline               # Scaffold a RAG pipeline
/mcp-server-scaffold        # Create a custom MCP server
/ollama-model-workflow      # Manage local LLMs with Ollama
```

## Author

[Michael K Alber](https://github.com/michaelalber)

## License

MIT License - see [LICENSE](LICENSE) for details.
