# AI Toolkit

A collection of AI coding agent skills and autonomous subagents for AI-assisted software development workflows.

Supports [Claude Code](https://claude.ai/code) and [OpenCode](https://opencode.ai/).

## Setup

**Claude Code**: The included [`CLAUDE.md`](CLAUDE.md) provides project conventions. It references [`AGENTS.md`](AGENTS.md) which contains the full skill and agent structure guidelines.

**OpenCode**: The included [`AGENTS.md`](AGENTS.md) is automatically recognized. Skills and agents use the same conventions across both platforms.

**Other AI Tools** (Cursor, Windsurf, GitHub Copilot, etc.): [`AGENTS.md`](AGENTS.md) follows the emerging standard for universal agent instructions. Most tools will pick it up automatically from the project root.

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

Skills for .NET enterprise development patterns, migrations, and security.

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator + optional Telerik Blazor UI generation. |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks, data loss detection, SQL review, and rollback verification. |
| `nuget-package-scaffold` | NuGet package creation with multi-targeting, CI/CD pipelines, and semantic versioning. |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis with risk scoring, upgrade strategies, and incremental patterns. |
| `dotnet-architecture-checklist` | .NET Blazor architecture review checklist with CQRS/FreeMediator validation and grading. |
| `dotnet-security-review` | OWASP-based .NET security review with Telerik specialization and manager-friendly reporting. |
| `dotnet-security-review-federal` | Federal compliance overlay (NIST 800-53, DOE, CUI, FIPS) extending the base security review. |
| `minimal-api-scaffolder` | .NET 10 minimal API scaffolding with OpenAPI documentation, versioning, and security patterns. |
| `4d-schema-migration` | 4D (4th Dimension) to SQL Server/EF Core/Blazor full-stack migration specialist. |

### Edge/IoT/Robotics Suite

Skills for edge computing, computer vision, sensor integration, and robotics.

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson and Raspberry Pi with model conversion and profiling. |
| `jetson-deploy` | Jetson Orin Nano deployment with TensorRT optimization, containerization, and power management. |
| `sensor-integration` | Sensor data pipeline with I2C, SPI, UART, and GPIO protocols. Calibration and anomaly detection. |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X. Subsumption architecture and behavior trees. |

### AI/ML Bridge Suite

Skills for RAG pipelines, MCP servers, and local LLM management.

| Skill | Description |
|-------|-------------|
| `rag-pipeline-python` | RAG scaffold with Ollama/cloud embeddings, chunking strategies, and vector stores (Python/LangChain/LlamaIndex). |
| `rag-pipeline-dotnet` | RAG implementation with Microsoft Semantic Kernel, vector store options, and embedding models (.NET). |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP (Python), testing patterns, and protocol reference. |
| `ollama-model-workflow` | Local LLM management with Modelfile configuration, quantization, and benchmarking. |

### Coaching & Learning Suite

Skills for developing software engineering judgment through deliberate practice, Socratic questioning, and compressed feedback loops.

| Skill | Description |
|-------|-------------|
| `architecture-review` | Devil's advocate critic -- challenges designs via Socratic questioning against SOLID, coupling, failure modes, and scalability. |
| `pattern-tradeoff-analyzer` | Pattern selection coach -- presents 2-3 patterns with explicit tradeoffs, challenges golden hammer tendencies. |
| `system-design-kata` | Domain-calibrated exercises (security workflows, edge fleet, hybrid cloud) with critique rubrics. |
| `dependency-mapper` | Coupling visualization with Robert C. Martin metrics -- makes architectural decisions visible as dependency patterns. |
| `code-review-coach` | Deliberate practice for review -- user reviews first, then compares against expert analysis with category-based scoring. |
| `refactor-challenger` | Refactoring prioritization coach -- distinguishes aesthetic preferences from production-impact smells. |
| `security-review-trainer` | Progressive security challenges -- intentional vulnerabilities in clean code, scored findings, increasing difficulty. |
| `pr-feedback-writer` | Review communication coach -- blocking vs suggestion vs nit, constructive framing, explaining the "why". |
| `technical-debt-assessor` | Debt quantification practice -- deliberate vs accidental, cost-to-fix vs cost-to-carry, business case building. |
| `architecture-journal` | Lightweight ADR templates with retrospective prompts at 30/90/180 days for converting experience into expertise. |

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

### Agent Design Suite

Skills for designing, specifying, and extracting AI agent definitions.

| Skill | Description |
|-------|-------------|
| `spec-coach` | Interactive spec design coach from first principles. Guides through vision, PRD structure, INVEST story quality, specification by example, and three-tier guardrails. |
| `skill-creator` | Creates, revises, and scores SKILL.md definitions against the 10-section gold standard. Three modes: CREATE, REVISE, SCORE. |

### RPI Workflow Suite

Skills for the Research-Plan-Implement parallel workflow using session isolation and specialized subagents.

| Skill | Description |
|-------|-------------|
| `rpi-research` | Research phase -- parallel codebase exploration using subagents to gather context before planning. |
| `rpi-plan` | Plan phase -- converts a research artifact into a phased implementation plan with discrete, testable steps. |
| `rpi-implement` | Implement phase -- executes a phased implementation plan mechanically, one step at a time. |
| `rpi-iterate` | Iterate phase -- surgically updates an existing implementation plan based on new discoveries or scope changes. |

### Other Skills

| Skill | Description |
|-------|-------------|
| `python-arch-review` | Python architecture review with TDD, YAGNI, and code quality gates. |
| `jira-review` | Jira ticket review with complexity scoring and requirements extraction. |
| `jira-comment-writer` | Plain-language Jira comment drafter for project managers and clients. Translates technical updates into stakeholder-friendly language. |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code and generates well-formatted technical guides. |

## Agents

Autonomous agents that make decisions and take actions independently. Each agent has both Claude Code and OpenCode versions unless noted.

### Development Workflow

| Agent | Description | Skills |
|-------|-------------|--------|
| `tdd-agent` | Autonomous TDD -- drives the complete RED-GREEN-REFACTOR cycle with strict guardrails. | tdd-cycle, tdd-implementer, tdd-refactor, tdd-verify |
| `code-review-agent` | Autonomous code review -- security, correctness, performance, maintainability, and style analysis. | code-review-coach, security-review-trainer, pr-feedback-writer, automated-code-review |
| `test-generation-agent` | Autonomous test generation -- analyzes code, identifies gaps, generates tests with TDD patterns. | tdd-implementer, tdd-cycle, dotnet-vertical-slice, test-scaffold |
| `documentation-agent` | Autonomous documentation sync -- detects staleness, generates XML docs, updates READMEs. | architecture-journal, doc-sync |
| `dependency-audit-agent` | Autonomous dependency auditing -- vulnerability scanning, license compliance, upgrade paths. | dependency-mapper, technical-debt-assessor, supply-chain-audit |
| `spec-extractor-agent` | Extracts structured agent specifications from natural-language descriptions or existing code. | spec-coach |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code and generates well-formatted technical guides. | confluence-guide-writer |

### DevOps / Infrastructure

| Agent | Description | Skills |
|-------|-------------|--------|
| `migration-orchestrator` | Semi-autonomous migration orchestration -- EF Core and .NET Framework migrations with approval gates. | ef-migration-manager, legacy-migration-analyzer |
| `environment-health-agent` | Autonomous environment health monitoring -- Docker, services, connections, and recovery. | environment-health |

### Edge AI / IoT

| Agent | Description | Skills |
|-------|-------------|--------|
| `model-optimization-agent` | Autonomous model optimization -- quantization, format conversion, and benchmarking for edge. | edge-cv-pipeline, jetson-deploy, model-optimization |
| `sensor-anomaly-agent` | Autonomous sensor anomaly detection -- statistical outliers, drift monitoring, recalibration. | sensor-integration, anomaly-detection |
| `fleet-deployment-agent` | Semi-autonomous fleet deployment -- canary, staged rollout, health gates, and rollback. | jetson-deploy, fleet-management |

### Knowledge / RAG

| Agent | Description | Skills |
|-------|-------------|--------|
| `research-agent` | Autonomous research -- multi-source investigation, credibility scoring, and structured briefings. | rag-pipeline-python, research-synthesis |
| `context-builder-agent` | Autonomous context assembly -- git change summarization, ADR matching, dependency mapping. | architecture-journal, dependency-mapper, session-context |

### RPI Workflow Subagents

Specialized subagents that execute individual phases of the Research-Plan-Implement workflow.

| Agent | Description |
|-------|-------------|
| `rpi-planner` | Converts a research artifact into a phased, testable implementation plan. |
| `rpi-implement` | Executes a single implementation phase mechanically from a plan artifact. |
| `rpi-code-analyzer` | Analyzes code structure and patterns during the research phase. |
| `rpi-file-locator` | Locates relevant files and entry points during the research phase. |
| `rpi-pattern-finder` | Identifies existing patterns and conventions during the research phase. |

### Meta / Orchestration

| Agent | Description | Skills |
|-------|-------------|--------|
| `task-decomposition-agent` | Meta-orchestrator -- decomposes complex goals into sub-tasks and assigns to specialized agents. | task-decomposition |

## Installation

### Claude Code

```bash
bash scripts/install-claude.sh
```

Copies all agents to `~/.claude/agents/` and all skills to `~/.claude/skills/`.

**Windows (PowerShell):**

```powershell
.\scripts\install-claude.ps1
```

**Verification:** Open Claude Code, type `/` to see available slash commands, or run `/agents` to see installed agents.

### OpenCode

```bash
bash scripts/install-opencode.sh
```

Copies all agents to `~/.config/opencode/agents/` and all skills to `~/.config/opencode/skills/`.

**Windows (PowerShell):**

```powershell
.\scripts\install-opencode.ps1
```

**Verification:** Open OpenCode, type `/` to see available slash commands, or press `Tab` to cycle through available agents.

OpenCode searches for skills in these locations (in order):

| Location | Path |
|----------|------|
| Project-local (OpenCode) | `.opencode/skills/<name>/SKILL.md` |
| Project-local (Claude) | `.claude/skills/<name>/SKILL.md` |
| Global (OpenCode) | `~/.config/opencode/skills/<name>/SKILL.md` |
| Global (Claude) | `~/.claude/skills/<name>/SKILL.md` |

**Verification:** Open OpenCode, type `/` to see available slash commands, or press `Tab` to cycle through available agents.

### OpenCode vs Claude Code Agents

| Feature | Claude Code | OpenCode |
|---------|-------------|----------|
| Agent location | `~/.claude/agents/` | `~/.config/opencode/agents/` |
| Tools format | `tools: Read, Edit, Write...` | `tools:` with `read: true` style |
| Skill injection | `skills: [name, ...]` in frontmatter | On-demand via `skill` tool |
| Mode field | N/A | `mode: subagent` |

## Usage

Skills are invoked automatically based on context or triggered with slash commands:

```
/tdd-cycle                      # Start a TDD session
/tdd-agent                      # Autonomous TDD mode
/tdd-pair                       # Collaborative TDD
/tdd-verify                     # Audit TDD compliance
/dotnet-vertical-slice          # Scaffold a vertical slice feature
/ef-migration-manager           # Manage EF Core migrations safely
/edge-cv-pipeline               # Build an edge CV pipeline
/rag-pipeline-python            # Scaffold a RAG pipeline (Python)
/rag-pipeline-dotnet            # Scaffold a RAG pipeline (.NET)
/mcp-server-scaffold            # Create a custom MCP server
/ollama-model-workflow          # Manage local LLMs with Ollama
/architecture-review            # Challenge a design with Socratic questioning
/code-review-coach              # Practice deliberate code review
/pattern-tradeoff-analyzer      # Analyze pattern tradeoffs
/security-review-trainer        # Progressive security challenges
/architecture-journal           # Record and review architecture decisions
/dotnet-security-review         # OWASP security review for .NET
/dotnet-security-review-federal # Federal compliance overlay
/legacy-migration-analyzer      # .NET Framework migration analysis
/4d-schema-migration            # 4D to SQL Server migration
/spec-coach                     # Design a spec interactively (agents, skills, PRDs, Spec Kit)
/rpi-research                   # Research phase of RPI workflow
/rpi-plan                       # Plan phase of RPI workflow
/rpi-implement                  # Implement phase of RPI workflow
/rpi-iterate                    # Update an existing implementation plan
/confluence-guide-writer        # Generate a guide from Confluence or source code
/jira-comment-writer            # Draft a stakeholder-friendly Jira comment
/skill-creator                  # Create, revise, or score a SKILL.md definition
```

Agents are invoked as subagents:

```
Use tdd-agent to implement a Calculator.add method
Use code-review-agent to review the latest changes
Use migration-orchestrator to plan the EF Core migration
Use research-agent to investigate WebSocket vs SSE for real-time updates
Use spec-extractor-agent to extract an agent spec from this description
Use rpi-planner to turn this research artifact into an implementation plan
```

## Project Templates

The `project-templates/` directory contains per-project context files based on the [Four Prompt Disciplines & Five Primitives framework](https://natesnewsletter.substack.com/). Copy the relevant files into your own project root to give AI agents the context they need to operate effectively across sessions.

> These are **project-level** files. They supplement your global `CLAUDE.md` / `AGENTS.md` — they do not replace them. Global standards (coding style, security rules, quality gates) stay in the global files. Project-specific context goes here.

| File | Discipline | Purpose | When to use |
|------|-----------|---------|-------------|
| `CLAUDE.md` | Context Engineering | Project context for Claude Code: stack, architecture, key files, persistent decisions, boot ritual | Every project using Claude Code |
| `AGENTS.md` | Context Engineering | Same as above for OpenCode | Every project using OpenCode |
| `intent.md` | Intent Engineering | What the agent optimizes for: goals, values, tradeoff hierarchy, agent architecture selection | Every project |
| `constraints.md` | Specification Engineering | Musts, must-nots, preferences, escalation triggers, code quality gates | Every project |
| `evals.md` | Specification Engineering | Test cases, CI gate definitions, taste rules, rejection log | Every project |
| `domain-memory.md` | Agent Harness State | Dark factory backlog, worker boot ritual, progress log | Dark factory / multi-session work only |
| `design.md` | Context Engineering | Design system tokens, component hierarchy, interaction patterns | UI-heavy projects only |

**Minimum set for a coding harness:** `CLAUDE.md` (or `AGENTS.md`) + `intent.md` + `constraints.md` + `evals.md`.
**Add for dark factory:** `domain-memory.md`.
**Add for UI-heavy projects:** `design.md`.

Specs (problem statements, acceptance criteria, decomposition) live in **Jira / Confluence** — not in a local file.

## Repository Structure

```
ai-toolkit/
├── skills/                     # Shareable skills
│   ├── <skill-name>/
│   │   ├── SKILL.md            # Skill definition with frontmatter
│   │   └── references/         # Supporting documentation
│   └── ...
├── claude/
│   ├── agents/                 # Claude Code agent definitions
│   │   └── <agent-name>.md
│   └── global/                 # Global Claude Code files (installed to ~/.claude/)
│       ├── CLAUDE.md           # Global context and standards
│       └── settings.local.json
├── opencode/
│   ├── agents/                 # OpenCode agent definitions
│   │   └── <agent-name>.md
│   └── global/                 # Global OpenCode files (installed to ~/.config/opencode/)
│       ├── AGENTS.md           # Global context and standards
│       └── opencode.json
├── project-templates/          # Per-project context files — copy to your project root
│   ├── CLAUDE.md               # Project-level context for Claude Code
│   ├── AGENTS.md               # Project-level context for OpenCode
│   ├── intent.md               # Agent intent: goals, values, tradeoff hierarchy
│   ├── constraints.md          # Musts, must-nots, preferences, escalation triggers
│   ├── evals.md                # Test cases, CI gate, taste rules
│   ├── domain-memory.md        # Dark factory backlog and progress log
│   └── design.md               # Design system reference (UI-heavy projects)
├── scripts/                    # Install scripts (Bash + PowerShell)
│   ├── install-claude.sh
│   ├── install-claude.ps1
│   ├── install-opencode.sh
│   └── install-opencode.ps1
├── docs/                       # Supplementary documentation
├── AGENTS.md                   # This project's OpenCode context (project-level)
├── CLAUDE.md                   # This project's Claude Code context (project-level)
├── intent.md                   # This project's agent intent and architecture
├── constraints.md              # This project's agent constraints and quality gates
├── evals.md                    # This project's eval definitions and taste rules
├── DEVELOPER.md                # Developer setup and tooling guide
└── README.md
```

## Author

[Michael K Alber](https://github.com/michaelalber)

## License

MIT License - see [LICENSE](LICENSE) for details.
