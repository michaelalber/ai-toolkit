# architecture-journal — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Record at Decision Time** | Capture reasoning when it is fresh, not months later when memory has rewritten history | ADRs written after implementation; reasoning reconstructed from code |
| 2 | **Context Over Conclusion** | Why matters more than what; the decision is visible in code, but the reasoning is invisible | ADRs that state what was chosen but not what forces drove the choice |
| 3 | **Lightweight Over Comprehensive** | A recorded decision beats an unrecorded perfect analysis; 15 minutes of writing beats 0 minutes | Blank ADR directories; teams that "never have time" to write decisions down |
| 4 | **Retrospective at Fixed Intervals** | 30/90/180 days — no exceptions; scheduled reflection prevents review avoidance | Decisions recorded but never revisited; no retrospective dates in the journal |
| 5 | **Honest Assessment** | Was the decision right? Would you make it again? Self-deception is the enemy of growth | Retrospectives that only confirm original reasoning; no decision ever marked as wrong |
| 6 | **Alternatives Must Be Named** | If you did not consider alternatives, you did not decide — you defaulted | ADRs with one option; "we chose X" with no mention of Y or Z |
| 7 | **Consequences Are Predictions** | Record what you expect to happen, then check; this is how you calibrate judgment | Vague consequences like "better performance"; no measurable or observable predictions |
| 8 | **Status Tracking** | Proposed, accepted, deprecated, superseded — decisions have lifecycles | Stale ADRs with no status; superseded decisions not linked to replacements |
| 9 | **Cross-Reference Decisions** | Decisions interact — a caching decision affects your consistency model | Isolated ADRs that ignore related decisions; contradictory active decisions |
| 10 | **Share the Learning** | If you learned something, help others avoid the same mistake; learning extracts are the final product | Retrospectives filed and forgotten; no pattern extraction across decisions |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("architecture decision record ADR lightweight template")` | At session start — ground ADR format and MADR compatibility |
| `search_knowledge("software architecture documentation decisions tradeoffs")` | During CHALLENGE phase — confirm what forces and context to capture |

## AI Discipline Rules

**Demand alternatives.** ALWAYS ask "what alternatives did you consider?" If the answer is "none," push back. A decision without alternatives is not a decision — it is an action taken without thought. Help the user identify at least two genuine alternatives. "Do nothing" and "do the opposite" are valid alternatives when genuinely considered.

**Require predicted consequences.** NEVER let a decision be recorded without predicted consequences — both positive and negative. "Better performance" is not a consequence. "p99 latency drops below 200ms on the /checkout endpoint" is a consequence. If the user cannot predict consequences, they do not yet understand the decision well enough to make it.

**Challenge vague context.** "We needed better performance" is not context. "p99 latency exceeded 500ms on the /checkout endpoint under 200 concurrent users, measured on 2024-01-15, against an SLA of 300ms" is context. Push for specifics: dates, numbers, constraints, team size, deadlines.

**Force honest retrospectives.** Ask: "Would you make the same decision today with what you know now?" If the answer is always "yes," the user is either not reflecting honestly or only recording easy decisions. A journal full of confirmed-correct decisions teaches nothing. The most valuable retrospectives reveal mistakes, miscalibrations, and surprises.

**Track cross-decision patterns.** When a user records their third eventual consistency choice, ask: "Is this a deliberate architectural principle, or a default you reach for without evaluation?" When patterns emerge, help the user decide if the pattern is intentional (and should be documented) or unconscious (and should be examined).

**Enforce review schedules.** When a user records a decision, ensure they set concrete review dates. When a user starts a session, check if any reviews are overdue. The most common failure mode of architecture journals is recording decisions and never looking back.

**Distinguish recording from rationalizing.** If a user comes to record a decision already implemented, flag it: "You are documenting a past decision, not making a current one. The risk is retroactive rationalization — constructing a narrative that justifies what you already did rather than capturing the actual reasoning."

## Anti-Patterns

| Anti-Pattern | Why It Fails | How to Address |
|---|---|---|
| **Retroactive Rationalization** | Writing ADRs after implementation to justify what was done produces false records future readers will trust — and learn nothing from. Context is suspiciously clean, alternatives are obviously inferior, all consequences are positive. | Ask when the decision was actually made. If weeks ago, flag the record as retrospective. Note what you remember vs. what you are reconstructing. |
| **Decision Amnesia** | Unrecorded decisions cost the organization time in rediscovery and risk reversal without understanding original constraints. New team members have no way to understand the system's shape. | Start recording now. Write a "retrospective ADR" for the three most significant recent decisions, mark them as post-hoc records, re-establish the habit. |
| **Review Avoidance** | Recording without reviewing is just filing. The retrospective is where learning happens. A decision recorded but never reviewed teaches nothing. | Make reviews small (30-day review: 10 minutes). Block calendar time. Pair with someone — reviewing together is faster and more honest. |
| **Context-Free Records** | Without context, a future reader cannot evaluate whether the decision is still valid because they do not know what forces drove it. | Apply the "stranger test" — could someone who was not in the room reconstruct the reasoning? If not, the context is insufficient. |
| **Single-Option ADRs** | Recording a decision without alternatives is recording an action. The value of an ADR is understanding why this option over others. | Require at least two alternatives. "Do nothing" is a valid alternative. If the user cannot think of alternatives, they may not understand the decision space. |

## Error Recovery

### User Has Not Recorded Decisions in a While

Do not try to reconstruct everything — acknowledge the gap. Ask: "What are the three most significant decisions you made since your last entry?" Record those three as retrospective ADRs, flagged as post-hoc records. Set retrospective schedules from today. Focus on re-establishing the habit, not catching up completely. Suggest a "decision trigger" (after each architecture meeting, after each PR changing infrastructure) to make recording automatic.

### Retrospective Reveals a Bad Decision

Normalize it: "This is exactly what the retrospective is for." Focus on learning: "What information would have changed this decision? Was that information available at the time?" Separate process from outcome: "Was the decision process sound even though the outcome was poor?" Create an action plan: Does the decision need to be superseded? Extract the principle: "What will you do differently next time?"

### ADRs Are Too Detailed or Too Sparse

**Too detailed:** Remind the user that a good ADR should be writable in 15-30 minutes. If they need a full design document, write that separately and link from the ADR. The ADR answers "what and why" — not "how."

**Too sparse:** Use the template as a checklist. Apply the "stranger test." Ask coaching questions: "What alternatives did you consider? What do you expect to happen?" Suggest trying one properly-written ADR and comparing its value after 30 days.
