# ESLint / TypeScript baseline for the Vue checklist

The checklist treats lint + type-check as the **gate**: run these first and report failures before
applying the architectural items. Below is the minimum signal the review depends on.

## Required plugins

| Plugin | Catches |
|--------|---------|
| `eslint-plugin-vue` | template syntax errors, `v-for` key requirements, reactivity anti-patterns |
| `eslint-plugin-vuejs-accessibility` | missing labels/`alt`, non-semantic interactive elements, keyboard traps |
| `@typescript-eslint` | `no-explicit-any`, unsafe `as` casts, floating promises |
| `eslint-plugin-import` | cross-feature deep imports, cycles |

## Flat config baseline (eslint.config.js, ESLint 9+)

```js
import js from "@eslint/js";
import ts from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import vueA11y from "eslint-plugin-vuejs-accessibility";

export default [
  js.configs.recommended,
  ...ts.configs.strictTypeChecked,
  ...pluginVue.configs["flat/recommended"],
  {
    plugins: { "vuejs-accessibility": vueA11y },
    rules: {
      "vue/require-v-for-key": "error",              // missing key → Critical finding
      "vue/no-mutating-props": "error",               // mutating a prop directly
      "vue/no-side-effects-in-computed-properties": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "vuejs-accessibility/click-events-have-key-events": "warn",
    },
  },
];
```

## tsconfig signal

```jsonc
{
  "compilerOptions": {
    "strict": true,                 // missing/false → High finding (type safety value)
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true
  }
}
```

`strict: false` (or absent) is a **High** finding on its own — every other type check is unreliable
without it. Vue SFCs need `vue-tsc` (not raw `tsc`) to type-check `<template>` blocks.

## Commands the SCAN phase runs

```bash
npx eslint . --max-warnings 0     # baseline gate
npx vue-tsc --noEmit              # type gate (SFC-aware)
npx knip                          # dead exports / unused deps (Boundary & dep hygiene)
npx vite-bundle-visualizer        # bundle weight evidence (optional)
```

A destructured `reactive()` losing reactivity is **not** a clean pass — grep for the pattern and treat
each as a finding to justify or fix:

```bash
grep -rn "const { .* } = reactive(" src/
```
