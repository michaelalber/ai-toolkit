---
description: Start the QRSPI Research phase (objective, ticket-hidden codebase mapping). Usage: /qrspi-research <feature>
agent: qrspi-orchestrator
subtask: true
---

Run the QRSPI **Research** phase for: $ARGUMENTS

Load the `qrspi-research` skill. Locate the feature folder under `thoughts/shared/qrspi/` and read
its **answered** `questions.md` to derive a NEUTRAL topic string. Keep the ticket hidden: pass
ONLY the neutral topic to `@research-file-locator`, `@research-code-analyzer`, and
`@research-pattern-finder`, spawned in parallel. Synthesize their findings objective-only (no
opinions, every claim cited) into `thoughts/shared/qrspi/<feature-folder>/research.md` with status
`complete`, then tell me to review before `/qrspi-spec`.

If no `questions.md` exists for this feature, derive the neutral topic from the argument and note
the gap.
