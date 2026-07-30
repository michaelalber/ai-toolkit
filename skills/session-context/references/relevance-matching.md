# Relevance Matching Reference

> "Information is not knowledge. The trick is not finding information -- it is finding the
> information that matters right now, for this task, in this context."
> -- Peter Drucker (paraphrased)

This reference covers techniques for scoring context relevance when building session
briefings. The goal is to include the right context and exclude the noise, so that
every item in a briefing earns its place.

## Context Relevance Scoring Framework

### The Relevance Score

Every piece of context -- a commit group, an ADR, a dependency relationship, a
convention observation -- receives a relevance score from 0 to 100. The score
determines whether the item appears in the briefing and where it is positioned.

| Score Range | Classification | Action |
|------------|---------------|--------|
| 80-100 | Critical relevance | Include in executive summary |
| 60-79 | High relevance | Include in detailed sections |
| 40-59 | Medium relevance | Include if space permits, or mention briefly |
| 20-39 | Low relevance | Omit from briefing, available on request |
| 0-19 | Not relevant | Omit entirely |

### Scoring Dimensions

Each piece of context is scored across four dimensions. The final score is a
weighted combination:

```
Relevance Score = (Proximity * 0.35) + (Recency * 0.25) + (Impact * 0.25) + (Confidence * 0.15)
```

## Dimension 1: File Proximity to Current Task

Proximity measures how close a piece of context is to the focus area in terms
of the project's structure and dependency graph.

### Proximity Levels

| Level | Distance | Score | Example |
|-------|----------|-------|---------|
| Direct | The context IS about a focus area file | 100 | Commit modifying `src/auth/tokens.py` when focus is `src/auth/` |
| Adjacent | Same module or package | 80 | Change to `src/auth/models.py` when focus is `src/auth/tokens.py` |
| One-hop dependency | Focus area imports from or is imported by | 65 | Change to `src/db/session.py` when focus area imports `db.session` |
| Two-hop dependency | Transitive dependency | 40 | Change to `src/config/settings.py` -> used by `db.session` -> used by focus |
| Same project, different area | No dependency path | 15 | Change to `src/billing/` when focus is `src/auth/` |
| Different project / external | Outside the repository | 5 | Update to a third-party library |

### Computing Proximity

```
1. Start with the focus area files as the center (distance = 0)
2. Parse import/dependency statements in focus area files
   -> Mark imported modules as distance = 1
3. Parse imports in distance-1 modules
   -> Mark their imports as distance = 2
4. Stop at distance = 2 (diminishing returns beyond this)
5. Map each piece of context to a file
6. Look up the file's distance from the focus area
7. Convert distance to a proximity score using the table above
```

### Special Proximity Cases

**Cross-cutting files**: Configuration files, shared utilities, and middleware
affect everything. Score them based on whether the focus area actually uses them:

```
If focus area imports from the cross-cutting file: Adjacent (80)
If focus area does not import but is affected at runtime: One-hop (65)
If no clear connection: Same project (15)
```

**Test files**: Test files for the focus area have Direct proximity (100).
Test files for dependencies have One-hop proximity (65). Unrelated test files
get Same project proximity (15).

**Build and CI files**: Changes to build configs that affect the focus area's
build or deployment get Adjacent proximity (80). Changes to unrelated build
targets get Same project (15).

## Dimension 2: Recency Weighting

Recency measures how recently the context was created or last modified. More
recent context is generally more relevant, but recency alone is not sufficient
for inclusion.

### Recency Decay Function

```
Recency Score = max(0, 100 - (days_old * decay_rate))

Where decay_rate depends on context type:
- Commits: decay_rate = 4 (50% at ~12 days, 0% at 25 days)
- ADRs: decay_rate = 0.5 (50% at 100 days, 0% at 200 days)
- Dependencies: decay_rate = 1 (50% at 50 days, 0% at 100 days)
- Conventions: decay_rate = 0.2 (effectively no decay -- conventions are persistent)
```

### Why ADRs Decay Slowly

Architecture decisions have long half-lives. An ADR accepted 6 months ago that
governs the focus area is still highly relevant. The slow decay rate ensures
that ADRs remain in consideration even when they are not recent.

### Recency Overrides

Some context is relevant regardless of age:

```
- ADR with status "Accepted" that governs the focus area -> minimum recency = 60
- Dependency that the focus area directly imports -> minimum recency = 50
- Convention actively enforced by a linter rule -> minimum recency = 70
- Commit that introduced a breaking change to a dependency -> minimum recency = 70
```

## Dimension 3: Impact Assessment

Impact measures how much the context could affect the outcome of the current
session. High-impact context, if ignored, would lead to bugs, wasted effort,
or violations of project decisions.

### Impact Levels

| Level | Score | Criteria | Example |
|-------|-------|----------|---------|
| Critical | 100 | Ignoring this context WILL cause failure | Breaking API change in a dependency |
| High | 80 | Ignoring this context will likely cause problems | ADR constraint that limits implementation choices |
| Medium | 55 | This context improves decisions but is not blocking | Coding convention for the focus area |
| Low | 30 | Nice-to-know context that rarely changes decisions | Author information for changed files |
| Minimal | 10 | Background context with no direct bearing | Project-level activity statistics |

### Impact Heuristics

**Breaking changes**: Any commit that introduces a breaking change to something
the focus area depends on is Critical (100).

```
Detection:
- Commit message contains "BREAKING", "breaking change", or "!"
- Function signature changed in a file imported by the focus area
- Type/interface definition changed that the focus area implements
- Configuration value removed or renamed
```

**ADR constraints**: An active ADR that constrains implementation choices in the
focus area is High (80).

```
Detection:
- ADR mentions the focus area's module or technology by name
- ADR's "Consequences" section lists constraints applicable to the focus area
- ADR's "Decision" section prescribes a pattern the focus area should follow
```

**Hotspot files**: Files with high change frequency that overlap with the focus
area get a Medium (55) impact boost.

```
Detection:
- File changed 3+ times in the time window
- File is in the focus area or one-hop dependency
- Change pattern suggests instability (many bug fixes)
```

## Dimension 4: Confidence Level

Confidence measures how certain we are that the context is accurate and
applicable. High-confidence context comes from direct observation; low-confidence
context comes from inference or incomplete data.

### Confidence Levels

| Level | Score | Source |
|-------|-------|--------|
| Verified | 100 | Read from actual files, git log, or ADR content |
| Computed | 80 | Derived from verified data (e.g., dependency graph from parsed imports) |
| Inferred | 50 | Concluded from patterns but not directly stated (e.g., "appears to be a refactoring campaign") |
| Assumed | 25 | Based on convention or expectation without verification (e.g., "this module probably handles...") |
| Unknown | 0 | Cannot determine accuracy |

### Confidence Rules

1. **Never include context with confidence < 25 in the briefing**
2. **Mark inferred context explicitly**: "Based on commit patterns, this appears to be..."
3. **Prefer verified context over inferred**: If you can verify by reading a file, do so
4. **State when confidence is low**: "Limited confidence: git history is shallow"
5. **Do not boost low-confidence items with high proximity or impact scores**: A high-proximity,
   low-confidence item should still be flagged as uncertain

## ADR Applicability Heuristics

### Matching ADRs to Focus Areas

ADRs govern areas of a codebase even when they do not name specific files.
Use these heuristics to determine applicability:

### Direct Reference Matching

```
1. Parse ADR content for file paths, module names, and class names
2. Check if any referenced entities are in or adjacent to the focus area
3. If YES: Direct match -> Proximity = 100, minimum relevance = 80
```

### Technology Matching

```
1. Extract technologies mentioned in the ADR (database, framework, protocol, language)
2. Check if the focus area uses the same technology
3. If YES: Technology match -> Proximity = 65, relevance depends on other factors

Example:
ADR-0001 decides on PostgreSQL for data storage.
Focus area imports `sqlalchemy` and defines database models.
Match: Technology (PostgreSQL/SQL) -> relevant
```

### Pattern Matching

```
1. Extract architectural patterns mentioned in the ADR (event sourcing, CQRS,
   repository pattern, circuit breaker)
2. Check if the focus area implements or should implement the same pattern
3. If YES: Pattern match -> Proximity = 65

Example:
ADR-0003 decides on the repository pattern for data access.
Focus area contains a class that queries the database directly.
Match: Pattern (repository) -> relevant as a potential violation
```

### Constraint Matching

```
1. Extract constraints from the ADR's "Consequences" and "Decision" sections
2. Check if any constraint applies to the focus area's implementation
3. If YES: Constraint match -> Impact = 80

Example:
ADR-0005 states "All API authentication MUST use OAuth 2.0 JWT tokens."
Focus area is an API endpoint.
Match: Constraint -> the endpoint must use JWT auth
```

### Overdue Review Matching

```
1. Check each relevant ADR's review schedule
2. If a 30/90/180-day review is overdue, flag it
3. Overdue reviews get an impact boost of +20

Rationale: An overdue review means the decision has not been validated
against reality. It may be stale, wrong, or superseded in practice.
```

## Pattern Detection from Recent Changes

### Identifying Emerging Patterns

Recent commits can reveal patterns that are not explicitly documented:

```
1. GROUP commits by area and analyze the change trajectory:
   - Are all changes in one direction? (e.g., adding interfaces -> moving toward abstraction)
   - Are changes following a template? (e.g., each new file has the same structure)
   - Are changes systematic? (e.g., renaming all X to Y across the codebase)

2. COMPARE the focus area with recently changed code:
   - Is the focus area following the same patterns as recent changes?
   - Is the focus area behind on a migration or refactoring effort?
   - Are there new conventions emerging that the focus area does not yet follow?

3. SURFACE detected patterns with evidence:
   - "Recent commits add interfaces to all data access classes (commits abc..def).
     The focus area's OrderRepository does not yet have an interface."
```

### Pattern Types to Detect

| Pattern | Detection Signal | Context Value |
|---------|-----------------|---------------|
| Migration | Systematic renames or replacements across files | High -- focus area may need the same treatment |
| Convention shift | New files follow a different pattern than old files | Medium -- focus area should follow the new convention |
| Dependency update | Multiple modules updating the same dependency | Medium -- focus area may need the same update |
| Error handling change | New try/catch patterns or error types appearing | High -- focus area should use consistent error handling |
| Testing pattern | New test files following a different structure | Medium -- focus area tests should match |
| API versioning | New v2 endpoints appearing alongside v1 | High -- focus area may need version awareness |

## Dependency Path Relevance

### Why Dependency Paths Matter

A change to a transitive dependency can be just as impactful as a change to a
direct dependency, depending on the path. Dependency path analysis helps
prioritize which dependency changes to surface.

### Path Analysis Protocol

```
1. Build the dependency graph from the focus area outward (2 hops)
2. For each changed file in the time window:
   a. Find the shortest path from the focus area to the changed file
   b. If no path exists: irrelevant (unless it is a new dependency)
   c. If path length = 0: direct change to focus area (Critical)
   d. If path length = 1: direct dependency change (High)
   e. If path length = 2: transitive dependency change (Medium if volatile)
3. For each path, assess the coupling type:
   a. Interface/contract dependency: changes to the interface affect all implementers
   b. Data type dependency: changes to shared types propagate widely
   c. Utility dependency: changes are usually additive and low-risk
   d. Configuration dependency: changes may alter runtime behavior silently
```

### High-Risk Dependency Changes

Flag these dependency changes as high-risk regardless of path length:

```
- Interface signature changes (parameters added, removed, or retyped)
- Exception/error type changes (callers may not handle new errors)
- Configuration default changes (behavior shifts without code changes)
- Dependency version bumps (transitive dependency changes)
- Database schema changes (migration required)
- API contract changes (serialization/deserialization may break)
```

## Combining Scores

### The Final Relevance Calculation

```
Relevance = (Proximity * 0.35) + (Recency * 0.25) + (Impact * 0.25) + (Confidence * 0.15)
```

### Worked Example

```
Context item: ADR-0005 "Adopt OAuth 2.0 with JWT for API Authentication"
Focus area: src/auth/token_validator.py

Proximity: ADR mentions "authentication" and "token" -> Direct reference
           Score: 100

Recency:   ADR accepted 4 months ago (120 days)
           Score: max(0, 100 - (120 * 0.5)) = 40

Impact:    ADR constrains how authentication works in the focus area
           Score: 80

Confidence: ADR content read and verified
            Score: 100

Final: (100 * 0.35) + (40 * 0.25) + (80 * 0.25) + (100 * 0.15)
     = 35 + 10 + 20 + 15
     = 80 (Critical relevance -- include in executive summary)
```

### Another Worked Example

```
Context item: Commit group adding billing module tests
Focus area: src/auth/token_validator.py

Proximity: Billing module, no dependency path to auth
           Score: 15

Recency:   Committed 3 days ago
           Score: max(0, 100 - (3 * 4)) = 88

Impact:    No bearing on auth work
           Score: 10

Confidence: Verified from git log
            Score: 100

Final: (15 * 0.35) + (88 * 0.25) + (10 * 0.25) + (100 * 0.15)
     = 5.25 + 22 + 2.5 + 15
     = 44.75 (Medium -- omit unless space permits)
```

## Relevance Thresholds by Briefing Section

Different sections of the briefing have different inclusion thresholds:

| Section | Minimum Score | Rationale |
|---------|--------------|-----------|
| Executive summary | 80 | Only the most critical context |
| Recent changes | 60 | Changes worth knowing about |
| Architecture decisions | 50 | ADRs have long-term relevance |
| Dependency context | 55 | Dependencies matter for blast radius |
| Conventions | 45 | Conventions matter but are less urgent |
| Session recommendations | 70 | Only recommend based on high-relevance context |

## Edge Cases and Overrides

### New Project (< 30 Days of History)

When the project has very little history, lower all thresholds by 20 points.
In a new project, almost everything is relevant because the patterns have not
yet stabilized.

### Major Refactoring in Progress

When commit patterns suggest a major refactoring (high churn across many files,
systematic renames, many files moving between directories), boost the relevance
of all refactoring-related context by 15 points. The focus area may need to
participate in the refactoring.

### Merge Conflict in Progress

If `git status` shows merge conflicts, boost the relevance of all context
related to the conflicting files to Critical (100) regardless of calculated
score. Merge conflicts demand immediate attention.

### User-Specified Override

If the user explicitly says "I care about X," boost everything related to X
by 25 points and reduce everything unrelated by 15 points. User intent is
the strongest relevance signal.
