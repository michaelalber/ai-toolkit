# React App Scaffolder — Conventions, Principles & Recovery

Depth relocated from `SKILL.md`: domain principles, knowledge-base lookups, discipline
rules, the anti-pattern catalog, and error-recovery procedures. Load just-in-time.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Strict TypeScript** | `strict: true` plus `noUncheckedIndexedAccess`. Retrofitting strict mode later is expensive. | `tsconfig.json` with strict flags before any feature code |
| 2 | **Vite as Bundler** | Vite for dev server + build. Fast HMR, ESM, first-class TS. | `npm create vite@latest -- --template react-ts` |
| 3 | **Feature-Folder Layout** | `src/features/`, `src/shared/`, `src/app/`. Organized by feature from the start, not by type. | See structure below |
| 4 | **Routing Skeleton** | A typed route table with a layout route, a home route, and a 404. | `src/app/routes.tsx` |
| 5 | **Error Boundary** | A top-level error boundary in the app shell; route-level boundaries added per async area. | `src/app/ErrorBoundary.tsx` wraps the router |
| 6 | **Testing Toolchain** | Vitest + RTL + jsdom; a smoke test that renders the shell. | `vitest.config.ts`, `src/test/setup.ts` |
| 7 | **Lint & Format** | ESLint flat config (hooks + jsx-a11y + ts) and Prettier; scripts in `package.json`. | `eslint.config.js`, `.prettierrc` |
| 8 | **Env Handling** | `import.meta.env.VITE_*` typed in `vite-env.d.ts`; `.env.example` committed, `.env` gitignored. | `src/vite-env.d.ts` augmented |
| 9 | **Path Aliases** | `@/` → `src/` in both `tsconfig` and Vite, so imports are stable across moves. | `paths` + `resolve.alias` |
| 10 | **Scripts Are the Interface** | `dev`, `build`, `test`, `lint`, `format`, `typecheck` — one command each. | `package.json` scripts |
| 11 | **React Compiler by Default** | Stable since Oct 2025; auto-memoizes so `useMemo`/`useCallback`/`memo` stop being the default reflex. | `babel-plugin-react-compiler` in `vite.config.ts` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). No React corpus — cover TS/tooling; cite **react.dev** + Vite/Vitest docs.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TypeScript tsconfig strict compiler options", collection="javascript")` | At CONFIGURE — confirm strict flags |
| `search_knowledge("TypeScript module resolution path aliases", collection="javascript")` | When wiring `@/` aliases |
| `search_knowledge("WCAG landmarks skip link page structure", collection="ui_ux")` | When scaffolding the app shell/layout |
| `search_code_examples("vitest react testing library setup", language="typescript")` | When wiring the test harness |

## Scaffold Checklist (Output Template)

```markdown
## React App Scaffold: [App Name]

### Toolchain
- [ ] Vite + React + TypeScript template created
- [ ] `tsconfig` strict (+ noUncheckedIndexedAccess)
- [ ] `@/` path alias in tsconfig + vite
- [ ] ESLint flat config (react-hooks + jsx-a11y + ts)
- [ ] React Compiler wired (`babel-plugin-react-compiler` in `vite.config.ts`)
- [ ] Prettier configured
- [ ] Vitest + RTL + jsdom + setup file

### App Shell
- [ ] Router with home, layout, and 404 routes
- [ ] Top-level error boundary wrapping the router
- [ ] `shared/http` client (or placeholder) for the data layer
- [ ] `.env.example` committed; `.env` gitignored; `VITE_*` typed

### Scripts
- [ ] `dev` `build` `test` `lint` `format` `typecheck`

### Verification
- [ ] `typecheck` clean
- [ ] `lint` clean
- [ ] smoke `test` green
- [ ] `build` succeeds
```

## AI Discipline Rules

### CRITICAL: Strict TypeScript From the First Commit

**WRONG:** scaffolding with `"strict": false` "to move fast" — every later type guarantee is unreliable
and retrofitting strict mode means touching every file.

**RIGHT:** `"strict": true` (and `noUncheckedIndexedAccess`) in the initial `tsconfig`. Fix the handful
of strict errors now, not across thousands of lines later.

### REQUIRED: A Passing Smoke Test Ships With the Skeleton

The scaffold is not complete until `npm run test` passes a test that renders the app shell. An untested
skeleton invites an untested first feature.

### CRITICAL: Never Scaffold CRA; Never Clobber an Existing Project

Create React App is deprecated — Vite only for new apps. If a `package.json` exists, scaffold missing
pieces and confirm before changing anything; do not overwrite.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **`strict: false` to start** | Retrofitting strict mode is expensive | Strict from the first commit |
| 2 | **Create React App for a new app** | Deprecated, slow, unmaintained | Use Vite |
| 3 | **No test runner in the skeleton** | Tests get deferred forever | Wire Vitest + a smoke test up front |
| 4 | **Type-based folders (`components/`, `utils/`)** | Features sprawl across folders | Feature-folder layout (`features/`, `shared/`) |
| 5 | **No error boundary** | One throw blanks the whole app | Top-level boundary in the shell |
| 6 | **Secrets in `VITE_*`** | Shipped to the browser | Only public values get `VITE_`; secrets stay server-side |
| 7 | **No path alias** | Brittle `../../../` imports | `@/` alias in tsconfig + vite |
| 8 | **No lint in the skeleton** | Hook/a11y bugs accumulate | ESLint with hooks + jsx-a11y from the start |
| 9 | **Router added later** | Ad-hoc conditional rendering grows first | Router skeleton in the initial scaffold |
| 10 | **No `.env.example`** | New devs can't run it; secrets get committed | Commit `.env.example`; gitignore `.env` |

## Error Recovery

### `npm create vite` fails or network-restricted

```
Symptoms: the scaffolder cannot reach the registry.

Recovery:
1. Confirm Node ≥ 18 and registry access (npm ping).
2. If offline, create the structure manually from references/project-structure.md.
3. Pin versions in package.json and install once connectivity returns.
```

### Strict TypeScript errors on first build

```
Symptoms: tsc --noEmit reports errors immediately after scaffolding.

Recovery:
1. These are real — fix them now while the surface is tiny.
2. Do NOT set strict:false to silence them.
3. Common: add explicit types to props, narrow possibly-undefined index access.
```
