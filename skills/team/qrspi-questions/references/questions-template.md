# `questions.md` Template

The Questions phase writes this file to the feature folder
`thoughts/shared/qrspi/YYYY-MM-DD-{feature-slug}/questions.md`. The human answers each question
**inline** (fill the `**A:**` lines) before running `/qrspi-research`.

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [repo name]
topic: "[feature, one line]"
tags: [qrspi, questions, relevant-tag]
git_commit: [short hash]
phase: Questions (Q)
qrspi_feature: [feature-slug]
status: awaiting-answers   # -> answered (set by human once all A: lines are filled)
---

# Questions: [Feature]

## How to use this file
Answer each question inline on its `**A:**` line. Resolve every [BLOCKING] item before
Research. Leave non-blocking items unanswered only if you accept the agent's stated assumption.

## Open questions

### Data model
1. [BLOCKING] [specific question]
   **A:**

### API contract
2. [specific question]
   **A:**

### UI / UX
3. [specific question]
   **A:**

### Integration points
4. [specific question]
   **A:**

### Auth / permissions
5. [specific question]
   **A:**

### Testing
6. [specific question]
   **A:**

### Edge cases
7. [specific question]
   **A:**

### Migration / rollout
8. [specific question]
   **A:**

## Assumptions (only if not answered above)
- [assumption the agent will make if the matching question is left blank]
```

## Authoring rules
- One concern per question; each must be answerable in a sentence or two.
- Mark `[BLOCKING]` only when design genuinely cannot proceed without the answer.
- Omit an area heading entirely if the feature provably cannot touch it -- do not pad.
- Never answer your own questions here; record fallback assumptions in the Assumptions section.
