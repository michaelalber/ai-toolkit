---
description: Graduate a NEW system from QRASPI (greenfield) to QRSPI (brownfield) -- once the walking skeleton is green and V0/V1 is shipped, capture the repo + ADRs + skeleton state + fitness functions + stack into graduation.md and hand new feature work to QRSPI. Terminal -- do not run mid-workflow. Usage: /qraspi-graduate <project>
agent: qraspi-orchestrator
subtask: true
---

Run the QRASPI **Graduation** handoff for the system: $ARGUMENTS

Load the `qraspi-graduate` skill. Locate the project folder under `thoughts/shared/qraspi/`. Read
`skeleton.md` — confirm `status: complete` **and** `ci_green: true`; if the skeleton is not green, STOP
and route me to `/qraspi-skeleton`. Confirm **V0/V1 is shipped**: `implementation-log-{slice}.md` files
are present for the built slices, or I explicitly confirm V1 is done. If nothing is built yet, STOP —
that is mid-workflow, not graduation.

This phase **captures, it does not decide**. Assemble `graduation.md` (`status: complete`) from what
already exists: (1) the target repo + `docs/adr/` accepted ADRs; (2) the skeleton state — layers
exercised + current CI status; (3) the landed fitness functions and where each gates; (4) the stack
declaration; (5) the **QRSPI handoff instruction**. End with the literal bootstrap step: *"V0/V1 is
shipped. New features now use QRSPI — run `/qrspi-questions` in this repo."*

Report the `graduation.md` path and tell me QRASPI is complete for this system. This is **terminal** —
do not loop back into QRASPI phases. For the next feature in this now-existing codebase, use
`/qrspi-questions`.
