---
name: triage-issue
description: >
  Triages a GitHub Issue or bug report: classifies severity, identifies the likely
  root cause area, suggests reproduction steps, and recommends priority and owner.
  Use when asked to "triage this issue", "assess this bug", "classify this report",
  or given a bug report to evaluate.
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Triage the provided issue or bug report.

## Output

```markdown
### Triage: [Issue Title]

**Severity:** Critical | High | Medium | Low
**Type:** Bug | Regression | Performance | UX | Docs | Security
**Reproducible:** Yes | No | Unknown
**Affected area:** [module / feature / layer]

**Likely root cause:**
[1–2 sentences identifying the probable failure point]

**Reproduction steps:**
1. [step]
2. [step]
Expected: [X] — Actual: [Y]

**Priority:** P0 / P1 / P2 / P3
**Priority reason:** [why this priority, not higher or lower]

**Suggested owner:** [team or role, not a specific person]
**Suggested approach:** [1–2 sentence direction — not a full solution]
```

See `references/severity-matrix.md` for severity and priority definitions.
See `references/root-cause-taxonomy.md` for common root cause categories.
