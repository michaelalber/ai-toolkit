# RPI, QRSPI/QRASPI & Spec-Driven Development Overview

The following are some of the ways I'm using AI in my daily software development workflow. The
structured-workflow story has three generations: **RPI** (the original, now removed), **QRSPI**
(its instruction-budget-disciplined replacement for *existing* codebases), and **QRASPI** (the
greenfield counterpart for *new* systems). RPI → QRSPI was a replacement; QRSPI ↔ QRASPI are siblings
that meet at a graduation seam.

## RPI (Research-Plan-Implement) — _removed_

> **Deprecated 2026-06-02; removed 2026-06-19.** The four `rpi-*` skills and the
> `rpi-planner`/`rpi-implement` agents were deleted once QRSPI/QRASPI fully replaced them; the early
> sunset pulled the original ~2026-09-01 date forward. The three read-only subagents were renamed
> `research-*` (workflow-neutral) and kept. This section is retained to document the lineage.

A structured workflow that separates complex AI-assisted work into three clean phases — Research,
Plan, Implement — each in its own session with a compact handoff artifact. It worked, but in practice
it leaned on three fragile mechanisms: instruction-budget overflow (frontier models lose consistency
past ~150–200 instructions), magic-word dependencies (the workflow only behaved if you phrased the
request just so), and the plan-reading illusion (a plan that reads well but isn't mechanically
executable). QRSPI exists to fix all three.

---

## QRSPI (Questions-Research-Spec-Plan-Implement) — brownfield

The replacement for RPI, for an **existing codebase / adding a feature**. Correct behavior is the
default through **artifact gates** (no magic words): each phase refuses to run until the prior phase's
artifact exists on disk. The phases:

1. **Questions** — surface what the agent doesn't know; stop for human answers before research.
2. **Research** — ticket-hidden parallel codebase research via the `research-*` subagents; objective
   facts only, no recommendations.
3. **Spec** — Design Brain-Dump → human "brain-surgery" alignment loop → vertical-slice Structure Outline.
4. **Plan** — convert the spec into a vertically-sliced, file-precise tactical plan; refuse horizontal-layer plans.
5. **Implement** — execute the approved plan slice-by-slice with strict Red-Green-Refactor, checkpointing per slice.

Driven by the `qrspi-orchestrator` (no-edit alignment) and `qrspi-implement` (edit execution) agents.
Artifacts co-locate in `thoughts/shared/qrspi/YYYY-MM-DD-{slug}/`.

---

## QRASPI (Questions-Research-Architecture-Skeleton-Plan-Implement) — greenfield

The greenfield (V0/V1) counterpart, for a **new system from scratch**. Where QRSPI maps an existing
codebase and grows a feature, QRASPI maps a problem domain, locks the path-dependent decisions early,
lands an executable walking skeleton, then grows V1 on top of it. The phases:

1. **Questions** — surface unknowns across the six greenfield categories (functional scope · quality
   attributes · integration · compliance · deployment · data & domain); stop for human answers.
2. **Research** — map the solution landscape (external-domain via `research-synthesis`, or
   inherited-repo via the `research-*` subagents); factual, no premature recommendations.
3. **Architecture** — lock the path-dependent decisions as **MADR ADRs with ≥ 2 alternatives**
   (align-before-lock gate), draw the **C4 Context + Container in Mermaid**, and specify the required
   **fitness functions**. Accepted ADRs live in the target repo's `docs/adr/`.
4. **Skeleton** — scaffold a **runnable walking skeleton** from the ADRs (one vertical slice through
   every layer) and land the fitness functions as merge-blocking CI gates. The exit gate is **CI
   green**, not a claim.
5. **Plan** — convert the next slice from the skeleton's backlog into a vertically-sliced
   `plan-{slice}.md`; refuse horizontal-layer plans.
6. **Implement** — grow the green skeleton one approved slice at a time with Red-Green-Refactor,
   keeping the fitness gates green.

Driven by two agents split by **edit access**: `qraspi-orchestrator` (no-edit:
Questions/Research/Architecture/Plan/Graduate) and `qraspi-builder` (edit: Skeleton/Implement).
Artifacts co-locate in `thoughts/shared/qraspi/YYYY-MM-DD-{slug}/`. QRASPI's one extracted primitive
is `fitness-functions` (architectural CI gates); ADR-writing, C4, and walking-skeleton scaffolding are
folded into the phase skills.

### Graduation: QRASPI → QRSPI

QRASPI is V0/V1 only. Once the walking skeleton is green and the first real slices are shipped, the
system is no longer greenfield — new features are additions to an existing codebase, which is QRSPI's
job. The **`qraspi-graduate`** terminal phase makes the seam explicit: it writes a `graduation.md` that
captures the repo, the accepted ADRs, the skeleton state, the live fitness gates, and the stack, then
hands off with the literal instruction to run `/qrspi-questions` in the same repo. Both workflows
already share `tdd`, vertical slices, and the `research-*` subagents, so the seam is state capture +
documentation, not new machinery.

---

## Spec-Driven Development

A discipline of writing explicit behavioral specifications for AI agents and skills *before* building
them — defining vision, boundaries, success criteria, and failure modes upfront. This prevents "it
kind of works" from being mistaken for "it's done." The QRSPI Spec phase and the QRASPI Architecture
phase are this discipline applied inside the structured workflows; `spec-coach` is the interactive
front door for designing a new skill, agent, or PRD from first principles.

---

## Skills

| Skill | Workflow | Summary |
|---|---|---|
| `qrspi-questions` … `qrspi-implement` | QRSPI (brownfield) | Five phase skills: Questions, Research, Spec, Plan, Implement. Artifact-gated, ticket-hidden research, vertical-slice plans, per-slice Red-Green-Refactor. |
| `qraspi-questions` … `qraspi-graduate` | QRASPI (greenfield) | Seven phase/handoff skills: Questions, Research, Architecture, Skeleton, Plan, Implement, Graduate. MADR ADRs, Mermaid C4, runnable walking skeleton, CI-green gate. |
| `fitness-functions` | QRASPI primitive | Authors architectural fitness functions and wires them into CI as merge-blocking gates (NetArchTest, import-linter, cargo-deny, Conftest). |
| `spec-coach` | Spec-driven | Interactive specification of a new AI skill, agent, or PRD from first principles. |

## Agents

| Agent | Workflow | Summary |
|---|---|---|
| `qrspi-orchestrator` | QRSPI | No-edit alignment orchestrator for Questions/Research/Spec/Plan. |
| `qrspi-implement` | QRSPI | Edit-access execution agent; per-slice Red-Green-Refactor. |
| `qraspi-orchestrator` | QRASPI | No-edit orchestrator for Questions/Research/Architecture/Plan and the terminal Graduation handoff. |
| `qraspi-builder` | QRASPI | Edit-access builder for the Skeleton (scaffold + CI-green) and Implement (per-slice RGR) phases. |
| `research-file-locator` / `research-code-analyzer` / `research-pattern-finder` | shared | Read-only subagents spawned in parallel for codebase research; reused by both QRSPI and QRASPI. |
| `spec-extractor-agent` | Spec-driven | Analyzes an existing codebase to produce a pre-filled draft agent spec, used before a `spec-coach` session. |
