# Retrospective Prompts Reference

## 30-Day Review Questions (Early Signals)

The 30-day review catches implementation friction and early surprises. It should take 10-15 minutes. Do not overthink it -- the goal is to check whether reality matches predictions while memory is still fresh.

### Implementation Check

- Was the decision implemented as described in the ADR, or did the implementation diverge? If it diverged, why?
- What was harder than expected during implementation?
- What was easier than expected?
- Did the implementation reveal any assumptions in the ADR that were wrong?

### Early Signal Detection

- Are the predicted positive consequences starting to materialize? What evidence do you have?
- Are any predicted negative consequences appearing earlier or stronger than expected?
- Has anything happened that the ADR did not predict at all -- positive or negative?
- Have any team members raised concerns about this decision?

### Confidence Calibration

- On a scale of 1-10, how confident are you in this decision now versus when you made it?
- What new information have you learned since the decision that affects your confidence?
- Would you make the same decision today? If not, what changed?

### Quick Check Questions (Use When Time is Short)

- Did implementation match the plan? (yes / mostly / no)
- Any surprises? (describe in one sentence)
- Still the right call? (yes / yes with concerns / probably not)

## 90-Day Review Questions (Medium-Term Effects)

The 90-day review assesses whether the decision is delivering its intended value. This is the most important review -- long enough for real consequences to emerge, soon enough to change course if needed.

### Value Assessment

- What has this decision enabled that would not have been possible otherwise?
- What has this decision prevented or made harder?
- If you quantified the benefit of this decision, what would the number be? (e.g., requests/second improved, hours/week saved, incidents prevented)
- Is the team actively benefiting from this decision, or has it become invisible infrastructure?

### Cost Assessment

- What has the actual implementation and maintenance cost been versus the prediction?
- Has the decision introduced technical debt? Where and how much?
- What is the ongoing operational burden of this decision?
- Has the decision created coupling or dependencies that constrain future choices?

### Alternatives Revisited

- With 90 days of experience, would any of the rejected alternatives have been a better choice?
- Has new technology or information emerged that creates alternatives that did not exist at decision time?
- If you had to make this decision again today with the same constraints, would you choose the same option?

### Context Drift

- Have the requirements that drove this decision changed?
- Has the team changed in ways that affect this decision (new members, lost expertise, different priorities)?
- Has the business context shifted (new competitors, changed roadmap, budget changes)?
- Are the constraints from the original ADR still valid?

### Advice Generation

- What would you tell a colleague at another company facing the same decision?
- What is the one thing you wish you had known before making this decision?
- If someone asked "should we do what you did?", what caveats would you add?

## 180-Day Review Questions (Long-Term Consequences)

The 180-day review extracts transferable principles. Six months is long enough to see second-order effects and to judge the decision with genuine perspective.

### Honest Verdict

- Was this a good decision? Answer honestly, not defensively.
- Did the decision solve the problem it was intended to solve?
- What unexpected problems did it create?
- If this decision were reversed tomorrow, what would break and what would improve?

### Calibration Analysis

- What did you over-estimate about this decision? (expected benefits that were smaller, expected costs that were lower)
- What did you under-estimate? (hidden costs, unexpected complexity, team impact)
- What did you completely fail to predict?
- How does your prediction accuracy on this decision compare to your other decisions?

### Pattern Recognition

- What category does this decision fall into? (e.g., "build vs buy," "consistency vs availability," "flexibility vs simplicity")
- Have you made similar decisions before? How did those turn out?
- Is there a pattern in the kinds of decisions you get right? In the kinds you get wrong?
- Does this decision reflect a broader architectural philosophy you hold? Is that philosophy serving you well?

### Process Retrospective

- Was the decision-making process itself sound? Did you have the right people in the room, the right information, and enough time?
- What would you change about how you made this decision, separate from what you decided?
- Did the ADR recording process help you think more clearly about the decision?
- Did the 30-day and 90-day reviews catch anything useful?

### Principle Extraction

- Distill one principle from this experience: a statement that applies beyond this specific decision and this specific project.
- Is this principle new, or does it reinforce something you already believed?
- Under what conditions would this principle NOT apply?

### Status Decision

- Should this decision remain active as-is?
- Should it be modified (new ADR with adjustments)?
- Should it be superseded (fundamentally replaced)?
- Should it be deprecated (no longer relevant)?

## Cross-Decision Pattern Analysis Prompts

Use these prompts when reviewing multiple decisions together, typically during a quarterly inventory review.

### Theme Identification

- Looking at your last 5-10 decisions, what themes emerge? Are you repeatedly making the same kind of trade-off?
- Which decisions were easiest to make? What do they have in common?
- Which decisions caused the most debate? What made them hard?
- Are there categories of decisions where you are consistently right? Consistently wrong?

### Trade-Off Patterns

- Do you tend to favor one side of common trade-offs? (consistency over availability, simplicity over flexibility, speed over correctness)
- Is that tendency deliberate and documented, or unconscious?
- When you deviate from your usual tendency, what forces cause the deviation?
- Are there trade-offs you avoid making explicitly, instead letting the default win?

### Decision Debt

- Are there decisions you know need to be made but have been deferred?
- What is the cost of deferring those decisions?
- Are there decisions that interact with each other in ways that create emergent problems?
- Do any active decisions contradict each other?

### Organizational Patterns

- Who is involved in which decisions? Is the right expertise in the room?
- How long do decisions take from identification to acceptance? Is that appropriate?
- Are there decisions that get relitigated repeatedly? Why?
- What is the ratio of new decisions to retrospectives being conducted?

## Learning Extraction Prompts

Use these prompts to distill observations into teachable principles.

### From Observation to Principle

1. **State the observation**: "In ADR-005, ADR-012, and ADR-018, we chose managed services over self-hosted alternatives."
2. **Identify the common forces**: "In each case, the team was under time pressure and lacked operational expertise for the self-hosted option."
3. **Articulate the principle**: "When the team lacks operational expertise and the timeline is under 8 weeks, prefer managed services even at higher monetary cost."
4. **Define the boundary**: "This principle does not apply when the managed service creates a hard dependency on a single vendor for a critical capability."
5. **Test the principle**: "Would this principle have improved past decisions? Would it have prevented any mistakes?"

### Principle Quality Checks

A good principle is:
- **Specific enough to act on**: "Prefer managed services" is too vague. "Prefer managed services when ops expertise is absent and timeline is under 8 weeks" is actionable.
- **Falsifiable**: You should be able to describe a situation where the principle does NOT apply.
- **Derived from evidence**: It comes from actual decisions and their outcomes, not from theory.
- **Teachable**: You could explain it to a junior engineer and they would understand when to apply it.

### Anti-Principle Detection

Watch for principles that are actually rationalizations:
- "We always choose PostgreSQL" -- Is this a principle or a comfort zone?
- "Microservices are better for our scale" -- Based on what evidence? Compared to what?
- "We prefer open source" -- Under what conditions? At what cost?

## Common Retrospective Failures and How to Avoid Them

### Confirmation Bias in Reviews

**The failure**: Only looking for evidence that confirms the decision was correct. Ignoring signals that it was wrong.

**How to avoid it**: Start every retrospective by asking "What evidence would convince me this was the wrong decision?" Then actively look for that evidence before examining confirming evidence.

### Hindsight Bias

**The failure**: "Obviously this was going to happen." Rewriting your memory of what you knew at decision time based on what you know now.

**How to avoid it**: Re-read the original ADR before conducting the retrospective. Compare what you predicted with what happened. Do not edit the original predictions -- annotate them with reality.

### Outcome Bias

**The failure**: Judging the decision quality solely by the outcome. A good process can lead to bad outcomes (bad luck), and a bad process can lead to good outcomes (good luck).

**How to avoid it**: Evaluate the process separately from the outcome. Ask: "Given what we knew at the time, was the reasoning sound?" A decision that turned out badly but was well-reasoned is more valuable to learn from than a lucky guess that worked.

### Social Pressure

**The failure**: Softening retrospective findings because the original decision-maker is in the room, or because criticizing past decisions feels disloyal.

**How to avoid it**: Frame retrospectives as learning exercises, not blame exercises. Use the language "the decision" rather than "your decision." Focus on what the team learned, not who was wrong. If possible, have someone other than the original decider lead the retrospective.

### Skipping the Hard Questions

**The failure**: Rushing through the retrospective with surface-level answers. "Yep, still looks good. Moving on."

**How to avoid it**: Use the specific prompts in this document rather than free-form discussion. Require at least one concrete observation for each section. If nothing has changed, explain why -- do not just check a box. The most valuable retrospectives are the ones where something surprising emerges.

### Never Reaching the Principle

**The failure**: Conducting retrospectives but never extracting transferable principles. Each review exists in isolation.

**How to avoid it**: After every third retrospective, conduct a cross-decision pattern analysis. Look for themes. Force yourself to write one principle, even if it feels premature. Principles can be revised -- but unwritten principles cannot be shared.
