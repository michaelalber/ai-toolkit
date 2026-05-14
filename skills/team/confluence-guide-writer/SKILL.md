---
name: confluence-guide-writer
description: >
  Reads Confluence spec pages and/or source code and generates well-formatted
  tutorial and user guide content for a Confluence space's user guide section.
  Targets client/end-user/stakeholder audiences. Use when writing Confluence user guides, generating tutorial or how-to pages for clients or end users, or producing stakeholder documentation from Confluence spec pages or source code. Trigger phrases: "write user guide", "generate confluence page", "create tutorial", "confluence docs for clients".
  Do NOT use when the goal is to detect or reconcile stale pages — use
  doc-sync instead.
---

# Confluence User Guide Writer

> "If you can't explain it simply, you don't understand it well enough."
> -- Albert Einstein

## Core Philosophy

This skill transforms technical source material — Confluence spec pages, architecture
docs, API references, and source code — into user-facing guides written for
**clients, end-users, and stakeholders**, not engineers.

**The fundamental principle:** What the system *does* matters to engineers. What
the user *achieves* matters to this audience. Every sentence must answer:
"What does the reader need to do?" — not "How is the system built?"

**Non-Negotiable Constraints:**

1. **Audience before accuracy** — Technically correct but incomprehensible documentation is useless.
2. **Source fidelity** — Every guide must be traceable to actual spec pages or code. Never invent capabilities.
3. **One guide, one outcome** — Each page teaches the reader how to accomplish one thing.
4. **Confluence-native formatting** — Use headings, callouts, numbered steps, and info/warning panels.
5. **Screenshots placeholder discipline** — Mark every screenshot location. Never omit placeholders.

**Audience Tiers:**

| Tier | Who | Vocabulary | Technical Depth |
|------|-----|------------|-----------------|
| End-User | Day-to-day operators | Plain language, action verbs, zero jargon | Steps only |
| Client | Business stakeholders, managers | Business terms, outcome framing | High-level "what" |
| Power User | Admins, integration owners | Domain terms, some technical context | Feature depth |

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
| 9 | **Plain Language Mandatory** | Write at Grade 8 for end-user guides. Active voice. Sentences under 20 words. | Run the draft through `references/plain-language-checklist.md` before finalizing. |
| 10 | **Change-Aware Writing** | Guides go stale the moment the product changes. Write for easy updates. | Note the version or date last verified. Use step numbers, not "above". |

## Knowledge Base Lookups

Run all searches during INTAKE — once per session, not once per phase.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Diataxis documentation framework tutorial howto")` | INTAKE — calibrate guide type classification |
| `search_knowledge("plain language writing active voice")` | INTAKE — ground plain language standards |
| `search_knowledge("information architecture navigation confluence")` | INTAKE — validate hierarchy decisions |
| `search_knowledge("user story acceptance criteria writing")` | INTAKE — extract tasks from spec pages written as user stories |

## Workflow: INTAKE → ANALYZE → STRUCTURE → DRAFT → REVIEW → PUBLISH

### Phase 1: INTAKE — Gather Source Material

```
1. Identify the Confluence space and target parent page path
2. Read source spec pages via Confluence MCP
3. Read relevant code files if code is the source
4. Identify audience tier (End-User | Client | Power User)
5. Extract: user tasks, system responses, prerequisites, error states
6. Run all Knowledge Base Lookups from the table above
7. Log intake findings → ANALYZE
```

### Phase 2: ANALYZE — Map Spec to Structure

```
1. Classify each task: How-To | Tutorial | Reference | Explanation
   How-To = steps for competent users; Tutorial = onboarding learners;
   Reference = complete field/option enumeration; Explanation = why it works this way
2. Identify which tasks belong on separate pages (one task = one page)
3. Build vocabulary translation table: technical term → audience term
4. Identify UI elements needing screenshot placeholders
5. Identify warning conditions (data loss, irreversible actions)
```

### Phase 3: STRUCTURE — Propose Page Hierarchy

```
1. Draft the hierarchy (parent + child pages)
2. Name each page with a verb phrase
3. Present hierarchy to user
4. If hierarchy is ambiguous, emit draft with [VERIFY] annotations and stop.
5. Wait for explicit approval before drafting
```

### Phase 4: DRAFT — Generate Pages

```
1. Draft the overview/landing page first
2. Draft each child page in navigation order
3. Apply templates from references/page-templates.md
4. Apply plain language rules from references/plain-language-checklist.md
5. Mark all screenshot locations: [SCREENSHOT: description]
6. Add source reference panel to every page
7. Present all drafts to user
8. Wait for explicit approval before publishing
```

**Mandatory page elements:** H1 verb phrase title → prerequisites panel → numbered steps
with screenshot placeholders → warning panels for irreversible actions → Next Steps → Source Reference panel.

**Confluence conventions:** sentence case headings; `:::info` / `:::warning` / `:::note` callouts;
`**bold**` for UI element names; numbered lists for sequential steps; conditions before
instructions ("If X, do Y" — not "Do Y if X").

### Phase 5: REVIEW — Validate Drafts

Run the plain language checklist. Verify: every step is actionable, every UI step has a
screenshot placeholder, vocabulary is translated, source references are present, no invented
capabilities remain. Fix failures, present validation summary, await approval.

### Phase 6: PUBLISH — Write to Confluence

```
1. Resolve parent page ID via Confluence MCP
2. Create/update pages in correct hierarchy order (parent before children)
3. Log each published page: title, action (created/updated), URL
4. Confirm all pages accessible
5. Report all published URLs to user
```

## State Block

```
<confluence-guide-state>
phase: INTAKE | ANALYZE | STRUCTURE | DRAFT | REVIEW | PUBLISH
space: [Confluence space key]
section: [target parent page path]
audience: End-User | Client | Power User
sources_read: [count]
pages_planned: [count]
pages_drafted: [count]
pages_published: [count]
pending_approval: hierarchy | drafts | none
last_action: [what was just completed]
next_action: [what happens next]
</confluence-guide-state>
```

## Output Templates

See `references/page-templates.md` for complete How-To, Tutorial, Reference, and
Overview page templates with all mandatory sections and placeholder markers.

**Publishing log** (inline):

```markdown
| Page Title | Action | URL | Parent |
|------------|--------|-----|--------|
| [title] | created | [url] | [parent] |
```

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

## Error Recovery

### Source Material Is Incomplete or Ambiguous

```
Symptom: Spec page describes system design but not user workflow; critical steps missing.

Recovery:
1. Stop — do not guess or invent missing steps
2. List gaps explicitly in a CLARIFICATION REQUEST to the user
3. Ask targeted questions: "The spec describes two export options but doesn't
   indicate which is available to end-users. Can you clarify?"
4. Draft known sections and mark gaps: [CLARIFICATION NEEDED: describe the gap]
5. Do not publish until all gaps are resolved
```

### Target Confluence Space or Page Not Found

```
Symptom: confluence_get_page returns 404 or permission error; ambiguous parent page.

Recovery:
1. Ask the user for the exact space key and parent page URL or ID
2. Use confluence_search with narrower terms to find the correct space
3. List candidate pages for user selection if multiple matches exist
4. If access denied, flag that MCP connection may need re-authentication
5. Do not create pages in the wrong location — confirm parent before publishing
```

### Audience Tier Not Specified

```
Symptom: Request says "write a user guide" with no audience specified.

Recovery:
1. Ask: "Who is the primary audience — end-users (daily operators),
   clients/stakeholders (business-level), or power users/admins?"
2. Default to End-User if the user cannot specify — state the assumption explicitly
3. Note the assumed audience in the state block
```

## Integration with Other Skills

- **`doc-sync`** — If existing Confluence pages are stale relative to code changes, exit and invoke `doc-sync` first. `confluence-guide-writer` generates new content; `doc-sync` reconciles stale content.

- **`jira-comment-writer`** — After publishing, use `jira-comment-writer` to add a plain-language comment to the relevant Jira ticket linking to the published Confluence pages.

- **`architecture-journal`** — For explanation-type pages (Why does the system work this way?), cross-reference ADRs maintained by `architecture-journal` to provide accurate rationale.

- **`context-builder-agent`** — For complex feature documentation sessions, use `context-builder-agent` first to gather context (recent changes, relevant ADRs, affected files) before INTAKE.
