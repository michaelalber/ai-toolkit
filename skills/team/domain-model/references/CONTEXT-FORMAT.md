# CONTEXT.md Format

Template for the `CONTEXT.md` file in a project root. This file is the authoritative
domain vocabulary for the `domain-model` skill. All code naming should align with it.

---

```markdown
# Domain Context: [Project/System Name]

## Bounded Contexts

| Context | Responsibility | Core Aggregates | Upstream / Downstream |
|---------|---------------|-----------------|----------------------|
| [ContextName] | [What it owns] | [Aggregate1, Aggregate2] | upstream: [X] / downstream: [Y] |

## Ubiquitous Language

| Term | Type | Definition | Synonyms to Avoid |
|------|------|-----------|-------------------|
| [Term] | Entity/VO/Aggregate/Event/Service/Command | [one-sentence definition] | [deprecated synonyms] |

## Key Aggregates

### [AggregateName]

**Root entity:** [EntityName]
**Invariants:**
- [rule that must always hold]

**Domain events emitted:**
- [EventName] — when [trigger]

## Context Map

```
[ContextA] --[relationship]--> [ContextB]
```

Relationships: Shared Kernel | Customer-Supplier | Conformist | Anti-Corruption Layer | Open Host | Published Language

## Anti-Corruption Layer Notes

[Any translation logic between external models and this domain's model]

## Open Questions

- [ ] [unresolved domain question]
```
