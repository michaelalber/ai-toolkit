# Domain Principles, Discipline Rules & Anti-Patterns

Full depth for `confluence-guide-writer`. Loaded just-in-time during ANALYZE, DRAFT, and REVIEW.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Task-Oriented Writing** | Guides exist to help readers complete tasks. Every page answers "How do I do X?" | Frame every title as a verb phrase: "How to submit a request." |
| 2 | **Audience Vocabulary** | Users speak the language of their job, not the system. `entity_resolution` → "matching duplicate records". | Build a vocabulary translation table in ANALYZE before drafting. |
| 3 | **One Task Per Page** | Mixed-purpose pages confuse readers and make search results ambiguous. | If a draft teaches more than one discrete task, split it into child pages. See AI Discipline Rules. |
| 4 | **Step Completeness** | Every numbered step must be actionable: where to navigate, what to click, what to expect next. | For each step, ask: can a new user follow this without asking a question? If no, rewrite. |
| 5 | **Screenshot Discipline** | Screenshots are mandatory for UI-based guides. | Every step involving a UI element gets `[SCREENSHOT: description]` if no image is provided. |
| 6 | **Progressive Disclosure** | Lead with the minimum needed to accomplish the task. Advanced options go in expandable sections. | Main flow = steps. Info panel = prerequisites. Warning panel = irreversible actions. |
| 7 | **Source Traceability** | Every guide must reference the source it was generated from. | Add a "Source Reference" note panel at the bottom of each page. |
| 8 | **No Dead Ends** | Every guide ends with "Next Steps" linking to 2-3 related pages. | Dead-end guides force readers to lose context. Always include follow-on links. |
| 9 | **Plain Language Mandatory** | Write at Grade 8 for end-user guides. Active voice. Sentences under 20 words. | Run the draft through `plain-language-checklist.md` before finalizing. |
| 10 | **Change-Aware Writing** | Guides go stale the moment the product changes. Write for easy updates. | Note the version or date last verified. Use step numbers, not "above". |

## AI Discipline Rules

### CRITICAL: Never Invent Capabilities

```
WRONG: Describing a "bulk export" feature after reading a spec that only mentions
       single-record export, because "it seems like it should be there."

RIGHT: Document only what exists in source. Flag gaps:
       "[NOTE: No bulk export capability found in source material.
        Confirm whether this feature exists before publishing.]"
```

### CRITICAL: Translate Before Writing

```
WRONG: "Navigate to the entity resolution queue to begin deduplication."

RIGHT: "Navigate to the Duplicate Records section to review and merge
       matching entries."
```

### CRITICAL: Gate Before Publishing

```
WRONG: Draft → immediately push to Confluence without user review.

RIGHT:
  1. Present hierarchy → wait for approval
  2. Draft pages → present to user → wait for approval
  3. Publish approved pages only
  4. Log published URLs
```

### CRITICAL: Screenshot Placeholders Are Mandatory

```
WRONG: "Click the Submit button." (No placeholder)

RIGHT: "Click the **Submit** button.
       [SCREENSHOT: Submit button — blue, labeled 'Submit Request', lower right of form]"
```

### One Task Per Page

See Domain Principles #3 for the principle. Applied as:

```
WRONG: One page titled "User Management" covering add, remove, reset password, assign roles.

RIGHT: Overview page "User Management" → child pages:
       "How to add a new user" | "How to remove a user" |
       "How to reset a password" | "How to assign roles"
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Tech-to-User Dump** | Spec pages are written for engineers. End-users cannot act on them. | Analyze for user tasks, translate vocabulary, rewrite in task-oriented plain language. |
| 2 | **Screenshot Debt** | Users cannot find UI elements without visuals. Guides become unusable immediately. | Block publishing until screenshots are provided or deferral is explicitly agreed with a dated TODO. |
| 3 | **Jargon Bleed** | End-users and clients do not know technical terms and stop reading. | Build the vocabulary translation table in ANALYZE; substitute audience terms throughout. |
| 4 | **Missing Prerequisites** | Users fail at step 1 because they lack required access or knowledge. | Always include a Prerequisites info panel at the top of every how-to and tutorial page. |
| 5 | **Dead-End Page** | Users complete the task with no context for what to do next. | Every page ends with Next Steps or Related Pages linking to 2-3 follow-on pages. |
| 6 | **Passive Voice** | Passive voice is harder to read and hides who does what. | Active voice only: "Click Submit to save the form." |
| 7 | **Explanation Inside How-To** | How-to users need steps, not theory. Mixing types degrades both. | Keep how-to steps pure. Link to a separate Explanation page for the "why". |
| 8 | **No Warning Panels** | Users perform irreversible actions without knowing the consequences. | Add a warning panel before any step that is irreversible or has significant impact. |
| 9 | **Weak Link Text** | "Click here" is meaningless to screen readers and scanners alike. | Use descriptive link text: "See [How to export a report](link)." |
| 10 | **Version Blindness** | A guide accurate in v1.2 is wrong in v2.0 with no way for readers to tell. | Note version or last-verified date in the source reference panel. |
