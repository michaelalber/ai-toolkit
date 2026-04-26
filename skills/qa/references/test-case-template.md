# QA Test Case Template

Format for writing test cases during QA review.

## Functional test case

```markdown
### TC-[NNN]: [Short name]

**Feature:** [feature name]
**Type:** happy path | edge case | regression | security
**Priority:** High | Medium | Low

**Preconditions:**
- [state that must exist before the test]

**Steps:**
1. [action]
2. [action]

**Expected result:**
[what the system should do — specific and observable]

**Pass criteria:**
- [ ] [binary check]

**Notes:**
[any test data, environment requirements, or known flakiness]
```

## Automated test stub (Given/When/Then)

```
Given: [starting state]
When:  [action taken]
Then:  [observable outcome]
And:   [additional assertion]
```

## Regression test case

```markdown
### Regression: [Issue reference]

**Root cause:** [brief description from triage]
**Fixed in:** [commit or PR reference]
**Regression check:** [specific step that would reproduce the original bug]
**Pass:** [the bug does NOT reproduce]
```
