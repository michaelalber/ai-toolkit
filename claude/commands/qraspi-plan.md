---
description: Start the QRASPI Plan phase -- convert the next slice from the skeleton's backlog into a mechanically executable, vertically-sliced plan-{slice}.md grown on the green walking skeleton. Use for "/qraspi-plan <project>". Reads skeleton.md, writes plan-{slice}.md (status ready-for-review). Refuses horizontal-layer plans. To plan a feature in an existing codebase use /qrspi-plan; for the deprecated RPI workflow use /rpi-plan.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRASPI project folders and their artifacts:
!`for d in thoughts/shared/qraspi/*/; do echo "$d"; ls -1 "$d" 2>/dev/null | sed 's/^/  - /'; done 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRASPI **Plan** phase for the new system: $ARGUMENTS

Use the `qraspi-orchestrator` agent (it loads the `qraspi-plan` skill). Locate the project folder
above and read its `skeleton.md` — if it is missing, STOP and route me to `/qraspi-skeleton`. Confirm
`skeleton.md` is `status: complete` **and** `ci_green: true`; if the skeleton is not green, STOP — it
must stand up green before any slice is planned.

Read the **slice backlog** in `skeleton.md` and take the **next unbuilt slice** (default), or the one
I named. Skim the accepted `docs/adr/` and the live **fitness gates** this slice's verification must
keep green. This phase does NOT re-open the architecture — a design change routes back to
`/qraspi-architecture`.

Apply the **RE-SLICE GATE**: if the slice's phases organize by horizontal layer (all models, then all
services, then all UI), STOP and re-slice into end-to-end increments before writing. Then write
`plan-{slice}.md` (`status: ready-for-review`): each phase carries **exact file paths**, a **RED
test step before the GREEN code step**, an **automated verification command** that includes the
skeleton's fitness gates, and a **rollback** line — plus a "What we're NOT doing" list. Report the
slice planned and the remaining backlog count, then tell me to review/approve before
`/qraspi-implement`.

This grows one slice on a NEW system's skeleton. To plan a feature in an existing codebase, use
`/qrspi-plan`.
