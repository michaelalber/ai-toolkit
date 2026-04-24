# AI Toolkit

A collection of AI coding agent skills and autonomous subagents for AI-assisted software development workflows.

## Platforms

| Platform | Provider | Privacy | Best for |
|----------|----------|---------|----------|
| **[Claude Code](https://claude.ai/code)** | Anthropic subscription | Cloud | Best reasoning, MCP ecosystem, Claude-native workflows |
| **[OpenCode](https://opencode.ai/)** | Any cloud provider (Anthropic, OpenAI, Google, Mistral…) | Cloud | Provider flexibility, multi-model teams |
| **[Pi](https://pi.dev)** | Ollama local models (7B–32B) | Fully offline | Zero API cost, privacy-first, air-gapped use |

### Claude Code
```bash
bash scripts/install-claude.sh     # macOS / Linux
.\scripts\install-claude.ps1       # Windows
```
Copies agents to `~/.claude/agents/` and skills to `~/.claude/skills/`. See [`claude/global/README.md`](claude/global/README.md) for global config setup.

### OpenCode
```bash
bash scripts/install-opencode.sh   # macOS / Linux
.\scripts\install-opencode.ps1     # Windows
```
Copies agents to `~/.config/opencode/agents/` and skills to `~/.config/opencode/skills/`. See [`opencode/global/README.md`](opencode/global/README.md) for provider config and Ollama tuning.

### Pi (Ollama / Local Models)
```bash
bash scripts/install-pi.sh         # 7B-safe default
bash scripts/install-pi.sh --full  # 20B variant
```
Installs `AGENTS.md`, `models.json`, and `settings.json` to `~/.pi/agent/`. See [`pi/global/README.md`](pi/global/README.md) for the full Ollama setup guide — model selection, Modelfile context window config, and compaction tuning.

**Other AI Tools** (Cursor, Windsurf, GitHub Copilot, etc.): [`AGENTS.md`](AGENTS.md) follows the emerging universal agent instructions standard and is auto-discovered from the project root.

---

## Skills

### TDD Suite

| Skill | Description |
|-------|-------------|
| `tdd-cycle` | Orchestrates the RED-GREEN-REFACTOR cycle. Maintains phase state and enforces transitions. |
| `tdd-implementer` | GREEN phase specialist. Implements minimal code to make failing tests pass using Fake It, Obvious Implementation, or Triangulation strategies. |
| `tdd-refactor` | REFACTOR phase specialist. Safely improves code structure while keeping tests green. Includes code smell detection and refactoring recipes. |
| `tdd-agent` | Fully autonomous TDD mode. AI drives all phases with strict guardrails and explicit verification at each step. |
| `tdd-pair` | Collaborative TDD with role-based pairing. Supports Ping-Pong, Navigator, and Teaching modes. |
| `tdd-verify` | Audits code for TDD compliance. Detects anti-patterns, scores test quality, and generates compliance reports. |

### Enterprise .NET Suite

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

### Edge / IoT / Robotics Suite

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson and Raspberry Pi with model conversion and profiling. |
| `jetson-deploy` | Jetson Orin Nano deployment with TensorRT optimization, containerization, and power management. |
| `sensor-integration` | Sensor data pipeline with I2C, SPI, UART, and GPIO protocols. Calibration and anomaly detection. |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X. Subsumption architecture and behavior trees. |

### AI / ML Bridge Suite

| Skill | Description |
|-------|-------------|
| `rag-pipeline-python` | RAG scaffold with Ollama/cloud embeddings, chunking strategies, and vector stores (Python/LangChain/LlamaIndex). |
| `rag-pipeline-dotnet` | RAG implementation with Microsoft Semantic Kernel, vector store options, and embedding models (.NET). |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP (Python), testing patterns, and protocol reference. |
| `ollama-model-workflow` | Local LLM management with Modelfile configuration, quantization, and benchmarking. |

### Coaching & Learning Suite

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

| Skill | Description |
|-------|-------------|
| `spec-coach` | Interactive spec design coach from first principles. Guides through vision, PRD structure, INVEST story quality, specification by example, and three-tier guardrails. |
| `skill-creator` | Creates, revises, and scores SKILL.md definitions against the 10-section gold standard. Three modes: CREATE, REVISE, SCORE. |

### RPI Workflow Suite

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

---

## Agents

Autonomous agents that make decisions and take actions independently. Each agent has both Claude Code and OpenCode versions unless noted.

### Development & DevOps

| Agent | Description | Skills |
|-------|-------------|--------|
| `tdd-agent` | Autonomous TDD -- drives the complete RED-GREEN-REFACTOR cycle with strict guardrails. | tdd-cycle, tdd-implementer, tdd-refactor, tdd-verify |
| `code-review-agent` | Autonomous code review -- security, correctness, performance, maintainability, and style analysis. | code-review-coach, security-review-trainer, pr-feedback-writer, automated-code-review |
| `test-generation-agent` | Autonomous test generation -- analyzes code, identifies gaps, generates tests with TDD patterns. | tdd-implementer, tdd-cycle, dotnet-vertical-slice, test-scaffold |
| `documentation-agent` | Autonomous documentation sync -- detects staleness, generates XML docs, updates READMEs. | architecture-journal, doc-sync |
| `dependency-audit-agent` | Autonomous dependency auditing -- vulnerability scanning, license compliance, upgrade paths. | dependency-mapper, technical-debt-assessor, supply-chain-audit |
| `spec-extractor-agent` | Extracts structured agent specifications from natural-language descriptions or existing code. | spec-coach |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code and generates well-formatted technical guides. | confluence-guide-writer |
| `migration-orchestrator` | Semi-autonomous migration orchestration -- EF Core and .NET Framework migrations with approval gates. | ef-migration-manager, legacy-migration-analyzer |
| `environment-health-agent` | Autonomous environment health monitoring -- Docker, services, connections, and recovery. | environment-health |
| `task-decomposition-agent` | Meta-orchestrator -- decomposes complex goals into sub-tasks and assigns to specialized agents. | task-decomposition |

### Edge AI / IoT / Knowledge

| Agent | Description | Skills |
|-------|-------------|--------|
| `model-optimization-agent` | Autonomous model optimization -- quantization, format conversion, and benchmarking for edge. | edge-cv-pipeline, jetson-deploy, model-optimization |
| `sensor-anomaly-agent` | Autonomous sensor anomaly detection -- statistical outliers, drift monitoring, recalibration. | sensor-integration, anomaly-detection |
| `fleet-deployment-agent` | Semi-autonomous fleet deployment -- canary, staged rollout, health gates, and rollback. | jetson-deploy, fleet-management |
| `research-agent` | Autonomous research -- multi-source investigation, credibility scoring, and structured briefings. | rag-pipeline-python, research-synthesis |
| `context-builder-agent` | Autonomous context assembly -- git change summarization, ADR matching, dependency mapping. | architecture-journal, dependency-mapper, session-context |

> RPI workflow subagents (`rpi-planner`, `rpi-implement`, `rpi-code-analyzer`, `rpi-file-locator`, `rpi-pattern-finder`) are spawned automatically by the RPI skills — they are not invoked directly.

---

## Usage

There are two ways to invoke capabilities — **commands** (user-typed) and **skills/agents** (model-invoked):

**Commands** (`claude/commands/`, `opencode/commands/`) — type `/` to trigger; inject live shell state before the model acts:

```
/tdd-cycle                    # Injects dotnet test output, then runs the TDD cycle
/code-review                  # Injects git diff, then reviews changes
/security-review src/          # OWASP review scoped to a path
/arch-review OrderService      # Socratic challenge of a component
/new-feature CreateInvoice     # Scaffold a vertical slice feature
/migrate AddInvoiceTable       # EF Core migration with safety checks
/research "WebSocket vs SSE"   # Multi-source research briefing
/context-prime                 # Prime session from git state and recent work
```

**Skills and agents** — invoked autonomously by the model or referenced in a prompt:

```
Use tdd-agent to implement a Calculator.add method
Use code-review-agent to review the latest changes
Use migration-orchestrator to plan the EF Core migration
Use research-agent to investigate WebSocket vs SSE for real-time updates
```

Type `/` in your agent to see the full list of available commands.

---

## Project Templates

The `project-templates/` directory contains per-project context files based on the **Four Prompt Disciplines & Five Primitives** framework by [Nate B. Jones](https://natesnewsletter.substack.com/). Copy the relevant files into your own project root — see [`project-templates/README.md`](project-templates/README.md) for the full guide including agent architecture selection.

> These are **project-level** files. They supplement your global config — they do not replace it. Global standards stay in the global files; project-specific context goes here.

| File | Purpose | When to use |
|------|---------|-------------|
| `CLAUDE.md` / `AGENTS.md` | Project context: stack, architecture, key files, boot ritual | Every project |
| `intent.md` | What the agent optimizes for: goals, values, tradeoff hierarchy | Every project |
| `constraints.md` | Musts, must-nots, preferences, escalation triggers | Every project |
| `evals.md` | Test cases, CI gate definitions, taste rules, rejection log | Every project |
| `domain-memory.md` | Dark factory backlog and progress log | Multi-session agentic work only |
| `design.md` | Design system tokens, component hierarchy, interaction patterns | UI-heavy projects only |

**Minimum set:** `CLAUDE.md` (or `AGENTS.md`) + `intent.md` + `constraints.md` + `evals.md`.

Specs (problem statements, acceptance criteria, decomposition) live in **Jira / Confluence** — not in a local file.

---

## Repository Structure

```
ai-toolkit/
├── skills/                     # Shareable skills (SKILL.md + references/)
├── claude/
│   ├── agents/                 # Claude Code agent definitions
│   ├── commands/               # User-invoked slash commands with shell injection
│   └── global/                 # Global config → ~/.claude/
│       ├── CLAUDE.md           # Global instructions (every project)
│       ├── settings.json       # Hooks: credential stop + post-write build/lint gates
│       └── settings.local.json # Permissions: bash allow/deny, read allow/deny
├── opencode/
│   ├── agents/                 # OpenCode agent definitions
│   ├── commands/               # User-invoked commands with agent routing
│   └── global/                 # Global config → ~/.config/opencode/
│       ├── AGENTS.md           # Global instructions (every project)
│       └── opencode.json       # Providers, MCP servers, permissions, temperatures
├── pi/
│   └── global/                 # Global config → ~/.pi/agent/  (Ollama setup guide inside)
├── project-templates/          # Per-project context files — copy to your project root
├── scripts/                    # Install scripts (Bash + PowerShell)
├── docs/                       # Supplementary documentation
├── AGENTS.md                   # This project's OpenCode context
├── CLAUDE.md                   # This project's Claude Code context
├── intent.md / constraints.md / evals.md
└── DEVELOPER.md
```

---

## Author

[Michael K Alber](https://github.com/michaelalber)

## License

MIT License - see [LICENSE](LICENSE) for details.
