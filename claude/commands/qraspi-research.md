---
description: Start the QRASPI Research phase -- map the solution LANDSCAPE for a new system (factual, no recommendations) via research-synthesis (external-domain) or the read-only subagents (inherited-repo). Use for "/qraspi-research <project>". Reads the answered questions.md and writes research.md. For an existing codebase use /qrspi-research instead.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRASPI project folders and their artifacts:
!`for d in thoughts/shared/qraspi/*/; do echo "$d"; ls -1 "$d" 2>/dev/null | sed 's/^/  - /'; done 2>/dev/null || echo "(none yet)"`
</live_state>

Run the QRASPI **Research** phase for the new system: $ARGUMENTS

Use the `qraspi-orchestrator` agent (it loads the `qraspi-research` skill). Locate the project
folder above and read its **answered** `questions.md` to scope the landscape. Detect the mode: with
no codebase at the target use **external-domain** — invoke `research-synthesis` and survey
libraries, prior art, patterns, and constraints with source credibility; with an existing host repo
use **inherited-repo** — pass ONLY a neutral topic to `@research-file-locator`,
`@research-code-analyzer`, and `@research-pattern-finder`, spawned in parallel.

Synthesize a factual **landscape map** — never a recommendation. Convert every comparative judgment
into an open question for the Architecture phase; keep `recommendations_made: false`. Write
`thoughts/shared/qraspi/<project-folder>/research.md` with status `complete`, then tell me to review
before `/qraspi-architecture`.

If no `questions.md` exists for this project, scope the landscape from the argument and note the
gap. This is for a NEW system; to map an existing codebase, use `/qrspi-research` instead.
