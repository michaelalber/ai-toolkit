# Jira Review Output Template

The structured review the skill produces for a Jira issue.

```markdown
## Jira Issue Review

**Issue**: [KEY-123] Issue Title
**Type**: Story | Bug | Task | Epic
**Status**: To Do | In Progress | etc.

---

### Requirements Analysis

**Acceptance Criteria Found**: Yes | No | Partial
- [ ] Criterion 1 extracted from description
- [ ] Criterion 2 extracted from description

**Definition of Done Found**: Yes | No | Partial
- [ ] DoD item 1
- [ ] DoD item 2

**User Story**: [Extracted if present, or "Not specified"]

---

### Complexity Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Scope Breadth | X/5 | [specific components identified] |
| Requirements Clarity | X/5 | [what's clear vs unclear] |
| Technical Uncertainty | X/5 | [new tech or unknowns] |
| Dependencies | X/5 | [external dependencies] |
| Estimation Confidence | X/5 | [sizing info present?] |

**Overall Complexity**: Low (X%) | Medium (X%) | High (X%)

---

### Recommendation

**[READY TO IMPLEMENT]** | **[NEEDS CLARIFICATION]** | **[NEEDS PLANNING MODE]**

[Detailed explanation of the recommendation]

---

### Clarifying Questions

[Only include if recommendation is NEEDS CLARIFICATION]

1. [Specific question about ambiguous requirement]
2. [Question about missing information]
3. [Question about technical constraints]

---

### Suggested Next Steps

- [Actionable next step 1]
- [Actionable next step 2]
```

## Handoff Snippets

**READY TO IMPLEMENT** → "Consider `/tdd-cycle`: write tests from the AC, implement minimum code to
pass, refactor while green."

**NEEDS PLANNING MODE** → "Use plan mode: break into smaller tasks, identify technical approach and
alternatives, create a step-by-step plan."

**NEEDS CLARIFICATION** → provide specific questions for the product owner, suggest issue updates,
and offer to draft clearer acceptance criteria once clarified.
