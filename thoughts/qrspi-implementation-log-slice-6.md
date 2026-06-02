---
date: 2026-06-02T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 6 — bookkeeping, docs & RPI deprecation"
tags: [qrspi, slice-6, bookkeeping, deprecation, rpi, docs, agents-md, readme]
git_commit: cfa92cd
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 6
branch: qrspi-slice-3-spec
status: complete
---

# QRSPI Implementation Log — Slice 6: Bookkeeping, docs & RPI deprecation

Implements Slice 6 from `thoughts/qrspi-plan.md` §6. This is a **docs/bookkeeping slice** — no
production code, so there is no Red-Green-Refactor cycle. Verification is structural (count/parity
checks), matching how Slices 2–5 verified. It reconciles README/AGENTS badges to the
already-on-disk QRSPI suite (Slices 2–5 deferred all doc reconciliation here, per the Slice 5
handoff) and marks RPI deprecated ahead of the Slice 7 sunset.

## What this slice is (per plan §6, Slice 6, re-read in full)

> - Deprecate RPI (#8): `disable-model-invocation: true` + `**DEPRECATED — use QRSPI instead**`
>   prefix on the 4 rpi-* skills and the `rpi-planner`/`rpi-implement` agents (both platforms).
> - README: add a "QRSPI Workflow Suite" section; mark the RPI suite deprecated; bump counts.
> - AGENTS.md: add a "QRSPI Workflow" Skill-Suites row; mark the RPI row deprecated; update Open
>   Loops counts; add Persistent-Decisions rows (#10, #2, #6, #8); fix the two stale
>   `skills/<name>/` paths and document `audience:` (#11).
> - `.matt-pocock-attribution.yml`: no change (#2 = vendor 0 new).
> - Checkpoint: skill count matches the README badge; agent/command parity match (37/37, 15/15);
>   every QRSPI skill has ≥1 reference; the 4 rpi-* skills no longer auto-invoke + carry DEPRECATED;
>   no `rpi-file-locator|rpi-code-analyzer|rpi-pattern-finder` files remain.

## What was done

### 1. RPI deprecation markers (#8)
- **4 rpi-* skills** (`rpi-research`, `rpi-plan`, `rpi-implement`, `rpi-iterate`): added
  `disable-model-invocation: true` to frontmatter and a `**DEPRECATED — use QRSPI (<replacement>)
  instead.**` prefix to each `description`. Replacement pointers: research→`qrspi-research`,
  plan→`qrspi-plan`, implement→`qrspi-implement`. `rpi-iterate` has **no** QRSPI equivalent (plan
  #7), so its prefix routes to "edit spec.md and re-run /qrspi-plan instead".
- **2 rpi agent pairs** (`rpi-planner`, `rpi-implement`, both platforms = 4 files): prepended the
  `**DEPRECATED — use the QRSPI workflow (<agent>) instead.**` prefix to each `description`.
  `disable-model-invocation` is a **skill** field (AGENTS.md:135 semantics — confirmed by the
  plan's own parenthetical scoping in #8), so for agents the description prefix is the deprecation
  mechanism; no `disable-model-invocation` was added to agent frontmatter.
- Skill bodies and agent bodies are otherwise untouched — RPI keeps functioning for explicit
  opt-in during the transition window (full removal is Slice 7, ~2026-09-01).

### 2. AGENTS.md
- **Skill Suites table**: added a `QRSPI Workflow` row (5 phase skills + orchestrator/implement
  agents + renamed `research-*` subagents) and marked the `RPI Workflow` row
  `_(DEPRECATED — use QRSPI)_` with the sunset note.
- **Open Loops**: skills 81→86, agents 35→37, commands 10→15 — each line annotated with the QRSPI
  delta and the sunset reversion (skills→82, agents→35/35 at Slice 7).
- **Persistent Decisions**: added 4 rows dated 2026-06-02 — #8 (QRSPI replaces RPI; deprecate now,
  remove at sunset), #2 (vendor 0 new primitives; reference `tdd`), #6 (broaden minimal-tier to
  "thin, self-sufficient workflow-phase drivers ≤ ~40 directives"), #10 (per-feature artifact
  folder `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/`).
- **Project Overview** prose: "81+ skills" → "86+ skills".
- **Stale-path fixes (#11)**: `skills/architecture-review/SKILL.md` → `skills/personal/architecture-review/SKILL.md`
  (3 occurrences: lines for Key Files, Persistent Decisions, gold-standard pointer); the two
  generic `skills/<name>/` paths (Key directories + Skill Conventions intro) → `skills/{team,personal}/<name>/`;
  and **documented `audience:`** in both the Skill Conventions prose and the frontmatter example
  (`audience: team  # team | personal — selects the skills/<audience>/ install subdirectory`).
  Fixed all 5 stale occurrences (plan #11 named 3; the other 2 were the same stale strings — fixing
  all keeps the diff coherent rather than leaving identical strings half-stale).

### 3. README.md
- **Badges**: skills 81→86, agents 35→37.
- **Summary line**: "86 skills, 37 agents, and 15 slash commands".
- **At a glance table**: Skills (team) 63→68, Agents (Claude/OpenCode) 35→37 each, Slash commands 10→15.
- **QRSPI Workflow Suite** section added (all 5 phase skills, the artifact-gate / no-magic-words
  framing, the agent/subagent drivers, the per-feature folder path); **RPI Workflow Suite** marked
  `_(deprecated — use QRSPI)_` with a sunset blockquote.
- **Team-agents header**: "(32 agents)" → "(34 agents)" (27 listed rows + 7 workflow subagents =
  qrspi ×2, research-* ×3, rpi ×2).
- **Workflow-subagent footnote** rewritten: now documents the QRSPI agents + renamed `research-*`
  subagents (corrects the stale pre-Slice-2 `rpi-code-analyzer/file-locator/pattern-finder` names)
  and flags the deprecated `rpi-planner`/`rpi-implement`.
- **Commands section**: "Ten" → "Fifteen"; added the 5 `/qrspi-*` command rows.
- **Repository Structure tree**: team skills 63→68, team agents 32→34 (both platforms), commands
  10→15 (both platforms).
- **Stale path (#11)**: "Live in `skills/<name>/SKILL.md`" → `skills/{team,personal}/<name>/SKILL.md`.

### 4. `.matt-pocock-attribution.yml`
- **No change** (#2 = reference existing `tdd`/`*-feature-slice`, vendor 0 new). Confirmed
  untouched in the diff.

## Verification (all green — structural, per plan §6 checkpoint)

| Check | Expect | Result |
| --- | --- | --- |
| `find skills -name SKILL.md \| wc -l` | 86 | **86** ✅ (matches README badge) |
| claude agents (recursive) | 37 | **37** ✅ |
| opencode agents (recursive) | 37 | **37** ✅ |
| agent parity | 37 == 37 | ✅ |
| claude / opencode commands | 15 / 15 | **15 / 15** ✅ |
| team skills | 68 | **68** ✅ |
| claude / opencode team agents | 34 / 34 | **34 / 34** ✅ |
| each qrspi skill ≥1 reference | yes | ✅ (questions/research/plan/implement = 1, spec = 2) |
| 4 rpi-* skills `disable-model-invocation: true` | all | ✅ (4/4) |
| 4 rpi-* skills DEPRECATED prefix | all | ✅ (4/4) |
| 4 rpi agent files DEPRECATED prefix | all | ✅ (claude+opencode × planner+implement) |
| no `rpi-{file-locator,code-analyzer,pattern-finder}.md` | 0 | **0** ✅ |
| renamed `research-*` subagents present | 6 | **6** ✅ |
| stray stale counts/paths in README+AGENTS | none | **none** ✅ |
| `add_frontmatter.py` | 0 updated | **"0 files updated"** ✅ (tree conforms) |
| `.matt-pocock-attribution.yml` diff | none | **none** ✅ |
| files changed | 10 | AGENTS.md, README.md, 4 rpi agents, 4 rpi skills ✅ |

## Deliberate plan-driven choices worth noting at review

1. **`disable-model-invocation` on skills only, DEPRECATED prefix on agents.** The plan lumps
   skills + agents in the #8 sentence but its own parenthetical scopes the field to skills. Agents
   are gated via their `description` (what the selector sees), so the prefix is their deprecation
   mechanism; no undocumented agent frontmatter field was invented.
2. **Fixed all 5 stale `skills/...` strings, not the 3 the plan named.** The other 2 are the same
   stale strings (Key directories + the README "Live in" line). Leaving identical strings
   half-corrected would be worse for a reviewer than fixing the lot. Still surgical — no AGENTS.md
   rewrite (#11 honored in spirit and letter).
3. **README agent tables were stale, not just the badges.** Slices 2/5 deferred *all* doc work
   here, so the "(32 agents)" header and the pre-rename subagent footnote were corrected as part of
   this slice — they are the same bookkeeping surface the plan assigns to Slice 6.
4. **QRSPI agents documented in the footnote, not the main agent table.** Mirrors how RPI's
   workflow agents were documented (spawned automatically, not invoked directly) — parity with the
   established pattern rather than a new table row.
5. **No eval harness run.** Plan §5 defers eval authoring; no executable trigger-eval harness
   exists in-repo. The disambiguation eval spec from Slices 2–5 still stands as a checklist.

## Eval status (TDD / eval discipline)

No code in this slice → no unit tests. No executable trigger-eval harness in-repo (plan §5 defers
eval authoring to a later session). Structural verification table above is the acceptance gate; all
rows pass.

## Build complete: Slices 1–6 done

The initial QRSPI build (plan §6 Slices 1–6) is now complete and the full **Q→R→S→P→I** pipeline
plus all bookkeeping is in place. End-state counts: **86 skills / 37 agents (both) / 15 commands
(both)**, README + AGENTS reconciled, RPI deprecated.

## Handoff to Slice 7 (Sunset — scheduled ~2026-09-01, +90 days)

**What Slice 7 will do** (do NOT do now — it is a scheduled, separate step):
1. Delete the 4 deprecated `rpi-*` skill dirs (`rpi-research`, `rpi-plan`, `rpi-implement`,
   `rpi-iterate`) and the `rpi-planner`/`rpi-implement` agent pairs (both platforms).
2. Verify nothing references them: `grep -rl 'rpi-' --include='*.md' .` clean (note: the
   `research-*` subagents and QRSPI suite remain; only `rpi-*` names go).
3. Update counts: skills 86→82, agents 37→35 (both); commands stay 15. Remove the deprecated RPI
   rows from README (suite section + footnote) and AGENTS.md (suite row + Open-Loops sunset notes).
4. Checkpoint: `find . -name 'rpi-*'` empty; QRSPI + `research-*` subagents are the only workflow
   remaining.

**Trigger condition (verbatim from plan §6 / §8):** sunset fires ~2026-09-01 — the owner-confirmed
90-day deprecation window from the 2026-06-02 deprecation.

**Branch:** `qrspi-slice-3-spec` (Slice 6 changes uncommitted on disk; no commit was requested).
