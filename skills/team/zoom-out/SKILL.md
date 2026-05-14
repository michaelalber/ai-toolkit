---
name: zoom-out
description: >
  Zooms out from the current code to map callers, dependents, and module relationships
  before continuing. Use when entering unfamiliar code, debugging a confusing call chain,
  or asked to "zoom out", "map the context", or "show me the bigger picture".
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
disable-model-invocation: true
---

Before continuing with the immediate task, orient yourself in the codebase:

1. Identify the current file and function being worked on.
2. Find all callers of the current function or consumers of the current module.
3. Trace one level up — what orchestrates this code? What domain concept does it serve?
4. Identify the module's public API boundary: what does it expose, what does it hide?
5. Note any cross-cutting concerns (logging, error handling, auth) that flow through.

Report a map:

- **Current location:** `file:line` — function/class name and one-line purpose
- **Callers:** list of call sites with context
- **Module role:** what problem this module solves in the broader system
- **Dependencies:** what this module depends on and what depends on it

Once the map is complete, resume the original task with this context in view.

See `references/orientation-checklist.md` for a thorough orientation guide on large codebases.
