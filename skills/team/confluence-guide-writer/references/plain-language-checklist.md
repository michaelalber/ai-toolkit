# Plain Language Checklist — Confluence User Guide Writer

Run this checklist on every draft before presenting to the user for review.
Fix all failures before marking the DRAFT phase complete.

---

## Vocabulary

- [ ] No unexpanded acronyms on first use (write out the full term, then abbreviation in parentheses)
- [ ] No technical jargon that the target audience would not recognize
- [ ] All system terms translated to audience vocabulary (see vocabulary table from ANALYZE phase)
- [ ] UI element names match what appears on screen (button labels, menu names, field names)
- [ ] Consistent terminology throughout — one term per concept, used the same way every time
- [ ] No idioms or culturally specific phrases ("home stretch", "ball is in your court", "moving the needle") — use plain equivalents
- [ ] All link text is descriptive — no "click here", "read more", "here", or "this page"

## Sentences

- [ ] Active voice throughout ("Click Submit" not "The Submit button should be clicked")
- [ ] Average sentence length under 20 words
- [ ] No nominalizations: "configuration of" → "configuring", "submission of" → "submitting"
- [ ] No double negatives: "not unable to" → "able to"
- [ ] Each sentence contains one idea
- [ ] No buried verbs: "make a decision" → "decide", "provide assistance" → "help"
- [ ] No "please" in instructions — adds length without adding meaning
- [ ] Conditions appear before instructions: "If X, do Y" — not "Do Y if X"
- [ ] No hedging language: "should work", "might be available", "you may want to consider" — be specific or state the uncertainty directly
- [ ] Present tense in introductions and descriptions: "This guide walks you through..." not "This guide will walk you through..."
- [ ] No pre-announcing: do not say "In this section I will explain X" — just explain X
- [ ] Reader addressed as "you" — no "the user", "users", or "one" when the reader is meant

## Structure

- [ ] H1 title is a verb phrase in sentence case ("How to submit a request" not "How to Submit a Request")
- [ ] Intro paragraph states what the user achieves (1–3 sentences, no jargon)
- [ ] Prerequisites listed before steps, not embedded in step text
- [ ] Steps are numbered, sequential, and each step is one action
- [ ] Each step includes where to navigate, what to click/enter, and what to expect next
- [ ] Warning panels appear BEFORE the step that requires caution, not after
- [ ] No explanatory prose embedded inside how-to steps (link to an Explanation page instead)
- [ ] Next Steps section present at the end of every page

## Formatting

- [ ] UI element names are **bold** (button labels, menu items, field names)
- [ ] Values the user must type exactly are in `code format`
- [ ] Screenshot placeholders at every step that involves clicking a UI element
- [ ] Screenshot placeholder format: `[SCREENSHOT: description of what to capture]`
- [ ] When screenshots are eventually published, each image has descriptive alt text for accessibility
- [ ] Info panels for prerequisites and helpful context
- [ ] Warning panels only for irreversible or high-consequence actions
- [ ] Note panels for source references at the bottom of every page
- [ ] No walls of prose — maximum 3 sentences in any paragraph outside of Explanation pages

## Completeness

- [ ] Every numbered step is independently actionable — a new user could follow without asking a question
- [ ] Troubleshooting section covers the most common error states visible in source material
- [ ] Source reference panel present and links to actual source pages/files
- [ ] Version or "last verified" date noted in source reference panel
- [ ] No capabilities described that do not appear in source material
- [ ] No steps describe actions that the audience does not have permission to take (check role/permission requirements)

---

## Audience-Tier Specific Checks

### End-User Tier

- [ ] No technical architecture vocabulary (no: API, endpoint, database, entity, schema, provisioning)
- [ ] Reading level approximately Grade 8 (short sentences, common words)
- [ ] Every step is a UI action — no CLI commands, no config file edits, no code
- [ ] Outcomes described in terms of user goals, not system states ("your request is saved" not "the record is persisted")

### Client / Stakeholder Tier

- [ ] Business outcomes foregrounded ("reduce processing time by X" not "system executes Y")
- [ ] No implementation details that don't affect the business outcome
- [ ] KPIs or business metrics referenced where source material includes them
- [ ] Explanation pages separate from how-to pages (stakeholders read explanations, not steps)

### Power User / Admin Tier

- [ ] Technical terms retained where power users need them (configuration keys, role names, permission scopes)
- [ ] Edge cases and configuration options documented in expandable sections
- [ ] CLI or API instructions formatted in code blocks with copy-able text
- [ ] Links to reference pages for full field/option documentation

---

## Common Fixes

| Problem | Before (wrong) | After (correct) |
|---------|----------------|-----------------|
| Passive voice | "The form is submitted by clicking Save" | "Click **Save** to submit the form" |
| Nominalization | "The configuration of the settings" | "Configuring the settings" |
| Jargon | "Authenticate via your IAM credentials" | "Log in with your username and password" |
| Buried verb | "Make a selection from the dropdown" | "Select [option] from the dropdown" |
| Missing navigation | "Click Submit" | "Click **Submit** in the lower right of the form" |
| Ambiguous pronoun | "It will update when you click" | "The status will update when you click **Save**" |
| Missing article | "User must have Admin role" | "You must have the **Admin** role" |
| Present continuous | "You are now configuring the..." | "Configure the..." |
| Double modal | "You might want to consider..." | "Consider..." |
| Hedge language | "This should usually work" | "This will [specific outcome]" |
| "Please" in instructions | "Please click **Save**" | "Click **Save**" |
| Condition after action | "Click **Forgot Password** if you lost access" | "If you lost access, click **Forgot Password**" |
| Explanation in how-to step | "Click **Approve**. The system uses a queue-based workflow that..." | "Click **Approve**. To learn how approval works, see [Understanding Approvals](link)." |
| Title case headings | "How to Submit a Reimbursement Request" | "How to submit a reimbursement request" |
| Future tense intro | "This guide will walk you through..." | "This guide walks you through..." |
| Future tense outcome | "By the end, you will be able to export..." | "By the end, you can export..." |
| Pre-announcing | "In this section, I will explain how to configure..." | Remove — just explain. Or: "Configure [feature] as follows." |
| Third person distance | "The user should click **Submit**" | "Click **Submit**" |
| Weak link text | "For more information, [click here](link)" | "See [Export options reference](link)" |
| Idiom | "We're in the home stretch" | "This is the final step." |
| Hedge language | "This should usually complete in a few seconds" | "This completes in under five seconds." or "Completion time varies — typically under five seconds." |
