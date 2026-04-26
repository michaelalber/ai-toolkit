---
name: jira-review
description: >
  Automatically review Jira issues for implementation readiness. Detects complexity
  signals, parses acceptance criteria, and recommends clarification or planning mode
  when needed. Use when asked to review a Jira issue for readiness, check if a ticket has enough detail to implement, assess acceptance criteria completeness, or evaluate a story before sprint planning. Do NOT use when implementation is already complete — this skill
  reviews for readiness, not post-implementation accuracy; Do NOT use when the
  issue tracker is not Jira.
---

# Jira Issue Review Skill

## Core Philosophy

Before writing a single line of code, we must understand what we're building and why. This skill embodies the principle that **unclear requirements are the root cause of most project failures**. By systematically reviewing Jira issues before implementation, we:

1. **Prevent wasted effort** - Catching ambiguity early saves hours of rework
2. **Surface hidden complexity** - Identify technical risks before they become blockers
3. **Ensure testability** - Clear acceptance criteria enable TDD from the start
4. **Align expectations** - Questions asked now prevent misunderstandings later

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Completeness Before Clarity** | A vague issue blocks implementation regardless of how well-written it is. Missing acceptance criteria is a harder blocker than unclear prose. | Flag missing acceptance criteria before assessing description quality. |
| 2 | **Ambiguity Is Blocking** | Ambiguous requirements produce wrong implementations. Any requirement that admits two interpretations will result in the wrong one being chosen. | Any requirement that admits two interpretations must be flagged as a blocker, not a suggestion. |
| 3 | **Complexity Is Measurable** | Implementation complexity can be estimated from signal density, not intuition. Signals include: new integrations, cross-service changes, undecided technical approaches, external dependencies. | Apply the complexity scoring formula from `references/complexity-scoring.md`. Do not guess complexity. |
| 4 | **Testability Is a Gate** | An issue without acceptance criteria cannot be verified as done. TDD cannot start without a testable criterion. If you cannot write the first test from the AC, the AC is not ready. | No issue passes review without at least one acceptance criterion that can be expressed as a test. |
| 5 | **Size Predicts Risk** | Large issues (high complexity score) correlate with planning failures, scope drift, and missed dependencies. High-complexity issues rarely survive implementation unchanged. | Flag issues scoring ≥ 8 for decomposition before sprint commitment. |
| 6 | **Context Reduces Rework** | Missing context forces implementers to make assumptions. Every assumption the implementer must make is a potential rework event. | Every gap in the issue that requires the implementer to assume something is a required clarification. |
| 7 | **Dependencies Must Be Explicit** | Undeclared dependencies cause cascading delays. A feature that cannot be completed until another team ships will slip; the earlier this is surfaced, the smaller the impact. | Flag any issue that implies another issue's completion or another team's delivery without linking it explicitly. |
| 8 | **Reproducibility Is Non-Negotiable** | A bug report that cannot be reproduced cannot be fixed. Developers who cannot reproduce a bug make changes that may not fix it and may introduce regressions. | Any bug issue missing reproduction steps fails review unconditionally. |
| 9 | **UI Issues Require Visuals** | Describing a visual problem in text produces ambiguous fixes. "The button looks wrong" is not actionable. A screenshot with markup is. | Flag any UI/UX issue lacking screenshots, annotated mockups, or Figma links. |
| 10 | **Estimates Are Evidence-Based** | Story point estimates without complexity signals are fiction. Accurate estimates require measurable inputs. | Require complexity scoring before accepting an estimate. Reject point assignments made without supporting signal evidence. |

## Auto-Trigger Behavior

This skill activates automatically when the following MCP tools are invoked:

- `jira_get_issue` - Fetch a single Jira issue
- `jira_get_issue_with_docs` - Fetch issue with linked documentation

Upon detecting these tool calls, immediately perform a comprehensive review of the returned issue data before proceeding with any implementation work.

## Requirements Extraction

### Parsing the Description Field

Extract structured requirements from the Jira issue description using the patterns defined in `references/description-patterns.md`.

**Primary extraction targets:**

1. **Acceptance Criteria (AC)** - Specific, testable conditions that must be met
2. **Definition of Done (DoD)** - Completion checklist items
3. **User Stories** - As a [role], I want [feature], so that [benefit]
4. **Technical Requirements** - Performance, security, compatibility constraints

### Extraction Algorithm

```
1. Scan for section headers (case-insensitive):
   - "Acceptance Criteria", "AC:", "Criteria"
   - "Definition of Done", "DoD:", "Done When"

2. Parse list items following headers:
   - Numbered lists (1., 2., 3.)
   - Bullet points (-, *, •)
   - Checkboxes ([ ], [x], ☐, ☑)

3. Detect BDD patterns anywhere in description:
   - Given [precondition]
   - When [action]
   - Then [expected result]

4. Flag unstructured descriptions for manual review
```

## Complexity Scoring

Use the 5-dimension weighted scoring system defined in `references/complexity-scoring.md`.

### Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Scope Breadth | 1.5 | Number of components/systems affected |
| Requirements Clarity | 1.5 | Specificity and completeness of AC/DoD |
| Technical Uncertainty | 1.2 | New tech, integrations, unknowns |
| Dependencies | 1.0 | External team/system dependencies |
| Estimation Confidence | 1.0 | Presence of sizing/story points |

### Scoring Formula

```
weighted_score = Σ(dimension_score × weight) / Σ(max_score × weight)
complexity_percentage = weighted_score × 100
```

### Thresholds

- **Low Complexity** (GREEN): < 40%
- **Medium Complexity** (YELLOW): 40% - 70%
- **High Complexity** (RED): > 70%

## Recommendation Logic

Based on complexity assessment and requirements completeness:

```
IF complexity < 40% AND ac_complete AND dod_present:
    -> READY TO IMPLEMENT
    -> Suggest: "Consider using /tdd-cycle to begin implementation"

ELIF complexity > 70% OR critical_info_missing:
    -> NEEDS PLANNING MODE
    -> Suggest: "Use plan mode to break down this issue before implementation"

ELSE:
    -> NEEDS CLARIFICATION
    -> Generate specific questions using templates from references/clarifying-questions.md
```

### Critical Information Flags

The following trigger immediate "NEEDS CLARIFICATION" regardless of complexity:

- No acceptance criteria found
- Vague success criteria ("should work well", "be user-friendly")
- Undefined technical terms specific to the domain
- Missing error handling requirements
- No performance/scale expectations when relevant

## Output Template

When reviewing a Jira issue, produce the following structured output:

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

## Complexity Signal Detection

### High Complexity Signals (RED FLAGS)

Look for these indicators that suggest high complexity:

**Scope Indicators:**
- Multiple components mentioned (API + frontend + database)
- Cross-service communication required
- Multiple user roles affected
- Data migration involved

**Uncertainty Keywords:**
- "research", "investigate", "spike", "POC", "explore"
- "figure out", "determine", "decide"
- "might need", "possibly", "could require"

**Vague Requirements:**
- "should be fast" (no specific metrics)
- "user-friendly" (no UX specification)
- "scalable" (no load expectations)
- "secure" (no specific security requirements)

**Dependency Signals:**
- External team mentions
- Third-party API integrations
- Waiting on decisions

### Medium Complexity Signals (YELLOW FLAGS)

- 2-3 components affected
- Partial AC coverage (some criteria, but gaps)
- Some ambiguous requirements mixed with clear ones
- Internal dependencies only

### Low Complexity Signals (GREEN FLAGS)

- Single component change
- Clear, testable acceptance criteria
- Well-defined definition of done
- Familiar technology stack
- No external dependencies
- Existing patterns to follow

## Clarifying Question Generation

When gaps are identified, generate targeted questions using the templates in `references/clarifying-questions.md`.

**Question Quality Guidelines:**

1. **Be specific** - Reference exact text from the issue
2. **Be actionable** - Questions should have concrete answers
3. **Prioritize** - List most critical questions first
4. **Limit scope** - Maximum 5 questions to avoid overwhelming

## AI Discipline Rules

### CRITICAL: Flag Gaps by Name, Not Category

A vague flag ("this issue is unclear") gives the product owner nothing actionable. A specific
flag ("Missing: acceptance criteria — the description says 'fix the login page' but does not
state what 'fixed' means") is actionable.

```
WRONG: "This issue is too vague to implement."
       (Product owner does not know what to add)

RIGHT: "Missing: acceptance criteria.
        The description says 'fix the login page' but does not state:
        - What 'fixed' means (what is currently wrong?)
        - Which users are affected (all? specific roles?)
        - What the success condition looks like
        Please add acceptance criteria before this issue is sprint-ready."
```

### CRITICAL: Complexity Scores Require Evidence

Recommending a complexity score without listing the signals that produced it is guesswork.
The score must be derivable from the signals you name.

```
WRONG: "This issue has a complexity score of 8 — it looks quite large."

RIGHT: "Complexity score: 8 (HIGH). Signals detected:
        - API changes: 2 endpoints modified (Scope Breadth: 3/5)
        - New database table: 1 (Scope Breadth contribution)
        - Auth change: session model affected (Technical Uncertainty: 4/5)
        - External dependency: mobile team must ship push notification support first
          (Dependencies: 5/5)
        Recommend decomposition before sprint commitment."
```

## Integration Points

### Handoff to TDD Cycle

When recommending "READY TO IMPLEMENT", suggest:

```
This issue appears ready for implementation. Consider using /tdd-cycle to:
1. Write tests based on the acceptance criteria
2. Implement the minimum code to pass tests
3. Refactor while maintaining green tests
```

### Handoff to Planning Mode

When recommending "NEEDS PLANNING MODE", suggest:

```
This issue requires deeper analysis before implementation. Use plan mode to:
1. Break down into smaller, implementable tasks
2. Identify technical approach and alternatives
3. Create a step-by-step implementation plan
```

### Handoff to Clarification

When recommending "NEEDS CLARIFICATION", provide:

1. Specific questions to ask the product owner/stakeholder
2. Suggestions for updating the Jira issue
3. Offer to help draft clearer acceptance criteria once clarified

## Examples

### Example: Well-Defined Issue (READY TO IMPLEMENT)

```
Issue: [PROJ-123] Add logout button to header

Description:
As a logged-in user, I want to see a logout button in the header so that I can securely end my session.

Acceptance Criteria:
1. Logout button appears in header only when user is authenticated
2. Clicking logout clears the session token
3. User is redirected to login page after logout
4. Success toast notification displays "You have been logged out"

Definition of Done:
- Unit tests for logout functionality
- E2E test for logout flow
- Code reviewed and approved
```

**Review Result**: READY TO IMPLEMENT (Complexity: 25%)

### Example: Vague Issue (NEEDS CLARIFICATION)

```
Issue: [PROJ-456] Improve dashboard performance

Description:
The dashboard is slow. Make it faster.
```

**Review Result**: NEEDS CLARIFICATION (Complexity: Unable to assess)

Clarifying Questions:
1. What specific metrics define "slow"? (current load time, target load time)
2. Which dashboard components are experiencing performance issues?
3. Are there specific user actions that trigger slowness?
4. What is the acceptable performance target?

### Example: Complex Issue (NEEDS PLANNING MODE)

```
Issue: [PROJ-789] Implement real-time notifications

Description:
Add real-time notification system. Should work across all platforms (web, mobile).
Need to research best approach - WebSockets vs SSE vs polling.
Must integrate with existing user preferences.
Coordinate with mobile team for push notification support.

AC:
- Users receive notifications in real-time
- Works on all platforms
```

**Review Result**: NEEDS PLANNING MODE (Complexity: 82%)

Reasons:
- Multiple platforms (web + mobile)
- Technical uncertainty (approach not decided)
- External dependency (mobile team coordination)
- Vague AC ("real-time" not defined, "all platforms" scope unclear)
