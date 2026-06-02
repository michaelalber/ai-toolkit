# QRSPI 5-Phase ↔ Source 8-Stage Mapping

The QRSPI source workflow defines **8 stages** (5 alignment + 3 execution). This toolkit exposes a
**5-phase** user-facing model (Q-R-S-P-I). This table is the canonical reconciliation so the
source and the implementation cannot drift. `qrspi-spec` owns the two stages that the 5-phase model
collapses into "Spec".

| QRSPI phase (this toolkit) | Skill / agent              | Source stage(s)                          |
|----------------------------|----------------------------|------------------------------------------|
| **Q** — Questions          | `qrspi-questions`          | 1. Questions                             |
| **R** — Research           | `qrspi-research`           | 2. Research (ticket-hidden)              |
| **S** — Spec               | `qrspi-spec`               | **3. Design Discussion + 4. Structure Outline** |
| **P** — Plan               | `qrspi-plan`               | 5. Plan                                  |
| **I** — Implement          | `qrspi-implement` (agent)  | 6. Work Tree + 7. Implement + 8. Pull Request |

## Why Spec combines stages 3 and 4

The source separates **Design Discussion** (stage 3 — the ~200-line brain-dump the engineer
redirects) from **Structure Outline** (stage 4 — signatures, types, and vertically-sliced phases,
"like a C header file"). QRSPI keeps them as **two movements inside one `spec.md`** rather than two
phases because:

- They share one artifact and one human gate; splitting them into two skills would double the
  artifact-handoff overhead for no added control.
- The hard STOP is *between* the movements (the "brain surgery" loop), not between phases — it lives
  inside `qrspi-spec` as the `design_approved` gate.

## The two movements (enforced by the skill)

1. **Design Brain-Dump** (stage 3): current state · desired end state · design decisions. Presented,
   then revised in a loop until the human approves (`design_approved: true`).
2. **Structure Outline** (stage 4): type/function signatures and vertical slices
   (mock-API → front-end → database, one checkpoint per slice). Written only after approval.

## Where the other source stages live

- Stages **1–2** (Questions, Research) are their own QRSPI phases upstream of Spec.
- Stage **5** (Plan) is `qrspi-plan`, which consumes the approved `spec.md`.
- Stages **6–8** (Work Tree, Implement, Pull Request) are absorbed by the `qrspi-implement` agent,
  which drives Red-Green-Refactor per vertical slice and ends at a human-reviewed PR.
