# Description Patterns for Requirements Extraction

This document defines patterns for extracting acceptance criteria (AC), definition of done (DoD), and other structured requirements from Jira issue descriptions.

## Section Header Patterns

### Acceptance Criteria Headers

Match these headers (case-insensitive) to identify AC sections:

```
Primary patterns:
- "Acceptance Criteria"
- "Acceptance Criteria:"
- "AC:"
- "AC"
- "Criteria:"
- "Criteria"
- "Requirements:"
- "Requirements"

Secondary patterns:
- "Expected Behavior"
- "Expected Behavior:"
- "Success Criteria"
- "Success Criteria:"
- "What Success Looks Like"
```

### Definition of Done Headers

Match these headers (case-insensitive) to identify DoD sections:

```
Primary patterns:
- "Definition of Done"
- "Definition of Done:"
- "DoD:"
- "DoD"
- "Done When:"
- "Done When"
- "Completion Criteria"
- "Completion Criteria:"

Secondary patterns:
- "This is done when"
- "Complete when"
- "Finished when"
- "Deliverables:"
- "Deliverables"
```

### User Story Headers

```
- "User Story"
- "User Story:"
- "Story:"
- "As a"  (start of user story format)
```

## List Format Patterns

### Numbered Lists

```
Standard:
1. First item
2. Second item
3. Third item

With parentheses:
1) First item
2) Second item

With period and space:
1 . First item (handle extra space)
```

### Bullet Points

```
Standard dash:
- Item one
- Item two

Asterisk:
* Item one
* Item two

Unicode bullet:
• Item one
• Item two

Arrow:
→ Item one
> Item one
```

### Checkboxes

```
Markdown checkboxes:
- [ ] Unchecked item
- [x] Checked item
- [X] Checked item (capital X)

Unicode checkboxes:
☐ Unchecked item
☑ Checked item
✓ Checked item
✔ Checked item

Jira checkbox format:
(/) Done item
(x) Not done item
```

## BDD (Behavior-Driven Development) Patterns

### Given/When/Then Format

```
Full format:
Given [precondition]
When [action]
Then [expected result]

With And:
Given [precondition]
And [additional precondition]
When [action]
Then [expected result]
And [additional result]

Inline format:
GIVEN [precondition] WHEN [action] THEN [result]
```

### Scenario Format

```
Scenario: [scenario name]
  Given [precondition]
  When [action]
  Then [expected result]

Feature: [feature name]
  Scenario: [scenario 1]
    Given...
  Scenario: [scenario 2]
    Given...
```

## User Story Patterns

### Standard Format

```
As a [role/persona]
I want [feature/capability]
So that [benefit/value]

Variations:
As a [role], I want [feature] so that [benefit]
As a [role], I want to [action] so that [benefit]
As [role], I want [feature], so [benefit]
```

### Role Patterns

```
Common roles:
- "As a user"
- "As an admin"
- "As a logged-in user"
- "As an anonymous user"
- "As a [specific persona name]"
- "As the system"
```

## Technical Requirement Patterns

### Performance Requirements

```
Keywords to detect:
- "must complete in X seconds"
- "response time < X ms"
- "should handle X concurrent users"
- "latency under X"
- "throughput of X per second"
- "99th percentile"
- "SLA"
```

### Security Requirements

```
Keywords to detect:
- "must be authenticated"
- "requires authorization"
- "role-based access"
- "RBAC"
- "encrypt"
- "sanitize input"
- "prevent [XSS/SQL injection/CSRF]"
- "audit log"
```

### Compatibility Requirements

```
Keywords to detect:
- "must work on [browser/platform]"
- "backwards compatible"
- "support [version]"
- "mobile responsive"
- "cross-browser"
- "IE11" / "Safari" / specific browser mentions
```

## Edge Case Detection

### Unstructured Descriptions

When no clear headers are found, look for:

1. **Implicit lists** - Sentences starting with "Also," "Additionally," "Furthermore"
2. **Conditional statements** - "If X, then Y" patterns
3. **Negations** - "Should not", "Must not", "Cannot"
4. **Boundary mentions** - "At least", "At most", "Between X and Y"

### Mixed Format Handling

When descriptions mix formats:

```
Priority order for extraction:
1. Explicit headers with lists (highest confidence)
2. BDD patterns (Given/When/Then)
3. Checkbox items anywhere in description
4. Numbered/bulleted lists without headers
5. Inline requirements (lowest confidence)
```

### Jira-Specific Formatting

Handle Jira wiki markup:

```
Headers:
h1. Heading
h2. Subheading
h3. Smaller heading

Lists:
* Bullet item
# Numbered item
*# Mixed nesting

Panels:
{panel:title=Acceptance Criteria}
content here
{panel}

Code blocks:
{code}
code here
{code}

Tables:
||Header 1||Header 2||
|Cell 1|Cell 2|
```

## Extraction Priority Rules

### What to Extract

1. **Must extract:**
   - All items under AC headers
   - All items under DoD headers
   - All Given/When/Then scenarios
   - User story if present

2. **Should extract:**
   - Technical constraints (performance, security)
   - Explicit test cases mentioned
   - Error handling requirements

3. **May extract:**
   - Implicit requirements from description prose
   - Inferred edge cases

### What to Flag

Flag for clarification if:

1. **No structured requirements found**
   - Description is pure prose
   - No lists, headers, or patterns detected

2. **Incomplete patterns**
   - Header present but no items follow
   - "Given" without "Then"
   - User story missing "so that"

3. **Contradictory requirements**
   - Two criteria that conflict
   - Ambiguous scope boundaries

4. **Vague quantifiers**
   - "fast", "quick", "responsive" without metrics
   - "many", "few", "some" without numbers
   - "user-friendly" without specific UX criteria

## Output Format for Extracted Requirements

```markdown
### Extracted Acceptance Criteria

**Source**: [Header name or "Inferred from description"]
**Confidence**: High | Medium | Low

1. [Extracted criterion - verbatim or normalized]
2. [Extracted criterion]

### Extracted Definition of Done

**Source**: [Header name or "Standard DoD applied"]
**Confidence**: High | Medium | Low

1. [DoD item]
2. [DoD item]

### User Story

**Format**: Standard | Abbreviated | Inferred
> As a [role], I want [feature], so that [benefit]

### Additional Requirements Detected

- **Performance**: [requirement if found]
- **Security**: [requirement if found]
- **Compatibility**: [requirement if found]

### Extraction Warnings

- [Warning about unstructured content]
- [Warning about missing elements]
- [Warning about ambiguous requirements]
```
