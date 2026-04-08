---
name: confluence-guide-writer
description: >
  Reads Confluence spec pages and/or source code and generates well-formatted
  tutorial and user guide content for a Confluence space's user guide section.
  Targets client/end-user/stakeholder audiences. Trigger phrases: "write user
  guide", "generate confluence page", "create tutorial", "user guide section",
  "confluence docs for clients", "stakeholder documentation".
---

# Confluence User Guide Writer

> "If you can't explain it simply, you don't understand it well enough."
> -- Albert Einstein

> "The documentation you write for users is not the documentation you write for yourself."
> -- Adapted from Daniele Procida, Diátaxis Framework

## Core Philosophy

This skill transforms technical source material — Confluence spec pages, architecture docs, API references, and source code — into user-facing guides that real people can act on. The output lives in the user guide section of a Confluence space and is written for **clients, end-users, and stakeholders**, not engineers.

**The fundamental principle:** What the system *does* matters to engineers. What the user *achieves* matters to the audience of these guides. Every sentence must be written from the perspective of what the reader needs to do, not how the system is built.

**Non-Negotiable Constraints:**

1. **Audience before accuracy** — Technically correct but incomprehensible documentation is useless. Write for the reader's vocabulary, not the system's vocabulary.
2. **Source fidelity** — Every guide MUST be traceable to actual spec pages or code. Do not invent capabilities or workflows that do not exist.
3. **One guide, one outcome** — Each page teaches the reader how to accomplish one thing. Do not combine multiple unrelated tasks on a single page.
4. **Confluence-native formatting** — Use headings, callouts, numbered steps, and info/warning panels. No plain prose walls.
5. **Screenshots placeholder discipline** — Mark every place where a screenshot should appear. Never describe a UI element that will be invisible to the reader without a visual.

**Audience Tiers:**

| Tier | Who | Vocabulary | Technical Depth |
|------|-----|------------|-----------------|
| End-User | Day-to-day operators, direct users of the system | Plain language, action verbs, zero jargon | Steps only — no "how it works" |
| Client | Business stakeholders, managers, sponsors | Business terms, outcome framing, KPIs | High-level "what", minimal "how" |
| Power User | Advanced users, admins, integration owners | Domain terms, some technical context | Feature depth, configuration options |

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Task-Oriented Writing** | Guides exist to help readers complete tasks. Every page answers the question: "How do I do X?" Not "What is X?" or "How does X work?" Task orientation forces clarity — if you cannot state the task, you cannot write the guide. | Frame every guide title as a verb phrase: "How to submit a request", "How to configure notifications", "How to export a report." |
| 2 | **Audience Vocabulary** | Users do not speak system vocabulary. They speak the language of their job. A field called `user_principal_identifier` is "your login name" to an end-user. A process called `entity_resolution` is "matching duplicate records" to a client. The skill of user documentation is translation. | Before drafting, list the technical terms and translate each to the audience's vocabulary. Use the translated term throughout. |
| 3 | **One Task Per Page** | Confluence user guides are most useful when each page has a single, clear purpose. Mixed-purpose pages confuse readers and make search results ambiguous. A page about "User Management" is not useful; "How to add a new user" and "How to reset a password" are. | If a draft page teaches more than one discrete task, split it. Use a parent page for navigation and child pages for each task. |
| 4 | **Step Completeness** | Every numbered step must be actionable. "Configure the settings" is not a step. "Click Settings in the top navigation bar, then select General." is. Every step should describe: where to navigate, what to click or enter, and what to expect next. | For each step, ask: can a new user follow this without asking a question? If no, rewrite. |
| 5 | **Screenshot Discipline** | Screenshots are mandatory for UI-based guides. Mark every screenshot location with a clear placeholder. Describe exactly what the screenshot must show so a documentation reviewer can produce it. Never describe a UI element without a corresponding screenshot placeholder. | Every step that involves clicking a UI element gets a `[SCREENSHOT: description]` placeholder if no image is provided. |
| 6 | **Progressive Disclosure** | Lead with the minimum needed to accomplish the task. Advanced options, warnings, and edge cases go in expandable sections or callout panels — not in the main flow. A reader who just wants to reset their password does not want to read about all password policy exceptions first. | Main flow = steps to complete the task. Info panel = prerequisites. Warning panel = data loss/irreversible actions. Expand section = advanced options. |
| 7 | **Source Traceability** | Every guide must reference the source material it was generated from. This enables reviewers to verify accuracy and future writers to update guides when features change. Source references go in a note panel at the bottom of each page, not in the main content. | Add a "Source Reference" note panel at the bottom: "This guide was generated from [Spec Page Title](link) and [file path]." |
| 8 | **No Dead Ends** | Every guide ends with a "Next Steps" or "Related Pages" section. Readers who complete one task frequently need to complete a related task. Dead-end guides force readers to navigate away and lose context. | End every guide with 2-3 links to related pages: the next logical task, the parent guide section, or a reference page. |
| 9 | **Plain Language Mandatory** | Write at a Grade 8 reading level for end-user guides. Use active voice. Short sentences (under 20 words). One idea per sentence. Avoid: passive voice, nominalization ("the configuration of" → "configuring"), jargon, and acronyms without expansion. | Run the draft through the Plain Language checklist in `references/plain-language-checklist.md` before finalizing. |
| 10 | **Change-Aware Writing** | User guides go stale the moment the product changes. Write guides that are easy to update: use step numbers instead of "above", use consistent terminology so find-and-replace works, and note version-specific behavior explicitly. | At the top of each guide, note the version or date when the guide was last verified. In the source reference panel, note the commit or Confluence version the guide was generated from. |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Diataxis documentation framework tutorial howto")` | During ANALYZE phase — calibrate guide type (tutorial vs. how-to vs. reference vs. explanation) |
| `search_knowledge("plain language writing active voice")` | During DRAFT phase — verify plain language standards are applied |
| `search_knowledge("information architecture navigation confluence")` | During STRUCTURE phase — validate page hierarchy decisions |
| `search_knowledge("user story acceptance criteria writing")` | During INTAKE phase — extract tasks from spec pages written as user stories |

## Workflow: INTAKE → ANALYZE → STRUCTURE → DRAFT → REVIEW → PUBLISH

### Phase 1: INTAKE — Gather Source Material

Collect all source material before writing any content. Do not draft from memory or assumption.

**Actions:**

1. Identify the Confluence space and target section (user guide parent page)
2. Read the source spec pages via Confluence MCP (`confluence_get_page`, `confluence_search`)
3. If code is provided, read the relevant files to understand actual behavior
4. Identify the target audience tier (End-User, Client, Power User)
5. Identify the scope: one task, one feature, or one section of a guide
6. Extract: what the user needs to do, what the system does in response, prerequisite conditions, and possible error states
7. Log intake findings before proceeding

**Intake Checklist:**

```markdown
### INTAKE Phase

**Target Space**: [space key or name]
**Target Section**: [parent page path]
**Source Pages Read**: [list with page titles and IDs]
**Source Code Read**: [list with file paths]
**Audience Tier**: [End-User | Client | Power User]
**Guide Scope**: [one sentence describing what the user will be able to do]

**Extracted Tasks**:
- [task 1 — user action → system response]
- [task 2 — user action → system response]

**Prerequisites**:
- [what the user must have/know/do before starting]

**Error States to Document**:
- [error condition and resolution]

Proceeding to ANALYZE.
```

### Phase 2: ANALYZE — Map Spec to User Guide Structure

Transform the source material into a user-facing content plan.

**Actions:**

1. Classify each extracted task by guide type (How-To, Tutorial, Reference, Explanation)
2. Identify which tasks belong on separate pages
3. Map technical terms to audience vocabulary
4. Identify all UI elements that need screenshot placeholders
5. Identify all warning conditions (data loss, irreversible actions, permission requirements)
6. Determine page hierarchy: parent page → child pages

**Guide Type Taxonomy (Diátaxis):**

| Type | Question It Answers | Audience | When to Use |
|------|--------------------|----|---|
| How-To | "How do I accomplish X?" | Already-competent users who know *what* they want to do but need the steps | A user who has used the system before needs to complete a specific task |
| Tutorial | "How do I get started?" | New users — learners who have never done this before | Onboarding; the user's goal is learning, not just completing a task |
| Reference | "What are all the options/fields/values?" | Users who need factual completeness | Complete enumeration of a feature's parameters, fields, or statuses |
| Explanation | "Why does it work this way?" | Stakeholders and clients who need context | Background and rationale; answers "why", not "how to" |

> **Diátaxis rule:** How-to guides and tutorials are NOT interchangeable. A how-to assumes the user already knows the context — it gives them steps. A tutorial teaches the context — the learner's success and safety is the primary obligation. Do not embed "how the system works" explanations inside how-to steps. If explanation is needed, it belongs on a separate Explanation page, linked from the how-to.

**Vocabulary Translation Table (fill during analysis):**

| Technical Term | Audience Term | Notes |
|---------------|---------------|-------|
| [system term] | [user term] | [context] |

### Phase 3: STRUCTURE — Plan Page Hierarchy

Define the page structure before writing any content.

**Actions:**

1. Propose a page hierarchy to the user for approval before drafting
2. Name each page with a verb phrase (How to..., Getting started with..., Understanding...)
3. Identify which existing pages need updates vs. which are new
4. Map parent-child relationships

**Page Hierarchy Template:**

```markdown
## Proposed Page Hierarchy

**Parent**: [Space] > [Section]
  ├── [Parent Guide Page] (overview, links to children)
  │   ├── [Child Page 1: How to X]
  │   ├── [Child Page 2: How to Y]
  │   └── [Child Page 3: Reference — Fields and Values]
```

**GATE: Present hierarchy to user and wait for approval before drafting.**

### Phase 4: DRAFT — Generate Confluence Pages

Write each page using the approved structure and Confluence formatting.

**Actions:**

1. Draft the parent overview page first (brief, links to children)
2. Draft each child page in logical order
3. Apply the appropriate page template from `references/page-templates.md`
4. Mark all screenshot locations with `[SCREENSHOT: description]`
5. Apply plain language rules from `references/plain-language-checklist.md`
6. Add source reference panel at the bottom of each page

**Mandatory Page Elements (every page):**

```
1. H1 Title (verb phrase for task pages)
2. Brief intro paragraph (1-3 sentences, what the user achieves)
3. Prerequisites panel (info callout)
4. Numbered steps (for how-to and tutorial pages)
5. Screenshot placeholders at each UI step
6. Warning panels for irreversible actions
7. Next Steps / Related Pages section
8. Source Reference panel (collapsed note at bottom)
```

**Confluence Markdown/Storage Format Conventions:**

- Use `##` for H2 section headers within a page
- Use sentence case for all headings and page titles ("How to submit a request" not "How to Submit a Request")
- Use `:::info` / `:::warning` / `:::note` callout syntax (or Confluence panel macros)
- Use numbered lists for sequential steps
- Use bulleted lists for non-sequential items
- Use `**bold**` for UI element names (button labels, menu items, field names)
- Use code blocks for values the user must type exactly
- **Conditions before instructions:** State the condition first, then the action. Write "If you need to reset your password, click **Forgot Password**" — not "Click **Forgot Password** if you need to reset your password."
- Do not use "please" in instructions — it adds length without adding clarity ("Click Save" not "Please click Save")
- When screenshots are published, every image requires descriptive alt text for accessibility (e.g., alt="Submit button in the lower right of the form")

### Phase 5: REVIEW — Validate Before Publishing

Before pushing to Confluence, validate every page.

**Review Checklist:**

```markdown
### Per-Page Review

- [ ] Title is a verb phrase in sentence case matching the task
- [ ] Intro paragraph states what the user achieves (not how the system works)
- [ ] Every step is actionable (where to click, what to enter, what to expect)
- [ ] Conditions appear before instructions ("If X, do Y" — not "Do Y if X")
- [ ] No "please" in any instruction
- [ ] Every UI element has a screenshot placeholder
- [ ] No explanatory prose embedded inside how-to steps (explanation belongs on a separate page)
- [ ] Technical jargon is translated to audience vocabulary
- [ ] Warning panels cover all irreversible or permission-gated actions
- [ ] Next Steps section links to at least 2 related pages
- [ ] Source Reference panel is present with source page/file links
- [ ] Plain language checklist passed
- [ ] No capabilities are described that do not exist in the source material
- [ ] [Optional but recommended] At least one real user from the target audience attempted to follow the guide; blockers were resolved
```

**GATE: Present completed drafts to user for review before publishing.**

### Phase 6: PUBLISH — Write to Confluence

Push approved pages to the Confluence space using MCP tools.

**Actions:**

1. Identify the correct parent page ID using `confluence_search` or `confluence_get_page`
2. Create or update each page using `confluence_create_page` or `confluence_update_page`
3. Set the correct parent page for hierarchy
4. Log each published page URL
5. Confirm all pages are accessible before marking session complete

**Publishing Log Template:**

```markdown
### Published Pages

| Page Title | Action | URL | Parent |
|------------|--------|-----|--------|
| [title] | created | [url] | [parent title] |
| [title] | updated | [url] | [parent title] |
```

## State Block

Maintain state across conversation turns:

```
<confluence-guide-state>
phase: [INTAKE | ANALYZE | STRUCTURE | DRAFT | REVIEW | PUBLISH]
space: [Confluence space key]
section: [target parent page path]
audience: [End-User | Client | Power User]
sources_read: [count and list of source pages/files]
pages_planned: [count of pages in hierarchy]
pages_drafted: [count of completed drafts]
pages_published: [count of published pages]
pending_approval: [hierarchy | drafts | none]
last_action: [what was just completed]
next_action: [what happens next]
</confluence-guide-state>
```

**Example state progression:**

```
<confluence-guide-state>
phase: INTAKE
space: PRODHELP
section: User Guide > Account Management
audience: End-User
sources_read: 2 pages, 1 code file
pages_planned: 0
pages_drafted: 0
pages_published: 0
pending_approval: none
last_action: Source material read — spec page "Account Management API" and UserController.cs
next_action: Analyze tasks and build vocabulary translation table
</confluence-guide-state>
```

```
<confluence-guide-state>
phase: STRUCTURE
space: PRODHELP
section: User Guide > Account Management
audience: End-User
sources_read: 2 pages, 1 code file
pages_planned: 4
pages_drafted: 0
pages_published: 0
pending_approval: hierarchy
last_action: Page hierarchy drafted — 1 overview + 3 task pages
next_action: Awaiting user approval of hierarchy before drafting
</confluence-guide-state>
```

```
<confluence-guide-state>
phase: PUBLISH
space: PRODHELP
section: User Guide > Account Management
audience: End-User
sources_read: 2 pages, 1 code file
pages_planned: 4
pages_drafted: 4
pages_published: 4
pending_approval: none
last_action: All 4 pages published to PRODHELP space
next_action: Session complete
</confluence-guide-state>
```

## Output Templates

### Page: How-To Guide

```markdown
# How to [accomplish the task]

[One to three sentence introduction. State what the user will be able to do after
following this guide. Do NOT explain how the system works internally.]

---

:::info Prerequisites
Before you begin, make sure you have:
- [prerequisite 1]
- [prerequisite 2]
:::

## Steps

1. Navigate to **[Section]** in the top navigation bar.

   [SCREENSHOT: Top navigation bar with [Section] highlighted]

2. Click the **[Button Name]** button in the upper right corner.

   [SCREENSHOT: [Button Name] button location on the [Section] page]

3. In the **[Field Name]** field, enter [what to enter].

   [SCREENSHOT: Form with [Field Name] field highlighted]

4. Click **[Submit/Save/Confirm]** to save your changes.

   [SCREENSHOT: Confirmation dialog or success message]

The [result of the action] will appear in [where the result appears].

---

:::warning Important
[Include this panel only if the action is irreversible or has significant consequences.
Example: "Deleting a record cannot be undone. All associated data will be permanently removed."]
:::

## Troubleshooting

| If you see... | Do this... |
|---------------|------------|
| [error message or unexpected result] | [resolution step] |
| [error message or unexpected result] | [resolution step] |

## Next Steps

- [How to do the next logical task](link)
- [Related task the user commonly does next](link)
- [Return to: User Guide — Section Overview](link)

---

:::note Source Reference
This guide was generated from:
- Confluence: [Source Page Title](link) (version [N], [date])
- Code: [file path] ([commit or date])
:::
```

### Page: Tutorial (Getting Started)

```markdown
# Getting Started with [Feature/System]

Welcome to [Feature/System]. This tutorial will walk you through [what the user
will set up or accomplish]. By the end, you will be able to [concrete outcome].

**This tutorial takes approximately [N] minutes.**

---

:::info What you will need
- [Account type / access level required]
- [Any setup that must be done first]
:::

## Part 1: [First milestone]

In this section, you will [what the user does in Part 1].

### Step 1: [Action]

[Instruction for step 1.]

[SCREENSHOT: description]

### Step 2: [Action]

[Instruction for step 2.]

[SCREENSHOT: description]

You have completed Part 1. You should now see [what success looks like].

---

## Part 2: [Second milestone]

[Continue pattern...]

---

## What you accomplished

In this tutorial, you:
- [Accomplishment 1]
- [Accomplishment 2]
- [Accomplishment 3]

## What to explore next

- [How to do the most common next task](link)
- [How to customize [feature]](link)
- [Reference: All available options](link)

---

:::note Source Reference
This guide was generated from:
- Confluence: [Source Page Title](link)
- Code: [file path]
:::
```

### Page: Reference Page

```markdown
# [Feature Name] — Reference

This page documents all [fields / options / values] available in [Feature Name].
For step-by-step instructions, see [How to use Feature Name](link).

---

## [Section: e.g., Fields]

| Field | Description | Required | Values |
|-------|-------------|----------|--------|
| **[Field Name]** | [What this field does] | Yes / No | [valid values or format] |

## [Section: e.g., Status Values]

| Status | Meaning | What to do |
|--------|---------|------------|
| [value] | [plain language explanation] | [action the user should take] |

---

:::note Source Reference
This reference was generated from:
- Confluence: [Source Page Title](link)
- Code: [file path] — [class/method name]
:::
```

### Page: Overview / Landing Page

```markdown
# [Section Name] User Guide

[Two to four sentence introduction: what this section of the guide covers and who
it is for. State the business outcome the user achieves, not the technical features.]

---

## In this section

| Page | What it covers |
|------|----------------|
| [Getting Started with X](link) | Set up your account and complete your first [task] |
| [How to do Y](link) | [One sentence description] |
| [How to do Z](link) | [One sentence description] |
| [Reference: Options and Values](link) | Complete list of settings and their meanings |

---

:::info Need help?
If you cannot find what you are looking for, contact [support contact or link to
help page].
:::
```

## AI Discipline Rules

### CRITICAL: Never Invent Capabilities

Documentation that describes features that do not exist destroys user trust.

```
WRONG: Describing a "bulk export" feature after reading a spec that only mentions
       single-record export, because it "seems like it should be there."

RIGHT: Document only what exists in the source spec or code. If a feature seems
       missing from the source material, flag it for the user:
       "[NOTE: No bulk export capability was found in the source material.
        Confirm whether this feature exists before publishing.]"
```

### CRITICAL: Translate Before Writing

Every technical term must be translated to the audience's vocabulary before drafting begins.

```
WRONG: "Navigate to the entity resolution queue to begin deduplication."
       (Technical vocabulary, incomprehensible to end-users)

RIGHT: "Navigate to the Duplicate Records section to review and merge
       matching entries."
       (Audience vocabulary, outcome-focused)
```

### CRITICAL: Gate Before Publishing

Never push to Confluence without user approval of (1) the page hierarchy and (2) the drafted content.

```
WRONG: Drafting and publishing in one uninterrupted sequence without
       showing the user the output first.

RIGHT:
  1. Present hierarchy → wait for approval
  2. Draft pages → present to user → wait for approval
  3. Publish approved pages
  4. Log published URLs for user verification
```

### CRITICAL: Screenshot Placeholders Are Not Optional

Every UI step without a screenshot is a guide that will fail real users.

```
WRONG: "Click the Submit button." (No screenshot, user cannot find the button)

RIGHT: "Click the **Submit** button in the lower right of the form.
       [SCREENSHOT: Submit button location on the form — button is blue,
        labeled 'Submit Request', in the lower right corner]"
```

### REQUIRED: One Task Per Page

```
WRONG: A page titled "User Management" that covers adding users, removing
       users, resetting passwords, and managing roles — all on one page.

RIGHT:
  - Overview page: "User Management" (links to children)
  - Child: "How to add a new user"
  - Child: "How to remove a user"
  - Child: "How to reset a user's password"
  - Child: "How to assign roles"
```

### REQUIRED: Conditions Before Instructions

Place the condition before the action in every conditional instruction. (Google Developer Style Guide)

```
WRONG: "Click Forgot Password if you have lost access to your account."
RIGHT: "If you have lost access to your account, click Forgot Password."
```

This applies to warnings, prerequisites, and inline conditional steps. Readers scan for
conditions first to decide whether a step applies to them.

### REQUIRED: No Explanation Inside How-To Steps

How-to guides are for users who already know the context — they need the steps, not the theory.
Embedding explanatory prose inside how-to steps mixes content types (Diátaxis anti-pattern).

```
WRONG: Step 3: "Click Approve. The system uses a two-stage workflow where
       approvals are first staged in a queue and then promoted to the active
       state via a background job. This ensures consistency across distributed
       nodes. Click Approve to begin this process."

RIGHT: Step 3: "Click Approve."

       [SCREENSHOT: Approve button]

       If you want to understand how the approval process works, see
       [Understanding the Approval Workflow](link).
```

### REQUIRED: Source Reference on Every Page

Every published guide must include a source reference note panel so future writers know where the information came from.

```
WRONG: Publishing a page with no provenance — no one knows if it is accurate
       or outdated.

RIGHT: Every page ends with a collapsed note panel:
  "This guide was generated from:
   - Confluence: [Source Spec Page](link) (version N, date)
   - Code: src/handlers/UserHandler.cs (commit abc1234)"
```

## Anti-Patterns Table

| Anti-Pattern | Description | Why It Fails | Correct Approach |
|--------------|-------------|-------------|-----------------|
| **Tech-to-User Dump** | Copying spec page content verbatim into the user guide. | Spec pages are written for engineers. They assume system knowledge, use internal vocabulary, and describe implementation details. End-users cannot act on them. | Analyze the spec for user tasks, translate vocabulary, and rewrite in task-oriented, plain language. |
| **God Page** | One massive page covering everything about a feature. | Readers cannot find what they need. Search results are ambiguous. Long pages are not read — they are scrolled. Updates break the entire page when the feature changes. | One page, one task. Use parent-child hierarchy for navigation. |
| **Passive Voice Prose** | "The form can be submitted by clicking the Submit button." | Passive voice is harder to read, longer, and hides who does what. Increases cognitive load for all readers, especially non-native speakers. | Active voice only: "Click Submit to save the form." |
| **Screenshot Debt** | Publishing guides with "[SCREENSHOT: TBD]" placeholders that are never filled in. | Users cannot find UI elements without visual references. Guides become immediately unusable for anyone unfamiliar with the UI. | Block publishing until screenshots are provided OR explicitly agreed to defer with a dated TODO. |
| **Jargon Bleed** | Using technical terms without translation: "authenticate via OAuth2", "provision an IAM role", "instantiate a new tenant record". | End-users and clients do not know these terms. They stop reading. They call support. | Build a vocabulary table during ANALYZE phase. Substitute audience terms throughout. |
| **Missing Prerequisites** | Jumping straight into steps without noting what the user must have or know first. | Users fail at step 1 because they lack access, a required dependency, or background knowledge. They blame the docs. | Always include a Prerequisites info panel at the top of every how-to and tutorial page. |
| **Dead-End Page** | A page that ends after the last step with no navigation forward. | Users complete the task and have no context for what to do next. They navigate away and lose their guide context. | Every page ends with a Next Steps or Related Pages section linking to 2-3 logical follow-on pages. |
| **Version Blindness** | Publishing guides with no indication of when they were written or what version they apply to. | Features change. A guide that was accurate in v1.2 is wrong in v2.0. Readers have no way to know if the guide applies to their version. | Note the version or date in the source reference panel and in the intro paragraph if version-specific. |
| **Explanation as How-To** | Writing "How the system processes requests" when the user needs "How to submit a request". | Explanation guides serve stakeholder curiosity. How-to guides serve user tasks. Mixing them produces neither effectively. | Separate explanation content onto its own page type. Keep how-to pages purely task-focused. |
| **No Warning Panels** | Documenting irreversible or high-consequence actions (delete, deactivate, submit final) without warning callouts. | Users make mistakes that cannot be undone. They lose data, lock accounts, or submit incorrect information with no chance to correct it. | Add a warning panel before any step that is irreversible or has significant business impact. |

## Error Recovery

### Source Material Is Incomplete or Ambiguous

The spec page or code does not fully explain the feature's behavior or user workflow.

**Indicators:**
- Spec page describes the system design but not the user workflow
- Code shows multiple code paths but the correct one for the user's context is unclear
- Critical steps are missing from the source material

**Recovery Actions:**
1. Stop — do not guess or invent missing steps
2. List the specific gaps explicitly in a CLARIFICATION REQUEST to the user
3. Ask targeted questions: "The spec describes two export options but doesn't indicate which is available to end-users. Can you clarify?"
4. Optionally: draft the known sections and mark gaps with `[CLARIFICATION NEEDED: describe the gap]`
5. Do not publish until all gaps are resolved

### Target Confluence Space or Page Not Found

The MCP tool cannot locate the target space or parent page.

**Indicators:**
- `confluence_search` returns no results for the space key
- `confluence_get_page` returns 404 or permission error
- Parent page title is ambiguous (multiple matches)

**Recovery Actions:**
1. Ask the user to provide the exact space key and parent page URL or page ID
2. Use `confluence_search` with narrower terms to identify the correct space
3. List candidate pages for user selection if multiple matches exist
4. If access is denied, flag that the MCP connection may need re-authentication
5. Do not create pages in the wrong location — confirm parent page identity before publishing

### User Guide Is Out of Scope of Source Material

The user requests a guide for a feature that does not appear in the source pages or code.

**Indicators:**
- No matching content in spec pages for the requested topic
- Code search reveals no relevant implementation
- The feature may be planned but not built

**Recovery Actions:**
1. State explicitly: "[CANNOT COMPLETE]: No source material found for [requested topic]."
2. Offer to search additional Confluence pages or code locations
3. Ask the user to provide the correct source material
4. If the feature is in-progress, offer to draft a placeholder page with "coming soon" language pending source material
5. Never generate content about features that cannot be verified in source material

### Audience Tier Is Unclear

The user has not specified who the guide is for, and the appropriate vocabulary and depth are ambiguous.

**Indicators:**
- Request says "write a user guide" without specifying End-User, Client, or Power User
- Source material serves multiple audience types
- The Confluence section contains guides for multiple audiences

**Recovery Actions:**
1. Ask: "Who is the primary audience for this guide — end-users who operate the system day-to-day, clients and stakeholders who need business-level understanding, or power users who configure and administer the system?"
2. If the guide will be read by multiple audiences, offer to create separate pages for each tier
3. Default to the most accessible tier (End-User) if the user cannot specify
4. Note the assumed audience in the state block and in the source reference panel

## Integration with Other Skills

- **`doc-sync`** — When existing Confluence pages are detected as stale relative to code changes, hand off to `doc-sync` for staleness analysis before generating updated guides. The `confluence-guide-writer` generates new content; `doc-sync` identifies and reconciles stale content. Use together when updating an existing user guide section after a product release.

- **`jira-comment-writer`** — After publishing a new guide section, use `jira-comment-writer` to add a plain-language comment to the relevant Jira ticket noting that documentation has been published and linking to the Confluence pages.

- **`context-builder-agent`** — When starting a documentation session for a complex feature, use `context-builder-agent` first to gather session context (recent changes, relevant ADRs, affected files). This context becomes input to the INTAKE phase, ensuring the guide reflects the current state of the codebase.

- **`architecture-journal`** — For explanation-type pages targeted at stakeholders (Why does the system work this way?), cross-reference ADRs maintained by `architecture-journal` to provide accurate rationale without inventing design decisions.
