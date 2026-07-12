---
name: codebase-design
audience: team
source: mattpocock/skills
source_commit: unknown
source_note: "Modified locally — see .matt-pocock-attribution.yml for details"
description: >
  Shared vocabulary for designing deep modules — a lot of behaviour behind a small
  interface, placed at a clean seam, testable through that interface. Use when designing
  or improving a module's interface, finding deepening opportunities, deciding where a
  seam goes, making code more testable, or when another skill needs the deep-module
  vocabulary. Pairs with improve-codebase-architecture (which applies it) and domain-model
  (which supplies the domain nouns). Ported from https://github.com/mattpocock/skills (Matt Pocock).
disable-model-invocation: true
---

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean
seam, testable through that interface. Use this language and these principles wherever code
is being designed or restructured. The aim is leverage for callers, locality for
maintainers, and testability for everyone.

## Glossary

Use these terms exactly — don't substitute "component," "service," "API," or "boundary."
Consistent language is the whole point.

- **Module** — anything with an interface and an implementation. Scale-agnostic: a function,
  class, package, or tier-spanning slice. *Avoid*: unit, component, service.
- **Interface** — everything a caller must know to use the module correctly: the type
  signature, plus invariants, ordering constraints, error modes, required configuration,
  and performance characteristics. *Avoid*: API, signature (too narrow — type-level only).
- **Implementation** — what's inside a module, its body of code. Distinct from **Adapter**:
  a thing can be a small adapter with a large implementation (a Postgres repo) or a large
  adapter with a small implementation (an in-memory fake). Say "adapter" when the seam is
  the topic; "implementation" otherwise.
- **Depth** — leverage at the interface: how much behaviour a caller (or test) can exercise
  per unit of interface they must learn. **Deep** = large behaviour behind a small
  interface. **Shallow** = interface nearly as complex as the implementation.
- **Seam** *(Michael Feathers)* — a place where you can alter behaviour without editing in
  that place; the *location* at which a module's interface lives. Where the seam goes is its
  own design decision. *Avoid*: boundary (overloaded with DDD's bounded context).
- **Adapter** — a concrete thing that satisfies an interface at a seam. Names a *role* (the
  slot it fills), not its substance.
- **Leverage** — what callers get from depth: more capability per unit of interface learned.
  One implementation pays back across N call sites and M tests.
- **Locality** — what maintainers get from depth: change, bugs, knowledge, and verification
  concentrate in one place instead of spreading across callers. Fix once, fixed everywhere.

## Deep vs shallow

**Deep** = small interface + lots of implementation. **Shallow** = large interface + thin
implementation (avoid).

```
  DEEP  [ small interface ]     SHALLOW  [ large interface ]
        [                 ]              [ thin impl        ]
        [   deep impl     ]        ← interface ≈ implementation (avoid)
        [   (hidden)      ]
```

When designing an interface, ask: Can I reduce the number of methods? Can I simplify the
parameters? Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be
  internally composed of small, mockable parts — they just aren't part of the interface. A
  module can have **internal seams** (private to its tests) as well as the **external seam**
  at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a
  pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you need
  to test *past* the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce
  a seam unless something actually varies across it.

## Designing for testability

Good interfaces make testing natural: **accept dependencies, don't create them** (pass
`paymentGateway` in); **return results, don't produce side effects** (`calculateDiscount(cart):
Discount` over a mutating `applyDiscount`); **keep the surface small** (fewer methods and params
= fewer, simpler tests). Worked examples in `references/DESIGN-NOTES.md`.

## Going deeper

- Testability examples, rejected framings, and the relational vocabulary map —
  `references/DESIGN-NOTES.md`.
- Deepening a cluster given its dependencies — `references/DEEPENING.md` (dependency
  categories, seam discipline, replace-don't-layer testing).
- Exploring alternative interfaces — `references/DESIGN-IT-TWICE.md` (parallel sub-agents
  design the interface several radically different ways, then compare on depth and locality).

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `improve-codebase-architecture` | Applies this vocabulary — surfaces shallow modules, information leakage, and deepening candidates. This skill supplies the words it names them with. |
| `domain-model` | Supplies domain nouns (ubiquitous language); this skill supplies module-shape nouns (depth, seam, adapter). They compose — domain names *what*, this names *how it's shaped*. |
| `refactor-challenger` | Prioritises which deepenings to actually perform; this skill frames the target shape. |
