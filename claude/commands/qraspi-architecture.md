---
description: Start the QRASPI Architecture phase -- lock the path-dependent decisions for a new system as MADR ADRs with alternatives, draw the C4 Context + Container in Mermaid, and specify the required fitness functions. Use for "/qraspi-architecture <project>". Reads research.md and writes docs/adr/NNNN-*.md + architecture.md. To review an EXISTING system's architecture use architecture-review; to design a feature in an existing codebase use /qrspi-spec.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRASPI project folders and their artifacts:
!`find thoughts/shared/qraspi -mindepth 1 -maxdepth 2 2>/dev/null | sort || echo "(none yet)"`
</live_state>

Run the QRASPI **Architecture** phase for the new system: $ARGUMENTS

Use the `qraspi-orchestrator` agent (it loads the `qraspi-architecture` skill). Locate the project
folder above and read its `research.md` (`status: complete`) — if it is missing, STOP and route me to
`/qraspi-research`. Read the answered `questions.md` for quality attributes and hard constraints. If
the domain is complex, optionally invoke `domain-model` first to produce a `CONTEXT.md` the ADRs
reference.

This is where the **picks happen**. Draft one **MADR ADR per path-dependent decision** in
`<target>/docs/adr/NNNN-kebab-title.md`, each with **>= 2 Considered Options** drawn from research's
"Options on the table", written `status: proposed`. Draft `architecture.md` with the **C4 Context +
Container in Mermaid**. Then **STOP and present** the proposed ADRs + C4 for alignment; loop on my
redirection and set `status: accepted` only after I approve (`adrs_aligned: true`).

For every accepted ADR that names a measurable quality attribute, **specify >= 1 fitness function**
in `architecture.md` (attribute · threshold · candidate tool · ADR id) — authoring/wiring is the
`fitness-functions` primitive's job in the Skeleton phase; `fitness_functions_specified` must be > 0.
Write `architecture.md` (`status: complete`, indexing the accepted ADRs), then tell me to review
before `/qraspi-skeleton`.

This is for a NEW system. To review or critique an existing system's architecture, use
`architecture-review`; to design a feature in an existing codebase, use `/qrspi-spec`.
