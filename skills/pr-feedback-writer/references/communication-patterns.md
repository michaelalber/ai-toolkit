# Communication Patterns

A reference guide for constructive review communication. Every pattern here is designed to achieve the same goal: honest, direct technical feedback that the author can act on without feeling attacked.

---

## Constructive Framing Patterns

These are reusable sentence structures that frame feedback constructively without sacrificing directness.

### The "What if..." Pattern

**Structure**: "What if [alternative approach]? That would [benefit]."

**When to use**: Suggestions and nits where you want to propose an alternative without implying the current approach is wrong.

**Examples**:

> What if we extracted this validation logic into a separate function? That would make it reusable for the admin endpoint that has the same requirements.

> What if this used a set instead of a list for the lookup? That would bring the membership check from O(n) to O(1), which matters since this runs on every request.

> What if we added a timeout to this HTTP call? That would prevent the caller from hanging indefinitely if the downstream service is slow.

**Why it works**: "What if" frames the suggestion as an exploration rather than a correction. It invites the author to evaluate the idea rather than comply with a directive. The "that would" clause provides the "why" -- the benefit that motivates the suggestion.

**Caution**: Do not use "what if" for blocking issues. A security vulnerability needs "Blocking: this must be fixed" not "What if we maybe did not have a SQL injection?"

---

### The "I noticed / I wonder" Pattern

**Structure**: "I noticed [observation]. I wonder if [concern or question]."

**When to use**: When you see something that might be a problem but you are not certain, or when you want to raise a concern without sounding like you are making an accusation.

**Examples**:

> I noticed this function does not handle the case where `user` is null. I wonder if that can happen when the session expires mid-request.

> I noticed the error from the database call is caught but not logged. I wonder if we will be able to debug failures in production without that information.

> I noticed this allocates a new connection for each item in the loop. I wonder if a connection pool or batch operation would be more efficient here, especially when the list is large.

**Why it works**: "I noticed" is an observation, not an accusation. "I wonder" signals genuine curiosity. Together, they convey the concern while leaving space for the author to explain context the reviewer might not have.

**Caution**: This pattern can become passive-aggressive if overused or used for things you are actually certain about. If you know it is a bug, say so. Do not "wonder" about SQL injections.

---

### The "Have you considered..." Pattern

**Structure**: "Have you considered [alternative]? [Reason it might be better]."

**When to use**: Suggestions where you want to present an option the author may not have thought of.

**Examples**:

> Have you considered using a read-write lock here instead of a mutex? The access pattern looks read-heavy, and a read-write lock would allow concurrent reads while still protecting writes.

> Have you considered returning an `Either` type instead of throwing? The callers would be forced to handle both the success and error cases at compile time, which prevents the "forgot to catch" problem we had in the billing module.

> Have you considered using the existing `DateRange` value object? It already handles the edge cases around timezone boundaries that this code is implementing manually.

**Why it works**: "Have you considered" presumes the author made a deliberate choice and offers an alternative for evaluation. It treats the author as a peer making decisions, not a subordinate following instructions.

**Caution**: Can sound condescending if used for obvious things. "Have you considered using a for loop instead of this recursive function that stack-overflows?" -- at that point, just state the problem directly.

---

### The Evidence-Based Pattern

**Structure**: "In my experience with [context], [observation]. [Suggestion based on that experience]."

**When to use**: When your feedback is informed by past experience rather than a hard rule. Particularly effective for architectural and design suggestions.

**Examples**:

> In my experience with event-driven systems, having the producer and consumer share a data model creates tight coupling that becomes painful when either side needs to evolve independently. Consider defining a separate event schema that can version independently of the internal models.

> In my experience, caching at this layer tends to create stale-data bugs that are very hard to reproduce. The last time we added a cache here, we spent two weeks debugging inconsistencies. If we do cache, I would suggest adding cache invalidation metrics so we can detect staleness early.

> In my experience with this API, the rate limits are lower than the documentation suggests. We hit 429s in production at about 60% of the documented limit. I would suggest adding retry logic with backoff even though the current volume is below the stated threshold.

**Why it works**: Grounding feedback in experience makes it concrete rather than theoretical. It also signals humility -- "this is what I have seen" rather than "this is the universal truth." The author can weigh the relevance of the experience to their specific context.

**Caution**: Avoid the authority version of this pattern: "I have been doing this for 15 years and you should..." Experience is context, not rank.

---

## Anti-Patterns with Rewrites

Specific examples of common feedback anti-patterns and how to rewrite them.

### "This is wrong"

**Anti-pattern**:
> This is wrong. Use a parameterized query.

**Problems**: No explanation of why it is wrong, no description of the consequence, imperative tone, no classification.

**Rewrite**:
> Blocking: This query constructs the SQL string by concatenating user input from the request body. An attacker can inject arbitrary SQL through the `search_term` parameter -- for example, `'; DROP TABLE users; --` would delete all user data. Use a parameterized query (`db.query("SELECT * FROM items WHERE name LIKE ?", [search_term])`) to ensure the input is treated as data, not as executable SQL.

**What changed**: Added classification (blocking). Replaced "this is wrong" with a specific description of the vulnerability. Explained the attack vector concretely. Provided the exact fix with a code example. Stated why the fix works (input treated as data, not SQL).

---

### "Why did you do it this way?"

**Anti-pattern**:
> Why did you do it this way? This could be a one-liner.

**Problems**: "Why did you" implies bad judgment. "This could be a one-liner" suggests the author's approach is unnecessarily complex without considering that they might have reasons.

**Rewrite**:
> Suggestion: I am curious about the approach here -- what led to using explicit iteration instead of `filter().map()`? The functional chain would reduce this to a single expression and remove the intermediate `results` array. If there is a readability or debugging reason for the explicit form, I am happy to keep it -- just want to make sure we have considered both options.

**What changed**: Added classification (suggestion). Replaced accusatory question with genuine curiosity about the decision. Stated the alternative with its benefits. Acknowledged the author might have valid reasons. Invited discussion.

---

### "You should use X"

**Anti-pattern**:
> You should use the Builder pattern here.

**Problems**: Imperative and presumptuous. No explanation of why, no acknowledgment that other approaches exist, directed at the person ("you should") rather than the code.

**Rewrite**:
> Suggestion: Have you considered a Builder pattern for this constructor? With 7 optional parameters, the constructor call on line 45 is hard to read -- it is not clear which `null` corresponds to which parameter without checking the signature. A builder would make the intent explicit: `User.builder().withEmail(email).withRole(role).build()`. This is a common pattern in the codebase (see `OrderBuilder` in the payments module for an example).

**What changed**: Added classification (suggestion). Framed as a question rather than a command. Explained the specific problem (7 optional params, unclear nulls). Showed what the builder call would look like. Pointed to an existing example in the codebase for reference.

---

### "This is not how we do things"

**Anti-pattern**:
> This is not how we do things here.

**Problems**: Appeals to unstated norms without explaining them, excludes the author (especially problematic for new team members), provides no path forward.

**Rewrite**:
> Suggestion: Our convention is to use repository classes for database access rather than inline queries. The pattern is documented in the team wiki at [link], and `UserRepository` is a good example of the approach. The main benefit is that it centralizes query logic, which makes it easier to add caching, logging, or connection management consistently. I should note this convention is not well-documented in the onboarding guide -- I will add it after this PR.

**What changed**: Stated the convention explicitly. Provided a reference and example. Explained the reason behind the convention. Took responsibility for the gap in documentation rather than blaming the author for not knowing.

---

### "LGTM" (on code with issues)

**Anti-pattern**:
> LGTM

**Problems**: Provides no value. Does not confirm what was checked. Gives the author false confidence that the code was reviewed.

**Rewrite** (when the code is genuinely good):
> Approved. I reviewed the authentication flow end-to-end. The token validation on line 23 correctly rejects expired tokens, and the error response on line 31 does not leak token details. One thing I appreciated: the separation between token parsing and permission checking makes each step independently testable. Clean implementation.

**What changed**: States what was reviewed. Identifies specific aspects that were verified. Notes what was done well and why. Demonstrates that the reviewer actually read and understood the code.

---

## Tone Calibration by Severity

The urgency and formality of your language should match the severity of the issue.

### Blocking: Clear, Direct, Urgent

**Tone characteristics**: Declarative statements. No hedging. Explicit "must fix before merge" language. Technical precision. Concrete impact description.

**Example**:
> Blocking: The authentication check on line 18 only validates the token format but does not verify the signature. This means any well-formatted token, including expired or forged tokens, will pass authentication. An attacker can access any user's data by crafting a token with the target user's ID. This must be fixed before merge. Use `jwt.verify(token, secret)` instead of `jwt.decode(token)` to ensure cryptographic verification.

**What makes the tone appropriate**: There is no softening because the issue is serious. But notice there is no blame, no sarcasm, no "how could you miss this." It is direct and technical, not personal.

### Suggestion: Collaborative, Reasoning, Open

**Tone characteristics**: Suggestion-framing language. Explanation of benefits. Acknowledgment that the author may disagree. Invitation to discuss.

**Example**:
> Suggestion: This function handles both parsing and validation in a single pass. Consider splitting these into two functions -- one that parses the input into a structured format, and one that validates the structure against business rules. The benefit is that you can unit test each concern independently, and if the validation rules change (which they do quarterly based on compliance updates), you only modify the validation function. Open to other approaches if you see a reason to keep them combined.

**What makes the tone appropriate**: The suggestion is clear and reasoned but leaves room for the author's judgment. The tone conveys "I think this would be better" not "you must do this."

### Nit: Casual, Brief, Explicitly Optional

**Tone characteristics**: Short. Marked as optional. No extensive justification (that would signal it is more important than a nit). Friendly.

**Example**:
> Nit: `processData` could be more descriptive -- maybe `transformSensorReadings`? Totally optional.

**What makes the tone appropriate**: Brevity signals low importance. "Totally optional" makes the classification unmistakable. No multi-paragraph justification for a naming preference.

### Question: Curious, Open, Non-Leading

**Tone characteristics**: Genuine curiosity. Context for why you are asking. No implied judgment.

**Example**:
> Question: I see this retries up to 10 times with no backoff. Is that intentional? I ask because the upstream service has been flaky lately, and I want to make sure rapid retries would not make the problem worse during an outage.

**What makes the tone appropriate**: States the observation, asks directly, and explains why the question matters. No hidden accusation.

### Praise: Specific, Technical, Genuine

**Tone characteristics**: Points to exact code. Explains why it is good. Connects to broader engineering principles.

**Example**:
> Praise: The approach of using a circuit breaker around the payment gateway call is exactly right. This prevents cascade failures when the gateway is down, and the fallback of queuing the charge for retry means we do not lose transactions. Smart design that will save us during the next gateway outage.

**What makes the tone appropriate**: Specific to the code being praised. Explains the engineering reasoning. Demonstrates that the reviewer understands why this decision matters.

---

## Cultural Considerations in Code Review

### High-Context vs Low-Context Communication

Some engineering cultures (and individual engineers) communicate with high context -- meaning is implied, feedback is indirect, and saving face is important. Others communicate with low context -- meaning is explicit, feedback is direct, and efficiency is valued over diplomacy.

**Adapting your feedback**:
- In high-context environments: Softer framing, more questions, fewer directives. "I wonder if..." is more appropriate than "This must change."
- In low-context environments: Direct statements, clear classifications, no ambiguity. "Blocking: fix this" is more efficient and more respected than elaborate softening.
- When you do not know: Default to explicit classification with collaborative framing. This works across cultures because the classification provides the directness while the framing provides the respect.

### Asynchronous Communication Amplifies Tone

In face-to-face conversation, tone of voice, facial expressions, and body language soften direct statements. In a PR comment, the words are all there is. A comment that sounds neutral in person can read as curt or hostile in text.

**Practical adjustments for async review**:
- Add a word of context where you would use tone of voice in person
- "Just a thought:" before a casual suggestion
- "Important:" before a serious concern
- "To clarify my earlier comment:" when adding nuance
- Read your comment from the author's perspective before posting. If you were tired and stressed, how would this land?

### Power Dynamics in Review

The same words carry different weight depending on who says them:
- A tech lead's "suggestion" often feels like a requirement to a junior developer
- A junior developer's "blocking" comment on a senior's code can feel presumptuous
- A peer's "nit" lands differently than a manager's "nit"

**Adjustments**:
- If you have authority over the author: Be more explicit that suggestions are genuinely optional. "This is just a thought -- do not feel obligated to change it."
- If the author has authority over you: Be more explicit about your reasoning. Back up blocking comments with evidence, not just opinion.
- If you are peers: Standard framing works. Classification handles the priority communication.

---

## Handling Disagreement Professionally

### When the Author Pushes Back

An author disagreeing with your feedback is not a failure of communication. It may be a success -- they read your comment, thought about it, and formed a different conclusion. The question is whether the disagreement leads to a productive conversation or an unproductive conflict.

**Productive disagreement pattern**:
1. Acknowledge their reasoning: "I see your point about [their argument]."
2. Clarify your concern: "My worry is specifically about [concrete scenario]."
3. Propose resolution: "Could we [compromise] to address both concerns?" or "I am willing to defer to your judgment here. Let us see how it works in practice."

**Unproductive patterns to avoid**:
- Repeating the same argument louder: "As I said..."
- Appealing to authority: "I have more experience with this."
- Escalating classification: Changing a suggestion to blocking because the author disagreed.
- Silent disapproval: Approving but resenting the decision.

### When You Are Wrong

Reviewers are wrong sometimes. You misread the code, misunderstood the requirement, or suggested something that does not actually work. How you handle being wrong defines your credibility more than how you handle being right.

**When the author shows you are mistaken**:
> "You are right -- I missed that the null check happens in the middleware. My comment about null handling here is not applicable. Sorry for the noise."

**What NOT to do**:
- Silently delete the comment and pretend it never happened
- Double down: "Well, it could still be a problem in theory..."
- Deflect: "I was just being thorough"

Admitting error openly builds more trust than never being wrong.

### When You Cannot Reach Agreement

Sometimes you and the author fundamentally disagree. The issue is not a clear-cut bug -- it is a design judgment, an architectural preference, or a tradeoff where reasonable people differ.

**Resolution strategies**:
- If it is not blocking: Defer to the author. They own the code. State your concern for the record, note your disagreement, and approve. "I still think X would be better for [reason], but I respect your judgment here. Approving."
- If it is blocking: Involve a third reviewer. Do not frame it as "settling a dispute" but as "getting another perspective on a tradeoff."
- If it is a recurring pattern: Raise it outside the PR. "I have noticed we keep debating [topic] in PRs. Can we align on a team convention?"

---

## Review Comment Structure

Every substantive review comment benefits from a consistent internal structure. This is not a rigid template -- it is a checklist of components that make a comment complete.

### The Three-Part Structure: Observation, Impact, Suggestion

**Observation**: What you see in the code. Factual, specific, tied to line numbers.

**Impact**: Why it matters. What goes wrong if this is not addressed. Who is affected and how.

**Suggestion**: What to do about it. A concrete alternative, a reference implementation, or an approach to investigate.

**Example applying all three**:

> Suggestion: The database connection is opened on line 12 but only closed in the success path (line 28). If the validation on line 18 throws, or if the transform on line 22 fails, the connection leaks. [Observation] Over time, leaked connections exhaust the pool, and new requests start failing with timeout errors -- we saw this exact pattern in the order service last quarter. [Impact] Wrapping lines 12-28 in a try/finally (or using a `with` block if the connection supports context management) would ensure the connection is closed regardless of which path executes. [Suggestion]

### When to Skip Parts

- **Nits** can skip Impact and Suggestion: "Nit: typo on line 15 -- 'recieve' should be 'receive'."
- **Praise** skips Suggestion: the whole point is that nothing needs to change.
- **Questions** skip Suggestion: you are asking, not advising.
- **Blocking** comments should never skip any part. The severity demands completeness.

### Comment Length Guidelines

| Classification | Typical Length | Rationale |
|---------------|---------------|-----------|
| Blocking | 3-6 sentences | Must fully explain the issue, its impact, and the fix |
| Suggestion | 2-4 sentences | Explain the concern, the benefit of changing, and the alternative |
| Nit | 1-2 sentences | Brief by definition. Long nits should be reclassified as suggestions |
| Question | 1-3 sentences | State what you observed, ask your question, explain why you are asking |
| Praise | 1-3 sentences | Point to what is good and why. Do not over-elaborate |

### The "One Comment Per Concern" Rule

Each review comment should address exactly one concern. Combining multiple issues into a single comment makes it hard for the author to respond to each one, mark items as resolved, or track which feedback has been addressed.

**Anti-pattern** (multiple concerns in one comment):
> The variable name is confusing, also this does not handle null, and you should probably add a test for the edge case where the list is empty.

**Better** (three separate comments):
> Comment 1 (Nit, line 5): `data` is ambiguous here -- consider `userRecords` to distinguish from the config data on line 30.

> Comment 2 (Blocking, line 12): This dereferences `user.address` without a null check. If the user has not set an address (which is optional in the registration flow), this throws a NullPointerException. Add a null check or use optional chaining.

> Comment 3 (Suggestion, line 20): Consider adding a test case for an empty input list. The current tests cover single-item and multi-item cases, but the empty case exercises the early return on line 8.

Each concern gets its own classification, its own discussion thread, and its own resolution tracking.
