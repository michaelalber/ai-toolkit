---
name: qrspi-research
audience: team
description: >
  QRSPI Research phase -- objective, ticket-hidden codebase mapping via parallel read-only
  subagents. Use for "/qrspi-research <feature>", "qrspi research X", "ticket-hidden research",
  "map what exists for X before designing". Do NOT use for the deprecated RPI workflow
  ("/rpi-research", "rpi research X") -- that routes to rpi-research, a different workflow.
---

# QRSPI Research

> "Research is what I'm doing when I don't know what I'm doing."
> -- Adapted from Wernher von Braun

## Core Philosophy

The Research phase maps what the codebase ACTUALLY contains -- never what the feature wants. Do
not load the ticket or feature description into context. Research what EXISTS, not what the
feature needs: loading the goal biases the map toward a predetermined design, the exact failure
QRSPI exists to prevent. The phase runs three read-only subagents in parallel, each on a neutral
topic string, and synthesizes one objective artifact.

**Non-Negotiable Constraints:**
1. TICKET-HIDDEN -- never load the ticket or feature description; derive a NEUTRAL topic string
   (areas and component names only) and pass ONLY that to the subagents
2. OBJECTIVE only -- no opinions, recommendations, or design; facts with file:line citations
3. PARALLEL subagents -- spawn `research-file-locator`, `research-code-analyzer`, and
   `research-pattern-finder` concurrently via the Task tool; never serially
4. CITE every claim -- if you cannot cite a file, drop the claim
5. CONTEXT BUDGET: keep utilization under 40%. At 60%, write `research.md` with progress and
   tell the user to start a fresh session.

## Workflow

```
PRE-FLIGHT
    [ ] Locate the feature folder thoughts/shared/qrspi/YYYY-MM-DD-{slug}/
    [ ] Read the ANSWERED questions.md to derive a NEUTRAL topic string (areas/components only)
        -> If no questions.md exists, derive the neutral topic from the argument and note the gap
    [ ] Record the current commit: git log --oneline -1

DELEGATE (parallel)
    Spawn concurrently via the Task tool, passing ONLY the neutral topic string:
      @research-file-locator   -- "Find all files related to: {neutral topic}"
      @research-code-analyzer  -- "Analyze the implementation of: {neutral topic}"
      @research-pattern-finder -- "Find patterns and conventions related to: {neutral topic}"
    Wait for ALL THREE before synthesizing

SYNTHESIZE
    De-duplicate file references; organize into overview, findings, code references, patterns,
    open questions. Convert any opinion into an open question. Compact to <= ~200 lines.

WRITE
    thoughts/shared/qrspi/YYYY-MM-DD-{slug}/research.md   (references/research-template.md)
    Set status: complete

REPORT
    Artifact path · 3-5 key findings · open questions ·
    "Review, then start a NEW session and run /qrspi-spec"
```

**Exit criteria:** `research.md` written objective-only; all three subagent outputs incorporated;
every claim cites a file; open questions surfaced; user told to review before `/qrspi-spec`.

## State Block

```
<qrspi-research-state>
phase: PRE-FLIGHT | DELEGATE | SYNTHESIZE | WRITE | REPORT | COMPLETE
feature_folder: thoughts/shared/qrspi/YYYY-MM-DD-{slug}/
neutral_topic: [ticket-free topic string]
ticket_loaded: false        # MUST remain false -- the firewall
subagents_spawned: 0 | 1 | 2 | 3
subagents_complete: 0 | 1 | 2 | 3
open_questions: [count]
context_budget: under-40 | approaching-60 | checkpoint-now
status: in_progress | complete
</qrspi-research-state>
```

## Output Template

See `references/research-template.md` for the full `research.md` structure and frontmatter.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `qrspi-questions` | Prior phase. Its answered `questions.md` is the neutral topic source. |
| `qrspi-spec` | Next phase. Consumes `research.md` as the factual ground for design. |
| `research-synthesis` | For research beyond the codebase (external systems, libraries): source credibility scoring and cross-referencing. |
| `rpi-research` | DEPRECATED sibling with the same parallel-subagent mechanic. Route here for QRSPI; do not invoke the RPI version. |
