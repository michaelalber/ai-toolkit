---
name: react-app-scaffolder
audience: team
description: Scaffolds a production-ready React + TypeScript application skeleton with Vite, a router, strict TypeScript, Vitest + React Testing Library, ESLint (hooks + jsx-a11y), Prettier, environment handling, an error boundary, and a feature-folder layout. React analog of an app/project scaffolder. Use when starting a new React app, bootstrapping a Vite + React + TypeScript project, setting up the testing/lint toolchain, or establishing the base folder structure and app shell. Triggers on phrases like "scaffold react app", "new react project", "bootstrap react typescript", "create vite react app", "set up react project", "react app skeleton", "react project structure".
---

# React App Scaffolder

> "Make the right thing the easy thing. A project's defaults become its culture."
> -- Adapted from engineering practice

> "Strict from day one is cheaper than strict retrofitted."
> -- Adapted from TypeScript adoption experience

## Core Philosophy

The first commit sets the project's defaults, and defaults are sticky: a project that starts without
`strict` TypeScript, without a test runner, or without lint rarely gains them later without pain. This
skill stands up the skeleton with the non-negotiables already on — strict types, Vitest, ESLint with the
hooks and a11y plugins, a router, an error boundary, and a feature-folder layout — so the first real
feature drops into a structured, tested, type-safe project.

Vite is the default bundler (fast, modern, ESM-native). Create React App is deprecated and is never the
target for a new project — if an existing CRA app is in play, route to `react-modernization-analyzer`.

> **Grounding note:** the KB has no React corpus. Use `collection="javascript"` for TS/tooling and cite
> **react.dev** / Vite + Vitest docs as the authority. Never invent a `react` collection.

**Non-Negotiable Constraints:**
1. **Vite + TypeScript `strict`** — `strict: true` in `tsconfig` from the first commit
2. **Test runner wired** — Vitest + React Testing Library with a `test` script and a passing smoke test
3. **Lint + format wired** — ESLint (react-hooks + jsx-a11y) and Prettier with scripts
4. **Router from the start** — a router with a typed route table and a not-found route
5. **Error boundary at the shell** — a top-level error boundary so one throw does not blank the app
6. **Env via Vite convention** — only `VITE_*` exposed to the client; secrets stay server-side

**What this skill is NOT:**
- It is NOT a feature generator — use `react-feature-slice` / `react-component-scaffolder` for that
- It is NOT a deployment/CI guide — it covers the application skeleton; CI is a follow-up
- It is NOT a styling-framework decision — leave styling choice to the team

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

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp). No React corpus — cover TS/tooling; cite **react.dev** + Vite/Vitest docs.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TypeScript tsconfig strict compiler options", collection="javascript")` | At CONFIGURE — confirm strict flags |
| `search_knowledge("TypeScript module resolution path aliases", collection="javascript")` | When wiring `@/` aliases |
| `search_knowledge("WCAG landmarks skip link page structure", collection="ui_ux")` | When scaffolding the app shell/layout |
| `search_code_examples("vitest react testing library setup", language="typescript")` | When wiring the test harness |

## Workflow

### Phase 1: DETECT

```bash
node -v && npm -v
ls package.json 2>/dev/null && echo "existing project — confirm before overwriting"
# If a Create React App project exists, STOP and route to react-modernization-analyzer.
grep -l "react-scripts" package.json 2>/dev/null && echo "CRA detected → modernization, not fresh scaffold"
```

If `package.json` already exists, do not clobber it — scaffold missing pieces only, and confirm first.

### Phase 2: CREATE

```bash
npm create vite@latest <app-name> -- --template react-ts
cd <app-name>
npm install
npm install -D vitest @testing-library/react @testing-library/user-event jsdom \
  eslint-plugin-react-hooks eslint-plugin-jsx-a11y prettier
npm install react-router-dom
```

### Phase 3: CONFIGURE

Apply the structure and config. See `references/project-structure.md` for full file contents.

```
src/
  app/
    App.tsx            # shell: providers + router + error boundary
    routes.tsx         # typed route table (home, layout, 404)
    ErrorBoundary.tsx  # top-level error boundary
  features/            # feature slices land here (react-feature-slice)
  shared/              # cross-cutting UI + utilities (http client, etc.)
  test/setup.ts        # RTL + jest-dom setup
  main.tsx             # createRoot
  vite-env.d.ts        # typed VITE_* env
eslint.config.js
vitest.config.ts
.env.example
.prettierrc
tsconfig.json          # strict
```

See `references/toolchain-config.md` for `tsconfig`, `eslint.config.js`, `vitest.config.ts`, and scripts.

### Phase 4: VERIFY

```bash
npm run typecheck      # tsc --noEmit, strict
npm run lint           # eslint clean
npm run test           # smoke test green
npm run build          # production build succeeds
npm run dev            # dev server boots
```

## State Block

```xml
<react-app-scaffold-state>
  phase: DETECT | CREATE | CONFIGURE | VERIFY | COMPLETE
  app_name: [name]
  existing_project: true | false
  cra_detected: true | false
  strict_ts: true | false
  router_configured: true | false
  test_harness_configured: true | false
  lint_configured: true | false
  error_boundary_added: true | false
  last_action: [description]
  next_action: [description]
</react-app-scaffold-state>
```

## Output Templates

### Scaffold Checklist

```markdown
## React App Scaffold: [App Name]

### Toolchain
- [ ] Vite + React + TypeScript template created
- [ ] `tsconfig` strict (+ noUncheckedIndexedAccess)
- [ ] `@/` path alias in tsconfig + vite
- [ ] ESLint flat config (react-hooks + jsx-a11y + ts)
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

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `react-feature-slice` | The first thing to use after the skeleton — adds feature slices into `src/features/`. |
| `react-component-scaffolder` | Generates individual components/routes within the scaffolded app. |
| `react-modernization-analyzer` | For an existing CRA / legacy app, assess and plan the move to this Vite skeleton instead of scaffolding fresh. |
| `react-security-review` | Run once features land to verify CSP, env exposure, and dependency posture. |
| `tdd` | Drive the first features test-first on top of the scaffolded Vitest harness. |
