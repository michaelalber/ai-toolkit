# ADR Template (MADR) -- greenfield decision lock

The Architecture phase writes one ADR per **path-dependent decision** to the target repo's
`docs/adr/NNNN-kebab-title.md` (default; overridable). MADR is chosen over raw Nygard because the
greenfield phase **requires** alternatives, and "Considered Options" is a MADR addition, not part of
original Nygard. ADRs are written `proposed`, presented for alignment, and only set `accepted` after
the human approves -- they capture the *order* of decisions, so numbering is sequential.

## Filename

`docs/adr/NNNN-present-tense-imperative-dash-case.md` -- e.g. `0001-use-postgres-for-persistence.md`,
`0002-adopt-vertical-slice-architecture.md`. `NNNN` is zero-padded and strictly sequential (adr-tools
convention); the number preserves decision order.

## Template

```markdown
---
adr: NNNN
title: [Short imperative phrase -- the decision, not the topic]
status: proposed   # proposed -> accepted (after human alignment) | superseded by NNNN
date: YYYY-MM-DD
deciders: [roles or names]
qraspi_project: [project-slug]
gated_by: [fitness-function id(s), or "none -- not a measurable quality attribute"]
---

# NNNN. [Title]

## Status
proposed   <!-- set to "accepted" ONLY after the human aligns (qraspi-architecture ALIGN gate) -->

## Context
[The forces at play -- the problem, the constraints from questions.md, the relevant facts from
research.md (cited). Why a decision is needed NOW and why it is expensive to reverse later.]

## Considered Options   <!-- REQUIRED: >= 2 real options, drawn from research's "Options on the table" -->
1. **[Option A]** -- [one-line factual characterization]
2. **[Option B]** -- [one-line factual characterization]
3. **[Option C]** -- [optional]

## Decision
[The chosen option, stated plainly: "We will use X."]

## Rationale
[Why this option over the others -- the trade-off resolution, tied to the project's quality
attributes. This is the content the human redirects during the ALIGN gate.]

## Consequences
**Positive:** [what this buys]
**Negative / accepted trade-offs:** [what it costs -- be honest; a consequence-free ADR is suspect]
**Fitness function:** [if this decision names a measurable quality attribute, the fitness function
that will gate it in CI -- see references/fitness-spec.md. Otherwise "n/a -- qualitative decision".]
```

## Authoring rules

- **>= 2 real options, not strawmen.** The self-check fails any ADR with fewer than 2 Considered
  Options. The alternatives come from research's "Options on the table" -- if research surfaced only
  one, that is an open question to resolve, not a one-option ADR.
- **Proposed before accepted.** Never write `status: accepted` before the ALIGN gate
  (`adrs_aligned: true`). A fait-accompli ADR defeats the phase.
- **Consequences are bidirectional.** Record both what the decision buys and what it costs. An ADR
  with only positive consequences has not weighed the trade-off.
- **Trace to a fitness function.** If the decision names a measurable quality attribute (latency,
  coverage, layer direction, dependency policy), name the fitness function that will enforce it.
- **One decision per ADR.** Bundle nothing. Sequential numbering preserves the decision order that
  makes the path dependency legible to the later Skeleton and QRSPI phases.
