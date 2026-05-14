---
name: to-prd
description: >
  Converts meeting notes, feature requests, or conversation context into a structured
  Product Requirements Document (PRD) with goals, user stories, and binary acceptance
  criteria. Use when asked to "write a PRD", "turn this into a product spec",
  "create requirements", or "document this feature".
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Convert the provided context into a structured PRD.

## Instructions

1. Read all provided context (conversation, notes, requirements).
2. Ask any clarifying questions in one batch before writing — not one at a time.
3. Write the PRD following the template in `references/prd-template.md`.
4. Present it and ask: "Anything missing or wrong before we break this into issues?"

## Key constraints

- Acceptance criteria must be binary (pass/fail), specific, and verifiable by an
  independent observer without asking clarifying questions.
- Non-goals are as important as goals — explicitly scope what is out of bounds.
- Open Questions must be resolved before implementation begins — flag any that block
  acceptance criteria from being written.

See `references/acceptance-criteria-guide.md` for guidance on writing good ACs.
