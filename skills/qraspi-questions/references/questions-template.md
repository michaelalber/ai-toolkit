# `questions.md` Template

The Questions phase writes this file to the project folder
`thoughts/shared/qraspi/YYYY-MM-DD-{project-slug}/questions.md`. The human answers each question
**inline** (fill the `**A:**` lines) before running `/qraspi-research`.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [target repo name -- may be empty/new at this stage]
topic: "[new system, one line]"
tags: [qraspi, questions, relevant-tag]
phase: Questions (Q)
qraspi_project: [project-slug]
status: awaiting-answers   # -> answered (set by human once all A: lines are filled)
---

# Questions: [New System]

## How to use this file
Answer each question inline on its `**A:**` line. Resolve every [BLOCKING] item before
Research. Leave non-blocking items unanswered only if you accept the agent's stated assumption.

## Open questions

### Functional scope
1. [BLOCKING] [what the system must DO -- the core capability and its boundaries]
   **A:**

### Quality attributes (the -ilities)
2. [which -ilities dominate -- latency, throughput, availability, security, scalability?]
   **A:**

### Integration / external systems
3. [what external systems, APIs, or data sources must it talk to?]
   **A:**

### Compliance / regulatory
4. [any regulatory, data-residency, audit, or licensing constraints?]
   **A:**

### Deployment / runtime target
5. [BLOCKING] [where does it run -- cloud, on-prem, edge device, air-gapped? what stack?]
   **A:**

### Data & domain model
6. [the core domain entities, their relationships, and the source of truth]
   **A:**

## Assumptions (only if not answered above)
- [assumption the agent will make if the matching question is left blank]
```

## Authoring rules
- One concern per question; each must be answerable in a sentence or two.
- **Cover all six categories** -- functional scope, quality attributes, integration, compliance,
  deployment, data & domain. Greenfield has no codebase to backfill a skipped area; ask now.
- Mark `[BLOCKING]` only when architecture genuinely cannot proceed without the answer.
- A category with no obvious question still gets one -- ask whether it applies; do not silently omit.
- Never answer your own questions here; record fallback assumptions in the Assumptions section.
```
