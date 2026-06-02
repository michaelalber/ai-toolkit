---
date: 2026-06-01T00:00:00
repository: ai-toolkit
topic: "QRSPI workflow — repo integration research (RPI Research phase)"
tags: [research, qrspi, rpi, skills, agents, commands, workflow]
git_commit: 7044b767229a8f80da640e34a98a04900a7576e0
status: complete
phase: Research (R)
---

# Research: Adding a QRSPI Workflow to ai-toolkit

## Research question

How does this repository compose skills, agents, and commands today, and what is the
factual integration surface for adding a new QRSPI (Questions–Research–Spec–Plan–Implement)
workflow alongside the existing four RPI skills? This artifact documents *what exists*. It
proposes no solution — that is the Plan phase.

**Convention note:** The repo's own convention is to write research artifacts to
`thoughts/shared/research/YYYY-MM-DD-topic-slug.md` (rpi-research SKILL.md:98). This session
was explicitly directed to write to `thoughts/qrspi-research.md`, so it does not follow that
convention. Flagging, not resolving.

---

## Section 1 — Repo convention inventory

### 1.1 Skill location and frontmatter

- Skills do **not** live at `skills/<name>/`. They live under an **audience subdirectory**:
  `skills/team/<name>/` (63 skills) and `skills/personal/<name>/` (18 skills). Confirmed by
  `ls skills/` → `personal team`, and `scripts/add_frontmatter.py:4-5,85` which maps
  `audience: team → skills/team/*` and `audience: personal → skills/personal/*`.
- **CONFLICT to flag (do not resolve):** `AGENTS.md:126` states "Each skill lives in
  `skills/<name>/`". The actual on-disk layout is `skills/team/<name>/` and
  `skills/personal/<name>/`. AGENTS.md's path is stale relative to the filesystem. Treat
  AGENTS.md as authoritative per session constraints, but this specific path claim is
  contradicted by the filesystem and `scripts/add_frontmatter.py`.
- Each skill dir contains `SKILL.md` + a `references/` directory (AGENTS.md:126,
  observed for all four rpi-* skills).

**Frontmatter shape (observed, rpi-research/SKILL.md:1-8):**
```yaml
---
name: rpi-research
audience: team        # <-- present in actual files, NOT documented in AGENTS.md:130-137
description: >
  ... Use for "/rpi-research topic", "research the codebase for X", ...
---
```
- AGENTS.md:130-137 documents only `name`, `description`, optional `disable-model-invocation`.
  The `audience:` field is present in real files but undocumented in the frontmatter spec —
  it is driven by `scripts/add_frontmatter.py`. Minor doc/file drift to note.
- Vendored (Matt Pocock) skills add three extra frontmatter keys (grill-me/SKILL.md:4-6):
  `source: mattpocock/skills`, `source_commit: unknown`,
  `source_note: "Modified locally — see .matt-pocock-attribution.yml for details"`.

### 1.2 Skill tiers and section structure

- Two tiers (AGENTS.md:139-147): **Minimal** (≤100 lines, ≥1 reference, no prescribed
  sections, often `disable-model-invocation: true`) and **Full-template** (≤400 lines,
  10 mandatory sections, ≥2 references).
- 10 mandatory sections, in order (AGENTS.md:174-187): Title+Epigraph, Core Philosophy,
  Domain Principles Table (10 rows: Priority/Description/Applied As), Workflow (phased with
  exit criteria), State Block (unique XML tag), Output Templates, AI Discipline Rules
  (WRONG/RIGHT), Anti-Patterns Table (10 rows), Error Recovery (3-4 scenarios),
  Integration with Other Skills. Gold standard: `skills/team/architecture-review/`… —
  note AGENTS.md:187 cites `skills/architecture-review/SKILL.md` (stale path; actual is
  under an audience subdir; architecture-review is in `skills/personal/`).
- All four rpi-* skills follow the full template. Section counts/line counts:
  - rpi-research/SKILL.md — 388 lines, 10 sections + 2 extra adapter sections
    (".NET/Blazor Adapter Notes", "Python Adapter Notes") + a "When NOT to Use RPI" section.
  - rpi-plan/SKILL.md — 197 lines, includes the two adapter sections.
  - rpi-implement/SKILL.md — 201 lines, includes the two adapter sections.
  - rpi-iterate/SKILL.md — 336 lines, includes a "Change log" section; no adapter sections.

### 1.3 Prose voice (sampled, quote sparingly)

- Each full skill opens with 1-2 epigraph quotes, often "Adapted from <person>"
  (rpi-research:12-15 quotes Weinberg; rpi-plan:11 quotes Eisenhower's "Plans are worthless…").
- Core Philosophy is declarative and names the failure it prevents — e.g. "Context pollution
  is the primary reason AI-assisted implementations fail on complex tasks" (rpi-research:19).
- Constraints are enumerated as a numbered "Non-Negotiable Constraints" list
  (rpi-research:23-29).
- Discipline rules use literal `WRONG:` / `RIGHT:` fenced blocks (rpi-research:203-245).
- Voice is second-person imperative to the agent, present tense, no hedging.

### 1.4 Other convention sources

- `AGENTS.md` (root, 275 lines) — authoritative project conventions; "Persistent Decisions"
  table (lines 73-88) and "Open Loops" (91-96) record durable decisions and counts.
- `CLAUDE.md` (root) — thin pointer to AGENTS.md plus a Quick Reference + checklists for
  adding skills/commands and the hook-enforcement table.
- `README.md` (30 KB), `DEVELOPER.md`, `intent.md`, `constraints.md`, `evals.md`,
  `docs/` — additional context. README carries a skill count + table that must be updated
  when skills change (CLAUDE.md "When Adding a Skill" step 5).
- `.matt-pocock-attribution.yml` (root) — machine-readable provenance ledger for vendored
  skills (see 1.5).

### 1.5 Vendored / third-party attribution pattern

Matt Pocock's skills are kept in-tree as ordinary `skills/team/<name>/` skills with **visible
credit at three layers**:
1. **Frontmatter keys** `source` / `source_commit` / `source_note` (grill-me/SKILL.md:4-6).
2. **Description line** ending `Ported from https://github.com/mattpocock/skills (Matt Pocock).`
   or `Source: https://github.com/mattpocock/skills/tree/main/<name> (Matt Pocock)`
   (zoom-out, to-prd, to-issues, caveman, improve-codebase-architecture, domain-model,
   triage-issue, grill-me — all carry this line in description).
3. **Root ledger** `.matt-pocock-attribution.yml` with per-skill `upstream_path`,
   `locally_modified`, and a `modifications_summary` paragraph. Header notes
   `source_commit: unknown` for all entries and instructs re-diffing on re-vendor.
- Currently vendored: grill-me, caveman, to-prd, to-issues, zoom-out,
  improve-codebase-architecture (in the YAML); domain-model and triage-issue also carry the
  "Ported from" description line. No separate `skills/vendor/` namespace exists — vendored
  skills sit beside first-party skills, distinguished only by metadata.
- Observation (not a repo fact): the live skill list in this session includes `qa` and
  `design-an-interface` ("Ported from mattpocock") but neither exists in the repo source
  (`find skills` finds no `qa`/`design-an-interface` dir). The installed machine skill set is
  a superset of the repo; do not assume these are in-repo.

### 1.6 thoughts/ layout

```
thoughts/
  skills-complexity-review.md          # loose top-level doc
  shared/
    plans/    2026-04-19-*.md          # plan artifacts, dated, kebab-slug
    research/ 2026-04-19-*.md          # research artifacts, dated, kebab-slug
```
- Naming: `YYYY-MM-DD-topic-slug.md` (rpi-research:98, observed in shared/research/ and
  shared/plans/).
- Research-artifact frontmatter (observed, shared/research/2026-04-19-skills-and-agents-inventory.md:1-7):
  `date`, `repository`, `topic`, `tags`, `git_commit`, `status`.
- rpi-plan writes to `thoughts/shared/plans/`, rpi-implement reads from there
  (rpi-research:55, Integration tables).

---

## Section 2 — Current skill composition model

Three primitives compose, each in its own directory and platform-paired:

### 2.1 Skills (model-invoked)
- `skills/{team,personal}/<name>/SKILL.md` (+ `references/`). Auto-loaded by the model when
  the `description` trigger matches (AGENTS.md:151). `disable-model-invocation: true` opts a
  skill out of auto-firing (AGENTS.md:135, used by interactive skills).

### 2.2 Agents (sub-agent definitions, dual-platform)
- `claude/agents/{team,personal}/<name>.md` and `opencode/agents/<name>.md`. Counts must
  reach parity (AGENTS.md:94 records "Claude Code (35) vs OpenCode (35)").
- Claude format: frontmatter `name`, `description`, `tools`, `model: inherit`, `skills:` array
  (AGENTS.md:201-211). Body follows a 10-section agent template (AGENTS.md:231-243): Title,
  Core Philosophy, Guardrails, Autonomous Protocol, Self-Check Loops, Error Recovery,
  AI Discipline Rules, Session Template, State Block (unique XML tag), Completion Criteria.
- OpenCode format: frontmatter `description`, `mode: subagent`, boolean `tools:` map;
  skills invoked via `skill({ name: "..." })` calls in the body (AGENTS.md:213-229).
- **RPI already uses the "sub-agents as context firewalls" pattern.** Five RPI agents exist
  in `claude/agents/team/`:
  - `rpi-planner.md` — orchestrator; `tools: Read, Glob, Grep, Bash, Write`; `skills:
    [rpi-research, rpi-plan, rpi-iterate]`; cannot edit source files
    (rpi-planner.md:1-9). Its epigraph quotes "Dex Horthy, Advanced Context Engineering"
    on context pollution (rpi-planner.md:18-19).
  - `rpi-file-locator.md` — read-only; `tools: Read, Glob, Grep`; `skills: []`
    (rpi-file-locator.md:1-7).
  - `rpi-code-analyzer.md`, `rpi-pattern-finder.md` — read-only analysis subagents.
  - `rpi-implement.md` — execution agent.
- rpi-research SKILL.md spawns `@rpi-file-locator`, `@rpi-code-analyzer`,
  `@rpi-pattern-finder` concurrently via the Task tool (rpi-research:77-82). This is the
  existing precedent for QRSPI's "sub-agents as context boundaries" requirement.

### 2.3 Commands (user-invoked `/slash`)
- `claude/commands/<name>.md` and `opencode/commands/<name>.md` — flat (no team/personal
  split). 10 commands each, parity required (AGENTS.md:95): arch-review, code-review,
  context-prime, evaluate-tests, grill-me, migrate, new-feature, research, security-review, tdd.
- Claude command frontmatter: `description` (with trigger phrase), `allowed-tools`; body uses
  `!`-prefixed shell injection for live state and `$ARGUMENTS` (CLAUDE.md "When Adding a
  Command"; research.md observed).
- OpenCode adds `agent:`, `subtask:`, optional `model:` (CLAUDE.md). `subtask: true` for
  read-heavy commands, `false` for file-writing commands.
- **There is NO `/rpi-research`, `/rpi-plan`, `/rpi-implement`, or `/rpi-iterate` command**
  (`grep -rl rpi claude/commands opencode/commands` → empty). RPI is invoked purely via
  skill triggers / the rpi-planner agent. The trigger phrase "/rpi-research topic" lives only
  inside the skill `description` as a *natural-language* trigger, not as a real command file.

### 2.4 Install mapping
- `scripts/install-claude.sh:16` runs `cp -rv skills/* ~/.claude/skills/` — copies the entire
  `skills/` tree, so the `team/` and `personal/` subdirs are **preserved** into the install
  target (`~/.claude/skills/team/<name>/`). Agents and commands are flattened via `find … -exec
  cp` (install-claude.sh:15,17).

### 2.5 Composition summary
A workflow today = N skills (`skills/team/`) + supporting agents (paired
`claude/agents/team/` + `opencode/agents/`) that the orchestrator skill spawns as context
firewalls + optional `/slash` commands (paired claude/opencode). RPI uses skills + agents but
**no commands**.

---

## Section 3 — QRSPI integration surface (facts + decisions to make, no recommendation)

### 3.1 Where new skill files would land
- First-party → `skills/team/<...>/SKILL.md` with `audience: team` frontmatter and a
  `references/` dir (matches all rpi-* skills). `skills/personal/` is for personal-audience
  skills only.
- Naming is the open decision (see Section 4 #1): parallel `skills/team/qrspi-*` vs nested
  `skills/team/qrspi/<phase>/`. **Note:** every existing skill is a flat
  `skills/team/<name>/` dir; there is currently **no nested grouping** anywhere in the repo,
  and `add_frontmatter.py:85` walks `skills/{team,personal}/*/SKILL.md` (one level). A nested
  layout would be a new structural pattern and may not receive `audience` frontmatter from
  the existing script.

### 3.2 Vendored primitive placement
- Red-Green-Refactor TDD and vertical-slice are attributed to Matt Pocock in the QRSPI brief.
  The repo already has TDD skills (`tdd`, `tdd-implementer`, `tdd-refactor`, `tdd-agent`,
  `tdd-pair`, `tdd-verify`, AGENTS.md:262) and vertical-slice scaffolders
  (`dotnet-vertical-slice`, `python-feature-slice`, `rust-feature-slice`). Whether QRSPI
  reuses these or vendors new "primitive" skills is a decision (Section 4 #2). No
  `skills/primitives/`, `skills/_shared/`, or `skills/vendor/` namespace exists today —
  introducing one is a new pattern; the established alternative is to keep skills flat with
  `.matt-pocock-attribution.yml` ledger entries.

### 3.3 Agent surface
- Precedent: RPI defines 5 dual-platform agents as context firewalls. QRSPI's "sub-agents as
  context boundaries, cheaper models for scoped tasks" maps directly onto this pattern. Any
  new agents need paired `claude/agents/team/` + `opencode/agents/` files and must update the
  parity counts (AGENTS.md:94, currently 35/35).

### 3.4 Command surface
- RPI ships zero commands, so QRSPI has no `/rpi-*` command precedent to parallel. If QRSPI
  adds commands, they go in paired `claude/commands/` + `opencode/commands/` (flat), update
  the 10/10 parity count (AGENTS.md:95), and follow the shell-injection format.

### 3.5 Bookkeeping touchpoints any QRSPI addition must update
- README skill count + table (CLAUDE.md "When Adding a Skill" #5).
- AGENTS.md "Open Loops" skill count (currently 81; AGENTS.md:93) and "Skill Suites" table
  (AGENTS.md:271 has an "RPI Workflow" suite row — QRSPI would add or extend a suite row).
- AGENTS.md "Persistent Decisions" table for any new structural decision.
- Agent/command parity counts if agents/commands are added.
- `.matt-pocock-attribution.yml` if any Pocock-derived primitive is vendored.

---

## Section 4 — Open questions for the Plan phase

Each item states the decision and the criteria the Plan must weigh. No recommendation given.

1. **Skill layout: parallel-flat vs nested.**
   `skills/team/qrspi-questions/`, `…-research/`, `…-spec/`, `…-plan/`, `…-implement/`
   (parallel to `rpi-*`) **vs** `skills/team/qrspi/{questions,research,spec,plan,implement}/`.
   Criteria: flat matches 100% of existing skills and the one-level walk in
   `add_frontmatter.py:85` and `install-claude.sh` glob; nested groups the workflow but is a
   net-new structural pattern that may break frontmatter tooling and install copying. Decide
   which one the tooling actually supports without modification.

2. **Shared-primitive placement and reuse.**
   Do Red-Green-Refactor and vertical-slice become new vendored skills, or does QRSPI
   reference the existing `tdd*` and `*-feature-slice` skills via Integration sections?
   Criteria: DRY vs. self-containment; whether a `skills/primitives|_shared|vendor/` namespace
   is worth introducing (no precedent exists) vs. flat + attribution ledger (established
   precedent). If new Pocock-derived skills are vendored, the 3-layer attribution pattern
   (1.5) and `.matt-pocock-attribution.yml` entry are mandatory.

3. **Per-phase sub-agents.**
   Does each QRSPI phase get its own `claude/agents/team/` + `opencode/agents/` firewall
   agent (mirroring RPI's 5 agents), or do phases reuse/extend the existing rpi-* agents?
   Criteria: QRSPI's "sub-agents as context boundaries (cheaper models for scoped tasks, not
   personas)" requirement vs. agent-count parity overhead (every new agent = 2 files + parity
   bump). Also: cheaper-model assignment — does the `model:` field get set per agent?

4. **Command surface and syntax.**
   Add `/qrspi-q … /qrspi-i` (5 commands) **or** a single `/qrspi <phase>` dispatcher **or**
   no commands (RPI's choice — skills only). Criteria: RPI's no-command precedent vs.
   discoverability; if commands are added, claude/opencode parity and the shell-injection
   format apply. Note the brief's failure-mode #2 (magic words) argues against syntax that
   *requires* memorized phrases.

5. **No-magic-words activation (failure mode #2).**
   How does each phase's `description` frontmatter make correct behavior the default without
   requiring trigger incantations? Criteria: RPI encodes triggers as multiple natural-language
   phrases in `description` (rpi-research:5-7); QRSPI must ensure that the *absence* of a magic
   phrase still routes correctly (e.g., Spec phase must not be skippable). Decide whether
   sequencing is enforced by skill content, by the orchestrator agent, or by `disable-model-invocation`.

6. **Instruction-budget discipline (failure mode #1).**
   QRSPI's premise is that RPI grew to 85+ instructions and frontier LLMs degrade past
   ~150-200 (Section 5). The four rpi-* skills are 197-388 lines each with 10 sections + 2
   adapter sections. Criteria: the Plan must decide a per-skill instruction ceiling and whether
   QRSPI skills can stay under the full-template's mandatory 10 sections (AGENTS.md:174-187) —
   i.e., does the 10-section requirement itself conflict with the instruction-budget goal?
   This is a potential tension between AGENTS.md's template mandate and QRSPI's core thesis.

7. **rpi-iterate disposition.**
   Does `rpi-iterate` graduate into a shared post-implementation/plan-revision skill both RPI
   and QRSPI use, stay RPI-only, or get a QRSPI equivalent? Criteria: QRSPI's 8-stage model has
   no explicit "iterate" stage; revision in QRSPI happens at the Spec ("brain surgery") gate.
   Decide whether iterate is cross-workflow shared infrastructure or workflow-specific.

8. **RPI coexistence / deprecation stance.**
   QRSPI is publicly positioned as Horthy's *replacement* for RPI. Does this repo keep both
   workflows side by side, mark RPI deprecated, or migrate RPI users to QRSPI? Criteria:
   "Maintain" phase (AGENTS.md:22) favors additive change; the Skill Suites table and README
   need a coherent story. Decision affects whether shared agents are renamed.

9. **Spec-phase naming reconciliation.**
   The brief's 5-phase model labels phase 3 "S (Spec) = Design Discussion + Structure Outline,"
   but the source blog labels them as separate stages D (Design Discussion) and S (Structure
   Outline), with P (Plan) as stage 5 (Section 5). Criteria: the Plan must pick one canonical
   naming for skills/commands and document the mapping so the 8-stage source and 5-phase
   implementation don't drift.

10. **Artifact paths and frontmatter.**
    QRSPI produces `questions.md`, a research/technical map, a ~200-line spec, and a plan. Do
    these reuse `thoughts/shared/research|plans/` with the dated-slug convention, or get
    QRSPI-specific locations (e.g., `thoughts/shared/qrspi/`)? Criteria: reuse matches RPI and
    the committed-artifacts principle (rpi-research:55); new paths add a structural pattern.

11. **Doc-drift conflicts to resolve while editing.**
    AGENTS.md:126 (`skills/<name>/`) and AGENTS.md:187 (`skills/architecture-review/SKILL.md`)
    are stale vs. the `skills/team|personal/` reality, and `audience:` frontmatter is
    undocumented (Section 1.1). The Plan should decide whether QRSPI work also corrects these
    (Boy Scout rule) or leaves them — and must not propagate the stale path.

---

## Section 5 — External source notes (QRSPI)

Source: `https://alexlavaee.me/blog/from-rpi-to-qrspi/` (fetched 2026-06-01), corroborated by
the task brief which also cites
`https://alexlavaee.me/blog/harness-engineering-why-coding-agents-need-infrastructure` and
`https://linearb.io/dev-interrupted/podcast/dex-horthy-humanlayer-rpi-methodology-ralph-loop`.

### 5.1 The 8 stages → 5 user-facing phases
The blog defines **8 stages**, grouped as 5 alignment stages + 3 execution stages:

Alignment:
1. **Questions (Q)** — agent surfaces what it doesn't know via targeted technical questions
   touching all relevant codebase areas. Artifact: a question list (brief: `questions.md`).
2. **Research (R)** — agent gathers objective codebase facts **with the feature ticket
   hidden**. Artifact: a factual technical map — no recommendations, no plan.
3. **Design Discussion (D)** — agent "brain dumps" ~200 lines covering current state, desired
   end state, and design decisions; engineer performs "brain surgery" to redirect architecture.
4. **Structure Outline (S)** — signatures, new types, high-level phases ("compared to a C
   header file"); enforces vertical slices (mock API → front-end → database with checkpoints).
5. **Plan (P)** — tactical implementation doc constrained by the prior design + structure.

Execution:
6. **Work Tree** — tasks organized into a hierarchy based on vertical slices.
7. **Implement (I)** — code writing (brief specifies strict Red-Green-Refactor TDD per slice).
8. **Pull Request (PR)** — human code review; engineers read and own the code.

**Brief vs. source labeling:** the task brief collapses this into a 5-letter user-facing model
**Q-R-S-P-I**, where its "**S (Spec)**" = the blog's Design Discussion + Structure Outline
combined, and "**I (Implement)**" absorbs Work Tree + Implement + PR. See Open Question #9.

### 5.2 Three RPI failure modes that motivated QRSPI
1. **Instruction-budget overflow** — frontier LLMs "lose consistency after approximately
   150-200 instructions"; RPI's prompt had "85+ instructions," so the deepest alignment steps
   were silently skipped.
2. **Magic-words dependency** — correct behavior required specific trigger phrases (e.g.,
   "Work back and forth with me…"); without them the agent skipped Design Discussion.
3. **Plan-reading illusion** — "Plans that read well don't necessarily build well"; persuasive
   prose masked wrong technical assumptions.

### 5.3 Quantitative constraints (verbatim where quoted)
- Context window: "Keep context window utilization under 40%. At 60%, start a fresh session."
- Instruction budget: ~"150-200 instructions" maximum before consistency loss.
- Vertical slices (mock API → front-end → database, with checkpoints) preferred over
  horizontal layers that complete all work by category.
- **Sub-agents** are "context boundaries" using cheaper models for scoped tasks — **not**
  character personas. (This is exactly the pattern RPI's read-only subagents already use;
  Section 2.2.)

### 5.4 Composing primitives (from the brief)
- **Red-Green-Refactor TDD** (Matt Pocock's agentic TDD): failing test first → minimal code to
  pass → refactor; forces every increment through an executable verifier. Composes into Plan
  (test plan) and Implement.
- **Vertical slices** (Matt Pocock): small end-to-end increments through all layers, creating
  natural verification checkpoints and mapping cleanly to fresh-context sessions per slice.

---

## Key findings (summary)

1. Skills live under `skills/team/` and `skills/personal/`, **not** `skills/<name>/` —
   AGENTS.md is stale on this (Section 1.1, flagged not resolved).
2. RPI already implements QRSPI's "sub-agents as context firewalls" pattern via 5 dual-platform
   agents in `claude/agents/team/` (rpi-planner + 3 read-only locators/analyzers + implement).
3. RPI ships **no `/slash` commands**; invocation is via skill `description` triggers and the
   rpi-planner agent. "/rpi-research" exists only as natural-language trigger text.
4. Vendored (Matt Pocock) skills are kept flat beside first-party skills with 3-layer
   attribution (frontmatter keys + description URL + `.matt-pocock-attribution.yml`).
5. The QRSPI thesis (instruction budget < ~150) is in tension with AGENTS.md's mandatory
   10-section full-template — the Plan phase must reconcile this (Open Question #6).

## Open questions needing human input (highest-leverage)

- #1 skill layout (flat vs nested) — affects tooling compatibility.
- #6 10-section template vs. instruction budget — a genuine convention-vs-thesis conflict.
- #8 RPI coexistence vs. deprecation — affects scope and shared-agent naming.

**Next step:** review this artifact, then start a NEW session and run the Plan phase.
