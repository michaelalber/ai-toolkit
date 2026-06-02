# `research.md` Template

The Research phase writes this to the project folder
`thoughts/shared/qraspi/YYYY-MM-DD-{project-slug}/research.md`. It is a **factual landscape map**
-- what EXISTS in the solution space, with no recommendation. Every claim carries a citation
(external-domain: a source + credibility note; inherited-repo: `file:line`).

```markdown
---
date: YYYY-MM-DDTHH:MM:SS
repository: [target repo name -- may be empty/new in external-domain mode]
topic: "[solution-landscape area -- NOT a chosen solution]"
tags: [qraspi, research, relevant-tag]
phase: Research (R)
qraspi_project: [project-slug]
research_mode: external-domain | inherited-repo
status: complete
---

# Research: [solution-landscape area]

## Research question
[The landscape area investigated, 1-2 sentences. No chosen stack, no desired outcome.]

## Summary
[2-3 paragraph factual overview of the solution space -- the only section Architecture MUST read.]

## Landscape findings
### 1. [Option / library / pattern / prior art]
[What it IS, where it is documented or used, its stated constraints -- facts only, cited.]

### 2. [Next option / area]
...

## Options on the table
[A neutral enumeration of the candidate approaches surfaced -- NOT ranked, NOT chosen. Each line
is a candidate Architecture will weigh as an ADR with alternatives.]
- [candidate A] — [one-line factual characterization, cited]
- [candidate B] — [one-line factual characterization, cited]

## Constraints discovered
- [hard constraint from the domain, regulation, or host repo -- cited]

## Open questions
1. [Every comparative judgment goes here as a question for Architecture to decide -- never a pick]
2. [Unverified assumption, marked UNKNOWN if a source/path could not be confirmed]
```

## Authoring rules
- **Landscape, not verdict:** "X is the best fit" is forbidden; "X and Y both support Z; trade-off
  is an open question for Architecture" is required. Convert every comparison into an Open question.
- **No premature solution:** do not select a stack, framework, or library. That is Architecture's
  job, behind an ADR with alternatives.
- **Cite or cut:** external-domain claims carry a source and credibility note; inherited-repo claims
  carry `file:line`. Uncited -> drop it.
- **Compact:** aim for <= ~200 lines; length is noise.
```
