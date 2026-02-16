# Clarifying Questions Reference

This document provides question templates and strategies for generating clarifying questions when Jira issues have gaps or ambiguities.

## Question Generation Principles

### Core Guidelines

1. **Be specific** - Reference exact text from the issue
2. **Be actionable** - Questions should have concrete, implementable answers
3. **Prioritize** - Ask most critical questions first (max 5)
4. **Avoid yes/no** - Frame questions to elicit detailed responses
5. **Suggest options** - When applicable, provide choices to make answering easier

### Question Structure

```
Template:
[Context from issue] + [Specific gap identified] + [What information is needed]

Example:
"The issue mentions 'fast response times' but doesn't specify a target.
What response time threshold should we aim for? (e.g., < 200ms, < 500ms, < 1s)"
```

## Question Templates by Category

### Missing Acceptance Criteria

**No AC present:**
```
"This issue doesn't have explicit acceptance criteria. To ensure we build
the right thing, could you specify:
1. What specific behavior should we observe when this is complete?
2. How will we verify the feature works correctly?
3. Are there any edge cases we should handle?"
```

**Incomplete AC:**
```
"The acceptance criteria cover [X scenarios], but I'd like to clarify:
- What should happen when [uncovered scenario]?
- Is [inferred requirement] also in scope?"
```

### Vague Requirements

**Undefined terms:**
```
"When the issue says '[vague term]', what specific behavior do you expect?

For example:
- '[term]' could mean [interpretation A] or [interpretation B]
- Which interpretation is correct, or is there another meaning?"
```

**Subjective criteria:**
```
"The requirement states '[subjective term like fast/user-friendly/clean]'.
To make this testable, could you provide:
- Specific metrics or thresholds?
- Examples of what 'good' looks like?
- Any existing standards we should follow?"
```

**Common vague terms and follow-ups:**

| Vague Term | Follow-up Question |
|------------|-------------------|
| "fast" | "What response time is acceptable? (e.g., < 200ms)" |
| "user-friendly" | "What specific UX patterns should we follow?" |
| "scalable" | "What load should this handle? (concurrent users, requests/sec)" |
| "secure" | "What specific security measures are required?" |
| "clean" | "What coding standards or patterns should we follow?" |
| "simple" | "What level of complexity is acceptable?" |
| "improved" | "What metrics define improvement? Current vs. target?" |

### Scope Boundaries

**Unclear scope:**
```
"The issue mentions [feature], but I want to confirm the boundaries:
- Is [related feature A] in scope or out of scope?
- Should we also handle [edge case B]?
- Does this include [platform/browser/device]?"
```

**"Etc." or open-ended lists:**
```
"The description says '[item 1, item 2, etc.]'. Could you provide the
complete list of items to include? This will help ensure we don't miss
anything or over-scope the work."
```

### Technical Uncertainty

**Technology choice:**
```
"The issue requires [capability], but the approach isn't specified.
Options include:
1. [Option A] - [pros/cons]
2. [Option B] - [pros/cons]

Which approach should we take, or is there a preferred pattern in this codebase?"
```

**Integration questions:**
```
"This involves integrating with [system/API]. Could you clarify:
- Is there existing documentation or examples?
- Who owns [system] and can answer technical questions?
- Are there authentication/authorization requirements?"
```

**Research-required:**
```
"This issue mentions '[new technology/approach]' which the team hasn't
used before. Should we:
1. Conduct a spike/POC first to validate the approach?
2. Proceed with implementation and learn as we go?
3. Consult with someone who has experience with this?"
```

### Dependencies

**External team:**
```
"This requires coordination with [team name]. Could you clarify:
- Who is the point of contact?
- What is their current availability/timeline?
- What do we need from them vs. what do we provide?"
```

**Blocking work:**
```
"Is this blocked by any other work that needs to complete first?
If so, what is the expected timeline for those blockers?"
```

**Third-party services:**
```
"This involves [third-party service]. Questions:
- Do we have an account/API key?
- Are there rate limits or usage constraints?
- Is there a sandbox/test environment available?"
```

### Error Handling

**Missing error scenarios:**
```
"The happy path is clear, but what should happen when:
- [Error scenario 1]?
- [Error scenario 2]?
- The user provides invalid input?
Should we show specific error messages or handle silently?"
```

**Failure modes:**
```
"If [dependency/service] is unavailable, should we:
1. Show an error and block the user?
2. Gracefully degrade (how)?
3. Queue for retry?
4. Something else?"
```

### User Experience

**Missing UX details:**
```
"The feature requires user interaction, but I need clarity on:
- What should the UI look like? (mockup/wireframe available?)
- Are there existing patterns in the app we should follow?
- What feedback should users see during processing?"
```

**Validation rules:**
```
"What validation rules apply to [input field]?
- Required or optional?
- Length limits?
- Format requirements?
- What error messages should display?"
```

### Performance and Scale

**No performance criteria:**
```
"This feature will be used by [users/systems]. To ensure adequate performance:
- What response time is acceptable?
- What load should this handle?
- Are there any rate limiting requirements?"
```

**Data volume:**
```
"How much data should this feature handle?
- Expected record counts?
- Growth projections?
- Should we implement pagination/lazy loading?"
```

## Question Prioritization

### Priority 1: Blockers
Questions where work cannot proceed without answers:
- Core functionality undefined
- Technology choice required
- External dependency unclear

### Priority 2: Scope Clarification
Questions that prevent scope creep or under-delivery:
- Boundary definitions
- Feature inclusions/exclusions
- Platform requirements

### Priority 3: Quality Criteria
Questions about non-functional requirements:
- Performance targets
- Security requirements
- Accessibility needs

### Priority 4: Edge Cases
Questions about error handling and unusual scenarios:
- Error states
- Failure modes
- Boundary conditions

## Question Formatting

### For Jira Comments

```markdown
## Clarification Needed

Before proceeding with implementation, I have a few questions:

### 1. [Question Category]
[Specific question with context]

### 2. [Question Category]
[Specific question with context]

---
*Once these are clarified, I can provide an accurate complexity estimate
and begin implementation.*
```

### For Slack/Chat

```
Quick clarification needed on [ISSUE-123]:

1. [Brief question]
2. [Brief question]

Let me know and I can proceed with implementation.
```

### For Review Output

```markdown
### Clarifying Questions

The following questions should be resolved before implementation:

1. **[Category]**: [Question]
   - Context: [Why this matters]
   - Suggestion: [Possible options if applicable]

2. **[Category]**: [Question]
   - Context: [Why this matters]
```

## Anti-Patterns to Avoid

### Don't Ask:

1. **Questions you can answer yourself**
   - Bad: "What framework should we use?"
   - Good: (Check the codebase first, then ask if unclear)

2. **Yes/no questions without follow-up**
   - Bad: "Should this be fast?"
   - Good: "What response time should we target?"

3. **Too many questions at once**
   - Bad: 10+ questions in one comment
   - Good: Prioritize top 5, note others as "additional considerations"

4. **Questions about obvious requirements**
   - Bad: "Should the code work?"
   - Good: Focus on genuinely ambiguous items

5. **Leading questions**
   - Bad: "Don't you think we should use React?"
   - Good: "What UI framework should we use?"

## Example: Complete Clarification Request

```markdown
## Clarification Needed for [PROJ-123]

I've reviewed the issue and have a few questions before proceeding:

### 1. Acceptance Criteria
The description mentions "improved search" but doesn't specify success criteria.
- What search behaviors should improve?
- What metrics define "improved"? (e.g., faster, more accurate, both?)

### 2. Scope Boundary
"Search across all content" - does this include:
- [ ] User profiles?
- [ ] Comments?
- [ ] Archived content?
- [ ] Attachments (PDF content)?

### 3. Performance Target
Given search can be resource-intensive:
- What response time is acceptable for search results?
- How many concurrent searches should we support?

### 4. Error Handling
If search fails or times out:
- Should we show partial results?
- What error message should users see?

---

**Blocking questions**: #1, #3 (need these to proceed)
**Nice to have**: #2, #4 (can make reasonable assumptions if needed)

Once clarified, estimated complexity: Medium
Suggested approach: [Brief technical approach]
```
