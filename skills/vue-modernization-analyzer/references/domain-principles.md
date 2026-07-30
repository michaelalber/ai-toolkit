# Domain Principles

The ten principles that drive every assessment and recommendation.

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Risk Assessment First** | Every modernization carries risk; quantify it before recommending. An Options→Composition migration on 400 components with no tests differs from 40 components at 80% coverage. | Score every path: Effort (S/M/L/XL), Risk (Low/Med/High/Critical), Blocker potential |
| 2 | **Incremental Migration** | Vue 2.7+ supports Composition API alongside Options API; TS and JS coexist per-file; Vue CLI→Vite can be staged. Every path must decompose into phases that each leave the app working. | Each recommendation has a phased approach with working checkpoints |
| 3 | **Dependency Compatibility** | The migration is only as viable as its dependencies. A UI library with no Vue 3 build blocks the upgrade; an unmaintained `vue-router@3` blocks routing changes. | Audit `vue` peer/compat ranges of every dependency before recommending a version bump |
| 4 | **Test Coverage Gate** | Characterization tests (component tests that document current behavior) must exist before risky migrations. Without them you cannot prove behavior was preserved. | Assess component-test coverage; recommend characterization tests as Phase 0 — especially before Options→Composition |
| 5 | **Tooling Before Framework** | Vue CLI→Vite and JS→TS are tooling migrations that unblock everything else (fast feedback, type safety). Usually the highest-value early wins. | Sequence Vue CLI→Vite and TS adoption early; they de-risk later phases |
| 6 | **Strangler for State** | Vuex → Pinia is migrated module by module, not all at once. Server state moves to a query layer separately from client state. | Recommend per-module store migration; split server-state extraction into its own phase |
| 7 | **Version Gating** | Vue 3 (Composition API, multiple root nodes/Fragments, Teleport, Suspense) removes patterns from Vue 2 (filters, `$listeners`, global `Vue.use`/`Vue.mixin`). Identify what each bump enables and breaks. | Map the Vue 2→3 breaking changes against the codebase |
| 8 | **Test Framework Migration** | Vue Test Utils v1 (Vue 2) has a different mount API than v2 (Vue 3); Karma/Mocha setups are legacy — migrate to Vitest + Vue Testing Library test by test. | Flag Vue Test Utils v1 as a Vue 3 blocker; plan the test-tooling migration before/with the bump |
| 9 | **Effects & Data Layer** | `created()`/`mounted()` + `fetch` and `ref`+`onMounted` server-state patterns are fragile — no caching, no dedupe, no shared state across components. Recommend a query layer as part of modernization. | Identify ad-hoc fetching; recommend TanStack Query for Vue migration as a phase |
| 10 | **Build & Deploy Maturity** | Ejected/custom `vue.config.js` webpack overrides, Node-version pinning, and missing CI are modernization blockers. Assess them as prerequisites. | Flag custom webpack config and missing CI as prerequisites |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). The KB has a Vue 2/3 corpus under `collection="javascript"`
(alongside TS) — cite **vuejs.org** migration guides for version-specific detail.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Vue 2 to Vue 3 migration breaking changes", collection="javascript")` | At ASSESS — confirm the Vue 2→3 breaking-change surface |
| `search_knowledge("TypeScript migration from JavaScript gradual", collection="javascript")` | When scoring the JS→TS path |
| `search_knowledge("TypeScript strict any incremental adoption", collection="javascript")` | When scoring the JS→TS path |
| `search_knowledge("WCAG keyboard accessibility audit", collection="ui_ux")` | When the modernization should also close a11y gaps |
| `search_code_examples("vue options api to composition api", language="typescript")` | When estimating the Options→Composition effort |
