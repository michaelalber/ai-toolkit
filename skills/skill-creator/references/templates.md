# Skill Creator Output Templates

The blank 5-section skill scaffold is in `skill-template.md`. These are the report templates for
REVISE and SCORE modes.

## Revision Diff Summary (REVISE mode)

```markdown
## Skill Revision: <skill-name>

**Date**: <date>
**Mode**: REVISE
**Defects found**: <N>

### Changes Made

| Section | Change | Reason |
|---------|--------|--------|
| [section] | [what changed] | [why] |

### Line Count
Before: <N> lines
After: <N> lines

### State Block Tag
Unchanged: `<<skill-name>-state>` ✓

### Issues Remaining
- [ ] <any unresolved issues>
```

## Scorecard (SCORE mode)

Dimensions and 1–5 criteria are defined in `scoring-rubric.md`.

```markdown
## Skill Quality Scorecard: <skill-name>

| # | Dimension | Score (1–5) | Evidence |
|---|-----------|-------------|---------|
| 1 | Trigger precision | [N] | [evidence from description field] |
| 2 | Core Philosophy + constraints | [N] | [evidence] |
| 3 | Lean layout discipline (≤ 200 lines, 5 sections) | [N] | [evidence] |
| 4 | Workflow completeness | [N] | [evidence] |
| 5 | State block present and unique | [N] | [evidence] |
| 6 | Output template as pointers | [N] | [evidence] |
| 7 | Integration declaration | [N] | [evidence] |
| 8 | References depth (principles/anti-patterns/discipline/recovery) | [N] | [evidence] |
| 9 | Reference hygiene (≥ 2 files, pointed to) | [N] | [evidence] |
| 10 | AI-first phrasing | [N] | [evidence] |
| — | **Total** | **[N]/50** | |

**Verdict**: EXEMPLARY / PASS / REVISE / DEPRECATE

**Critical issues** (blocks correct behavior):
- [issue]

**High issues** (degrades reliability):
- [issue]
```
