# Complexity Scoring Methodology

This document defines the detailed scoring methodology for assessing Jira issue complexity.

## Overview

The complexity score is calculated across 5 dimensions, each with a specific weight reflecting its impact on implementation difficulty. The weighted average produces a percentage that maps to Low/Medium/High complexity.

## Dimensions

### 1. Scope Breadth (Weight: 1.5)

Measures how many components, systems, or areas of the codebase are affected.

| Score | Criteria | Examples |
|-------|----------|----------|
| 1 | Single file or function change | Fix typo, update constant |
| 2 | Single component modification | Add button to existing form |
| 3 | Multiple files in same module | New feature in existing service |
| 4 | Multiple modules or services | Feature spanning API and frontend |
| 5 | Cross-system changes | Database + API + Frontend + External integration |

**Scoring Guidelines:**
- Count distinct layers mentioned (UI, API, database, external)
- Count number of services or microservices affected
- Consider data flow - does change cascade through system?

**Keywords that increase score:**
- "and" connecting components ("API and frontend")
- "across" indicating breadth ("across all modules")
- "integration" suggesting system boundaries
- Multiple file types mentioned (.tsx, .py, .sql)

### 2. Requirements Clarity (Weight: 1.5)

Measures how specific, complete, and testable the requirements are.

| Score | Criteria | Indicators |
|-------|----------|------------|
| 1 | Crystal clear, testable AC | Numbered criteria with specific values |
| 2 | Mostly clear with minor gaps | Good AC, few ambiguous terms |
| 3 | Partially specified | Some AC present, some gaps |
| 4 | Vague with some structure | Headers exist but content unclear |
| 5 | No clear requirements | Missing AC/DoD, ambiguous description |

**Scoring Guidelines:**
- Are acceptance criteria present? (+1 if missing)
- Are they testable (specific, measurable)? (+1 if vague)
- Is definition of done specified? (+0.5 if missing)
- Are edge cases addressed? (+0.5 if not)

**Red flags that increase score:**
- Subjective terms: "user-friendly", "fast", "clean"
- Undefined scope: "etc.", "and more", "similar features"
- Missing success criteria: no way to verify completion
- No error scenarios: happy path only

### 3. Technical Uncertainty (Weight: 1.2)

Measures the level of unknowns, new technology, or required research.

| Score | Criteria | Indicators |
|-------|----------|------------|
| 1 | Familiar tech, established patterns | Copy existing implementation |
| 2 | Minor new elements | New library version, small learning curve |
| 3 | Some research needed | New library, unfamiliar API |
| 4 | Significant unknowns | New technology stack, complex integration |
| 5 | Major research required | POC needed, architecture decisions pending |

**Scoring Guidelines:**
- Is the technology stack familiar to the team?
- Are there existing patterns to follow?
- Does the issue explicitly mention research or investigation?
- Are there architectural decisions yet to be made?

**Keywords that increase score:**
- "research", "investigate", "explore", "spike"
- "POC", "proof of concept", "prototype"
- "evaluate", "compare", "decide between"
- "figure out", "determine approach"
- "new technology", "first time", "never done"

### 4. Dependencies (Weight: 1.0)

Measures reliance on external teams, systems, or blocking factors.

| Score | Criteria | Indicators |
|-------|----------|------------|
| 1 | No dependencies | Self-contained change |
| 2 | Internal dependencies only | Depends on other team's merged PR |
| 3 | External API dependency | Third-party service integration |
| 4 | Cross-team coordination | Requires sync with other team |
| 5 | Multiple external dependencies | Multiple teams, external vendors |

**Scoring Guidelines:**
- Count external teams mentioned
- Identify third-party services or APIs
- Check for blocking issues or prerequisites
- Consider deployment dependencies

**Keywords that indicate dependencies:**
- Team names or mentions of "coordinate with"
- "waiting on", "blocked by", "depends on"
- "after [X] is complete", "prerequisite"
- External service names (Stripe, Auth0, AWS services)
- "sync with", "align with", "discuss with"

### 5. Estimation Confidence (Weight: 1.0)

Measures how well the work has been sized and estimated.

| Score | Criteria | Indicators |
|-------|----------|------------|
| 1 | Well-sized with high confidence | Story points, time estimate, breakdown |
| 2 | Estimated with some uncertainty | Story points but range is wide |
| 3 | Rough estimate only | "About a day" type estimates |
| 4 | No estimate, but estimable | Could be sized but hasn't been |
| 5 | Cannot be estimated | Too vague to size, needs breakdown |

**Scoring Guidelines:**
- Are story points assigned?
- Is there a time estimate?
- Has the issue been broken into subtasks?
- Does the team have historical reference for similar work?

**Indicators of low confidence:**
- No story points or time estimate
- Very large story point values (8, 13, 21)
- Question marks in estimates
- Comments indicating uncertainty about size

## Calculation Formula

```
weighted_sum = (scope × 1.5) + (clarity × 1.5) + (uncertainty × 1.2) + (dependencies × 1.0) + (estimation × 1.0)

max_weighted_sum = (5 × 1.5) + (5 × 1.5) + (5 × 1.2) + (5 × 1.0) + (5 × 1.0)
                 = 7.5 + 7.5 + 6.0 + 5.0 + 5.0
                 = 31.0

complexity_percentage = (weighted_sum / max_weighted_sum) × 100
```

### Example Calculation

Issue with scores:
- Scope: 3/5 (multiple files, same module)
- Clarity: 2/5 (good AC, minor gaps)
- Uncertainty: 2/5 (minor new elements)
- Dependencies: 1/5 (self-contained)
- Estimation: 2/5 (story points assigned)

```
weighted_sum = (3 × 1.5) + (2 × 1.5) + (2 × 1.2) + (1 × 1.0) + (2 × 1.0)
             = 4.5 + 3.0 + 2.4 + 1.0 + 2.0
             = 12.9

complexity_percentage = (12.9 / 31.0) × 100 = 41.6%
```

**Result**: Medium Complexity (41.6%)

## Threshold Definitions

### Low Complexity (< 40%)

**Characteristics:**
- Single component affected
- Clear, testable acceptance criteria
- Familiar technology
- No external dependencies
- Well-estimated

**Recommendation:** READY TO IMPLEMENT

### Medium Complexity (40% - 70%)

**Characteristics:**
- Multiple components but manageable scope
- Some requirements gaps
- Minor unknowns or learning curve
- Internal dependencies only
- Reasonable estimate with some uncertainty

**Recommendation:** NEEDS CLARIFICATION (address gaps first)

### High Complexity (> 70%)

**Characteristics:**
- Wide scope across systems
- Significant requirements gaps
- Major technical unknowns
- External dependencies or coordination
- Cannot be confidently estimated

**Recommendation:** NEEDS PLANNING MODE

## Special Cases

### Automatic High Complexity Triggers

Regardless of calculated score, flag as HIGH COMPLEXITY if:

1. **Missing AC entirely** - Cannot verify completion
2. **Research explicitly required** - "spike", "POC", "investigate"
3. **Architecture decision pending** - Core approach undecided
4. **Multiple external team dependencies** - Coordination overhead
5. **First-time technology** - No team experience

### Automatic Low Complexity Indicators

Consider reducing complexity if:

1. **Identical to previous work** - Copy-paste with modifications
2. **Explicit documentation exists** - Step-by-step guide available
3. **Isolated change** - Zero impact on other components
4. **Team has deep expertise** - Done many times before
