---
name: qa
description: >
  Performs structured QA review of a feature, PR, or implementation: verifies acceptance
  criteria coverage, generates edge case test cases, and flags gaps before shipping.
  Use when asked to "QA this", "review for quality", "write QA test cases",
  "find edge cases", or before marking a feature done.
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Perform structured QA review.

## Protocol

**1. Load acceptance criteria**
From the PRD, issue, or conversation. If none exist:
"I need acceptance criteria before reviewing. Please provide them or run `to-prd` first."

**2. Verify happy path** — for each AC:
- [ ] Is this criterion met by the current implementation?
- [ ] Is there an automated test covering it?

**3. Generate edge case test matrix** — see `references/edge-case-taxonomy.md`:

| Scenario | Input | Expected behavior | Priority |
|----------|-------|------------------|----------|
| Empty / null input | [describe] | [expected] | High |
| Boundary values | [describe] | [expected] | High |
| Invalid format | [describe] | [expected] | High |
| Concurrent access | [describe] | [expected] | Medium |
| Large volume | [describe] | [expected] | Medium |
| Dependency failure | [describe] | [expected] | Medium |

**4. Flag gaps:**
- Acceptance criteria not met by the current implementation
- Missing automated test coverage
- Edge cases with no defined behavior (requires a decision)

**5. Report:**

```markdown
## QA Report: [Feature / PR Name]

**AC coverage:** [N/N met] | [N/N tested]

**Gaps:**
- [ ] [gap + recommended fix or decision needed]

**Edge cases to add:**
- [ ] [test case description]

**Ready to ship:** Yes / No — [reason if No]
```
