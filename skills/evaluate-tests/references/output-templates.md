# Output Templates

Both report templates for `evaluate-tests`. Relocated verbatim from SKILL.md during the
lean-layout migration (2026-11-12).

## Mode 1 — Test Evaluation Report

```markdown
## Test Evaluation: [file or suite name]

### Summary
Tests evaluated: N | PASS: N | COUPLED: N | FRAGILE: N | THEATER: N

### Prioritized Rewrite List

| Priority | Test | Class | Reason | Suggested Fix |
|----------|------|-------|--------|---------------|
| 1 | `test_name` | COUPLED | Asserts `repo.save.called` — tests the how, not the what | Assert `repo.find(id) is not None` instead |
| 2 | `test_name` | FRAGILE | Reads `user._email` directly | Assert via `user.get_profile()["email"]` |
| 3 | `test_name` | THEATER | No assertion — only calls the method | Add assertion on return value or observable state |

### Horizontal Slice Signals
[commit evidence or "not detectable from test file alone — run Mode 2 (commit history)"]
```

## Mode 2 — TDD Compliance Scorecard

```markdown
## TDD Compliance Scorecard: [repo/branch]
**Period**: [date range] | **Commits analyzed**: N

| Category | Score | Status |
|----------|-------|--------|
| Test-First Development | X/5 | GREEN/YELLOW/RED |
| Behavioral Testing | X/5 | GREEN/YELLOW/RED |
| Minimal Implementation | X/5 | GREEN/YELLOW/RED |
| Refactoring Discipline | X/5 | GREEN/YELLOW/RED |
| Coverage Quality | X/5 | GREEN/YELLOW/RED |
**Overall**: X/25 ([percentage]%)

Anti-patterns: [list or "none"]
Recommendations: Immediate: [...] | Short-term: [...] | Ongoing: [...]
```

### Commit-order analysis table (Mode 2, step 2)

| Commit | Type | TDD compliant? |
|--------|------|----------------|
| abc123 | Test | N/A (first) |
| def456 | Impl | Yes (test first) |
| ghi789 | Both | No (should be separate) |
| jkl012 | Impl | No (no preceding test) |
