# AI Discipline, Anti-Patterns, and Error Recovery

## AI Discipline Rules

### CRITICAL: Evidence Before Recommendation

**WRONG:**
```
This looks like an old Vue app. I recommend upgrading to Vue 3.
```

**RIGHT:**
```
Version detection:
  package.json → "vue": "^2.6.14"
  grep "methods:" → 128 Options API components across 94 files
  grep "from '@vue/test-utils'" → 60 test files use Vue Test Utils v1 (Vue 2 mount API)

Vue 2 → 3 is viable but Vue Test Utils v1 tests will need the v2 API. Sequence the test-tooling
migration alongside the version bump, testing the mount-API changes on a small slice first.
```

### REQUIRED: Quantify Before Scoring

**WRONG:** "The Options→Composition migration is large."

**RIGHT:** "128 Options API components (grep count); 41 use `created()` data fetching; test coverage
18%. Effort: XL. Risk: Med — raised by low coverage. Recommend characterization tests first."

### CRITICAL: Incremental Plans Only

**WRONG:** "Rewrite the app in Vite + TypeScript + Composition API."

**RIGHT:** "Phase 1: Vue CLI→Vite (1wk). Phase 2: add TS per-file (ongoing). Phase 3: test tooling to
Vitest + Vue Testing Library (2wk). Phase 4: Vue 3 (1wk). Phase 5: Options→Composition, ~15
components/week."

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Big-bang rewrite recommendation** | Rewrites fail; behavior is lost; timeline explodes | Incremental migration with working checkpoints |
| 2 | **Recommending Options→Composition without tests** | Cannot verify behavior preserved | Component characterization tests as Phase 0 |
| 3 | **Ignoring dependency Vue 3 support** | A lib with no Vue 3 build blocks the bump | Audit every dep's Vue 3 compatibility first |
| 4 | **Missing the Vue Test Utils v1 blocker** | v1's mount API differs from v2; suites silently break | Flag the test-tooling migration as a prerequisite to Vue 3 |
| 5 | **Combining version + Options→Composition + JS→TS at once** | Unmanageable, untestable change set | Sequence: tooling → tests → version → components → state → types |
| 6 | **No effort estimates** | A plan without estimates can't be scheduled | Every phase has S/M/L/XL or a day estimate |
| 7 | **Assessing without running greps** | Counts are evidence; intuition is not | Always run the SCAN greps before scoring |
| 8 | **Recommending Vue 3-only features pre-upgrade** | `<script setup>`, Teleport, Suspense don't exist on Vue 2 without a bridge | Gate feature recommendations to the post-upgrade version |
| 9 | **Treating server state like client state in the plan** | Moving fetch into Pinia reinvents caching | Plan server-state → query layer as its own phase |
| 10 | **Skipping the Vue CLI→Vite tooling win** | Slow builds drag every later phase | Do the tooling migration early to speed feedback |

## Error Recovery

### Cannot determine a dependency's Vue 3 support

```
Symptoms: a UI library's Vue 3 compatibility is unclear.

Recovery:
1. Check package.json peerDependencies/engines for vue.
2. Check the package's repo for recent releases and Vue 3 issues/branches.
3. Check for a maintained fork or a modern replacement.
4. If unknown, mark "Unknown — manual investigation required" in the blockers table; do not assume.
```

### Test coverage is zero

```
Symptoms: no component tests found.

Recovery:
1. Document: "Coverage 0% — no behavioral tests."
2. Phase 0 becomes mandatory: component characterization tests on critical flows before any risky migration.
3. Flag this as the highest-risk factor; do not recommend Options→Composition until Phase 0 is done.
```

### Build config is customized / ejected webpack (`vue.config.js`)

```
Symptoms: a hand-rolled `vue.config.js` with `configureWebpack`/`chainWebpack` exists.

Recovery:
1. Inventory the custom webpack needs (loaders, aliases, env injection, proxies).
2. Map each to its Vite equivalent (plugins, resolve.alias, define, server.proxy).
3. Flag any need without a Vite equivalent as a blocker to resolve before the tooling migration.
```
