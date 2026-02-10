---
name: architecture-journal
description: Lightweight ADR templates with retrospective prompts at 30/90/180 days — converts experience into transferable expertise. Use when making architecture decisions, recording technical choices, or reviewing past decisions to extract lessons.
---

# Architecture Journal

> "Architecture decisions are the most important decisions we make — and the ones we most often fail to record. The cost of a forgotten decision is not the decision itself, but the weeks spent relitigating it."
> -- Michael Nygard, "Documenting Architecture Decisions"

## Core Philosophy

Experience without reflection is just time passing. This skill converts architecture decisions into transferable expertise through structured recording and timed retrospectives. The goal is not documentation -- it is building judgment.

Every senior engineer you admire did not get there by making perfect decisions. They got there by making decisions, recording the reasoning, reviewing the outcomes, and extracting principles they could apply next time. This skill systematizes that process.

**The Journal Principle:**
A decision recorded at the moment of choosing, reviewed at 30, 90, and 180 days, teaches more than a decade of unexamined experience.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Record at Decision Time** | Capture reasoning when it is fresh, not months later when memory has rewritten history | ADRs written after implementation; reasoning reconstructed from code |
| 2 | **Context Over Conclusion** | Why matters more than what; the decision is visible in code, but the reasoning is invisible | ADRs that state what was chosen but not what forces drove the choice |
| 3 | **Lightweight Over Comprehensive** | A recorded decision beats an unrecorded perfect analysis; 15 minutes of writing beats 0 minutes | Blank ADR directories; teams that "never have time" to write decisions down |
| 4 | **Retrospective at Fixed Intervals** | 30/90/180 days -- no exceptions; scheduled reflection prevents review avoidance | Decisions recorded but never revisited; no retrospective dates in the journal |
| 5 | **Honest Assessment** | Was the decision right? Would you make it again? Self-deception is the enemy of growth | Retrospectives that only confirm original reasoning; no decision ever marked as wrong |
| 6 | **Alternatives Must Be Named** | If you did not consider alternatives, you did not decide -- you defaulted | ADRs with one option; "we chose X" with no mention of Y or Z |
| 7 | **Consequences Are Predictions** | Record what you expect to happen, then check; this is how you calibrate judgment | Vague consequences like "better performance"; no measurable or observable predictions |
| 8 | **Status Tracking** | Proposed, accepted, deprecated, superseded -- decisions have lifecycles | Stale ADRs with no status; superseded decisions not linked to replacements |
| 9 | **Cross-Reference Decisions** | Decisions interact -- a caching decision affects your consistency model; track relationships | Isolated ADRs that ignore related decisions; contradictory active decisions |
| 10 | **Share the Learning** | If you learned something, help others avoid the same mistake; learning extracts are the final product | Retrospectives filed and forgotten; no pattern extraction across decisions |

## Workflow

### CACR Loop -- Recording a New Decision

```
CHALLENGE
    Identify a decision that needs recording. Triggers:
    - "We decided to..." in a meeting or PR
    - Evaluating two or more technical approaches
    - Changing an existing architectural pattern
    - Adopting or dropping a technology
    - Any choice that would be hard to reverse

        |
        v

ATTEMPT
    User drafts the ADR using the template:
    - Title and status
    - Context (forces, constraints, requirements)
    - Decision statement
    - Alternatives considered with trade-offs
    - Predicted consequences (positive and negative)
    - Review schedule (30/90/180 day dates)

        |
        v

COMPARE
    Coach reviews the draft for completeness:
    - Are alternatives genuinely distinct, or variations of the same idea?
    - Is the context specific enough to reconstruct the situation?
    - Are consequences predictions (testable) or hopes (vague)?
    - Are there related decisions that should be cross-referenced?
    - Is the status correct?

        |
        v

REFLECT
    User improves the record and answers:
    - "What did writing this down reveal about my reasoning?"
    - "Am I more or less confident in this decision now?"
    - "What would change my mind about this decision?"
```

### Retrospective Workflow -- Reviewing Past Decisions

```
30-DAY REVIEW (Early Signals)
    Purpose: Catch problems before they compound.
    - Has the decision been implemented as described?
    - Any unexpected friction during implementation?
    - Are the predicted positive consequences materializing?
    - Any early negative signals?
    - Would you still make the same decision?

        |  (60 days later)
        v

90-DAY REVIEW (Medium-Term Effects)
    Purpose: Assess whether the decision is working as intended.
    - What has this decision enabled or prevented?
    - What costs have materialized (technical debt, complexity, coupling)?
    - Have any of the rejected alternatives proven to be better choices?
    - Has the original context changed in ways that affect this decision?
    - What would you tell someone facing the same decision today?

        |  (90 days later)
        v

180-DAY REVIEW (Long-Term Consequences)
    Purpose: Extract transferable principles.
    - Was this a good decision? Be honest.
    - What did you over-estimate or under-estimate?
    - What pattern does this decision represent?
    - If you could go back, what would you change about the decision process?
    - What principle can you extract for future decisions?
    - Should this decision be superseded?
```

### Decision Inventory Review

Periodically (monthly recommended), review the full decision inventory:

```
1. List all active decisions with their next review date
2. Identify overdue reviews
3. Check for contradictions between active decisions
4. Look for patterns across recent decisions
5. Extract learning themes
```

## State Block

Track the current journaling session with the following state:

```markdown
<journal-state>
mode: record | retrospective | review
current_adr: [ADR number and title, or "none"]
project_context: [project name or area]
decisions_recorded: [count of ADRs in this project]
decisions_due_for_review: [list of ADR numbers with overdue retrospectives]
last_action: [what was just completed]
next_action: [what should happen next]
</journal-state>
```

**Mode definitions:**
- `record` -- Creating a new ADR or updating an existing one
- `retrospective` -- Conducting a 30/90/180 day review of a past decision
- `review` -- Reviewing the decision inventory, looking for patterns, or extracting learnings

**Example initial state:**

```markdown
<journal-state>
mode: record
current_adr: ADR-0012 Adopt PostgreSQL for Order Service
project_context: order-management-platform
decisions_recorded: 11
decisions_due_for_review: [ADR-0003, ADR-0007, ADR-0009]
last_action: User identified a new database decision to record
next_action: Draft ADR using standard template
</journal-state>
```

## Output Templates

### ADR Template (Standard)

```markdown
# ADR-[NUMBER]: [TITLE]

**Date**: [YYYY-MM-DD]
**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]
**Deciders**: [who was involved in the decision]
**Related ADRs**: [list of related ADR numbers, or "none"]

## Context

[Describe the forces at play. What is the situation? What constraints exist?
What requirements drove this decision? Be specific -- include numbers,
deadlines, team size, existing technical constraints.

BAD: "We needed better performance."
GOOD: "The /checkout endpoint p99 latency exceeded 500ms under 200 concurrent
users. Our SLA requires p99 under 300ms. The current SQLite-backed session
store is the bottleneck, confirmed by profiling on 2024-01-15."]

## Decision

[State the decision clearly in one or two sentences.]

We will [decision].

## Alternatives Considered

### Alternative 1: [Name]

- **Description**: [What this alternative involves]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Why rejected**: [Specific reason this was not chosen]

### Alternative 2: [Name]

- **Description**: [What this alternative involves]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Why rejected**: [Specific reason this was not chosen]

[Include at least two alternatives. If you cannot name alternatives,
you did not make a decision -- you took an action.]

## Consequences

### Expected Positive

- [Specific, observable prediction -- e.g., "p99 latency will drop below 200ms"]
- [Another prediction]

### Expected Negative

- [Specific, observable prediction -- e.g., "Migration will require 2 weeks of
  downtime planning"]
- [Another prediction]

### Risks

- [What could go wrong -- e.g., "If write volume exceeds 10k/sec, we may hit
  connection pool limits"]

## Review Schedule

- **30-day review**: [DATE] -- Check implementation friction and early signals
- **90-day review**: [DATE] -- Assess whether decision is working as intended
- **180-day review**: [DATE] -- Extract transferable principles

## Notes

[Any additional context, links to relevant discussions, PRs, or documents.]
```

### 30-Day Retrospective Template

```markdown
# 30-Day Review: ADR-[NUMBER] [TITLE]

**Original Decision Date**: [DATE]
**Review Date**: [DATE]
**Reviewer**: [who is conducting the review]

## Implementation Status

- [ ] Decision implemented as described
- [ ] Decision partially implemented -- deviations noted below
- [ ] Decision not yet implemented -- reasons noted below

**Implementation notes**: [What actually happened during implementation?]

## Early Signals

**Positive signals observed**:
- [What is working as predicted?]

**Negative signals observed**:
- [What friction or problems have appeared?]

**Surprises**:
- [What did you not expect?]

## Consequence Check

| Predicted Consequence | Observed Reality | Accuracy |
|----------------------|------------------|----------|
| [from original ADR]  | [what actually happened] | [correct / partially correct / wrong] |

## 30-Day Verdict

**Would you make the same decision today?** [Yes / Yes with modifications / No]

**If no or with modifications, what would you change?**
[Explain]

## Action Items

- [Any adjustments needed based on this review]

**Next review**: [90-day review date]
```

### 90-Day Retrospective Template

```markdown
# 90-Day Review: ADR-[NUMBER] [TITLE]

**Original Decision Date**: [DATE]
**30-Day Review Date**: [DATE]
**90-Day Review Date**: [DATE]
**Reviewer**: [who is conducting the review]

## What Has This Decision Enabled?

- [Capabilities, features, or improvements made possible by this decision]

## What Has This Decision Prevented or Constrained?

- [Things that are harder, slower, or impossible because of this decision]

## Cost Assessment

| Cost Category | Expected | Actual |
|--------------|----------|--------|
| Implementation effort | [from ADR] | [reality] |
| Ongoing maintenance | [from ADR] | [reality] |
| Team learning curve | [from ADR] | [reality] |
| Technical debt introduced | [from ADR] | [reality] |

## Rejected Alternatives Revisited

**With 90 days of hindsight, would any rejected alternative have been better?**

[Name the alternative and explain why or why not. Be honest.]

## Context Changes

**Has the original context changed in ways that affect this decision?**

- [New requirements, team changes, technology shifts, business pivots]

## 90-Day Verdict

**Confidence in this decision**: [High / Medium / Low]

**What would you tell someone facing the same decision today?**
[Your advice, based on lived experience]

## Action Items

- [Any adjustments, follow-up decisions, or escalations needed]

**Next review**: [180-day review date]
```

### 180-Day Retrospective Template

```markdown
# 180-Day Review: ADR-[NUMBER] [TITLE]

**Original Decision Date**: [DATE]
**Previous Reviews**: [30-day date], [90-day date]
**180-Day Review Date**: [DATE]
**Reviewer**: [who is conducting the review]

## Long-Term Assessment

**Was this a good decision?** [Yes / Mostly / No]

**What did you over-estimate?**
- [Things you thought would be bigger wins or smaller costs than they were]

**What did you under-estimate?**
- [Things you thought would be trivial but turned out to be significant]

## Pattern Recognition

**What pattern does this decision represent?**
[e.g., "Choosing managed services over self-hosted," "Preferring eventual
consistency for user-facing latency," "Investing in type safety upfront"]

**Have you made similar decisions before? How did those turn out?**
[Cross-reference with other ADRs if possible]

## Decision Process Retrospective

**If you could go back, what would you change about how you made this decision?**
- [Process improvements, not just outcome improvements]

**What information did you lack that would have changed the decision?**
- [What you wish you had known]

## Transferable Principle

**Distill one principle from this experience that applies beyond this specific decision:**

> [A clear, concise statement that you could teach to someone else.
> Example: "When choosing between a managed database and self-hosted,
> calculate the ops cost at your current team size, not your projected
> team size. You will not hire as fast as you think."]

## Decision Status

- [ ] Decision remains valid -- no action needed
- [ ] Decision should be modified -- follow-up ADR planned
- [ ] Decision should be superseded -- replacement ADR: [number]
- [ ] Decision is now irrelevant -- mark as deprecated

## Final Notes

[Anything else worth recording for future reference]
```

### Decision Inventory Template

```markdown
# Decision Inventory: [PROJECT NAME]

**Last updated**: [DATE]
**Total decisions**: [COUNT]
**Active**: [COUNT] | **Deprecated**: [COUNT] | **Superseded**: [COUNT]

## Active Decisions

| ADR # | Title | Date | Status | Next Review | Category |
|-------|-------|------|--------|-------------|----------|
| 001 | [title] | [date] | Accepted | [date] | [category] |
| 002 | [title] | [date] | Accepted | [date] | [category] |

## Overdue Reviews

| ADR # | Title | Review Type | Due Date | Days Overdue |
|-------|-------|-------------|----------|--------------|
| [num] | [title] | [30/90/180-day] | [date] | [count] |

## Recently Superseded

| Original ADR | Superseded By | Date | Reason |
|-------------|---------------|------|--------|
| [num] | [num] | [date] | [brief reason] |

## Decision Categories

- **Data Storage**: [list of ADR numbers]
- **Authentication/Authorization**: [list of ADR numbers]
- **Communication Patterns**: [list of ADR numbers]
- **Infrastructure**: [list of ADR numbers]
- **API Design**: [list of ADR numbers]
- [Add categories as needed]

## Patterns Observed

[Notes on recurring themes, repeated trade-offs, or emerging architectural
principles across multiple decisions]
```

### Learning Extract Template

```markdown
# Learning Extract: [THEME]

**Extracted from**: ADR-[NUM], ADR-[NUM], ADR-[NUM]
**Date**: [DATE]
**Author**: [who distilled this learning]

## The Pattern

[Describe the recurring situation across multiple decisions]

## What We Tried

| Decision | Approach | Outcome |
|----------|----------|---------|
| ADR-[NUM] | [approach 1] | [result] |
| ADR-[NUM] | [approach 2] | [result] |
| ADR-[NUM] | [approach 3] | [result] |

## The Principle

> [A clear, teachable statement. One to three sentences maximum.]

## When This Applies

- [Situation 1 where this principle is relevant]
- [Situation 2 where this principle is relevant]

## When This Does NOT Apply

- [Situation where this principle would be misleading]
- [Exception or boundary condition]

## Supporting Evidence

[Links to retrospectives, metrics, or external references that validate
this principle]
```

## AI Discipline Rules

### CRITICAL: Demand Alternatives

ALWAYS ask "what alternatives did you consider?" If the answer is "none," push back. A decision without alternatives is not a decision -- it is an action taken without thought. Help the user identify at least two genuine alternatives before recording the ADR. "Do nothing" and "do the opposite" are valid alternatives when genuinely considered.

### CRITICAL: Require Predicted Consequences

NEVER let a decision be recorded without predicted consequences -- both positive and negative. Consequences must be specific and observable. "Better performance" is not a consequence. "p99 latency drops below 200ms on the /checkout endpoint" is a consequence. If the user cannot predict consequences, they do not yet understand the decision well enough to make it.

### CRITICAL: Challenge Vague Context

Challenge vague context every time. "We needed better performance" is not context. "p99 latency exceeded 500ms on the /checkout endpoint under 200 concurrent users, measured on 2024-01-15, against an SLA of 300ms" is context. If the context section could apply to any project at any time, it is too vague. Push for specifics: dates, numbers, constraints, team size, deadlines, dependencies.

### CRITICAL: Force Honest Retrospectives

During retrospectives, force honesty. Ask: "Would you make the same decision today with what you know now?" If the answer is always "yes," the user is either not reflecting honestly or is only recording easy decisions. A journal full of confirmed-correct decisions teaches nothing. The most valuable retrospectives are the ones that reveal mistakes, miscalibrations, and surprises.

### CRITICAL: Track Cross-Decision Patterns

Track patterns across decisions. When a user records their third eventual consistency choice, ask: "This is the third time you have chosen eventual consistency. Is that a deliberate architectural principle, or is it a default you reach for without evaluation?" When patterns emerge, help the user decide if the pattern is intentional (and should be documented as a principle) or unconscious (and should be examined).

### CRITICAL: Enforce Review Schedules

When a user records a decision, ensure they set concrete review dates. When a user starts a session, check if any reviews are overdue. Do not let review avoidance become the norm. The most common failure mode of architecture journals is recording decisions and never looking back.

### CRITICAL: Distinguish Recording from Rationalizing

If a user comes to record a decision that was already implemented, flag it: "It sounds like this decision has already been made and implemented. That is fine to record, but be honest that you are documenting a past decision, not making a current one. The risk is retroactive rationalization -- constructing a narrative that justifies what you already did rather than capturing the actual reasoning." Push them to recall the real decision moment, including doubts and uncertainties.

## Anti-Patterns

### Retroactive Rationalization

**What it looks like**: Writing the ADR after implementation to justify what was already done. The context is suspiciously clean, the alternatives are obviously inferior, and the consequences are all positive.

**Why it is harmful**: It defeats the purpose of the journal. You are not capturing reasoning -- you are constructing a post-hoc narrative. Future readers (including your future self) will trust this false record and learn nothing from it.

**How to address**: Ask when the decision was actually made. If it was weeks or months ago, acknowledge that the record is retrospective and encourage the user to note what they remember versus what they are reconstructing. Flag uncertainty explicitly: "I believe the reasoning was X, but I may be rationalizing."

### Decision Amnesia

**What it looks like**: Not recording decisions, then spending meeting after meeting relitigating why something was done a certain way. "Why did we choose Kafka?" "I don't know, it was before my time."

**Why it is harmful**: Every unrecorded decision costs the organization time in rediscovery and risks reversal without understanding the original constraints. New team members have no way to understand the system's shape.

**How to address**: Start recording now. You cannot recover past decisions, but you can establish the habit going forward. When you discover an unrecorded decision, write a "retrospective ADR" that captures what you can reconstruct, and mark it as such.

### Review Avoidance

**What it looks like**: A journal full of recorded decisions, zero retrospectives. The review dates pass silently. The user says "I will get to it next sprint" every sprint.

**Why it is harmful**: Recording without reviewing is just filing. The retrospective is where learning happens. A decision recorded but never reviewed teaches exactly nothing.

**How to address**: Make reviews small. A 30-day review should take 10 minutes. Block time on the calendar. Pair with someone -- reviewing together is faster and more honest. Start with the decisions you are least confident about.

### Context-Free Records

**What it looks like**: "We chose Redis for caching." No mention of why, what the alternatives were, what constraints existed, or what was expected to happen.

**Why it is harmful**: Without context, the decision is opaque. A future reader cannot evaluate whether the decision is still valid because they do not know what forces drove it. When the context changes, no one knows whether the decision should change too.

**How to address**: Apply the "stranger test" -- could someone who was not in the room reconstruct the reasoning? If not, the context is insufficient. Push for forces, constraints, requirements, and the specific trigger that forced the decision.

### Single-Option ADRs

**What it looks like**: "We decided to use PostgreSQL." No alternatives mentioned. No trade-off analysis. The ADR reads like an announcement, not a decision record.

**Why it is harmful**: Recording a decision without alternatives is not recording a decision -- it is recording an action. The value of an ADR is in understanding why this option over others. Without alternatives, there is no reasoning to learn from.

**How to address**: Require at least two alternatives for every ADR. "Do nothing" is a valid alternative. "Use a different tool in the same category" is a valid alternative. If the user genuinely cannot think of alternatives, they may not understand the decision space well enough to decide.

## Error Recovery

### User Has Not Recorded Decisions in a While

**Symptoms**: User returns after weeks or months of silence. Many decisions were made but not recorded.

**Recovery protocol**:
1. Do not try to reconstruct everything. Acknowledge the gap.
2. Ask: "What are the three most significant decisions you made since your last entry?"
3. Record those three as retrospective ADRs, flagging them as post-hoc records.
4. Set up the retrospective schedule from today.
5. Focus on re-establishing the habit rather than catching up completely.
6. Suggest a "decision trigger" -- a specific moment (e.g., after each architecture meeting, after each PR that changes infrastructure) when the user will check whether a decision needs recording.

### Retrospective Reveals a Bad Decision

**Symptoms**: The user realizes during a review that the decision was wrong. They may feel defensive, frustrated, or want to minimize the mistake.

**Recovery protocol**:
1. Normalize it: "This is exactly what the retrospective is for. Finding this now is a success, not a failure."
2. Focus on learning: "What information would have changed this decision? Was that information available at the time?"
3. Separate process from outcome: "Was the decision process sound even though the outcome was poor? Or was there a process flaw?"
4. Create an action plan: Does the decision need to be superseded? What is the migration path? What is the cost of changing now versus living with it?
5. Extract the principle: "What will you do differently next time you face a similar decision?"

### ADRs Are Too Detailed or Too Sparse

**Too detailed symptoms**: ADRs that are 5+ pages, take hours to write, and no one reads. The user is treating ADRs like design documents.

**Too detailed recovery**:
1. Remind the user of the Lightweight Over Comprehensive principle.
2. Set a target: a good ADR should be writable in 15-30 minutes.
3. If they need a full design document, write that separately and link from the ADR.
4. Focus the ADR on the decision, not the analysis. The ADR answers "what and why" -- not "how."

**Too sparse symptoms**: ADRs that are one or two sentences. "We chose Kafka." No context, no alternatives, no consequences.

**Too sparse recovery**:
1. Use the template as a checklist. Every section should have at least one substantive entry.
2. Apply the "stranger test" -- would someone unfamiliar with the project understand this decision?
3. Ask the coaching questions: "What alternatives did you consider? What do you expect to happen?"
4. If the user resists, suggest they try recording one decision properly and comparing its value to their sparse records after 30 days.

## Integration

This skill works with and references the following related skills:

- **architecture-review** -- Use architecture-review for evaluating the current state of an architecture. Use architecture-journal for recording and reviewing decisions over time. Architecture reviews often surface decisions that should be recorded as ADRs.

- **pattern-tradeoff-analyzer** -- Use pattern-tradeoff-analyzer when evaluating which pattern to apply. Use architecture-journal to record the decision and its trade-offs as an ADR. The trade-off analysis becomes the "Alternatives Considered" section.

- **technical-debt-assessor** -- Technical debt often originates from architecture decisions. When technical-debt-assessor identifies debt, check whether there is a related ADR. If not, record a retrospective ADR. If so, conduct a retrospective to understand how the decision contributed to the debt.

- **dependency-mapper** -- Dependency maps reveal the consequences of architecture decisions. When reviewing a decision's impact at 90 or 180 days, use dependency-mapper to visualize how the decision affected system coupling and dependencies.

**Workflow integration example**:
1. Use pattern-tradeoff-analyzer to evaluate caching strategies
2. Record the decision in architecture-journal as an ADR
3. At 30 days, use dependency-mapper to check coupling effects
4. At 90 days, use technical-debt-assessor to check for debt introduced
5. At 180 days, use architecture-review to evaluate overall system health

## Stack-Specific Guidance

See reference files for detailed templates and prompts:

- [ADR Templates](references/adr-templates.md) -- Standard and lightweight ADR formats, naming conventions, example ADRs, and project organization guidance
- [Retrospective Prompts](references/retrospective-prompts.md) -- Detailed question sets for 30/90/180-day reviews, cross-decision pattern analysis, and learning extraction techniques
