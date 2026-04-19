---
date: 2026-04-19T00:00:00
repository: ai-toolkit
topic: "Skill routing eval suite — precision/recall/F1 against skill descriptions"
tags: [research, eval, routing, skills, ollama]
git_commit: 58b7d32
status: complete
---

# Research: Skill Routing Eval Suite

## Research question

What infrastructure is needed to measure whether the right skill activates for a
given user prompt, and what are the collision risks and structural constraints that
the plan must account for?

## Summary

The ai-toolkit has 53 skills. Each skill's routing signal is the `description:`
field in its `SKILL.md` frontmatter — this is the verbatim text the platform
injects into the agent's context for skill selection. No routing eval exists today;
`evals.md` has 4 structural test cases (TC1–TC4), none of which test routing.

The primary structural challenge is description heterogeneity: 36 of 53 skills are
prose-only (no quoted trigger phrases), 17 are mixed (prose + explicit quoted
phrases). Prose-only skills require semantic/embedding matching to evaluate; mixed
skills support both keyword recall and semantic tests. The TDD suite (6 skills) is
the highest collision risk — all 6 are prose-only with near-identical vocabulary.

The established Python tool pattern is `tools/pdf2md/`: self-contained under
`tools/<name>/`, own `pyproject.toml` with hatchling, `src/` layout, Typer CLI,
pytest+cov. No JSONL or fixture files exist anywhere in the repo — all fixture
infrastructure must be created from scratch. No `thoughts/` directory existed; it
has been created at `thoughts/shared/research/` per RPI convention.

## Detailed findings

### 1. Skill description taxonomy (all 53 skills)

Three description styles confirmed:

- **Prose-only** (36 skills): Free-text "Use when..." descriptions. No quoted
  trigger phrases. Examples: `architecture-review`, all 6 TDD skills,
  `architecture-journal`, `code-review-coach`, `dependency-mapper`, all edge/IoT
  skills, all AI/ML skills.
  - `skills/tdd-cycle/SKILL.md:3`
  - `skills/tdd-agent/SKILL.md:3`
  - `skills/architecture-review/SKILL.md:3`

- **Mixed** (17 skills): Prose + explicit quoted trigger list. Examples:
  `dotnet-architecture-checklist`, `dotnet-security-review`,
  `dotnet-security-review-federal`, `dotnet-vertical-slice`,
  `legacy-migration-analyzer`, `minimal-api-scaffolder`, `supply-chain-audit`,
  `4d-schema-migration`, `agent-spec-writer`, `confluence-guide-writer`,
  `rpi-implement`, `rpi-iterate`, `rpi-plan`, `rpi-research`.
  - `skills/dotnet-architecture-checklist/SKILL.md:3`
  - `skills/dotnet-security-review/SKILL.md:3`

- **YAML block scalar** (8 skills, subset of Mixed): `description: >` spanning
  multiple lines. PyYAML parses these correctly as a single string.
  - `skills/rpi-research/SKILL.md:3–6`
  - `skills/4d-schema-migration/SKILL.md:3–N`

### 2. Collision pairs (highest risk first)

| Pair | Risk | Distinguishing signal |
|---|---|---|
| `tdd-cycle` ↔ `tdd-agent` | HIGH | "orchestrate" vs. "autonomous/AI drives" |
| `tdd-cycle` ↔ `tdd-pair` | HIGH | "orchestrate phases" vs. "pair programmer role" |
| `tdd-implementer` ↔ `tdd-cycle` | HIGH | "implement failing test" hits both |
| `tdd-verify` ↔ `automated-code-review` | MEDIUM | "review this commit" hits both |
| `dotnet-security-review` ↔ `dotnet-security-review-federal` | HIGH | Only federal-specific tokens distinguish |
| `dotnet-architecture-checklist` ↔ `dotnet-security-review` | MEDIUM | "check for issues" vs. "check for vulnerabilities" |
| `architecture-review` ↔ `dotnet-architecture-checklist` | MEDIUM | Generic vs. .NET-specific |
| `minimal-api-scaffolder` ↔ `dotnet-vertical-slice` | MEDIUM | "add endpoint with handler" hits both |
| `automated-code-review` ↔ `code-review-coach` | MEDIUM | Automation intent vs. coaching intent |
| `supply-chain-audit` ↔ `dotnet-security-review` | MEDIUM | "vulnerability scan" hits both |

### 3. Existing eval infrastructure

- `evals.md` — 4 test cases, all structural, none routing (`evals.md:24–79`)
- TC1 requires "≥ 2 trigger phrases" in frontmatter (`evals.md:30`) — only
  existing routing contract; not mechanically enforced
- No JSONL, no fixture files, no Python eval scripts anywhere in repo

### 4. Python tool pattern (gold standard)

`tools/pdf2md/pyproject.toml:1–38` — the established pattern:
- `hatchling` build backend
- `requires-python = ">=3.10"`
- `src/<name>/` layout
- Typer CLI entrypoint in `[project.scripts]`
- `pytest>=8` + `pytest-cov>=5` in `[project.optional-dependencies] dev`
- `testpaths = ["tests"]`, `addopts = "--cov=<name> --cov-report=term-missing"`
- No `requirements.txt` — all deps in `pyproject.toml`
- Fixtures generated programmatically; no binary fixtures committed

### 5. SKILL.md frontmatter is ground truth

The platform injects `description:` verbatim from `skills/*/SKILL.md` frontmatter.
`opencode/global/AGENTS.md` does not contain a static skill registry — it is
runtime-injected. The eval runner must parse frontmatter directly.

## Code references

### Core pattern
- `tools/pdf2md/pyproject.toml` — Python tool scaffold to replicate
- `tools/pdf2md/src/pdf2md/cli.py` — Typer CLI entrypoint pattern
- `tools/pdf2md/src/pdf2md/models.py` — `@dataclass` model pattern (no Pydantic)

### Routing signal source
- `skills/*/SKILL.md` lines 1–N — YAML frontmatter `name:` + `description:`
- `skills/dotnet-architecture-checklist/SKILL.md:3` — best example of explicit triggers
- `skills/tdd-cycle/SKILL.md:3` + `skills/tdd-agent/SKILL.md:3` — highest collision pair

### Eval contract
- `evals.md:30` — only existing routing contract ("≥ 2 trigger phrases")
- `evals.md:24–79` — TC1–TC4 (structural; no routing)

## Key design patterns

1. **Self-contained tool packages**: Each tool under `tools/<name>/` owns its
   `pyproject.toml`. No root-level Python package.
2. **Typer CLI**: All Python tools expose a CLI via Typer; entry point in
   `[project.scripts]`.
3. **Stdlib dataclasses**: No Pydantic in tooling layer; `@dataclass` only.
4. **Programmatic fixtures**: No binary fixture files committed; fixtures generated
   at test time via code.
5. **SKILL.md as single source of truth**: Frontmatter `description:` is what the
   platform uses; eval must parse it directly, not a secondary registry.

## Open questions

1. **Judge strategy**: Ollama (matches real routing, model-dependent) vs.
   TF-IDF/keyword (reproducible, fast, but doesn't simulate actual LLM routing)?
   Given the goal is to measure real routing behavior, Ollama is the likely answer
   — but tradeoff is model-dependent variance between runs.

2. **TDD suite fixture design**: 6 near-identical prose descriptions. Should the
   eval include role-disambiguation prompts ("I want the AI to drive TDD
   autonomously" → `tdd-agent`) or only canonical trigger prompts?

3. **Null routing cases**: Should the eval include prompts that should match no
   skill (e.g., "what's the weather")? Needed for a complete specificity/F1 picture.

4. **LangSmith readiness**: Should `judge.py` be structured as an isolated,
   wrappable function so `@traceable` can be added later without restructuring?
   Hard requirement for Phase 1 or nice-to-have?

5. **`evals.md` TC5**: Add routing eval as TC5 in `evals.md` pointing to the new
   tool, or keep entirely separate?

6. **Agent parity gap**: `claude/agents/confluence-guide-writer.md` has no OpenCode
   counterpart — pre-existing open loop in `AGENTS.md`. Out of scope for this eval
   work but should not be closed by this task.
