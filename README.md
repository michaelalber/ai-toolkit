# AI Toolkit

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-93-blue)](#skills)
[![Agents](https://img.shields.io/badge/agents-51-blue)](#agents)
[![Tools](https://img.shields.io/badge/tools-pdf2md%20%7C%20web2md%20%7C%20code2md-blue)](#repository-structure)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20OpenCode%20%7C%20Pi-informational)](#platforms)

**93 skills, 51 agents, and 25 slash commands for AI-assisted software development — spanning TDD, .NET, Python, PHP, Rust, React, Vue, security, DDD, knowledge management, and more.**

> **Edge AI, robotics, ML, and industrial automation?** Those skills now live in the companion
> [edge-ai-robotics-automation-toolkit](../edge-ai-robotics-automation-toolkit) — install it alongside this one.

Works with [Claude Code](https://claude.ai/code), [OpenCode](https://opencode.ai/), and [Pi](https://pi.dev) (Ollama local models).

---

## Why I built this

I work across a wide range of domains — enterprise .NET, Python, Rust, edge AI, robotics, and federal security compliance. As AI coding assistants became central to my workflow, I found myself writing the same guidance over and over: how to run a proper TDD cycle, how to review code for OWASP compliance, how to scaffold a vertical slice feature correctly.

This toolkit encodes that expertise as reusable primitives. Each skill is an opinionated, structured prompt that reflects how I actually work — not a generic template. The result is an AI coding assistant that reasons the way I'd want a senior engineer to reason: with discipline, with domain knowledge, and with the right tradeoffs in mind.

**Design decisions:**
- **Three primitives, one toolkit** — skills (model-invoked expertise), agents (autonomous executors), commands (user-triggered with live shell context). Each has a distinct role.
- **Platform parity** — every skill and agent exists in both Claude Code and OpenCode format with identical behavior. Pi gets its own Ollama-optimized config.
- **Two-tier skill design** — full-template skills (5-section lean layout: philosophy, workflow, state, output-template pointers, integrations; depth such as principle tables, anti-patterns, and error recovery loads on demand from `references/`) for domain-expert tools; minimal-tier skills (≤ 100 lines, focused instructions) for mode switches and conversational tools.
- **Global + project layered config** — global standards apply everywhere; project-level files add specificity without duplicating the global.

---

## At a glance

| | Count |
|--|-------|
| Skills (team) | 81 |
| Skills (professional) | 12 |
| Agents (Claude Code) | 51 |
| Agents (OpenCode) | 51 |
| Slash commands (per platform) | 25 |
| Platforms | Claude Code, OpenCode, Pi |

---

## How it works

Three distinct primitives compose the toolkit:

**Skills** — Structured, opinionated prompt files that encode domain expertise. Model-invoked autonomously. Live in `skills/{team,professional}/<name>/SKILL.md`. Full-template skills follow a 5-section lean layout with depth in `references/`.

**Agents** — Autonomous executors that combine skills with tool access and guardrails. Operate independently within defined boundaries. Live in `claude/agents/` and `opencode/agents/`.

**Commands** — User-triggered slash commands (type `/command-name`) that inject live shell state before the model acts. Live in `claude/commands/` and `opencode/commands/`.

```
User types /tdd
    → command injects live dotnet test output
    → model reads failing tests
    → tdd skill drives RED-GREEN-REFACTOR
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
# Skills (both team and professional by default)
mkdir -p ~/.claude/skills
ln -sf /path/to/ai-toolkit/skills/team/*/ ~/.claude/skills/
ln -sf /path/to/ai-toolkit/skills/professional/*/ ~/.claude/skills/

# Agents
mkdir -p ~/.claude/agents
ln -sf /path/to/ai-toolkit/claude/agents/team/*.md ~/.claude/agents/
ln -sf /path/to/ai-toolkit/claude/agents/professional/*.md ~/.claude/agents/
```

To install only the team-facing skills (e.g. when sharing this with a colleague), omit the `professional/` lines.

See [`claude/global/README.md`](claude/global/README.md) for global config setup (hooks, permissions, commands).

> **Upgrade notice (2026-07-17) — if you installed `claude/global/` before this date, its hooks and
> secret deny-rules were not doing anything.** Two bugs made them silently inert, and neither
> produced an error, so the config reviewed as protective while enforcing nothing:
>
> - **No hook ever ran.** The `matcher` values used permission-rule syntax (`Bash(*)`,
>   `Write(*.cs)`). Matchers test the tool *name*, so those matched nothing. The hook bodies also
>   read `$CLAUDE_TOOL_INPUT_*` environment variables, which do not exist — had the matchers been
>   right, the guards would have failed *open* and allowed what they were meant to block.
> - **Secret deny-rules only covered the working directory.** `Read(**/.env)` matches at or under
>   cwd, not filesystem-wide. Working in any project directory left `~/.ssh`, `~/.aws`, `~/.npmrc`
>   and similar readable. The `//` prefix (`Read(//**/.env)`) is what makes a rule absolute.
>
> **To upgrade:** re-copy `settings.json` and `settings.local.json`, and install the new `hooks/`
> directory, per [`claude/global/README.md`](claude/global/README.md). Then run the verification
> checks in that file — a misconfigured hook is silent, so confirm rather than assume. Fixed in
> `957222c`.

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
ln -sf /path/to/ai-toolkit/skills/team/*/ ~/.config/opencode/skills/
ln -sf /path/to/ai-toolkit/skills/professional/*/ ~/.config/opencode/skills/

mkdir -p ~/.config/opencode/agents
ln -sf /path/to/ai-toolkit/opencode/agents/team/*.md ~/.config/opencode/agents/
ln -sf /path/to/ai-toolkit/opencode/agents/professional/*.md ~/.config/opencode/agents/

# Commands
mkdir -p ~/.config/opencode/commands
ln -sf /path/to/ai-toolkit/opencode/commands/*.md ~/.config/opencode/commands/
```

See [`opencode/global/README.md`](opencode/global/README.md) for provider config, Ollama tuning, and permissions.

### Pi (Ollama / Local Models)
```bash
bash scripts/install-pi.sh         # macOS / Linux — 7B-safe default
bash scripts/install-pi.sh --full  # macOS / Linux — 20B variant
```
```powershell
pwsh scripts/install-pi.ps1        # Windows — 7B-safe default
pwsh scripts/install-pi.ps1 -Full  # Windows — 20B variant
```
See [`pi/global/README.md`](pi/global/README.md) for the full Ollama setup guide — Modelfile config, compaction tuning, model selection by VRAM.

**Working local-first?** [`LOCAL-FIRST-WORKFLOW.md`](LOCAL-FIRST-WORKFLOW.md) is the methodology for running ~80% of coding work on a self-hosted ~30B model and escalating the hard 20% to a frontier cloud model — the routing rule, escalation triggers, the cost-of-being-wrong routing matrix, the refusal list
(work that no model tier should touch), portability discipline, and how to adjust prompting for
smaller local models. Its companion [`LOCAL-AI-CHEATSHEET.md`](LOCAL-AI-CHEATSHEET.md) is the tool picker — which local-AI tool (Pi, OpenCode, Open WebUI, Goose, …) to reach for per task.

### Other agent tools (`~/.agents/skills/`)

For any tool that discovers skills under the generic `~/.agents/skills/` directory, install the shared skills tree (both `team/` and `professional/`) with:

```bash
bash scripts/install-agents.sh        # macOS / Linux
```
```powershell
pwsh scripts/install-agents.ps1       # Windows
```

**Other AI tools** (Cursor, Windsurf, Copilot, etc.): [`AGENTS.md`](AGENTS.md) follows the universal agent instructions standard and is auto-discovered from the project root.

---

## Skills

This toolkit is organized in two folders. `skills/team/` contains skills and agents I use in production work and consider shareable — patterns extracted from years of enterprise .NET, legacy modernization, and AI-augmented development on regulated-industry codebases. It also incorporates several vendored workflow-primitive skills from Matt Pocock's repo (see [Companion Skills](#companion-skills) below). `skills/professional/` is my professional-development track: deliberate-practice loops that sharpen engineering judgment (architecture critique, code review, pattern selection, refactoring prioritization) and learning scaffolds for the professional domains I'm actively growing into. (Edge AI, ML, robotics, and automation skills — including model optimization — now live in the companion [edge-ai-robotics-automation-toolkit](../edge-ai-robotics-automation-toolkit).) These are career-skill investments, not side projects — the split keeps "what I ship for the team" distinct from "the competencies I'm deliberately building."

## Companion Skills

This toolkit incorporates several skills from Matt Pocock's [skills repo](https://github.com/mattpocock/skills) alongside my own. Vendored copies carry `source: mattpocock/skills` in their frontmatter along with the upstream commit hash they were pulled from, so the provenance is traceable. Matt updates frequently — periodically check his repo and re-vendor when meaningful changes land.

Matt's skills cover the **workflow primitives** that apply to any project regardless of stack: grilling a plan until it's coherent (`grill-me`), zooming out to understand a call chain (`zoom-out`), and improving a codebase's module structure (`improve-codebase-architecture`). They're small, composable, and deliberately stack-agnostic — exactly the layer my own skills don't try to replicate.

The skills I've written cover the **domain-specific layers** that sit on top: enterprise .NET patterns (vertical slice, CQRS, EF Core migrations, federal-compliance security review), AI/ML infrastructure (RAG pipelines, MCP server scaffolding, local LLM workflows, model optimization), and the coaching loops in my professional-development track that build architectural and review judgment.

The two layers are non-overlapping by design. Where they look adjacent — his `improve-codebase-architecture` vs. my `architecture-review` — each is solving a different layer. Matt's is the workflow primitive; mine is the domain-calibrated, opinionated version for a specific stack or practice context.

See `.matt-pocock-attribution.yml` at the repo root for the full provenance manifest, including modification notes for each vendored skill.

## skills/team/

### TDD Suite

| Skill | Description |
|-------|-------------|
| `tdd` | Canonical RED-GREEN-REFACTOR inner loop — the one TDD skill. Enforces behavioral, structure-insensitive tests, prohibits horizontal slicing, and carries GREEN strategies + per-language idioms and the REFACTOR smell catalog in its `references/`. |
| `tdd-agent` | Operating mode: AI drives all phases autonomously with strict guardrails and verification at each step. Defers to `tdd` for the loop. |
| `evaluate-tests` | Audits existing tests in two modes — test-file quality (prioritized rewrite list) and TDD compliance (commit-history scorecard + anti-patterns). |

### Enterprise .NET Suite

| Skill | Description |
|-------|-------------|
| `dotnet-vertical-slice` | Scaffold vertical slice architecture with CQRS + FreeMediator + optional Telerik Blazor UI generation. |
| `ef-migration-manager` | EF Core migration lifecycle with safety checks, data loss detection, SQL review, and rollback verification. |
| `nuget-package-scaffold` | NuGet package creation with multi-targeting, CI/CD pipelines, and semantic versioning. |
| `legacy-migration-analyzer` | .NET Framework to .NET 10 migration analysis with risk scoring, upgrade strategies, and incremental patterns. |
| `dotnet-architecture-checklist` | .NET architecture review — detects style and grades both layered/N-tier controller APIs and vertical-slice CQRS/Blazor. |
| `dotnet-security-review` | OWASP-based .NET security review with Telerik specialization and manager-friendly reporting. |
| `security-review-federal` | Shared, language-agnostic federal/gov overlay for any base security review — NIST 800-53, FIPS 140-2/3, CUI, POA&M, EO 14028, DOE 205.1B. |
| `oss-vetting` | OSS library vetting and SBOM analysis for federal contractor environments (LANL/DOE/CUI) — security posture, supply chain risk, license compliance, and CUI suitability against four governing frameworks; Confluence-ready report. |
| `minimal-api-scaffolder` | .NET 10 minimal API scaffolding with OpenAPI documentation, versioning, and security patterns. |
| `dotnet-controller-api-scaffolder` | Controller-based ASP.NET Core Web API scaffolding that detects and conforms to an existing codebase's conventions (base controller, validation, service/mediator boundary, response shape). |
| `4d-schema-migration` | 4D (4th Dimension) to SQL Server/EF Core/Blazor full-stack migration specialist. |
| _(planned)_ `shared-kernel-generator` | .NET shared kernel scaffolding — not yet implemented. |

### Python Suite

| Skill | Description |
|-------|-------------|
| `python-architecture-checklist` | Python architecture checklist executor — clean-arch boundaries, type safety, complexity, config/secrets; graded report with ruff/mypy/radon evidence. |
| `python-security-review` | OWASP-based Python security review (FastAPI, Django, Flask) with bandit and pip-audit. |
| `python-feature-slice` | Feature-based Python architecture using FastAPI routers, Pydantic v2, and a service layer. |
| `alembic-migration-manager` | Full Alembic migration lifecycle with safety checks and rollback planning. |
| `python-modernization-analyzer` | Legacy Python modernization — Python 2→3, sync→async, Flask→FastAPI paths. |
| `fastapi-scaffolder` | FastAPI endpoints with OpenAPI docs, Pydantic v2, JWT auth, rate limiting, and health checks. |
| `pypi-package-scaffold` | Python package scaffolding for PyPI — pyproject.toml, CI/CD, test harness, supply chain checks. |

### PHP Suite

| Skill | Description |
|-------|-------------|
| `php-architecture-checklist` | PHP/Laravel architecture checklist executor — service-layer boundaries, strict typing, input validation, query safety, config/secrets; graded report with phpstan/php-cs-fixer evidence. |
| `php-security-review` | OWASP-based PHP/Laravel security review — mass-assignment, query injection, Blade XSS, auth/session, file uploads; composer audit + psalm/phpstan; graded manager-friendly report. |
| `php-feature-slice` | Feature-based Laravel architecture — feature folders, thin controllers, Form Requests, service/action layer, API Resources, structural CQRS. |
| `php-api-scaffolder` | Laravel API endpoints with API Resources, Form Request validation, Sanctum auth, throttle rate limiting, URI versioning, OpenAPI, and health checks. |
| `php-package-scaffold` | Composer package scaffolding for Packagist — composer.json, PSR-4, Pest/PHPUnit harness, GitHub Actions matrix CI, semver tag publish workflow. |
| `php-migration-manager` | Full Laravel migration lifecycle — tested down(), expand-contract for zero-downtime, dangerous-operation guards, batched backfills. |

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

### React Suite

| Skill | Description |
|-------|-------------|
| `react-architecture-checklist` | React architecture checklist executor — hooks discipline, effect correctness, component cohesion, state placement, render performance, type safety, accessibility; graded report with eslint/tsc evidence. |
| `react-security-review` | OWASP-based React/TypeScript front-end security review — XSS escape hatches, bundle-secret exposure, token storage, CSP, open redirects; npm audit + eslint-plugin-security; graded manager-friendly report. |
| `react-feature-slice` | Feature-based React architecture — feature folders, presentational + container components, custom hooks, a typed data layer, and structural CQRS (query vs mutation hooks). |
| `react-component-scaffolder` | Single React component/route scaffolding — typed props, co-located RTL test, accessibility baseline, optional Storybook story. |
| `react-app-scaffolder` | Vite + React + TypeScript app skeleton — strict TS, Vitest + RTL, ESLint (hooks + a11y), router, error boundary, feature-folder layout. |
| `react-modernization-analyzer` | Legacy React modernization — class→hooks, CRA→Vite, React 17→18→19, JS→TS, Enzyme→RTL, legacy Redux→RTK paths (assess & plan, no execution). |

### Vue Suite

| Skill | Description |
|-------|-------------|
| `vue-architecture-checklist` | Vue architecture checklist executor — reactivity discipline, watcher/lifecycle correctness, component cohesion, state placement, render performance, type safety, accessibility; graded report with eslint/vue-tsc evidence. |
| `vue-security-review` | OWASP-based Vue/TypeScript front-end security review — v-html XSS, bundle-secret exposure, token storage, CSP, open redirects; npm audit + eslint-plugin-security; graded manager-friendly report. |
| `vue-feature-slice` | Feature-based Vue architecture — feature folders, presentational + container SFCs, composables, a typed data layer, and structural CQRS (query vs mutation composables). |
| `vue-component-scaffolder` | Single Vue SFC/route scaffolding — typed defineProps, co-located Vue Testing Library test, accessibility baseline, optional Storybook story. |
| `vue-app-scaffolder` | Vite + Vue + TypeScript app skeleton — strict TS, Vitest + Vue Testing Library, ESLint (vue + a11y), router, app-level error handling, feature-folder layout. |
| `vue-modernization-analyzer` | Legacy Vue modernization — Options→Composition API, Vue CLI→Vite, Vue 2→3, JS→TS, Vue Test Utils v1→Vitest+VTL, Vuex→Pinia paths (assess & plan, no execution). |

### AI/ML Bridge Suite

> Moved to the companion **[edge-ai-robotics-automation-toolkit](../edge-ai-robotics-automation-toolkit)** —
> RAG pipelines (`rag-pipeline-python`, `rag-pipeline-dotnet`), `mcp-server-scaffold`, and
> `ollama-model-workflow` now ship there alongside the edge-AI, robotics, and automation skills.

### QRSPI Workflow Suite

A structured Questions → Research → Spec → Plan → Implement loop — the instruction-budget-disciplined
replacement for RPI. Correct behavior is the default through artifact gates (no magic words): each phase
refuses to run until the prior artifact exists. Driven by the `qrspi-orchestrator` (alignment) and
`qrspi-implement` (execution) agents, with shared read-only `research-*` subagents. Artifacts co-locate in
`thoughts/shared/qrspi/YYYY-MM-DD-{slug}/`.

| Skill | Description |
|-------|-------------|
| `qrspi-questions` | Surfaces what the agent doesn't know as targeted technical questions; stops for human answers before research. |
| `qrspi-research` | Ticket-hidden codebase research — spawns the `research-*` subagents in parallel, writes objective facts only (no recommendations). |
| `qrspi-spec` | Design Brain-Dump → human "brain-surgery" alignment loop → vertical-slice Structure Outline. |
| `qrspi-plan` | Converts the spec into a vertically-sliced tactical plan; refuses horizontal-layer plans. |
| `qrspi-implement` | Executes an approved plan slice-by-slice through strict Red-Green-Refactor, checkpointing per slice. |

### QRASPI Workflow Suite

A structured Questions → Research → Architecture → Skeleton → Plan → Implement loop for **new systems** —
the greenfield (V0/V1) counterpart to QRSPI. Where QRSPI maps an existing codebase and grows a feature,
QRASPI maps a problem domain, locks the path-dependent decisions as MADR ADRs (with alternatives) +
Mermaid C4, lands a runnable **walking skeleton** with fitness functions as merge-blocking CI gates,
grows it slice-by-slice with Red-Green-Refactor, then **graduates** the result to QRSPI once real
features begin. Same no-magic-words artifact gates; the Skeleton's exit gate is CI green, not a claim.
Driven by the `qraspi-orchestrator` (no-edit Q/R/A/P/graduate) and `qraspi-builder` (edit
Skeleton/Implement) agents. Artifacts co-locate in `thoughts/shared/qraspi/YYYY-MM-DD-{slug}/`; accepted
ADRs live in the target repo's `docs/adr/`.

| Skill | Description |
|-------|-------------|
| `qraspi-questions` | Surfaces unknowns across the six greenfield categories (functional · quality attributes · integration · compliance · deployment · domain); stops for human answers. |
| `qraspi-research` | Maps the solution landscape (external-domain via `research-synthesis`, or inherited-repo via the `research-*` subagents) — factual, no recommendations. |
| `qraspi-architecture` | Locks path-dependent decisions as MADR ADRs with ≥ 2 alternatives (align-before-lock), draws the C4 in Mermaid, and specifies the required fitness functions. |
| `qraspi-skeleton` | Scaffolds a runnable walking skeleton from the ADRs (one slice through every layer) and lands the fitness functions as CI gates; the exit gate is CI green. |
| `qraspi-plan` | Converts the next slice from the skeleton's backlog into a vertically-sliced `plan-{slice}.md`; refuses horizontal-layer plans. |
| `qraspi-implement` | Grows the green skeleton one approved slice at a time with Red-Green-Refactor, keeping the fitness gates green; checkpoints per slice. |
| `qraspi-graduate` | Terminal handoff — captures the repo + ADRs + skeleton state + fitness gates + stack into `graduation.md` and hands new feature work to QRSPI. |
| `fitness-functions` | Authors architectural fitness functions and wires them into CI as merge-blocking gates (NetArchTest, import-linter, cargo-deny, Conftest). QRASPI's one new primitive. |

### Requirements & Workflow Suite

| Skill | Description |
|-------|-------------|
| `capture-consolidate` | Consolidates multiple capture documents (transcripts, emails, SOWs) into a unified requirements registry. |
| `email-capture` | Extracts requirements, decisions, and action items from email threads and converts them to structured captures. |
| `transcript-capture` | Converts meeting transcripts or Zoom/Slack summaries into structured capture documents. |
| `domain-model` | DDD domain modeling consultant — enforces CONTEXT.md vocabulary, surfaces code/plan contradictions, records decisions as ADRs sparingly. |

### Docs, Jira & Confluence

| Skill | Description |
|-------|-------------|
| `jira-review` | Jira ticket review with complexity scoring and requirements extraction. |
| `jira-comment-writer` | Plain-language Jira comment drafter — translates technical updates into stakeholder language. |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code, generates well-formatted technical guides. |

### Knowledge Management Suite (PARA)

The PARA method (Tiago Forte) applied to documents across local folders, OneDrive/Teams synced
paths, and Confluence/Jira. Both skills share a per-project `.para.yml` config and the
actionability-first classification model (Projects → Areas → Resources → Archives).

| Skill | Description |
|-------|-------------|
| `para-file` | Captures and files one incoming document into PARA by actionability — scaffolds the P/A/R/Archive tree if missing, classifies, summarizes + tags, and files via the matching backend (filesystem, OneDrive/Teams, Confluence, or Jira). User-invocable via `/para-file`. |
| `para-review` | Periodic PARA review — hygiene audit (misfiled/stale/archivable/empty), the weekly review ritual, change summarization, and safe reversible archiving of completed/inactive items. User-invocable via `/para-review`. |

### Agent Design & Meta

| Skill | Description |
|-------|-------------|
| `skill-creator` | Creates, revises, and scores SKILL.md definitions against the 5-section lean gold standard. |

### Agent Support Suite (Team)

| Skill | Description | Used By |
|-------|-------------|---------|
| `automated-code-review` | Autonomous review checklists — security, correctness, performance, maintainability, style | code-review-agent |
| `test-scaffold` | Test generation conventions, AAA naming, mock patterns for FreeMediator/repositories | test-generation-agent |
| `doc-sync` | Documentation staleness detection, XML doc generation, README sync | documentation-agent |
| `supply-chain-audit` | NuGet/npm/pip vulnerability scanning, license matrix, CVE correlation | dependency-audit-agent |
| `environment-health` | Docker health checks, service monitoring, container lifecycle | environment-health-agent |
| `research-synthesis` | Multi-source cross-referencing, source credibility scoring, briefing formats | research-agent |
| `session-context` | Git change summarization, ADR relevance matching, pattern applicability | context-builder-agent |
| `task-decomposition` | Goal breakdown heuristics, dependency DAGs, sub-agent assignment protocols | task-decomposition-agent |

### Workflow Primitives (vendored from mattpocock/skills)

Vendored copies of workflow-primitive skills from [Matt Pocock's skills repo](https://github.com/mattpocock/skills). Each carries `source: mattpocock/skills` in its frontmatter. See [Companion Skills](#companion-skills) for the rationale and re-vendoring guidance.

| Skill | Description | Upstream path |
|-------|-------------|---------------|
| `grill-me` | Relentless plan/design interview — one question at a time with recommended answers. | `skills/productivity/grill-me/SKILL.md` |
| `zoom-out` | Map callers, dependents, and module relationships before continuing. | `skills/engineering/zoom-out/SKILL.md` |
| `improve-codebase-architecture` | Deep module refactoring using APOSD vocabulary — eliminates shallow modules, information leakage, naming mismatches. | `skills/engineering/improve-codebase-architecture/SKILL.md` |
| `codebase-design` | Shared deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) that `improve-codebase-architecture` names problems with. | `skills/engineering/codebase-design/SKILL.md` |

---

## skills/professional/

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
| `spec-coach` | Interactive spec design coach — vision, PRD structure, INVEST story quality, specification by example, three-tier guardrails. |

### Writing & Portfolio

| Skill | Description |
|-------|-------------|
| `substack-writer` | Multi-pass editorial pipeline that shapes the author's raw technical notes into publication-quality Substack/blog posts — keeps the human as the source of technical substance and applies editorial craft rather than generating generic filler. |

---

## Agents

Autonomous agents that make decisions and take actions independently. Each exists in both Claude Code (`claude/agents/`) and OpenCode (`opencode/agents/`) format. Agents are split into `team/` and `professional/` subdirectories mirroring the skill split.

## claude/agents/team/ and opencode/agents/team/ (45 agents)

### Development & DevOps

| Agent | Description | Skills |
|-------|-------------|--------|
| `tdd-agent` | Autonomous TDD — drives the complete RED-GREEN-REFACTOR cycle with strict guardrails. | tdd, evaluate-tests |
| `code-review-agent` | Autonomous code review — security, correctness, performance, maintainability, style. | code-review-coach, security-review-trainer, pr-feedback-writer, automated-code-review |
| `test-generation-agent` | Autonomous test generation — analyzes code, identifies gaps, generates tests with TDD patterns. | tdd, test-scaffold |
| `documentation-agent` | Autonomous documentation sync — detects staleness, generates XML docs, updates READMEs. | architecture-journal, doc-sync |
| `dependency-audit-agent` | Autonomous dependency auditing — vulnerability scanning, license compliance, upgrade paths. | supply-chain-audit, technical-debt-assessor |
| `spec-extractor-agent` | Extracts structured agent specs from natural-language descriptions or existing code. | spec-coach |
| `confluence-guide-writer` | Reads Confluence spec pages and/or source code, generates formatted technical guides. | confluence-guide-writer |
| `migration-orchestrator` | Semi-autonomous migration orchestration — EF Core and .NET Framework migrations with approval gates. | ef-migration-manager, legacy-migration-analyzer |
| `environment-health-agent` | Autonomous environment health monitoring — Docker, services, connections, recovery. | environment-health |
| `task-decomposition-agent` | Meta-orchestrator — decomposes complex goals into sub-tasks, assigns to specialized agents. | task-decomposition |
| `pm-capture-agent` | Converts meeting transcripts, Slack summaries, and SOWs into structured capture documents. | transcript-capture, email-capture, capture-consolidate |
| `research-agent` | Autonomous research — multi-source investigation, credibility scoring, structured briefings. | research-synthesis |
| `context-builder-agent` | Autonomous context assembly — git change summarization, ADR matching, dependency mapping. | session-context |

### Language & Security

| Agent | Description |
|-------|-------------|
| `python-security-agent` | OWASP Python security review with bandit, pip-audit, and executive summary. |
| `python-federal-security-agent` | Federal Python security review — NIST 800-53, FISMA, FIPS compliance. |
| `python-modernization-agent` | Legacy Python modernization analysis — Python 2→3, sync→async, Flask→FastAPI. |
| `rust-arch-checklist-agent` | Rust architecture review — ownership, trait design, error handling, unsafe audit, Clippy. |
| `rust-security-agent` | OWASP Rust security review with cargo-audit, cargo-deny, unsafe block audit. |
| `rust-migration-agent` | C/C++ to Rust migration analysis and Rust modernization planning. |
| `react-arch-checklist-agent` | React architecture review — hooks discipline, effects, state placement, render perf, type safety, accessibility. |
| `react-security-agent` | OWASP React/front-end security review — XSS, bundle secrets, token storage, npm audit, executive summary. |
| `react-modernization-agent` | Legacy React modernization analysis — class→hooks, CRA→Vite, React 17→18→19, JS→TS, Enzyme→RTL. |
| `vue-arch-checklist-agent` | Vue architecture review — reactivity discipline, watchers, state placement, render perf, type safety, accessibility. |
| `vue-security-agent` | OWASP Vue/front-end security review — v-html XSS, bundle secrets, token storage, npm audit, executive summary. |
| `vue-modernization-agent` | Legacy Vue modernization analysis — Options→Composition API, Vue CLI→Vite, Vue 2→3, JS→TS, Vuex→Pinia. |
| `oss-vetting-agent` | Federal OSS/SBOM vetting — scores a package across security, supply chain, maintainership, license, and CUI suitability against EO 14028/SSDF/800-171/800-161; Confluence-ready Approve / Approve-with-conditions / Reject report. |

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
| `php-feature-slice-agent` | Feature-based Laravel architecture — feature folders, thin controllers, Form Requests, service layer, API Resources. |
| `php-api-scaffold-agent` | Laravel API endpoints — API Resources, Sanctum auth, throttle rate limiting, URI versioning, OpenAPI, health checks. |
| `php-package-agent` | Composer package scaffolding for Packagist — composer.json, PSR-4, matrix CI, semver tag publish workflow. |
| `php-migration-agent` | Full Laravel migration lifecycle — tested down(), expand-contract, dangerous-operation guards, batched backfills. |
| `react-feature-slice-agent` | Feature-based React architecture — feature folders, presentational + container components, custom hooks, typed data layer, structural CQRS. |
| `react-component-scaffold-agent` | Single React component/route — typed props, co-located RTL test, accessibility baseline, optional Storybook story. |
| `react-app-scaffold-agent` | Vite + React + TS app skeleton — strict TS, Vitest + RTL, ESLint (hooks + a11y), router, error boundary, feature-folder layout. |
| `vue-feature-slice-agent` | Feature-based Vue architecture — feature folders, presentational + container SFCs, composables, typed data layer, structural CQRS. |
| `vue-component-scaffold-agent` | Single Vue SFC/route — typed defineProps, co-located Vue Testing Library test, accessibility baseline, optional Storybook story. |
| `vue-app-scaffold-agent` | Vite + Vue + TS app skeleton — strict TS, Vitest + Vue Testing Library, ESLint (vue + a11y), router, app-level error handling, feature-folder layout. |

> QRSPI workflow agents (`qrspi-orchestrator`, `qrspi-implement`) and the shared read-only research subagents (`research-file-locator`, `research-code-analyzer`, `research-pattern-finder`) are spawned automatically by the QRSPI skills/commands — not invoked directly.
>
> QRASPI greenfield agents (`qraspi-orchestrator`, `qraspi-builder`) are spawned automatically by the QRASPI skills/commands — the orchestrator drives the no-edit Questions/Research/Architecture/Plan/Graduate phases, the builder the edit Skeleton/Implement phases. They reuse the same `research-*` subagents.

---

## Commands

Twenty-five slash commands per platform. Each injects live shell state before the model acts — the model sees real output, not a description of it.

| Command | Injects | What it does |
|---------|---------|--------------|
| `/tdd` | `dotnet test` output | Runs the TDD cycle against live failing tests |
| `/evaluate-tests [path]` | — | Audits existing tests: test-file quality (coupling, fragility, theater) and TDD compliance (commit-history scorecard) |
| `/code-review` | `git diff` | Reviews staged or branch changes |
| `/security-review [path]` | — | OWASP security review scoped to a path |
| `/oss-vetting [package@version]` | Detected dependency manifests | Vets an OSS/third-party package for federal use (LANL/DOE/CUI) — Approve / conditions / Reject report |
| `/arch-review [component]` | — | Socratic architecture challenge |
| `/new-feature [FeatureName]` | Project structure, `.csproj` files | Scaffolds a vertical slice feature |
| `/migrate [MigrationName]` | `dotnet ef migrations list` | EF Core migration with safety checks |
| `/research [topic]` | — | Multi-source research briefing |
| `/context-prime` | `git log`, `git status`, `git diff` | Primes session from current repo state |
| `/grill-me [plan]` | — | Relentless one-question-at-a-time plan/design interview with recommended answers |
| `/qrspi-questions [feature]` | `ls` of the feature folder | Surfaces open technical questions; stops for human answers before research |
| `/qrspi-research [feature]` | `ls` of the feature folder | Ticket-hidden parallel codebase research → objective `research.md` |
| `/qrspi-spec [feature]` | `ls` of the feature folder | Design Brain-Dump → brain-surgery loop → vertical-slice Structure Outline |
| `/qrspi-plan [feature]` | `ls` of the feature folder | Vertically-sliced tactical plan; refuses horizontal-layer plans |
| `/qrspi-implement [feature]` | Feature folder + existing slice logs | Executes an approved plan slice-by-slice with Red-Green-Refactor |
| `/qraspi-questions [project]` | `ls` of the qraspi project folders | Surfaces unknowns across the six greenfield categories; stops for human answers |
| `/qraspi-research [project]` | `ls` of the qraspi project folders | Maps the solution landscape (factual, no recommendations) |
| `/qraspi-architecture [project]` | `ls` of the qraspi project folders | Locks decisions as MADR ADRs + Mermaid C4; specifies fitness functions |
| `/qraspi-skeleton [project]` | `ls` of the qraspi project folders | Scaffolds a runnable walking skeleton with fitness-gate CI; exit gate is CI green |
| `/qraspi-plan [project]` | `ls` of the qraspi project folders | Plans the next backlog slice; refuses horizontal-layer plans |
| `/qraspi-implement [project]` | `ls` of the qraspi project folders | Grows the skeleton one approved slice at a time with Red-Green-Refactor |
| `/qraspi-graduate [project]` | `ls` of the qraspi project folders | Terminal QRASPI→QRSPI handoff — writes `graduation.md` |

---

## Usage

```
/tdd                               # runs TDD cycle with live test output
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
├── skills/
│   ├── team/                   # 81 team skills (shareable, production-ready)
│   └── professional/           # 12 professional skills (deliberate practice)
├── claude/
│   ├── agents/
│   │   └── team/               # 51 Claude Code team agents
│   ├── commands/               # 25 slash commands with shell injection
│   └── global/                 # Global config → ~/.claude/
│       ├── CLAUDE.md           # Global instructions (every project)
│       ├── settings.json       # Hooks: credential stop + post-write build/lint gates
│       └── settings.local.json # Permissions: bash allow/deny, read allow/deny
├── opencode/
│   ├── agents/
│   │   └── team/               # 51 OpenCode team agents
│   ├── commands/               # 25 slash commands with agent routing
│   └── global/                 # Global config → ~/.config/opencode/
│       ├── AGENTS.md           # Global instructions (every project)
│       └── opencode.json       # Providers, MCP, permissions, temperatures
├── pi/
│   └── global/                 # Global config → ~/.pi/agent/
│       ├── AGENTS-7b.md        # Standalone 7B global (~25 rules, self-contained)
│       ├── AGENTS-20b.md       # Standalone 20B+ global (full rules + collection map)
│       ├── models.json         # Ollama provider config
│       ├── settings.json       # Compaction tuned for local context windows
│       ├── Modelfile-7b        # Modelfile template for 7B models
│       └── Modelfile-20b       # Modelfile template for 20B models
├── project-templates/          # Per-project context files — copy to your project root
├── scripts/                    # Install scripts (Bash + PowerShell)
├── tools/                      # Standalone utilities (not skills/agents/commands)
│   ├── pdf2md/                 # PDF → Markdown converter for RAG ingestion
│   ├── web2md/                 # Web pages & docs sites → Markdown for RAG ingestion
│   └── code2md/                # Codebase → language-tagged Markdown for RAG ingestion
└── docs/                       # Supplementary documentation
```

---

## Author

**Michael K. Alber** — [codeberg.org/michaelkalber](https://codeberg.org/michaelkalber)

Software engineer working across enterprise .NET, Python, Rust, edge AI, robotics, and federal security domains. I build tools that encode engineering standards into AI-assisted workflows — grounding AI output in deliberate practice rather than generic defaults.

Related projects:
- [grounded-code-mcp](https://codeberg.org/michaelkalber/grounded-code-mcp) — local RAG server that grounds AI coding agents in the books, standards, and docs you actually trust; 17 curated collections, fully local embeddings via Ollama
- [pi-packages](https://codeberg.org/michaelkalber/pi-packages) — domain-specific Pi harnesses for local Ollama inference: hardware routing, RAG integration, context budgeting, and project-type auto-detection across six project types

---

## License

MIT — see [LICENSE](LICENSE) for details.
