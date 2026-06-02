# `research.md` Template

The Research phase writes this to the feature folder
`thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/research.md`. It is **objective only** -- a map
of what exists, with no opinions or design. Every claim cites a file path (ideally `file:line`).

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[neutral topic string -- NOT the ticket wording]"
tags: [qrspi, research, relevant-tag]
git_commit: [short hash]
phase: Research (R)
qrspi_feature: [feature-slug]
status: complete
---

# Research: [neutral topic]

## Research question
[The neutral topic investigated, 1-2 sentences. No feature goal, no desired outcome.]

## Summary
[2-3 paragraph factual overview -- the only section the Spec phase MUST read.]

## Detailed findings
### 1. [Component/area]
[File paths with line references, type signatures, flow descriptions -- facts only.]

### 2. [Next component/area]
...

## Code references
### Core implementation
- `path/to/file` — description
### Integration points
- `path/to/file` — description
### Tests
- `path/to/test` — description

## Key design patterns
1. [Pattern and where it appears -- naming, DI, error handling, test conventions]
2. [Pattern and where it appears]

## Open questions
1. [Human-judgment item -- do not proceed to Spec until resolved]
2. [Unverified assumption, marked UNKNOWN if a path could not be confirmed]
```

## Authoring rules
- **Ticket-hidden:** the `topic` and every heading describe AREAS, not the feature's goal.
- **No opinions:** "the auth layer is messy" is forbidden; "auth spans `A.cs:12`, `B.cs:30`" is
  required. Convert any judgment into an Open question.
- **Cite or cut:** an uncited claim becomes a wrong assumption in Spec -- drop it.
- **Compact:** aim for <= ~200 lines; length is noise.
