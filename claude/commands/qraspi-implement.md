---
description: Start the QRASPI Implement phase -- grow the green walking skeleton ONE approved slice at a time with strict Red-Green-Refactor per phase, keeping the skeleton's fitness gates green. Use for "/qraspi-implement <project>". Reads plan-{slice}.md (status approved) + skeleton.md (ci_green), writes implementation-log-{slice}.md. To implement a feature in an existing codebase use /qrspi-implement; for the deprecated RPI workflow use /rpi-implement.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRASPI project folders and their artifacts:
!`for d in thoughts/shared/qraspi/*/; do echo "$d"; ls -1 "$d" 2>/dev/null | sed 's/^/  - /'; done 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRASPI **Implement** phase for the new system: $ARGUMENTS

Use the `qraspi-builder` agent (it loads the `qraspi-implement` and `tdd` skills). Locate the project
folder above. Read `skeleton.md` — confirm `status: complete` **and** `ci_green: true`; if the skeleton
is not green, STOP and route me to `/qraspi-skeleton`. Read `plan-{slice}.md` for the target slice — if
absent, STOP and route me to `/qraspi-plan`; confirm it is `status: approved` (not merely
ready-for-review). Then run the **baseline suite** (tests + the skeleton's fitness gates); a red
baseline is a STOP, not yours to fix.

Execute the phases inside `plan-{slice}.md` **in order**, one vertical increment at a time, delegating
the inner loop to `tdd`: **RED** (write the failing test, RUN it, confirm it FAILS) → **GREEN** (minimal
code; RUN build + tests + the fitness gates; ALL must pass) → **REFACTOR** (stays green). The skeleton's
fitness gates are part of GREEN — a change that trips a gate is not done; fix it, never disable the gate.
**RECORD** each phase's RED and GREEN output to `implementation-log-{slice}.md`, then suggest a commit.
If anything is not in the plan, STOP and re-run `/qraspi-plan` (or `/qraspi-architecture` for a design
change) — never improvise.

When the slice is green and recorded, report phases complete/total and point me to the next backlog
slice (`/qraspi-plan`) or to `/qraspi-graduate` if every backlog slice is built.

This grows a NEW system's skeleton. To implement a feature in an existing codebase, use
`/qrspi-implement`.
