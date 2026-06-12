---
description: Start the QRSPI Research phase -- objective, ticket-hidden codebase mapping via parallel read-only subagents. Use for "/qrspi-research <feature>". Reads the answered questions.md and writes research.md. Distinct from the deprecated /rpi-research.
allowed-tools: Bash(ls:*), Bash(date:*), Read
---

<live_state>
Today: !`date +%Y-%m-%d`
QRSPI feature folders and their artifacts:
!`find thoughts/shared/qrspi -mindepth 1 -maxdepth 2 2>/dev/null | sort || echo "(none yet)"`
</live_state>

Run the QRSPI **Research** phase for: $ARGUMENTS

Use the `qrspi-orchestrator` agent (it loads the `qrspi-research` skill). Locate the feature
folder above and read its **answered** `questions.md` to derive a NEUTRAL topic string. Keep the
ticket hidden: pass ONLY the neutral topic to `@research-file-locator`,
`@research-code-analyzer`, and `@research-pattern-finder`, spawned in parallel. Synthesize their
findings objective-only (no opinions, every claim cited) into
`thoughts/shared/qrspi/<feature-folder>/research.md` with status `complete`, then tell me to
review before `/qrspi-spec`.

If no `questions.md` exists for this feature, derive the neutral topic from the argument and note
the gap.
