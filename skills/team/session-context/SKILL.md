---
name: session-context
description: Git change summarization, ADR relevance matching, and pattern applicability for building session context. Provides techniques for analyzing recent project activity, scoring context relevance, and detecting patterns that accelerate AI coding session starts. Use when building context for a new coding session, analyzing recent changes, or matching project decisions to current work.
---

# Session Context

> "Context is worth 80 IQ points. The difference between a productive coding session and a
> stumbling one is almost never skill -- it is whether you understood the state of the system
> before you started changing it."
> -- Alan Kay (attributed)

## Core Philosophy

Every AI coding session starts with a context gap. The model does not know what changed yesterday, which architectural decisions govern this module, or which files are volatile and which are stable. This skill bridges that gap systematically, turning the cold-start problem into a solved problem.

Session context is not about knowing everything -- it is about knowing the right things. A developer who knows that three files in the auth module changed last week, that ADR-0005 governs the authentication approach, and that the payment module depends on the auth module's token validator is far more effective than one who read the entire git log but cannot prioritize.

**The Session Context Principle:**
Relevant context, delivered concisely at session start, prevents more bugs than any amount of testing after the fact. The best debugging is the debugging you never have to do because you understood the system before you touched it.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Relevance Over Recency** | A 6-month-old ADR about the module you are modifying matters more than yesterday's commit to an unrelated file | Context briefings sorted purely by date; old but critical decisions omitted |
| 2 | **Summarize, Do Not Dump** | Raw git logs and full ADR reproductions overwhelm rather than inform; summaries with citations let the reader drill down on demand | Context briefings that are longer than the code being worked on |
| 3 | **Cite Every Claim** | Every statement about what changed, what was decided, or what depends on what must reference a specific commit, file, or ADR | Vague statements like "the project recently migrated to..." without a commit hash |
| 4 | **Proximity-First Expansion** | Start with files directly in the focus area, expand to direct dependencies, then to transitive dependencies -- stop when relevance drops below threshold | Briefings that cover the whole project equally regardless of focus |
| 5 | **Hotspots Signal Risk** | Files that changed frequently in recent history are more likely to have bugs, merge conflicts, and implicit knowledge requirements | Briefings that treat all files as equally stable |
| 6 | **Conventions Are Context** | Coding patterns, linter configs, and naming conventions observed in the focus area are as important as what changed -- they prevent style drift and review friction | Briefings that cover changes but not how the code is expected to look |
| 7 | **Decisions Govern Implementation** | Active ADRs constrain what implementations are acceptable; surfacing them prevents well-intentioned violations | Developers making decisions that contradict active ADRs because they did not know the ADRs existed |
| 8 | **Dependencies Define Blast Radius** | Knowing what depends on the focus area tells you who will be affected by your changes; knowing what the focus area depends on tells you what might break underneath you | Changes made without understanding upstream or downstream impact |
| 9 | **Patterns Emerge from Changes** | Clusters of related commits reveal ongoing efforts, refactoring campaigns, and feature work that provide narrative context | Treating each commit as isolated; missing the storyline |
| 10 | **Staleness Is a Warning** | Overdue ADR retrospectives, long-untouched dependencies, and stale convention files are risks that should be surfaced | Briefings that only report recent activity and miss decay signals |

## Workflow

### Context Building Flow

```
SCOPE
    Define the focus area and time window:
    - User-specified files, modules, or features
    - Default time window: 2 weeks for active projects, 4 weeks for less active
    - Identify the git repository root and branch topology

        |
        v

GATHER
    Collect raw context from multiple sources:
    - Git log with stats for the time window
    - File change frequencies (hotspot detection)
    - Import/dependency statements in the focus area
    - ADR files and their modification dates
    - Convention files (.editorconfig, linter configs, CONTRIBUTING.md)
    - README and design documents

        |
        v

SCORE
    Rate each piece of gathered context for relevance:
    - Apply proximity scoring (distance from focus area)
    - Apply recency weighting (recent changes to relevant files score higher)
    - Apply decision applicability (ADRs that govern the focus area)
    - Apply dependency relevance (changes to dependencies of the focus area)
    - Filter out context below the relevance threshold

        |
        v

SYNTHESIZE
    Assemble the scored context into a structured briefing:
    - Group git changes by feature/area
    - Rank ADRs by relevance score
    - Present dependency subgraph focused on the work area
    - Surface warnings (hotspots, overdue reviews, breaking changes)
    - Formulate session recommendations

        |
        v

DELIVER
    Present the briefing in the standard template format:
    - Executive summary first (< 40 lines)
    - Detailed sections following
    - Every claim cited with source
    - Recommendations are specific and actionable
```

### Change Summarization Protocol

When summarizing git changes, follow this protocol:

```
1. COLLECT: git log --stat --since="[window]" for the focus area
2. GROUP:   Cluster commits by:
   a. Feature (commits that touch related files)
   b. Area (commits grouped by directory/module)
   c. Author (when attribution matters for context)
3. SUMMARIZE: For each group, produce:
   a. Commit range (first..last hash)
   b. File count
   c. One-sentence summary of what changed and why
4. DETECT: Identify patterns:
   a. Hotspot files (>3 changes in the window)
   b. Churn files (many additions AND deletions -- refactoring signals)
   c. New files (additions to the codebase)
   d. Deleted files (removals from the codebase)
5. CONTEXTUALIZE: For each hotspot, explain why it is hot:
   a. Bug fixes? Feature additions? Refactoring?
   b. Is this expected churn or a warning sign?
```

### ADR Relevance Matching Protocol

When matching ADRs to the focus area:

```
1. DISCOVER: Find all ADR files in the repository
   - Check: docs/adr/, adr/, docs/decisions/, architecture/
   - Pattern: NNNN-*.md or ????-*.md
2. PARSE: Extract from each ADR:
   - Title, status, date, related ADRs
   - Technologies and modules mentioned
   - Consequences (what it enables and constrains)
   - Review schedule and dates
3. SCORE: Rate each ADR for relevance:
   - Direct mention of focus area files/modules -> HIGH
   - Technology match (same language, framework, tool) -> MEDIUM
   - Same project area but different module -> LOW
   - Deprecated or superseded -> SKIP (unless replacement missing)
4. CHECK: For relevant ADRs, verify:
   - Is the status still "Accepted"?
   - Are any retrospectives overdue?
   - Do consequences conflict with planned changes?
5. SURFACE: Include in the briefing with:
   - ADR number and title
   - Status and relevance score
   - One-line explanation of why it matters for this session
```

## State Block

Track the current context-building session:

```markdown
<session-context-state>
mode: scope | gather | score | synthesize | deliver
focus_area: [files, modules, or features]
time_window: [date range]
repository: [path to repository root]
commits_collected: [count]
files_in_focus: [count]
adrs_discovered: [count]
adrs_relevant: [count]
dependencies_traced: [count]
hotspots_detected: [count]
relevance_threshold: [score cutoff]
last_action: [what was just completed]
next_action: [what should happen next]
</session-context-state>
```

**Mode definitions:**
- `scope` -- Defining the focus area and time window
- `gather` -- Collecting raw context from git, files, and ADRs
- `score` -- Rating gathered context for relevance
- `synthesize` -- Assembling scored context into a structured briefing
- `deliver` -- Presenting the final briefing

## Output Templates

### Executive Summary Template

```markdown
### Executive Summary

**What changed**: [2-3 sentences summarizing recent activity in/around the focus area.
Cite commit ranges. Example: "The auth module received 12 commits (abc1234..def5678)
over the past week, primarily adding OAuth 2.0 refresh token support. The payment
module had 3 dependency updates (ghi9012..jkl3456)."]

**Key decisions**: [List active ADRs governing this area. Example: "ADR-0005
(OAuth 2.0 with JWT) governs authentication approach. ADR-0012 (PostgreSQL for
order service) affects data access patterns."]

**Watch out for**: [Specific warnings. Example: "auth/token_validator.py changed 7
times this week (hotspot). ADR-0005 90-day review is 2 weeks overdue."]

**Recommended focus**: [Actionable guidance. Example: "Review token_validator.py
changes before modifying auth flows. Check ADR-0005 consequences section for
constraints on token handling."]
```

### Change Group Template

```markdown
#### [Group Name: e.g., "OAuth 2.0 Refresh Token Implementation"]

| Commits | Files | Summary |
|---------|-------|---------|
| abc1234..def5678 (Jan 15-20) | 8 | Added refresh token rotation to auth module |

**Key files changed:**
- `src/auth/token_validator.py` -- New refresh token validation logic
- `src/auth/models.py` -- Added RefreshToken model
- `tests/auth/test_refresh.py` -- 12 new tests covering rotation scenarios

**Why this matters for [focus area]:** [One sentence connecting this change group
to the current session's focus]
```

### Dependency Context Template

```markdown
### Dependency Context

**Focus area depends on** (outbound):
- `core.models` -- Stable (unchanged in 3 months), provides base entity types
- `db.session` -- Changed 2x this week (commit abc1234), session management refactored
- `auth.tokens` -- Hotspot (7 changes this week), active feature development

**Depends on focus area** (inbound):
- `api.controllers` -- 4 controllers import from focus area, will need testing if interfaces change
- `workers.background_tasks` -- 2 task handlers reference focus area entities

**Recently changed dependencies** (risk surface):
- `db.session` (commit abc1234, Jan 18): Connection pooling parameters changed. If focus
  area uses long-running transactions, verify timeout behavior.
```

### Hotspot Analysis Template

```markdown
### File Hotspots

| Rank | File | Changes | Authors | Pattern |
|------|------|---------|---------|---------|
| 1 | src/auth/token_validator.py | 7 | 2 | Active feature development |
| 2 | src/db/session.py | 4 | 1 | Refactoring (high churn) |
| 3 | src/api/middleware.py | 3 | 2 | Bug fixes (3 fix commits) |

**Interpretation:**
- `token_validator.py`: Expect this file to change further. Coordinate with team
  members working on auth. Consider adding a lock or review requirement.
- `session.py`: High churn suggests refactoring in progress. Changes here may affect
  any code that opens database sessions.
- `middleware.py`: Three bug fixes suggest fragile code. Review recent changes
  carefully before adding more middleware.
```

## AI Discipline Rules

### CRITICAL: Cite Sources for Every Claim

Never state "the project uses X" or "this module changed recently" without a specific reference. Commit hashes, file paths, line numbers, and ADR numbers are mandatory. If you cannot cite a source, you cannot include the claim. This is the single most important rule -- unsourced context is worse than no context because it creates false confidence.

### CRITICAL: Relevance Scoring Must Be Explicit

When including context in a briefing, state why it is relevant. "ADR-0005 is relevant because it governs the authentication module, which is the focus area" is acceptable. Including ADR-0005 without explanation is not. The reader should understand the editorial judgment behind every inclusion.

### CRITICAL: Conciseness Is Not Optional

The executive summary must fit in one screen (< 40 lines). If you cannot summarize the context that concisely, you are including too much. Ruthlessly prioritize. The detailed sections exist for drill-down; the summary exists for orientation. A 200-line executive summary is a failure of editorial judgment.

### CRITICAL: Distinguish Observation from Inference

"Commits abc1234..def5678 added refresh token support" is observation (verifiable from commit messages and diffs). "The team is preparing for a major auth overhaul" is inference (may be wrong). Both can appear in a briefing, but inferences must be clearly labeled: "Based on the pattern of auth-related commits, it appears the team may be..."

### CRITICAL: Do Not Reproduce, Summarize

Do not paste full ADR contents, full git logs, or full file contents into the briefing. Summarize with citations. The briefing is a guide to the territory, not the territory itself. A developer who needs the full ADR can follow the citation.

### CRITICAL: Surface Decay and Staleness

Actively look for and report staleness signals: overdue ADR retrospectives, dependencies that have not been updated in years, convention files that contradict actual code practices, and TODO comments older than 6 months. Decay is invisible until someone looks for it, and the context builder should be that someone.

### CRITICAL: Focus Area Boundaries Are Soft

The focus area defines the center of attention, not a hard boundary. Context from outside the focus area is included when it has a dependency relationship, a recent change that affects the focus area, or a governing decision. The scoring system handles this -- do not artificially restrict context to only files within the focus area.

## Anti-Patterns

### The Kitchen Sink Briefing

**What it looks like**: A briefing that includes every commit, every ADR, and every dependency in the project. The executive summary is 200 lines. The developer spends 30 minutes reading context instead of 5 minutes orienting.

**Why it fails**: Information overload is the same as no information. The developer cannot distinguish important context from noise.

**Correct approach**: Score every piece of context for relevance. Include only items above the threshold. Keep the executive summary under 40 lines. Use detailed sections for drill-down, not for initial reading.

### The Recency Trap

**What it looks like**: A briefing that only includes context from the last 3 days. A critical ADR from 6 months ago that governs the focus area is omitted because it is "old."

**Why it fails**: Architectural decisions and dependency relationships do not expire on a schedule. The most relevant context may be the oldest.

**Correct approach**: Score by relevance to the focus area, not by date. Use recency as a tiebreaker between equally relevant items, not as a primary filter.

### Citation-Free Context

**What it looks like**: "The auth module was recently refactored." "There are some dependency issues." "The team decided to use PostgreSQL."

**Why it fails**: Without citations, the developer cannot verify claims, cannot drill down for details, and cannot trust the briefing. Unsourced claims create false confidence.

**Correct approach**: Every claim gets a citation. "The auth module was refactored in commits abc1234..def5678 (Jan 15-20, 14 files changed)." No exceptions.

### Inference Presented as Fact

**What it looks like**: "The team is migrating to a microservices architecture." (Based on observing 3 new service directories, but no ADR or explicit statement.)

**Why it fails**: The inference may be wrong. The new directories could be experiments, prototypes, or copies. Acting on a wrong inference wastes time or causes damage.

**Correct approach**: "Three new service directories (order-svc/, payment-svc/, auth-svc/) appeared in commits ghi9012..jkl3456. No ADR was found documenting this pattern. This may indicate a move toward service decomposition, but should be confirmed."

## Error Recovery

### Shallow Clone Limits History

**Symptoms**: `git log` returns fewer commits than expected. `git rev-parse --is-shallow-repository` returns true.

**Recovery**:
1. Note the shallow clone limitation in the briefing header
2. Report the actual depth available
3. Adjust the time window to match available history
4. Recommend `git fetch --unshallow` if deeper history is needed
5. Mark the briefing as "limited history" so the reader knows it may be incomplete

### Monorepo With Thousands of Files

**Symptoms**: Focus area is one small part of a massive monorepo. Scanning all files is impractical.

**Recovery**:
1. Limit git log to the focus area path: `git log -- [path]`
2. Limit dependency scanning to direct imports from focus area files
3. Search for ADRs only in the focus area's subtree first, then project-wide
4. Note "monorepo scope limitation" in the briefing
5. Recommend the user specify a narrower focus if the briefing is still too broad

### No Recent Activity

**Symptoms**: The focus area has no commits in the time window. The briefing has no change summary.

**Recovery**:
1. Expand the time window incrementally (2 weeks -> 4 weeks -> 3 months)
2. Report the last activity date for the focus area
3. Flag this as a staleness signal: "No changes in [N weeks] -- verify this area is still actively maintained"
4. Focus the briefing on dependency context and applicable ADRs instead
5. Check if the focus area was recently created by being split from another area

## Integration

This skill works with and references the following related skills:

- **architecture-journal** -- Session context identifies relevant ADRs and surfaces overdue retrospectives. Architecture journal provides the templates and review protocols for acting on those findings. When session context finds an overdue review, recommend loading architecture-journal for the retrospective workflow.

- **dependency-mapper** -- Session context traces dependencies at a summary level to establish blast radius. Dependency mapper provides the full Robert C. Martin metrics (Ca, Ce, I, A, D) for deeper analysis. When session context reveals concerning dependency patterns, recommend loading dependency-mapper for quantitative assessment.

**Workflow integration example:**
1. Load session-context to build the initial briefing
2. If dependency patterns look concerning, load dependency-mapper for metrics
3. If ADRs need reviewing, load architecture-journal for retrospective workflow
4. Use the briefing as the starting point for the coding session

## Stack-Specific Guidance

See reference files for detailed techniques:

- [Change Summarization](references/change-summarization.md) -- Git log analysis techniques: commit grouping by feature/area, diff stat interpretation, file hotspot detection, author attribution, branch topology summarization
- [Relevance Matching](references/relevance-matching.md) -- Context relevance scoring: file proximity to current task, recency weighting, ADR applicability heuristics, pattern detection from recent changes, dependency path relevance
