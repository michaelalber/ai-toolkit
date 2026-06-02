---
date: 2026-06-01T00:00:00
repository: ai-toolkit
topic: "QRSPI Slice 1 — Primitives (no-op confirmation)"
tags: [qrspi, rpi, implement, slice-1, primitives]
git_commit: 7044b767229a8f80da640e34a98a04900a7576e0
plan_artifact: thoughts/qrspi-plan.md
phase: Implement (I)
slice: 1
branch: qrspi-slice-1-primitives
status: complete
---

# QRSPI Implementation Log — Slice 1: Primitives (no-op confirmation)

Implements Slice 1 from `thoughts/qrspi-plan.md` §6. Per plan decision #2
("reference existing `tdd` + `*-feature-slice`; vendor 0 new"), Slice 1 writes **no new
files** — it confirms the reused primitives are present and loadable, and records the baseline
counts that later slices will mutate. This is a deliberate no-op-build slice, not skipped work.

## What this slice is (per plan §6, Slice 1, re-read in full)

> - No new files. Primitives are the **existing** `tdd` + `*-feature-slice` skills; they are
>   referenced from the Integration sections written in Slices 4–5.
> - Confirm the dependencies are present and loadable: `tdd` (`skills/team/tdd/SKILL.md`) and at
>   least the `*-feature-slice` skills relevant to the target stack.
> - **Checkpoint:** reused primitives confirmed present; no skill-count change.

## What was done

1. Verified the four reused primitives are present, carry valid `name:` frontmatter, and have a
   `references/` directory (i.e. structurally loadable as skills):

   | Primitive | Path | `name:` | `references/` |
   | --- | --- | --- | --- |
   | TDD inner loop (RGR) | `skills/team/tdd/SKILL.md` | `tdd` | ok |
   | .NET vertical slice | `skills/team/dotnet-vertical-slice/SKILL.md` | `dotnet-vertical-slice` | ok |
   | Python feature slice | `skills/team/python-feature-slice/SKILL.md` | `python-feature-slice` | ok |
   | Rust feature slice | `skills/team/rust-feature-slice/SKILL.md` | `rust-feature-slice` | ok |

   `tdd` is the canonical RED-GREEN-REFACTOR inner loop that `qrspi-implement` will load
   (plan #2-A; agent `skills:[qrspi-implement, tdd]`). The three `*-feature-slice` skills are the
   stack-specific scaffolders the Integration sections of `qrspi-spec`/`qrspi-plan`/`qrspi-implement`
   will cross-link (plan #2).

2. Recorded the baseline parity/count numbers as the **pre-build snapshot**. These are the
   numbers Slice 6 must move to, and Slice 7 (sunset) must move again:

   | Metric | Baseline (now) | After build (Slice 6 target) | After sunset (Slice 7 target) |
   | --- | --- | --- | --- |
   | skills (`find skills -name SKILL.md`) | **81** | 86 (+5 phase skills) | 82 (−4 rpi-* skills) |
   | claude agents | **35** | 37 (+2 qrspi agents) | 35 (−2 rpi-* agents) |
   | opencode agents | **35** | 37 | 35 |
   | claude commands | **10** | 15 (+5 qrspi commands) | 15 |
   | opencode commands | **10** | 15 | 15 |

   (Note: the 3 rpi read-only subagents are *renamed* to `research-*` in Slice 2, not added or
   removed, so they do not change the agent counts. The +2 agent delta is purely
   `qrspi-orchestrator` + `qrspi-implement`.)

3. Confirmed no skill-count change occurred this slice (still 81). Checkpoint met.

## Eval status (TDD / eval discipline for this slice)

Slice 1 ships **no skill, agent, or command** — therefore it introduces **no new activation
triggers** and has **nothing to RED-GREEN against**. The Red-Green-Refactor / failing-trigger-eval
discipline applies to Slices 2–5 where skills actually ship. For this slice the eval spec is the
checklist below; it is satisfied by the confirmation work above.

### Slice 1 eval checklist (executable by a later eval-harness session — all pass)

- [x] `skills/team/tdd/SKILL.md` exists and has a `name:` frontmatter key.
- [x] All three `*-feature-slice` SKILL.md files exist with `name:` frontmatter.
- [x] Each primitive has a `references/` directory (minimal/full-tier rule, AGENTS.md:143).
- [x] `find skills -name SKILL.md | wc -l` == 81 (no skill added or removed by this slice).
- [x] No `skills/team/qrspi-*` directory exists yet (Slice 1 writes no QRSPI skill).
- [x] No new branch artifact other than this log.

### Forward eval debt this slice does NOT own (carried to Slices 2–5, plan §5)

The 200-trigger-eval set in plan §5 belongs to the slices that ship the skills. Recorded here so
it is not lost:

- `qrspi-questions` — MUST: "/qrspi-questions X", "surface unknowns for X"; MUST NOT: generic Q&A;
  disambiguate vs `spec-coach`, `grill-me`. (Slice 2)
- `qrspi-research` — MUST: "/qrspi-research X", "ticket-hidden research"; MUST NOT: "/rpi-research X";
  disambiguate vs `rpi-research` (same words, different workflow — dominant collision risk). (Slice 2)
- `qrspi-spec` — MUST: "design discussion for X", "structure outline for X"; MUST NOT: "write a PRD".
  (Slice 3)
- `qrspi-plan` — MUST: "/qrspi-plan X"; MUST NOT: "/rpi-plan X" (highest collision risk). (Slice 4)
- `qrspi-implement` — MUST: "/qrspi-implement plan.md"; MUST NOT: "/rpi-implement", "run tdd". (Slice 5)

## Plan-vs-reality cross-check (flagging, not resolving)

No discrepancies found for Slice 1. The plan's stated baseline (skills 81, agents 35/35, commands
10/10) matches the filesystem exactly as of `git_commit 7044b76`. The plan's correction of the
stale research claim (OpenCode agents ARE nested under `opencode/agents/team/`, all 5 rpi-* agents
present, three read-only subagents present in both platforms) was re-verified this session:
`opencode/agents/team/` contains `rpi-file-locator.md`, `rpi-code-analyzer.md`,
`rpi-pattern-finder.md` — confirming the Slice 2 rename targets exist on both platforms.

## Handoff to Slice 2 (`qrspi-questions` + `qrspi-research`)

**What was done:** Primitives confirmed present + loadable; baseline counts captured (81 / 35 / 35
/ 10 / 10); no files added; this log written.

**What tests pass:** Slice 1 eval checklist (6/6, structural). No executable test suite for this
slice — nothing ships.

**What's deferred:** Everything that writes files. Slice 1 is intentionally inert per plan #2.

**What Slice 2 needs to know:**
1. **Rename targets exist on both platforms.** `rpi-file-locator`, `rpi-code-analyzer`,
   `rpi-pattern-finder` are present in BOTH `claude/agents/team/` and `opencode/agents/team/`
   (6 files). Slice 2 renames all 6 to `research-file-locator` / `research-code-analyzer` /
   `research-pattern-finder`, renames their State-Block XML tags, and **repoints** the deprecated
   `rpi-research` skill + `rpi-planner` agent to the new names so RPI keeps working during the
   deprecation window (plan #8 step 1, §6 Slice 2).
2. **Baseline to move:** Slice 2 adds `qrspi-questions` + `qrspi-research` skills (81→83),
   `qrspi-orchestrator` agent pair (35→36 each), and both command pairs (10→12 each). The +2 agent
   count from the orchestrator lands here; `qrspi-implement` agent is Slice 5.
3. **Minimal tier, ≤ ~40 directives, self-sufficient** (plan #6). Each skill must work when invoked
   directly without the orchestrator supplying per-phase logic. ≥1 `references/` file each.
4. **Frontmatter shape** matches `rpi-research/SKILL.md:1-8`: `name`, `audience: team`,
   `description: >` with `/qrspi-<phase>` usage + natural triggers + a `Do NOT use when` negative
   (must include the RPI negative trigger to win the word-collision disambiguation, plan §5).
5. **Ticket-hidden research is structural** (plan §4.1): the orchestrator passes only a neutral
   topic string to the renamed read-only subagents (tools `Read, Glob, Grep` — they never receive
   the ticket); `qrspi-research` Core Philosophy states the rule verbatim.
6. **Artifact paths** (plan #10): `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/questions.md` and
   `research.md`. Per-feature folder is what makes the 40/60 context budget cheap.
7. **Voice/attribution constraints (session-level):** match rpi-* prose voice + frontmatter
   exactly; keep Matt Pocock attribution visible on primitive skills; no magic words (default
   behavior on a plain prompt must be correct); AGENTS.md updates are Slice 6 — do NOT interleave.

**Branch:** `qrspi-slice-1-primitives` (committed, not pushed, no PR — local review first).
