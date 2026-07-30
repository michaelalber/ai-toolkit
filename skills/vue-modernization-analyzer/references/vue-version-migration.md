# Vue version & pattern migration reference

Breaking-change and pattern detail behind the ASSESS phase. Use to map each path against what the SCAN
greps found. Cite **vuejs.org** migration guides as the authority; this is a planning summary, not a
substitute.

## Vue 2 → 3

| Change | Impact | Detection |
|--------|--------|-----------|
| `new Vue({...})` → `createApp({...})` | Required entry-point change; global config moves onto the app instance | `grep -rn "new Vue(" src/` |
| Filters (`{{ value \| filter }}`, `Vue.filter`) removed | Must become a method or `computed` | `grep -rn "Vue.filter\|filters:" src/` |
| `$listeners` merged into `$attrs` | Manual `v-on="$listeners"` no longer needed/valid | `grep -rn '\$listeners' src/` |
| `$on`/`$off`/`$once` (event bus pattern) removed from instances | Global event bus pattern breaks | `grep -rn '\.\$on(\|\.\$off(\|\.\$once(' src/`; migrate to `mitt` or props/emits |
| Global API (`Vue.use`, `Vue.mixin`, `Vue.component`) → app instance API | `app.use()`, `app.mixin()`, `app.component()` | `grep -rn "Vue.use(\|Vue.mixin(\|Vue.component(" src/` |
| Multiple root nodes (Fragments) allowed | Templates with a single wrapping `<div>` can be simplified (optional) | n/a — opportunity, not a blocker |
| `v-model` default prop/event renamed (`value`/`input` → `modelValue`/`update:modelValue`) | Custom `v-model` components need updating | `grep -rn "model: {" src/` |
| Vue Test Utils v1 → v2 | Different `mount`/`shallowMount` options API | `grep -rln "from '@vue/test-utils'" src/` — confirm the installed major |

## Options API → Composition API (mapping)

| Options API | Composition API equivalent |
|-----------------|-----------------|
| `data()` | `ref()` / `reactive()` |
| `computed: { x() {...} }` | `const x = computed(() => …)` |
| `methods: { m() {...} }` | `function m() {...}` (plain function in `setup`/`<script setup>`) |
| `watch: { prop(n, o) {...} }` | `watch(() => props.prop, (n, o) => {...})` |
| `created()` | top-level code in `setup()`/`<script setup>` (runs before mount) |
| `mounted()` | `onMounted(() => {...})` |
| `beforeUnmount()`/`unmounted()` | `onBeforeUnmount()` / `onUnmounted()` |
| `props` | `defineProps<Props>()` |
| `$emit` | `defineEmits<Emits>()` |
| `this.$refs.x` | `const x = ref<InstanceType<...> | null>(null)`, template `ref="x"` |

Notes:
- Mixins have no direct Composition API equivalent — extract shared logic into a **composable**
  (`use<Name>`) instead; do not port mixins mechanically.
- `data()` fields that never change belong as plain `const`, not `ref()` — don't reactivity-wrap
  everything by default.
- Error-handling hooks (`errorCaptured`) become `onErrorCaptured()` — direct 1:1 mapping.

## Vue CLI → Vite

| Vue CLI concept | Vite equivalent |
|-------------|-----------------|
| `vue-cli-service serve/build` | `vite` / `vite build` |
| `VUE_APP_*` env vars | `VITE_*` (and `import.meta.env`) |
| `public/index.html` | root `index.html` with `<script type="module" src="/src/main.ts">` |
| Jest/Karma+Mocha (via `@vue/cli-plugin-unit-*`) | Vitest (`test` block in `vite.config.ts`) |
| `configureWebpack`/`chainWebpack` in `vue.config.js` | map to Vite plugins/`resolve.alias`/`define` |
| `devServer.proxy` in `vue.config.js` | `server.proxy` in `vite.config.ts` |
| Custom webpack loaders with no Vite equivalent | **blocker** — resolve before the tooling migration |

## JS → TS (gradual, per-file)

1. Add `typescript` + `vue-tsc` + `tsconfig` with `strict: true`.
2. Convert one SFC at a time: add `lang="ts"` to its `<script>` block, type `defineProps`/`defineEmits`.
3. Convert leaf components first (fewest dependents), add types, move up the graph.
4. Track progress with the `find src -name '*.vue' | xargs grep -L 'lang="ts"' | wc -l` count from SCAN.

## Vue Test Utils v1 → Vitest + Vue Testing Library (test by test)

| VTU v1 / Karma idiom | Vitest + Vue Testing Library idiom |
|--------------|-----------|
| `shallowMount`/`mount` + `wrapper.find('.cls')` | `render` + `screen.getByRole/Text/Label` |
| `wrapper.vm.someInternalState` | assert behavior, not internals (no `.vm` access) |
| `wrapper.setProps` | `rerender` |
| `wrapper.trigger('click')` | `userEvent.click(...)` |

Vue Testing Library tests assert user-visible behavior, so they double as characterization tests for the
version/Composition-API migrations — prioritize converting the highest-traffic flows first.
