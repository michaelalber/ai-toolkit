---
date: 2026-06-02
repository: ai-toolkit
topic: "QRASPI greenfield workflow — Research phase"
tags: [qraspi, qrspi, research, greenfield, walking-skeleton, adr, fitness-functions]
phase: Research (R)
status: complete
note: >
  RPI Research artifact for the QRASPI rollout itself. Objective map of the post-QRSPI repo
  state plus the external-pattern record QRASPI is built on. No solution, no plan, no ADRs for
  the QRASPI rollout (meta-recursion stops at one level). Decision points are framed, not resolved.
---

# QRASPI Research

QRASPI is the greenfield (V0/V1) counterpart to QRSPI. This artifact maps what the repo
contains after the QRSPI bootstrap, the integration surface a QRASPI rollout would touch, the
greenfield-specific concerns it raises, and the external patterns it inherits. It does **not**
propose a design.

---

## Section 1 — Post-QRSPI Repo State Inventory

### 1.1 Skill layout and the QRSPI skill shape

- Skills live in `skills/{team,professional}/<name>/SKILL.md` with a sibling `references/`
  directory; the `team` vs `professional` subdir is chosen by the `audience:` frontmatter and
  applied by `scripts/add_frontmatter.py` (`AGENTS.md:128-132`).
- The five QRSPI phase skills are in `skills/team/` as a **flat parallel namespace**, one
  directory per phase:
  - `skills/team/qrspi-questions/` (`SKILL.md`, 86 lines; `references/questions-template.md`)
  - `skills/team/qrspi-research/` (93 lines; `references/research-template.md`)
  - `skills/team/qrspi-spec/` (92 lines; `references/spec-template.md`, `references/stage-mapping.md`)
  - `skills/team/qrspi-plan/` (97 lines; `references/plan-template.md`)
  - `skills/team/qrspi-implement/` (92 lines; `references/slice-log-template.md`)
- All five are **minimal-tier** (≤ 100 lines, ≥ 1 reference) per the Decision logged at
  `AGENTS.md:90` ("thin, self-sufficient workflow-phase drivers (≤ ~40 imperative directives)").
  They deliberately do **not** use the full 10-section skill template — that template was judged
  to reproduce the instruction bloat QRSPI exists to fix.
- The QRSPI skills share a consistent reduced shape (observed across all five SKILL.md files):
  1. Frontmatter (`name`, `audience: team`, `description` with trigger phrases + "Do NOT use" negatives)
  2. Title + epigraph
  3. **Core Philosophy** + numbered **Non-Negotiable Constraints** (the LAST constraint is always
     `CONTEXT BUDGET: keep utilization under 40%. At 60%, write <artifact> with progress…`)
  4. **Workflow** — an ASCII block of named phases (e.g. `PRE-FLIGHT / SURFACE / WRITE / STOP`)
     followed by an explicit **Exit criteria** line
  5. **State Block** — a unique XML tag (`<qrspi-questions-state>`, `<qrspi-research-state>`, …)
     carrying phase, feature_folder, gate booleans, `context_budget`, `status`
  6. **Output Template** — a pointer to `references/`, never an inline template
  7. **Integration with Other Skills** — a table cross-linking the prior/next phase, `tdd`, the
     `*-feature-slice` scaffolders, and the DEPRECATED `rpi-*` sibling
- Frontmatter `description` for each phase encodes routing AND an explicit "Do NOT use for the
  deprecated RPI workflow" disambiguation (`skills/team/qrspi-research/SKILL.md:4-9`).

### 1.2 Agents

- Agents live in `claude/agents/{team,professional}/<name>.md` and `opencode/agents/{team,professional}/`.
  Counts are at parity: **34 team + 3 professional** each on both platforms (verified via `ls | wc -l`).
- QRSPI ships **two** agents (both platforms), split by edit access:
  - `qrspi-orchestrator` (`claude/agents/team/qrspi-orchestrator.md`) — drives the **Q→R→S→P
    alignment** phases. Tools: `Read, Glob, Grep, Bash, Write` — **no Edit**; cannot touch source
    (`qrspi-orchestrator.md:4`, Guardrail 1 at line 54). `skills:` array loads all four alignment
    phase skills. Acts as the ticket-hidden firewall.
  - `qrspi-implement` (`claude/agents/team/qrspi-implement.md`) — the **execution** agent. Tools:
    `Read, Edit, Write, Bash, Glob, Grep` (has Edit). `skills:` array = `qrspi-implement` + `tdd`.
- Unlike the skills, the **agents DO follow the 10-section agent template** (`AGENTS.md:238-249`):
  Title+Epigraph, Core Philosophy, Guardrails, Autonomous Protocol, Self-Check Loops, Error
  Recovery, AI Discipline Rules, Session Template, State Block, Completion Criteria. Both QRSPI
  agents are full-length (orchestrator 257 lines, implement 239 lines).
- Read-only research subagents (renamed from `rpi-*` to be workflow-neutral, `AGENTS.md:88`),
  shared by QRSPI and reusable by QRASPI:
  - `claude/agents/team/research-file-locator.md`
  - `claude/agents/team/research-code-analyzer.md`
  - `claude/agents/team/research-pattern-finder.md`
  - (`research-agent.md` also present — a separate general research agent.)
  These are spawned in parallel via the Task tool, each on a neutral topic string.

### 1.3 Commands

- Commands live in `claude/commands/` and `opencode/commands/` — **15 each** (parity).
- QRSPI ships 5: `qrspi-questions.md … qrspi-implement.md` on both platforms.
- Command shape (`claude/commands/qrspi-research.md`): frontmatter (`description`,
  `allowed-tools` scoped e.g. `Bash(ls:*), Bash(date:*), Read`), a `<live_state>` block that
  shell-injects `date` and an `ls` of the feature folders, then an instruction body that **routes
  to the `qrspi-orchestrator` agent** and restates the phase's gates. `$ARGUMENTS` carries the
  feature.
- Commands are user-invoked (`/qrspi-research`); skills are model-invoked. Different primitives,
  same directory scope (`AGENTS.md:83`).

### 1.4 Artifact storage

- QRSPI artifacts co-locate per feature in `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/`
  (`AGENTS.md:91`): `questions.md`, `research.md`, `spec.md`, `plan.md`,
  `implementation/slice-NN-*.md`.
- This directory **does not exist yet** (`ls -d thoughts/shared/qrspi` → absent) — QRSPI has not
  been run on a real feature; only the bootstrap that built QRSPI itself has executed.
- Each artifact carries frontmatter with a lifecycle `status:` field that is the gate for the next
  phase: `questions.md` → `awaiting-answers`/`answered`; `spec.md`/`plan.md` →
  `draft → ready-for-review → approved`. The `approved` status on `plan.md` blocks
  `qrspi-implement` (`qrspi-implement.md` Guardrail 1).
- The repo-root `thoughts/` holds the QRSPI **bootstrap** meta-artifacts: `qrspi-research.md`,
  `qrspi-plan.md`, `qrspi-implementation-log-slice-{2..6}.md`. **This QRASPI research artifact is
  the analog**, written to `thoughts/qraspi-research.md` (repo root, not under `shared/qrspi/`).

### 1.5 Primitives, scaffolders, and the no-new-primitive doctrine

- **QRSPI vendored zero new primitive skills** (`AGENTS.md:89`). The canonical RED-GREEN-REFACTOR
  inner loop is the existing **`tdd`** skill (`skills/team/tdd/`); `qrspi-implement` references it
  rather than duplicating it. The vertical-slice gate lives inside the `qrspi-spec`/`qrspi-plan`
  content, not in a separate skill.
- Vertical-slice scaffolders available for reuse: `dotnet-vertical-slice`, `python-feature-slice`,
  `rust-feature-slice` (plus `axum-scaffolder`, `fastapi-scaffolder`, `minimal-api-scaffolder`).
- MCP server scaffolding exists: `mcp-server-scaffold` (FastMCP pattern).
- TDD suite: `tdd, tdd-implementer, tdd-refactor, tdd-agent, tdd-pair, tdd-verify, evaluate-tests`.

### 1.6 Supporting conventions

- **Vendored-skill attribution**: `.matt-pocock-attribution.yml` (repo root) records per-skill
  upstream provenance — `skill`, `source: mattpocock/skills`, `upstream_path`, `locally_modified`,
  `modifications_summary`. Visible credit is kept; the file header notes commit hashes are unknown.
  If QRASPI vendors or adapts any external skill, this is the attribution pattern to extend.
- **Skill count = 86** (`AGENTS.md:97`, README). Open Loops track skill/agent/command counts;
  adding QRASPI skills/agents/commands obliges updates to `AGENTS.md` Open Loops + Skill Suites
  table (`AGENTS.md:265-283`) and `README.md`.
- **`project-templates/`** holds copy-into-target-project files: `AGENTS.md, CLAUDE.md,
  constraints.md, design.md, domain-memory.md, evals.md, intent.md, README.md`. A greenfield
  workflow that scaffolds a new project may need to seed these — relevant to the Skeleton phase.
- **`docs/`** has `rpi-and-spec-driven-dev-overview.md` (a narrative doc still RPI-framed) and
  `audit-remediation-plan.md`. The narrative doc would be a candidate for a QRSPI/QRASPI update.
- **RPI is deprecated** (`AGENTS.md:88`, Decision 2026-06-02): `rpi-research/plan/implement/iterate`
  carry `disable-model-invocation: true` + a `DEPRECATED` description prefix; removal at sunset
  ~2026-09-01 (Slice 7). QRASPI must not depend on any `rpi-*` skill or the `rpi-planner`/
  `rpi-implement` agents.

---

## Section 2 — QRASPI Integration Surface

The factual surface QRASPI would touch, with the QRSPI precedent for each (decisions framed in §5).

### 2.1 Skill namespace

- QRSPI precedent: flat parallel namespace `skills/team/qrspi-*` — five sibling directories, no
  nesting. (There is no `skills/team/qrspi/` parent.)
- QRASPI has **six** phases (Q-R-A-S-P-I) vs QRSPI's five → six phase skills if it mirrors the
  one-skill-per-phase precedent. Candidate names: `qraspi-questions`, `qraspi-research`,
  `qraspi-architecture`, `qraspi-skeleton`, `qraspi-plan`, `qraspi-implement`.
- Both `qrspi-*` and `qraspi-*` would sort adjacently under `skills/team/`; the names differ by
  one character (`qr**a**spi`). Slug collision risk and the visual near-duplicate is a framed
  concern (§5).

### 2.2 Primitive reuse vs greenfield-specific

Reusable from the existing toolkit (no new primitive needed):
- **`tdd`** — the RGR inner loop for QRASPI's Implement phase (same as QRSPI).
- **`research-file-locator` / `research-code-analyzer` / `research-pattern-finder`** — read-only
  parallel subagents. **Caveat:** these are *codebase*-oriented (Glob/Grep over existing source).
  Greenfield Research has **no codebase to map** — its factual record is the problem domain and
  solution landscape (external). The subagents may be reusable only for the
  "greenfield-within-existing-repo" scenario (§4.5); pure greenfield Research likely needs a
  different evidence source (web/domain research, cf. `research-synthesis`). Framed in §5.
- **`*-feature-slice` scaffolders** — for the vertical slices the Skeleton/Implement phases build.
- **`mcp-server-scaffold`** — for the MCP-server greenfield archetype (§4.1).

Greenfield-specific, with **no existing skill** (candidate new capabilities):
- **ADR authoring** (Nygard-format Architecture Decision Records) — the **A** phase. Nearest
  existing assets: the `domain-model` skill "records decisions as ADRs sparingly" (README:234) and
  `architecture-journal` ("lightweight ADR templates with retrospective prompts at 30/90/180 days",
  README:294). Neither is a full ADR-authoring phase driver. `session-context` does "ADR relevance
  matching" (README:261).
- **Walking skeleton / tracer-bullet scaffolding** — the **S** phase. No existing skill scaffolds
  an end-to-end-through-every-layer hello-world with CI + observability + secure-by-default.
- **Architectural fitness-function encoding** — landing fitness functions as CI gates. No existing
  skill. (Note: `tools/` and `scripts/` exist for repo automation; `claude/global/settings.json`
  hosts deterministic PostToolUse build/lint hooks — a precedent for "gate as deterministic check.")
- **C4 diagram authoring** (context + container) — no existing skill.

Open doctrinal question (mirrors QRSPI's zero-new-primitive choice): are ADR-writing,
walking-skeleton, and fitness-function-encoding **folded into the phase skills' own content**
(the way `qrspi-spec`/`qrspi-plan` fold the vertical-slice gate into their bodies), or **extracted
as new shared primitives**? Framed in §5.

### 2.3 Command naming

- QRSPI precedent: `/qrspi-questions … /qrspi-implement`, one command per phase, both platforms,
  each routing to the orchestrator/implement agent with a `<live_state>` `ls` of the feature folder.
- QRASPI candidates: `/qraspi-questions`, `/qraspi-research`, `/qraspi-architecture`,
  `/qraspi-skeleton`, `/qraspi-plan`, `/qraspi-implement`. The `description` field must
  unambiguously disambiguate QRASPI from QRSPI (and from deprecated RPI), exactly as the QRSPI
  commands disambiguate from RPI today.

### 2.4 Sub-agent isolation / agent split

- QRSPI uses **two** agents split by edit access: `qrspi-orchestrator` (alignment, **no Edit**) and
  `qrspi-implement` (execution, **has Edit**). Each phase does NOT get its own agent — one
  orchestrator multiplexes the four alignment phases by loading the matching skill.
- QRASPI's phase set crosses the edit boundary differently: **Q, R, A** are alignment/no-source-edit
  (questions, domain research, ADRs/C4 are markdown artifacts), but **S (Skeleton)** writes source
  (scaffolds a runnable repo) and **I (Implement)** writes source. So the alignment/execution split
  is at a different seam than QRSPI's (QRSPI's seam is after Plan; QRASPI's is after Architecture).
  Where the Skeleton phase sits (alignment-side artifact-only "skeleton spec" vs execution-side
  "scaffold the repo") is a framed decision (§3.5, §5). This determines whether QRASPI needs 2
  agents (orchestrator + executor) like QRSPI, or 3 (e.g. alignment / skeleton-scaffolder /
  implementer).
- The read-only research subagents are reusable as-is for the parallel-spawn mechanic.

---

## Section 3 — Greenfield-Specific Concerns

Factual landscape of the decisions the **A** and **S** phases introduce. (Resolutions → §5.)

### 3.1 ADR storage location

- The Joel Parker Henderson ADR repo recommends a dedicated `adr/` directory and a present-tense
  imperative dash-cased filename (`choose-database.md`), and explicitly does **not** mandate
  sequential numbering — teams adapt (source: github.com/joelparkerhenderson/architecture-decision-record).
- Common conventions in the wild: `docs/adr/`, `docs/architecture/decisions/`, repo-root `adr/`.
  adr-tools defaults to `doc/adr/` with `NNNN-title.md` sequential numbering.
- The session brief frames the choice as: a per-target-project decision encoded in the Architecture
  skill, vs a default applied unless overridden. The repo's own `project-templates/` precedent
  (copy-into-project files) suggests the toolkit already ships project-seeding conventions.

### 3.2 Stack templates for the Skeleton

- The toolkit already contains stack-specific scaffolders the Skeleton could compose:
  `dotnet-vertical-slice` (CQRS + FreeMediator + optional Telerik Blazor), `python-feature-slice`
  (FastAPI + Pydantic v2 + service layer), `rust-feature-slice` (Axum), `mcp-server-scaffold`
  (FastMCP), `fastapi-scaffolder`, `minimal-api-scaffolder`, `axum-scaffolder`,
  `rag-pipeline-{python,dotnet}`, and the Edge/IoT suite (`edge-cv-pipeline`, `jetson-deploy`,
  `sensor-integration`, `picar-x-behavior`).
- Open: does the Skeleton skill ship its own template skeletons per stack (e.g. .NET Blazor +
  EF Core + xUnit; Python + FastAPI + pytest; FastMCP server), or declare-the-stack-and-generate,
  or delegate to the existing scaffolders? Framed in §5. The scaffolders are feature-slice tools,
  not full-repo+CI+observability skeletons — there is a gap between "scaffold a feature" and
  "scaffold the walking skeleton."

### 3.3 Fitness-function encoding

- Fitness functions measure how close an architecture is to its goal and are encoded as automated
  tests in CI/CD that gate deployment; categories span code-quality, resiliency, observability,
  performance, compliance, security, operability (source: thoughtworks.com fitness-function-driven
  -development; framework: Ford/Parsons/Kua, *Building Evolutionary Architectures*).
- Encoding is stack-dependent: CI-gate scripts (bash/PowerShell), test-framework integration, or
  dedicated tools (ArchUnit/NetArchTest for JVM/.NET layer rules; Conftest/OPA for policy;
  dependency-cruiser for JS). The repo already has a "deterministic gate" precedent in
  `claude/global/settings.json` PostToolUse hooks and likely needs template variants per stack.
- Existing related skill: `dependency-mapper` (Robert C. Martin stability metrics, circular-ref
  detection) — a fitness-function-shaped capability already present.

### 3.4 C4 diagrams: text vs drawn

- C4 (Simon Brown, c4model.com) defines four levels: System Context, Container, Component, Code.
  QRASPI brief scopes to Context + Container.
- Text-based options (version-controllable, AI-generatable): Structurizr DSL, Mermaid `C4Context`,
  PlantUML C4-PlantUML. Drawn artifacts (draw.io, Excalidraw) are not diffable. The repo is
  markdown-native with no build system (`AGENTS.md:30`), which favors text/Mermaid that renders in
  markdown viewers. Framed in §5.

### 3.5 Runnable repo vs scaffold spec (Skeleton output)

- Walking skeleton (Cockburn) = a tiny end-to-end implementation that exercises the main
  architectural components and is the carrier for the build/test/deploy harness — *executable*, not
  a document. Tracer bullet (Hunt & Thomas, *Pragmatic Programmer*) = the same idea: a thin
  end-to-end thread through every layer, doing minimal real work, kept and grown. (Cockburn's page
  alistair.cockburn.us/walking-skeleton/ could not be fetched — certificate expired; this is the
  well-established definition.)
- Tension named in the brief: full automation (Skeleton produces a running `make build && make test
  && make deploy` hello-world) vs producing a spec for a human-driven scaffold — over-constraining
  templates risks re-introducing the "magic-words" trap QRSPI/QRASPI exist to avoid. This is the
  same tension as §2.4's agent-split seam.

### 3.6 Graduation handoff to QRSPI

- Composition rule (brief): QRASPI is V0/V1 only; once the Skeleton ships and the system accrues
  real features, **new features use QRSPI**. The Skeleton phase produces the codebase QRSPI then
  operates on.
- Today there is **no graduation mechanism** in the repo — QRSPI's artifacts assume an existing
  codebase (its Research subagents Glob/Grep over source). The handoff (explicit "graduation" step
  vs informal transition) is unspecified and framed in §5. Both workflows already share primitives
  (`tdd`, vertical slices, the `research-*` subagents), so the seam is conceptual, not tooling.

---

## Section 4 — Greenfield Scenarios and Their Implications

The five archetypes from the brief, plus what each implies for QRASPI skill design. (No
recommendation — implications only.)

### 4.1 New Python MCP server (small, single-service, library-heavy)
- Existing asset: `mcp-server-scaffold` (FastMCP). Small surface; the Architecture phase may
  produce only 1–2 ADRs (transport, tool-surface shape); fitness functions are light (lint, type,
  pip-audit — already enforced by the global `ruff` PostToolUse hook). Skeleton = a FastMCP server
  exposing one trivial tool end-to-end with pytest + CI. Implication: QRASPI must scale **down**
  gracefully — a six-phase ceremony on a single-service library risks the bikeshedding/ceremony
  cost the workflow is meant to prevent.

### 4.2 New .NET 10 / Blazor Server enterprise app (EF Core + vertical slice + CQRS)
- Existing assets: `dotnet-vertical-slice`, `ef-migration-manager`, `dotnet-architecture-checklist`,
  `dotnet-security-review`. Multi-project solution. The Architecture phase carries weight: DB choice,
  auth model, CQRS/mediator, migration strategy — the path-dependent decisions the brief says
  Architecture exists to lock early. Fitness functions are richest here (NetArchTest layer rules,
  coverage gates, the global `dotnet build` hook). Skeleton = one vertical slice end-to-end (Blazor
  page → handler → EF Core → DB) + CI + health checks. Implication: this is the archetype the full
  six-phase workflow fits best; templates per-stack matter most here.

### 4.3 New edge AI / IoT project (Pi or Jetson, hardware-coupled, constrained runtime)
- Existing assets: Edge/IoT suite. Hardware coupling breaks the "runnable skeleton in CI" assumption
  — `make deploy` targets a device, not a container; observability and the test harness are
  constrained by the runtime. Implication: the Skeleton's "exercises every layer" definition is
  hardware-dependent; the deploy target is not uniformly automatable. The `pi/global/` install
  target and per-project `SYSTEM.md` template (`AGENTS.md:52,67`) are relevant.

### 4.4 New eval harness / AI tooling project (Python, infrastructure-heavy)
- Existing assets: `research-synthesis`, `rag-pipeline-python`, the global CLAUDE.md "Evaluation
  Design" doctrine ("create `evals.md` before the agent starts"), and the repo's own `evals.md`.
  Brief says Skeleton includes "eval harness scaffolding where applicable." Implication: QRASPI's
  Skeleton must know when eval-harness scaffolding is in scope; fitness functions and evals overlap
  conceptually (both are executable acceptance gates) and the boundary needs framing.

### 4.5 Greenfield-within-existing-repo (e.g. adding a new MCP server to ai-toolkit)
- Partial scenario: repo conventions (AGENTS.md, global hooks, `skills/{team,professional}/`
  layout, attribution file) are **inherited**, but the component is new. Implication: this is the
  one archetype where the **codebase-oriented `research-*` subagents apply** (map existing repo
  conventions before adding the component), unlike pure greenfield where Research is external/domain.
  QRASPI's Research phase may need a mode switch: external-domain vs inherited-repo-conventions.

### 4.6 Cross-cutting implication
- The five archetypes vary the Architecture weight, the Skeleton's "every layer" definition, the
  deploy target, and the fitness-function tooling. Open: does the **Skeleton skill carry
  archetype-awareness** (template variants per stack), or does the **Architecture phase produce
  enough constraint that Skeleton is archetype-agnostic** (consumes the ADRs + stack declaration and
  scaffolds generically)? This is the central design tension and is framed in §5.

---

## Section 5 — Open Questions for the Plan Phase

Numbered, each with decision criteria. **Not** recommendations.

1. **Skill namespace: flat-parallel `skills/team/qraspi-*` vs nested `skills/team/qraspi/`?**
   Criteria: QRSPI precedent is flat-parallel (no nesting); `add_frontmatter.py` walks
   `skills/{team,professional}/*/` (one level) — nesting may break frontmatter tooling (verify);
   slug near-collision with `qrspi-*` (one-char difference) argues for a disambiguating convention.

2. **Phase-to-skill mapping: six skills (one per Q-R-A-S-P-I phase) vs fewer (e.g. fold A+S, or
   reuse `qrspi-plan`/`qrspi-implement` verbatim)?**
   Criteria: QRSPI maps 5 phases→5 skills but folds source stages 3+4 into `qrspi-spec`
   (`stage-mapping.md`); precedent exists for collapsing. Does QRASPI's Plan/Implement differ
   enough from QRSPI's to need its own skills, or can it route to `qrspi-plan`/`qrspi-implement`?

3. **New primitives vs folded content (the QRSPI zero-new-primitive doctrine, `AGENTS.md:89`).**
   Are ADR-authoring, walking-skeleton-scaffolding, and fitness-function-encoding extracted as new
   shared skills, or folded into the `qraspi-architecture`/`qraspi-skeleton` phase bodies?
   Criteria: QRSPI folded the vertical-slice gate into phase content and vendored 0 primitives
   (DRY + "Companion Skills" non-overlap). Counter-pull: ADR-authoring and fitness-functions are
   reusable outside QRASPI (existing `architecture-journal`, `domain-model`, `dependency-mapper`
   already touch these) — extraction may reduce duplication. Resolve per-capability.

4. **Agent topology: 2 agents (alignment-orchestrator + executor, QRSPI-style) vs 3 (orchestrator +
   skeleton-scaffolder + implementer)?**
   Criteria: QRASPI's edit-boundary seam differs from QRSPI's — S (Skeleton) and I (Implement)
   both write source, while Q/R/A are artifact-only. Whether Skeleton is alignment-side (produces a
   scaffold spec) or execution-side (writes the repo) decides the count. Tools differ by Edit access.

5. **ADR storage location — `docs/adr/` vs `docs/architecture/decisions/` vs repo-root `adr/`; and
   is it a fixed default or a per-target-project override encoded in the Architecture skill?**
   Criteria: ADR-repo recommends `adr/` + dash-case filenames, no mandated numbering; adr-tools
   defaults to `doc/adr/` + `NNNN-` numbering; the toolkit already ships `project-templates/` as a
   project-seeding precedent. Nygard format = Title/Status/Context/Decision/Consequences (the brief
   adds "Alternatives Considered" — that section is MADR/Tyree-Akerman, not original Nygard; confirm
   which template QRASPI standardizes on).

6. **Skeleton template strategy: ship per-stack skeletons, declare-stack-and-generate, or delegate
   to existing `*-feature-slice`/`*-scaffold` skills?**
   Criteria: existing scaffolders are feature-slice tools, not full-repo+CI+observability skeletons
   — there is a gap. Per-stack templates risk the magic-words/over-constraint trap (§3.5); generate-
   from-scratch risks inconsistency. Archetype variance (§4) bears directly here.

7. **Fitness-function encoding mechanism — CI scripts, test-framework integration, or dedicated
   tools (NetArchTest/ArchUnit/Conftest)? One mechanism or per-stack variants?**
   Criteria: stack-dependent; `dependency-mapper` already does Martin-metric checks; global
   `settings.json` hooks are a deterministic-gate precedent. Brief requires fitness functions land
   as CI gates in the Skeleton.

8. **C4 format: Structurizr DSL vs Mermaid `C4Context` vs PlantUML — text-based assumed; which?**
   Criteria: repo is markdown-native, no build system; Mermaid renders inline in markdown viewers;
   Structurizr DSL is richer but needs tooling. Version-controllable + AI-generatable is required.

9. **Skeleton output: runnable repo (full automation) vs scaffold spec for human-driven setup?**
   Criteria: walking-skeleton is *executable* by definition (§3.5); but full automation risks
   over-constraining templates (the magic-words trap). Hardware-coupled archetype (§4.3) cannot
   uniformly auto-deploy. May be archetype-conditional.

10. **Greenfield Research evidence source: pure-greenfield has no codebase — do the codebase-oriented
    `research-*` subagents apply, or does Research use external/domain research (`research-synthesis`)?
    Does Research need a mode switch (external-domain vs inherited-repo-conventions, §4.5)?**
    Criteria: subagents Glob/Grep over source; greenfield has none except the inherited-repo
    archetype. Brief says R's factual record is "the problem domain and solution landscape."

11. **Graduation handoff to QRSPI: explicit "graduation" step/artifact vs informal transition?**
    Criteria: no mechanism exists today; QRSPI's Research assumes an existing codebase, which the
    Skeleton produces. Shared primitives (`tdd`, vertical slices, `research-*`) make the seam
    conceptual. Brief leaves it open.

12. **Domain-modeling sub-phase between R and A for high-domain-complexity systems (DDD strategic +
    tactical), or subsumed into Architecture?**
    Criteria: existing `domain-model` skill (DDD vocabulary, CONTEXT.md, records ADRs sparingly,
    `disable-model-invocation: true`) already covers this ground. Brief asks whether QRASPI needs a
    distinct sub-phase or folds it into A.

13. **Minimal-tier vs full-template for QRASPI phase skills.**
    Criteria: QRSPI used minimal-tier for all five phase skills (`AGENTS.md:90`), deliberately
    rejecting the 10-section template as instruction bloat. QRASPI's Architecture and Skeleton phases
    are heavier (ADR format, C4, fitness functions, multi-stack templates) — do they overflow the
    ≤100-line minimal budget, pushing content to `references/` (QRSPI's overflow strategy) or to the
    full template?

14. **Bookkeeping obligations.** Adding QRASPI obliges updates to: `AGENTS.md` Skill Suites table
    (`:265-283`), Open Loops counts (`:97-99`), skill count (86); `README.md` (new suite section +
    command table, paralleling the QRSPI section at `:195-209` and command table at `:394-398`);
    both `claude/` and `opencode/` agent+command parity; `.matt-pocock-attribution.yml` if anything
    is vendored. Plan must schedule these.

---

## Section 6 — External Source Notes

Paraphrased; cited. The QRASPI brief's five sources plus what was retrievable.

### 6.1 Walking Skeleton — Alistair Cockburn (alistair.cockburn.us/walking-skeleton/)
- **Could not fetch** (TLS certificate expired on the host as of 2026-06-02). The following is the
  well-established definition from the pattern literature, flagged as not freshly verified:
  A walking skeleton is a tiny end-to-end implementation of the system that performs a small real
  function but, critically, links together the **main architectural components**. It exists to
  exercise and shape the architecture and to carry the build/test/deploy automation, not to deliver
  features. It is "walking" because it runs end-to-end from day one; it is a "skeleton" because it
  has minimal flesh. It is grown, not thrown away — distinguishing it from a spike/prototype.

### 6.2 Tracer Bullet — Hunt & Thomas, *The Pragmatic Programmer*
- A tracer bullet is a thin but complete thread through every layer of the system, doing minimal
  real work, kept and incrementally fleshed out. Unlike a prototype (built to learn, then
  discarded), tracer code is production code that is grown. Functionally synonymous with the walking
  skeleton in the QRASPI brief. (Established source; no fetch.)

### 6.3 Architecture Decision Records — Joel Parker Henderson repo + Michael Nygard
- (github.com/joelparkerhenderson/architecture-decision-record, fetched 2026-06-02.) The repo
  catalogs template variants: **Nygard** (simple, popular), **Tyree-Akerman** (more sophisticated),
  **Alexandrian**, **business-case** (costs/SWOT), **MADR** (Markdown Any Decision Records),
  **Planguage**, plus arc42/EdgeX/Merson/Zimmermann variants.
- Placement: recommends a dedicated `adr/` directory; filenames are present-tense imperative,
  lowercase, dash-separated, `.md` (e.g. `choose-database.md`). Sequential numbering is **not**
  mandated — adaptable.
- **Nygard format** (from Nygard's "Documenting Architecture Decisions"): **Title, Status, Context,
  Decision, Consequences**. Note: the QRASPI brief lists "context, decision, status, consequences,
  alternatives considered" — *Alternatives Considered* is a MADR/Tyree-Akerman addition, **not** in
  original Nygard. The Plan phase must reconcile which template QRASPI standardizes on (§5 Q5).

### 6.4 C4 Model — Simon Brown (c4model.com)
- Four hierarchical levels of abstraction: **System Context**, **Container**, **Component**, **Code**.
  QRASPI scopes to Context + Container. C4 is notation-independent; text-based renderers include
  Structurizr DSL (Brown's own tool), Mermaid (`C4Context`/`C4Container` diagrams), and C4-PlantUML.
  Text DSLs are version-controllable and AI-generatable, aligning with the repo's markdown-native,
  no-build-system posture (`AGENTS.md:30`). (Established source; no fetch this session.)

### 6.5 Architectural Fitness Functions — Thoughtworks / Ford, Parsons, Kua
- (thoughtworks.com/insights/articles/fitness-function-driven-development, fetched 2026-06-02.)
  A fitness function measures how close an architecture is to its architectural goal, extending TDD
  beyond code quality to non-functional dimensions: code-quality, resiliency, observability,
  performance, compliance, security, operability. They are encoded as **automated tests integrated
  into CI/CD as gatekeepers** before production, run continuously rather than post-facto. They
  operationalize *Building Evolutionary Architectures* (Ford/Parsons/Kua, 2017): "guided,
  incremental change as the first principle across multiple dimensions." Categories in the broader
  literature: atomic vs holistic, triggered vs continuous, static vs dynamic.

### 6.6 QRSPI foundation — Alex Lavaee, "From RPI to QRSPI" (alexlavaee.me/blog/from-rpi-to-qrspi/)
- Not fetched this session; its content is already embodied in the landed QRSPI skills/agents
  (§1) and the session brief. The three RPI failure modes QRSPI/QRASPI inherit mitigations for:
  instruction-budget overflow (frontier models lose consistency past ~150–200 instructions —
  `qrspi-orchestrator.md:26-28`), magic-word dependencies (replaced by **artifact gates** — each
  phase refuses to run until the prior artifact exists on disk, README:198), and the plan-reading
  illusion (mitigated by mechanical, file-precise plans). QRASPI's analog is the
  **architecture-reading illusion**, which the brief says the early Skeleton mitigates by forcing
  ADRs to be executable rather than aspirational.

---

## Appendix — Verbatim repo facts cited

- Skill counts/parity: `find skills -name SKILL.md | wc -l` = 86; agents 34 team+3 prof each
  platform; commands 15 each platform (verified this session).
- `thoughts/shared/qrspi/` does not yet exist (no real QRSPI feature run).
- QRSPI skills: `skills/team/qrspi-{questions,research,spec,plan,implement}/` (86–97 lines each).
- QRSPI agents: `claude/agents/team/qrspi-{orchestrator,implement}.md` (+ opencode mirror).
- Research subagents: `claude/agents/team/research-{file-locator,code-analyzer,pattern-finder}.md`.
- Deprecation: RPI skills/agents `disable-model-invocation: true` + DEPRECATED prefix, sunset
  ~2026-09-01 (`AGENTS.md:88,97-99`).
</content>
</invoke>
