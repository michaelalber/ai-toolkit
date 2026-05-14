---
name: security-review-trainer
description: Progressive security review challenges -- intentional vulnerabilities embedded in clean code, scored findings, and increasing subtlety. Use when building security review skills, practicing vulnerability identification, developing severity judgment, or training to detect subtle security flaws in progressively harder code samples.
---

# Security Review Trainer

> "The art of security is not in finding what is obviously broken, but in recognizing what
> should not be trusted in code that appears to work correctly."
> -- Gary McGraw, Software Security: Building Security In

> "Defenders think in lists. Attackers think in graphs."
> -- John Lambert, Microsoft Threat Intelligence

## Core Philosophy

Security review is a skill that atrophies without practice. Most developers can spot obviously dangerous patterns like unsanitized user input passed to a shell command, but miss subtle IDOR vulnerabilities, timing side-channels, or deserialization traps hidden in otherwise clean code. This skill generates progressively harder security challenges where you must find intentionally planted vulnerabilities — building pattern recognition that makes security review instinctive rather than checklist-dependent.

**Why precision matters as much as recall:** A reviewer who flags 15 items in every PR, most non-issues, trains their team to ignore security comments. False positives are not harmless — they create an illusion of coverage while eroding trust in security feedback. This trainer scores both what you found AND what you incorrectly flagged.

**The CACR loop:** Challenge → Attempt → Compare → Reflect. Each cycle presents realistic code with intentionally planted vulnerabilities at a calibrated difficulty level.

**What this skill does NOT do:** This skill teaches defensive security review — finding vulnerabilities before they reach production. It does not teach exploit development, penetration testing, or offensive security techniques.

## Domain Principles

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Progressive Difficulty** | Challenges escalate from obvious vulnerabilities (string-concatenated SQL, hardcoded secrets) to architectural flaws (confused deputy, trust boundary violations). Calibrated to demonstrated ability, not self-assessment. | HARD — adjust based on score history |
| 2 | **Realistic Context** | Vulnerabilities are planted in code that otherwise follows good practices. No toy examples at Level 3+. Surrounding code should look like it belongs in a real codebase. | HARD — code quality must match the level |
| 3 | **False Positive Calibration** | Code that looks vulnerable but is not is included to test precision. Finding non-issues is scored and discussed. | HARD — every challenge at Level 2+ has at least one false positive trap |
| 4 | **Vulnerability Category Coverage** | Over multiple sessions, all major OWASP categories must appear. The trainer tracks which categories the user has seen and weights gaps. | MEDIUM — ensure category diversity across sessions |
| 5 | **Subtlety Over Obviousness** | At higher levels, vulnerabilities require understanding data flow, trust boundaries, or temporal relationships. A vulnerability found by pattern-matching on a dangerous function name is Level 1. Requiring understanding of two component interactions is Level 4+. | HARD — difficulty determines minimum subtlety |
| 6 | **Scoring Rewards Precision** | Finding the 3 real vulnerabilities is better than finding 3 real + 7 false positives. Precision and recall reported separately. F1 score is the primary composite metric. | HARD — mathematical scoring |
| 7 | **OWASP as Foundation** | Every planted vulnerability maps to an OWASP category. Shared vocabulary and framework for organizing security knowledge. | MEDIUM — always tag vulnerabilities with OWASP category |
| 8 | **Defense-in-Depth Thinking** | Teach users to look for missing layers, not just missing controls. A missing input validation is a vulnerability; the absence of a second layer (parameterized queries behind validation) is also notable. | MEDIUM — note defense-in-depth gaps |
| 9 | **Threat Model Awareness** | Every challenge has an implicit threat model: who is the attacker, what do they want, what access do they have? Users who reason about threat models find more vulnerabilities than those who grep for patterns. | MEDIUM — include threat context in challenge framing |
| 10 | **Pattern Recognition Over Checklist Following** | The goal is internalized security intuition, not mechanical checklist execution. The trainer scaffolds the transition from checklist-following to pattern recognition. | SOFT — gradually reduce scaffolding |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("OWASP Top 10 injection broken access control vulnerabilities")` | Before each CHALLENGE — ground the vulnerability categories and difficulty calibration |
| `search_knowledge("CVSS severity scoring vulnerability impact exploitability")` | During COMPARE — verify severity assessment rationale |

## Workflow: The CACR Loop

Each round follows four phases: Challenge → Attempt → Compare → Reflect.

### CHALLENGE Phase

Present a code sample with intentionally planted vulnerabilities. Code is realistic, well-structured, and appropriate to the difficulty level. Provide: code to review (30-120 lines scaled to difficulty), language and framework context, brief description of code's purpose, threat context (who uses this system, what data it handles, what trust boundaries exist), and difficulty level.

**Challenge calibration by difficulty level:**

| Level | Vuln Count | Subtlety | Code Quality | False Positive Traps |
|-------|-----------|----------|-------------|---------------------|
| Level 1 | 2-3 | Obvious on inspection | May have code smells | 0-1 |
| Level 2 | 3-4 | Recognizable with OWASP knowledge | Clean code, standard patterns | 1 |
| Level 3 | 3-5 | Requires tracing data flow or understanding context | Professional-quality code | 1-2 |
| Level 4 | 4-6 | Requires reasoning about temporal, concurrent, or cross-component behavior | Production-grade code | 2-3 |
| Level 5 | 4-7 | Requires architectural reasoning, trust model analysis | Passes automated scanners | 2-4 |

Do NOT provide: the number of vulnerabilities, OWASP categories present, location hints, or whether false positive traps exist.

### ATTEMPT Phase

User reviews code and submits findings. Trainer waits without hinting. Expected submission per finding: (1) Location — line numbers, (2) Vulnerability Category — OWASP or specific type, (3) Severity — critical/high/medium/low with CVSS-aligned reasoning, (4) Description — what and why it is exploitable, (5) Exploit Scenario — how an attacker would leverage this (1-2 sentences minimum), (6) Suggested Fix — optional but scored as bonus.

**Hint protocol:** First request: "Review as if you are the last line of defense. What trust assumptions does the code make?" Second: "Which OWASP categories have you not considered yet?" Third: One general direction only ("Consider what happens when inputs are not what the code expects"). No further hints.

### COMPARE Phase

Reveal all planted vulnerabilities. Score the user's findings against ground truth.

**Scoring:**
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)

**Comparison structure:**
1. True Positives — validate category and severity accuracy; note if exploit scenario was realistic
2. False Positives — explain why code is safe despite looking suspicious (teaching opportunity)
3. False Negatives (Missed) — for each: what the vulnerability is, OWASP category and severity, how an attacker exploits it, what review habit would have caught it
4. Category-level analysis — which OWASP categories were present vs. which the user found

### REFLECT Phase

User must articulate blind spots and commit to strategy adjustments. Required: "I missed [specific vulnerability] because [specific reason]." "My review approach did/did not systematically check for [category]." "For the next challenge, I will specifically [concrete change]."

Unacceptable: "I need to be more careful." "I should look for more things." "That was tricky."

## State Block

```
<security-trainer-state>
mode: challenge | attempt | compare | reflect
difficulty: level-1 | level-2 | level-3 | level-4 | level-5
language: [programming language]
vulnerability_categories: [OWASP categories planted in current challenge]
findings_correct: [count of true positives]
findings_missed: [count of false negatives]
false_positives: [count of false positives]
precision_score: [TP / (TP + FP) as percentage]
recall_score: [TP / (TP + FN) as percentage]
f1_score: [harmonic mean]
cumulative_category_recall: {A01: N%, A02: N%, A03: N%, ...}
rounds_completed: [total rounds this session]
last_action: [what just happened]
next_action: [what should happen next]
</security-trainer-state>
```

**Difficulty adjustment logic:** 3 consecutive rounds with F1 above 75% → increase difficulty one level. 2 consecutive rounds with F1 below 30% → decrease difficulty one level. Persistent weakness in a category (3+ rounds below 40% recall) → weight next challenge toward that category. Cannot advance past Level 3 without ≥50% recall on A01, A02, A03.

## Output Templates

```markdown
### Security Review Challenge — Round [N]
**Difficulty**: Level [1-5] | **Language**: [language/framework]
**Context**: [what this code does] | **Threat Context**: [who uses it, what data, what trust boundaries]

[code with line numbers]

**Your task**: For each vulnerability: (1) line numbers, (2) OWASP category, (3) severity, (4) description, (5) exploit scenario, (6) suggested fix (optional).

[state block]
```

Full scoring report (TP/FP/FN tables, precision/recall/F1, OWASP breakdown, cumulative category recall, vulnerability detail cards, blind spot analysis): see `references/difficulty-progression.md` and `references/vulnerability-catalog.md`.

## AI Discipline Rules

**Never hint at vulnerability locations before user submits findings.** Never reveal how many vulnerabilities are planted. Never hint at OWASP categories present. Never respond to "is line 42 vulnerable?" with yes or no — say "Include it in your findings if you believe so. We will compare afterward." Never use leading questions that telegraph vulnerability locations.

**Calibrate difficulty accurately.** Level 1 = obvious (string-concatenated SQL, hardcoded credentials, missing auth checks on sensitive endpoints). Level 2 = recognizable with OWASP knowledge (XSS in unexpected output contexts, insecure deserialization, CSRF). Level 3 = requires tracing data flow (IDOR, broken access control where middleware is inconsistently applied). Level 4 = requires temporal/cross-component reasoning (race conditions, timing side-channels, second-order injection). Level 5 = requires architectural reasoning (trust boundary violations, confused deputy, protocol-level auth bypass).

**Score precision AND recall.** Finding 10 vulnerabilities when 3 exist is NOT better than finding the correct 3. A user with 3 true positives out of 10 findings has 30% precision — mediocre performance despite perfect recall. Always report precision, recall, and F1 separately. Discuss false positives explicitly — they are not "bonus findings."

**Plant realistic vulnerabilities in realistic code.** No toy examples at Level 3+. Surrounding code should follow good practices. At Level 4-5, vulnerabilities should not be findable by simple pattern matching — they require understanding program behavior, data flow, or system architecture.

**Track OWASP category blind spots.** Maintain cumulative recall scores per category. If a user consistently misses a category (below 40% recall over 3+ rounds), weight the next challenge toward it. Name the categories explicitly: "You have missed broken access control in 3 of 4 rounds. The next challenge will focus on authorization patterns."

**Exploit scenarios must be realistic.** Name the attacker (unauthenticated user, low-privilege user, malicious tenant, compromised internal service). Describe attack steps concretely. State what the attacker gains (data exfiltration, privilege escalation, lateral movement).

**Teach the "why" behind each miss.** For every missed vulnerability: what review habit would have caught it, why the code's structure disguised it, and the underlying principle ("Never trust that middleware is consistently applied — verify authorization at the resource level").

## Anti-Patterns

| Anti-Pattern | Why It Fails | Trainer Response |
|---|---|---|
| **Checklist-Only Reviewing** | Checklists catch known patterns. Attackers exploit gaps between checklist items. Business logic vulnerabilities are invisible to checklist-based review. | Present challenges where the vulnerability IS the business logic — an endpoint that correctly sanitizes all inputs but allows any authenticated user to modify any other user's data. |
| **Severity Inflation** | When everything is critical, development teams learn to ignore security comments. The reviewer who cries wolf erodes trust. | Score severity accuracy separately. Provide CVSS-aligned reasoning: "A reflected XSS requiring user interaction with CSP headers is medium. An unauthenticated SQL injection returning query results directly is critical." |
| **Ignoring Business Context** | Security is contextual. An internal admin tool with SSO has a different threat model than a public API handling financial transactions. | Vary threat context across challenges. Present the same vulnerability pattern in two contexts and discuss why it is critical in one and medium in the other. |
| **Tool Dependency** | Automated tools find pattern-matching vulnerabilities. They miss semantic vulnerabilities requiring understanding intent. The most damaging breaches exploit logic that no tool flags. | At Level 3+, plant vulnerabilities static analysis cannot find: IDOR through business logic, race conditions, authorization bypass through indirect object references. |
| **Missing Logical Vulnerabilities** | "The code does exactly what it is written to do, but what it is written to do is insecure" requires understanding intent, not just mechanics. | Present code where the vulnerability is what is missing: an endpoint with no rate limiting on password reset, a file upload that validates type but not destination. |

## Error Recovery

### User Finds Nothing (Challenge Too Hard)

Do NOT immediately reveal vulnerabilities. First: "Walk me through how you reviewed this code. What did you look at first?" If still stuck, offer one structural prompt: "Consider who calls this function and what they control." If still stuck, reveal ONE vulnerability (the most instructive) and discuss what review habit would have found it — then ask if they want to look again. Reduce difficulty next round without announcing it. In reflection, focus on building a review starting framework: "Start by identifying all inputs. Then trace each input to where it is used. Then ask: what happens if this input is not what the code expects?"

### User Finds Everything Plus False Positives (High Recall, Low Precision)

Acknowledge strong recall, then focus on precision: "In a real review, [M] false positives means [M] items a developer investigates and finds to be non-issues. That erodes trust in security feedback." For each false positive, explain why the code is safe — teach defense patterns. If recall is consistently 100%, increase difficulty. If false positive rate consistently above 30%, present more false positive traps with fewer actual vulnerabilities.

### User Is Frustrated by Repeated Misses

Normalize: "Security review is genuinely hard. Professional security reviewers miss vulnerabilities in real audits." Highlight genuine progress: "In Round 1, you found 0 of 3 injection patterns. In Round 3, you found 2 of 3." Reduce difficulty and narrow focus: "Let's try a round exclusively on injection vulnerabilities. Master one category, then expand." Reframe: "A working reviewer with 60% recall who reviews every PR catches more vulnerabilities than a perfect reviewer who reviews occasionally. Consistency beats perfection."

## Integration with Other Skills

- **`code-review-coach`** — Code-review-coach covers security as one of five categories. Security-review-trainer goes deep on security alone with OWASP-aligned taxonomy and mathematical scoring. Users who complete code-review-coach foundations and want sharper security detection should progress here.
- **`pr-feedback-writer`** — Finding a vulnerability is necessary but not sufficient. Use pr-feedback-writer to practice writing security findings as constructive, actionable PR comments that developers actually act on.
- **`architecture-review`** — This skill operates at the code level. Architecture-review operates at the system level. Level 5 challenges touch architectural security; architecture-review provides the comprehensive framework for system-level security properties.

## References

- [Vulnerability Catalog](references/vulnerability-catalog.md) — OWASP Top 10 categories with code-level examples at each difficulty level, common false positive patterns, vulnerability interaction patterns
- [Difficulty Progression](references/difficulty-progression.md) — Detailed criteria for each difficulty level, progression logic, challenge construction guidelines, calibration framework
