# Page Templates — Confluence User Guide Writer

Confluence-ready templates in storage format for each guide type. Copy and adapt
during the DRAFT phase. All templates use Confluence wiki markup compatible with
the REST API `storage` format.

---

## Template 1: How-To Guide (Most Common)

**Use when:** The user wants to accomplish one specific task.

**Title convention:** "How to [verb] [object]" — e.g., "How to submit a reimbursement request"

```markdown
# How to [Task Name]

[1–3 sentence intro. State what the user achieves. Active voice. No jargon.]

---

> **Prerequisites**
> Before you begin:
> - [access level or role required]
> - [any prior setup required]
> - [any system state that must exist first]

## Steps

1. [Navigate to location]. Click **[Menu Item]** in the [navigation area].

   [SCREENSHOT: [Menu Item] highlighted in [navigation area]]

2. [What to do next]. Enter [value] in the **[Field Name]** field.

   [SCREENSHOT: [Field Name] field on [page name]]

3. [Continue with each UI action.] Click **[Button Name]**.

   [SCREENSHOT: [Button Name] button — describe its appearance and location]

4. [Final confirmation action.]

   [SCREENSHOT: Success confirmation message or result state]

The [result] will [appear/update/send] within [timeframe if known].

---

> **Warning**
> [Include ONLY if the action is irreversible or high-consequence. Delete this
>  panel if not applicable.]
> [Warning text: what can go wrong and what to do if it does.]

---

## Troubleshooting

| If you see... | What it means | What to do |
|---------------|---------------|------------|
| [error message] | [plain-language explanation] | [resolution step] |
| [unexpected result] | [plain-language explanation] | [resolution step] |

---

## Next Steps

- [Most logical next task](link)
- [Related task](link)
- [Back to: Section Overview](link)

---

> **Note — Source Reference**
> This guide was generated from:
> - Confluence: [Source Page Title](link) (v[N], [date])
> - Code: [file path] ([commit/date])
> Last verified: [date]
```

---

## Template 2: Tutorial (Getting Started)

**Use when:** Onboarding a new user to a feature or system for the first time.

**Title convention:** "Getting started with [Feature]" or "[Feature]: Your first [task]"

```markdown
# Getting Started with [Feature Name]

Welcome to [Feature Name]. This tutorial walks you through [what the user
accomplishes]. By the end, you can [concrete, measurable outcome].

**Time required:** approximately [N] minutes.

---

> **What you will need**
> - [Account type / permission level]
> - [Any prior configuration or setup]
> - [Any information to have on hand]

---

## Part 1: [First milestone title]

In this part, you [what the user sets up or learns].

### 1.1 [First action]

[Instruction text.]

[SCREENSHOT: description of what the screenshot shows]

### 1.2 [Second action]

[Instruction text.]

[SCREENSHOT: description]

**Check your work:** After completing Part 1, you should see [what success looks
like — describe the UI state].

---

## Part 2: [Second milestone title]

In this part, you [what the user sets up or learns].

### 2.1 [First action]

[Instruction text.]

[SCREENSHOT: description]

**Check your work:** [Success indicator for Part 2.]

---

## Part 3: [Third milestone title — add or remove parts as needed]

[Continue pattern.]

---

## What you accomplished

You have successfully:
- [Accomplishment 1 — state what was done, not how]
- [Accomplishment 2]
- [Accomplishment 3]

## What to do next

- [First common next task](link)
- [Second common next task](link)
- [Reference: all available options](link)

---

> **Note — Source Reference**
> This tutorial was generated from:
> - Confluence: [Source Page Title](link) (v[N], [date])
> - Code: [file path] ([commit/date])
> Last verified: [date]
```

---

## Template 3: Reference Page

**Use when:** Documenting all fields, options, statuses, or values for a feature.

**Title convention:** "[Feature Name] — Reference" or "[Feature Name]: Fields and Values"

```markdown
# [Feature Name] — Reference

This page lists all [fields / options / statuses / values] available in
[Feature Name]. For step-by-step instructions, see [How to use Feature Name](link).

---

## [Section: e.g., Form Fields]

| Field | Description | Required | Accepted Values |
|-------|-------------|----------|-----------------|
| **[Field Name]** | [Plain-language description of what this field does] | Yes / No | [format, options, or range] |
| **[Field Name]** | [Description] | Yes / No | [values] |

---

## [Section: e.g., Status Values]

| Status | What it means | What to do |
|--------|---------------|------------|
| **[Status]** | [Plain-language meaning] | [User action if any] |
| **[Status]** | [Meaning] | [Action] |

---

## [Section: e.g., Permission Levels]

| Role | What they can do | What they cannot do |
|------|------------------|---------------------|
| **[Role Name]** | [Capabilities] | [Restrictions] |

---

## Related pages

- [How to [primary task for this feature]](link)
- [Getting Started with [Feature]](link)
- [Back to: Section Overview](link)

---

> **Note — Source Reference**
> This reference was generated from:
> - Confluence: [Source Page Title](link) (v[N], [date])
> - Code: [file path] — [class/method/enum name] ([commit/date])
> Last verified: [date]
```

---

## Template 4: Overview / Landing Page

**Use when:** Creating the parent page for a guide section. Links to all child pages.

**Title convention:** "[Section Name] Guide" or "[Section Name] — User Guide"

```markdown
# [Section Name] Guide

[2–4 sentence intro. Describe who this guide is for and what business outcome
they achieve. Do NOT describe technical features. Use present tense and address
the reader as "you". Example: "This guide helps [team/role] complete [business
tasks] using [product name]. Use these pages to [what the reader can do]."]

---

## In this section

| Page | What it covers |
|------|----------------|
| [Getting Started with X](link) | Set up your account and complete your first [task] |
| [How to do Y](link) | [One-sentence description of the task and outcome] |
| [How to do Z](link) | [One-sentence description] |
| [How to do W](link) | [One-sentence description] |
| [Reference: Fields and Options](link) | Complete list of settings and their meanings |

---

## New here?

Start with [Getting Started with [Feature]](link) — it takes approximately
[N] minutes and walks you through the most common workflow.

---

> **Info**
> Can't find what you're looking for? Contact [support contact or link to
> help/support page] or search this space for [keywords].

---

> **Note — Source Reference**
> This overview was generated from:
> - Confluence: [Source Page Title](link)
> Last verified: [date]
```

---

## Template 5: Explanation Page (Stakeholder-Facing)

**Use when:** Stakeholders or clients need to understand *why* the system works a
certain way, or what the high-level business logic is. Not task-oriented.

**Title convention:** "Understanding [Concept]" or "Why [Feature] works this way"

```markdown
# Understanding [Concept Name]

[2–4 sentence intro framing the business problem this concept addresses. Speak
in business terms — outcomes, costs, risks — not technical terms.]

---

## The business problem

[2–4 paragraphs explaining the problem this feature or workflow addresses.
Use business language. Cite real consequences of the problem: cost, risk,
compliance, user friction.]

## How [Feature/System] addresses it

[2–4 paragraphs explaining the solution at a business level. What does it do?
What is the result? What does the user/business gain?]

Do NOT describe implementation details. Do NOT use technical architecture
vocabulary. Describe outcomes.

## What this means for [your role]

[1–2 paragraphs tailored to the specific audience: what they need to know,
what decisions they can now make, or what they should expect.]

---

## Key terms

| Term | Plain-language definition |
|------|--------------------------|
| [Term as used in the system] | [What it means in business context] |

---

## Related pages

- [How to [primary task related to this concept]](link)
- [Reference: [relevant reference page]](link)

---

> **Note — Source Reference**
> This page was generated from:
> - Confluence: [Source Page Title](link) (v[N], [date])
> Last verified: [date]
```
