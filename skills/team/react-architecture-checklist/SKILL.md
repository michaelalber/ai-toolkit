---
name: react-architecture-checklist
audience: team
description: >
  Grades an existing React/TypeScript codebase. Detects React version, bundler (Vite/CRA/Next),
  TypeScript usage, state library, and router, then checks hooks discipline, component cohesion,
  effect correctness, render performance, state boundaries, accessibility, and type safety with
  file:line evidence. Use to review or grade a React codebase. Not for Socratic critique
  (architecture-review), security audits (react-security-review), or new test-first code (tdd).
---

# React Architecture Checklist

> "A checklist cannot fly a plane, but a pilot cannot fly safely without one."
> — Atul Gawande

## Core Architectural Values

Shared across the `dotnet` / `python` / `php` / `rust` / `react` architecture checklists — same values, language-specific checks.

> **Grounding note:** the knowledge base has no React corpus. Use `collection="javascript"` for TS/JS
> idioms, `collection="ui_ux"` for accessibility, and `collection="internal"` for architecture standards;
> cite **react.dev** as the primary React authority. Never invent a `react` collection.

| # | Value | What it means |
|---|-------|---------------|
| 1 | **Detect before judge** | Determine React version / bundler / TS / state lib before applying any item; context decides what is idiomatic. |
| 2 | **Evidence over opinion** | Every finding cites `file:line` and the offending pattern. "Too many re-renders" is not a finding; "`features/cart/Cart.tsx:31` recreates `onAdd` every render, breaking the memoized `<Row>`" is. |
| 3 | **Feature cohesion** | Organized by feature, not by technical type (`components/`, `hooks/`, `utils/` dumping grounds). Cross-feature imports are a violation. |
| 4 | **Dependencies point inward** | UI components depend on hooks/services, not the reverse; data-fetching is isolated from presentation. Boundaries are explicit via barrels. |
| 5 | **Hooks honor the rules** | Hooks called unconditionally at the top level; effect dependency arrays complete; effects clean up. A lint suppression of `react-hooks/exhaustive-deps` is a finding. |
| 6 | **Config & secrets hygiene** | No secrets in client bundles; only intentionally-public `VITE_`/`NEXT_PUBLIC_` values exposed; config injected, not hardcoded. |
| 7 | **Version awareness** | Recommendations gated to the detected React version; never suggest an API that does not exist there (e.g. `use()` / Actions on React 17). |
| 8 | **Tests gate change** | Untested components/hooks are a finding; high-risk interactive components without RTL tests are prioritized. |
| 9 | **Graded, actionable output** | A letter grade (A–F) from counted findings, plus prioritized, version-correct recommendations. |

## Workflow

Shared skeleton: `DETECT → SCAN → REPORT → RECOMMEND`.

```
DETECT     React version (package.json `react`), bundler (Vite/CRA/Next.js), TypeScript (tsconfig +
           strict), state library (Redux/RTK/Zustand/Context/none), router. Record findings;
           version changes what is idiomatic.

SCAN       Run the React Checklist below section by section. Gather evidence with tooling:
             npx eslint . --max-warnings 0          # baseline — incl. eslint-plugin-react-hooks
             npx tsc --noEmit                        # type errors gate the review
             npx knip                                # dead code / unused exports / deps
             grep -rn "useEffect" src/ | wc -l       # effect surface to audit
           Every violation becomes a finding with file:line and a severity (critical/high/medium/low).

REPORT     Emit the graded report (Output Template). Grade = function of counted findings.

RECOMMEND  Prioritize: critical → quick wins → modernization. Version-gate every recommendation.
```

## React Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Hooks rules** — hooks called unconditionally at top level; no hooks in loops/conditions; custom hooks prefixed `use` | Critical |
| 2 | **Effect correctness** — complete dependency arrays (no `exhaustive-deps` suppressions); cleanup returned for subscriptions/timers; no derived state that belongs in render | High |
| 3 | **Component cohesion** — one responsibility per component; container/presentation separation where it earns it; no 300-line god components | Medium |
| 4 | **State placement** — state lives at the lowest common owner; no prop-drilling past ~3 levels (lift to context/store); server state in a query cache, not `useState`+`useEffect` | High |
| 5 | **Render performance** — stable list `key`s (never array index for dynamic lists); `memo`/`useMemo`/`useCallback` only where a measured re-render warrants it; no new object/array/function literals passed to memoized children | Medium |
| 6 | **Type safety** — `tsconfig` `strict: true`; no `any` without justification; props typed (no implicit `any`); no `as` casts hiding shape mismatches | High |
| 7 | **Accessibility** — semantic elements over `div` soup; interactive elements keyboard-reachable; labels/`alt`/ARIA where needed; `eslint-plugin-jsx-a11y` clean | High |
| 8 | **Boundary & dep hygiene** — no cross-feature deep imports; data-fetching isolated from presentation; error boundaries around async UI; bundle/dep weight justified | Medium |

ESLint config: [eslint configuration](references/eslint-configuration.md). Full section-by-section list (with the hooks & effects audit table): [review checklist](references/review-checklist.md).

## State Block

```
<arch-checklist-state>
language: react
mode: DETECT | SCAN | REPORT | RECOMMEND | COMPLETE
detected: [react-version | bundler | ts:strict/loose | state-lib | tests:yes/no]
issues_found: [critical:N high:N medium:N low:N]
last_action: [what was just done]
next_action: [what should happen next]
</arch-checklist-state>
```

## Output Template

Shared across all architecture checklists.

```markdown
## Architecture Checklist: [app/package] (React)
**React**: [19] | **Bundler**: [Vite/CRA/Next] | **TS**: [strict/loose/none] | **State**: [RTK/Zustand/Context] | **Tests**: [yes/no]

| Section | Pass | Fail | Warn |
|---------|------|------|------|
| Hooks / Effects / Cohesion / State / Render / Types / a11y / Boundaries | … | … | … |

### Grade: [A–F]
Grading: **A** 0 crit/0 high/≤3 med · **B** 0 crit/≤2 high · **C** 0 crit, gaps in one area ·
**D** 1+ crit · **F** fundamental problems (conditional hooks, `any` everywhere, no a11y, server state in effects throughout).

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| CRITICAL | file:line | [pattern] | [version-gated fix] |

**Hooks/effects audit**: | location | issue | dep array | cleanup | risk |
**Quick wins**: [low-effort, high-impact] · **Modernization**: [larger items with effort estimate]
```

## AI Discipline Rules

- **Lint + types must pass first.** `eslint --max-warnings 0` and `tsc --noEmit` are the baseline; report failures before the architectural checklist.
- **Evidence or it is not a finding.** Cite `file:line`; show the eslint/grep output. Never grade on vibes.
- **Version-gate recommendations.** Do not suggest React 18/19 APIs (`useTransition`, Actions, `use()`, server components) for a React 16/17 codebase.
- **Architecture, not security.** XSS, secret leakage, and dependency CVEs belong to `react-security-review` — note them and route there.

## Integration with Other Skills

- **`architecture-review`** — When the grade is D/F, escalate to the Socratic critic: this checklist finds _what_ is wrong; `architecture-review` builds _why_.
- **`react-security-review`** — Companion for the security dimension (XSS, bundle secrets, `npm audit`).
- **`react-feature-slice`** — Correct-pattern reference when the checklist flags structural/cross-feature violations.
- **`react-modernization-analyzer`** — When findings cluster around legacy patterns (class components, CRA), route to the modernization plan.
- **`tdd`** — Methodology for adding the RTL tests the checklist flags as missing, and for driving any refactor.
- **`dotnet` / `python` / `php` / `rust`-architecture-checklist** — Sibling skills sharing this exact Core Values + workflow + output.
