# vue-architecture-checklist — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## Vue Checklist (language-specific)

| # | Check | Severity |
|---|-------|----------|
| 1 | **Reactivity discipline** — no destructuring `reactive()` without `toRefs`; `ref` unwrapped correctly in templates vs script; no reassigning a `reactive()` object wholesale | Critical |
| 2 | **Watcher/lifecycle correctness** — complete `watch` dependency sources (no implicit-stale closures); cleanup registered for subscriptions/timers in `onUnmounted`; no derived state recomputed that belongs in a `computed` | High |
| 3 | **Component cohesion** — one responsibility per SFC; container/presentational separation where it earns it; no 400-line god components | Medium |
| 4 | **State placement** — state lives at the lowest common owner; no prop-drilling past ~3 levels (lift to `provide`/`inject` or a Pinia store); server state in a query layer, not `ref`+`onMounted` fetch | High |
| 5 | **Render performance** — stable `v-for` `:key` (never array index for dynamic lists); `computed` preferred over methods for derived values; `v-once`/`v-memo` only where a measured re-render warrants it | Medium |
| 6 | **Type safety** — `tsconfig` `strict: true`; `<script setup lang="ts">` with typed `defineProps`/`defineEmits`; no `any` without justification | High |
| 7 | **Accessibility** — semantic elements over `div` soup; interactive elements keyboard-reachable; labels/`alt`/ARIA where needed; `eslint-plugin-vuejs-accessibility` clean | High |
| 8 | **Boundary & dep hygiene** — no cross-feature deep imports; data-fetching isolated from presentation; error handling around async UI (`onErrorCaptured`/`app.config.errorHandler`); bundle/dep weight justified | Medium |

ESLint config: [eslint configuration](references/eslint-configuration.md). Full section-by-section list (with the reactivity & watcher audit table) + grounding query map: [review checklist](references/review-checklist.md).

## AI Discipline Rules

- **Lint + types must pass first.** `eslint --max-warnings 0` and `vue-tsc --noEmit` are the baseline; report failures before the architectural checklist.
- **Evidence or it is not a finding.** Cite `file:line`; show the eslint/grep output. Never grade on vibes.
- **Version-gate recommendations.** Do not suggest Vue 3-only APIs (`<script setup>`, Teleport, Suspense) for a Vue 2 codebase without the Composition API bridge.
- **Architecture, not security.** XSS, secret leakage, and dependency CVEs belong to `vue-security-review` — note them and route there.
