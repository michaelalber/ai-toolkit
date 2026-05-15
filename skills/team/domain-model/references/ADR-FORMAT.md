# ADR Format

Template for Architecture Decision Records created by the `domain-model` skill.
Save to `docs/decisions/ADR-XXXX-[kebab-title].md`.

---

```markdown
# ADR-XXXX: [Short descriptive title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-YYYY
**Deciders:** [names or roles]

## Context

[What is the situation or problem that led to this decision?
Include constraints, forces, and relevant background.
Be specific — "we needed X" is better than "we wanted to improve things".]

## Decision

[The change we are making. State it as an active sentence:
"We will use X because Y."]

## Domain Model Impact

**Bounded context affected:** [ContextName]
**Aggregate affected:** [AggregateName or "none"]
**Ubiquitous language change:** [new term / renamed term / none]

## Consequences

**Positive:**
- [outcome 1]

**Negative:**
- [tradeoff 1]

**Neutral:**
- [side effect 1]

## Alternatives Considered

| Alternative | Why rejected |
|------------|-------------|
| [alt 1] | [reason] |

## References

- [link or document]
```
