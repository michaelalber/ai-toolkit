# Comment Templates

Ready-to-use templates for each comment type. Placeholders in `[brackets]` are filled by the skill during drafting.

---

## Progress Update

Use when: work is actively in progress, nothing is blocking, timeline is on track.

```
**Update — [Brief topic, e.g., "User login flow"]**

[One sentence: what was completed or reached this period.]
[One sentence: current state — what's being worked on now.]
[One sentence: expected next milestone or completion date.]
```

**Example:**

> **Update — Payment form**
>
> The payment form now correctly validates card numbers and displays error messages in plain language.
> We're currently connecting it to the billing system so submissions are processed in real time.
> Expected to be fully functional by end of week.

---

## Completion

Use when: the work described in the issue is done and confirmed working.

```
**Completed — [Feature or task name]**

[One sentence: what is now working and who benefits from it.]
[One sentence (optional): any limitation, known edge case, or follow-up item to be aware of.]
[One sentence: what the stakeholder should do next, if anything — e.g., review, test, sign off.]
```

**Example:**

> **Completed — Export to PDF**
>
> Users can now export any report to PDF directly from the Reports page.
> The first export on a large report (100+ rows) may take up to 15 seconds — we'll optimize this in a follow-up.
> Feel free to test this in the staging environment and let us know if it meets your expectations.

---

## Blocker

Use when: work has stopped or slowed due to a dependency, missing information, or unexpected issue.

```
**Blocker — [Brief description of what's affected]**

[One sentence: what is currently blocked and since when (if relevant).]
[One sentence: the reason — keep it non-technical and factual. Avoid blame.]
[One sentence: what's being done about it.]
[One sentence: impact on timeline, if any. Be specific.]
```

**Example:**

> **Blocker — Report export feature**
>
> Work on the report export feature is paused.
> We're waiting on access credentials from the third-party printing service before we can complete the connection.
> We've sent the request and are following up — expecting a response by Wednesday.
> If credentials arrive Wednesday as expected, we remain on track for the Friday delivery.

---

## Decision Needed

Use when: the team cannot proceed without input or approval from the stakeholder.

```
**Action needed — [Brief description of the decision]**

[One sentence: context — what the team is working on and why a decision is needed.]
[Bullet list of options, 2–3 max. Each option: what it is, one key implication.]
[One sentence: the deadline for the decision and what happens if it slips.]
```

**Example:**

> **Action needed — Notification email design**
>
> We're ready to build the automated notification emails but need your input on the format before we begin.
>
> - **Option A — Plain text email:** Simple, no branding. Fast to build, works in all email clients.
> - **Option B — Branded HTML email:** Matches your visual identity. Takes an extra 2–3 days to build and will need brand assets (logo, colors) from your team.
>
> Please let us know your preference by Thursday so we can stay on schedule for the end-of-month delivery.

---

## Combined Update

Use when: two closely related items need to be communicated together. Limit to two items — any more should be separate comments or a summary table.

```
**Update — [Issue or sprint area]**

**[Item 1 label]:** [One sentence — status and key detail.]
**[Item 2 label]:** [One sentence — status and key detail.]

[One sentence: overall status — on track, at risk, or needs attention.]
[One sentence: next milestone or action.]
```

**Example:**

> **Update — Checkout flow**
>
> **Cart page:** Complete and live in the test environment.
> **Payment page:** In progress — the form is built, we're now connecting it to the payment processor.
>
> Overall the checkout flow remains on track.
> We expect the full flow to be ready for your review by next Tuesday.

---

## Tone Variants

The same template can be adjusted for audience:

| Tone | Signal words | Typical audience |
|------|-------------|-----------------|
| **Formal** | "We would like to inform you", complete sentences, no contractions | External client, executive |
| **Professional-friendly** | Direct sentences, occasional "we're", "you'll" | Project manager, account manager |
| **Casual** | Conversational, first names, short sentences | Trusted internal PM, close team |

**Default is professional-friendly.** Use formal for external clients or escalated situations. Use casual only when you know the relationship well.
