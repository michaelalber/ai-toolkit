---
name: ubiquitous-language
description: >
  Extracts and formalizes the ubiquitous language from a conversation or codebase.
  Flags ambiguous terms, resolves contradictions, and saves the glossary to
  UBIQUITOUS_LANGUAGE.md. Use when establishing shared vocabulary for a domain,
  after a domain-model session, or asked to "extract the ubiquitous language",
  "build a glossary", or "document the domain terms".
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
disable-model-invocation: true
---

Extract and formalize the domain's ubiquitous language from the current context.

## Steps

**1. Scan** — collect domain terms from:
- This conversation (nouns, verbs, role names, event names, state transitions)
- Class names, method names, variable names in the codebase (if accessible)
- Existing `CONTEXT.md` if present

**2. Classify** each term as:

| Type | Definition |
|------|-----------|
| Entity | Has identity, persists over time |
| Value Object | Defined by attributes, no identity |
| Aggregate | Cluster of objects with one root entity |
| Domain Event | Something that happened — past tense noun |
| Service | Stateless domain operation |
| Command | Intent to change state — imperative verb phrase |
| Policy | Business rule that reacts to an event |

See `references/term-classification.md` for examples of each type.

**3. Flag ambiguities** — surface:
- Terms used inconsistently across the codebase
- Overloaded words (same word, different meanings in different contexts)
- Synonyms for the same concept (pick one, deprecate the rest)

**4. Resolve** — for each ambiguity, ask the user: "Which term should be canonical?"

**5. Save** — write to `UBIQUITOUS_LANGUAGE.md`:

```markdown
# Ubiquitous Language

| Term | Type | Definition | Synonyms to Avoid |
|------|------|-----------|-------------------|
| [Term] | [Type] | [one-sentence definition] | [deprecated synonyms] |
```

**6. Update CONTEXT.md** — if it exists, sync any new or changed terms.

Report: terms added, ambiguities resolved, terms still open.
