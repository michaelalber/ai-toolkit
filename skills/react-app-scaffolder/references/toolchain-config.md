# Toolchain config — tsconfig, eslint, vitest, scripts

The non-negotiable config that makes the skeleton strict, tested, and linted from the first commit.

## `tsconfig.json` (strict)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"]
}
```

`strict: true` is the line that matters — never ship the skeleton with it off.

## `vite.config.ts` (alias + test block)

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [
    react({ babel: { plugins: ["babel-plugin-react-compiler"] } }),
  ],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true,
  },
});
```

## `src/test/setup.ts`

```ts
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => cleanup());
```

## `eslint.config.js` (flat config — hooks + a11y + ts)

```js
import js from "@eslint/js";
import ts from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import jsxA11y from "eslint-plugin-jsx-a11y";

export default [
  js.configs.recommended,
  ...ts.configs.strictTypeChecked,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: { "react-hooks": reactHooks, "jsx-a11y": jsxA11y },
    languageOptions: { parserOptions: { project: "./tsconfig.json" } },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",
      "@typescript-eslint/no-explicit-any": "error",
      ...jsxA11y.configs.recommended.rules,
    },
  },
];
```

## `.prettierrc`

```json
{ "singleQuote": false, "semi": true, "trailingComma": "all", "printWidth": 100 }
```

## `package.json` scripts

```jsonc
{
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit"
  }
}
```

Each command is the single interface for its job. `build` runs `typecheck` first so a type error can
never reach a production bundle.

## `.gitignore` additions

```
node_modules
dist
.env
*.local
```

`.env` is gitignored; `.env.example` is committed. Secrets never enter the repo or a `VITE_*` var.

## React Compiler

`babel-plugin-react-compiler` (wired above) auto-memoizes the component tree at build time — do not
also install the standalone `eslint-plugin-react-compiler` package; its lint rules now ship inside
`eslint-plugin-react-hooks`'s `recommended-latest` preset, which the flat config above already pulls
in via `react-hooks/*` rules. Verify in React DevTools: compiled components show a "Memo ✨" badge.
