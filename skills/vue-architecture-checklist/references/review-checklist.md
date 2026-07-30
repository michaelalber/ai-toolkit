# Vue review checklist — section by section

Full expansion of the 8 checklist items. Each row is a concrete thing to grep/read for, the severity,
and the version note that gates the recommendation.

## 1. Reactivity discipline (Critical)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `const { total } = reactive(state)` | Destructuring a `reactive()` loses reactivity — the local var is a frozen snapshot | Use `toRefs(state)` before destructuring, or keep `state.total` |
| `props` destructured in `<script setup>` without `toRefs`/`computed` | Loses reactivity on the extracted value | `const { name } = toRefs(props)`, or reference `props.name` directly |
| Whole-object reassignment of a `reactive()` (`state = { ...state, x: 1 }`) | Breaks the proxy identity; loses reactivity | Mutate properties in place, or use `ref` for values that get wholesale-replaced |
| `ref` used but `.value` forgotten in script (not template) | Silent bug — comparisons/assignments hit the ref wrapper, not the value | Always `.value` in `<script>`; Vue auto-unwraps only in `<template>` |

```bash
grep -rn "const { .* } = reactive(" src/       # heuristic for destructured reactive()
```

## 2. Watcher/lifecycle correctness (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `watch` with an incomplete source list | Stale-closure bug — a dependency changes but the watcher doesn't fire | Add the missing source, or use `watchEffect` to auto-track |
| `watch`/`watchEffect` with no cleanup for a subscription/timer/listener | Leak; not disposed on unmount | Return/register a cleanup via the `onCleanup` callback or `onUnmounted` |
| `computed` that has side effects | Recomputed unpredictably; breaks caching assumptions | Move side effects to a `watch`/`watchEffect`; keep `computed` pure |
| Data fetching in `onMounted` + `ref` everywhere | Race conditions, no caching/dedupe | Use a composable data layer (e.g. TanStack Query for Vue / `useAsyncData` in Nuxt) for server state |

## 3. Component cohesion (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| SFC `<script>` block > ~250 lines or > ~3 responsibilities | Hard to test/reuse; merge-conflict magnet | Split presentation from data/logic; extract sub-components |
| Business logic inline in `<template>` expressions | Untestable, hard to read | Move to a `computed` or a composable |

## 4. State placement (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| Prop drilled > ~3 levels | Fragile, noisy refactors | Lift to `provide`/`inject` or a Pinia store slice |
| Pinia store holding ephemeral UI state (e.g. "is dropdown open") | Bloats global state, couples unrelated UI | Keep local `ref` in the component |
| Server data mirrored into a Pinia store via `onMounted` fetch | Cache invalidation reinvented badly | Server state → query layer; client state → store/local |

## 5. Render performance (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `:key="index"` on a reorderable/dynamic `v-for` | Wrong reconciliation, state bleed | Use a stable id |
| A method call in the template for a derived value recomputed every render | No caching; recalculated on every re-render | Use `computed` instead of a plain method |
| `v-once`/`v-memo` everywhere with no measured cause | Complexity with no benefit | Remove; memoize only measured hot paths |

## 6. Type safety (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `strict: false`/absent in tsconfig | Every other check is unreliable | Enable `strict` |
| `any` / untyped `defineProps` | No compile-time safety | Type props with `defineProps<Props>()`; replace `any` with the real shape or `unknown` + narrowing |
| `as SomeType` casts | Hides shape mismatches | Validate at the boundary (e.g. zod) and infer |

## 7. Accessibility (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `<div @click>` for actions | Not keyboard/AT reachable | Use `<button>`; add `@keydown` only if a non-button is unavoidable |
| Missing `alt` / form label / `aria-*` | Screen-reader users blocked | Add labels; run `eslint-plugin-vuejs-accessibility`; reference WCAG 2.2 via `collection="ui_ux"` |

## 8. Boundary & dependency hygiene (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `import ../otherFeature/internal` | Cross-feature coupling | Import only the feature's barrel (`features/x`), or shared code |
| Presentational component calling `fetch` directly | Couples UI to transport | Move to a composable/service in the feature's data layer |
| No `onErrorCaptured`/`app.config.errorHandler` around async UI | One throw can blank a subtree | Wrap routes/async subtrees with error handling |
| Heavy dep for a trivial need (e.g. moment for one format) | Bundle bloat | `knip` + bundle visualizer; replace or drop |

## Version gates

| Recommendation | Min Vue |
|----------------|---------|
| `<script setup>`, Teleport, Suspense, Fragments | 3.0 |
| Composition API on Vue 2 | 2.7 (built-in) or 2.6 with the `@vue/composition-api` plugin |
| `defineModel()` macro | 3.4 |
| Reactivity Transform (`$ref`/`$computed`) | experimental, removed after 3.4 — do not recommend |

Never recommend an API the detected version lacks.
