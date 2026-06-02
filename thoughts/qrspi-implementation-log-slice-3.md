---
date: 2026-06-02T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 3 — qrspi-spec (Design Brain-Dump + Structure Outline)"
tags: [qrspi, implement, slice-3, spec, brain-surgery, vertical-slice]
git_commit: a12cd4f
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 3
branch: qrspi-slice-3-spec
status: complete
---

# QRSPI Implementation Log — Slice 3: `qrspi-spec`

Implements Slice 3 from `thoughts/qrspi-plan.md` §6. Adds the Spec phase: a Design Brain-Dump the
human redirects ("brain surgery"), then a vertically-sliced Structure Outline — so the full
Q→R→S alignment chain works end-to-end.

## What this slice is (per plan §6, Slice 3, re-read in full)

> - Write SKILL.md (+ spec-template, stage-mapping references), extend `qrspi-orchestrator`
>   `skills:` to include it. Implements the brain-surgery loop (§4.2) and slice-structured outline.
> - Checkpoint: `/qrspi-spec` consumes `research.md`, produces an approved `spec.md` via the
>   human loop. Q→R→S works.

## What was done

### 1. `qrspi-spec` skill (minimal tier)
- `skills/team/qrspi-spec/SKILL.md` — **92 lines**, ≤ ~40 directives, self-sufficient when invoked
  directly. Frontmatter shape matches `qrspi-research/SKILL.md:1-9` (`name`, `audience: team`,
  `description: >` with `/qrspi-spec` usage + natural triggers + negatives for `to-prd`,
  `spec-coach`, and the deprecated RPI workflow — plan §5 disambiguation).
- **Brain-surgery loop (plan §4.2)** encoded as the `STOP & LOOP` workflow step and the
  `design_approved: true|false` state field: write the Brain-Dump, STOP, present, loop on human
  redirection, write the Structure Outline only after approval. Modeled on `rpi-plan`'s DESIGN
  gate ("Present… and WAIT for approval", `rpi-plan/SKILL.md:56`).
- **Vertical-slice structure (plan §4.3)** stated in constraint 3 and the `STRUCTURE OUTLINE`
  step (mock-API → front-end → database, a checkpoint per slice; signatures not bodies).
- 40/60 context-budget rule + `context_budget` state field (plan §4.5).
- Unique state tag `<qrspi-spec-state>` (verified appears only in this file).

### 2. TWO reference files (plan §2)
- `references/spec-template.md` — the two-movement `spec.md` structure + frontmatter with the
  `design_approved` and `status: draft|ready-for-review|approved` lifecycle (plan #10).
- `references/stage-mapping.md` — the canonical 8-stage-source → 5-phase-QRSPI table (plan #9),
  documenting that `qrspi-spec` owns source stages 3 (Design Discussion) + 4 (Structure Outline).

### 3. Extended `qrspi-orchestrator` (both platforms, parity preserved)
- Claude: added `qrspi-spec` to the `skills:` array; OpenCode: added the `skill({ name:
  "qrspi-spec" })` row to the Available Skills table (OpenCode has no `skills:` frontmatter).
- Both: added a **SPEC Phase** to the Autonomous Protocol; added a "Before writing the Structure
  Outline" self-check; wired the SEQUENCE CHECK live (`SPEC -> requires research.md (status:
  complete) -> writes spec.md`); added a SPEC Completion Criterion; added `design_approved` to both
  state blocks and `SPEC` to the phase/Mode enums; flipped the "Spec comes online later" note so
  only Plan + Implement remain marked as later-slice.

### 4. Command pair (flat, paired)
- `claude/commands/qrspi-spec.md` — `!`-injected `<live_state>` (today + `ls` of feature folders),
  routes to `qrspi-orchestrator`, encodes the STOP-before-Structure-Outline gate.
- `opencode/commands/qrspi-spec.md` — `agent: qrspi-orchestrator`, `subtask: true` (per plan §3;
  see Deliberate choices below).

## Verification (all green)

| Check | Result |
| --- | --- |
| skills count | 83 → **84** (+qrspi-spec) |
| claude agents | **36** (no new agent — qrspi-spec runs under the orchestrator) |
| opencode agents | **36** |
| agent parity | 36 == 36 ✅ |
| claude commands | 12 → **13** |
| opencode commands | 12 → **13** |
| command parity | 13 == 13 ✅ |
| minimal-tier lines | qrspi-spec 92 (≤100) ✅ |
| ≥2 references | spec-template.md + stage-mapping.md ✅ |
| frontmatter `name:` == dir | ✅ |
| unique state tag | `<qrspi-spec-state>` appears only in its own skill ✅ |
| `add_frontmatter.py` | "0 files updated" — new skill already conforms ✅ |
| orchestrator SPEC wiring | SPEC Phase + self-check + live SEQUENCE CHECK present on both platforms ✅ |
| no stale "(later slice)" on SPEC | clean on both platforms ✅ |

## Eval status (TDD / eval discipline)

No executable trigger-eval harness exists in-repo yet (plan §5 defers eval authoring). Eval spec
recorded as a checklist for a later eval-harness session.

### `qrspi-spec` trigger evals (plan §5)
- [ ] MUST activate: "/qrspi-spec X", "design discussion for X", "structure outline for X",
      "spec out X from the research"
- [ ] MUST NOT activate: "write a PRD" (→ `to-prd`), open-ended design chat (→ `spec-coach`),
      "/rpi-plan X" (→ deprecated `rpi-plan`)
- [ ] Disambiguation: routes here for QRSPI's gated brain-dump→outline; not `spec-coach` (free
      conversation), not `to-prd` (product doc), not `rpi-plan` (folds design into planning)

### Behavior evals (the brain-surgery gate)
- [ ] Spec requested with no `research.md` present → STOPS and routes to `/qrspi-research`
- [ ] Structure Outline is never written while `design_approved: false`
- [ ] A horizontal-layer slice plan is re-sliced before `status: ready-for-review`

## Deliberate plan-driven choices worth noting at review

1. **OpenCode `subtask: true` for spec** despite spec writing `spec.md` AND running an interactive
   brain-surgery loop. Plan §3 explicitly classifies the alignment phases (questions/research/spec/
   plan) as read-heavy `subtask:true`; only `implement` is `subtask:false`. Followed the plan over
   CLAUDE.md's "writes files → subtask:false" heuristic, consistent with the Slice 2 decision.
   **Flag for review:** spec's human-in-the-loop redirection is more interactive than the other
   alignment phases — if OpenCode subtask isolation hampers the in-session approval loop, switch
   this one command to `subtask: false`. Behavior is identical on Claude Code either way.
2. **No new agent.** `qrspi-spec` runs under the existing `qrspi-orchestrator` (extended in place,
   per the Slice 2 handoff), so agent counts stay 36/36. The Implement agent (`qrspi-implement`)
   is the only new agent the suite adds, in Slice 5.
3. **Planning artifacts left untracked** — `thoughts/qrspi-plan.md` / `qrspi-research.md` remain
   unstaged (not Slice 3 work), consistent with Slices 1–2.

## Handoff to Slice 4 (`qrspi-plan`)

**What was done:** `qrspi-spec` skill (+ spec-template, stage-mapping); orchestrator extended for
SPEC on both platforms; `qrspi-spec` command pair. Counts 84 / 36 / 36 / 13 / 13.

**What tests pass:** all structural/parity/minimal-tier checks above; `add_frontmatter` 0-updates;
orchestrator SPEC wiring on both platforms. Trigger/behavior evals written as checklists (no harness).

**What's deferred:** README/AGENTS.md/docs bookkeeping and the RPI DEPRECATED markers → **Slice 6**
(do not interleave). README/AGENTS.md badges are NOT yet updated; interim reality after Slice 3 is
84 / 36 / 36 / 13 / 13. Slice 6 reconciles the build-end totals 81→86 / 35→37 / 10→15.

**What Slice 4 needs to know:**
1. **Extend the orchestrator again, don't rebuild it.** Add `qrspi-plan` to the Claude `skills:`
   array and the OpenCode Available Skills table; add a PLAN section to the Autonomous Protocol;
   flip the PLAN line in the SEQUENCE CHECK from "(later slice)" to live
   (`PLAN -> requires spec.md (status: approved) -> writes plan.md`); add a PLAN completion
   criterion; add `PLAN` to the phase/Mode enums. (Same pattern this slice used for SPEC.)
2. **`qrspi-plan` is minimal tier** (≤100 lines, ≤~40 directives, ≥1 reference: `plan-template.md`).
3. **Horizontal-layer refusal gate (plan §4.3):** a PRE-WRITE checklist that STOPS and re-slices if
   phases are organized by technical layer; mirror `rpi-plan`'s YAGNI gate that blocks WRITE.
4. **Sets `status: ready-for-review`** on `plan.md`; consumes `spec.md` and refuses without it.
5. **Artifact:** `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/plan.md`; unique tag `<qrspi-plan-state>`.
6. **Branch from this slice's branch** (`qrspi-slice-3-spec`) if Slice 4 needs the SPEC-aware
   orchestrator present, and note it — same reasoning the Slice 2 handoff gave for Slice 3.

**Branch:** `qrspi-slice-3-spec` (committed, not pushed, no PR — local review first).
