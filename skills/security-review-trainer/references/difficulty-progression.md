# Difficulty Progression

Reference for calibrating challenge difficulty, determining when to advance or retreat,
and constructing challenge code at each level. This document defines the five difficulty
levels and the criteria for moving between them.

---

## Level Definitions

### Level 1: Obvious Vulnerabilities

**Target audience**: Developers new to security review or establishing a baseline.

**Vulnerability characteristics**:
- Findable by pattern recognition on well-known dangerous patterns
- Single-location vulnerabilities (the entire vulnerability is visible in one place)
- No surrounding code complexity to obscure the issue
- Standard examples from OWASP documentation

**Typical vulnerability types**:
- SQL queries built with string concatenation and user input
- Hardcoded credentials (API keys, passwords as string literals)
- Missing authentication on sensitive endpoints (no auth middleware, no token check)
- Password storage with fast/broken hash functions (MD5, SHA-1, plaintext)
- No input validation on user-facing endpoints
- Debug mode enabled in configuration
- No password complexity requirements

**Code construction**:
- 30-50 lines per challenge
- Code may have general quality issues (this is not a code quality exercise at Level 1)
- Vulnerabilities are directly visible without tracing data flow
- 2-3 vulnerabilities per challenge
- 0-1 false positive traps

**What success looks like**:
- Finding all planted vulnerabilities within 5-10 minutes
- Correctly categorizing them by OWASP category
- Reasonable severity assignments (within one level of correct)

---

### Level 2: Standard Vulnerabilities

**Target audience**: Developers with basic OWASP knowledge who can spot the obvious
and need to build breadth.

**Vulnerability characteristics**:
- Recognizable with solid OWASP knowledge but not immediately obvious
- May require understanding context (output context for XSS, data source for CSRF)
- The vulnerable pattern exists but is not the textbook example

**Typical vulnerability types**:
- XSS in non-obvious output contexts (JavaScript context, attribute context, URL context)
- Insecure deserialization of untrusted data
- CSRF on state-changing operations without token validation
- Weak cryptographic choices (ECB mode, static IVs, short key lengths)
- Overly permissive CORS configuration
- Session tokens not invalidated on logout
- Direct SSRF in webhook/URL preview features
- Security questions as account recovery

**Code construction**:
- 40-70 lines per challenge
- Clean code with proper naming and structure
- Vulnerabilities require reading more than one line to understand
- 3-4 vulnerabilities per challenge
- 1 false positive trap (code that looks suspicious but is safe)

**What success looks like**:
- Finding 70%+ of planted vulnerabilities
- Distinguishing the false positive trap from real vulnerabilities
- Providing plausible exploit scenarios for findings

---

### Level 3: Context-Dependent Vulnerabilities

**Target audience**: Developers who can find standard vulnerability patterns and need
to develop contextual reasoning.

**Vulnerability characteristics**:
- Require understanding what the code is supposed to do, not just how it works
- Data flow tracing across multiple functions or methods
- Authorization logic that is present but insufficient
- Configuration or initialization issues separate from runtime code
- Business logic flaws that are technically correct but semantically insecure

**Typical vulnerability types**:
- IDOR through predictable identifiers (sequential IDs, guessable UUIDs)
- Broken access control where middleware is inconsistently applied across routes
- Insecure defaults in framework or library configuration
- Mass assignment / over-posting through unfiltered object binding
- Username enumeration through differential error responses or timing
- Missing re-authentication for sensitive operations
- ORM injection through raw query fragments in otherwise safe ORM code
- Authentication failures not logged with sufficient detail
- Default credentials in initialization code

**Code construction**:
- 50-90 lines per challenge
- Professional-quality code with proper error handling and naming
- The vulnerable code path is not the "main" path -- it may be in error handling,
  edge cases, or secondary operations
- Surrounding code uses secure patterns, creating a false sense of safety
- 3-5 vulnerabilities per challenge
- 1-2 false positive traps

**What success looks like**:
- Finding 60%+ of planted vulnerabilities
- Correctly identifying IDOR and access control issues (not just injection)
- Articulating why the context makes a pattern vulnerable (not just naming the pattern)
- Keeping false positive rate below 25%

**Advancement gate**: Users cannot advance past Level 3 without demonstrating at least
50% recall on injection (A03), broken access control (A01), and cryptographic failures
(A02) individually.

---

### Level 4: Subtle Vulnerabilities

**Target audience**: Developers with strong security fundamentals who need to develop
intuition for temporal, concurrent, and cross-component vulnerabilities.

**Vulnerability characteristics**:
- Require reasoning about behavior over time, not just static code structure
- Concurrency, race conditions, and state management issues
- Vulnerabilities that span multiple code paths or components
- Side-channel attacks (timing, error-based information leakage)
- Second-order effects (stored data used unsafely in a different context)
- Vulnerability interaction patterns (two low-severity issues that combine)

**Typical vulnerability types**:
- Race conditions in token validation or financial operations
- Timing side-channels in authentication or comparison operations
- Second-order injection through stored-then-retrieved data
- SSRF through redirect chains that bypass URL validation
- JWT algorithm confusion attacks
- Horizontal privilege escalation through batch operations
- Sensitive data leakage through application logs
- XXE through dangerous parser defaults
- CI/CD pipeline security boundary violations

**Code construction**:
- 60-100 lines per challenge
- Production-grade code quality
- Multiple functions or classes that interact
- The vulnerability emerges from the interaction between components, not from any
  single line
- At least one vulnerability should be unfindable by static analysis tools
- 4-6 vulnerabilities per challenge
- 2-3 false positive traps (including code that uses secure-by-design patterns)

**What success looks like**:
- Finding 50%+ of planted vulnerabilities
- Identifying at least one temporal or cross-component vulnerability
- Describing exploit scenarios that account for timing or state
- Recognizing vulnerability interaction patterns

---

### Level 5: Architectural Vulnerabilities

**Target audience**: Senior developers and security-focused engineers who need to
reason about system-level security properties.

**Vulnerability characteristics**:
- Require understanding trust boundaries between system components
- The vulnerability is in the design, not just the implementation
- Protocol-level misunderstandings or specification ambiguities
- Supply chain and dependency-related attack vectors
- Emergent vulnerabilities from the composition of individually safe components
- Vulnerabilities that no automated tool would flag

**Typical vulnerability types**:
- Trust boundary violations between microservices (confused deputy)
- OAuth/OIDC implementation flaws (missing state parameter, token confusion)
- Supply chain attacks through dependency confusion or typosquatting
- SSRF through rendering pipelines (PDF generation, email templating)
- Insufficient entropy in security-critical random value generation
- Implicit trust assumptions between infrastructure components
- Authentication bypass through protocol-level misunderstanding
- Cloud storage misconfiguration spanning infrastructure and application code
- Template injection through user-customizable content systems

**Code construction**:
- 80-120 lines per challenge
- May include snippets from multiple services or configuration files
- Code passes automated security scanners without findings
- The vulnerability requires understanding the system context, not just the code
- May require reading infrastructure-as-code alongside application code
- 4-7 vulnerabilities per challenge
- 2-4 false positive traps (including patterns that appear dangerous due to
  unfamiliar but secure library usage)

**What success looks like**:
- Finding 40%+ of planted vulnerabilities (Level 5 is genuinely hard)
- Identifying at least one architectural or trust boundary vulnerability
- Articulating the trust model and where it breaks down
- Reasoning about what an attacker with different levels of access could achieve

---

## Progression Criteria

### When to Advance

A user advances to the next difficulty level when ALL of the following are met:

1. **F1 score above 75% for 3 consecutive rounds** at the current level
2. **Precision above 60%** (not just high recall through shotgun reviewing)
3. **At least one finding per round includes a plausible exploit scenario**
4. **Category diversity**: the user has demonstrated recall across at least 3 different
   OWASP categories at the current level

For advancing past Level 3 specifically, an additional gate applies:
- At least 50% individual recall on A01 (Broken Access Control), A02 (Cryptographic
  Failures), and A03 (Injection). These three categories represent the foundation
  of security review competence.

### When to Stay at Current Level

A user stays at their current level when:

1. F1 score is between 40% and 75% -- still learning at this level
2. The user shows strength in some categories but weakness in others --
   targeted challenges within the current level address the gaps
3. False positive rate is above 30% -- precision needs work before adding
   more complex challenges

### When to Decrease Difficulty

A user drops to the previous level when:

1. **F1 score below 30% for 2 consecutive rounds** -- the current level is too hard
2. **Recall below 20% for 2 consecutive rounds** -- the user is not finding vulnerabilities
3. **User expresses frustration** -- the trainer should reduce difficulty silently
   (without announcing the reduction) and narrow the vulnerability category focus

When decreasing difficulty:
- Do NOT announce the decrease ("I am making this easier for you")
- DO narrow the focus: "The next challenge focuses on injection patterns"
- DO acknowledge the difficulty: "Level [N] challenges are genuinely hard. Let us
  strengthen your foundation on [specific category]"

### Category-Weighted Progression

Independent of overall difficulty level, the trainer tracks per-category recall:

- If a specific OWASP category has below 40% recall over 3+ rounds, the next
  challenge should include at least one vulnerability from that category
- If a category has above 80% recall over 3+ rounds, reduce its frequency to
  make room for weaker categories
- Report category trends in every comparison phase so the user sees their
  own pattern

---

## Challenge Construction Guidelines

### General Principles

1. **Realistic code first, vulnerabilities second.** Write the code as if it were real,
   then introduce vulnerabilities by modifying specific lines or omitting specific
   checks. Do not write "vulnerable code" from scratch -- it never looks real.

2. **Match code quality to level.** Level 1 code may have general quality issues.
   Level 3+ code should be clean, well-named, and properly structured. The challenge
   is finding the security issue, not reading messy code.

3. **Provide sufficient context.** The code snippet must include enough surrounding
   context for a reviewer to understand the data flow. A bare function without knowing
   what calls it or where its parameters come from is unfair.

4. **Vary the language and framework.** Over a session, present challenges in different
   languages and frameworks. Security patterns are language-independent, but their
   manifestation varies. SQL injection looks different in Java/JDBC vs Python/Django
   vs Node/Sequelize.

5. **Include the threat model.** Every challenge should state who uses the system, what
   data it handles, and what trust boundaries exist. Without this, the user cannot
   reason about severity or exploitation.

### False Positive Trap Construction

False positive traps serve a specific pedagogical purpose: teaching the user to distinguish
genuinely dangerous code from code that merely looks dangerous.

**Effective traps:**
- Parameterized queries with variable names that suggest concatenation
- Public endpoints that are intentionally unauthenticated (health checks, public APIs)
- Constant-time comparison functions that look like simple equality
- Properly encoded output in the correct context
- Internal-only HTTP calls where the network context makes TLS unnecessary

**Ineffective traps (do not use):**
- Commented-out vulnerable code (not a real review scenario)
- Dead code that is never executed (not a real security concern)
- Code with obvious bugs that are not security-relevant (distracts from security focus)

### Level-Specific Construction Notes

**Level 1-2**: The vulnerability should be identifiable from the code alone without
needing external knowledge about libraries, frameworks, or deployment context. If the
user knows OWASP Top 10, they should be able to find it.

**Level 3**: The vulnerability requires understanding the code's purpose. Present
enough context (route definitions, middleware configuration, data model) for the user
to reason about authorization and data flow.

**Level 4**: The vulnerability requires reasoning about behavior over time or across
components. Present code that interacts with shared state, external services, or
concurrent operations. The vulnerability may only manifest under specific conditions
(concurrent requests, specific input sequences).

**Level 5**: The vulnerability requires understanding the system architecture. Present
code from multiple services or layers (application code + infrastructure configuration,
gateway code + backend service code, template engine + rendering pipeline). The
vulnerability is in the composition, not in any single component.

---

## Scoring Reference

### F1 Score Interpretation

| F1 Range | Interpretation | Action |
|----------|---------------|--------|
| 90-100% | Expert-level performance at this difficulty | Advance to next level |
| 75-89% | Strong performance, ready for advancement | Advance if consistent (3 rounds) |
| 50-74% | Developing competence, continue at this level | Stay, target weak categories |
| 30-49% | Struggling, may need more focused practice | Stay, narrow category focus |
| 0-29% | Level is too hard, or review approach needs restructuring | Decrease level or focus on single category |

### Precision vs Recall Imbalance

| Pattern | Diagnosis | Coaching Focus |
|---------|-----------|----------------|
| High recall, low precision | Shotgun reviewing: flagging everything suspicious | Teach false positive recognition, require confidence before flagging |
| Low recall, high precision | Conservative reviewing: only flagging certainties | Expand the categories checked, teach "suspicious until proven safe" |
| Both low | Fundamental gap in security knowledge | Decrease difficulty, focus on one OWASP category at a time |
| Both high | Strong reviewer at this level | Advance difficulty |
