---
date: 2026-06-02
repository: ai-toolkit
topic: "QRASPI Slice 3 — qraspi-architecture (RPI Implement phase)"
plan: thoughts/qraspi-plan.md
slice: 3
branch: qraspi-slice-2-questions-research
status: complete
---

# QRASPI Slice 3 — `qraspi-architecture` (the phase where the picks happen)

Implements Plan §6 Slice 3 + §4.3 / #5 / #8 / #12: the Architecture phase. A user can now run
`/qraspi-architecture` after Research and get aligned **MADR ADRs with alternatives** in the target
repo's `docs/adr/`, plus an `architecture.md` summary carrying **C4 Context + Container (Mermaid)**
and a **fitness-function spec** that hands off to the Slice-1 `fitness-functions` primitive. Q→R→A
now works end to end in the `qraspi-orchestrator` agent (no Edit).

## What was done

| File | Lines | Purpose |
|------|-------|---------|
| `skills/team/qraspi-architecture/SKILL.md` | 122 | Minimal-tier Architecture phase; MADR-ADRs-with-alternatives, align-before-lock gate, Mermaid C4, required fitness-function exit gate, optional `domain-model` pre-step |
| `skills/team/qraspi-architecture/references/adr-template.md` | 73 | MADR ADR template — **Considered Options required** (>= 2); `proposed`→`accepted`; sequential `NNNN-kebab` filenames; per-ADR fitness-function trace |
| `skills/team/qraspi-architecture/references/c4-conventions.md` | 95 | Mermaid `C4Context` + `C4Container` (two levels only); snippets; `architecture.md` summary shape that indexes the ADRs |
| `skills/team/qraspi-architecture/references/fitness-spec.md` | 56 | The fitness-function **spec** table (attribute · threshold · candidate tool · ADR id) — the contract handed to `fitness-functions` in Skeleton; spec here, authoring there |
| `claude/agents/team/qraspi-orchestrator.md` | extended | `skills:` += `qraspi-architecture`; new Guardrail 5 (ADR Alignment Gate); ARCHITECTURE protocol; self-check; 2 error-recovery paths; state fields `adrs_aligned`, `fitness_functions_specified`; completion criteria; Guardrail 1 broadened for `docs/adr/` |
| `opencode/agents/team/qraspi-orchestrator.md` | parity | Same body edits; protocol uses `skill({ name: "qraspi-architecture" })`; frontmatter `description` updated to name Architecture + `docs/adr/` |
| `claude/commands/qraspi-architecture.md` | — | `/qraspi-architecture <project>`, `!`-injected `ls` of `thoughts/shared/qraspi/`, routes to orchestrator, restates every gate |
| `opencode/commands/qraspi-architecture.md` | parity | `agent: qraspi-orchestrator`, `subtask: true` (read-heavy alignment, Plan §3) |

### Convention conformance (per session constraints)

- **Skill shape** matches the landed `qraspi-research` / `qrspi-spec` minimal-tier skills: block-scalar
  `description` with positive triggers + negative triggers; adapted-quote epigraph (Grady Booch on
  significant decisions); the verbatim 40%/60% **CONTEXT BUDGET** rule as the last Non-Negotiable; the
  `Core Philosophy → Workflow (PRE-FLIGHT→phase gates→Exit criteria) → State Block → Output Template →
  Integration` 5-part shape; unique state tag `<qraspi-architecture-state>` (verified sole definer).
- **Negative triggers** are phase-appropriate (Plan §5): QRSPI has **no** Architecture phase, so
  instead of a `qrspi-architecture` redirect the description routes away from `architecture-review`
  (review an EXISTING system), `architecture-journal` (retrospective ADR journaling), and `qrspi-spec`
  (design a feature in an existing codebase) — plus the standard deprecated-RPI negative.
- **Orchestrator** stays on the full agent template; Architecture is an alignment (no-source-edit)
  phase, so it lives in `qraspi-orchestrator` not `qraspi-builder` (#4 edit-seam holds). Guardrail 1
  was **broadened** (see Decision note below) to permit writing new `docs/adr/NNNN-*.md` records.
- **Reused primitives referenced, not duplicated:** `fitness-functions` (authoring/wiring — this
  phase only *specifies*), `domain-model` (optional pre-step), `architecture-journal` (the reusable
  ADR niche — this phase uses a MADR variant for the greenfield lock), `dependency-mapper`
  (referenced in `fitness-spec.md` for coupling metrics). No content copied.
- **Matt Pocock attribution:** N/A — original work, nothing vendored (`.matt-pocock-attribution.yml`
  unchanged).

### Greenfield-specific defaults implemented (no magic words — Plan §4.3)

- **Alternatives are mandatory:** `adr-template.md` is MADR with a required **Considered Options**
  section; the skill self-check + orchestrator Guardrail 5 fail any ADR with < 2 real options. A
  fait-accompli ADR cannot reach WRITE. State flag `adrs_min_alternatives_met`.
- **Brain-surgery alignment before lock:** ADRs are written `status: proposed`, the agent STOPS and
  presents, loops on the human's redirection, and sets `status: accepted` only after approval. State
  flag `adrs_aligned: true|false` is the gate — the greenfield analog of `qrspi-spec`'s
  `design_approved` (Plan §4.3).
- **Fitness functions are required output:** exit criteria require `fitness_functions_specified > 0`
  — >= 1 fitness function for every accepted ADR naming a measurable quality attribute. Authoring
  delegates to the `fitness-functions` primitive (the spec is the contract; Skeleton lands the gate).
- **#8 Mermaid C4:** `c4-conventions.md` standardizes on `C4Context` + `C4Container` only (markdown
  -native, no build system). **#12 domain-model:** optional PRE-FLIGHT step on high domain complexity
  — folded into Architecture, **not** a 7th phase.

## Tests / verification that pass

No executable evals this slice (Plan §5: trigger evals are authored in a later eval-harness session).
Verification was structural, all green:

- `find skills -name SKILL.md | wc -l` → **90** (89 → 90; +1 skill — consistent with the Slice 2 log's
  reconciled running count, final target 94).
- `grep -c '^## '` on the new SKILL → **5** sections (minimal tier — no 10-section requirement).
- references present: **3** (`adr-template.md`, `c4-conventions.md`, `fitness-spec.md`) — ≥ 1.
- agent parity: `find {claude,opencode}/agents -name '*.md' | wc -l` → **38 / 38** (unchanged — Slice 3
  extends the existing orchestrator, adds no agent; `qraspi-builder` still lands in Slice 4 → 39).
- command parity: **18 / 18** (17 → 18; +1 command pair).
- `python3 scripts/add_frontmatter.py` → "0 files updated" (frontmatter complete + well-formed; the
  flat `skills/team/*/` walk reaches the new skill).
- state-tag uniqueness: `<qraspi-architecture-state>` defined only in the new SKILL; orchestrator keeps
  its own `<qraspi-orchestrator-state>` — no collision.
- orchestrator parity: every Architecture addition (skills entry, Available-Skills row, Guardrail 5,
  ARCHITECTURE protocol, self-check, 2 error-recovery paths, state fields, completion criteria) present
  in **both** platform files; sole intended divergence is the protocol skill-load syntax
  (`Load skill …` vs `skill({ name: … })`), matching the existing Q/R pattern.

### Line-budget flag (held deliberately, per the Slice 2 precedent)

`qraspi-architecture/SKILL.md` is **122 lines** — over the ≤100 minimal-tier target, comparable to the
accepted `qraspi-research` overage (112). The bulk that *could* move is already in the 3 references
(MADR template, C4 conventions, fitness spec); the remaining 122 lines are the five phase gates
(research-gate · alternatives · align-loop · fitness-required · context-budget) plus the state block.
Splitting the workflow would hurt legibility more than the lines cost — the same judgment the Slice 2
log made for Research. The Plan (#13) explicitly designates Architecture a heavier phase whose budget
relief is the `fitness-functions` extraction + `references/`. Flagged here, not silently absorbed;
Slice 8 bookkeeping should note the two heavier phases (Architecture, Skeleton) run slightly long.

## Decision note — Guardrail 1 broadened (orchestrator write scope)

Plan #5 puts accepted ADRs in the **target repo's** `docs/adr/NNNN-*.md` (not the qraspi feature
folder), because QRSPI later reads them. The orchestrator previously wrote *only* under
`thoughts/shared/qraspi/…`. Guardrail 1 was broadened so the orchestrator may also **Write** (never
Edit) new `docs/adr/NNNN-*.md` decision records: they are new markdown artifacts, not source, so the
no-Edit edit-seam (#4) still holds — the orchestrator creates files, never mutates source. The
`architecture.md` summary stays in the feature folder and indexes the ADRs. (At Architecture time the
target repo may be near-empty; Slice 4 Skeleton scaffolds source around the same `docs/adr/`.) This is
a deliberate, plan-directed widening, not scope creep — recorded here for Slice 8 Persistent Decisions.

## Deferred (NOT done this slice — by design)

- **Trigger evals** for `qraspi-architecture` (Plan §5) — eval-spec checklist below.
- **Bookkeeping** (README/AGENTS counts, Skill-Suites table, Persistent-Decisions rows incl. the
  Guardrail 1 widening) — all Slice 8 per the session constraints and Plan §6/§7. **Do not interleave.**
- Extending `qraspi-orchestrator` `skills:` for `qraspi-plan` (Slice 5) / `qraspi-graduate` (Slice 7);
  the `qraspi-builder` agent + `qraspi-skeleton` (Slice 4).
- Committing `thoughts/qraspi-plan.md` / `qraspi-research.md` — pre-existing untracked planning
  artifacts; left as-is (same as Slices 1–2).

### Eval-spec checklist (for the later eval-harness session — Plan §5)

`qraspi-architecture` MUST activate on:
- [ ] "write the ADRs for new X"
- [ ] "what architecture for new X" / "C4 for new system X"
- [ ] "/qraspi-architecture X"

`qraspi-architecture` MUST NOT activate on:
- [ ] "architecture review of our existing X" → `architecture-review`
- [ ] "retrospective on the X decision" / "30/90/180-day ADR review" → `architecture-journal`
- [ ] "design the new feature for our existing app" → `/qrspi-spec`
- [ ] "/rpi-plan" / deprecated RPI

Disambiguation focus (Plan §5): vs `architecture-review` + `architecture-journal` (and `qrspi-spec`),
not vs a `qrspi-architecture` (QRSPI has no Architecture phase). The discriminator is greenfield
(new system, lock decisions) vs reviewing/journaling an existing one.

## What the next slice (Slice 4) needs to know

- Q→R→A runs standalone in `qraspi-orchestrator` (no Edit). `architecture.md` exists with: a Summary,
  an **Accepted ADRs index** table, C4 Context + Container (Mermaid), and a **Fitness functions (spec)**
  table. Accepted ADRs live in `<target>/docs/adr/NNNN-*.md`.
- **Slice 4 builds `qraspi-skeleton` + the `qraspi-builder` agent** (has Edit; `skills:[qraspi-skeleton,
  fitness-functions, tdd]`). Skeleton consumes `architecture.md` + the ADRs, selects an archetype, and
  **lands the specified fitness functions as CI gates** — it reads exactly the `Fitness functions (spec)`
  table this slice produced and hands each row to the `fitness-functions` primitive. The CI-green exit
  gate (§4.4) is Slice 4's; this slice produced the contract it enforces.
- State-tag convention extended: …, `<qraspi-architecture-state>` (with `adrs_aligned` +
  `fitness_functions_specified`). Slice 4 adds `<qraspi-skeleton-state>` and the builder's
  `<qraspi-builder-state>`.
- Branch `qraspi-slice-2-questions-research`: Slice 3 changes are staged in the working tree,
  **not yet committed** (commit/branch decision left to the human, same review-locally-first posture
  as Slices 1–2).
