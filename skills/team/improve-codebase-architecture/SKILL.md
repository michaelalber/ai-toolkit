---
name: improve-codebase-architecture
description: >
  Deep module refactoring using APOSD vocabulary: eliminates shallow modules, reduces
  information leakage, resolves temporal coupling, and aligns naming with the ubiquitous
  language. Use when asked to "improve the architecture", "refactor this module",
  "apply APOSD", or "clean up the design". Works best after domain-model is established.
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Improve this codebase's architecture using principles from *A Philosophy of Software
Design* (APOSD) by John Ousterhout.

## Prerequisites

1. Check for `CONTEXT.md` or `UBIQUITOUS_LANGUAGE.md` — load if present.
   These define the canonical vocabulary for all naming decisions.
2. If neither exists: "Domain model not established. Naming recommendations may
   not align with ubiquitous language. Run `domain-model` first for best results."

## Analysis Phase

Find the worst offenders first. Use `references/DEEPENING.md` as a checklist.

1. **Shallow modules** — interfaces that expose more complexity than they abstract.
   Red flag: method count approaches implementation line count.

2. **Information leakage** — implementation details that escape module boundaries.
   Red flag: two modules both know about the same data format, error type, or ordering.

3. **Temporal coupling** — callers that must invoke methods in a specific order.
   Red flag: comments like "call init() before use()" or "must call A before B".

4. **Naming mismatches** — code symbols that contradict the ubiquitous language.
   Red flag: `UserManager`, `DataProcessor`, `Helper` — words that reveal no domain meaning.

## Refactoring Protocol

For each identified issue:

1. Name the problem using APOSD vocabulary (shallow module, information leakage, etc.)
2. Quantify impact: how many call sites are affected?
3. Propose a refactoring using `references/INTERFACE-DESIGN.md` patterns
4. Show before/after: current interface → improved interface
5. Estimate effort: S (hours), M (1–2 days), L (1 week)

Priority order: information leakage → shallow modules → temporal coupling → naming

## Language Alignment

For every rename proposed:
- Verify the new name appears in `CONTEXT.md` or `UBIQUITOUS_LANGUAGE.md`
- If the term is new: add it to `UBIQUITOUS_LANGUAGE.md` first, then rename
- See `references/LANGUAGE.md` for naming anti-patterns to avoid

## Output

```markdown
## Architecture Review: [Module / Package Name]

**Issues found:** [N]

| Issue | Type | Call sites affected | Effort | Priority |
|-------|------|---------------------|--------|----------|
| [name] | Shallow / Info leak / Temporal / Naming | [N] | S/M/L | P1/P2/P3 |

### Proposed Refactorings

#### [Issue name]

**Type:** [APOSD category]
**Before:**
[current interface]

**After:**
[improved interface]

**Rationale:** [APOSD principle cited]
```
