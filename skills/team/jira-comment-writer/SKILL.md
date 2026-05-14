---
name: jira-comment-writer
description: >
  Plain-language Jira comment drafter for project managers and clients. Translates
  technical progress, blockers, and decisions into clear, jargon-free updates.
  Use when adding a comment to a Jira issue that a non-technical stakeholder will read.
  Do NOT use when the audience is engineers or technical peers — use pr-feedback-writer
  instead; this skill targets non-technical stakeholders only.
---

# Jira Comment Writer

> "The ability to simplify means to eliminate the unnecessary so that the necessary may speak."
> -- Hans Hofmann

> "If you can't explain it simply, you don't understand it well enough."
> -- Attributed to Albert Einstein

## Core Philosophy

A comment on a Jira issue is not a status log for engineers — it is a signal to a project manager or client that something happened, what it means, and what comes next. The people reading these comments care about outcomes, timelines, and decisions. They do not need to know which function was refactored or which library was upgraded. They need to know: **Is this moving? Are we on track? Do I need to do anything?**

This skill bridges the gap between technical work and stakeholder communication. You describe what you did in whatever terms come naturally — technical is fine. The skill turns that into a comment your PM or client can read, understand, and act on in thirty seconds.

**Voice and tone target (Google Developer Style Guide):** Write like a knowledgeable colleague writing to another professional — conversational, friendly, and respectful, without being stiff or overly casual. Avoid jargon, hedging language ("it would appear", "hopefully", "at this point in time"), and culturally specific idioms ("home stretch", "ball in your court", "move the needle"). Simple and consistent writing also makes comments more accessible to readers with varying levels of English proficiency.

**Three things every stakeholder comment must answer:**
1. **What happened?** — Progress made, blocker encountered, decision taken
2. **What does it mean?** — Impact on the overall goal, timeline, or scope
3. **What's next?** — Next action, expected date, or what you need from them

**What this skill is NOT:**
- It is NOT a log of implementation details
- It is NOT a place to explain technical decisions to other engineers
- It is NOT a status meeting transcript

## Domain Principles

| # | Principle | Applied As |
|---|-----------|------------|
| 1 | **Outcome over activity** | "The login page now works on mobile devices" not "Refactored the AuthController to handle responsive viewport breakpoints" |
| 2 | **Plain language first** | Every technical term that appears in a draft earns its place. If you can say it without jargon, do. |
| 3 | **One idea per comment** | A comment covering five topics gets skimmed. A comment covering one topic gets read. |
| 4 | **Be honest about blockers** | Downplaying blockers creates surprises. State the blocker, its impact, and the mitigation. Clear honesty is always better than vague reassurance. |
| 5 | **Name the next action explicitly** | "Work continues" is not an action. "Estimated completion by Friday" or "Waiting on your approval to proceed" is. |
| 6 | **Match tone to audience** | A formal client comment differs from an update to a friendly PM. Ask when unsure; default to professional-friendly. |
| 7 | **Never alarm, never hide** | Frame bad news clearly and factually. Don't soften it into invisibility. Don't dramatize it into crisis. |
| 8 | **No hedging** | Hedging ("it should be done soon", "we think this might work", "hopefully Friday") signals uncertainty and erodes trust. If you're uncertain, say so explicitly: "We expect completion by Friday, but this depends on [specific condition]." Precision beats false confidence and vague reassurance equally. |
| 9 | **Global readability** | Write for readers with varying levels of English proficiency. Avoid idioms: "We're in the home stretch" → "We're nearly finished." "The ball is in your court" → "Your input is needed to proceed." "Move the needle" → "Make measurable progress." Plain language is both clearer and more inclusive. |

## Workflow

### Phase 1: INTAKE — Gather Context

The skill asks for enough information to draft a comment that accurately represents the situation.

**Required inputs:**

| Input | Purpose |
|-------|---------|
| What you worked on / what happened | The raw material for the comment |
| Current status | In progress, blocked, complete, or needs decision |
| Impact on timeline or scope | Any change the stakeholder should know about |
| Next step | What happens next and who owns it |

**Optional inputs:**

| Input | Purpose |
|-------|---------|
| Audience tone | Formal (external client), professional-friendly (PM), or casual (trusted internal PM) |
| Any context the reader already has | Avoids re-explaining what they know |
| Specific things NOT to mention | Technical details the user wants kept internal |

**Intake prompt the skill uses when invoked without context:**

```
To write a clear stakeholder comment, tell me:

1. What happened or what did you work on? (Technical is fine — I'll translate it)
2. What's the current status? (In progress / blocked / complete / needs a decision)
3. Does this affect the timeline or scope in any way?
4. What's the next step, and who owns it?

Optionally: Who's reading this — an external client, your PM, or someone else?
```

**If the user provides context upfront**, proceed directly to DRAFT — do not repeat the intake questions.

### Phase 2: DRAFT — Write the Comment

Using the gathered context, produce a plain-language comment in the appropriate format.

**Comment format selection:**

| Situation | Format to use |
|-----------|--------------|
| Progress update | Progress Update template |
| Work completed | Completion template |
| Blocker or delay | Blocker template |
| Question or decision needed | Decision Needed template |
| Multiple items | Combined template (max two topics per comment) |

See [Comment Templates](references/comment-templates.md) for the full template set.

**Jargon translation rules:**

| Avoid | Say instead |
|-------|------------|
| "Refactored the codebase" | "Reorganized the code to make future changes faster" |
| "Fixed a null pointer exception" | "Fixed an error that caused the page to crash in certain situations" |
| "Deployed to staging" | "Uploaded the update to our test environment" |
| "API integration" | "Connection between [System A] and [System B]" |
| "The build is broken" | "A recent change caused an issue that's blocking testing — being investigated now" |
| "Technical debt" | "An area that needs cleanup to prevent future problems" |
| "Sprint capacity" | "Available time this week" |
| "Merge conflict" | "Two overlapping changes that need to be reconciled before proceeding" |

### Phase 3: REFINE — Iterate

After producing the draft, the skill presents it and asks one question:

> "Does this capture what you want to say, or should I adjust the tone, level of detail, or how the next step is framed?"

Refinement loops are fast and focused. Common adjustments:
- **Too formal / too casual**: Adjust register
- **Too much detail**: Strip to essential facts
- **Timeline wording**: Soften or sharpen the commitment language
- **Missing context**: Add a brief background sentence
- **Stakeholder concern**: Reframe the blocker in terms of plan, not problem

## State Block

```
<jira-comment-state>
mode: intake | draft | refine
issue_summary: [one-line description of the Jira issue, or "unknown"]
status: in_progress | blocked | complete | needs_decision
audience: client | pm_formal | pm_friendly
tone: formal | professional_friendly | casual
draft_version: [number]
last_action: [what just happened]
next_action: [what should happen next]
</jira-comment-state>
```

## Output Templates

### Intake Opening (when no context is provided)

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

### Draft Presentation

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

### Refined Draft

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

## Comment Templates

See [Comment Templates](references/comment-templates.md) for the full set of ready-to-use templates. Quick reference:

**Progress Update** — Work is in flight, nothing blocking, on track.
**Completion** — Work is done, outcome confirmed.
**Blocker** — Work is paused; explains impact and mitigation.
**Decision Needed** — Stakeholder input required before proceeding.
**Combined** — Two related items (use sparingly).

## AI Discipline Rules

### CRITICAL: Draft First, Ask After

If the user provides enough context to write a draft, write it — do not ask for more information. Intake questions are for when context is genuinely missing. Over-asking wastes the user's time and defeats the purpose of the skill.

### CRITICAL: Translate, Do Not Omit

Technical details should be translated into plain language, not removed. "A bug was fixed" is less useful to a stakeholder than "Fixed an error that was causing incorrect totals to appear on the summary report." The second version is still jargon-free but tells the reader something meaningful.

### CRITICAL: Blockers Must Include a Plan

A comment that says "work is blocked" without a mitigation creates anxiety. Always pair a blocker with the plan: what is being done about it, and when the stakeholder can expect an update.

### CRITICAL: One Draft Per Turn

Produce one clean draft. Do not produce multiple alternatives ("here are three versions...") unless the user explicitly requests options. Multiple versions create decision fatigue. Write the best version given the context, then refine from there.

### IMPORTANT: Preserve the User's Meaning

The user owns the content. The skill owns the translation. If the user says "we found a performance issue in the database queries," do not soften this to "we're making some improvements." The comment must accurately represent the situation — just without the jargon. Accuracy is non-negotiable even when the news is bad.

### IMPORTANT: Tone Is a Dial, Not a Switch

"Formal" and "casual" are ends of a spectrum. Most comments live in the professional-friendly middle. Read the audience cue the user gives, and calibrate accordingly. When in doubt, default to professional-friendly: complete sentences, no contractions, respectful but not stiff.

The target register across all tones is **conversational, friendly, and respectful** (Google Style Guide). Do not aim for corporate formality ("Please be advised that...") or breezy informality ("Hey, quick update!"). Aim for the register of a knowledgeable colleague writing a clear, direct email. The comment should be easy to read at a glance without feeling terse or dismissive.

## Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|--------------|-------------|-------------------|
| **Jargon dump** | PM reads "the CI/CD pipeline broke on merge" and cannot assess impact | Translate: "A technical issue is temporarily blocking the team from publishing updates — being investigated now" |
| **Activity without outcome** | "Worked on the API" tells the reader nothing about state or progress | Lead with the outcome: "The connection between the billing system and the portal is now partially working — payment reads are live, writes are scheduled for tomorrow" |
| **Vague timeline** | "Should be done soon" creates no accountability | Be specific or explicit about uncertainty: "On track for Friday" or "Timeline depends on the vendor response — I'll update by Wednesday" |
| **Over-reassurance** | "Everything is on track and going great!" when a blocker exists | Be honest: "One item is taking longer than expected — the rest of the work remains on track" |
| **Decision buried in prose** | The stakeholder misses that they need to do something | Put decision requests at the top or in bold: "**Action needed:** Please confirm which approach you'd prefer before we proceed." |
| **Too long** | Long comments get skimmed; the important part gets missed | Aim for 3–5 sentences. If more is genuinely needed, use bullet points with a one-line summary at the top. |
| **Hedge language** | "Hopefully we'll be done soon", "It should work", "We think Friday is possible" — these undermine credibility | Be precise or explicit about uncertainty: "On track for Friday" or "Timeline is uncertain — depends on vendor response, expected Wednesday" |
| **Idioms and culturally specific phrases** | "We're in the home stretch", "ball is in your court", "move the needle" — unclear to international readers | Use plain equivalents: "nearly done", "your input is needed", "make measurable progress" |
| **Corporate formality** | "Please be advised that at this juncture the team has encountered an impediment" | Write naturally: "The team has hit a blocker." Conversational clarity beats formal distance every time. |

## Error Recovery

### User Provides Only Technical Details With No Outcome Signal

**Signals:** "Fixed the race condition in the scheduler, refactored the event bus, bumped the ORM version."

**Approach:**
1. Ask: "What's the current status from the stakeholder's perspective — is the feature now working, still in progress, or was this maintenance work?"
2. Use the answer to frame the comment around the observable state, not the implementation steps.

### User Wants to Include Technical Details the Audience Won't Understand

**Signals:** "Make sure you mention we upgraded from Hibernate 5 to 6."

**Approach:**
1. If it affects the stakeholder (e.g., requires their action, causes a brief outage): translate it. "We'll be applying a background infrastructure update — this may cause a brief interruption to [feature] between [time] and [time]."
2. If it does not affect the stakeholder: explain gently that it can be omitted. "This detail is important internally but won't be meaningful to a PM or client. I'll leave it out of the stakeholder comment — but it's worth documenting in your internal notes or a separate technical comment."

### User Is Uncertain How Much to Share About a Delay

**Signals:** "We're behind but I don't want to alarm them."

**Approach:**
1. Remind: honest early communication is always less damaging than a late surprise.
2. Help frame it constructively: state the revised estimate, explain one clear reason, and name the mitigation. Do not over-explain or apologize excessively.
3. Example reframe: "This work has taken longer than estimated due to [one-sentence reason]. Our updated target is [date]. We're [brief mitigation action] to stay on track from here."

## Integration

- **`jira-review`** — Review a Jira issue for implementation readiness before starting work. Use jira-comment-writer afterward to communicate progress back to stakeholders.
- **`pr-feedback-writer`** — A complementary communication skill. PR feedback targets fellow engineers; Jira comments target stakeholders. The underlying craft (audience awareness, clarity, honesty) is the same.
- **`session-context`** — Use to understand the state of the work before drafting a progress comment.
