# ESLint / TypeScript baseline for the React checklist

The checklist treats lint + type-check as the **gate**: run these first and report failures before
applying the architectural items. Below is the minimum signal the review depends on.

## Required plugins

| Plugin | Catches |
|--------|---------|
| `eslint-plugin-react-hooks` (`recommended-latest` preset) | conditional hooks, incomplete effect dependency arrays (`exhaustive-deps`), **and** React Compiler lint rules — the standalone `eslint-plugin-react-compiler` package is legacy; its rules now ship in this plugin |
| `eslint-plugin-jsx-a11y` | missing labels/`alt`, non-semantic interactive elements, keyboard traps |
| `@typescript-eslint` | `no-explicit-any`, unsafe `as` casts, floating promises |
| `eslint-plugin-import` | cross-feature deep imports, cycles |

## Flat config baseline (eslint.config.js, ESLint 9+)

```js
import js from "@eslint/js";
import ts from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import jsxA11y from "eslint-plugin-jsx-a11y";

export default [
  js.configs.recommended,
  ...ts.configs.strictTypeChecked,
  {
    plugins: { "react-hooks": reactHooks, "jsx-a11y": jsxA11y },
    rules: {
      "react-hooks/rules-of-hooks": "error",      // conditional/looped hooks → Critical finding
      "react-hooks/exhaustive-deps": "error",     // a suppression here is itself a finding
      "@typescript-eslint/no-explicit-any": "error",
      "jsx-a11y/no-static-element-interactions": "warn",
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
without it.

## Commands the SCAN phase runs

```bash
npx eslint . --max-warnings 0     # baseline gate
npx tsc --noEmit                  # type gate
npx knip                          # dead exports / unused deps (Boundary & dep hygiene)
npx vite-bundle-visualizer        # bundle weight evidence (optional)
```

A suppressed rule (`// eslint-disable-next-line react-hooks/exhaustive-deps`) is **not** a clean pass —
grep for disables and treat each as a finding to justify or remove:

```bash
grep -rn "eslint-disable.*exhaustive-deps" src/
```
