# Change Summarization Reference

> "A commit log is a narrative. The art is in reading the story it tells, not just the
> individual words."
> -- Jessica Kerr

This reference covers techniques for analyzing git history and producing useful change
summaries for session context briefings. The goal is to transform raw git data into
structured, actionable summaries that help developers orient quickly.

## Git Log Analysis Techniques

### Collecting Raw Data

The foundation of change summarization is the right git log query. Different queries
serve different purposes:

```bash
# Basic log with stats for a time window
git log --since="2 weeks ago" --stat --format="%H|%ai|%an|%s"

# Log filtered to a specific path (focus area)
git log --since="2 weeks ago" --stat -- src/auth/

# Log with full diff for detailed analysis
git log --since="2 weeks ago" -p -- src/auth/

# Log showing only file names (faster for hotspot detection)
git log --since="2 weeks ago" --name-only --format="%H"

# Log with numstat for precise addition/deletion counts
git log --since="2 weeks ago" --numstat --format="%H|%ai|%an|%s"

# Shortlog for author attribution summary
git shortlog --since="2 weeks ago" -sn -- src/auth/

# Log showing branch merge topology
git log --since="2 weeks ago" --graph --oneline --all
```

### Interpreting Diff Stats

Diff stats reveal the nature of changes at a glance:

| Pattern | Interpretation | Example |
|---------|---------------|---------|
| High additions, low deletions | New feature or expansion | `+342 -12` -- new capability |
| Balanced additions and deletions | Refactoring or rewrite | `+180 -165` -- structural change |
| Low additions, high deletions | Cleanup or simplification | `+8 -245` -- removed dead code |
| Single-digit changes | Bug fix or config tweak | `+3 -2` -- targeted correction |
| Changes across many files | Cross-cutting concern | 40 files changed -- likely API change |
| Changes in test files only | Test coverage improvement | tests/ only -- no behavior change |
| Changes in config files only | Infrastructure or build change | .yml, .json -- deployment related |

### Numstat Interpretation

```
# git log --numstat output:
# additions  deletions  filename
    45        12        src/auth/token_validator.py
     0         0        src/auth/__init__.py
     8         3        tests/auth/test_tokens.py

# Interpretation:
# - token_validator.py: Major changes (45 adds, 12 dels) -- active development
# - __init__.py: Binary or renamed file (0/0 means git cannot diff)
# - test_tokens.py: Minor test additions accompanying the main change
```

## Commit Grouping Strategies

### Grouping by Feature

Feature-based grouping clusters commits that work toward the same goal. This
is the most useful grouping for session context because it answers "what was
being worked on?"

**Detection heuristics:**
1. **Common file sets**: Commits that touch overlapping sets of files likely
   belong to the same feature
2. **Branch origin**: Commits from the same feature branch are a natural group
3. **Commit message patterns**: Shared prefixes, ticket numbers, or keywords
   (e.g., "auth:", "TICKET-123", "refresh token")
4. **Temporal proximity**: Commits by the same author within a short time window
   on the same files

**Algorithm:**
```
1. Parse all commits in the time window
2. For each commit, extract: files changed, author, message, timestamp
3. Build a file co-occurrence matrix (which files change together)
4. Cluster commits where file overlap > 50%
5. Merge clusters with matching message patterns
6. Name each cluster from the most common message theme
```

**Example output:**
```markdown
#### OAuth 2.0 Refresh Token Implementation (8 commits, Jan 15-20)

| Commits | Files | Summary |
|---------|-------|---------|
| abc1234..def5678 | 8 | Added refresh token rotation, validation, and storage |

Key files: token_validator.py (+45/-12), models.py (+23/-0), test_refresh.py (+89/-0)
Authors: Alice (5), Bob (3)
```

### Grouping by Area

Area-based grouping clusters commits by the part of the codebase they affect.
This answers "where in the system were changes happening?"

**Detection approach:**
```
1. Map each changed file to its module/directory
2. Group commits by primary module (the module with the most changed files)
3. Handle cross-module commits by assigning to the module with the most changes
4. Present as a module-level summary
```

**Example output:**
```markdown
| Area | Commits | Files | Summary |
|------|---------|-------|---------|
| src/auth/ | 12 | 8 | Refresh token feature + 2 bug fixes |
| src/db/ | 4 | 3 | Connection pooling refactor |
| src/api/ | 3 | 5 | New endpoint for token refresh |
| tests/ | 8 | 6 | Tests accompanying auth and db changes |
```

### Grouping by Author

Author-based grouping is useful when the session needs to understand who
is working on what, particularly for coordination purposes.

```
1. Group commits by author
2. For each author, summarize the areas they touched
3. Identify author-area concentrations (who is the expert on what)
```

**Example output:**
```markdown
| Author | Commits | Primary Area | Summary |
|--------|---------|-------------|---------|
| Alice | 7 | src/auth/ | Refresh token implementation |
| Bob | 5 | src/db/ | Connection pooling refactor |
| Carol | 3 | src/api/ | API endpoint additions |
```

## File Hotspot Detection

### What Makes a Hotspot

A file is a hotspot when it changes significantly more frequently than its
neighbors. Hotspots indicate:

- **Active development**: The file is being built or extended
- **Instability**: The file keeps needing fixes
- **Coupling magnet**: Other changes force this file to change
- **Knowledge concentration**: Only certain people change this file

### Hotspot Detection Algorithm

```
1. Count changes per file in the time window
2. Calculate the mean and standard deviation of change counts
3. Flag files with change counts > mean + 1 standard deviation
4. For each hotspot, analyze the commit messages to determine WHY:
   a. "fix" / "bug" / "patch" -> instability
   b. "add" / "feature" / "implement" -> active development
   c. "refactor" / "move" / "rename" -> structural change
   d. Mixed -> coupling magnet (forced changes from elsewhere)
```

### Hotspot Context

For each detected hotspot, provide context that helps the developer decide
whether it is a risk or just normal activity:

```markdown
**Hotspot: src/auth/token_validator.py (7 changes in 2 weeks)**

- Change pattern: Active development (5 feature commits, 2 bug fixes)
- Authors: Alice (5), Bob (2) -- primary knowledge holder is Alice
- Churn ratio: +245/-67 (net growth, not refactoring)
- Risk assessment: Medium -- active development means the file is in flux.
  If you need to modify this file, coordinate with Alice and review recent
  changes first.
- Last commit: def5678 (Jan 20) "add token rotation error handling"
```

### Churn Analysis

Churn measures volatility -- how much a file is being rewritten rather than
extended:

```
Churn ratio = min(additions, deletions) / max(additions, deletions)

Ratio near 0.0: Pure addition or deletion (growth or shrinkage)
Ratio near 0.5: Moderate rewriting
Ratio near 1.0: Heavy rewriting (equal adds and deletes)
```

High churn + many commits = refactoring in progress or instability.
Low churn + many commits = steady feature addition (healthy growth).

## Branch Topology Summarization

### Reading Branch Structure

Branch topology reveals the team's workflow and the state of parallel work:

```bash
# Visualize branch topology
git log --graph --oneline --all --since="2 weeks ago"

# Find branches that diverge from main
git branch -a --no-merged main

# Find the divergence point of a branch
git merge-base main feature-branch
```

### Topology Patterns to Report

| Pattern | Meaning | Report As |
|---------|---------|-----------|
| Single branch (main only) | Trunk-based development | "All changes on main branch" |
| Long-lived feature branch | Extended parallel work | "Branch [name] diverged [N days] ago, [N commits] ahead" |
| Multiple short branches merged | Standard PR workflow | "[N] branches merged in time window" |
| Divergent branches | Potential merge conflicts | "Branches [A] and [B] both modify [files] -- merge conflict risk" |
| Stale branches | Abandoned work | "Branch [name] last updated [N days] ago" |

### Merge Conflict Risk Detection

When two branches modify the same files, flag the potential conflict:

```
1. For each unmerged branch, list changed files
2. Compare against the focus area's recently changed files
3. If overlap exists, flag it:

"Branch feature-oauth and branch fix-session-handling both modify
src/auth/token_validator.py. If you are working on auth, be aware
of potential merge conflicts."
```

## Commit Message Parsing

### Extracting Semantic Information

Commit messages contain signals about the nature of changes:

| Prefix/Pattern | Interpretation | Context Value |
|---------------|---------------|---------------|
| `fix:` / `bugfix:` | Bug correction | High -- area had defects |
| `feat:` / `feature:` | New capability | High -- area is growing |
| `refactor:` | Structural change | Medium -- behavior unchanged but code different |
| `test:` | Test changes | Low -- tests only, no behavior change |
| `docs:` | Documentation | Low -- no code change |
| `chore:` / `build:` | Infrastructure | Medium -- build/deploy changes may affect behavior |
| `BREAKING:` / `!:` | Breaking change | Critical -- downstream consumers affected |
| Ticket numbers (`PROJ-123`) | Linked to issue tracker | Useful for drill-down |
| `WIP` / `wip` | Work in progress | Signal that this area is still in flux |
| `revert` | Undoing a previous change | High -- something went wrong |

### Multi-Line Message Analysis

The commit body often contains more context than the subject line:

```
1. Parse the first line as the summary
2. Look for "Why:" or "Reason:" lines in the body
3. Look for "Breaking changes:" or "BREAKING:" sections
4. Look for "Related:" or "See also:" references
5. Look for "Co-authored-by:" for collaboration signals
```

## Time Window Selection

### Choosing the Right Window

| Project Activity Level | Recommended Window | Rationale |
|----------------------|-------------------|-----------|
| High (10+ commits/day) | 1 week | Longer windows overwhelm with data |
| Moderate (3-10 commits/day) | 2 weeks | Balanced coverage and manageable volume |
| Low (< 3 commits/day) | 4 weeks | Need wider window to capture enough context |
| Dormant (< 1 commit/week) | 3 months | Focus on most recent activity period |

### Adaptive Window Strategy

```
1. Start with the default window (2 weeks)
2. Count commits in the window
3. If < 10 commits: expand to 4 weeks
4. If > 100 commits: narrow to 1 week, filtered to focus area
5. If > 200 commits even after filtering: narrow to 3 days + summarize
   the broader window at a high level
```

## Producing Actionable Summaries

### The Summary Formula

For each change group, produce a summary that follows this formula:

```
WHO did WHAT to WHERE because WHY, and it matters because IMPACT.

Example:
"Alice added refresh token rotation (commits abc..def, 8 files in src/auth/)
to implement the token lifecycle described in ADR-0005. This matters because
any code that validates auth tokens will now encounter refresh tokens and
must handle the new RefreshTokenExpired error type."
```

### Connecting Changes to the Session

The final step is always connecting the summarized changes to the current
session's focus:

```
For each change group, ask:
1. Does this change affect files in the focus area? -> Direct relevance
2. Does this change affect dependencies of the focus area? -> Indirect relevance
3. Does this change establish a pattern the focus area should follow? -> Convention relevance
4. Does this change conflict with what the session intends to do? -> Conflict relevance

Only include change groups that have at least one YES answer.
```
