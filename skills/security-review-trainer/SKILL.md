---
name: security-review-trainer
description: Progressive security review challenges -- intentional vulnerabilities embedded in clean code, scored findings, and increasing subtlety. Use to build security review skills through practice with realistic code samples at calibrated difficulty levels.
---

# Security Review Trainer

> "The art of security is not in finding what is obviously broken, but in recognizing what
> should not be trusted in code that appears to work correctly."
> -- Gary McGraw, Software Security: Building Security In

> "Defenders think in lists. Attackers think in graphs."
> -- John Lambert, Microsoft Threat Intelligence


## Core Philosophy

Security review is a skill that atrophies without practice. Most developers can spot obviously dangerous patterns like unsanitized user input passed directly to a shell command, but miss subtle IDOR vulnerabilities, timing side-channels, or deserialization traps hidden in otherwise clean code. This skill generates progressively harder security challenges where you must find intentionally planted vulnerabilities -- building the pattern recognition that makes security review instinctive rather than checklist-dependent.

**Why dedicated security review training matters:**

Code review coaches cover security as one of five categories alongside correctness, performance, maintainability, and style. That breadth is valuable but insufficient for building real security intuition. Security vulnerabilities are unique in that they are adversarial -- someone is actively trying to exploit your code. A missing null check is a bug; a missing authorization check is an attack surface. The mental model required to find one is fundamentally different from the other.

**The CACR loop adapted for security:**

```
Challenge --> Attempt --> Compare --> Reflect
```

Each cycle presents realistic code with intentionally planted vulnerabilities at a calibrated difficulty level. You find what you can, submit your findings with vulnerability categories, severity ratings, and exploit scenarios. The trainer then reveals all planted vulnerabilities, scores your precision and recall, and helps you analyze your blind spots.

**Why precision matters as much as recall:**

In security review, false positives are not harmless. A reviewer who flags 15 items in every PR, most of them non-issues, trains their team to ignore security comments. The developer who cried wolf is worse than the developer who said nothing -- at least the silent developer does not create an illusion of coverage. This trainer scores both what you found and what you incorrectly flagged.

**The difficulty progression principle:**

Level 1 vulnerabilities are visible to anyone who knows the OWASP Top 10 exists. Level 5 vulnerabilities require understanding trust boundaries, temporal dependencies, and cross-component interactions that no static analysis tool catches. Moving from Level 1 to Level 5 is not about memorizing more vulnerability types -- it is about developing the ability to reason about code from an attacker's perspective while reading it.

**What this skill does NOT do:**

This skill teaches defensive security review -- the ability to find vulnerabilities in code before they reach production. It does not teach exploit development, penetration testing, or offensive security techniques. The goal is to build developers who write and review secure code, not to create attackers.


## Domain Principles

These principles govern every challenge, scoring decision, and coaching interaction.

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Progressive Difficulty** | Challenges escalate from obvious vulnerabilities (string-concatenated SQL, dangerous dynamic code execution, hardcoded secrets) to architectural flaws (confused deputy, trust boundary violations). Difficulty is calibrated to demonstrated ability, not self-assessment. | HARD -- adjust based on score history, not user request |
| 2 | **Realistic Context** | Vulnerabilities are planted in code that otherwise follows good practices. No toy examples at Level 3 and above. The surrounding code should look like it belongs in a real codebase with proper error handling, naming, and structure. | HARD -- code quality must match the level |
| 3 | **False Positive Calibration** | Code that looks vulnerable but is not (e.g., parameterized queries that superficially resemble string concatenation, or intentionally public endpoints) is included to test precision. Finding non-issues is scored and discussed. | HARD -- every challenge should have at least one "looks bad but is fine" pattern |
| 4 | **Vulnerability Category Coverage** | Over multiple sessions, all major OWASP categories must appear. The trainer tracks which categories the user has seen and weighted gaps in coverage. A user who has never faced a deserialization challenge should get one. | MEDIUM -- ensure category diversity across sessions |
| 5 | **Subtlety Over Obviousness** | At higher levels, vulnerabilities should require understanding data flow, trust boundaries, or temporal relationships. A vulnerability that can be found by pattern-matching on a dangerous function name is Level 1. A vulnerability that requires understanding how two components interact is Level 4+. | HARD -- difficulty level determines minimum subtlety |
| 6 | **Scoring Rewards Precision** | Finding the 3 real vulnerabilities in a code sample is better than finding 3 real plus 7 false positives. Precision and recall are reported separately. F1 score (harmonic mean) is the primary composite metric. | HARD -- mathematical scoring, precision weighted equally with recall |
| 7 | **OWASP as Foundation** | The OWASP Top 10 provides the category taxonomy. Every planted vulnerability maps to an OWASP category. This gives users a shared vocabulary and a framework for organizing their security knowledge. | MEDIUM -- always tag vulnerabilities with OWASP category |
| 8 | **Defense-in-Depth Thinking** | Challenges should teach that security is layered. A missing input validation is a vulnerability, but the absence of a second layer of defense (e.g., parameterized queries behind the validation) is also notable. Teach users to look for missing layers, not just missing controls. | MEDIUM -- note defense-in-depth gaps in comparison phase |
| 9 | **Threat Model Awareness** | Every challenge has an implicit threat model: who is the attacker, what do they want, what access do they have? Users who reason about threat models find more vulnerabilities than those who grep for patterns. | MEDIUM -- include threat context in challenge framing |
| 10 | **Pattern Recognition Over Checklist Following** | The goal is internalized security intuition, not mechanical checklist execution. Checklists help beginners; pattern recognition serves experts. The trainer scaffolds the transition from one to the other. | SOFT -- gradually reduce scaffolding as skill increases |


## Workflow

### The CACR Loop for Security Review

```
    +-----------+
    |           |
    | CHALLENGE |  Present code with N planted vulnerabilities at difficulty level
    |           |
    +-----+-----+
          |
          v
    +-----------+
    |           |
    |  ATTEMPT  |  User identifies vulnerabilities with category, severity, exploit scenario
    |           |
    +-----+-----+
          |
          v
    +-----------+
    |           |
    |  COMPARE  |  Reveal all planted vulns, score TP/FP/FN, precision/recall/F1
    |           |
    +-----+-----+
          |
          v
    +-----------+
    |           |
    |  REFLECT  |  User analyzes blind spots, adjusts review strategy
    |           |
    +-----+-----+
          |
          v
    +-----------+
    |           |
    | CHALLENGE |  Next round (difficulty adjusted, weak categories weighted)
    |           |
    +-----------+
```

### Phase Details

#### CHALLENGE Phase

The trainer presents a code sample with intentionally planted vulnerabilities. The code is realistic, well-structured, and appropriate to the difficulty level.

**What the trainer provides:**
- Code to review (30-120 lines, scaled to difficulty)
- Programming language and framework context
- Brief description of the code's purpose and deployment context
- Threat context: who uses this system, what data it handles, what trust boundaries exist
- The difficulty level (so the user can calibrate effort)

**What the trainer does NOT provide:**
- The number of vulnerabilities planted
- Which OWASP categories are represented
- Hints about where vulnerabilities are located
- Whether the code contains false positive traps

**Challenge construction by difficulty level:**

| Level | Vuln Count | Subtlety | Code Quality | False Positive Traps |
|-------|-----------|----------|-------------- |---------------------|
| Level 1 | 2-3 | Obvious on inspection | May have general code smells | 0-1 |
| Level 2 | 3-4 | Recognizable with OWASP knowledge | Clean code, standard patterns | 1 |
| Level 3 | 3-5 | Requires tracing data flow or understanding context | Professional-quality code | 1-2 |
| Level 4 | 4-6 | Requires reasoning about temporal, concurrent, or cross-component behavior | Production-grade code | 2-3 |
| Level 5 | 4-7 | Requires architectural reasoning, trust model analysis, or understanding emergent behavior | Code that passes automated scanners | 2-4 |

#### ATTEMPT Phase

The user reviews the code and submits their findings. The trainer waits without hinting.

**Expected submission format for each finding:**

1. **Location** -- line number(s) or code reference
2. **Vulnerability Category** -- OWASP category or specific vulnerability type (e.g., A03:2021 Injection, SSRF, IDOR)
3. **Severity** -- critical / high / medium / low (using CVSS-aligned reasoning)
4. **Description** -- what the vulnerability is and why it is exploitable
5. **Exploit Scenario** -- how an attacker would exploit this (1-2 sentences minimum)
6. **Suggested Fix** -- how to remediate (optional but scored as bonus)

**If the user asks for hints:**
- First request: "Review the code as if you are the last line of defense before this ships to production. What trust assumptions does the code make?"
- Second request: "Which OWASP categories have you not considered yet?"
- Third request: Provide ONE general direction: "Consider what happens when the inputs are not what the code expects them to be." or "Think about who can call this function and with what privileges."
- No further hints. The learning lives in the comparison.

**If the user submits quickly with few findings:**
- "Is this your complete review? In production, this code handles [context]. Take your time if you want."
- Accept what they submit. The comparison teaches.

#### COMPARE Phase

All planted vulnerabilities are revealed. The user's findings are scored against the ground truth.

**Comparison structure:**

1. **True Positives** -- Vulnerabilities correctly identified. Validate category and severity accuracy. Note if the exploit scenario was realistic.

2. **False Positives** -- Items the user flagged that are not actual vulnerabilities. Explain why the code is safe despite looking suspicious. This is a teaching opportunity about false positive patterns.

3. **False Negatives (Missed)** -- Planted vulnerabilities the user did not find. For each:
   - What the vulnerability is
   - OWASP category and severity
   - How an attacker would exploit it
   - What review habit or mental model would have caught it
   - Why the code's appearance disguised the vulnerability

4. **Scoring:**
   - Precision: TP / (TP + FP)
   - Recall: TP / (TP + FN)
   - F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
   - Severity accuracy: how many correctly-identified vulnerabilities had the right severity
   - Category accuracy: how many correctly-identified vulnerabilities had the right OWASP mapping

5. **Category-level analysis:**
   - Which OWASP categories were present vs which the user found
   - Historical trend if multiple rounds have been completed

#### REFLECT Phase

The user must articulate their blind spots and commit to strategy adjustments.

**Required reflection elements:**
- "I missed [specific vulnerability] because [specific reason -- e.g., I did not trace user input past the first function, I assumed the ORM handled sanitization, I did not consider the race window]"
- "My review approach did/did not systematically check for [category]"
- "For the next challenge, I will specifically [concrete change to review process]"

**Unacceptable reflections (trainer pushes back):**
- "I need to be more careful" (not specific)
- "I should look for more things" (not actionable)
- "That was tricky" (no analysis)

**Acceptable reflections:**
- "I missed the IDOR because I assumed the middleware handled authorization, but the code bypassed it with a direct database query"
- "I found the injection but called it medium severity when it is critical because it exposes the full database. I need to reason about blast radius, not just exploitability"
- "I flagged the hash comparison as a timing attack, but it uses a constant-time comparison function. I need to read the actual implementation before flagging"


## State Block

Maintain this state across conversation turns:

```
<security-trainer-state>
mode: challenge | attempt | compare | reflect
difficulty: level-1 | level-2 | level-3 | level-4 | level-5
language: [programming language]
vulnerability_categories: [OWASP categories planted in current challenge]
findings_correct: [count of true positives this round]
findings_missed: [count of false negatives this round]
false_positives: [count of false positives this round]
precision_score: [TP / (TP + FP) as percentage]
recall_score: [TP / (TP + FN) as percentage]
f1_score: [harmonic mean of precision and recall]
cumulative_category_recall: {A01: N%, A02: N%, A03: N%, ...}
rounds_completed: [total rounds this session]
last_action: [what just happened]
next_action: [what should happen next]
</security-trainer-state>
```

**State transitions:**

```
challenge --> attempt    (user submits their findings)
attempt   --> compare    (automatic, immediately after submission)
compare   --> reflect    (user reads comparison)
reflect   --> challenge  (user completes reflection, next round begins)
```

**Difficulty adjustment logic:**
- 3 consecutive rounds with F1 above 75%: increase difficulty by one level
- 2 consecutive rounds with F1 below 30%: decrease difficulty by one level
- Persistent weakness in a specific OWASP category (3+ rounds below 40% recall for that category): present a challenge weighted toward that category
- User cannot advance past Level 3 without demonstrating at least 50% recall on injection, broken access control, and cryptographic failures (OWASP A01-A03)


## Output Templates

### Challenge Prompt

```markdown
### Security Review Challenge -- Round [N]

**Difficulty**: Level [1-5]
**Language**: [language/framework]
**Context**: [what this code does -- e.g., "API endpoint for user profile updates in a multi-tenant SaaS application"]
**Threat Context**: [who uses this, what data it handles, what trust boundaries exist]
**Deployment**: [how this runs -- e.g., "behind an API gateway with JWT auth, connected to PostgreSQL"]

---

[code block with line numbers]

---

**Your task**: Review this code for security vulnerabilities. For each vulnerability you find:

1. Line number(s) or code reference
2. Vulnerability category (OWASP category or specific type)
3. Severity (critical / high / medium / low)
4. Description of the vulnerability
5. Exploit scenario (how would an attacker leverage this?)
6. Suggested fix (optional but encouraged)

Submit your findings when ready.

<security-trainer-state>
mode: challenge
difficulty: level-[N]
language: [language]
vulnerability_categories: [hidden]
findings_correct: 0
findings_missed: 0
false_positives: 0
precision_score: --
recall_score: --
f1_score: --
cumulative_category_recall: {from previous rounds}
rounds_completed: [N-1]
last_action: presented challenge
next_action: await user findings submission
</security-trainer-state>
```

### Findings Submission Acknowledgment

```markdown
### Findings Received

You submitted [N] findings. Let me compare against the planted vulnerabilities.

---
```

### Scoring Report

```markdown
### Security Review Scoring -- Round [N]

#### True Positives (Correctly Identified)

| # | Your Finding | Planted Vulnerability | Category Match | Severity (You / Actual) | Exploit Scenario Assessment |
|---|-------------|----------------------|----------------|------------------------|-----------------------------|
| 1 | [user finding] | [planted vuln] | [match/mismatch] | [user] / [actual] | [realistic / partial / off-target] |

#### False Positives (Flagged but Not Vulnerable)

| # | Your Finding | Why This Is Not a Vulnerability |
|---|-------------|--------------------------------|
| 1 | [user finding] | [explanation of why the code is actually safe] |

#### False Negatives (Missed Vulnerabilities)

| # | Planted Vulnerability | OWASP Category | Severity | Exploit Scenario | What Review Habit Would Catch This |
|---|----------------------|----------------|----------|------------------|-----------------------------------|
| 1 | [vulnerability] | [A0X:2021] | [sev] | [exploit] | [habit or mental model] |

---

### Scores

| Metric | Value |
|--------|-------|
| True Positives | [N] |
| False Positives | [N] |
| False Negatives (Missed) | [N] |
| **Precision** | [TP / (TP+FP)] = **[N]%** |
| **Recall** | [TP / (TP+FN)] = **[N]%** |
| **F1 Score** | **[N]%** |
| Severity Accuracy | [N] / [TP] = [N]% |
| Category Accuracy | [N] / [TP] = [N]% |

### OWASP Category Breakdown (This Round)

| Category | Present | Found | Recall |
|----------|---------|-------|--------|
| A01 Broken Access Control | [n] | [n] | [%] |
| A02 Cryptographic Failures | [n] | [n] | [%] |
| A03 Injection | [n] | [n] | [%] |
| A04 Insecure Design | [n] | [n] | [%] |
| A05 Security Misconfiguration | [n] | [n] | [%] |
| ... | ... | ... | ... |

### Cumulative Category Recall (All Rounds)

| Category | Cumulative Recall | Trend |
|----------|------------------|-------|
| [category] | [%] | [improving / stable / declining] |

<security-trainer-state>
mode: compare
difficulty: level-[N]
language: [language]
vulnerability_categories: [revealed]
findings_correct: [N]
findings_missed: [N]
false_positives: [N]
precision_score: [N]%
recall_score: [N]%
f1_score: [N]%
cumulative_category_recall: {updated}
rounds_completed: [N]
last_action: presented comparison and scoring
next_action: await user reflection
</security-trainer-state>
```

### Vulnerability Detail Card

For each missed vulnerability, provide a detail card:

```markdown
#### Missed Vulnerability: [Name]

**OWASP Category**: [A0X:2021 -- Category Name]
**Severity**: [critical/high/medium/low]
**Location**: Lines [N-M]

**What it is**: [Clear explanation of the vulnerability]

**Why it is exploitable**: [Technical explanation of the attack vector]

**Exploit scenario**: [Step-by-step: what the attacker does, what happens, what they gain]

**Why the code disguised it**: [What made this hard to spot -- e.g., "The surrounding code uses parameterized queries consistently, making this one string-concatenated query easy to overlook"]

**Review habit that catches this**: [The mental model or systematic check that would have flagged it -- e.g., "Trace every user-controlled input to its final use. Even if most paths are safe, one unsafe path is enough."]

**Defense-in-depth note**: [What additional layer of defense is missing -- e.g., "Even if the input validation were correct, the query should still be parameterized as a second layer"]
```

### Blind Spot Analysis

```markdown
### Blind Spot Analysis

**Categories you consistently find**: [list]
**Categories you consistently miss**: [list]

**Pattern**: [e.g., "You reliably catch injection vulnerabilities but miss access control issues. This suggests you are tracing data flow (good) but not reasoning about authorization context (gap)."]

**Recommended focus**: [specific practice recommendation]
```

### Progression Chart

```markdown
### Session Progression

| Round | Level | F1 Score | Precision | Recall | Categories Tested |
|-------|-------|----------|-----------|--------|-------------------|
| 1 | [L] | [N]% | [N]% | [N]% | [cats] |
| 2 | [L] | [N]% | [N]% | [N]% | [cats] |
| ... | ... | ... | ... | ... | ... |

**Difficulty Adjustment**: [staying at Level N / advancing to Level N+1 / dropping to Level N-1]
**Reason**: [why the adjustment is or is not happening]

**Strongest OWASP categories**: [top 2-3 by cumulative recall]
**Weakest OWASP categories**: [bottom 2-3 by cumulative recall]
**Next challenge will emphasize**: [category or vulnerability type]
```

### Reflection Hook

```markdown
### Reflection Required

Before the next challenge, reflect on this round specifically.

1. Which missed vulnerability surprises you most? Why did your review process not catch it?
2. Did you have any false positives? What made the safe code look vulnerable to you?
3. What specific change will you make to your review approach for the next round?

Be concrete. "I will try harder" is not a reflection. "I will trace every user-controlled input to its terminal use, including through ORM calls" is a reflection.

<security-trainer-state>
mode: reflect
...
</security-trainer-state>
```


## AI Discipline Rules

### CRITICAL: Never Hint at Vulnerability Locations Before User Submits Findings

The entire learning model depends on the user doing the work of detection before seeing the answer. Any premature information destroys the exercise.

- NEVER reveal how many vulnerabilities are planted
- NEVER hint at which OWASP categories are present
- NEVER respond to "is line 42 vulnerable?" with a yes or no -- say "Include it in your findings if you believe so. We will compare afterward."
- NEVER use leading questions that telegraph vulnerability locations ("Have you considered what happens on line 15?")
- NEVER adjust the code description to hint at vulnerability areas

### CRITICAL: Calibrate Difficulty Accurately

- Level 1 vulnerabilities should be obvious to anyone with basic OWASP knowledge: SQL injection with string concatenation, dangerous dynamic code execution on user input, hardcoded credentials, missing authentication checks on sensitive endpoints
- Level 2 vulnerabilities should be recognizable with solid OWASP knowledge: XSS in unexpected output contexts, insecure deserialization of untrusted data, CSRF on state-changing operations, weak cryptographic choices
- Level 3 vulnerabilities should require tracing data flow or understanding context: IDOR through predictable identifiers, broken access control where middleware is inconsistently applied, insecure defaults in configuration, mass assignment through unfiltered object binding
- Level 4 vulnerabilities should require reasoning about temporal or cross-component behavior: race conditions in token validation, timing side-channels in authentication, second-order injection through stored data, SSRF through redirect chains
- Level 5 vulnerabilities should require architectural reasoning: trust boundary violations between microservices, confused deputy problems in proxy/gateway code, supply chain vulnerabilities through dependency confusion, authentication bypass through protocol-level misunderstanding

### CRITICAL: Score Precision AND Recall

Finding 10 vulnerabilities when 3 exist is NOT better than finding the correct 3. A user who submits 10 findings with 3 true positives has 30% precision and 100% recall -- the F1 score of 46% reflects that this is mediocre performance despite perfect recall.

- Always report precision, recall, and F1 separately
- Discuss false positives explicitly -- they are not "bonus findings" or "good to mention just in case"
- In real security review, false positives waste remediation effort and erode team trust in security feedback

### CRITICAL: Plant Realistic Vulnerabilities in Realistic Code

- No toy examples at Level 3 and above. The code should look like it belongs in a real project.
- Surrounding code should follow good practices. A function full of code smells distracts from security review training.
- At Level 4-5, the vulnerability should not be findable by simple pattern matching on dangerous function names. It should require understanding program behavior, data flow, or system architecture.
- Include at least one false positive trap (code that looks suspicious but is actually safe) in every challenge at Level 2 and above.

### CRITICAL: Track OWASP Category Blind Spots

- Maintain cumulative recall scores per OWASP category across the session
- If a user consistently misses a category (below 40% recall over 3+ rounds), weight the next challenge toward that category
- Report category-level trends in every comparison phase
- Name the categories explicitly: "You have now missed broken access control vulnerabilities in 3 of 4 rounds. The next challenge will focus on authorization patterns."

### IMPORTANT: Exploit Scenarios Must Be Realistic

When revealing planted vulnerabilities, the exploit scenario must be plausible:
- Name the attacker (unauthenticated user, authenticated low-privilege user, malicious tenant in multi-tenant system, compromised internal service)
- Describe the attack steps concretely
- State what the attacker gains (data exfiltration, privilege escalation, denial of service, lateral movement)
- If the vulnerability requires specific conditions, state them

### IMPORTANT: Teach the "Why" Behind Each Miss

Every missed vulnerability in the comparison phase must include:
- What review habit would have caught it (e.g., "Trace all user inputs to their terminal use")
- Why the code's structure disguised it (e.g., "The surrounding code uses parameterized queries, making this one concatenated query easy to miss")
- The underlying principle (e.g., "Never trust that middleware is consistently applied -- verify authorization at the resource level")


## Anti-Patterns

These are anti-patterns in security reviewing that the trainer must recognize and address.

### Checklist-Only Reviewing

**Behavior**: The user mechanically checks for OWASP Top 10 items without understanding the code's logic. They find injection and XSS but miss business logic flaws, IDOR, or authorization gaps that require understanding what the code is supposed to do.

**Why it is harmful**: Checklists catch known vulnerability patterns. Attackers exploit the gaps between checklist items. Business logic vulnerabilities, which are often the most damaging, are invisible to checklist-based review.

**Trainer response**: Present challenges where the vulnerability IS the business logic. An endpoint that correctly sanitizes all inputs but allows any authenticated user to modify any other user's data. A payment flow that validates amounts but not currency, allowing arbitrage. Force the user to understand what the code does, not just how it handles inputs.

### Severity Inflation

**Behavior**: Everything is "critical." A missing Content-Security-Policy header is rated the same as a SQL injection that exposes the entire database.

**Why it is harmful**: When everything is critical, nothing is critical. Development teams triage by severity. If a security reviewer marks 20 items as critical, the team either ignores all of them or wastes time on the wrong ones.

**Trainer response**: Score severity accuracy separately. Show CVSS-aligned reasoning: "A reflected XSS that requires user interaction and is mitigated by CSP headers is medium at most. A SQL injection in an unauthenticated endpoint that returns query results directly is critical. The difference is exploitability, scope, and impact."

### Ignoring Business Context

**Behavior**: The user reviews code in isolation without considering what the application does, who uses it, or what data it processes. They apply the same standards to an internal admin tool and a public-facing payment API.

**Why it is harmful**: Security is contextual. A read-only internal dashboard with SSO has a different threat model than a public API handling financial transactions. Applying maximum paranoia everywhere wastes effort; applying minimum paranoia everywhere creates breaches.

**Trainer response**: Vary the threat context across challenges. Present the same vulnerability pattern in two different contexts and discuss why it is critical in one and medium in the other.

### Tool Dependency

**Behavior**: The user only finds vulnerabilities that automated scanners would find. They catch injection and XSS patterns but miss logic flaws, authorization bugs, race conditions, and trust boundary violations.

**Why it is harmful**: Automated tools are necessary but insufficient. They find pattern-matching vulnerabilities (known-bad function calls, tainted data flows). They miss semantic vulnerabilities that require understanding intent. The most damaging real-world breaches exploit logic that no tool flags.

**Trainer response**: At Level 3+, plant vulnerabilities that static analysis tools cannot find. IDOR through business logic, race conditions in stateful operations, authorization bypass through indirect object references. Score and discuss: "A SAST tool would have found 1 of the 4 vulnerabilities here. The other 3 require human reasoning."

### Missing Logical Vulnerabilities

**Behavior**: The user traces data flow for injection but does not reason about what the code is supposed to do vs what it actually does. They miss: operations that should be atomic but are not, checks that should be present but are absent, states that should be unreachable but are not.

**Why it is harmful**: Logical vulnerabilities are where the highest-impact breaches live. "The code does exactly what it is written to do, but what it is written to do is insecure" is a class of bug that requires understanding intent, not just mechanics.

**Trainer response**: Present code where the vulnerability is not in how something is implemented but in what is missing. An endpoint with no rate limiting on password reset. A file upload that validates type but not destination. A privilege check on read but not on write.


## Error Recovery

### User Finds Nothing (Challenge Too Hard)

**Signals**: "I don't see any issues," "This code looks fine to me," submitting zero findings.

**Trainer approach**:
- Do NOT immediately reveal vulnerabilities. First ask: "Walk me through how you reviewed this code. What did you look at first? What trust assumptions did you identify?"
- If still stuck, offer one structural prompt: "Consider who calls this function and what they control."
- If still stuck, reveal ONE vulnerability (the most instructive one) and discuss the review habit that would have found it. Then ask: "Knowing this, do you want to look again before I reveal the rest?"
- Reduce difficulty next round without announcing it.
- In reflection, focus on building a review starting framework rather than lamenting the miss: "Start by identifying all inputs. Then trace each input to where it is used. Then ask: what happens if this input is not what the code expects?"

### User Finds Everything Plus False Positives (Too Easy or Imprecise)

**Signals**: User finds all planted vulnerabilities but also flags 5+ items that are not actual vulnerabilities. High recall, low precision.

**Trainer approach**:
- Acknowledge the strong recall: "You found all [N] planted vulnerabilities. Your detection instinct is working."
- Focus scoring discussion on precision: "However, [M] of your [total] findings were false positives. In a real review, this means [M] items that a developer investigates and finds to be non-issues. That erodes trust in security feedback."
- For each false positive, explain why the code is safe. This is a teaching moment about defense patterns: "You flagged this as SQL injection, but the code uses parameterized queries. The variable name `query` made it look like string concatenation, but trace the actual execution: the parameter is bound, not interpolated."
- If recall is consistently 100%, increase difficulty.
- If false positive rate is consistently above 30%, present challenges with more false positive traps and fewer actual vulnerabilities.

### User Is Frustrated by Repeated Misses

**Signals**: Self-deprecating comments, wanting to quit, expressing that security review "is not for me."

**Trainer approach**:
- Normalize the difficulty: "Security review is genuinely hard. Professional security reviewers miss vulnerabilities in real audits. The difference between a strong reviewer and a weak one is not that the strong one finds everything -- it is that the strong one has systematic habits that maximize coverage."
- Highlight genuine progress, however small: "In Round 1, you found 0 of 3 injection patterns. In Round 3, you found 2 of 3. That is real improvement in a specific, measurable skill."
- Reduce difficulty and narrow focus: "Let us try a round focused exclusively on injection vulnerabilities. Master one category, then expand."
- Reframe the goal: "A working security reviewer with 60% recall who reviews every PR catches more vulnerabilities than a perfect reviewer who only reviews occasionally. Consistency beats perfection."


## Integration

### Cross-Skill References

This skill connects to other coaching and practice skills in the toolkit:

- **code-review-coach** -- Security review is a specialization of code review. Code-review-coach covers five categories (security, correctness, performance, maintainability, style) with equal weight. Security-review-trainer goes deep on the security category alone, with OWASP-aligned taxonomy, exploit scenario analysis, and security-specific scoring. Users who complete code-review-coach foundations and want to sharpen their security detection should progress here.

- **pr-feedback-writer** -- Finding a vulnerability is necessary but not sufficient. Communicating it effectively to a developer who needs to fix it is a separate skill. Use pr-feedback-writer to practice writing security findings as constructive, actionable PR comments that developers will actually read and act on. Security findings written as "this is vulnerable, fix it" get ignored; findings written with context, impact, and a suggested fix get merged.

- **architecture-review** -- Security-review-trainer operates at the code level (functions, endpoints, data flows within a service). Architecture-review operates at the system level (service boundaries, trust zones, data flow between components). Level 5 challenges in this skill touch on architectural security, but architecture-review provides the comprehensive framework for reasoning about system-level security properties.

### Suggested Skill Sequences

**For building security review capability from scratch:**
1. `code-review-coach` at beginner/intermediate (build general review habits)
2. `security-review-trainer` at Level 1-3 (develop security-specific detection)
3. `security-review-trainer` at Level 4-5 (advance to subtle and architectural vulnerabilities)
4. `pr-feedback-writer` (learn to communicate findings effectively)

**For experienced developers adding security skills:**
1. `security-review-trainer` at Level 2 (establish baseline)
2. `security-review-trainer` at Level 3-5 (progress based on demonstrated ability)
3. `architecture-review` (extend security thinking to system design)


## Stack-Specific Guidance

Security challenges can be presented in any language. The following references provide vulnerability-specific and progression-specific guidance:

- [Vulnerability Catalog](references/vulnerability-catalog.md) -- OWASP Top 10 categories with code-level examples at each difficulty level, common false positive patterns, and vulnerability interaction patterns
- [Difficulty Progression](references/difficulty-progression.md) -- Detailed criteria for each difficulty level, progression logic, challenge construction guidelines, and the calibration framework for advancing or retreating across levels
