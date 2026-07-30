# Vue Component Scaffolder — Conventions, Discipline & Recovery

Depth relocated from `SKILL.md`: domain principles, KB lookups, AI discipline rules,
anti-patterns, and error-recovery procedures.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Explicit Props Contract** | Every component declares props via `defineProps<Props>()`. Optional props have defaults via `withDefaults`; emits are typed. | `defineProps<{ label: string; disabled?: boolean }>()` |
| 2 | **Presentational vs Container** | A presentational component is pure (props in, template out). A container wires data/state to a presentational child. Default to presentational. | `UserCard` (pure) vs `UserCardContainer` (uses a query composable) |
| 3 | **Accessibility Baseline** | Semantic element first; interactive elements are real `<button>`/`<a>`; images have `alt`; inputs have labels. | `<button type="button">` not `<div role="button">` |
| 4 | **Controlled by Default** | Form inputs are controlled via `v-model` unless there is a measured reason to use a template ref directly. | `<input v-model="value" />` |
| 5 | **Composition over Props Explosion** | When a component sprouts many boolean props, prefer `<slot>`s or splitting it. | `<Card><template #header>…</template></Card>` over 8 `show*` flags |
| 6 | **Stable Identity** | List items use stable `:key`s; expensive derived values use `computed`, not a recomputed method call in the template. | `:key="item.id"`, not `:key="index"` |
| 7 | **Test the Behavior** | The component test renders the SFC and asserts user-visible behavior via roles/text, not implementation. | `screen.getByRole("button", { name: /save/ })` |
| 8 | **Story for the Surface** | A Storybook story (optional) documents the props surface and edge states (loading, empty, error). | `Default`, `Loading`, `Empty`, `Error` stories |
| 9 | **No Silent `any`** | Props, emits, and refs are typed. `any` requires a written justification. | `defineEmits<{ change: [e: Event] }>()` |
| 10 | **Errors Surface** | Async/container components render an error state and (where relevant) sit under `onErrorCaptured`. | `<p v-if="isError" role="alert">…</p>` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). The KB has a Vue 2/3 corpus under `collection="javascript"`
(alongside TS) — these cover TS + accessible UI; cite **vuejs.org**.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("WCAG button link semantics keyboard", collection="ui_ux")` | At SCAFFOLD — confirm the accessible element for the interaction |
| `search_knowledge("WCAG form label error association", collection="ui_ux")` | When the component is a form/input |
| `search_knowledge("Vue TypeScript defineProps defineEmits generics", collection="javascript")` | When typing props and emits |
| `search_code_examples("vue testing library user event", language="typescript")` | When generating the component test |

## AI Discipline Rules

### CRITICAL: Typed Props, No Implicit `any`

**WRONG:**
```vue
<script setup>
defineProps(["text"])                          // untyped props array
</script>
<template><span>{{ text }}</span></template>
```

**RIGHT:**
```vue
<script setup lang="ts">
withDefaults(defineProps<{ text: string; tone?: "info" | "warn" }>(), { tone: "info" });
</script>
<template><span :class="`badge badge--${tone}`">{{ text }}</span></template>
```

### REQUIRED: Accessible Interactive Elements

**WRONG:**
```vue
<div @click="onSave">Save</div>             <!-- not keyboard/AT reachable -->
```

**RIGHT:**
```vue
<button type="button" @click="onSave">Save</button>
```

### CRITICAL: A Test Ships With the Component

The `*.test.ts` is created in the same step as the component. A component without a co-located test is
an incomplete scaffold — never defer it.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Untyped / implicit `any` props** | No compile-time safety; bad autocomplete | Declare `defineProps<Props>()` |
| 2 | **`<div @click>` for actions** | Not keyboard/screen-reader reachable | Use `<button>`/`<a>` |
| 3 | **No co-located test** | Behavior unverified; regressions slip in | Create `*.test.ts` with the component |
| 4 | **Data fetching in a presentational component** | Couples UI to transport; hard to test | Fetch in a container/composable; pass data as props |
| 5 | **Boolean-prop explosion** | Unreadable, combinatorial states | Compose with `<slot>`s or split |
| 6 | **Uncontrolled inputs by default** | State drifts from the DOM | `v-model`-controlled inputs |
| 7 | **Testing implementation details** | Brittle tests break on refactor | Query by role/text; assert user-visible behavior |
| 8 | **`:key="index"` on dynamic lists** | Wrong reconciliation | Stable id key |
| 9 | **Method calls for derived values in the template** | Recomputed every render, no caching | `computed` the value |
| 10 | **Missing error/empty states** | Blank UI on failure | Render explicit empty/error states |

## Error Recovery

### `vuejs-accessibility` flags an interactive element

```
Symptoms: eslint-plugin-vuejs-accessibility errors on a clickable div/span.

Recovery:
1. Replace with the semantic element (<button>/<a>).
2. If a non-semantic element is truly required, add role + tabindex + @keydown and document why.
3. Re-run eslint until clean.
```

### Component test cannot find an element

```
Symptoms: getByRole/getByLabelText throws "unable to find".

Recovery:
1. Prefer getByRole with an accessible name — if it is missing, the component has an a11y gap, not just a test gap.
2. Add the label/aria-label to the component (fixes both the test and accessibility).
3. Use screen.debug() to inspect the rendered tree.
```

## Output: Scaffold Checklist

```markdown
## Vue Component Scaffold: [Component Name]

### Contract
- [ ] `defineProps<Props>()` declared (no implicit `any`)
- [ ] Optional props have defaults via `withDefaults`; emits typed
- [ ] Kind chosen: presentational / container / form / route

### Accessibility
- [ ] Semantic element used (button/link/heading/list)
- [ ] Labels / `alt` / ARIA where needed
- [ ] Keyboard reachable; focus visible
- [ ] `eslint-plugin-vuejs-accessibility` clean

### Tests
- [ ] Component test co-located; asserts behavior via roles/text
- [ ] Edge states covered (empty / loading / error) where relevant

### Story (optional)
- [ ] Default + edge-state stories

### Verification
- [ ] `vue-tsc --noEmit` clean
- [ ] `eslint` clean
- [ ] `vitest` green
```
