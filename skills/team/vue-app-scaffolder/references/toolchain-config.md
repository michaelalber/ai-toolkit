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
    "jsx": "preserve",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src", "src/**/*.vue"]
}
```

`strict: true` is the line that matters — never ship the skeleton with it off.

## `vite.config.ts` (alias + test block)

```ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],
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
import { cleanup } from "@testing-library/vue";

afterEach(() => cleanup());
```

## `eslint.config.js` (flat config — vue + a11y + ts)

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
    files: ["**/*.{ts,vue}"],
    plugins: { "vuejs-accessibility": vueA11y },
    languageOptions: { parserOptions: { project: "./tsconfig.json" } },
    rules: {
      "vue/require-v-for-key": "error",
      "vue/no-mutating-props": "error",
      "@typescript-eslint/no-explicit-any": "error",
      ...vueA11y.configs.recommended.rules,
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
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "vue-tsc --noEmit"
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
