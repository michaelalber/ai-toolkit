# Session Context Conventions

Depth behind the Core Philosophy constraints: principles, the change-summarization and ADR-matching
protocols, discipline rules, anti-patterns, and recovery. Detailed git techniques are in
`change-summarization.md`; relevance scoring in `relevance-matching.md`.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Relevance Over Recency** | A 6-month-old ADR about the module you're modifying beats yesterday's commit to an unrelated file | Briefings sorted purely by date; old-but-critical decisions omitted |
| 2 | **Summarize, Do Not Dump** | Raw logs and full ADR reproductions overwhelm; summaries with citations let the reader drill down | Briefings longer than the code being worked on |
| 3 | **Cite Every Claim** | Every statement about changes/decisions/dependencies references a specific commit, file, or ADR | "the project recently migrated to…" with no commit hash |
| 4 | **Proximity-First Expansion** | Start with focus-area files, expand to direct then transitive deps; stop when relevance drops below threshold | Briefings covering the whole project equally |
| 5 | **Hotspots Signal Risk** | Frequently-changed files are likelier to have bugs, conflicts, and implicit knowledge | Treating all files as equally stable |
| 6 | **Conventions Are Context** | Patterns, linter configs, naming in the focus area prevent style drift and review friction | Covering changes but not how the code should look |
| 7 | **Decisions Govern Implementation** | Active ADRs constrain acceptable implementations | Decisions that contradict active ADRs the dev didn't know existed |
| 8 | **Dependencies Define Blast Radius** | Inbound deps tell you who's affected; outbound tell you what might break underneath | Changes made without upstream/downstream understanding |
| 9 | **Patterns Emerge from Changes** | Clusters of related commits reveal ongoing efforts and the storyline | Treating each commit as isolated |
| 10 | **Staleness Is a Warning** | Overdue retrospectives, long-untouched deps, stale convention files are risks | Briefings that report only recent activity and miss decay |

## Change Summarization Protocol

Detailed techniques in `change-summarization.md`.

```
1. COLLECT     git log --stat --since="[window]" for the focus area
2. GROUP       cluster commits by feature (related files), area (directory/module), author (when it matters)
3. SUMMARIZE   per group: commit range (first..last), file count, one-sentence what+why
4. DETECT      hotspots (>3 changes in window), churn (many +/− — refactoring), new files, deleted files
5. CONTEXTUALIZE  per hotspot: bug fixes? features? refactoring? expected churn or warning sign?
```

## ADR Relevance Matching Protocol

Scoring heuristics in `relevance-matching.md`.

```
1. DISCOVER  find ADRs: docs/adr/, adr/, docs/decisions/, architecture/ — pattern NNNN-*.md
2. PARSE     title, status, date, related ADRs, technologies/modules mentioned, consequences, review schedule
3. SCORE     direct mention of focus files/modules → HIGH; tech match → MEDIUM; same area, different
             module → LOW; deprecated/superseded → SKIP (unless replacement missing)
4. CHECK     status still "Accepted"? retrospectives overdue? consequences conflict with planned changes?
5. SURFACE   ADR number + title, status + relevance score, one-line "why it matters for this session"
```

## Discipline Rules

- **Cite sources for every claim.** Never "the project uses X" without a commit hash, file path,
  line number, or ADR number. Unsourced context is worse than none — it creates false confidence.
- **Relevance scoring must be explicit.** State *why* each item is included ("ADR-0005 governs the
  auth module, the focus area"). The reader should see the editorial judgment behind every inclusion.
- **Conciseness is not optional.** The executive summary fits one screen (< 40 lines). Detailed
  sections exist for drill-down; the summary for orientation.
- **Distinguish observation from inference.** "Commits abc..def added refresh tokens" is observation;
  "the team is preparing an auth overhaul" is inference and must be labeled as such.
- **Do not reproduce, summarize.** No full ADRs, git logs, or file contents — summarize with citations.
- **Surface decay and staleness.** Actively report overdue retrospectives, years-untouched deps,
  convention files that contradict the code, and TODOs older than 6 months.
- **Focus-area boundaries are soft.** Include outside-area context when it has a dependency
  relationship, a recent change affecting the focus, or a governing decision; let scoring decide.

## Anti-Patterns

**The Kitchen Sink Briefing** — every commit, ADR, and dependency; a 200-line summary. Information
overload equals no information. *Fix:* score for relevance, include only above threshold, summary < 40 lines.

**The Recency Trap** — only the last 3 days; a critical 6-month-old governing ADR omitted as "old."
Architectural decisions don't expire on a schedule. *Fix:* score by relevance; use recency only as a tiebreaker.

**Citation-Free Context** — "The auth module was recently refactored." Unverifiable, no drill-down,
false confidence. *Fix:* "Refactored in abc1234..def5678 (Jan 15-20, 14 files)." No exceptions.

**Inference Presented as Fact** — "The team is migrating to microservices" from 3 new directories
with no ADR. *Fix:* "Three new service dirs appeared in ghi..jkl; no ADR found; may indicate
decomposition but should be confirmed."

## Error Recovery

**Shallow clone limits history** (`git rev-parse --is-shallow-repository` is true):
1. Note the limitation in the briefing header; report the actual depth available
2. Adjust the time window to match; recommend `git fetch --unshallow` if deeper history is needed
3. Mark the briefing "limited history"

**Monorepo with thousands of files:**
1. Limit `git log -- [path]` to the focus area; limit dependency scanning to direct imports
2. Search ADRs in the focus subtree first, then project-wide; note "monorepo scope limitation"
3. Recommend a narrower focus if still too broad

**No recent activity** (no commits in the window):
1. Expand the window incrementally (2w → 4w → 3mo); report the last activity date
2. Flag as staleness: "No changes in N weeks — verify this area is still maintained"
3. Focus the briefing on dependency context and applicable ADRs; check if recently split from another area
