---
date: 2026-06-02
repository: ai-toolkit
topic: "QRASPI greenfield workflow — implementation plan (RPI Plan phase)"
tags: [plan, qraspi, qrspi, greenfield, walking-skeleton, adr, fitness-functions, skills, agents, commands]
research_artifact: thoughts/qraspi-research.md
status: approved
phase: Plan (P)
note: >
  Converts thoughts/qraspi-research.md into a phased, vertically-sliced plan for the QRASPI
  greenfield workflow. Cites the research artifact by section (R§N). Parallels the QRSPI rollout
  (thoughts/qrspi-plan.md) structurally; references QRSPI skills rather than re-specifying where
  the shapes match. Does NOT write skill files — that is Implement.
---

# Plan: Adding a QRASPI Greenfield Workflow to ai-toolkit

QRASPI is the greenfield (V0/V1) counterpart to QRSPI: **Q**uestions → **R**esearch →
**A**rchitecture → **S**keleton → **P**lan → **I**mplement. Where QRSPI maps an existing codebase
and grows a feature, QRASPI maps a problem domain, locks the path-dependent decisions as ADRs,
lands an executable walking skeleton with CI green, then grows V1 on top of it — and **graduates
the result to QRSPI** once real features start (R§3.6).

This plan resolves the 14 open questions in R§5, fixes the file layout, specifies per-skill
frontmatter + outlines, specifies no-magic-words enforcement, the graduation mechanism, the
verification strategy, and an 8-slice dog-food sequence. **No skill files are written here.**

**Counts re-verified against the filesystem this session:** skills **86**, agents **37/37**
(claude/opencode parity), commands **15/15**. The five `qrspi-*` skills, the
`qrspi-orchestrator`/`qrspi-implement` agents, and the renamed read-only `research-*` subagents
all exist as R§1 describes.

---

## Section 0 — Decision summary (all 14 questions from R§5)

| #   | Question (R§5)                          | Decision                                                                                                  | Type             |
| --- | --------------------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------- |
| 1   | Skill namespace flat vs nested          | **Parallel-flat** `skills/team/qraspi-*/` (tooling fact, mirrors QRSPI #1)                                | Decided          |
| 2   | Phase-to-skill mapping (6 vs fewer)     | **Six phase skills**; `qraspi-plan`/`qraspi-implement` are their own skills (thin), not routed to QRSPI's | Decided          |
| 3   | New primitives vs folded                | **Fold ADR/C4/skeleton into phase skills + references/**; extract **one** primitive — `fitness-functions` (**Option A**, owner-confirmed) | Decided |
| 4   | Agent topology (2 vs 3)                 | **2 agents** by edit access: `qraspi-orchestrator` (Q/R/A/P, no Edit) + `qraspi-builder` (S/I, Edit)      | Decided          |
| 5   | ADR storage + template                  | Target repo `docs/adr/NNNN-kebab.md` (overridable); **MADR** template (has Alternatives Considered)       | Decided          |
| 6   | Skeleton template strategy              | **Hybrid**: per-archetype recipe in `references/archetypes/` ⊕ existing `*-feature-slice` scaffolders     | Decided          |
| 7   | Fitness-function mechanism              | **Per-stack CI gates**, owned by the `fitness-functions` primitive; `dependency-mapper` is one ready-made | Decided          |
| 8   | C4 format                               | **Mermaid `C4Context`/`C4Container`** (markdown-native, no build system, R§3.4)                           | Decided          |
| 9   | Skeleton output runnable vs spec        | **Runnable repo; exit gate = CI green** (executable by definition, R§3.5/§6.1)                            | Decided          |
| 10  | Greenfield research evidence source     | **Mode switch**: `external-domain` (default) via `research-synthesis`/web; `inherited-repo` via `research-*` | Decided        |
| 11  | Graduation handoff                      | **Explicit thin skill + command** `/qraspi-graduate` → `graduation.md` (no new agent)                     | Decided          |
| 12  | Domain-modeling sub-phase               | **No 7th phase**; fold into Architecture, reference existing `domain-model` skill                         | Decided          |
| 13  | Minimal-tier vs full-template           | **Minimal-tier** for all phase skills + primitives (AGENTS.md:90 already broadened the definition)        | Decided          |
| 14  | Bookkeeping                             | **Slice 8** — counts, suites, decisions, parity, docs index                                               | Decided          |

---

## Section 1 — Resolved decisions with reasoning

### #1 Skill namespace — parallel-flat (decided)

`skills/team/qraspi-{questions,research,architecture,skeleton,plan,implement}/`, plus
`skills/team/fitness-functions/` and `skills/team/qraspi-graduate/`. Same tooling fact that fixed
QRSPI (qrspi-plan #1): `scripts/add_frontmatter.py` walks `skills/{team,professional}/*/` **one
level** (R§1.1), and the install glob copies the flat tree. Nesting `skills/team/qraspi/<phase>/`
is a net-new structural pattern the frontmatter script would not reach. Flat matches 100% of the
86 existing skills. The one-character near-collision with `qrspi-*` (R§2.1) is handled entirely in
the `description` fields — every QRASPI skill carries a `Do NOT use for QRSPI (existing codebase)`
negative trigger, exactly as the QRSPI skills disambiguate from deprecated RPI
(`skills/team/qrspi-research/SKILL.md:7-8`). The extra `a` is mnemonic: **A**rchitecture.

### #2 Phase-to-skill mapping — six skills, Plan/Implement are their own (decided)

QRASPI has six phases (R§2.1). Each gets one skill — the one-skill-per-phase precedent QRSPI set.
`qraspi-plan` and `qraspi-implement` do **not** route into `qrspi-plan`/`qrspi-implement` despite
near-identical core loops, for three reasons: (a) different artifact root and pre-flight gates —
`qraspi-implement` pre-flight requires the skeleton's CI green and fitness functions in place
(§4.4), which QRSPI's implement has no concept of; (b) trigger-eval disambiguation (Section 5)
needs distinct `description` fields per skill anyway; (c) routing a `/qraspi-*` command into a
`qrspi-*` skill blurs the graduation seam (#11). They stay **thin** — `qraspi-implement` delegates
the RGR inner loop to the existing `tdd` skill exactly as `qrspi-implement` does
(`qrspi-orchestrator.md:48`), duplicating nothing. Folding A+S is rejected: A is artifact-only and
S writes source (R§2.4) — they sit on opposite sides of the edit boundary (#4).

### #3 New primitives vs folded — fold three, extract one (decided: Option A)

QRSPI's "vendor 0 new primitives" doctrine (AGENTS.md:89) rested on `tdd` already existing. The
QRASPI candidates have **no full existing equivalent** (R§2.2), so that reasoning does not transfer
automatically — each is resolved on its own merits against reusability + the minimal-tier budget
(#13):

- **ADR-writing → FOLD into `qraspi-architecture`, reference `architecture-journal`.** The existing
  `architecture-journal` skill already occupies the reusable-ADR niche ("lightweight ADR templates
  with retrospective prompts", R§2.2); a new ADR primitive would overlap it and violate the
  "Companion Skills" non-overlap doctrine. The QRASPI-specific MADR variant lives in
  `qraspi-architecture/references/adr-template.md`; the alignment gate lives in the skill body.
- **C4-diagram-generation → FOLD into `qraspi-architecture`.** Tightly bound to the Architecture
  phase; one caller → no primitive (YAGNI). Conventions → `references/c4-conventions.md` (#8).
- **walking-skeleton-scaffolding → FOLD into `qraspi-skeleton`.** The walking-skeleton concept *is*
  the Skeleton phase; a separate primitive would have exactly one caller. Per-stack recipes →
  `references/archetypes/` (#6); feature-level wiring delegates to `*-feature-slice` scaffolders.
- **fitness-function-encoding → EXTRACT as primitive `fitness-functions`.** This is the one that
  earns extraction: (a) reusable outside QRASPI — any project at any maturity (including a
  *brownfield QRSPI feature*) wants to add a fitness function as a CI gate; (b) it carries
  substantial per-stack content (NetArchTest / ArchUnit / import-linter / Conftest + CI scripting)
  that would blow the Architecture skill's ≤100-line budget; (c) it has **two** QRASPI callers
  (`qraspi-architecture` specifies them, `qraspi-skeleton` lands them as gates), so it is the
  shared inner capability — the QRASPI analog of how `tdd` is shared (R§2.2). `dependency-mapper`
  (Martin metrics, R§3.3) becomes one ready-made fitness function it references, not a replacement.

> **DECIDED (owner-confirmed): Option A — extract `fitness-functions` as a new primitive skill.**
> Two callers (`qraspi-architecture` specifies, `qraspi-skeleton` lands), cross-workflow reuse (QRSPI
> brownfield features can add CI-gate fitness functions), and minimal-tier budget relief all point to
> a shared primitive — the QRASPI analog of how `tdd` is shared. This is the **first new primitive
> since the AGENTS.md:89 "QRSPI vendored 0 new primitives" decision**, so Slice 8 must log the
> exception in Persistent Decisions with the two-caller rationale (the doctrine is upheld in spirit:
> a primitive is extracted only when ≥2 callers exist and an existing skill does not already cover
> it — `dependency-mapper` covers one category, not the surface). Skill count 86 → **94**.
>
> *Rejected — Option B (fold into `qraspi-skeleton`, specs inlined in `qraspi-architecture`):* honors
> the zero-new doctrine to the letter but duplicates fitness content across two phase skills and
> pushes both toward the budget ceiling. *Rejected — Option C (defer extraction):* the two-caller
> threshold is already met today, so deferring re-works a decision the evidence already settles.

### #4 Agent topology — 2 agents by edit access (decided)

The edit boundary alternates across QRASPI's phases (Q/R/A artifact, **S source**, P artifact, **I
source** — R§2.4), but it still splits cleanly into *who may edit*: the no-edit phases (Q, R, A, P
— all produce markdown, including Plan) versus the source-writing phases (S, I). So the QRSPI
2-agent topology (orchestrator no-Edit + executor Edit) maps directly, with the seam drawn by edit
access rather than by phase order:

- **`qraspi-orchestrator`** (new, paired; mirrors `qrspi-orchestrator.md` shape) — drives Q→R→A→P.
  Tools `Read, Glob, Grep, Bash, Write` (**no Edit**). `skills:` =
  `[qraspi-questions, qraspi-research, qraspi-architecture, qraspi-plan, qraspi-graduate]`. Acts as
  the research firewall and the ADR-alignment gatekeeper.
- **`qraspi-builder`** (new, paired; mirrors `qrspi-implement.md` shape) — drives S→I. Tools
  `Read, Edit, Write, Bash, Glob, Grep` (**has Edit**). `skills:` =
  `[qraspi-skeleton, qraspi-implement, fitness-functions, tdd]`.

Phase order (S between A and P) is enforced by artifact gates (§4), not by the agent split — each
phase is a fresh session routed to the correct agent by its command. A third agent (R§5 Q4)
buys nothing: Skeleton and Implement share tools, the "CI/tests must be green" gate philosophy, and
the execution context. **+2 agents/platform → 39/39.** Reuse the 3 read-only `research-*` subagents
as-is (R§1.2) for inherited-repo Research (#10).

### #5 ADR storage + template (decided)

- **Location:** the **target project's** `docs/adr/NNNN-kebab-title.md` with sequential numbering
  (not the qraspi feature folder — ADRs are project artifacts that QRSPI later reads). Default is
  overridable via a `--adr-dir` argument / architecture.md frontmatter. Rationale: `docs/adr/` is
  the most common in-the-wild convention (R§3.1); sequential `NNNN-` numbering (adr-tools default,
  R§6.3) preserves the *order* of path-dependent decisions, which is precisely what the Architecture
  phase exists to capture. The `architecture.md` summary in the feature folder is the index that
  points at them.
- **Template:** **MADR**, not raw Nygard. R§6.3 flags that "Alternatives Considered" is a
  MADR/Tyree addition, *not* original Nygard — and the brief **requires** alternatives
  (ADRs-with-alternatives, not fait-accompli, §4.3). MADR natively carries Title / Status / Context
  / Considered Options / Decision / Consequences. Standardize on it. Template:
  `qraspi-architecture/references/adr-template.md`.

### #6 Skeleton template strategy — hybrid recipe ⊕ scaffolder (decided)

R§3.2 identifies the real gap: existing `*-feature-slice`/`mcp-server-scaffold` skills scaffold a
**feature**, not a **full repo + CI + observability + secure-by-default** skeleton. The Skeleton
phase fills that gap by composing two layers:

1. **Archetype recipe** (`qraspi-skeleton/references/archetypes/<archetype>.md`) — supplies the
   repo-level scaffold the feature-slice tools don't: project layout, CI workflow, the
   fitness-function CI gates (from #3/#7), health check, observability hook, secure-by-default
   config. Recipes are **instructions the skill follows**, not rigid copy-paste repos — this
   avoids the over-constraint / magic-words trap (R§3.5).
2. **Feature-slice scaffolder** — invoked for the *one* vertical slice the skeleton walks
   end-to-end (`dotnet-vertical-slice`, `python-feature-slice`, `rust-feature-slice`,
   `mcp-server-scaffold`, etc.).

Archetypes keyed to the five R§4 scenarios: `python-mcp-server` (§4.1), `dotnet-blazor-vertical-slice`
(§4.2), `python-fastapi-service`, `edge-ai-device` (§4.3), `eval-harness` (§4.4). **Discovery:** the
Skeleton skill reads the stack declaration from `architecture.md`/the ADRs and selects the matching
archetype by name; no match → a generic "declare-stack-and-generate" recipe. This makes Skeleton
**archetype-aware but ADR-driven** — it consumes the constraints Architecture produced (R§4.6).

### #7 Fitness-function encoding — per-stack CI gates (decided)

Mechanism is uniform — *an automated check wired into the target project's CI workflow as a
gatekeeper* (R§6.5) — but the *tool* is per-stack, owned by the `fitness-functions` primitive (#3):
NetArchTest (.NET layer rules), ArchUnit (JVM), import-linter / dependency-cruiser (Python/JS),
Conftest/OPA (policy), plus universal gates (coverage threshold, lint, dep-audit). `dependency-mapper`
(Martin metrics, R§3.3) is referenced as a ready-made coupling fitness function. Per-stack detail
lives in `fitness-functions/references/<stack>.md`. The repo's PostToolUse hooks
(`claude/global/settings.json`, R§2.2) are the *local* deterministic-gate precedent; fitness
functions are their **CI-level** analog in the target repo.

### #8 C4 format — Mermaid (decided)

**Mermaid `C4Context` + `C4Container`.** The repo is markdown-native with no build system
(R§3.4/§6.4); Mermaid renders inline in GitHub/Codeberg/VS Code markdown viewers, is
version-controllable, and is AI-generatable. Structurizr DSL is richer but needs tooling the repo
lacks. Conventions + skeleton snippets: `qraspi-architecture/references/c4-conventions.md`.

### #9 Skeleton output — runnable repo, CI-green gate (decided)

A walking skeleton is **executable by definition** (R§3.5/§6.1) — that is the whole point
(distinguishes it from a spike). The Skeleton phase's exit gate is therefore a real command: run
the target project's CI / test suite and require exit 0. This is *why* Skeleton sits on the
execution agent (#4). The over-constraint risk (R§3.5) is held off by #6's recipe-not-rigid-repo
choice. **Archetype-conditional carve-out (R§4.3):** for hardware-coupled archetypes the CI-green
gate covers build + unit tests + lint + fitness functions; the device-deploy step is a *documented
manual gate*, not auto-run — the skeleton is executable up to the hardware boundary.

### #10 Greenfield research evidence source — mode switch (decided)

`qraspi-research` pre-flight detects the mode (R§4.5, R§5 Q10):

- **`external-domain`** (default; pure greenfield, no codebase) — research the **problem domain +
  solution landscape** using the existing `research-synthesis` skill (source credibility scoring,
  cross-referencing) plus WebSearch/WebFetch. The codebase-oriented `research-*` subagents do **not**
  apply (nothing to Glob/Grep). Output is a *factual landscape map* (libraries, prior art, patterns,
  constraints), never a recommendation (§4.2).
- **`inherited-repo`** (greenfield-within-existing-repo, §4.5) — the `research-*` subagents apply
  exactly as in QRSPI: map the existing repo's conventions/hooks/layout before adding the new
  component, ticket-hidden via a neutral topic string.

Detection: pre-flight checks whether a populated source tree exists at the target. The skill body
carries both modes; the state block records `research_mode`.

### #11 Graduation handoff — explicit thin skill + command (decided)

The seam is conceptual — both workflows already share `tdd`, vertical slices, and the `research-*`
subagents (R§3.6) — so graduation is **state capture + documentation**, not new machinery. But an
explicit artifact earns its keep: QRSPI's Research assumes an existing codebase, and `graduation.md`
is what bootstraps the *first* QRSPI feature with the context QRASPI produced. Decision: a thin,
minimal-tier `qraspi-graduate` skill + `/qraspi-graduate` command, run under `qraspi-orchestrator`
(read-only; it writes one markdown artifact). No new agent. `graduation.md` captures:

1. Pointer to the target repo + its `docs/adr/` (the accepted ADRs).
2. Skeleton state — which layers the walking skeleton exercises; current CI status.
3. The landed fitness functions and where each gates.
4. The stack declaration.
5. The handoff instruction: *"V0/V1 is shipped. New features now use QRSPI — run `/qrspi-questions`
   in this repo."*

### #12 Domain-modeling sub-phase — folded into Architecture (decided)

**No 7th phase.** The existing `domain-model` skill (DDD vocabulary, `CONTEXT.md`,
`disable-model-invocation: true`, R§5 Q12) already covers this ground, and a 7th phase contradicts
the scale-down requirement (R§4.1). `qraspi-architecture` pre-flight offers an **optional** domain
step: when it detects high domain complexity, it invokes `domain-model` to produce a `CONTEXT.md`
the ADRs reference. QRASPI stays six phases.

### #13 Minimal-tier for all QRASPI skills (decided)

All eight new skills use the **minimal tier** (≤100 lines / ≤~40 imperative directives, ≥1
reference), per the QRSPI precedent AGENTS.md:90 — which *already* broadened the minimal-tier
definition to cover "thin, self-sufficient workflow-phase drivers." QRASPI phase skills are the same
primitive, so **no new governance is needed**. The heavier phases (Architecture, Skeleton) hold to
budget precisely *because* their bulk lives in `references/` (adr-template, c4-conventions,
archetypes/, fitness templates) loaded just-in-time — QRSPI's overflow strategy (R§5 Q13). The
extraction of `fitness-functions` (#3) is the structural relief valve that keeps Architecture under
budget.

### #14 Bookkeeping (decided)

All updates land in Slice 8 — enumerated in Section 7.

---

## Section 2 — Exact file layout

**Skills** (8 new, `skills/team/`, each `SKILL.md` + `references/`):

```
skills/team/fitness-functions/SKILL.md     + references/{dotnet,python,rust,policy}.md   (#3, Option A)
skills/team/qraspi-questions/SKILL.md       + references/questions-template.md
skills/team/qraspi-research/SKILL.md        + references/research-template.md, landscape-vs-codebase.md
skills/team/qraspi-architecture/SKILL.md     + references/{adr-template,c4-conventions,fitness-spec}.md
skills/team/qraspi-skeleton/SKILL.md         + references/skeleton-template.md, archetypes/<5 files>.md
skills/team/qraspi-plan/SKILL.md             + references/plan-slice-template.md
skills/team/qraspi-implement/SKILL.md        + references/implementation-log-template.md
skills/team/qraspi-graduate/SKILL.md         + references/graduation-template.md
```

**Agents** (2 new, paired — #4):

```
claude/agents/team/qraspi-orchestrator.md     opencode/agents/team/qraspi-orchestrator.md
claude/agents/team/qraspi-builder.md          opencode/agents/team/qraspi-builder.md
```

**Commands** (7, paired, flat — R§2.3):

```
claude/commands/qraspi-{questions,research,architecture,skeleton,plan,implement,graduate}.md
opencode/commands/qraspi-{questions,research,architecture,skeleton,plan,implement,graduate}.md
```

**Reused, unchanged** (referenced, never duplicated): `tdd`, `research-synthesis`, `domain-model`,
`architecture-journal`, `dependency-mapper`, the `*-feature-slice`/`*-scaffold` skills, and the 3
read-only `research-*` subagents (R§1.2, R§2.2).

**Artifact storage** — per-feature folder, parallel to QRSPI's (R§1.4):

```
thoughts/shared/qraspi/YYYY-MM-DD-{slug}/
  questions.md                      # Q
  research.md                       # R — landscape map (external) or codebase map (inherited)
  architecture.md                   # A — summary + C4 (Mermaid) + fitness-fn specs; INDEXES the ADRs
  skeleton.md                       # S — what the walking skeleton instantiates + CI status + slice backlog
  plan-{slice}.md                   # P — one per vertical slice (the next increment), status gate
  implementation-log-{slice}.md     # I — one per slice (RGR record + CI/fitness output)
  graduation.md                     # terminal handoff to QRSPI
<target-project>/docs/adr/NNNN-*.md  # A — the ACCEPTED ADRs live in the project repo, not thoughts/
```

The feature folder lives in the working repo that QRASPI bootstraps — at Questions time the repo
may be empty; the Skeleton phase scaffolds source around it, and `docs/adr/` is created in that
same repo. After graduation, QRSPI operates on the same repo (R§3.6).

> **Naming note (decided, divergence from QRSPI):** the brief specifies `plan-{slice}.md` and
> `implementation-log-{slice}.md` *per slice* at the folder top level. QRSPI uses a single `plan.md`
> and `implementation/slice-NN-*.md`. QRASPI follows the brief: greenfield grows slice-by-slice on
> the skeleton, so Plan/Implement run **once per slice** (default: the next unbuilt slice; the slice
> backlog is enumerated in `skeleton.md`). This keeps context budget low and matches greenfield's
> emergent nature.

---

## Section 3 — Per-skill frontmatter + section outline

All eight use the **minimal tier** (#13): frontmatter shape and 6-part outline match
`skills/team/qrspi-research/SKILL.md:1-94`. Frontmatter:

```yaml
---
name: qraspi-<phase>
audience: team
description: >
  QRASPI <Phase> phase -- <one-line>. Use for "/qraspi-<phase> <project>", "<trigger 1>",
  "<trigger 2>". Do NOT use for QRSPI (an EXISTING codebase / adding a feature) -- that routes to
  qrspi-<phase>. Do NOT use for the deprecated RPI workflow.
---
```

Minimal-tier outline (lean; overflow → `references/`), identical structure to the QRSPI skills:
**1** Title + epigraph · **2** Core Philosophy + Non-Negotiable Constraints (last is always the
40%/60% CONTEXT BUDGET rule, verbatim from `qrspi-questions/SKILL.md:29-30`) · **3** Workflow
(PRE-FLIGHT → phase steps → **Exit criteria**) · **4** State Block (unique XML tag) · **5** Output
Template (pointer to `references/`) · **6** Integration with Other Skills.

Per-skill specifics:

| Skill                 | Artifact produced                 | State tag                     | Phase-specific gate                                                                                          |
| --------------------- | --------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `qraspi-questions`    | `questions.md`                    | `<qraspi-questions-state>`    | Balanced cross-section checklist: functional · quality-attributes · integration · compliance · deployment · domain (§4.1); STOPS for answers |
| `qraspi-research`     | `research.md`                     | `<qraspi-research-state>`     | **Landscape map, not evaluation** (§4.2); `research_mode` switch external-domain / inherited-repo (#10)       |
| `qraspi-architecture` | `architecture.md` + `docs/adr/*`  | `<qraspi-architecture-state>` | MADR ADRs **with alternatives** (§4.3); brain-surgery alignment gate (`adrs_aligned`); fitness fns **required** |
| `qraspi-skeleton`     | `skeleton.md` + scaffolded repo   | `<qraspi-skeleton-state>`     | **Runnable; exit = CI green** (`ci_green: true`, §4.4); fitness fns wired as CI gates; selects archetype (#6)  |
| `qraspi-plan`         | `plan-{slice}.md`                 | `<qraspi-plan-state>`         | **Refuses horizontal-layer plans** (mirrors `qrspi-plan` §4.3); `status: ready-for-review`                    |
| `qraspi-implement`    | `implementation-log-{slice}.md`   | `<qraspi-implement-state>`    | **RGR gate per slice** (delegates to `tdd`); pre-flight requires `ci_green` + approved `plan-{slice}.md`       |
| `fitness-functions`   | CI-gate scripts/tests in target   | `<fitness-functions-state>`   | Per-stack tool selection; lands as a CI gatekeeper, not a one-off check (§4.4, #7)                            |
| `qraspi-graduate`     | `graduation.md`                   | `<qraspi-graduate-state>`     | Captures ADRs + skeleton state + fitness fns + stack; hands off to QRSPI (#11)                                |

**Agents** — `qraspi-orchestrator` and `qraspi-builder` follow the **full 10-section agent
template** (AGENTS.md:77, mirrors `qrspi-orchestrator.md`), because the cross-phase *sequencing*
(orchestrator) and *execution-loop* (builder) weight lives in the persona, while each phase skill
stays self-sufficient (#13). Claude frontmatter: `name, description, tools, model: inherit,
skills:[…]`; OpenCode: `description, mode, boolean tools (edit: false|true), task: true` with
`skill({ name })` body calls (matches `opencode/agents/team/qrspi-orchestrator.md`). Unique state
tags `<qraspi-orchestrator-state>`, `<qraspi-builder-state>`.

**Commands** — Claude format per CLAUDE.md "When Adding a Command": `description` with trigger +
`/qraspi-<phase> <project>`, scoped `allowed-tools`, a `!`-injected `<live_state>` block (an `ls` of
`thoughts/shared/qraspi/` like `claude/commands/qrspi-research.md:6-10`), then route to the matching
agent + restate the phase gate. OpenCode adds `agent:` + `subtask:` — `subtask:true` for
Q/R/A/P/graduate (read-heavy alignment), `subtask:false` for skeleton/implement (write source).

---

## Section 4 — Default-behavior enforcement (no magic words)

QRASPI inherits QRSPI's three no-magic-words mechanisms (rich `description` triggers, artifact
pre-flight gates, orchestrator-owned ordering — qrspi-plan #5). The four greenfield-specific
enforcements the brief calls out:

### 4.1 Questions — balanced cross-section by content, not by request

`qraspi-questions` SURFACE step carries a **fixed greenfield category checklist** in the skill body
(exactly as `qrspi-questions/SKILL.md:42-44` carries `data model · API · UI · integration · auth ·
testing · edge cases · migration`). QRASPI's checklist is greenfield-tuned:

```
functional scope · quality attributes (the -ilities) · integration/external systems ·
compliance/regulatory · deployment/runtime target · data & domain model
```

The skill enumerates a question for **every** category whether or not the user named it; the state
block's `areas_covered` array must list all six before WRITE. The user never asks for each type —
the balance is structural, baked into the SURFACE enumeration.

### 4.2 Research — factual landscape map, not premature recommendations

The greenfield equivalent of QRSPI's ticket-hiding firewall (`qrspi-research/SKILL.md:18-30`): there
is no ticket and (in external-domain mode) no codebase, so the failure shifts from "biased map" to
"premature solution" (the skill picking FastAPI+Postgres before Architecture). Two structural guards:

1. **Framing in Core Philosophy** — verbatim rule: *"research.md is a factual landscape map, not an
   evaluation. Catalog what EXISTS in the solution space; convert every comparative judgment into an
   open question for the Architecture phase. Recommendations are A's job, gated behind ADRs."* This
   mirrors `qrspi-research` constraint #2 ("OBJECTIVE only … convert opinion to open question").
2. **Mode-specific firewall** (#10): inherited-repo mode keeps the read-only-subagents + neutral-topic
   firewall; external-domain mode uses `research-synthesis`'s source-credibility discipline (facts
   with citations) and bans recommendations via the state flag `recommendations_made: false` (must
   stay false, exactly like `qrspi-research`'s `ticket_loaded: false`).

### 4.3 Architecture — ADRs with alternatives, human-aligned, fitness functions required

Three structural defaults make the *right* ADR shape the only shape that passes:

1. **Alternatives are mandatory, not optional.** `references/adr-template.md` is MADR with a required
   **Considered Options** section; the skill self-check fails any ADR with < 2 alternatives. A
   fait-accompli ADR cannot reach WRITE. (#5)
2. **Brain-surgery alignment before lock** — direct reuse of `qrspi-spec`'s STOP-and-LOOP gate
   (`qrspi-spec/SKILL.md:48-50`): write the ADR set as `status: proposed`, **STOP**, present to the
   human, loop on redirection, set `status: accepted` only after approval. State flag
   `adrs_aligned: true|false` is the gate — the analog of `qrspi-spec`'s `design_approved`.
3. **Fitness functions are required output, not optional.** Exit criteria require a
   fitness-function spec section in `architecture.md` — ≥1 fitness function for every accepted ADR
   that names a measurable quality attribute. State block carries `fitness_functions_specified:
   [count]`, gated > 0. Authoring delegates to the `fitness-functions` primitive (#3).

### 4.4 Skeleton — executable, not aspirational (CI green is the gate)

`qraspi-skeleton` WRITE step ends with a **real command**, not a claim: run the scaffolded project's
CI / test suite via Bash and require exit 0. The state block carries `ci_green: true|false`; the
skill **cannot report COMPLETE with `ci_green: false`**. The fitness functions specified in
Architecture must be wired and passing as CI gates — that is *part of* CI green. This is the
repo/CI-level analog of `qrspi-implement`'s "RUN — must PASS (GREEN)" step
(qrspi-plan §4.4). Hardware archetypes: CI-green covers build+unit+lint+fitness, device-deploy is a
documented manual gate (#9).

### 4.5 Plan & Implement — same as QRSPI

- **Plan:** `qraspi-plan` carries the horizontal-layer **refusal gate** verbatim from
  `qrspi-plan` (qrspi-plan §4.3 / `qrspi-orchestrator.md:126-128` RE-SLICE GATE). A horizontal plan
  never reaches WRITE.
- **Implement:** `qraspi-implement` runs the RED-GREEN-REFACTOR slice loop, delegating the inner
  loop to `tdd` (qrspi-plan §4.4). Added pre-flight: refuses to start unless `skeleton.md` reports
  `ci_green: true` and an approved `plan-{slice}.md` exists for the slice.
- **Context budget:** every QRASPI skill carries the 40%/60% checkpoint-to-disk rule and a
  `context_budget` state field (qrspi-plan §4.5); the per-feature folder makes fresh sessions cheap.

---

## Section 5 — Verification strategy (trigger evals)

Follow the existing 200-trigger-eval pattern (qrspi-plan §5; evals authored later, **not** here).
The dominant new risk is **QRASPI ↔ QRSPI collision** — same workflow shape, the discriminator is
**greenfield (new system, no codebase) vs brownfield (existing codebase, add a feature)**. The
canonical pair the brief names:

- *"build a new MCP server from scratch"* → **QRASPI** (`/qraspi-questions`)
- *"add a tool to our existing MCP server"* → **QRSPI** (`/qrspi-questions`)

Per-skill eval coverage:

| Skill                 | MUST activate on                                                              | MUST NOT activate on                                          | Disambiguation focus                          |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `qraspi-questions`    | "new project from scratch", "greenfield X", "/qraspi-questions X"             | "add feature to existing X", "/qrspi-questions"               | vs `qrspi-questions` (greenfield vs brownfield) |
| `qraspi-research`     | "research the solution landscape for new X", "what libraries exist for X"     | "research our codebase for X", "/qrspi-research"              | vs `qrspi-research` (external/domain vs codebase) |
| `qraspi-architecture` | "what architecture for new X", "write the ADRs for X", "C4 for new system X"  | "architecture review of existing X" (→ `architecture-review`) | vs `architecture-review`, `architecture-journal` |
| `qraspi-skeleton`     | "scaffold the walking skeleton for X", "stand up V0 of X with CI"             | "scaffold a feature slice" (→ `*-feature-slice`)              | vs the feature-slice scaffolders (repo vs slice) |
| `qraspi-plan`         | "plan the first slice of new X", "/qraspi-plan X"                             | "/qrspi-plan X", "/rpi-plan X"                                | vs `qrspi-plan`, deprecated `rpi-plan`        |
| `qraspi-implement`    | "implement the slice on the skeleton", "/qraspi-implement"                    | "/qrspi-implement", "run tdd"                                 | vs `qrspi-implement`, `tdd`                    |
| `fitness-functions`   | "add a fitness function", "wire an arch test as a CI gate", "enforce layering in CI" | "run the tests", "review architecture"                | vs `dependency-mapper`, `tdd`                  |
| `qraspi-graduate`     | "graduate this to QRSPI", "the V1 is done, hand off to feature workflow"      | generic "we're done", "ship it"                               | terminal — must not fire mid-workflow         |

Eval sets must include a **brownfield negative** for every QRASPI skill (and a greenfield negative
for every QRSPI skill, when those evals are revised) so the model routes on the greenfield/brownfield
axis, not on shared keywords. `fitness-functions` needs cross-suite negatives vs `dependency-mapper`
(it *uses* it) and `tdd`.

---

## Section 6 — Implementation sequence (vertical slices)

Eat our own dog food: each slice ends at an independently usable checkpoint. Order respects
dependencies (primitive → entry phases → later phases → graduation → docs).

### Slice 1 — `fitness-functions` primitive (#3, Option A)

- Write `skills/team/fitness-functions/SKILL.md` (minimal tier) + per-stack `references/`
  (`dotnet.md` NetArchTest, `python.md` import-linter, `rust.md`, `policy.md` Conftest). Reference
  `dependency-mapper` as a ready-made coupling fitness function.
- **Checkpoint:** `/`-invoking nothing yet, but the skill is loadable and can author a CI-gate
  fitness function for a given stack on request. Skill count 86 → 87. *(If #3 resolves to Option
  B/C, this slice is a no-op confirmation and the content moves into `qraspi-skeleton/references/`.)*

### Slice 2 — `qraspi-questions` + `qraspi-research` (smallest viable QRASPI entry point)

- Write both SKILL.md (+ references, incl. `research/references/landscape-vs-codebase.md` for the
  mode switch #10), the `qraspi-orchestrator` agent pair (`skills:[qraspi-questions,
  qraspi-research]` initially, no Edit), and both command pairs. Reuse the existing `research-*`
  subagents (inherited-repo mode) and `research-synthesis` (external-domain mode).
- **Checkpoint:** a user runs `/qraspi-questions` then `/qraspi-research` and gets `questions.md`
  (balanced cross-section) + a `research.md` landscape map in a feature folder. Q→R works
  standalone. Skill count 88.

### Slice 3 — `qraspi-architecture`

- Write SKILL.md + references (`adr-template.md` MADR, `c4-conventions.md` Mermaid,
  `fitness-spec.md`); extend `qraspi-orchestrator` `skills:` to include it. Implements the ADR
  alignment gate (§4.3), Mermaid C4, the required-fitness-functions exit gate (invokes
  `fitness-functions`), and the optional `domain-model` step (#12).
- **Checkpoint:** `/qraspi-architecture` consumes `research.md`, produces aligned MADR ADRs in
  `docs/adr/` + an `architecture.md` summary with C4 + fitness-function specs. Q→R→A works. Skill 89.

### Slice 4 — `qraspi-skeleton` + `qraspi-builder` agent

- Write SKILL.md + `references/skeleton-template.md` + `references/archetypes/<5>.md`; write the
  `qraspi-builder` agent pair (`skills:[qraspi-skeleton, fitness-functions, tdd]`, has Edit).
  Implements archetype discovery (#6), feature-slice delegation, fitness-functions-as-CI-gates, and
  the **CI-green exit gate** (§4.4).
- **Checkpoint:** `/qraspi-skeleton` consumes `architecture.md`, scaffolds a runnable repo with CI
  passing and fitness functions gating. Q→R→A→S works; a walking skeleton stands up green. Skill 90.

### Slice 5 — `qraspi-plan`

- Write SKILL.md + `references/plan-slice-template.md`; extend `qraspi-orchestrator` `skills:`.
  Implements the horizontal-refusal gate (§4.5); produces `plan-{slice}.md` for the next unbuilt
  slice from the `skeleton.md` backlog; `status: ready-for-review`.
- **Checkpoint:** `/qraspi-plan` produces a vertically-sliced `plan-{slice}.md` and refuses a
  horizontal plan. Q→R→A→S→P works. Skill 91.

### Slice 6 — `qraspi-implement`

- Write SKILL.md + `references/implementation-log-template.md`; extend `qraspi-builder` `skills:`.
  Reuses `tdd` (RGR inner loop) and the vertical-slice discipline; pre-flight requires `ci_green` +
  approved `plan-{slice}.md`; writes `implementation-log-{slice}.md` per slice.
- **Checkpoint:** `/qraspi-implement` grows the skeleton one green slice at a time with RGR. Full
  Q→R→A→S→P→I pipeline works end-to-end on a greenfield project. Skill 92.

### Slice 7 — `qraspi-graduate` (graduation mechanism, #11)

- Write SKILL.md + `references/graduation-template.md` + `/qraspi-graduate` command pair; extend
  `qraspi-orchestrator` `skills:`. Produces `graduation.md` capturing ADRs + skeleton state +
  fitness functions + stack + the QRSPI handoff instruction.
- **Checkpoint:** `/qraspi-graduate` produces `graduation.md`; a user can then start `/qrspi-questions`
  in the same repo with full inherited context. QRASPI → QRSPI seam is real and usable. Skill 93.

### Slice 8 — Bookkeeping, docs & workflow index

- **AGENTS.md:** add a "QRASPI Workflow" Skill-Suites row (sibling of the QRSPI row); update Open
  Loops counts (skills 86→93/94, agents 37→39, commands 15→22); add Persistent-Decisions rows for
  (a) QRASPI greenfield workflow + the 2-agent edit-seam (#4), (b) the #3 primitive resolution as
  finally decided, (c) the per-feature `thoughts/shared/qraspi/` folder + per-slice plan/log naming
  (#5/#2-layout), (d) MADR-with-alternatives as the ADR standard (#5), (e) Mermaid C4 (#8),
  (f) CI-green as the Skeleton exit gate (#9).
- **README.md:** add a "QRASPI Workflow Suite" section (mirror the QRSPI section at README:195-209)
  + a command-table block (mirror README:394-398); bump skill/agent/command count badges; add the
  agents note (mirror README:364).
- **docs/:** update `docs/rpi-and-spec-driven-dev-overview.md` (R§1.6 — still RPI-framed) to document
  QRASPI as the greenfield workflow alongside QRSPI as the brownfield workflow, and the graduation
  seam between them.
- **`.matt-pocock-attribution.yml`:** no change (nothing vendored; `fitness-functions` is original).
- **Checkpoint:** `find skills -name SKILL.md | wc -l` matches the README badge;
  `find {claude,opencode}/agents -name '*.md' | wc -l` → 39 each; commands → 22 each; every QRASPI
  skill has ≥1 reference; AGENTS.md/README/overview all document QRASPI.

---

## Section 7 — Bookkeeping touchpoints (consolidated, R§5 Q14)

- README skill-count badge + counts line + new "QRASPI Workflow Suite" section + command table.
- AGENTS.md Open Loops counts (skills 86→93/94, agents 37→39, commands 15→22), Skill Suites table,
  Persistent Decisions (6 new rows, §6 Slice 8).
- Agent parity 37→39; command parity 15→22 (both platforms).
- `docs/rpi-and-spec-driven-dev-overview.md` reframed for QRASPI + QRSPI + graduation.
- `.matt-pocock-attribution.yml` — **no change** (original work, nothing vendored).
- Each new skill: ≥1 `references/` file (minimal-tier rule); unique State-Block XML tag.
- **Interaction with the QRSPI sunset (R§1.6, ~2026-09-01):** independent workstream. At sunset the
  4 `rpi-*` skills are removed (−4); QRASPI's +7/+8 is additive and unaffected. Final post-both
  state: skills 89/90, agents 37, commands 22.

---

## What this plan is NOT doing

- Not writing any skill, agent, or command file (that is Implement).
- Not building separate ADR-writing, C4, or walking-skeleton primitive skills — those fold into the
  phase skills + `references/` (#3). The only extracted primitive is `fitness-functions` (Option A,
  owner-confirmed in #3).
- Not adding a 7th phase for domain modeling — `domain-model` is referenced (#12).
- Not routing `/qraspi-plan`/`/qraspi-implement` into the QRSPI skills (#2).
- Not changing the behavior of the reused `research-*` subagents, `tdd`, or `research-synthesis`.
- Not introducing a `skills/primitives|vendor/` namespace (no precedent, R§5 Q1).
- Not performing the QRSPI sunset deletions (separate scheduled workstream, R§1.6).

## Status — all 14 questions resolved, Implement can proceed

The one open call (Section 1 #3 — `fitness-functions`) is resolved **Option A (extract)**,
owner-confirmed. Slice 1 builds the primitive; final skill count 86 → 94; Slice 8 logs the
new-primitive exception in AGENTS.md Persistent Decisions.

This plan is `status: ready-for-review` with **all 14 questions decided**. Review it, then start a
NEW session and run Implement: Slices 1→8 are the build, each ending at an independently usable
checkpoint.
