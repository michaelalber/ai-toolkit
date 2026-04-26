# AI Toolkit

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-83-blue)](#skills)
[![Agents](https://img.shields.io/badge/agents-35-blue)](#agents)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20OpenCode%20%7C%20Pi-informational)](#platforms)

**83 skills, 35 agents, and 9 slash commands for AI-assisted software development — spanning TDD, .NET, Python, Rust, edge AI, security, DDD, and more.**

Works with [Claude Code](https://claude.ai/code), [OpenCode](https://opencode.ai/), and [Pi](https://pi.dev) (Ollama local models).

---

## Why I built this

I work across a wide range of domains — enterprise .NET, Python, Rust, edge AI, robotics, and federal security compliance. As AI coding assistants became central to my workflow, I found myself writing the same guidance over and over: how to run a proper TDD cycle, how to review code for OWASP compliance, how to scaffold a vertical slice feature correctly.

This toolkit encodes that expertise as reusable primitives. Each skill is an opinionated, structured prompt that reflects how I actually work — not a generic template. The result is an AI coding assistant that reasons the way I'd want a senior engineer to reason: with discipline, with domain knowledge, and with the right tradeoffs in mind.

**Design decisions:**
- **Three primitives, one toolkit** — skills (model-invoked expertise), agents (autonomous executors), commands (user-triggered with live shell context). Each has a distinct role.
- **Platform parity** — every skill and agent exists in both Claude Code and OpenCode format with identical behavior. Pi gets its own Ollama-optimized config.
- **Two-tier skill design** — full-template skills (10-section template: philosophy, principles, workflow, state, output templates, AI discipline rules, anti-patterns, error recovery, integrations) for domain-expert tools; minimal-tier skills (≤ 100 lines, focused instructions) for mode switches and conversational tools.
- **Global + project layered config** — global standards apply everywhere; project-level files add specificity without duplicating the global.

---

## At a glance

| | Count |
|--|-------|
| Skills | 83 |
| Agents (Claude Code) | 35 |
| Agents (OpenCode) | 35 |
| Slash commands (per platform) | 9 |
| Platforms | Claude Code, OpenCode, Pi |

---

## How it works

Three distinct primitives compose the toolkit:

**Skills** — Structured, opinionated prompt files that encode domain expertise. Model-invoked autonomously. Live in `skills/<name>/SKILL.md`. Each follows a strict 10-section template.

**Agents** — Autonomous executors that combine skills with tool access and guardrails. Operate independently within defined boundaries. Live in `claude/agents/` and `opencode/agents/`.

**Commands** — User-triggered slash commands (type `/command-name`) that inject live shell state before the model acts. Live in `claude/commands/` and `opencode/commands/`.

```
User types /tdd-cycle
    → command injects live dotnet test output
    → model reads failing tests
    → tdd-cycle skill drives RED-GREEN-REFACTOR
    → hooks run dotnet build after every file write
```

---

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
See [`claude/global/README.md`](claude/global/README.md) for global config setup (hooks, permissions, commands).

### OpenCode
```bash
bash scripts/install-opencode.sh   # macOS / Linux
.\scripts\install-opencode.ps1     # Windows
```
See [`opencode/global/README.md`](opencode/global/README.md) for provider config, Ollama tuning, and permissions.

### Pi (Ollama / Local Models)
```bash
bash scripts/install-pi.sh         # 7B-safe default
bash scripts/install-pi.sh --full  # 20B variant
```
See [`pi/global/README.md`](pi/global/README.md) for the full Ollama setup guide — Modelfile config, compaction tuning, model selection by VRAM.

**Other AI tools** (Cursor, Windsurf, Copilot, etc.): [`AGENTS.md`](AGENTS.md) follows the universal agent instructions standard and is auto-discovered from the project root.

---

## Skills

### TDD Suite

| Skill | Description |
|-------|-------------|
| `tdd-cycle` | Orchestrates RED-GREEN-REFACTOR. Maintains phase state and enforces transitions. |
| `tdd-implementer` | GREEN phase specialist. Implements minimal code using Fake It, Obvious Implementation, or Triangulation. |
| `tdd-refactor` | REFACTOR phase specialist. Safely improves structure while keeping tests green. Code smell detection and refactoring recipes. |
| `tdd-agent` | Fully autonomous TDD. AI drives all phases with strict guardrails and verification at each step. |
| `tdd-pair` | Collaborative TDD with role-based pairing — Ping-Pong, Navigator, and Teaching modes. |
| `tdd-verify` | TDD compliance audit. Detects anti-patterns, scores test quality, generates compliance reports. |

### Enterprise .NET Suite

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator + optional Telerik Blazor UI generation. |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks, data loss detection, SQL review, and rollback verification. |
| `nuget-package-scaffold` | NuGet package creation with multi-targeting, CI/CD pipelines, and semantic versioning. |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis with risk scoring, upgrade strategies, and incremental patterns. |
| `dotnet-architecture-checklist` | .NET Blazor architecture review with CQRS/FreeMediator validation and grading. |
| `dotnet-security-review` | OWASP-based .NET security review with Telerik specialization and manager-friendly reporting. |
| `dotnet-security-review-federal` | Federal compliance overlay (NIST 800-53, DOE, CUI, FIPS) extending the base security review. |
| `minimal-api-scaffolder` | .NET 10 minimal API scaffolding with OpenAPI documentation, versioning, and security patterns. |
| `4d-schema-migration` | 4D (4th Dimension) to SQL Server/EF Core/Blazor full-stack migration specialist. |

### Python Suite

| Skill | Description |
|-------|-------------|
| `python-arch-review` | Python architecture review with TDD, YAGNI, and code quality gates. |
| `python-security-review` | OWASP-based Python security review (FastAPI, Django, Flask) with bandit and pip-audit. |
| `python-security-review-federal` | Federal compliance overlay for Python — NIST 800-53, FIPS 140-2/3, CUI handling. |
| `python-feature-slice` | Feature-based Python architecture using FastAPI routers, Pydantic v2, and a service layer. |
| `alembic-migration-manager` | Full Alembic migration lifecycle with safety checks and rollback planning. |
| `python-modernization-analyzer` | Legacy Python modernization — Python 2→3, sync→async, Flask→FastAPI paths. |
| `fastapi-scaffolder` | FastAPI endpoints with OpenAPI docs, Pydantic v2, JWT auth, rate limiting, and health checks. |
| `pypi-package-scaffold` | Python package scaffolding for PyPI — pyproject.toml, CI/CD, test harness, supply chain checks. |

### Rust Suite

| Skill | Description |
|-------|-------------|
| `rust-architecture-checklist` | Rust architecture review — ownership discipline, trait design, error handling, unsafe audit, crate boundaries. |
| `rust-security-review` | OWASP Rust security review with cargo-audit, cargo-deny, and unsafe block audit. |
| `rust-feature-slice` | Vertical slice modules for Rust/Axum — router, service trait, impl, models, error types, integration tests. |
| `sqlx-migration-manager` | SQLx migration lifecycle — create, review, rollback test, apply, regenerate offline cache. |
| `rust-migration-analyzer` | C/C++ to Rust rewrite planning and Rust edition upgrade/modernization analysis. |
| `axum-scaffolder` | Production-ready Axum HTTP APIs with utoipa OpenAPI, JWT middleware, rate limiting, and CORS. |
| `cargo-package-scaffold` | Rust crate scaffolding — Cargo.toml metadata, CI, test harness, CHANGELOG, crates.io publish workflow. |

### Edge / IoT / Robotics Suite

| Skill | Description |
|-------|-------------|
| `edge-cv-pipeline` | OpenCV + TFLite computer vision pipeline for Jetson and Raspberry Pi with model conversion and profiling. |
| `jetson-deploy` | Jetson Orin Nano deployment with TensorRT optimization, containerization, and power management. |
| `sensor-integration` | Sensor data pipeline with I2C, SPI, UART, and GPIO. Calibration and anomaly detection. |
| `picar-x-behavior` | Composable robot behaviors for SunFounder Picar-X — subsumption architecture and behavior trees. |

### AI / ML Suite

| Skill | Description |
|-------|-------------|
| `rag-pipeline-python` | RAG scaffold with Ollama/cloud embeddings, chunking strategies, and vector stores (Python/LangChain/LlamaIndex). |
| `rag-pipeline-dotnet` | RAG with Microsoft Semantic Kernel, vector store options, and embedding models (.NET). |
| `mcp-server-scaffold` | Custom MCP server creation with FastMCP (Python), testing patterns, and protocol reference. |
| `ollama-model-workflow` | Local LLM management — Modelfile config, quantization, benchmarking. |

### Coaching & Learning Suite

| Skill | Description |
|-------|-------------|
| `architecture-review` | Devil's advocate critic — challenges designs via Socratic questioning against SOLID, coupling, failure modes, scalability. |
| `pattern-tradeoff-analyzer` | Pattern selection coach — 2-3 patterns with explicit tradeoffs; challenges golden hammer tendencies. |
| `system-design-kata` | Domain-calibrated exercises (security workflows, edge fleet, hybrid cloud) with critique rubrics. |
| `dependency-mapper` | Coupling visualization with Robert C. Martin metrics. |
| `code-review-coach` | Deliberate review practice — user reviews first, then compares against expert analysis with category scoring. |
| `refactor-challenger` | Refactoring prioritization — distinguishes aesthetic preferences from production-impact smells. |
| `security-review-trainer` | Progressive security challenges — intentional vulnerabilities in clean code, scored findings. |
| `pr-feedback-writer` | Review communication coach — blocking vs suggestion vs nit, constructive framing, explaining the "why". |
| `technical-debt-assessor` | Debt quantification — deliberate vs accidental, cost-to-fix vs cost-to-carry, business case building. |
| `architecture-journal` | Lightweight ADR templates with retrospective prompts at 30/90/180 days. |
| `grill-me` | Relentless plan/design interview — one question at a time with recommended answers, walking every branch of the decision tree. ([source](https://github.com/mattpocock/skills/tree/main/grill-me)) |
| `zoom-out` | Zooms out from current code to map callers, dependents, and module relationships before continuing. ([source](https://github.com/mattpocock/skills)) |
| `caveman` | Switches to terse, keyword-driven communication mode — cuts token usage ~75%. Persistent once triggered. ([source](https://github.com/mattpocock/skills)) |
| `design-an-interface` | Applies "Design It Twice" from APOSD — generates two radically different interface designs and compares them. ([source](https://github.com/mattpocock/skills)) |
| `improve-codebase-architecture` | Deep module refactoring using APOSD vocabulary — eliminates shallow modules, information leakage, and naming mismatches. ([source](https://github.com/mattpocock/skills)) |

### DDD Suite

| Skill | Description |
|-------|-------------|
| `domain-model` | DDD domain modeling consultant — enforces CONTEXT.md vocabulary, surfaces code/plan contradictions, records decisions as ADRs sparingly. ([source](https://github.com/mattpocock/skills)) |
| `ubiquitous-language` | Extracts and formalizes domain vocabulary from conversation or codebase — classifies terms, resolves ambiguities, saves to UBIQUITOUS_LANGUAGE.md. ([source](https://github.com/mattpocock/skills)) |

### Product & GitHub Workflow Suite

| Skill | Description |
|-------|-------------|
| `to-prd` | Converts meeting notes or feature requests into a structured PRD with goals, user stories, and binary acceptance criteria. ([source](https://github.com/mattpocock/skills)) |
| `to-issues` | Converts a PRD into atomic GitHub Issues ordered by dependency — infrastructure first, features next, polish last. ([source](https://github.com/mattpocock/skills)) |
| `triage-issue` | Triages a GitHub Issue or bug report — classifies severity, identifies root cause area, recommends priority and owner. ([source](https://github.com/mattpocock/skills)) |
| `qa` | Structured QA review — verifies acceptance criteria coverage, generates edge case test matrix, flags gaps before shipping. ([source](https://github.com/mattpocock/skills)) |

### Agent Support Suite

| Skill | Description | Used By |
|-------|-------------|---------|
| `automated-code-review` | Autonomous review checklists — security, correctness, performance, maintainability, style | code-review-agent |
| `test-scaffold` | Test generation conventions, AAA naming, mock patterns for FreeMediator/repositories | test-generation-agent |
| `doc-sync` | Documentation staleness detection, XML doc generation, README sync | documentation-agent |
| `supply-chain-audit` | NuGet/npm/pip vulnerability scanning, license matrix, CVE correlation | dependency-audit-agent |
| `environment-health` | Docker health checks, service monitoring, container lifecycle | environment-health-agent |
| `model-optimization` | Quantization workflows, TensorRT/TFLite conversion, accuracy/latency benchmarking | model-optimization-agent |
| `anomaly-detection` | Statistical anomaly detection, drift algorithms, alert/log/calibrate decision trees | sensor-anomaly-agent |
| `fleet-management` | Rolling deployment strategies, multi-device coordination, rollback triggers | fleet-deployment-agent |
| `research-synthesis` | Multi-source cross-referencing, source credibility scoring, briefing formats | research-agent |
| `session-context` | Git change summarization, ADR relevance matching, pattern applicability | context-builder-agent |
| `task-decomposition` | Goal breakdown heuristics, dependency DAGs, sub-agent assignment protocols | task-decomposition-agent |

### Agent Design Suite

| Skill | Description |
|-------|-------------|
| `spec-coach` | Interactive spec design coach — vision, PRD structure, INVEST story quality, specification by example, three-tier guardrails. |
| `skill-creator` | Creates, revises, and scores SKILL.md definitions against the 10-section gold standard. |

### RPI Workflow Suite

A structured Research → Plan → Implement loop with parallel subagents and session isolation.

| Skill | Description |
|-------|-------------|
| `rpi-research` | Parallel codebase exploration using subagents to gather context before planning. |
| `rpi-plan` | Converts a research artifact into a phased implementation plan with discrete, testable steps. |
| `rpi-implement` | Executes a phased implementation plan mechanically, one step at a time. |
| `rpi-iterate` | Surgically updates an existing plan based on new discoveries or scope changes. |

### Other Skills

| Skill | Description |
|-------|-------------|
| `jira-review` | Jira ticket review with complexity scoring and requirements extraction. |
| `jira-comment-writer` | Plain-language Jira comment drafter — translates technical updates into stakeholder language. |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code, generates well-formatted technical guides. |

---

## Agents

Autonomous agents that make decisions and take actions independently. Each exists in both Claude Code and OpenCode format.

### Development & DevOps

| Agent | Description | Skills |
|-------|-------------|--------|
| `tdd-agent` | Autonomous TDD — drives the complete RED-GREEN-REFACTOR cycle with strict guardrails. | tdd-cycle, tdd-implementer, tdd-refactor, tdd-verify |
| `code-review-agent` | Autonomous code review — security, correctness, performance, maintainability, style. | code-review-coach, security-review-trainer, pr-feedback-writer, automated-code-review |
| `test-generation-agent` | Autonomous test generation — analyzes code, identifies gaps, generates tests with TDD patterns. | tdd-implementer, tdd-cycle, test-scaffold |
| `documentation-agent` | Autonomous documentation sync — detects staleness, generates XML docs, updates READMEs. | architecture-journal, doc-sync |
| `dependency-audit-agent` | Autonomous dependency auditing — vulnerability scanning, license compliance, upgrade paths. | supply-chain-audit, technical-debt-assessor |
| `spec-extractor-agent` | Extracts structured agent specs from natural-language descriptions or existing code. | spec-coach |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code, generates formatted technical guides. | confluence-guide-writer |
| `migration-orchestrator` | Semi-autonomous migration orchestration — EF Core and .NET Framework migrations with approval gates. | ef-migration-manager, legacy-migration-analyzer |
| `environment-health-agent` | Autonomous environment health monitoring — Docker, services, connections, recovery. | environment-health |
| `task-decomposition-agent` | Meta-orchestrator — decomposes complex goals into sub-tasks, assigns to specialized agents. | task-decomposition |
| `pm-capture-agent` | Converts meeting transcripts, Slack summaries, and SOWs into structured capture documents. | |

### Domain-Specific

| Agent | Description | Skills |
|-------|-------------|--------|
| `model-optimization-agent` | Autonomous model optimization — quantization, format conversion, benchmarking for edge. | model-optimization |
| `sensor-anomaly-agent` | Autonomous sensor anomaly detection — statistical outliers, drift monitoring, recalibration. | anomaly-detection |
| `fleet-deployment-agent` | Semi-autonomous fleet deployment — canary, staged rollout, health gates, rollback. | fleet-management |
| `research-agent` | Autonomous research — multi-source investigation, credibility scoring, structured briefings. | research-synthesis |
| `context-builder-agent` | Autonomous context assembly — git change summarization, ADR matching, dependency mapping. | session-context |

### Language & Security

| Agent | Description |
|-------|-------------|
| `python-security-agent` | OWASP Python security review with bandit, pip-audit, and executive summary. |
| `python-federal-security-agent` | Federal Python security review — NIST 800-53, FISMA, FIPS compliance. |
| `rust-arch-checklist-agent` | Rust architecture review — ownership, trait design, error handling, unsafe audit, Clippy. |
| `rust-security-agent` | OWASP Rust security review with cargo-audit, cargo-deny, unsafe block audit. |
| `rust-migration-agent` | C/C++ to Rust migration analysis and Rust modernization planning. |

### Scaffolding

| Agent | Description |
|-------|-------------|
| `fastapi-scaffold-agent` | FastAPI endpoints with OpenAPI docs, Pydantic v2, JWT auth, rate limiting, health checks. |
| `axum-scaffold-agent` | Production-ready Axum APIs with utoipa OpenAPI, JWT middleware, rate limiting. |
| `python-feature-slice-agent` | Feature-based Python architecture with FastAPI routers, Pydantic v2, service layer. |
| `rust-feature-slice-agent` | Vertical slice modules for Rust/Axum with router, service trait, models, integration tests. |
| `cargo-package-scaffold-agent` | Rust crate scaffolding — Cargo.toml, CI, test harness, crates.io publish workflow. |
| `pypi-package-agent` | Python package scaffolding for PyPI — pyproject.toml, CI/CD, supply chain checks. |
| `alembic-migration-agent` | Full Alembic migration lifecycle with safety checks and rollback planning. |
| `sqlx-migration-agent` | SQLx migration lifecycle — create, review, rollback test, apply, regenerate offline cache. |

> RPI workflow subagents (`rpi-planner`, `rpi-implement`, `rpi-code-analyzer`, `rpi-file-locator`, `rpi-pattern-finder`) are spawned automatically by the RPI skills — not invoked directly.

---

## Commands

Nine slash commands per platform. Each injects live shell state before the model acts — the model sees real output, not a description of it.

| Command | Injects | What it does |
|---------|---------|--------------|
| `/tdd-cycle` | `dotnet test` output | Runs the TDD cycle against live failing tests |
| `/code-review` | `git diff` | Reviews staged or branch changes |
| `/security-review [path]` | — | OWASP security review scoped to a path |
| `/arch-review [component]` | — | Socratic architecture challenge |
| `/new-feature [FeatureName]` | Project structure, `.csproj` files | Scaffolds a vertical slice feature |
| `/migrate [MigrationName]` | `dotnet ef migrations list` | EF Core migration with safety checks |
| `/research [topic]` | — | Multi-source research briefing |
| `/context-prime` | `git log`, `git status`, `git diff` | Primes session from current repo state |
| `/grill-me [plan]` | — | Relentless one-question-at-a-time plan/design interview with recommended answers |

---

## Usage

```
/tdd-cycle                         # runs TDD cycle with live test output
/code-review                       # reviews git diff
/security-review src/              # OWASP scan scoped to src/
/arch-review OrderService          # Socratic challenge of a component
/new-feature CreateInvoice         # scaffold a vertical slice feature
/migrate AddInvoiceTable           # EF Core migration with safety checks
/research "WebSocket vs SSE"       # structured research briefing
/context-prime                     # session brief from git state

Use tdd-agent to implement a Calculator.add method
Use code-review-agent to review the latest changes
Use migration-orchestrator to plan the EF Core migration
Use research-agent to investigate WebSocket vs SSE for real-time updates
```

---

## Project Templates

The `project-templates/` directory contains per-project context files based on the **Four Prompt Disciplines & Five Primitives** framework by [Nate B. Jones](https://natesnewsletter.substack.com/). Copy the relevant files into your project root — see [`project-templates/README.md`](project-templates/README.md) for the full guide.

| File | Purpose | When to use |
|------|---------|-------------|
| `CLAUDE.md` / `AGENTS.md` | Project context: stack, architecture, key files, boot ritual | Every project |
| `intent.md` | What the agent optimizes for: goals, values, tradeoff hierarchy | Every project |
| `constraints.md` | Musts, must-nots, preferences, escalation triggers | Every project |
| `evals.md` | Test cases, CI gate definitions, taste rules, rejection log | Every project |
| `domain-memory.md` | Dark factory backlog and progress log | Multi-session agentic work only |
| `design.md` | Design system tokens, component hierarchy, interaction patterns | UI-heavy projects only |

---

## Repository Structure

```
ai-toolkit/
├── skills/                     # 83 skills (SKILL.md + references/ per skill)
├── claude/
│   ├── agents/                 # 35 Claude Code agent definitions
│   ├── commands/               # 8 slash commands with shell injection
│   └── global/                 # Global config → ~/.claude/
│       ├── CLAUDE.md           # Global instructions (every project)
│       ├── settings.json       # Hooks: credential stop + post-write build/lint gates
│       └── settings.local.json # Permissions: bash allow/deny, read allow/deny
├── opencode/
│   ├── agents/                 # 35 OpenCode agent definitions
│   ├── commands/               # 8 slash commands with agent routing
│   └── global/                 # Global config → ~/.config/opencode/
│       ├── AGENTS.md           # Global instructions (every project)
│       └── opencode.json       # Providers, MCP, permissions, temperatures
├── pi/
│   └── global/                 # Global config → ~/.pi/agent/
│       ├── AGENTS-lite.md      # 7B-safe global baseline (~25 rules)
│       ├── AGENTS.md           # 20B project overlay (~50 rules)
│       ├── models.json         # Ollama provider config
│       ├── settings.json       # Compaction tuned for local context windows
│       ├── Modelfile-7b        # Modelfile template for 7B models
│       └── Modelfile-20b       # Modelfile template for 20B models
├── project-templates/          # Per-project context files — copy to your project root
├── scripts/                    # Install scripts (Bash + PowerShell)
└── docs/                       # Supplementary documentation
```

---

## Author

**Michael K. Alber** — [github.com/michaelalber](https://github.com/michaelalber)

Software engineer working across enterprise .NET, Python, Rust, edge AI, robotics, and federal security domains. I build tools that encode engineering standards into AI-assisted workflows — grounding AI output in deliberate practice rather than generic defaults.

Related projects:
- [grounded-code-mcp](https://github.com/michaelalber/grounded-code-mcp) — local MCP RAG server that grounds AI coding agents in the books and standards you actually trust

---

## License

MIT — see [LICENSE](LICENSE) for details.
