# Deliberate Practice for Code Review

This reference applies Anders Ericsson's deliberate practice framework to the specific skill of code review. It defines practice structure, progression, cadence, tracking, and strategies for breaking through common plateaus.


## Ericsson's Deliberate Practice Principles Applied to Code Review

Anders Ericsson's research on expertise identifies four requirements for deliberate practice. Each applies directly to code review skill development.

### 1. Well-Defined, Specific Goals

General goal: "Get better at code review" -- useless.
Deliberate practice goal: "Improve my security issue detection rate from 30% to 60% over the next 10 sessions by systematically tracing user input through every function I review."

Each practice session must target a specific, measurable aspect of review skill:
- Detection rate in a specific category (security, correctness, performance)
- Severity calibration accuracy
- False positive reduction
- Time-to-first-finding for a new code snippet
- Comment quality (constructive, actionable, specific)

### 2. Focused Attention Beyond Current Ability

Practice at the edge of your competence. If you consistently score above 80% on beginner challenges, you are not practicing -- you are performing. Deliberate practice is uncomfortable because it operates in the zone where you fail frequently enough to learn.

For code review, this means:
- Reviewing code in languages you are less familiar with (forces focus on logic over syntax)
- Reviewing code in domains outside your expertise (forces explicit reasoning about assumptions)
- Reviewing code with issues that require multi-step reasoning (race conditions, second-order effects)
- Reviewing under time pressure to build pattern recognition speed

### 3. Immediate, Informative Feedback

The CACR loop provides this. The comparison phase delivers feedback while the review reasoning is still in working memory. The critical detail: feedback must be specific enough to act on.

Bad feedback: "You missed some issues."
Good feedback: "You missed the SQL injection on line 14. Your review did not trace the `username` parameter from the HTTP request through to the database query on line 22. The review habit that catches this: for every function, identify all inputs that originate from outside the trust boundary and follow them to every point of use."

### 4. Repetition with Refinement

Volume matters, but only when combined with reflection. Reviewing 100 code snippets without analyzing your misses produces 100 repetitions of your current habits. Reviewing 20 code snippets with detailed reflection on each miss produces genuine skill growth.

The refinement cycle:
1. Review code (attempt)
2. Compare against expert analysis (feedback)
3. Identify the specific gap (reflection)
4. Name the review habit that would close the gap (strategy)
5. Deliberately apply that habit in the next round (practice)
6. Verify whether the habit worked (measurement)


## Practice Session Structure

### Warm-Up (5-10 minutes, 1 round)

**Purpose**: Activate review mindset, calibrate attention.

- Use a beginner-difficulty challenge in a familiar language
- Focus on speed: how quickly can you identify the obvious issues?
- Do not linger on edge cases or subtleties
- Target: 80%+ detection rate with fast turnaround

The warm-up serves the same function as scales for a musician. It is not where learning happens, but it prepares the cognitive machinery for focused work.

### Focused Practice (20-40 minutes, 2-4 rounds)

**Purpose**: Work at the edge of competence in a targeted area.

- Use intermediate or advanced difficulty challenges
- Focus on ONE category weakness per session (e.g., "today I practice security review")
- Take full time on each review -- thoroughness over speed
- After each comparison, write down the specific habit that would have caught what you missed
- Apply that habit explicitly in the next round

**Session focus examples:**
- "Security trace": For every function, identify all external inputs and trace them to every use
- "Error path audit": For every operation that can fail, verify the error handling is correct and complete
- "Concurrency check": For every piece of shared state, verify synchronization and consider interleaving
- "Edge case sweep": For every conditional and loop, consider the boundary values and empty cases

### Cool-Down (5-10 minutes, reflection)

**Purpose**: Consolidate learning, set direction for next session.

- Review your scores across the session
- Identify the single most important thing you learned
- Write a one-sentence review habit to carry forward
- Rate your focus and effort honestly (even perfect practice has off days)

**Cool-down template:**
```
Session date: [date]
Rounds: [N]
Focus area: [category]
Detection rate trend: [round1]% -> [roundN]%
Key learning: [one specific insight]
New habit: [one specific review action to practice]
Next session focus: [what to work on next]
```


## Progression Ladder

### Level 1: Obvious Bugs (Beginner)

**Characteristics of challenges:**
- Single-function code, 15-30 lines
- Issues are syntactically or logically obvious on first read
- One category dominates (usually correctness or style)

**Typical issues at this level:**
- Null pointer dereference with no null check
- Off-by-one error in a simple loop
- Hardcoded password in plain text
- Unused variable or dead code branch
- Division without zero check

**Graduation criteria**: Consistent 75%+ detection rate over 5 rounds.

### Level 2: Common Patterns (Intermediate)

**Characteristics of challenges:**
- Multi-function code, 30-50 lines
- Issues require reading across function boundaries
- Multiple categories present in each challenge

**Typical issues at this level:**
- Resource leak in an error path (file handle, connection)
- N+1 query pattern in a data access function
- Missing input validation on an internal API
- Exception caught too broadly, swallowing important errors
- String concatenation building a SQL query

**Graduation criteria**: Consistent 65%+ detection rate over 5 rounds with at least 70% severity accuracy.

### Level 3: Subtle Logic (Advanced)

**Characteristics of challenges:**
- Class or module-level code, 40-70 lines
- Issues require understanding of state, concurrency, or domain rules
- Interactions between issues (fixing one reveals another)

**Typical issues at this level:**
- Race condition between check and use of a shared resource
- Implicit coupling through shared mutable state
- Floating-point comparison causing intermittent incorrect results
- Error handling that masks the root cause of failures
- Cache invalidation logic with a subtle timing window

**Graduation criteria**: Consistent 55%+ detection rate over 5 rounds with coverage across all five categories.

### Level 4: Design and Architecture (Advanced-Expert)

**Characteristics of challenges:**
- Multi-class or multi-module code, 50-80 lines
- Issues are about design decisions, not just implementation
- Some issues are debatable (reasonable people might disagree)

**Typical issues at this level:**
- Abstraction that leaks implementation details across module boundaries
- Feature envy indicating misplaced responsibility
- Primitive Obsession preventing domain model evolution
- Temporal coupling requiring methods to be called in a specific undocumented order
- Missing domain concept that would simplify multiple functions

**Graduation criteria**: Consistent 50%+ detection rate with ability to articulate trade-offs for debatable issues.

### Level 5: Systemic and Adversarial (Expert)

**Characteristics of challenges:**
- Production-grade code, 60-80+ lines
- Issues require reasoning about the system beyond the visible code
- Adversarial inputs, distributed system edge cases, emergent behavior

**Typical issues at this level:**
- Timing side-channel that leaks information about secret values
- Distributed consensus violation under specific network partition scenarios
- Denial-of-service vulnerability through algorithmic complexity attack (e.g., hash collision)
- Subtle memory model violation in lock-free concurrent code
- Security vulnerability that only manifests through a chain of three individually-safe operations

**Graduation criteria**: There is no graduation. Level 5 is where you continue to practice and refine indefinitely. Expert performance is maintained through continued deliberate practice, not achieved and preserved.


## Session Cadence Recommendations

### Building the Habit (First 4 weeks)

- 3 sessions per week, 30 minutes each
- Focus on Levels 1 and 2
- Priority: build the practice habit and the reflection habit
- Do not optimize for score; optimize for consistency

### Developing Skill (Weeks 5-12)

- 2-3 sessions per week, 30-45 minutes each
- Focus on Levels 2 and 3
- Priority: develop category-specific review strategies
- Begin tracking per-category detection rates

### Maintaining and Refining (Ongoing)

- 1-2 sessions per week, 30-45 minutes each
- Focus on Levels 3-5 based on current ability
- Priority: address persistent weaknesses, maintain strengths
- Supplement with real PR reviews where possible (use the same self-scoring approach)

### Minimum Effective Dose

If time is scarce: one 20-minute session per week with 2 focused rounds is enough to prevent skill decay. It is not enough to build new capability, but it preserves existing ability.


## Tracking Improvement Over Time

### What to Track

1. **Detection rate by category** -- The most important metric. Track per-session averages.
2. **Severity accuracy** -- Calibration drift is real. Track whether you consistently over- or under-classify.
3. **False positive rate** -- Should decrease over time as discrimination improves.
4. **Time per review** -- Initially increases as you become more thorough, then decreases as pattern recognition builds.
5. **Difficulty level** -- Track which level you are practicing at. Plateaus at one level followed by breakthrough to the next are the expected pattern.

### What Not to Track

- Absolute score in isolation (a 40% at Level 4 may indicate more skill than 90% at Level 1)
- Score compared to other people (different reviewers have different starting points and different domains)
- Number of sessions without reference to quality of practice (ten distracted sessions teach less than three focused ones)

### Review Journal

Keep a simple log. One line per session is enough:

```
[date] | Level [N] | Focus: [category] | Detection: [N]% | Key learning: [one sentence]
```

Over 20+ sessions, patterns emerge: which categories improve fastest, where plateaus occur, which types of issues remain blind spots.


## Common Plateaus and How to Break Through

### Plateau: "I find the same types of issues every time"

**Cause**: You have developed strong pattern recognition for a subset of issue types and your review defaults to scanning for those patterns.

**Breakthrough strategy**: Single-category sessions. Force yourself to review ONLY for security, ignoring everything else. Then ONLY for performance. This breaks the habit of scanning for familiar patterns and builds new scanning strategies.

### Plateau: "I find issues but mis-classify severity"

**Cause**: Severity calibration requires understanding impact, which requires understanding the system context beyond the code snippet.

**Breakthrough strategy**: Before scoring severity, ask three questions: "Who is affected if this bug ships?", "How often would it trigger?", "What is the blast radius?" Practice writing one-sentence impact statements for each finding before assigning severity.

### Plateau: "I catch everything in small functions but miss things in larger code"

**Cause**: Working memory limits. Larger code requires systematic review strategy, not just reading top-to-bottom.

**Breakthrough strategy**: Adopt a multi-pass review approach. First pass: understand what the code does (no findings yet). Second pass: check inputs, outputs, and error handling. Third pass: check the specific category you are weakest in. This reduces cognitive load per pass.

### Plateau: "My score is stuck at intermediate level"

**Cause**: You have extracted the easy gains and are now facing issues that require deeper reasoning.

**Breakthrough strategy**: Study the issues you miss. Keep a "miss log" -- every issue from the expert analysis that you did not find, with your analysis of why you missed it. After 10-15 entries, patterns will emerge. Those patterns are your specific training targets.

### Plateau: "I take too long and still miss things"

**Cause**: Review strategy is not efficient. You are probably re-reading the same code multiple times without a clear purpose for each pass.

**Breakthrough strategy**: Time-box each review pass. Give yourself 2 minutes for comprehension, 3 minutes for a targeted category scan, 2 minutes for a second category. The constraint forces efficiency and reveals where your time goes. Speed and thoroughness are not opposites -- they are both products of structured approach.

### Plateau: "I find issues but cannot write good review comments"

**Cause**: Detection and communication are separate skills. Finding an issue is pattern recognition; explaining it constructively is technical writing.

**Breakthrough strategy**: For every finding, write it as you would in a real PR comment. Include: what the issue is, why it matters, and a suggested fix. Then compare your comment against the expert analysis phrasing. Use the `pr-feedback-writer` skill for focused practice on the communication side.
