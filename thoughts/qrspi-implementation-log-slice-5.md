---
date: 2026-06-02T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 5 — qrspi-implement (per-slice Red-Green-Refactor execution)"
tags: [qrspi, implement, slice-5, rgr, tdd, vertical-slice, checkpoint]
git_commit: 1e1c31f
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 5
branch: qrspi-slice-3-spec
status: complete
---

# QRSPI Implementation Log — Slice 5: `qrspi-implement`

Implements Slice 5 from `thoughts/qrspi-plan.md` §6. Adds the Implement phase: a dedicated execution
agent that consumes an **approved** `plan.md` and runs each vertical slice through strict
Red-Green-Refactor, checkpointing to a per-slice proof log. This closes the full **Q→R→S→P→I**
pipeline end-to-end.

## What this slice is (per plan §6, Slice 5, re-read in full)

> - Write SKILL.md (+ slice-log-template), the `qrspi-implement` agent pair (edit access,
>   `skills:[qrspi-implement, tdd]`). Implements the RGR gate (§4.4), `approved`-status guard,
>   per-slice checkpointing (§4.5).
> - Checkpoint: `/qrspi-implement` executes an approved `plan.md` slice-by-slice with RGR and
>   writes slice logs. Full Q→R→S→P→I pipeline works end-to-end.

## What was done

### 1. `qrspi-implement` skill (minimal tier)
- `skills/team/qrspi-implement/SKILL.md` — **92 lines**, ≤ ~40 directives, self-sufficient when
  invoked directly. Frontmatter matches the `qrspi-*` shape (`name`, `audience: team`,
  `description: >` with `/qrspi-implement` usage + natural triggers + negatives for the deprecated
  `rpi-implement` and bare `tdd` — plan §5 disambiguation).
- **RGR-per-slice gate (plan §4.4)** as the `SLICE LOOP` workflow: RED (write failing test, RUN, must
  FAIL) → GREEN (minimal code, RUN build+test, must PASS) → REFACTOR (stays GREEN) → RECORD the RED +
  GREEN command output → CHECKPOINT. Constraint 4 makes production-code-before-a-failing-test a STOP.
- **approved-status guard** (constraint 1 + PRE-FLIGHT): refuses to run unless `plan.md` is
  `status: approved`; a `ready-for-review` plan STOPs.
- **Per-slice 40/60 context budget (plan §4.5)**: `context_budget` state field + checkpoint-per-slice
  rule (each `slice-NN-*.md` is a resumption point — stricter than `rpi-implement`'s 70%).
- Delegates RGR mechanics to the `tdd` skill via the Integration table (plan §2-A).
- Unique state tag `<qrspi-implement-state>` (verified appears only in this file).

### 2. ONE reference file (minimal-tier rule)
- `references/slice-log-template.md` — the per-slice `implementation/slice-NN-{name}.md` structure:
  frontmatter, RED proof block, GREEN proof block, files-changed list, resume note + authoring rules
  ("proof, not prose"; RED must actually be red; one slice per file; `status: complete` only after GREEN).

### 3. `qrspi-implement` agent pair (NEW agent — full 10-section template, plan §3)
- `claude/agents/team/qrspi-implement.md` — `tools: Read, Edit, Write, Bash, Glob, Grep` (edit
  access), `model: inherit`, `skills: [qrspi-implement, tdd]`. All 10 agent sections (Title+epigraph,
  Core Philosophy, Guardrails ×4, Autonomous Protocol, Self-Check Loops, Error Recovery, AI
  Discipline Rules, Session Template, State Block, Completion Criteria). Modeled on `rpi-implement.md`
  but swaps the 70%/no-RGR-proof model for QRSPI's per-slice RGR + 40/60 budget. Unique tag
  `<qrspi-implement-agent-state>`.
- `opencode/agents/team/qrspi-implement.md` — `mode: primary`, boolean tools (`edit/patch/write/bash/
  glob/grep: true`, `task: false`), `skill({ name })` calls in body. Unique tag
  `<qrspi-implement-agent-oc-state>` (the `-oc-` suffix keeps it distinct from the Claude tag, exactly
  as the `rpi-implement` pair does).

### 4. Command pair (flat, paired)
- `claude/commands/qrspi-implement.md` — `!`-injected `<live_state>` (today + `ls` of feature folders
  AND any existing `implementation/slice-*` logs, so a resuming session sees prior slices), routes to
  the **`qrspi-implement` agent** (not the orchestrator — the orchestrator cannot edit source).
- `opencode/commands/qrspi-implement.md` — `agent: qrspi-implement`, **`subtask: false`** (it writes
  source — per CLAUDE.md "writes files → subtask:false" AND plan §3, which singles out implement as
  the one `subtask:false` QRSPI command). This is the deliberate contrast with the four alignment
  commands, all `subtask: true`.

### 5. Orchestrator touch (both platforms, parity preserved) — minimal
- Flipped the stale "The Implement agent comes online in a later slice" note to reflect that
  `qrspi-implement` now exists as a separate edit-access agent the orchestrator hands off to.
- Completed the Guardrail-2 SEQUENCE CHECK: `PLAN -> ... -> writes plan.md` (flipped the Slice-4
  leftover `(later slice)` marker, now that PLAN is live) and added the `IMPLEMENT -> requires plan.md
  (status: approved) -> runs in the qrspi-implement agent` row.
- The orchestrator's `skills:` array is intentionally **unchanged** — `qrspi-implement` is a separate
  agent (edit access), not a skill the read-only orchestrator loads (plan §3).

## Verification (all green)

| Check | Result |
| --- | --- |
| skills count | 85 → **86** (+qrspi-implement) |
| claude agents (total) | 36 → **37** (+qrspi-implement) |
| opencode agents (total) | 36 → **37** |
| agent parity | 37 == 37 ✅ |
| claude commands | 14 → **15** |
| opencode commands | 14 → **15** |
| command parity | 15 == 15 ✅ |
| minimal-tier lines | qrspi-implement 92 (≤100) ✅ |
| ≥1 reference | slice-log-template.md ✅ |
| frontmatter `name:` == dir | `qrspi-implement` ✅ |
| `add_frontmatter.py` | "0 files updated" — new skill already conforms ✅ |
| unique state tags | `<qrspi-implement-state>`, `<qrspi-implement-agent-state>`, `<qrspi-implement-agent-oc-state>` each appear in exactly one file ✅ |
| agent `skills:` | `[qrspi-implement, tdd]` ✅ (plan §3, §4.4) |
| agent edit access | claude `Edit, Write`; opencode `edit/write/patch: true` ✅ |
| opencode implement subtask | `false` (writes source); alignment phases all `true` ✅ |
| orchestrator SEQUENCE CHECK | PLAN live + IMPLEMENT row present on both platforms ✅ |

These build-end counts (86 / 37 / 37 / 15 / 15) match the plan's post-build targets (plan §6 Slice 6:
"skills 81→86, agents 35→37, commands 10→15"). README/AGENTS badges are NOT yet reconciled — that is
Slice 6 (see deferred).

## Eval status (TDD / eval discipline)

No executable trigger-eval harness exists in-repo yet (plan §5 defers eval authoring). Eval spec
recorded as a checklist for a later eval-harness session.

### `qrspi-implement` trigger evals (plan §5)
- [ ] MUST activate: "/qrspi-implement plan.md", "execute the qrspi plan", "build the approved plan
      slice by slice"
- [ ] MUST NOT activate: "/rpi-implement" (→ deprecated `rpi-implement`), "run tdd" (→ `tdd`),
      "implement the plan" with no QRSPI context (→ `rpi-implement` / generic)
- [ ] Disambiguation: routes here for QRSPI's approved-gated, per-slice-RGR execution; not
      `rpi-implement` (70% checkpoint, no RGR proof), not `tdd`/`tdd-agent` (bare inner loop, no plan)

### Behavior evals (the RGR + approval gates)
- [ ] Implement requested with `plan.md` status only `ready-for-review` → STOPS, asks for approval
- [ ] No `plan.md` present → STOPS and routes to `/qrspi-plan`
- [ ] Red baseline before any change → STOPS, does not fix the baseline
- [ ] Production code written before a failing test → STOP (test-first violation)
- [ ] A slice with no captured RED output is treated as not-done (proof, not prose)
- [ ] At ~40% context (or slice end) → writes the slice log, suggests a commit, hands off a fresh session

## Deliberate plan-driven choices worth noting at review

1. **NEW agent (first one the suite adds).** Unlike Slices 3–4 (which ran under the orchestrator),
   Implement gets its own edit-access agent — plan §3 mandates this: the orchestrator is read-only
   (`edit: false`), so it cannot run Implement. Hence agent counts move 36 → 37 here.
2. **OpenCode `subtask: false` for implement.** The single QRSPI command that writes source; both
   CLAUDE.md and plan §3 agree it must hold primary context, in contrast to the four alignment
   commands (`subtask: true`). This is the inverse of the Slice 2/3 subtask decision, on purpose.
3. **Orchestrator `skills:` left unchanged.** `qrspi-implement` is an agent, not a skill the
   orchestrator loads. The only orchestrator edits are the handoff note + SEQUENCE CHECK completion.
4. **Slice-4 (`qrspi-plan`) deliverables are co-resident and uncommitted.** This slice was built on
   top of the on-disk (but uncommitted) Slice 4 — see "Commit grouping" below.
5. **Planning artifacts left untracked** — `thoughts/qrspi-plan.md` / `qrspi-research.md` remain
   unstaged (meta-artifacts, not slice deliverables), consistent with Slices 2–4.

## Commit grouping (needs a human decision before committing)

The working tree currently mixes **uncommitted Slice 4** (qrspi-plan: orchestrator PLAN wiring +
`skills/team/qrspi-plan/` + both `qrspi-plan` commands) with **new Slice 5** files. Slices 2 and 3
were each a single commit. Recommended: commit Slice 4 first (`feat: QRSPI Slice 4 — qrspi-plan`),
then Slice 5 (`feat: QRSPI Slice 5 — qrspi-implement`), keeping the one-commit-per-slice history.
The orchestrator file carries edits from **both** slices, so a clean split needs either a staged
hunk split or accepting that the orchestrator lands with whichever slice is committed second. Left
uncommitted pending the user's call (no commit was requested).

## Handoff to Slice 6 (Bookkeeping, docs & RPI deprecation)

**What was done:** `qrspi-implement` skill (+ slice-log-template); the `qrspi-implement` agent pair
(edit access, `skills:[qrspi-implement, tdd]`); the `qrspi-implement` command pair; orchestrator
handoff note + SEQUENCE CHECK completed on both platforms. Counts **86 / 37 / 37 / 15 / 15**.

**What tests pass:** all structural/parity/minimal-tier checks above; `add_frontmatter` 0-updates;
unique state tags; agent edit-access + `skills` array. Trigger/behavior evals written as checklists
(no harness yet).

**What's deferred to Slice 6 (do not interleave):**
1. **README**: add the "QRSPI Workflow Suite" section; mark the RPI suite **deprecated** → QRSPI;
   bump the skill/agent/command count badges to 86 / 37 / 15.
2. **AGENTS.md**: add the "QRSPI Workflow" Skill-Suites row; mark the RPI row deprecated; update Open
   Loops counts (skills 81→86, agents 35→37, commands 10→15); add Persistent-Decisions rows
   (per-feature artifact folder #10, reference-don't-vendor #2, broadened minimal-tier #6, QRSPI
   replaces RPI #8); fix the two stale `skills/<name>/` paths and document `audience:` (#11).
3. **RPI DEPRECATED markers**: `disable-model-invocation: true` + `**DEPRECATED — use QRSPI instead**`
   prefix on the 4 rpi-* skills and the `rpi-planner`/`rpi-implement` agents (both platforms).
4. **`.matt-pocock-attribution.yml`**: no change (#2 = vendor 0 new).
5. **Commit grouping** (above) should be resolved before Slice 6 starts so the history is clean.

**What Slice 7 (sunset, ~2026-09-01) will do:** delete the 4 rpi-* skill dirs + `rpi-planner`/
`rpi-implement` agent pairs; counts 86→82, agents 37→35, commands stay 15; remove deprecated rows.

**Branch:** `qrspi-slice-3-spec` (Slices 4 + 5 uncommitted on disk; no commit made — see grouping).
