---
description: Start the QRASPI Research phase -- map the solution landscape for a new system, factual, no recommendations. Usage: /qraspi-research <project>
agent: qraspi-orchestrator
subtask: true
---

Run the QRASPI **Research** phase for the new system: $ARGUMENTS

Load the `qraspi-research` skill. Locate the project folder under `thoughts/shared/qraspi/` and read
its **answered** `questions.md` to scope the landscape. Detect the mode: with no codebase at the
target use **external-domain** — invoke `research-synthesis` and survey libraries, prior art,
patterns, and constraints with source credibility; with an existing host repo use **inherited-repo**
— pass ONLY a neutral topic to `@research-file-locator`, `@research-code-analyzer`, and
`@research-pattern-finder`, spawned in parallel.

Synthesize a factual **landscape map** — never a recommendation. Convert every comparative judgment
into an open question for the Architecture phase; keep `recommendations_made: false`. Write
`thoughts/shared/qraspi/<project-folder>/research.md` with status `complete`, then tell me to review
before `/qraspi-architecture`.

If no `questions.md` exists for this project, scope the landscape from the argument and note the
gap. This is for a NEW system; to map an existing codebase, use `/qrspi-research` instead.
