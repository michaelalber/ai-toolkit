# Jira Review Conventions

Depth behind the Core Philosophy constraints: principles, extraction algorithm, complexity scoring,
signal detection, discipline rules, and worked examples. The scoring system lives in
`complexity-scoring.md`, description parsing in `description-patterns.md`, and question templates in
`clarifying-questions.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Completeness Before Clarity** | A vague issue blocks implementation regardless of prose quality; missing AC is a harder blocker than unclear wording. | Flag missing acceptance criteria before assessing description quality. |
| 2 | **Ambiguity Is Blocking** | Any requirement that admits two interpretations will have the wrong one chosen. | Flag two-interpretation requirements as blockers, not suggestions. |
| 3 | **Complexity Is Measurable** | Complexity is estimated from signal density, not intuition (new integrations, cross-service changes, undecided approaches, external deps). | Apply the scoring formula from `complexity-scoring.md`; never guess. |
| 4 | **Testability Is a Gate** | An issue without AC cannot be verified done; TDD can't start without a testable criterion. | No issue passes review without ≥ 1 AC expressible as a test. |
| 5 | **Size Predicts Risk** | High-complexity issues correlate with scope drift and missed dependencies. | Flag issues scoring ≥ 8 (or > 70%) for decomposition before sprint commitment. |
| 6 | **Context Reduces Rework** | Every assumption the implementer must make is a potential rework event. | Every gap requiring an assumption is a required clarification. |
| 7 | **Dependencies Must Be Explicit** | Undeclared dependencies cause cascading delays. | Flag any issue implying another issue/team's delivery without an explicit link. |
| 8 | **Reproducibility Is Non-Negotiable** | A bug that can't be reproduced can't be fixed. | Any bug issue missing reproduction steps fails review unconditionally. |
| 9 | **UI Issues Require Visuals** | "The button looks wrong" is not actionable; a marked-up screenshot is. | Flag any UI/UX issue lacking screenshots, annotated mockups, or Figma links. |
| 10 | **Estimates Are Evidence-Based** | Story points without complexity signals are fiction. | Require complexity scoring before accepting an estimate. |

## Auto-Trigger

Activate automatically when these MCP tools are invoked, and review the returned issue before any
implementation work: `jira_get_issue`, `jira_get_issue_with_docs`.

## Requirements Extraction Algorithm

Patterns are in `description-patterns.md`. Extraction targets: Acceptance Criteria, Definition of
Done, User Stories (As a/I want/so that), Technical Requirements.

```
1. Scan for section headers (case-insensitive): "Acceptance Criteria", "AC:", "Criteria";
   "Definition of Done", "DoD:", "Done When"
2. Parse list items following headers: numbered (1. 2.), bullets (- * •), checkboxes ([ ] [x] ☐ ☑)
3. Detect BDD patterns anywhere: Given [precondition] / When [action] / Then [expected result]
4. Flag unstructured descriptions for manual review
```

## Complexity Scoring

Full 5-dimension weighted system in `complexity-scoring.md`.

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Scope Breadth | 1.5 | Number of components/systems affected |
| Requirements Clarity | 1.5 | Specificity/completeness of AC/DoD |
| Technical Uncertainty | 1.2 | New tech, integrations, unknowns |
| Dependencies | 1.0 | External team/system dependencies |
| Estimation Confidence | 1.0 | Presence of sizing/story points |

`weighted_score = Σ(dimension_score × weight) / Σ(max_score × weight)`; `complexity% = weighted_score × 100`.
Thresholds: **< 40%** GREEN (low) · **40–70%** YELLOW (medium) · **> 70%** RED (high).

## Complexity Signal Detection

**RED (high):** multiple components (API + frontend + DB); cross-service communication; multiple
roles; data migration. Uncertainty keywords: "research/investigate/spike/POC/explore", "figure
out/determine/decide", "might need/possibly/could require". Vague: "fast" (no metric),
"user-friendly" (no UX spec), "scalable" (no load), "secure" (no requirements). Dependency: external
team, third-party API, waiting on decisions.

**YELLOW (medium):** 2-3 components; partial AC coverage; some ambiguous + some clear requirements;
internal dependencies only.

**GREEN (low):** single-component change; clear testable AC; well-defined DoD; familiar stack; no
external deps; existing patterns to follow.

**Critical-info flags** (force NEEDS CLARIFICATION regardless of complexity): no AC found; vague
success criteria ("should work well"); undefined domain terms; missing error-handling requirements;
no performance/scale expectations when relevant.

## Clarifying Question Quality

Templates in `clarifying-questions.md`. Be specific (reference exact issue text), actionable
(concrete answers), prioritized (most critical first), and limited (max 5 questions).

## Discipline Rules

- **Flag gaps by name, not category.** "This issue is unclear" gives the product owner nothing.
  *Right:* "Missing: acceptance criteria. The description says 'fix the login page' but doesn't
  state what 'fixed' means, which users are affected, or the success condition. Add AC before this
  is sprint-ready."
- **Complexity scores require evidence.** Never "score of 8 — it looks large." *Right:* "Score 8
  (HIGH). Signals: 2 endpoints modified (Scope 3/5); 1 new table; session model affected (Technical
  Uncertainty 4/5); mobile team must ship push support first (Dependencies 5/5). Recommend decomposition."

## Worked Examples

**READY TO IMPLEMENT (~25%)** — `[PROJ-123] Add logout button`: clear user story; 4 testable AC
(button shown only when authenticated, click clears token, redirect to login, success toast); DoD
lists unit + E2E tests + review.

**NEEDS CLARIFICATION (unable to assess)** — `[PROJ-456] Improve dashboard performance`: description
is "The dashboard is slow. Make it faster." Questions: what metric defines slow (current/target
load time)? which components? which user actions trigger it? acceptable target?

**NEEDS PLANNING MODE (~82%)** — `[PROJ-789] Implement real-time notifications`: multiple platforms
(web + mobile); approach undecided (WebSockets vs SSE vs polling); external dependency (mobile team
push support); vague AC ("real-time" undefined, "all platforms" scope unclear).
