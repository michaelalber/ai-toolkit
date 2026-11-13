# react-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## React Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Hooks rules** — hooks called unconditionally at top level; no hooks in loops/conditions; custom hooks prefixed `use` | Critical |
| 2 | **Effect correctness** — complete dependency arrays (no `exhaustive-deps` suppressions); cleanup returned for subscriptions/timers; no derived state that belongs in render | High |
| 3 | **Component cohesion** — one responsibility per component; container/presentation separation where it earns it; no 300-line god components | Medium |
| 4 | **State placement** — state lives at the lowest common owner; no prop-drilling past ~3 levels (lift to context/store); server state in a query cache, not `useState`+`useEffect` | High |
| 5 | **Render performance** — stable list `key`s (never array index for dynamic lists); if the React Compiler is wired, manual `memo`/`useMemo`/`useCallback` are a finding unless justified (compiler bail-out, cross-boundary prop to a non-compiled dep); if not wired, use them only where a measured re-render warrants it | Medium |
| 6 | **Type safety** — `tsconfig` `strict: true`; no `any` without justification; props typed (no implicit `any`); no `as` casts hiding shape mismatches | High |
| 7 | **Accessibility** — semantic elements over `div` soup; interactive elements keyboard-reachable; labels/`alt`/ARIA where needed; `eslint-plugin-jsx-a11y` clean | High |
| 8 | **Boundary & dep hygiene** — no cross-feature deep imports; data-fetching isolated from presentation; error boundaries around async UI; bundle/dep weight justified | Medium |

ESLint config: [eslint configuration](references/eslint-configuration.md). Full section-by-section list (with the hooks & effects audit table) + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Lint + types must pass first.** `eslint --max-warnings 0` and `tsc --noEmit` are the baseline; report failures before the architectural checklist.
- **Evidence or it is not a finding.** Cite `file:line`; show the eslint/grep output. Never grade on vibes.
- **Version-gate recommendations.** Do not suggest React 18/19 APIs (`useTransition`, Actions, `use()`, server components) for a React 16/17 codebase.
- **Architecture, not security.** XSS, secret leakage, and dependency CVEs belong to `react-security-review` — note them and route there.
