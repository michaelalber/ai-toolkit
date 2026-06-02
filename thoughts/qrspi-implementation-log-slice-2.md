---
date: 2026-06-01T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 2 — qrspi-questions + qrspi-research (smallest viable QRSPI entry point)"
tags: [qrspi, rpi, implement, slice-2, questions, research, subagent-rename]
git_commit: 7044b767229a8f80da640e34a98a04900a7576e0
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 2
branch: qrspi-slice-2-questions-research
status: complete
---

# QRSPI Implementation Log — Slice 2: `qrspi-questions` + `qrspi-research`

Implements Slice 2 from `thoughts/qrspi-plan.md` §6. Delivers the smallest viable QRSPI entry
point: a user can run `/qrspi-questions` then `/qrspi-research` and get a `questions.md` plus a
ticket-hidden `research.md` in a per-feature folder, while the deprecated RPI suite keeps working
against the renamed read-only subagents.

## What this slice is (per plan §6, Slice 2, re-read in full)

> - Rename the 3 read-only subagents (#8): rpi-file-locator → research-file-locator,
>   rpi-code-analyzer → research-code-analyzer, rpi-pattern-finder → research-pattern-finder
>   (6 paired files + state-tags). Repoint the deprecated rpi-research/rpi-planner to the new
>   names so RPI keeps working during the window.
> - Write both SKILL.md (+ references), the qrspi-orchestrator agent pair (drives Q→R, spawns
>   the renamed research-* subagents), and both command pairs.
> - Checkpoint: a user can run /qrspi-questions then /qrspi-research and get questions.md + a
>   ticket-hidden research.md in a feature folder; deprecated rpi-research still resolves its
>   (renamed) subagents. Q→R works without S/P/I.

## What was done

### 1. Renamed the 3 read-only subagents (6 files, both platforms)
`git mv` + content neutralization (so **no rpi-\* branding survives** in these files, plan §8):
- `rpi-file-locator → research-file-locator`, `rpi-code-analyzer → research-code-analyzer`,
  `rpi-pattern-finder → research-pattern-finder` in both `claude/agents/team/` and
  `opencode/agents/team/`. Git detected all 6 as renames (R).
- Inside each: state-block tag renamed (`<research-file-locator-state>` etc.), title renamed
  (`# Research File Locator …`), `RPI read-only subagent` → `Read-only research subagent`,
  `RPI subagent:` → `Research subagent:`, and `rpi-planner` → `the orchestrator` (neutral, since
  both the deprecated `rpi-planner` and the new `qrspi-orchestrator` now spawn them).
- **Behavior unchanged** — only branding/identity. Tools, protocol, self-checks untouched.

### 2. Repointed live spawn references so RPI keeps working
Replaced ONLY the three subagent tokens (kept each file's own `rpi-*` identity) in:
- `claude/agents/team/rpi-planner.md`, `opencode/agents/team/rpi-planner.md`
- `skills/team/rpi-research/SKILL.md` + `references/subagent-delegation-guide.md`
- `skills/team/rpi-iterate/SKILL.md` + `references/changelog-template.md`  ← **see Plan Gap below**

Verified `rpi-planner` still spawns `@research-file-locator/-code-analyzer/-pattern-finder` and
still loads its own `rpi-research/rpi-plan/rpi-iterate` skills (identity intact).

### 3. Wrote the two QRSPI phase skills (minimal tier)
- `skills/team/qrspi-questions/SKILL.md` (86 lines) + `references/questions-template.md`
- `skills/team/qrspi-research/SKILL.md` (93 lines) + `references/research-template.md`
- Both ≤ 100 lines, ≤ ~40 directives, self-sufficient when invoked directly, ≥1 reference
  (plan #6). Frontmatter shape matches `rpi-research/SKILL.md:1-8` (`name`, `audience: team`,
  `description: >` with `/qrspi-<phase>` usage + natural triggers + a `Do NOT use` negative that
  includes the RPI negative for word-collision disambiguation, plan §5).
- Ticket-hidden firewall stated verbatim in `qrspi-research` Core Philosophy (plan §4.1).
- 40/60 context-budget rule + `context_budget` state field in both (plan §4.5).

### 4. Wrote the orchestrator agent pair (full 10-section template)
- `claude/agents/team/qrspi-orchestrator.md` (`tools: Read, Glob, Grep, Bash, Write`,
  `model: inherit`, `skills: [qrspi-questions, qrspi-research]`) and the OpenCode mirror
  (`mode: primary`, `edit:false`, `task:true`, `skill({name})` calls).
- Owns cross-phase **sequencing** (artifact gates, not magic phrases) and the ticket-hidden
  firewall. Scoped to Q→R this slice; a note marks Spec/Plan/Implement as later-slice additions
  (no dangling skill loads — `skills:` lists only the two that exist).
- Unique state tag `<qrspi-orchestrator-state>`.

### 5. Wrote both command pairs (flat, paired)
- `claude/commands/qrspi-questions.md`, `qrspi-research.md` — `!`-injected `<live_state>`
  (today's date + `ls` of feature folders/artifacts), route to `qrspi-orchestrator`.
- `opencode/commands/qrspi-questions.md`, `qrspi-research.md` — `agent: qrspi-orchestrator`,
  `subtask: true` (per plan §3: alignment phases are read-heavy; see Note below).

## Verification (all green)

| Check | Result |
| --- | --- |
| skills count | 81 → **83** (+qrspi-questions, +qrspi-research) |
| claude agents | 35 → **36** (+qrspi-orchestrator; 3 renames net 0) |
| opencode agents | 35 → **36** |
| claude commands | 10 → **12** | 
| opencode commands | 10 → **12** |
| agent parity | 36 == 36 ✅ |
| command parity | 12 == 12 ✅ |
| minimal-tier lines | qrspi-questions 86, qrspi-research 93 (≤100) ✅ |
| ≥1 reference per skill | 1 each ✅ |
| frontmatter `name:` == dir | ✅ both skills + 3 renamed subagents |
| unique state tags | new tags appear only in their own (paired) files; no rpi-*-state remnants ✅ |
| dangling subagent refs | only `README.md` + `docs/` retain old names (deferred to Slice 6) ✅ |
| `add_frontmatter.py` | "0 files updated" — new skills already conform ✅ |
| git rename detection | all 6 subagent moves shown as `R` ✅ |

## Eval status (TDD / eval discipline)

No executable trigger-eval harness exists in-repo at this stage (plan §5 defers eval authoring).
Per session discipline, the eval spec is the markdown checklist below for a later eval-harness
session to execute. Nothing to RED-GREEN mechanically yet.

### `qrspi-questions` trigger evals (plan §5)
- [ ] MUST activate: "/qrspi-questions add SSO", "what don't we know about the billing rewrite",
      "surface unknowns for the export feature"
- [ ] MUST NOT activate: "answer this question: …", generic Q&A, "/rpi-research X"
- [ ] Disambiguation: routes here, not `spec-coach` (interactive design) or `grill-me` (quizzes me)

### `qrspi-research` trigger evals (plan §5 — dominant QRSPI↔RPI collision risk)
- [ ] MUST activate: "/qrspi-research X", "qrspi research X", "ticket-hidden research for X"
- [ ] MUST NOT activate: "/rpi-research X", "rpi research X"  → must route to deprecated `rpi-research`
- [ ] Disambiguation: same words as `rpi-research`; the `Do NOT use … rpi-research` negative in the
      description must win routing when the user names the workflow

### Behavior-preservation evals for the rename (RPI must still work)
- [x] `grep -rlE 'rpi-(file-locator|code-analyzer|pattern-finder)'` over `claude/ opencode/ skills/`
      returns nothing (all live refs repointed)
- [x] `rpi-planner` (both platforms) spawns `@research-*` and retains `skills: rpi-research/plan/iterate`
- [x] renamed subagents keep `tools: Read, Glob, Grep` (claude) / `read/glob/grep: true` (opencode),
      read-only discipline intact

## Plan gap flagged (and how I resolved it)

**The plan's Slice 2 repoint list ("repoint the deprecated rpi-research/rpi-planner") is
non-exhaustive.** `rpi-iterate/SKILL.md` (lines 88-89, 157, 244) and its `changelog-template.md`
also issue live `@rpi-file-locator`/`@rpi-code-analyzer` spawn calls, and
`rpi-research/references/subagent-delegation-guide.md` carries the live `Task(@rpi-*)` delegation
table. Leaving any of these on the old names would dangle once the agent files are renamed —
directly contradicting the plan's own stated goal that "RPI keeps working during the window"
(§8 step 1, §6 Slice 2 checkpoint).

**Resolution:** I repointed the full set of LIVE spawn references (rpi-planner ×2, rpi-research
SKILL + its delegation guide, rpi-iterate SKILL + its changelog template). I did **not** touch
`README.md:344` or `docs/rpi-and-spec-driven-dev-overview.md:39-41` — those are prose/doc
references, not live spawns, and the session constraint reserves doc bookkeeping for Slice 6.
This is the minimal superset that satisfies the checkpoint without interleaving Slice 6 work.

## Deliberate plan-driven choices worth noting at review

1. **OpenCode `subtask: true` for questions/research** despite both writing a small artifact.
   Plan §3 explicitly classifies the alignment phases as read-heavy (`subtask:true` for
   questions/research/spec/plan; `false` only for implement). Followed the plan over CLAUDE.md's
   general "writes files → subtask:false" heuristic, since the artifacts are small and the phases
   are dominated by reading. Flag for review if you prefer the heuristic.
2. **Subagent prose neutralized to `the orchestrator`** rather than naming `qrspi-orchestrator`,
   because both `rpi-planner` (deprecated) and `qrspi-orchestrator` spawn them during the window.
3. **Planning artifacts left untracked** — `thoughts/qrspi-plan.md` / `qrspi-research.md` were
   unstaged from this commit (not Slice 2 work; consistent with the Slice 1 session).

## Handoff to Slice 3 (`qrspi-spec`)

**What was done:** subagent rename + full live-ref repoint; `qrspi-questions` + `qrspi-research`
skills (+ templates); `qrspi-orchestrator` pair (Q→R); 4 command files. Counts 83 / 36 / 36 / 12 / 12.

**What tests pass:** all structural/parity/minimal-tier checks above; rename behavior-preservation
evals (3/3). Trigger evals are written as checklists (no harness yet).

**What's deferred:** README/AGENTS.md/docs bookkeeping and the RPI DEPRECATED markers → **Slice 6**
(do not interleave). Counts are NOT yet reflected in README/AGENTS.md badges — Slice 6 reconciles
81→86 / 35→37 / 10→15 at build end. After Slice 2 the interim reality is 83 / 36 / 36 / 12 / 12.

**What Slice 3 needs to know:**
1. **Extend the orchestrator, don't rebuild it.** Add `qrspi-spec` to `qrspi-orchestrator`
   `skills:` (both platforms), add a SPEC section to the Autonomous Protocol, and flip the
   "Spec comes online later" note. The SEQUENCE CHECK guardrail already lists `SPEC -> requires
   research.md` — wire it live.
2. **`qrspi-spec` is minimal tier** (≤100 lines, ≤~40 directives, ≥1 reference), same frontmatter
   shape. It needs TWO reference files per plan §2: `spec-template.md` and `stage-mapping.md`
   (the 8-stage→5-phase table, plan #9).
3. **Brain-surgery loop (plan §4.2):** write the ~200-line Design Brain-Dump, STOP, present, loop
   on human redirection (`design_approved: true|false` in the state block), and only then write
   the Structure Outline. Model the hard human gate on `rpi-plan`'s DESIGN step.
4. **Vertical-slice structure (plan §4.3):** the Structure Outline instructs slices as
   mock-API → front-end → database with checkpoints. Cross-link the `*-feature-slice` skills in
   Integration (plan #2).
5. **Artifact:** `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/spec.md` with lifecycle
   `status: draft | ready-for-review | approved`; unique tag `<qrspi-spec-state>`.
6. **Branch from `main`** (each slice branch is reviewed independently; Slice 1 + Slice 2 added no
   source the later slices depend on at the file level except the orchestrator — if Slice 3 needs
   the orchestrator present, branch from this slice's branch instead and note it).

**Branch:** `qrspi-slice-2-questions-research` (committed, not pushed, no PR — local review first).
