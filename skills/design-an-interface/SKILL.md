---
name: design-an-interface
description: >
  Applies "Design It Twice" from APOSD: generates two radically different interface
  designs for the same problem, then compares them on information hiding, complexity,
  and cohesion before recommending one. Use when designing a new API, module boundary,
  or class interface, or asked to "design the interface", "apply design it twice",
  or "compare interface designs".
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Apply the "Design It Twice" principle from *A Philosophy of Software Design* (Ousterhout).

## Protocol

**1. Clarify the problem**

Confirm:
- What does this interface need to do?
- Who are the consumers? How will they call it?
- What complexity must it hide from callers?

**2. Generate Design A** — narrow and deep:
- Expose only what consumers absolutely need
- Push complexity down into the implementation
- Few methods, each with a clear, complete purpose

**3. Generate Design B** — different decomposition:
- Choose a meaningfully different abstraction boundary
- May be more explicit, more composable, or more granular
- Must not be a minor variation of Design A

**4. Compare on these dimensions:**

| Dimension | Design A | Design B |
|-----------|----------|----------|
| Information hiding (1–5, higher=better) | | |
| Method count (lower=simpler) | | |
| Conceptual complexity (1–5, lower=better) | | |
| Cohesion (1–5, higher=better) | | |
| Error surface (1–5, lower=better) | | |
| **Total** | | |

See `references/aposd-principles.md` for scoring guidance on each dimension.

**5. Recommend** — state which design is better and why, citing specific APOSD principles.
If scores are close, propose a hybrid that takes the best of each.

**6. Validate** — ask: "Any constraint or use case I missed that would change this?"
