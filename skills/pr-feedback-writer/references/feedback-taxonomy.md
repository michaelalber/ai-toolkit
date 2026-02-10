# Feedback Taxonomy

A comprehensive classification system for PR review comments. Correct classification is the foundation of effective review communication -- it tells the author how to prioritize, how urgently to respond, and what latitude they have.

---

## Comment Types Defined

### Blocking

**Definition**: A blocking comment identifies an issue that must be fixed before the PR can be merged. The reviewer will not approve the PR until this is addressed.

**When to use blocking**:
- Security vulnerabilities (SQL injection, XSS, authentication bypass, secrets in code)
- Correctness bugs that will produce wrong results in production
- Data loss or corruption risks
- Contract violations (API breaking changes without versioning, schema migrations that destroy data)
- Compliance violations (PII handling, audit logging requirements)
- Resource leaks that will degrade production systems (unclosed connections, memory leaks in hot paths)

**When NOT to use blocking**:
- Style preferences, even strong ones
- Performance concerns in non-critical paths
- "I would have done it differently" opinions
- Missing tests (unless the code is untestable or the change is high-risk)
- Documentation gaps

**The blocking test**: "If this ships as-is, will it cause harm to users, data integrity, or system reliability?" If yes, blocking. If no, it is a suggestion or nit.

---

### Suggestion

**Definition**: A suggestion identifies something that should be improved but where the author has latitude to disagree or defer. The reviewer is saying "I think this should change, but I will not block the PR over it."

**When to use suggestion**:
- Error handling that is incomplete but not dangerous
- Performance improvements in code that is not on a hot path
- Design patterns that would improve maintainability
- Missing tests for non-critical paths
- Naming improvements that affect readability
- Refactoring opportunities that would reduce complexity
- Documentation that would help the next developer

**When NOT to use suggestion**:
- Issues that would cause real harm if ignored (those are blocking)
- Pure preferences with no objective basis (those are nits)
- Things you are unsure about (those are questions)

**The suggestion test**: "If the author pushes back with a reasonable justification, would I accept it?" If yes, suggestion. If no, it is probably blocking.

---

### Nit

**Definition**: A nit is an optional observation. The reviewer is explicitly communicating "this is my preference; take it or leave it." The author can ignore every nit in a review without consequence.

**When to use nit**:
- Formatting preferences not enforced by linting
- Alternative naming that is equally valid
- Minor style inconsistencies
- "While you are here" improvements to adjacent code
- Subjective readability preferences
- Trivial optimizations with no measurable impact

**When NOT to use nit**:
- Anything you actually want fixed (be honest -- that is a suggestion)
- Issues that will bother you if they ship (again, that is a suggestion)
- Objective improvements to clarity or correctness (those are suggestions)

**The nit test**: "If the author ignores this comment entirely and merges, will I care?" If no, it is a nit. If yes, reclassify.

**The nit honesty check**: Many reviewers label comments as "nit" to seem non-confrontational when they actually want the change made. This is dishonest classification. If you expect the author to address it, do not call it a nit. Call it what it is: a suggestion.

---

### Question

**Definition**: A genuine question seeking understanding. Not a rhetorical question, not a disguised criticism, not a leading question where you already know the answer you want. A real question.

**When to use question**:
- You genuinely do not understand the approach and want to learn
- You suspect an issue but are not sure and want the author's perspective
- You want to understand context that is not in the PR description
- You see a pattern you are unfamiliar with and want explanation

**When NOT to use question**:
- You already know the answer and want the author to "figure it out" (this is Socratic method misapplied -- just state your concern)
- You are using question form to soften a criticism ("Have you considered not introducing a SQL injection?")
- The question is rhetorical ("Do we really want to ship this?")

**Distinguishing genuine questions from disguised criticism**:

| Disguised Criticism | Genuine Question |
|-------------------|-----------------|
| "Why would you do it this way?" | "I have not seen this pattern before -- what advantage does it give us over the more common approach?" |
| "Have you considered testing this?" | "What is your testing plan for this? I want to understand the coverage strategy." |
| "Is this really the best approach?" | "I am trying to understand the tradeoffs here. What alternatives did you consider?" |
| "Do you think this will scale?" | "I am not sure how this behaves at 10x current load. Do you have data on the scaling characteristics?" |

---

### Praise

**Definition**: Specific, substantive positive feedback that reinforces good decisions and demonstrates that the reviewer engaged deeply with the code.

**When to use praise**:
- Clever solutions to genuinely hard problems
- Good use of design patterns in appropriate contexts
- Thoughtful error handling or edge case coverage
- Clear, well-structured code in a complex domain
- Good test design (especially for tricky scenarios)
- Improvements to existing code quality beyond what the PR required

**When NOT to use praise**:
- As a softener before criticism ("Nice work overall, but...")
- Generically ("Looks good!" adds no value)
- For meeting basic expectations ("Good job writing tests" -- tests are expected)

**Specific vs generic praise**:

| Generic (Noise) | Specific (Signal) |
|----------------|-------------------|
| "Nice!" | "Good call making this idempotent -- that will save us debugging headaches in the retry logic." |
| "Looks good" | "The approach of separating the validation from the transformation here makes each step independently testable. Clean design." |
| "LGTM" | "I verified the thread safety of this implementation. The read-write lock is the right choice given the read-heavy access pattern." |

---

## Decision Tree for Classification

Use this decision tree when you are unsure how to classify a comment.

```
Is there a concrete risk of harm (security, data loss, incorrect results)?
|
+-- YES --> BLOCKING
|
+-- NO
    |
    Do you genuinely not understand something and want to learn?
    |
    +-- YES --> QUESTION
    |
    +-- NO
        |
        Is the author doing something particularly well?
        |
        +-- YES --> PRAISE (be specific)
        |
        +-- NO
            |
            If the author ignores this, will the codebase be objectively worse?
            |
            +-- YES --> SUGGESTION
            |
            +-- NO
                |
                Is this a preference with no objective basis?
                |
                +-- YES --> NIT
                |
                +-- NO --> Reconsider. You may need SUGGESTION.
```

### Secondary classification factors:

**Upgrade conditions** -- when a lower classification should be escalated:
- A nit becomes a suggestion when the inconsistency affects multiple files
- A suggestion becomes blocking when the same pattern has caused incidents before
- A question becomes a suggestion when you have enough evidence to state a concern

**Downgrade conditions** -- when a higher classification should be reduced:
- A blocking becomes a suggestion when the risk is theoretical and the code path is rarely executed
- A suggestion becomes a nit when the improvement is marginal and the code is scheduled for rewrite
- A blocking becomes a suggestion when there are mitigating controls elsewhere in the system

---

## Examples: Good and Bad Versions

### Blocking Comment

**Bad version**:
> You have a SQL injection here. Fix it.

Problems: Blame-directed ("you have"), no explanation of why it matters, no guidance on how to fix it, imperative tone.

**Good version**:
> Blocking: The query on line 34 concatenates user input directly into the SQL string, which creates a SQL injection vulnerability. An attacker could use the `name` parameter to execute arbitrary queries -- for example, extracting the entire users table. Use a parameterized query (`db.query("SELECT * FROM users WHERE name = ?", [name])`) to prevent this. This must be fixed before merge.

Why it works: States the classification explicitly, identifies the exact location, explains the attack vector, provides a concrete fix, and states the merge requirement clearly.

---

### Suggestion Comment

**Bad version**:
> This should use a map instead of a for loop.

Problems: No explanation of why, imperative tone, no acknowledgment that the author might have reasons for their approach.

**Good version**:
> Suggestion: Consider using `map()` instead of the for loop here. It would eliminate the manual array management on lines 12-15 and make the transformation intent clearer. The current approach works correctly, but `map()` would make it immediately obvious that this is a one-to-one transformation with no filtering or accumulation. Happy to discuss if you see a reason to keep the explicit loop.

Why it works: States classification, suggests rather than demands, explains the benefit, acknowledges the current code works, invites dialogue.

---

### Nit Comment

**Bad version**:
> Rename this variable.

Problems: No alternative suggested, no reason given, could be interpreted as a demand.

**Good version**:
> Nit: `data` is a bit ambiguous here since lines 20-35 work with three different data representations (raw, validated, and transformed). Something like `raw_input` would make it clear which stage this represents. Totally optional -- just a readability thought.

Why it works: States classification, provides a concrete alternative, explains the reasoning, explicitly marks it as optional.

---

### Question Comment

**Bad version (disguised criticism)**:
> Why did you not use the existing validation library?

Problems: "Why did you not" implies the author made a mistake. This is not a genuine question -- it is criticism in question form.

**Good version**:
> Question: I noticed this implements custom validation logic for email addresses. We have the `validator` library in our dependencies that handles this. Is there a specific requirement here that the library does not cover? I ask because the library also handles internationalized email addresses and edge cases that are easy to miss in custom implementations.

Why it works: States classification, provides context (the library exists), asks a genuine question (maybe there IS a reason), explains why it matters.

---

### Praise Comment

**Bad version**:
> Nice.

Problems: Adds no information. The author does not know what is being praised or why.

**Good version**:
> Praise: The retry logic here with exponential backoff and jitter is exactly right for this use case. I have seen implementations that use fixed delays and hammer the upstream service during outages. The jitter prevents the thundering herd problem and the max-retry cap prevents infinite loops. Well thought out.

Why it works: Identifies exactly what is being praised, explains why it is the right approach, demonstrates that the reviewer understood the code deeply enough to evaluate the design decision.

---

## How Classification Changes by Context

The same code issue warrants different classifications depending on context.

### Production Code vs Prototype

| Issue | Production Code | Prototype / Spike |
|-------|----------------|-------------------|
| Missing input validation | Blocking -- unvalidated input in production is a security risk | Suggestion -- worth noting for when the code graduates to production |
| No error handling on API call | Blocking -- will crash in production when the API is unavailable | Nit -- for a spike, logging the error is sufficient |
| Hard-coded configuration | Suggestion -- should be externalized for deployment flexibility | Nit -- prototypes often hard-code values; flag for later |
| Missing tests | Suggestion -- production code should be tested | Nit or omit -- spikes are exploratory; tests come when the approach is validated |

### Security-Critical vs Internal Tool

| Issue | Security-Critical System | Internal Developer Tool |
|-------|------------------------|----------------------|
| SQL injection | Blocking -- immediate, high severity | Blocking -- still blocking, but explanation can be shorter since impact is lower |
| Missing rate limiting | Blocking -- DoS risk on public-facing endpoints | Suggestion -- internal tools have lower abuse risk but should still be robust |
| Verbose error messages | Blocking -- leaks implementation details to attackers | Nit -- internal users benefit from detailed error messages |
| Session management gaps | Blocking -- authentication/authorization are core security controls | Suggestion -- internal tools may rely on network-level access control |

### Junior Author vs Senior Author

The classification does not change based on author seniority -- a bug is a bug regardless of who wrote it. What changes is the communication:

| Scenario | Junior Author | Senior Author |
|----------|--------------|---------------|
| Blocking security issue | Full explanation of the vulnerability, the attack vector, and the fix. Include references to OWASP or internal security documentation. | Concise identification: "Blocking: SQL injection on line 34 via string concatenation. Parameterize the query." |
| Suggestion for better pattern | Explain the pattern, why it is preferred, and link to an example in the codebase. "Have you seen the approach in `UserService`? That pattern handles this case well." | State the suggestion and the reason. Trust them to evaluate: "Suggestion: builder pattern would simplify construction here given the optional params." |
| Nit on naming | Frame as team convention: "Nit: our convention is camelCase for local variables. I know it is easy to miss when you are focused on the logic." | Simple note: "Nit: camelCase convention for locals." |

---

## Classification Integrity

### The Credibility Cost of Mis-Classification

Every time a reviewer marks a nit as blocking, their future blocking comments carry less weight. Every time a reviewer marks a real issue as a nit, they enable a defect to ship. Classification accuracy is directly tied to reviewer credibility.

**Over-classification** (marking too many things as blocking):
- Authors learn to ignore your blocking comments
- PRs stall on trivia
- You develop a reputation as a bottleneck
- Your genuinely important feedback gets lost in the noise

**Under-classification** (marking too few things as blocking):
- Defects ship to production
- Authors miss learning opportunities about severity
- The team's quality bar silently drops
- You avoid short-term conflict at the cost of long-term reliability

### Calibration Exercise

For any comment you are about to classify, ask these three questions:

1. "If this ships and causes an incident at 3am, would I say 'I told them in the review'?" If yes, it had better be blocking.
2. "If the author responds 'I disagree and I am merging', would I request changes?" If yes, it is at least a suggestion. If you would block the merge, it is blocking.
3. "If I were the author and received this classification, would I think it was fair?" If the answer is "they would think I am being dramatic," you may be over-classifying.
