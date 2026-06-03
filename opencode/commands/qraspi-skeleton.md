---
description: Start the QRASPI Skeleton phase -- stand up a runnable walking skeleton for a new system from the accepted ADRs. Scaffold the repo, walk one vertical slice end-to-end, land the fitness functions as CI gates, prove it with a real CI run (exit 0). Usage: /qraspi-skeleton <project>
agent: qraspi-builder
subtask: false
---

Run the QRASPI **Skeleton** phase for the new system: $ARGUMENTS

Load the `qraspi-skeleton` skill. Locate the project folder under `thoughts/shared/qraspi/` and read
its `architecture.md` (`status: complete`) plus the accepted `docs/adr/NNNN-*.md` — if architecture is
missing or not complete, STOP and route me to `/qraspi-architecture`. The stack comes from the ADRs;
never invent it.

**Detect the archetype** by matching the ADR stack declaration to a recipe
(`python-mcp-server`, `dotnet-blazor-vertical-slice`, `python-fastapi-service`, `edge-ai-device`,
`eval-harness`, or the generic recipe). **Scaffold a runnable repo**: the archetype supplies the
repo+CI+observability+secure-by-default layer; invoke the matching `*-feature-slice`/`*-scaffold` skill
for the **one** vertical slice that walks every layer end-to-end. Recipes are instructions to adapt to
the ADRs, not templates to copy verbatim.

**Land the fitness functions:** for each one specified in `architecture.md`, use the `fitness-functions`
skill to author it and wire it into CI as a merge-blocking gate. Then **VERIFY with a real command** —
run the project's CI / test suite and require **exit 0** (build + unit + lint + fitness gates all
green). `ci_green` is the captured exit status; do not report COMPLETE with `ci_green: false`. For a
hardware archetype, CI-green covers the host-runnable gates and the device-deploy step is a documented
manual gate.

Write `skeleton.md` (`status: complete`) with the CI status and a **slice backlog** for `/qraspi-plan`,
suggest a commit, and tell me to review before `/qraspi-plan`.

This stands up V0 of a NEW system. To scaffold a single feature slice in an existing repo, use a
`*-feature-slice` scaffolder; for a feature in an existing codebase (QRSPI), use `/qrspi-implement`.
