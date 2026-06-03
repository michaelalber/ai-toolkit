# React review checklist — section by section

Full expansion of the 8 checklist items. Each row is a concrete thing to grep/read for, the severity,
and the version note that gates the recommendation.

## 1. Hooks rules (Critical)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| Hook call inside `if`/`for`/`&&`/early return | Breaks the hook-order invariant; React throws or silently corrupts state | Move the hook to the top level; branch on its result, not around its call |
| Custom hook not prefixed `use` | Lint can't enforce the rules of hooks | Rename `getUser()` → `useUser()` |
| Hook called from a non-component / non-hook | Rules of hooks only hold in components/hooks | Extract into a hook or a plain function |

```bash
grep -rn "if (.*) {[^}]*use[A-Z]" src/   # heuristic for conditional hooks
```

## 2. Effect correctness (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `// eslint-disable ... exhaustive-deps` | Hides a stale-closure bug | Add the missing dep, or restructure (e.g. `useReducer`, functional updates) |
| `useEffect` with no cleanup for a subscription/timer/listener | Leak; double-fire under StrictMode | Return a cleanup function |
| `useEffect` that only computes derived state | Extra render, stale values | Compute during render or with `useMemo` |
| Data fetching in `useEffect` + `useState` everywhere | Race conditions, no caching/dedupe | Use a query cache (TanStack Query / RTK Query) for server state |

## 3. Component cohesion (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| Component file > ~250 lines or > ~3 responsibilities | Hard to test/reuse; merge-conflict magnet | Split presentation from data/logic; extract sub-components |
| Business logic inline in JSX | Untestable | Move to a custom hook or service |

## 4. State placement (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| Prop drilled > ~3 levels | Fragile, noisy refactors | Lift to context or a store slice |
| Global store holding ephemeral UI state (e.g. "is dropdown open") | Bloats global state, couples unrelated UI | Keep local `useState` |
| Server data mirrored into Redux via effects | Cache invalidation reinvented badly | Server state → query cache; client state → store/local |

## 5. Render performance (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `key={index}` on a reorderable/dynamic list | Wrong reconciliation, state bleed | Use a stable id |
| New `{}` / `[]` / `() => …` passed to a `memo`-wrapped child | Defeats the memo | `useMemo`/`useCallback` the value, or drop the premature `memo` |
| `memo`/`useMemo` everywhere with no measured cause | Complexity with no benefit | Remove; memoize only measured hot paths |

## 6. Type safety (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `strict: false`/absent in tsconfig | Every other check is unreliable | Enable `strict` |
| `any` / untyped props | No compile-time safety | Type props; replace `any` with the real shape or `unknown` + narrowing |
| `as SomeType` casts | Hides shape mismatches | Validate at the boundary (e.g. zod) and infer |

## 7. Accessibility (High)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `<div onClick>` for actions | Not keyboard/AT reachable | Use `<button>`; add `onKeyDown` only if a non-button is unavoidable |
| Missing `alt` / form label / `aria-*` | Screen-reader users blocked | Add labels; run `eslint-plugin-jsx-a11y`; reference WCAG 2.2 via `collection="ui_ux"` |

## 8. Boundary & dependency hygiene (Medium)

| Look for | Why it fails | Recommendation |
|----------|--------------|----------------|
| `import ../otherFeature/internal` | Cross-feature coupling | Import only the feature's barrel (`features/x`), or shared code |
| Presentation component calling `fetch` directly | Couples UI to transport | Move to a hook/service in the feature's data layer |
| No error boundary around async/suspense UI | One throw blanks the app | Wrap routes/async subtrees in an error boundary |
| Heavy dep for a trivial need (e.g. moment for one format) | Bundle bloat | `knip` + bundle visualizer; replace or drop |

## Version gates

| Recommendation | Min React |
|----------------|-----------|
| `useTransition`, automatic batching, Suspense for data | 18 |
| Actions, `useActionState`, `use()`, `ref` as a prop | 19 |
| Server Components | 18+ with a framework (Next.js App Router) |

Never recommend an API the detected version lacks.
