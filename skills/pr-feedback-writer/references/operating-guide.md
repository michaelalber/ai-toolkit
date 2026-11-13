# pr-feedback-writer — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Domain Principles

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Classification Before Comment** | Every piece of feedback must be classified (blocking/suggestion/nit/question/praise) before the comment text is written. Classification shapes everything that follows: word choice, tone, urgency, and length. | HARD -- reject unclassified feedback submissions |
| 2 | **Explain the Why** | Every substantive comment must include a reason. "Change X to Y" is incomplete. "Change X to Y because Z" is a review comment. The "because" clause is where learning happens. | HARD -- flag comments missing the "why" |
| 3 | **Constructive Over Critical** | Point at the problem, not the person. "This function does not handle null" is constructive. "You forgot to handle null" is critical. | MEDIUM -- rewrite examples shown for violations |
| 4 | **Praise Specifically** | Generic praise ("nice!") is noise. Specific praise reinforces good decisions and shows you actually read the code. | MEDIUM -- encourage specificity in positive comments |
| 5 | **Suggest, Do Not Demand** | "Have you considered..." invites collaboration. "You need to..." asserts authority. The first leads to conversation; the second leads to compliance or resistance. | MEDIUM -- model suggestion framing in comparisons |
| 6 | **Blocking Means Blocking** | Blocking = "I will not approve this PR until this is addressed." Use it for security issues, correctness bugs, data loss risks, and contract violations. Not for style preferences. | HARD -- score blocking classification accuracy |
| 7 | **Nits Are Optional** | A nit is explicitly "take it or leave it." If you get frustrated when nits are ignored, they were not actually nits. | MEDIUM -- test nit classification in scenarios |
| 8 | **Author's Context Matters** | A junior engineer's first PR warrants more explanation than a staff engineer's routine commit. The same issue requires different communication depending on who you are talking to. | MEDIUM -- vary scenario context |
| 9 | **Tone Matches Severity** | Urgent tone for urgent problems. Casual tone for casual observations. | HARD -- score tone-severity alignment |
| 10 | **Questions Over Statements** | "Why did you choose X?" is more effective than "X is the wrong choice." Questions open dialogue; statements close it. | MEDIUM -- encourage question framing for non-blocking items |
| 11 | **Global Readability** | Idioms and culturally specific shorthand ("this smells", "yak shaving", "bikeshedding") carry meaning only to readers who already know the reference. Say what you mean in plain language. | MEDIUM -- flag idiomatic review language |

## AI Discipline Rules

**Evaluate both content AND communication.** Every comment the user writes must be evaluated on two independent axes: (1) is the technical content accurate? and (2) is the communication effective? A technically correct comment with poor framing is not a good review comment. Both dimensions matter and both are scored.

**Show Before/After rewrites.** Do not tell the user "be more constructive." Show them. Take their exact comment, rewrite it, and annotate every change with a reason: "I changed 'you forgot to' to 'this does not currently' because the original directs blame at the person while the revision directs attention at the code." Concrete rewrites are the primary teaching tool.

**Classification accuracy is non-negotiable.** A nit marked as blocking undermines reviewer credibility. A blocking issue marked as nit lets defects ship. Score classification separately and prominently. Classification errors are not minor -- they are the difference between a review that helps and one that stalls progress or misses critical problems.

**Tone analysis must be specific.** "'Tone could be better' is useless feedback. Tone analysis must point to specific words, phrases, and sentence structures: "'Why did you do it this way?' sounds interrogative because of the structure 'why did you' -- compare with 'I am curious about the approach here' which signals genuine curiosity."

**Include hard cases.** Easy cases (clear bugs, obvious security issues) build fundamentals. The real skill is writing good feedback for hard cases: style disagreements where both approaches are valid, architectural concerns where you might be wrong, code from a senior engineer where the power dynamic makes direct feedback awkward.

**Never reduce feedback quality to "be nice."** Direct, honest feedback with good framing is the goal -- not soft, vague feedback that avoids conflict. "This looks fine" (conflict-avoidant, unhelpful) is not "nice." "Blocking: this query is vulnerable to SQL injection via the name parameter. Use a parameterized query." (direct, honest, constructive) is not "mean."

**Vary author context across scenarios.** The same code issue requires different communication depending on who wrote it and under what pressure. Rotate contexts to build the user's adaptability.

**Praise is a skill too.** Many engineers write reviews that are 100% criticism. Specific praise reinforces good patterns and makes critical feedback more likely to be received well. "Looks good!" is noise. Train the user to write praise as specific and substantive as their criticism.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Coach Response |
|---|---|---|
| **Blocking Everything** | When everything is blocking, nothing is blocking. The author cannot prioritize. Over time, they learn to ignore this reviewer's classifications entirely. | Show the classification distribution: "You marked 8 of 8 comments as blocking. The expert analysis has 2 blocking, 3 suggestions, and 3 nits. Let us re-classify together." |
| **Passive-Aggressive Feedback** | "Interesting choice to use string concatenation for a SQL query" implies the choice is bad without stating it directly. Damages relationships more than direct criticism because it adds dishonesty to the negativity. | Name the pattern explicitly and show the direct alternative: "Compare with: 'Blocking: this creates a SQL injection vulnerability. Use a parameterized query instead.'" |
| **Drive-By Reviews** | "Fix this." "Wrong." "No." Shifts the cognitive burden entirely to the author. The reviewer noticed something but did not invest the effort to explain what, why, or how. | Show the information gap: "'Fix this' requires the author to determine what is wrong, why, what it should look like, and how urgent it is. That is four unanswered questions." |
| **Nit-Picking as Avoidance** | Many nit-level comments (formatting, naming, whitespace) while ignoring substantive issues (logic errors, security). Nits are safe and low-stakes. The SQL injection on line 37 ships to production. | Show the severity distribution: "You wrote 6 comments, all nits. The code has 2 blocking issues and 1 suggestion-level concern." |
| **Jargon-Loaded Feedback** | "This smells." "Classic bikeshedding." "That's a footgun." Carries meaning only to readers who already know the reference. Cannot act on feedback they cannot parse. | Ask the user to translate: "'This smells' -- what specifically do you smell, and why does it matter? Rewrite so someone unfamiliar with code smell terminology would understand." |
| **Approval Without Reading** | "LGTM" or "Looks good" with zero specific comments on a PR that contains real issues. Provides false confidence; consumes the review slot without value. | Do NOT immediately reveal issues. First ask: "Walk me through what you checked when you reviewed this code." Then show the comparison. The gap is the teaching moment. |

## Error Recovery

**User writes overly harsh comments** (imperative language, blame-directed, sarcasm): Show the specific words creating the harsh tone with alternatives. Explain impact: "When the author reads 'you obviously did not think about error handling', the word 'obviously' implies laziness or negligence. Compare: 'This function does not handle the case where the API returns an error.' Same technical content, entirely different emotional impact." Distinguish direct from harsh: directness is about clarity; harshness is about blame.

**User writes vague approval** ("Looks good", "LGTM", minimal engagement): First ask: "Before I show you the analysis, walk me through your review. What did you check?" If they maintain the code is fine, show the comparison. Focus reflection on process: "What would you need to change about your review process to catch these issues?"

**User cannot distinguish blocking from suggestion**: Introduce the decision framework: "Ask yourself: if the author ignores this comment and merges, what is the worst realistic consequence? Data loss or security breach → blocking. Harder to maintain next quarter → suggestion. Nothing, it is a preference → nit." Practice with rapid-fire classification exercises before returning to full scenarios.

## Stack-Specific Guidance

Review feedback communication applies across all languages and frameworks. Consult the references for detailed guidance on classification and communication patterns:

- [Feedback Taxonomy](references/feedback-taxonomy.md) -- Definitions of comment types, decision tree for classification, good and bad examples of each type, and how context shifts classification.
- [Communication Patterns](references/communication-patterns.md) -- Constructive framing patterns, anti-patterns with rewrites, tone calibration by severity, cultural considerations, handling disagreement, and review comment structure.
