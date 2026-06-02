---
date: 2026-06-01T00:00:00
repository: ai-toolkit
topic: "QRSPI workflow — implementation plan (RPI Plan phase)"
tags: [plan, qrspi, rpi, skills, agents, commands, workflow]
git_commit: 7044b767229a8f80da640e34a98a04900a7576e0
research_artifact: thoughts/qrspi-research.md
status: Approved
phase: Plan (P)
---

# Plan: Adding a QRSPI Workflow to ai-toolkit

Converts `thoughts/qrspi-research.md` into a phased, vertically-sliced implementation plan.
Every architectural claim cites the research artifact by section (e.g. _R§2.2_) or a verified
file. This plan does **not** write skill files — that is the Implement phase.

**Three research facts I re-verified against the filesystem and corrected** (the research
artifact was partly stale here): OpenCode agents are **not** flat — they live under
`opencode/agents/{team,personal}/` exactly like Claude's, and all 5 rpi-\* agents already exist
there (corrects R§2.2). Both platforms sit at **35 agents** (parity confirmed). Commands are
flat at **10/10**. Skills total **81** (`find skills -name SKILL.md | wc -l`).

---

## Section 0 — Decision summary (all 11 open questions from R§4)

| #   | Question                       | Decision                                                                                             | Type                            |
| --- | ------------------------------ | ---------------------------------------------------------------------------------------------------- | ------------------------------- |
| 1   | Skill layout flat vs nested    | **Parallel-flat** `skills/team/qrspi-*/`                                                             | Decided (tooling)               |
| 2   | Shared-primitive placement     | **Reference existing `tdd` + `*-feature-slice`; vendor 0 new**                                       | Decided (was [DECISION NEEDED]) |
| 3   | Per-phase sub-agents           | **2 new agents** (qrspi-orchestrator, qrspi-implement); reuse 3 rpi read-only subagents              | Decided                         |
| 4   | Command surface                | **5 named commands** `/qrspi-questions … /qrspi-implement`                                           | Decided                         |
| 5   | No-magic-words activation      | **Structural artifact-gates in skill content**                                                       | Decided                         |
| 6   | 10-section template vs budget  | **Minimal tier for all 5 phase skills**                                                              | Decided (was [DECISION NEEDED]) |
| 7   | rpi-iterate disposition        | **Stays RPI-only; QRSPI gets none**                                                                  | Decided                         |
| 8   | RPI coexistence vs deprecation | **QRSPI replaces RPI: deprecate now, rename subagents to `research-*`, remove all rpi-\* at sunset** | Decided                         |
| 9   | Spec-phase naming              | **`qrspi-spec` = Design Discussion + Structure Outline**                                             | Decided                         |
| 10  | Artifact paths                 | **Per-feature folder `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/`**                                    | Decided                         |
| 11  | Doc-drift Boy Scout            | **Fix only the AGENTS.md lines QRSPI touches**                                                       | Decided                         |

---

## Section 1 — Resolved decisions with reasoning

### #1 Skill layout — parallel-flat (decided)

`skills/team/qrspi-questions/`, `qrspi-research/`, `qrspi-spec/`, `qrspi-plan/`,
`qrspi-implement/`. _R§3.1_: `scripts/add_frontmatter.py:85` walks `skills/{team,personal}/*/`
**one level**, and `install-claude.sh` copies the tree by glob. Nested
`skills/team/qrspi/<phase>/` is a net-new structural pattern that the frontmatter script would
not reach and the install glob would not preserve correctly. Flat matches 100% of the 81
existing skills. No human input needed — this is a tooling-compatibility fact.

### #2 Shared primitives — **DECIDED: reference existing, vendor 0 new**

The brief lists "shared primitive skills (Red-Green-Refactor TDD, vertical slices)" as Slice 1.
Two verified facts make new primitives redundant:

1. **`tdd` already IS both primitives.** Its description (`skills/team/tdd/SKILL.md:4-10`):
   _"The canonical RED-GREEN-REFACTOR inner loop. Enforces behavioral, structure-insensitive
   tests and **prohibits horizontal slicing**. Use … as the inner loop for rpi-implement,
   spec-implement, **or any other implementation skill**."_ So `tdd` covers RGR _and_ the
   anti-horizontal-slice angle, and was purpose-built as the shared inner loop for other
   implementation skills — exactly QRSPI's Implement need. A new `red-green-refactor` skill
   would be ~100% duplication.
2. **The `*-feature-slice` skills are stack-specific scaffolders, not planning rules.** They
   _generate code_ (CQRS handlers, FastAPI routers, Axum service traits); none enforces
   "slice the _plan_ as mock-API → front-end → DB with checkpoints" (_R§5.3_). That gap is a
   **planning-discipline** gap, and its natural home is inside `qrspi-spec`/`qrspi-plan`
   (§4.3) — not a reusable primitive nothing else would call.

**Decision: reference, don't vendor.** `qrspi-implement` loads `tdd` as its inner loop
(agent `skills:[qrspi-implement, tdd]`, §4.4); `qrspi-spec`/`qrspi-plan` carry the
vertical-slice gate in their own content (§4.3); all five skills cross-link `tdd` and the
`*-feature-slice` skills via Integration sections. Zero new skills, zero attribution-ledger
churn. Honors DRY and the repo's "Companion Skills" non-overlap doctrine (README:124), which is
a logged design principle — duplicating `tdd` would be the single largest convention violation
in this plan.

**Rejected — vendor new Pocock primitives.** Besides duplicating `tdd`, the repo's attribution
convention (_R§1.5_) requires a **traceable `upstream_path`** in `.matt-pocock-attribution.yml`,
but _R§5.4_ attributes the _concept_ to Pocock, not a named upstream skill file — so attribution
would be aspirational, not traceable. The brief's Slice-1 framing predated knowing `tdd` already
fills both roles; in the same repo as `tdd`, a self-contained QRSPI "island" buys nothing.

**Slice 1 consequence:** no new files — Slice 1 becomes a no-op confirmation step (§6).

### #3 Per-phase sub-agents — 2 new + 3 reused (decided)

_R§2.2_ establishes the "sub-agents as context firewalls" precedent (5 rpi agents). QRSPI maps
on directly without duplicating the read-only workhorses:

- **`qrspi-orchestrator`** (new, paired) — drives Q→R→S→P, cannot edit source (mirrors
  `rpi-planner.md:4` `tools: Read, Glob, Grep, Bash, Write`; OpenCode `edit: false`).
- **`qrspi-implement`** (new, paired) — execution agent with edit access (mirrors
  `rpi-implement.md`), enforces Red-Green-Refactor per slice.
- **Reuse the 3 read-only subagents** — renamed to `research-file-locator`,
  `research-code-analyzer`, `research-pattern-finder` per #8 — for the Research phase. They take
  a _topic string_ and are workflow-neutral (`rpi-file-locator.md:39` "Parse the research topic
  from the task prompt"). Reusing them is what makes ticket-hiding free (see §4.1) and avoids 6
  redundant files. Behavior unchanged — only the rpi-\* branding is dropped.
- **`model:` field:** keep `model: inherit` (repo convention, `rpi-planner.md:5`). QRSPI's
  "cheaper models for scoped tasks" intent (_R§5.3_) is satisfied _structurally_ by scope
  isolation; a per-agent model pin can be a follow-up and is not required for v1.

Net: **+2 agents per platform → 37/37**. Bump parity counts (AGENTS.md:94, README:8).

### #4 Command surface — 5 named commands (decided)

_R§3.4_: RPI ships zero commands, but the brief explicitly requests slash commands, and
failure-mode #2 (_R§5.2_) argues _against_ memorized phrases. A single `/qrspi <phase>`
dispatcher reintroduces a remembered argument; five 1:1-named commands are maximally
discoverable. Add `/qrspi-questions`, `/qrspi-research`, `/qrspi-spec`, `/qrspi-plan`,
`/qrspi-implement` — paired `claude/commands/` + `opencode/commands/` (flat, _R§2.3_).
Each is a thin shell-injection wrapper that prints current state (e.g. `ls` of the feature
folder) and routes to the matching skill/agent. **+5 commands per platform → 15/15** (AGENTS.md:95).

### #5 No-magic-words activation — structural gates (decided)

Correct behavior is the default through three content-level mechanisms, none requiring an
incantation (_R§4.5_):

1. **Rich `description` triggers** — each skill lists multiple natural-language phrases _and_
   the command name, exactly like `rpi-research/SKILL.md:4-7`.
2. **Artifact pre-flight gates in skill content** — each phase skill's Workflow opens with a
   PRE-FLIGHT that checks the feature folder for the prior artifact and **refuses** to proceed
   if absent. This is the existing `rpi-plan` pattern: "If no research artifact exists, stop"
   (`rpi-plan/SKILL.md:50,102`). Spec is unskippable because `qrspi-plan` reads `spec.md` and
   stops without it.
3. **Orchestrator owns ordering** — `qrspi-orchestrator` carries the phase sequence; it never
   advances a phase whose input artifact is missing. Sequencing lives in skill+agent content,
   not in `disable-model-invocation` (which only controls auto-firing, AGENTS.md:135).

### #6 10-section template vs instruction budget — **DECIDED: minimal tier, all 5**

This is the genuine convention-vs-thesis conflict (_R§4.6_, _R§5.2_ failure-mode #1). The four
rpi-\* skills are 197–388 lines; QRSPI exists because prompts past ~150–200 instructions degrade.

**Decision driver: token cost + the move to local models.** Both push the same way, harder
than line-count aesthetics:

- The ~150–200-instruction ceiling is a _frontier-model_ figure; smaller local models (the
  repo already targets Ollama via `pi/global/`, README:22) degrade sooner and have smaller
  context windows. A budget design is what lets QRSPI run at all on an 8B–14B local model.
- Every section is an **always-on token tax paid per invocation**. A 388-line skill is a fixed
  cost every run; minimal skills + just-in-time `references/` loading pay for the template only
  at WRITE time.

**Decision: minimal tier for all five phase skills**, with two guardrails that make it honest
(the minimal tier was blessed for "single-instruction skills", AGENTS.md:143 — QRSPI phase
skills are slightly more, so we name limits rather than lean on a loophole):

1. **Instruction ceiling** — the thesis counts instructions, not lines: **≤ ~40 imperative
   directives per phase skill**, well under 150–200 even when orchestrator + skill + one
   reference co-load, and far below the 85+ that broke RPI (_R§5.2_).
2. **References-offload, not orchestrator-dependence** — overflow (output templates,
   anti-patterns, adapter notes, error-recovery detail) goes to `references/` loaded
   just-in-time. Each skill stays **self-sufficient when invoked directly** (local models are
   weak at multi-agent orchestration, so skills must not depend on `qrspi-orchestrator` to
   supply their per-phase logic). The orchestrator handles only cross-phase _sequencing_.

**Rejected — full 10-section template** (match rpi-*): reproduces the exact instruction bloat
QRSPI was created to fix; self-defeating, and worst on local models.
**Rejected — split (qrspi-implement full, rest minimal):** under a budget priority this is
backwards — `qrspi-implement` is the heaviest *and\* most-invoked phase, so full-template there
maximizes cost on the hot path.

**Governance:** Slice 6 logs an AGENTS.md Persistent Decision broadening the minimal-tier
definition to include "thin, self-sufficient workflow-phase drivers (≤ ~40 directives)", so the
next contributor reads QRSPI as convention-conformant, not a violation.

### #7 rpi-iterate — no QRSPI equivalent (decided)

_R§4.7_: QRSPI's 8-stage source has no iterate stage; revision happens at the Spec
"brain-surgery" gate (§4.2) or by re-running a phase. Graduating `rpi-iterate` to shared
infra is speculative (YAGNI). If QRSPI implementation hits a plan gap, the user edits
`spec.md`/`plan.md` and re-runs `/qrspi-plan`. No `qrspi-iterate` skill. (`rpi-iterate` itself
rides the deprecated RPI suite per #8.)

### #8 RPI coexistence — **DECIDED: QRSPI replaces RPI (deprecate now, remove at sunset)**

_R§4.8_: QRSPI is Horthy's replacement for RPI, motivated by RPI _delivering poor results_ (the
three failure modes, _R§5.2_). Owner decision: **QRSPI fully replaces RPI — no rpi-\* files left
around** after the transition. Coexistence is rejected (leaves the poor-outcome path
discoverable); indefinite deprecation is rejected (leaves odd files behind).

**Two-step transition (owner-confirmed):**

1. **Now (this build) — deprecate the workflow + rename the shared subagents.**
   - The 4 rpi-\* skills (`rpi-research`, `rpi-plan`, `rpi-implement`, `rpi-iterate`) and the
     `rpi-planner`/`rpi-implement` agents get `disable-model-invocation: true` (skills,
     AGENTS.md:135 semantics) + a `**DEPRECATED — use QRSPI instead**` description prefix. They
     keep functioning for explicit opt-in during the window.
   - The 3 read-only subagents are **renamed to neutral names** so no rpi-* branding survives:
     `rpi-file-locator → research-file-locator`, `rpi-code-analyzer → research-code-analyzer`,
     `rpi-pattern-finder → research-pattern-finder` (6 files, paired; state-block tags renamed
     too). They are workflow-neutral (`rpi-file-locator.md:39` parses a topic string) — *not*
     the poor-outcome part. QRSPI references the neutral names natively; the deprecated
     `rpi-research`/`rpi-planner` are **repointed** to the neutral names so RPI still works
     during the window. *(Exact neutral names are adjustable — see Open items.)\*

2. **Sunset (~2026-09-01, +90 days) — remove all rpi-\* files.** Delete the 4 rpi-_ skill dirs
   and the `rpi-planner`/`rpi-implement` agent pairs. End state: \*\*zero rpi-_ files\*_; the
   renamed `research-_` subagents + the qrspi-\* suite are all that remain (Slice 7).

**Knock-on:** #7 stands — no `qrspi-iterate`; `rpi-iterate` is removed at sunset. #3's subagent
reuse now targets the renamed `research-*` agents.

### #9 Spec-phase naming — combined `qrspi-spec` (decided)

_R§4.9 / R§5.1_: canonical user-facing model is **Q-R-S-P-I**. `qrspi-spec` owns the blog's
stage 3 (Design Discussion) **and** stage 4 (Structure Outline) as two internal movements:
"Design Brain-Dump" then "Structure Outline". `qrspi-implement` absorbs stages 6–8 (Work Tree,
Implement, PR). The 8→5 mapping table is documented inside `qrspi-spec/SKILL.md` and AGENTS.md
so the source and implementation can't drift.

### #10 Artifact paths — per-feature folder (decided)

_R§4.10 / R§1.6_: RPI scatters 2 artifact types across `research/` and `plans/`. QRSPI has
**five** tightly-coupled artifacts per feature, so co-locate them:

```
thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/
  questions.md            # Q — open technical questions (human answers inline)
  research.md             # R — objective, ticket-hidden codebase map
  spec.md                 # S — design brain-dump + structure outline; status: lifecycle
  plan.md                 # P — vertically-sliced tactical plan; status: approved gate
  implementation/
    slice-01-{name}.md     # I — per-slice log (RGR record + verification output)
    slice-02-{name}.md
```

Frontmatter reuses the research convention (`date, repository, topic, tags, git_commit,
status`, _R§1.6_) plus `phase:` and `qrspi_feature:` (the slug). `spec.md` and `plan.md` add a
lifecycle `status:` (`draft | ready-for-review | approved`) mirroring `rpi-plan` (the approved
gate blocks `qrspi-implement`, like `rpi-implement.md:22`). This is a new path pattern → log it
in AGENTS.md Persistent Decisions (Slice 6).

### #11 Doc-drift — targeted Boy Scout fix (decided)

_R§4.11_: AGENTS.md:126 (`skills/<name>/`) and :62/:187 (`skills/architecture-review/…`) are
stale vs the `skills/team|personal/` reality, and `audience:` is undocumented (_R§1.1_). Fix
**only** these lines during Slice 6 (they sit next to QRSPI's own AGENTS.md edits) and document
`audience:`. Do not propagate the stale path into any new QRSPI doc. Keep the diff reviewable —
no broad AGENTS.md rewrite.

---

## Section 2 — Exact file layout

**Skills** (5, `skills/team/`, each `SKILL.md` + `references/`):

```
skills/team/qrspi-questions/SKILL.md     + references/questions-template.md
skills/team/qrspi-research/SKILL.md      + references/research-template.md
skills/team/qrspi-spec/SKILL.md          + references/spec-template.md, stage-mapping.md
skills/team/qrspi-plan/SKILL.md          + references/plan-template.md
skills/team/qrspi-implement/SKILL.md     + references/slice-log-template.md
```

**Agents** (2 new, paired — supports #3):

```
claude/agents/team/qrspi-orchestrator.md      opencode/agents/team/qrspi-orchestrator.md
claude/agents/team/qrspi-implement.md         opencode/agents/team/qrspi-implement.md
```

**Commands** (5, paired, flat — supports #4):

```
claude/commands/qrspi-questions.md   …  qrspi-implement.md   (5 files)
opencode/commands/qrspi-questions.md …  qrspi-implement.md   (5 files)
```

**Renamed → shared infra (#8, Slice 2):** `rpi-file-locator → research-file-locator`,
`rpi-code-analyzer → research-code-analyzer`, `rpi-pattern-finder → research-pattern-finder`
(`{claude,opencode}/agents/team/`, paired = 6 files; behavior unchanged, state-tags renamed).
**Deprecated then removed (#8):** the 4 rpi-\* skills + `rpi-planner`/`rpi-implement` agent
pairs — markers in Slice 6, deleted in Slice 7 (sunset).
**Docs touched (Slice 6):** `AGENTS.md`, `README.md`. `.matt-pocock-attribution.yml` unchanged
(#2 = vendor 0 new).

---

## Section 3 — Per-skill frontmatter + section outline

All five use **minimal tier** (per #6, decided): each ≤ ~100 lines / **≤ ~40 imperative
directives**, self-sufficient when invoked directly, overflow pushed to `references/` loaded
just-in-time. Frontmatter shape matches `rpi-research/SKILL.md:1-8`:

```yaml
---
name: qrspi-<phase>
audience: team
description: >
  QRSPI <Phase> phase -- <one-line>. Use for "/qrspi-<phase> <feature>",
  "<natural trigger 1>", "<natural trigger 2>". Do NOT use when <negative trigger>.
---
```

Minimal-tier section outline (lean; overflow → `references/`):

1. **Title + epigraph** (1 quote, "Adapted from…" voice, _R§1.3_)
2. **Core Philosophy** — phase non-negotiables, the **context-budget rule** (§4.5), and the
   **pre-flight artifact gate** (§4 / #5)
3. **Workflow** — PRE-FLIGHT → phase steps → exit criteria
4. **State Block** — unique XML tag (below)
5. **Output template** — pointer to `references/<phase>-template.md`
6. **Integration** — links to neighbor phases + (per #2) `tdd` / `*-feature-slice`

Per-skill specifics (artifact + unique state tag + the one thing each enforces):

| Skill             | Artifact produced              | State tag                 | Phase-specific gate                                                                                       |
| ----------------- | ------------------------------ | ------------------------- | --------------------------------------------------------------------------------------------------------- |
| `qrspi-questions` | `questions.md`                 | `<qrspi-questions-state>` | Surfaces unknowns across all relevant areas; STOPS for human answers before R (_R§5.1_)                   |
| `qrspi-research`  | `research.md`                  | `<qrspi-research-state>`  | **Ticket-hidden** (§4.1); spawns 3 rpi subagents in parallel; objective-only (`rpi-research/SKILL.md:24`) |
| `qrspi-spec`      | `spec.md`                      | `<qrspi-spec-state>`      | **Brain-surgery loop** (§4.2) + **vertical-slice structure** (§4.3)                                       |
| `qrspi-plan`      | `plan.md`                      | `<qrspi-plan-state>`      | **Refuses horizontal-layer plans** (§4.3); sets `status: ready-for-review`                                |
| `qrspi-implement` | `implementation/slice-NN-*.md` | `<qrspi-implement-state>` | **Red-Green-Refactor gate** per slice (§4.4); requires `plan.md` `status: approved`                       |

**Agents.** `qrspi-orchestrator` and `qrspi-implement` follow the **full 10-section agent
template** (AGENTS.md:231-243) — agents are personas loaded once, so the cross-phase
_sequencing_ (orchestrator) and _execution-loop_ (implement) weight lives here; each phase
skill still carries its own per-phase logic self-sufficiently (#6). Claude
frontmatter: `name, description, tools, model: inherit, skills:[...]`; OpenCode: `description,
mode, boolean tools, task: true`, with `skill({ name })` calls in the body (AGENTS.md:199-229,
matches `opencode/agents/team/rpi-planner.md`). `qrspi-orchestrator` `skills:` =
`[qrspi-questions, qrspi-research, qrspi-spec, qrspi-plan]`, `edit:false`. `qrspi-implement`
`skills:` = `[qrspi-implement, tdd]`, `edit:true`. Unique state tags
`<qrspi-orchestrator-state>`, `<qrspi-implement-agent-state>` (AGENTS.md:251 uniqueness rule).

**Commands.** Claude format (CLAUDE.md "When Adding a Command"): `description` with trigger +
`/qrspi-<phase> <feature>` usage, `allowed-tools`, a `!`-injected `<live_state>` block (e.g.
`!ls thoughts/shared/qrspi/`), then route to the skill/agent. OpenCode adds `agent:`,
`subtask:` — `subtask:true` for questions/research/spec/plan (read-heavy), `subtask:false` for
implement (writes files), per CLAUDE.md guidance.

---

## Section 4 — Default-behavior enforcement (no magic words)

### 4.1 Ticket-hidden Research (mechanism)

The orchestrator derives a **neutral topic string** from `questions.md`/the ticket and passes
**only that string** to the three renamed `research-*` read-only subagents via the Task tool
(pattern inherited from `rpi-research/SKILL.md:77-82`). The subagents' tools are `Read, Glob,
Grep` (`rpi-file-locator.md:4`, renamed per #8) — they never receive the ticket. `qrspi-research/SKILL.md` Core
Philosophy states the rule explicitly: _"Do not load the ticket or feature description into
context. Research what EXISTS, not what the feature wants."_ `research.md` is written
objective-only (no recommendations), inheriting `rpi-research` constraint #1
(`rpi-research/SKILL.md:24`). The firewall is structural: a sanitized prompt + read-only tools,
not a remembered phrase.

### 4.2 Brain-surgery alignment loop in Spec (built into the skill)

`qrspi-spec/SKILL.md` Workflow encodes a hard human gate, modeled on `rpi-plan`'s DESIGN step
("Present… and WAIT for approval", `rpi-plan/SKILL.md:56`):

1. Write the ~200-line **Design Brain-Dump** (current state / desired end state / design
   decisions, _R§5.1_ stage 3).
2. **STOP.** Present it; do **not** write the Structure Outline yet.
3. Loop: human redirects architecture → agent revises brain-dump → re-present → repeat until
   the human approves.
4. Only then write the Structure Outline (stage 4).
   The loop is triggered by skill _content_ (a blocking step + a State-Block flag
   `design_approved: true|false`), not a phrase.

### 4.3 Vertical-slice enforcement in Spec/Plan (Plan refuses horizontal)

- **Spec:** the Structure Outline section instructs slices as mock-API → front-end → database
  with checkpoints (_R§5.3 / R§5.4_).
- **Plan:** `qrspi-plan/SKILL.md` PRE-WRITE checklist contains a refusal gate (an anti-pattern
  the skill must self-check): _"If phases are organized by technical layer (all models, then
  all services, then all UI), STOP and re-slice. Each phase must deliver an end-to-end
  testable increment."_ This mirrors `rpi-plan`'s YAGNI gate that blocks WRITE
  (`rpi-plan/SKILL.md:60-65`). A horizontal plan never reaches the WRITE step.

### 4.4 Red-Green-Refactor in Implement (test-first gate)

`qrspi-implement/SKILL.md` SLICE LOOP (one slice = ideally one fresh session, §4.5):

1. Write the failing test.
2. **RUN it — must FAIL (RED).** If it passes, the test is wrong → fix the test, not the code.
3. Write minimal production code.
4. **RUN — build + test must PASS (GREEN).**
5. Refactor.
6. **RUN — must stay GREEN.**
7. Record RED/GREEN command output in `implementation/slice-NN-*.md`.
   Production code before a failing test is a STOP condition (anti-pattern row). Delegates detail
   to the `tdd` skill via Integration (per #2-A). The build/test-between-RED-and-GREEN requirement
   is structural — a command runs at every numbered step.

### 4.5 40%/60% context budget (checkpoint-to-disk)

Every QRSPI skill carries a CONTEXT BUDGET rule in Core Philosophy and a `context_budget`
field in its State Block: _"Keep context utilization under 40%. At 60%, write the current
artifact (and progress) to the feature folder and tell the user to start a fresh session"_
(_R§5.3_ verbatim constraint). The per-feature folder (#10) is what makes a fresh session
cheap — the next session reads the folder, not the transcript. `qrspi-implement` checkpoints
**per slice** (each `slice-NN-*.md` is a resumption point), extending `rpi-implement`'s 70%
progress-note pattern (`rpi-implement.md:42,46`) to the stricter 40/60 budget.

---

## Section 5 — Verification strategy (trigger evals)

Follow the existing **200-trigger-eval** pattern (per the brief; evals authored later, not in
this plan). For each new skill the eval set must cover:

| Skill             | MUST activate on                                                             | MUST NOT activate on                              | Disambiguation focus                                |
| ----------------- | ---------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------- |
| `qrspi-questions` | "/qrspi-questions X", "what don't we know about X", "surface unknowns for X" | "answer this question", generic Q&A               | vs `spec-coach` (interactive design), vs `grill-me` |
| `qrspi-research`  | "/qrspi-research X", "qrspi research X", "ticket-hidden research"            | "rpi research X", "/rpi-research X"               | vs `rpi-research` (same words, different workflow)  |
| `qrspi-spec`      | "/qrspi-spec", "design discussion for X", "structure outline for X"          | "write a PRD", "spec coach"                       | vs `spec-coach`, `to-prd`, `rpi-plan`               |
| `qrspi-plan`      | "/qrspi-plan X", "qrspi plan X"                                              | "/rpi-plan X", "plan the changes" (RPI)           | vs `rpi-plan` (highest collision risk)              |
| `qrspi-implement` | "/qrspi-implement plan.md", "execute the qrspi plan"                         | "/rpi-implement", "run tdd", "implement the plan" | vs `rpi-implement`, `tdd`, `tdd-agent`              |

The dominant risk is **QRSPI↔RPI word collision** — eval sets must include negative RPI
triggers for every QRSPI skill so the model routes to the right workflow when the user names it
(supports #8 coexistence). Cross-suite negatives (spec-coach, to-prd, tdd) prevent the new
skills from poaching existing triggers.

---

## Section 6 — Implementation sequence (vertical slices)

Eat our own dog food: each slice is an end-to-end increment ending at an independently usable
checkpoint. Slices respect dependency order (orchestrator/skills before commands that route to
them).

### Slice 1 — Primitives (no-op confirmation, per #2)

- No new files. Primitives are the **existing** `tdd` + `*-feature-slice` skills; they are
  referenced from the Integration sections written in Slices 4–5.
- Confirm the dependencies are present and loadable: `tdd` (`skills/team/tdd/SKILL.md`) and at
  least the `*-feature-slice` skills relevant to the target stack.
- **Checkpoint:** reused primitives confirmed present; no skill-count change.

### Slice 2 — `qrspi-questions` + `qrspi-research` (smallest viable QRSPI entry point)

- **Rename the 3 read-only subagents** (#8): `rpi-file-locator → research-file-locator`,
  `rpi-code-analyzer → research-code-analyzer`, `rpi-pattern-finder → research-pattern-finder`
  (6 paired files + state-tags). Repoint the deprecated `rpi-research`/`rpi-planner` to the new
  names so RPI keeps working during the window.
- Write both SKILL.md (+ references), the `qrspi-orchestrator` agent pair (drives Q→R, spawns
  the renamed `research-*` subagents), and both command pairs.
- **Checkpoint:** a user can run `/qrspi-questions` then `/qrspi-research` and get
  `questions.md` + a ticket-hidden `research.md` in a feature folder; deprecated `rpi-research`
  still resolves its (renamed) subagents. Q→R works without S/P/I.

### Slice 3 — `qrspi-spec`

- Write SKILL.md (+ spec-template, stage-mapping references), extend `qrspi-orchestrator`
  `skills:` to include it. Implements the brain-surgery loop (§4.2) and slice-structured outline.
- **Checkpoint:** `/qrspi-spec` consumes `research.md`, produces an approved `spec.md` via the
  human loop. Q→R→S works.

### Slice 4 — `qrspi-plan`

- Write SKILL.md (+ plan-template), extend orchestrator `skills:`. Implements the
  horizontal-layer refusal gate (§4.3), sets `status: ready-for-review`.
- **Checkpoint:** `/qrspi-plan` consumes `spec.md`, produces a vertically-sliced `plan.md` and
  refuses a horizontal plan. Q→R→S→P works.

### Slice 5 — `qrspi-implement`

- Write SKILL.md (+ slice-log-template), the `qrspi-implement` agent pair (edit access,
  `skills:[qrspi-implement, tdd]`). Implements the RGR gate (§4.4), `approved`-status guard,
  per-slice checkpointing (§4.5).
- **Checkpoint:** `/qrspi-implement` executes an approved `plan.md` slice-by-slice with RGR and
  writes slice logs. Full Q→R→S→P→I pipeline works end-to-end.

### Slice 6 — Bookkeeping, docs & RPI deprecation

- **Deprecate RPI (#8):** add `disable-model-invocation: true` + `**DEPRECATED — use QRSPI
instead**` description prefix to the 4 rpi-_ skills (`rpi-research`, `rpi-plan`,
  `rpi-implement`, `rpi-iterate`) and the `rpi-planner`/`rpi-implement` agents (both platforms,
  parity preserved). The 3 read-only subagents were renamed to `research-_` in Slice 2 (behavior
  unchanged); full rpi-\* removal happens at sunset (Slice 7).
- README: add a "QRSPI Workflow Suite" section (mirror the RPI suite, README:195-204); mark the
  RPI Workflow Suite **deprecated** with a pointer to QRSPI; bump skill/agent/command counts.
- AGENTS.md: add a "QRSPI Workflow" Skill-Suites row (AGENTS.md:271 sibling); mark the RPI row
  deprecated; update Open Loops counts (AGENTS.md:93-95: at build end skills 81→86 — 5 phase
  skills, no primitives per #2, deprecated RPI skills still on disk; agents 35→37; commands
  10→15. At sunset/Slice 7: skills 86→82, agents 37→35); add Persistent-Decisions rows for the
  per-feature artifact folder (#10), the chosen #2 resolution, **#6 — broaden the minimal-tier
  definition to include "thin, self-sufficient workflow-phase drivers (≤ ~40 directives)"**, and
  **#8 — QRSPI replaces RPI; deprecate now, remove rpi-\* at sunset 2026-09-01**; fix the two
  stale `skills/<name>/` paths and document `audience:` (#11).
- `.matt-pocock-attribution.yml`: no change (#2 = reference existing, vendor 0 new).
- **Checkpoint:** `find skills -name SKILL.md | wc -l` matches the README badge; agent/command
  parity counts match (`find {claude,opencode}/agents -name '*.md' | wc -l` → 37 each;
  commands → 15 each); every QRSPI skill has ≥1 reference file; the 4 rpi-\* skills no longer
  auto-invoke (`disable-model-invocation: true` present) and carry the DEPRECATED prefix; no
  `rpi-file-locator|rpi-code-analyzer|rpi-pattern-finder` files remain (renamed).

### Slice 7 — Sunset (scheduled ~2026-09-01, +90 days; separate from the initial build)

- Delete the 4 deprecated rpi-_ skill dirs and the `rpi-planner`/`rpi-implement` agent pairs
  (both platforms). Verify nothing references them: `grep -rl 'rpi-' --include='_.md' .` clean.
- Update counts (skills 86→82, agents 37→35); remove the deprecated RPI rows from README/AGENTS.md.
- **Checkpoint:** `find . -name 'rpi-*'` is empty; QRSPI + `research-*` subagents are the only
  workflow remaining. RPI fully replaced.

---

## Section 7 — Bookkeeping touchpoints (consolidated, _R§3.5_)

- README skill count badge (README:4) + counts line (README:8) + suite table.
- AGENTS.md Open Loops counts (:93-95), Skill Suites table (:271), Persistent Decisions (:75+).
- Agent parity 35→37 (AGENTS.md:94, README:8); command parity 10→15 (AGENTS.md:95).
- `.matt-pocock-attribution.yml` — only under #2 = B/C.
- Each new skill: ≥1 `references/` file (minimal-tier rule, AGENTS.md:143); unique State-Block
  XML tag (AGENTS.md:251).

---

## What this plan is NOT doing

- Not writing any skill, agent, or command file (that is Implement).
- Not creating a `qrspi-iterate` skill (#7).
- Not changing the _behavior_ of the 3 read-only subagents — they are renamed to `research-*`
  and repointed only (#3, #8); logic unchanged.
- Not removing rpi-\* files during the initial build (Slices 1–6) — removal is the scheduled
  sunset step (Slice 7, ~2026-09-01).
- Not introducing a `skills/primitives|vendor/` namespace (no precedent, _R§3.2_).
- Not a broad AGENTS.md rewrite — only the lines QRSPI touches (#11).

## All 11 questions resolved — Implement can proceed

_Resolved in conversation:_

- _#2 Shared primitives — reference existing `tdd`/`_-feature-slice`; vendor 0 new.\*
- _#6 Skill tier — minimal tier for all 5, self-sufficient, ≤ ~40 directives, references-offload._
- _#8 RPI stance — QRSPI replaces RPI: deprecate + rename subagents to `research-_` now;
  remove all rpi-_ at sunset (~2026-09-01, owner-confirmed 90-day window)._

**One cosmetic item, non-blocking:** the neutral subagent names (`research-file-locator`,
`research-code-analyzer`, `research-pattern-finder`) are a proposal — adjust if you prefer
another convention (e.g. `codebase-*`).

This plan is `status: ready-for-review` with **all 11 questions resolved**. Review it, then start
a NEW session and run Implement: Slices 1→6 are the build; **Slice 7 fires at sunset (~2026-09-01)**.
