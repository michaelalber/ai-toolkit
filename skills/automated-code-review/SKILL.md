---
name: automated-code-review
description: Systematic review execution engine -- transforms coaching CACR loops into autonomous review checklists with pass/fail gates, convention detection, and structured finding production. Use when running autonomous code reviews to ensure systematic coverage and consistent quality.
---

# Automated Code Review

> "Inspection at the source is called prevention. Inspection after the fact is called sorting."
> -- W. Edwards Deming

> "You cannot inspect quality into a product."
> -- Harold F. Dodge

## Core Philosophy

Code review coaching teaches humans how to review. Automated code review teaches agents how to execute reviews systematically. The difference is the same as between a textbook and a manufacturing process: one builds understanding; the other produces consistent output at scale.

This skill converts the CACR (Challenge-Attempt-Compare-Reflect) coaching framework into an execution framework: systematic checklists that the agent runs against code, with explicit pass/fail gates that prevent superficial reviews, and convention detection that calibrates findings to the project's own standards rather than abstract ideals.

**The gap this skill fills:**

A code review coaching skill teaches a human to ask "did I check error handling?" An automated review skill tells an agent exactly HOW to check error handling: enumerate every function call that can fail, verify each has an error path, verify the error path handles the error (not swallows it), verify the error message includes diagnostic context. The difference is between a principle and a procedure.

**Three pillars of automated review:**

1. **Systematic coverage** -- Every review category is checked against a concrete checklist. No category is skipped because the agent "did not think of it." The checklist is the minimum; the agent can find additional issues beyond the checklist, but the checklist ensures a baseline.

2. **Convention calibration** -- Findings are calibrated to the project's own conventions, not to abstract best practices. If a project uses snake_case, a camelCase variable is a finding. If the project uses camelCase, it is not. Convention detection precedes review execution.

3. **Pass/fail gating** -- Each review phase has explicit gates. A review cannot proceed from SCAN to ANALYZE without confirming that conventions have been detected. A review cannot proceed from ANALYZE to SYNTHESIZE without confirming that all five categories have been checked for every file. Gates prevent the agent from producing a superficial report and claiming the review is complete.

**What this skill does NOT do:**

This skill does not teach the agent to review code. It assumes the agent already understands code review principles (from code-review-coach) and security analysis (from security-review-trainer). What it provides is the operational framework: the checklists, the gates, the convention detection, and the structured output format that turns review knowledge into consistent review execution.


## Domain Principles

These principles govern every automated review execution.

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Checklist as Floor** | The checklist defines the minimum review scope. The agent can find issues beyond the checklist, but cannot skip checklist items. A review that misses a checklist item is incomplete regardless of what else it found. | HARD -- every checklist item must be marked pass/fail/not-applicable |
| 2 | **Convention Before Judgment** | Before reporting any style or convention finding, the agent must detect the project's actual conventions. Reporting a finding based on external standards when the project follows different conventions is a false positive. | HARD -- convention detection is a gate before ANALYZE phase |
| 3 | **Evidence for Every Finding** | Every finding must include the specific code (line numbers, snippet) that triggers it. "This module has poor error handling" is not a finding. "Line 42: `except Exception: pass` swallows all exceptions including KeyboardInterrupt" is a finding. | HARD -- findings without evidence are rejected |
| 4 | **Severity from Impact** | Severity is determined by the impact of the issue in the project's actual context, not by the theoretical worst case. A SQL injection in an internal tool with no user-facing input is lower severity than the same pattern in a public API. Context shapes severity. | HARD -- severity must include context reasoning |
| 5 | **False Positive Prevention** | Before reporting, verify the finding against framework behavior, middleware, project patterns, and surrounding code. The agent should have a lower false positive rate than a hurried human reviewer, not a higher one. | HARD -- false positive check is part of every finding pipeline |
| 6 | **Structured Output** | Review output follows a consistent format across all reviews. Consumers of the review (human or CI) can parse the output predictably. Ad hoc formatting is not acceptable. | HARD -- output must match defined templates |
| 7 | **Category Completeness** | All five review categories (security, correctness, performance, maintainability, style) must be evaluated for every file in scope. Skipping a category because "the code looks fine" in that area is not permitted -- the checklist must be explicitly run. | HARD -- per-category results logged for every file |
| 8 | **Incremental Context** | When reviewing a diff (not a full file), the agent must read the full file to understand context. A diff-only review misses issues that arise from interactions between changed and unchanged code. | MEDIUM -- full file context required for diff reviews |
| 9 | **Convention Drift Detection** | When a file's conventions differ from the project's detected conventions, distinguish between "this file is wrong" and "this file predates the convention." Old code that works is not necessarily a finding. | MEDIUM -- flag convention age when reporting style findings |
| 10 | **Positive Signal** | Report what the code does well, not just what it does poorly. Positive observations calibrate the review and prevent the report from reading as pure criticism. At minimum, one positive observation per file reviewed. | MEDIUM -- positive observations section required in output |


## Workflow

### Execution Pipeline

The automated review executes a four-phase pipeline. Each phase has entry gates and exit gates. The review cannot advance to the next phase without passing the exit gate of the current phase.

```
    +-----------+     GATE: scope defined, files enumerable
    |           |
    |   SCAN    |---> Identify scope, detect conventions, enumerate files
    |           |
    +-----+-----+
          |
          v         GATE: conventions detected, all files readable
    +-----------+
    |           |
    |  ANALYZE  |---> Run checklists per file, per category. Record findings.
    |           |
    +-----+-----+
          |
          v         GATE: all files analyzed, all categories checked
    +-----------+
    |           |
    | SYNTHESIZE|---> De-duplicate, cross-reference, rank, theme.
    |           |
    +-----+-----+
          |
          v         GATE: findings verified, false positives filtered
    +-----------+
    |           |
    |  REPORT   |---> Produce structured output.
    |           |
    +-----------+
```

### Phase Gates

#### SCAN Exit Gate

All of the following must be true:
- [ ] Review scope is explicitly defined (diff, files, directory, PR)
- [ ] All files in scope have been enumerated with languages identified
- [ ] Project conventions have been detected (or explicitly marked as "unable to detect")
- [ ] Tech stack and frameworks have been identified
- [ ] At least 3 existing project files have been sampled for convention detection

#### ANALYZE Exit Gate

All of the following must be true for every file in scope:
- [ ] File was read completely (not partially, not from cache)
- [ ] Security checklist was run -- all items marked pass/fail/N-A
- [ ] Correctness checklist was run -- all items marked pass/fail/N-A
- [ ] Performance checklist was run -- all items marked pass/fail/N-A
- [ ] Maintainability checklist was run -- all items marked pass/fail/N-A
- [ ] Style checklist was run against detected conventions -- all items marked pass/fail/N-A
- [ ] Every finding has evidence (line number + code snippet)
- [ ] Every finding has category and severity assigned
- [ ] False positive check completed for every finding

#### SYNTHESIZE Exit Gate

All of the following must be true:
- [ ] Duplicate findings have been merged
- [ ] Cross-file issues have been identified
- [ ] Findings are ranked by severity
- [ ] Related findings are grouped into themes where applicable
- [ ] Final false positive review completed on consolidated list

#### REPORT Exit Gate

All of the following must be true:
- [ ] Output follows the structured template
- [ ] Every finding has evidence, category, severity, and suggested fix
- [ ] Findings are ordered by severity (critical first)
- [ ] Positive observations are included
- [ ] "Needs verification" findings are flagged separately
- [ ] Review statistics are computed and included


## Review Checklists

The checklists below define the minimum checks per category. For detailed sub-item guidance, see [Review Checklist Engine](references/review-checklist-engine.md).

### Security Checklist (Minimum)

```
[ ] All external inputs traced to their terminal use
[ ] SQL/NoSQL queries checked for injection (parameterized or not)
[ ] Authentication/authorization verified on every access-controlled path
[ ] Sensitive data not exposed in logs, errors, or responses
[ ] Cryptographic operations use appropriate algorithms and key management
[ ] File path operations checked for traversal
[ ] Deserialization of untrusted data checked
[ ] Dependencies checked against known vulnerability databases (if manifest present)
```

### Correctness Checklist (Minimum)

```
[ ] Every conditional checked for boundary cases
[ ] Every loop checked for off-by-one and termination
[ ] Null/nil/undefined handled at every dereference point
[ ] Error handling present for every operation that can fail
[ ] Error paths do not swallow exceptions silently
[ ] Types are consistent (no implicit coercion surprises)
[ ] Concurrency primitives are correct (locks, atomics, channels)
[ ] Resource cleanup occurs in all paths (happy and error)
```

### Performance Checklist (Minimum)

```
[ ] No O(n^2) or worse on unbounded or user-controlled input
[ ] No database queries inside loops (N+1 pattern)
[ ] No blocking I/O in async/event-driven contexts
[ ] No unbounded collection growth (caches, buffers, logs)
[ ] Pagination or streaming used for large data sets
[ ] Expensive operations not repeated unnecessarily (missing caching)
```

### Maintainability Checklist (Minimum)

```
[ ] Functions have single, clear responsibility
[ ] No magic numbers or string literals without context
[ ] Naming is descriptive and consistent within the file
[ ] No copy-paste duplication (Rule of Three applies)
[ ] Abstraction levels are not mixed (business logic vs I/O)
[ ] Error messages include diagnostic context
[ ] No dead code (unreachable branches, unused variables)
```

### Style Checklist (Minimum)

```
[ ] Naming convention matches project convention
[ ] Formatting matches project convention (indentation, braces, line length)
[ ] Import organization matches project convention
[ ] Language idioms are used where appropriate
[ ] File organization follows project patterns
[ ] No unused imports or variables
```


## Convention Detection Protocol

Before any style or convention-dependent review, the agent must detect the project's conventions. For detailed detection procedures, see [Convention Detection](references/convention-detection.md).

### Detection Steps

```
1. SEARCH for configuration files:
   - Linter configs (.eslintrc, .pylintrc, .rubocop.yml, etc.)
   - Formatter configs (.prettierrc, .editorconfig, rustfmt.toml, etc.)
   - CI pipeline configs that enforce style

2. SAMPLE existing code:
   - Read 3-5 representative files in the same directory or module
   - Note naming conventions (camelCase, snake_case, PascalCase)
   - Note error handling patterns (try/catch, Result types, error codes)
   - Note logging patterns (structured, unstructured, log levels used)
   - Note testing patterns (test file location, naming, assertion style)

3. DETECT framework conventions:
   - Identify the framework and check for framework-specific conventions
   - Note any project-specific overrides of framework defaults

4. RECORD detected conventions in the review state:
   - Naming: [convention]
   - Error handling: [pattern]
   - Logging: [pattern]
   - Testing: [pattern]
   - Formatting: [standard or config file reference]

5. APPLY detected conventions to review checklists:
   - Style checklist items calibrate to detected conventions
   - Maintainability items calibrate to project patterns
   - "Inconsistency" findings reference project standards, not external standards
```


## Finding Pipeline

Every potential finding passes through this pipeline before inclusion in the report:

```
DETECT -> VERIFY -> CATEGORIZE -> SEVERITY -> FORMAT -> INCLUDE

1. DETECT:   Agent notices a potential issue
2. VERIFY:   Check against context -- is this actually an issue?
              - Is it reachable in the execution path?
              - Is it handled by a framework or middleware?
              - Is it an intentional pattern in this project?
              If not verified -> DISCARD (log as filtered false positive)
3. CATEGORIZE: Assign primary category (security/correctness/performance/
               maintainability/style)
4. SEVERITY:  Assign severity based on impact in context
              - Who is affected? How often? What is the blast radius?
              If ambiguous -> mark as "needs verification"
5. FORMAT:    Produce structured finding with evidence
6. INCLUDE:   Add to findings list
```


## Output Templates

### Per-File Analysis Log

```markdown
### File: [path]

**Purpose**: [what this file does]
**Lines**: [total lines]
**Language**: [language]

#### Checklist Results

| Category | Items Checked | Pass | Fail | N/A |
|----------|--------------|------|------|-----|
| Security | [N] | [N] | [N] | [N] |
| Correctness | [N] | [N] | [N] | [N] |
| Performance | [N] | [N] | [N] | [N] |
| Maintainability | [N] | [N] | [N] | [N] |
| Style | [N] | [N] | [N] | [N] |

#### Findings

| # | Line | Category | Severity | Finding | Evidence | Suggested Fix |
|---|------|----------|----------|---------|----------|---------------|

#### Positive Observations

- [what this file does well]
```

### Consolidated Report

```markdown
## Automated Code Review Report

**Scope**: [description]
**Files reviewed**: [N]
**Review date**: [date]
**Conventions detected**: [summary]

### Critical Findings

[Findings with full evidence, one per section]

### High Findings

[Findings with full evidence]

### Medium Findings

[Findings, grouped by theme where possible]

### Low / Nit Findings

[Summary table format]

### Needs Verification

[Findings where context was ambiguous]

### Positive Observations

[Per-file and cross-cutting positive observations]

### Review Statistics

| Metric | Value |
|--------|-------|
| Files reviewed | [N] |
| Checklist items evaluated | [N] |
| Total findings | [N] |
| Critical | [N] |
| High | [N] |
| Medium | [N] |
| Low | [N] |
| Nit | [N] |
| Needs verification | [N] |
| False positives filtered | [N] |
| Positive observations | [N] |
```


## Integration

### Cross-Skill References

This skill integrates with other review and coaching skills in the toolkit:

- **code-review-coach** -- Provides the underlying review rubric, scoring methodology, and category definitions that this skill operationalizes. Code-review-coach teaches what to look for; automated-code-review provides the execution checklists that ensure nothing is skipped.

- **security-review-trainer** -- Provides deep security review patterns, OWASP category mapping, and vulnerability detection strategies. The security checklist in this skill is a minimum; security-review-trainer expands it with level-appropriate subtlety.

- **pr-feedback-writer** -- Provides guidance on formatting findings as constructive, actionable PR comments. After automated-code-review produces findings, pr-feedback-writer shapes how those findings are communicated to the code author.


## Stack-Specific Guidance

Automated review checklists apply across all languages. The following references provide detailed checklist items and detection procedures:

- [Review Checklist Engine](references/review-checklist-engine.md) -- Detailed per-category checklists with sub-items, automated pass/fail criteria, severity mapping, and language-specific checklist extensions
- [Convention Detection](references/convention-detection.md) -- Pattern detection procedures for project conventions (naming, error handling, logging, testing patterns) with per-ecosystem detection strategies
