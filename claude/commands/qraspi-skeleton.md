---
description: Start the QRASPI Skeleton phase -- stand up a RUNNABLE walking skeleton for a new system from the accepted ADRs. Scaffold the repo, walk one vertical slice end-to-end, land the specified fitness functions as CI gates, and prove it with a real CI run (exit 0). Use for "/qraspi-skeleton <project>". Reads architecture.md + docs/adr/, writes a runnable repo + skeleton.md. To scaffold a single feature slice in an existing repo use the *-feature-slice scaffolders; for QRSPI (existing codebase) use /qrspi-implement.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRASPI project folders and their artifacts:
!`for d in thoughts/shared/qraspi/*/; do echo "$d"; ls -1 "$d" 2>/dev/null | sed 's/^/  - /'; done 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRASPI **Skeleton** phase for the new system: $ARGUMENTS

Use the `qraspi-builder` agent (it loads the `qraspi-skeleton` and `fitness-functions` skills). Locate
the project folder above and read its `architecture.md` (`status: complete`) plus the accepted
`docs/adr/NNNN-*.md` — if architecture is missing or not complete, STOP and route me to
`/qraspi-architecture`. The stack comes from the ADRs; never invent it.

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
