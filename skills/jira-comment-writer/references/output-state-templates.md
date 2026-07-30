# Output & State Templates

The skill emits a `<jira-comment-state>` block with every response. This file holds the
three full presentation templates referenced by `SKILL.md`, plus the bare intake prompt.

---

## Intake Prompt (when invoked without context)

```
To write a clear stakeholder comment, tell me:

1. What happened or what did you work on? (Technical is fine — I'll translate it)
2. What's the current status? (In progress / blocked / complete / needs a decision)
3. Does this affect the timeline or scope in any way?
4. What's the next step, and who owns it?

Optionally: Who's reading this — an external client, your PM, or someone else?
```

If the user provides context upfront, proceed directly to DRAFT — do not repeat these questions.

---

## Intake Opening (when no context is provided)

```markdown
To write a clear comment for your stakeholders, I need a quick picture of the situation.

**Tell me:**
1. What happened or what did you work on? (Technical is fine — I'll translate it)
2. What's the current status? (In progress / blocked / complete / needs a decision)
3. Any impact on the timeline or scope?
4. What's the next step, and who owns it?

*Optional: Who's reading this — an external client, your PM, or someone else?*

<jira-comment-state>
mode: intake
issue_summary: unknown
status: unknown
audience: unknown
tone: professional_friendly
draft_version: 0
last_action: session opened
next_action: awaiting user context
</jira-comment-state>
```

---

## Draft Presentation

```markdown
Here's a draft comment for [audience type]:

---

[comment body]

---

Does this capture what you want to say, or should I adjust the tone, level of detail, or how the next step is framed?

<jira-comment-state>
mode: draft
issue_summary: [summary]
status: [status]
audience: [audience]
tone: [tone]
draft_version: 1
last_action: draft produced
next_action: await user feedback or approval
</jira-comment-state>
```

---

## Refined Draft

```markdown
Updated draft:

---

[revised comment body]

---

**What changed**: [one-line note on what was adjusted and why]

<jira-comment-state>
mode: refine
...
draft_version: [N]
last_action: draft refined — [brief description of change]
next_action: await approval or further refinement
</jira-comment-state>
```
