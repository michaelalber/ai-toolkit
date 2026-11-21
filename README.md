# AI Toolkit

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-78-blue)](#skills)
[![Agents](https://img.shields.io/badge/agents-51-blue)](#agents)
[![Commands](https://img.shields.io/badge/commands-22-blue)](#commands)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20OpenCode%20%7C%20Pi-informational)](#install)

**78 skills, 51 agents, and 22 slash commands for AI-assisted software development** — TDD,
structured feature workflows, and architecture/security/scaffolding families for .NET, Python, PHP,
Rust, React, and Vue. Works with [Claude Code](https://claude.ai/code), [OpenCode](https://opencode.ai/),
and [Pi](https://pi.dev).

> Edge AI, ML, robotics, and industrial automation skills live in the companion
> [edge-ai-robotics-automation-toolkit](../edge-ai-robotics-automation-toolkit).

---

## Why

I kept writing the same guidance for AI coding assistants: how to run a real TDD cycle, how to review
for OWASP, how to scaffold a vertical slice. This toolkit encodes that guidance as reusable,
opinionated prompts so the assistant reasons the way I'd want a senior engineer to — with discipline,
domain knowledge, and explicit tradeoffs.

## How it works

| Primitive                                                   | Invoked by               | Lives in                                                    |
| ----------------------------------------------------------- | ------------------------ | ----------------------------------------------------------- |
| **Skills** — domain expertise as structured prompts         | the model, automatically | `skills/<name>/SKILL.md` (+ `references/` loaded on demand) |
| **Agents** — autonomous executors with tools and guardrails | you or another agent     | `claude/agents/`, `opencode/agents/` (kept in parity)       |
| **Commands** — `/name` that injects live shell state first  | you                      | `claude/commands/`, `opencode/commands/`                    |

```
/tdd → injects live test output → tdd-loop skill drives RED-GREEN-REFACTOR → hooks build after each write
```

Global config (`claude/global/`, `opencode/global/`, `pi/global/`) sets standards for every project;
[`project-templates/`](project-templates/README.md) adds per-project context on top.

---

## Install

|          | Claude Code | OpenCode | Pi                                                                                        |
| -------- | ----------- | -------- | ----------------------------------------------------------------------------------------- |
| Skills   | ✅          | ✅       | ✅ (`/skill:<name>`)                                                                      |
| Commands | ✅          | ✅       | ✅ as prompt templates (no `!` shell injection)                                           |
| Agents   | ✅          | ✅       | ❌ no subagents — QRSPI/QRASPI phases are artifact-gated, so you drive them one at a time |

```bash
bash scripts/install-claude.sh     # → ~/.claude (respects CLAUDE_CONFIG_DIR)
bash scripts/install-opencode.sh   # → ~/.config/opencode
bash scripts/install-pi.sh         # → ~/.pi/agent
bash scripts/install-agents.sh     # → ~/.agents/skills (Goose, Open WebUI, other tools)
```

PowerShell equivalents (`*.ps1`) sit next to each script. Re-running a script removes skills,
agents, and commands deleted from the repo; skills you added by hand are kept.

The scripts install skills, agents, and commands only. **Global config is a manual step** — see each
platform's guide:

- [`claude/global/README.md`](claude/global/README.md) — `CLAUDE.md`, hooks, permissions. Run its
  verification checks: a misconfigured hook fails silently.
- [`opencode/global/README.md`](opencode/global/README.md) — providers, Ollama tuning, permissions.
- [`pi/global/README.md`](pi/global/README.md) — Ollama setup, context length, model choice.

Other tools (Cursor, Windsurf, Copilot) read the root [`AGENTS.md`](AGENTS.md).

Running mostly on local models? See [`docs/LOCAL-FIRST-WORKFLOW.md`](docs/LOCAL-FIRST-WORKFLOW.md)
(when to escalate to a cloud model) and [`docs/LOCAL-AI-CHEATSHEET.md`](docs/LOCAL-AI-CHEATSHEET.md)
(which local tool for which task).

---

## Skills

One line per skill; the `SKILL.md` frontmatter says exactly when each one triggers.

### Workflows

| Skill                 | Purpose                                         |
| --------------------- | ----------------------------------------------- |
| `tdd-loop`            | The canonical RED-GREEN-REFACTOR loop           |
| `evaluate-tests`      | Audit test quality and TDD compliance           |
| `qrspi-questions`     | QRSPI (existing codebase) 1/5: surface unknowns |
| `qrspi-research`      | 2/5: ticket-hidden codebase research            |
| `qrspi-spec`          | 3/5: design brain-dump → structure outline      |
| `qrspi-plan`          | 4/5: vertically sliced plan                     |
| `qrspi-implement`     | 5/5: execute the plan slice by slice            |
| `qraspi-questions`    | QRASPI (new system) 1/7: surface unknowns       |
| `qraspi-research`     | 2/7: map the solution landscape                 |
| `qraspi-architecture` | 3/7: MADR ADRs + Mermaid C4                     |
| `qraspi-skeleton`     | 4/7: walking skeleton, CI green                 |
| `qraspi-plan`         | 5/7: plan the next slice                        |
| `qraspi-implement`    | 6/7: grow the skeleton slice by slice           |
| `qraspi-graduate`     | 7/7: hand off to QRSPI                          |
| `fitness-functions`   | Architecture rules as CI gates                  |

### Language families

Each language has the same set: architecture checklist, security review, feature slice,
scaffolders, migrations, and a modernization analyzer.

| Skill                              | Purpose                                           |
| ---------------------------------- | ------------------------------------------------- |
| `dotnet-architecture-checklist`    | Grade a .NET solution (layered or vertical slice) |
| `dotnet-security-review`           | OWASP review, Telerik-aware                       |
| `dotnet-vertical-slice`            | CQRS + FreeMediator feature slice                 |
| `dotnet-controller-api-scaffolder` | Controller API that matches existing conventions  |
| `minimal-api-scaffolder`           | .NET Minimal API endpoints                        |
| `ef-migration-manager`             | EF Core migrations with safety checks             |
| `nuget-package-scaffold`           | NuGet package + CI                                |
| `legacy-migration-analyzer`        | .NET Framework → .NET 10 plan                     |
| `python-architecture-checklist`    | Grade a Python codebase                           |
| `python-security-review`           | OWASP review with bandit, pip-audit               |
| `python-feature-slice`             | FastAPI feature slice                             |
| `fastapi-scaffolder`               | FastAPI endpoints                                 |
| `alembic-migration-manager`        | Alembic migrations                                |
| `pypi-package-scaffold`            | PyPI package + CI                                 |
| `python-modernization-analyzer`    | Python upgrade / migration plan                   |
| `php-architecture-checklist`       | Grade a PHP/Laravel codebase                      |
| `php-security-review`              | OWASP review for PHP/Laravel                      |
| `php-feature-slice`                | Laravel feature slice                             |
| `php-api-scaffolder`               | Laravel API endpoints                             |
| `php-migration-manager`            | Laravel migrations                                |
| `php-package-scaffold`             | Composer package + CI                             |
| `rust-architecture-checklist`      | Grade a Rust codebase                             |
| `rust-security-review`             | OWASP review + `unsafe` audit                     |
| `rust-feature-slice`               | Axum feature slice                                |
| `axum-scaffolder`                  | Axum endpoints                                    |
| `sqlx-migration-manager`           | SQLx migrations                                   |
| `cargo-package-scaffold`           | Crate + CI + crates.io publish                    |
| `rust-migration-analyzer`          | C/C++ → Rust or edition upgrade plan              |
| `react-architecture-checklist`     | Grade a React codebase                            |
| `react-security-review`            | OWASP review for React front-ends                 |
| `react-feature-slice`              | React feature slice                               |
| `react-component-scaffolder`       | Component + test + story                          |
| `react-app-scaffolder`             | Vite + React + TS app skeleton                    |
| `react-modernization-analyzer`     | React upgrade / migration plan                    |
| `vue-architecture-checklist`       | Grade a Vue codebase                              |
| `vue-security-review`              | OWASP review for Vue front-ends                   |
| `vue-feature-slice`                | Vue feature slice                                 |
| `vue-component-scaffolder`         | SFC + test + story                                |
| `vue-app-scaffolder`               | Vite + Vue + TS app skeleton                      |
| `vue-modernization-analyzer`       | Vue upgrade / migration plan                      |

### Security, judgment, and support

| Skill                       | Purpose                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| `security-review-federal`   | NIST 800-53 / FIPS / CUI overlay on any `<lang>-security-review` |
| `oss-vetting`               | OSS/SBOM assessment for federal and CUI projects                 |
| `supply-chain-audit`        | Dependency CVEs and license compliance                           |
| `architecture-review`       | Socratic critique of a design                                    |
| `pattern-tradeoff-analyzer` | Compare 2–3 patterns with tradeoffs                              |
| `dependency-mapper`         | Coupling and stability metrics                                   |
| `technical-debt-assessor`   | Prioritize debt and refactoring with a business case             |
| `architecture-journal`      | Lightweight ADRs with retrospectives                             |
| `pr-feedback-writer`        | Write clear review comments                                      |
| `spec-coach`                | Interactive spec / PRD design                                    |
| `automated-code-review`     | Review engine behind `/code-review`                              |
| `test-scaffold`             | .NET test conventions                                            |
| `doc-sync`                  | Find and fix stale docs                                          |
| `environment-health`        | Diagnose Docker, services, ports                                 |
| `research-synthesis`        | Multi-source research with citations                             |
| `session-context`           | Prime a session from git state                                   |
| `task-decomposition`        | Break goals into agent-assigned tasks                            |
| `transcript-capture`        | Meeting transcript → requirements                                |
| `email-capture`             | Email / SOW → requirements                                       |
| `capture-consolidate`       | Merge captures into one bundle                                   |
| `jira-comment-writer`       | Stakeholder-friendly Jira comments                               |
| `confluence-guide-writer`   | User guides from specs or code                                   |
| `skill-creator`             | Create and score skills in this repo                             |

## Agents

51 agents, identical in Claude Code and OpenCode format.

- **General:** `tdd-agent`, `code-review-agent`, `test-generation-agent`, `documentation-agent`,
  `dependency-audit-agent`, `environment-health-agent`, `research-agent`, `context-builder-agent`,
  `task-decomposition-agent`, `migration-orchestrator`, `spec-extractor-agent`, `pm-capture-agent`,
  `confluence-guide-writer`, `oss-vetting-agent`
- **Per language:** each family has review, security, modernization, and scaffolding agents
  (`<lang>-arch-checklist-agent`, `<lang>-security-agent`, `<lang>-feature-slice-agent`, …), plus
  `python-federal-security-agent`. Browse [`claude/agents/`](claude/agents/).
- **Workflow (spawned by the commands, not called directly):** `qrspi-orchestrator`,
  `qrspi-implement`, `qraspi-orchestrator`, `qraspi-builder`, and the read-only `research-file-locator`,
  `research-code-analyzer`, `research-pattern-finder`.

## Commands

| Command                                                                                | What it does                          |
| -------------------------------------------------------------------------------------- | ------------------------------------- |
| `/tdd`                                                                                 | TDD cycle against live test output    |
| `/evaluate-tests [path]`                                                               | Audit test quality and TDD compliance |
| `/code-review`                                                                         | Review the current `git diff`         |
| `/security-review [path]`                                                              | OWASP review of a path                |
| `/oss-vetting [pkg@ver]`                                                               | Vet a package for federal/CUI use     |
| `/arch-review [component]`                                                             | Socratic architecture challenge       |
| `/new-feature [Name]`                                                                  | Scaffold a .NET vertical slice        |
| `/migrate [Name]`                                                                      | EF Core migration with safety checks  |
| `/research [topic]`                                                                    | Multi-source research briefing        |
| `/context-prime`                                                                       | Session brief from git state          |
| `/qrspi-{questions,research,spec,plan,implement} [feature]`                            | One QRSPI phase each                  |
| `/qraspi-{questions,research,architecture,skeleton,plan,implement,graduate} [project]` | One QRASPI phase each                 |

QRSPI and QRASPI phase artifacts go in `thoughts/shared/qrspi/` and `thoughts/shared/qraspi/`; each
phase refuses to run until the previous artifact exists. See
[`docs/structured-workflows-overview.md`](docs/structured-workflows-overview.md).

---

## Repository layout

```
skills/              78 skills (flat; one directory per skill)
claude/              agents/, commands/, global/ (→ ~/.claude)
opencode/            agents/, commands/, global/ (→ ~/.config/opencode)
pi/global/           Pi config (→ ~/.pi/agent)
project-templates/   per-project context files to copy into your repo
scripts/             install scripts (Bash + PowerShell)
tools/               standalone utilities, each with its own README:
                     pdf2md, web2md, code2md (→ RAG-ready Markdown),
                     ollama-evals (local model evals), skill-evals (lints and evaluates skills/)
bakeoff/             harness that benchmarks agent setups on fixed coding tasks
docs/                workflow and local-AI guides
```

Contributing: read [`CLAUDE.md`](CLAUDE.md) (conventions), [`constraints.md`](constraints.md), and
[`DEVELOPER.md`](DEVELOPER.md) (setup). Run `skill-evals lint` before committing a skill change.

---

## Author

**Michael K. Alber** — [codeberg.org/michaelkalber](https://codeberg.org/michaelkalber)

Related: [grounded-code-mcp](https://codeberg.org/michaelkalber/grounded-code-mcp) (local RAG server
for coding agents)

## License

MIT — see [LICENSE](LICENSE).
