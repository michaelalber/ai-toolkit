---
name: react-feature-slice
audience: team
description: Scaffolds feature-based React / TypeScript architecture using feature folders, presentational + container components, custom hooks, a typed data layer, and structural CQRS (query hooks vs mutation hooks). React analog of dotnet-vertical-slice and python-feature-slice — no DI framework; uses props/context for dependency injection and a query cache for server state. Use when creating feature-based React projects, adding React features, organizing components by feature rather than by technical type, or scaffolding a feature's data layer. Triggers on phrases like "scaffold react feature", "create react slice", "react feature folder", "react vertical slice", "add react feature", "react feature architecture", "organize react by feature".
---

# React Feature Slice Architecture

> "The best code is code that never has to be written."
> -- Jeff Atwood

> "Organize around business capabilities, not technical layers."
> -- Sam Newman, *Building Microservices*

## Core Philosophy

Feature slice architecture organizes code by feature, not by technical type. The default React tutorial
layout — `components/`, `hooks/`, `utils/`, `services/` — spreads one feature across many directories,
so adding "checkout" means touching five folders. This skill replaces that with self-contained vertical
slices: `features/cart/`, `features/checkout/`, each owning its full stack — components, hooks, data layer,
types, and tests.

React has no mediator and no DI container. **Dependency injection is props and context**; the container
resolves nothing for you. **CQRS is a structural and naming convention** — read hooks (`useOrdersQuery`)
versus mutation hooks (`useCreateOrder`) — backed by a query cache (TanStack Query / RTK Query) for server
state, never a library contract.

> **Grounding note:** the KB has no React corpus. Use `collection="javascript"` for TS, `collection="ui_ux"`
> for accessible component design, and cite **react.dev** for hooks/component patterns. Never invent a `react` collection.

**Non-Negotiable Constraints:**
1. **TypeScript `strict`** — every component, hook, and prop is typed; no `any` without justification
2. **Feature isolation** — no cross-feature imports; features communicate through `shared/` or composition only
3. **Data layer owns I/O** — components do not call `fetch`; query/mutation hooks do
4. **Server state in a query cache** — never `useState` + `useEffect` for server data
5. **Presentational components are pure** — they receive data and callbacks via props; no data fetching inside
6. **Barrel exports define the public surface** — other features import only the feature's `index.ts`

**What this skill is NOT:**
- It is NOT a microservices or micro-frontend guide — slices live within one React app
- It is NOT prescriptive about a state library — Context, Zustand, or RTK all fit the conventions
- It is NOT a styling system — bring your own (CSS Modules, Tailwind, etc.)

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature is a folder with its own components, hooks, data, types, and tests. No feature reaches into another feature's internals. | `features/checkout` never imports `features/cart/internal/cartMath` — only `features/cart` (barrel) or `shared/*` |
| 2 | **Data-Layer Autonomy** | Each feature's data layer (an `api.ts` + query/mutation hooks) owns I/O. Components call hooks; hooks call the api client. | Component: `const { data } = useOrdersQuery();` — never `fetch('/api/orders')` in a component |
| 3 | **Minimal Abstractions** | Add a context/provider only when prop-drilling actually hurts or a real second consumer exists. A single-use value stays a prop. | Introduce `CartProvider` when ≥3 levels drill the cart; otherwise pass props |
| 4 | **DI via Props & Context** | Dependencies (services, config, the api client) flow through props or a context provider — never imported as module singletons inside presentational components. | `<OrderList onSelect={…} />`; cross-cutting deps via a provider at the feature root |
| 5 | **Read/Write Separation** | Queries and commands are separate hooks. Structural CQRS — no library. Query hooks read+cache; mutation hooks mutate and invalidate. | `useOrdersQuery()`, `useOrderQuery(id)` vs `useCreateOrder()`, `useCancelOrder()` |
| 6 | **Validation at the Boundary** | Inbound form data and API responses are validated/parsed at the edge (e.g. zod) into typed models before they enter the feature. | `OrderSchema.parse(res)` in `api.ts`; the component receives a typed `Order`, never `any` JSON |
| 7 | **Presentational Purity** | Presentational components take data + callbacks and render. Container components/hooks own state and effects. | `OrderListView` (pure) vs `OrderList` (wires the query hook to the view) |
| 8 | **Component Thinness** | A component renders; logic lives in hooks. If a component body grows branching business logic, extract a hook. | `useCheckout()` holds the flow; `<Checkout/>` renders its result |
| 9 | **Strict Typing** | `strict: true`; props interfaces explicit; API models typed; no untyped `any` crossing a boundary. | `type OrderListProps = { orders: Order[]; onSelect: (id: string) => void }` |
| 10 | **Test Proximity** | Tests live beside the slice. RTL tests render the component; hook tests use `renderHook`. | `features/orders/OrderList.test.tsx`, `features/orders/useCreateOrder.test.ts` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions. The KB has no React corpus — these queries
cover TypeScript and accessible UI; cite **react.dev** for React-specific patterns.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TypeScript discriminated unions narrowing", collection="javascript")` | When typing feature models and state |
| `search_knowledge("TypeScript strict generics utility types", collection="javascript")` | When typing hooks and props |
| `search_knowledge("accessible component keyboard focus", collection="ui_ux")` | When scaffolding interactive presentational components |
| `search_knowledge("WCAG form labels error messaging", collection="ui_ux")` | When the slice includes a form |
| `search_code_examples("react custom hook data fetching", language="typescript")` | When generating query/mutation hook skeletons |

## Workflow

### Phase 1: DETECT

**Objective:** Understand the existing structure before scaffolding.

```bash
# React + tooling versions
grep -E '"(react|typescript|vite|next|@reduxjs/toolkit|zustand|@tanstack/react-query)"' package.json

# TypeScript strictness
grep -n '"strict"' tsconfig*.json

# Existing layout — type-based, feature-based, or mixed
find src -type d -maxdepth 2 | head -30

# Existing data-fetching pattern
grep -rn "useQuery\|createApi\|fetch(\|axios" src/ | head -20
```

Record: React version, bundler (Vite/CRA/Next), TS strict on/off, state/query libraries, current layout, router.

### Phase 2: SCAFFOLD

Create the feature folder. See `references/feature-folder-template.md` for file-by-file content.

```
src/features/<name>/
  components/<Name>List.tsx        # container: wires hooks → view
  components/<Name>ListView.tsx    # presentational: props in, JSX out
  components/<Name>Form.tsx        # form with boundary validation
  hooks/use<Name>sQuery.ts          # read (query hook)
  hooks/useCreate<Name>.ts          # write (mutation hook)
  data/api.ts                       # api client + zod parse; the only I/O
  data/schema.ts                    # zod schemas + inferred types
  types.ts                          # feature-local types
  index.ts                          # barrel: the feature's public surface
  <Name>List.test.tsx               # RTL test
  hooks/useCreate<Name>.test.ts     # hook test
```

### Phase 3: WIRE

Register the slice with the router and (only if shared) a context provider.

```tsx
// app/routes.tsx
import { OrdersPage } from "@/features/orders";   // barrel import only
{ path: "/orders", element: <OrdersPage /> }

// Provider only when prop-drilling earns it:
// <CartProvider> wraps the subtree that needs it, at the feature root.
```

### Phase 4: VERIFY

```bash
npx tsc --noEmit                                 # types clean
npx eslint src/features/<name>                    # incl. hooks + a11y rules
npx vitest run src/features/<name>                # slice tests green
# Cross-feature import check — should print nothing:
grep -rn "features/" "src/features/<name>" | grep -v "features/<name>"
```

## State Block

```xml
<react-feature-slice-state>
  phase: DETECT | SCAFFOLD | WIRE | VERIFY | COMPLETE
  feature_name: [name]
  react_version: [detected]
  existing_structure: type-based | feature-based | mixed | unknown
  query_lib: tanstack | rtk-query | none
  route_registered: true | false
  query_hook_created: true | false
  mutation_hook_created: true | false
  tests_scaffolded: true | false
  last_action: [description]
  next_action: [description]
</react-feature-slice-state>
```

## Output Templates

### Feature Slice Scaffold: [Feature Name]

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `src/features/<name>/components/<Name>List.tsx` (container)
- [ ] `src/features/<name>/components/<Name>ListView.tsx` (presentational)
- [ ] `src/features/<name>/components/<Name>Form.tsx`
- [ ] `src/features/<name>/hooks/use<Name>sQuery.ts` (read)
- [ ] `src/features/<name>/hooks/useCreate<Name>.ts` (write)
- [ ] `src/features/<name>/data/api.ts`
- [ ] `src/features/<name>/data/schema.ts`
- [ ] `src/features/<name>/types.ts`
- [ ] `src/features/<name>/index.ts` (barrel)
- [ ] `src/features/<name>/<Name>List.test.tsx`
- [ ] `src/features/<name>/hooks/useCreate<Name>.test.ts`

### Wiring
- [ ] Route registered via the barrel import
- [ ] Provider added only if prop-drilling warranted it

### Verification
- [ ] `tsc --noEmit` clean
- [ ] `eslint` clean (hooks + a11y)
- [ ] `vitest` green for the slice
- [ ] No cross-feature imports detected
```

### Feature Folder Diagram

```
src/
├── features/
│   └── orders/
│       ├── components/
│       │   ├── OrderList.tsx        ← container: hook → view
│       │   ├── OrderListView.tsx    ← presentational (pure)
│       │   └── OrderForm.tsx        ← boundary validation
│       ├── hooks/
│       │   ├── useOrdersQuery.ts     ← read
│       │   └── useCreateOrder.ts     ← write (invalidates cache)
│       ├── data/
│       │   ├── api.ts                ← the only I/O
│       │   └── schema.ts             ← zod + inferred types
│       ├── types.ts
│       └── index.ts                  ← barrel (public surface)
├── shared/                           ← cross-cutting code & UI primitives
└── app/routes.tsx                    ← imports feature barrels only
```

## AI Discipline Rules

### CRITICAL: No Data Fetching in Components

**WRONG:**
```tsx
function OrderList() {
  const [orders, setOrders] = useState<any[]>([]);          // untyped server state
  useEffect(() => { fetch("/api/orders").then(r => r.json()).then(setOrders); }, []); // race, no cache
  return <ul>{orders.map(o => <li key={o.id}>{o.total}</li>)}</ul>;
}
```

**RIGHT:**
```tsx
function OrderList() {
  const { data: orders = [], isLoading } = useOrdersQuery();  // query hook owns I/O + cache
  if (isLoading) return <Spinner />;
  return <OrderListView orders={orders} onSelect={…} />;       // presentational view
}
```

### REQUIRED: Validate at the Boundary

```ts
// data/schema.ts
export const OrderSchema = z.object({ id: z.string(), total: z.number() });
export type Order = z.infer<typeof OrderSchema>;

// data/api.ts — parse before the data enters the feature
export async function fetchOrders(): Promise<Order[]> {
  const res = await http.get("/api/orders");
  return z.array(OrderSchema).parse(res.data);   // typed Order[], never `any` JSON
}
```

### CRITICAL: No Cross-Feature Imports

```ts
// WRONG — in src/features/checkout/hooks/useCheckout.ts
import { cartTotal } from "@/features/cart/internal/cartMath";   // reaching into internals

// RIGHT — import the feature's barrel, or shared code
import { useCart } from "@/features/cart";        // public surface
import { formatMoney } from "@/shared/money";
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **`fetch` inside a component** | Races, no cache, untestable | Move I/O to a query/mutation hook + api client |
| 2 | **Server state in `useState`+`useEffect`** | Re-implements caching badly; stale data | Use a query cache (TanStack/RTK Query) |
| 3 | **Cross-feature deep imports** | Hidden coupling; one feature breaks another | Import the barrel, or move code to `shared/` |
| 4 | **`any` on props or API data** | No type safety; bugs surface at runtime | Type props; parse API data with zod at the boundary |
| 5 | **God component** | 300-line component mixing fetch, state, render | Split container/presentational; extract hooks |
| 6 | **Business logic in JSX** | Untestable, unreadable | Move to a custom hook |
| 7 | **Global store for ephemeral UI state** | Couples unrelated UI; bloats store | Keep local `useState` |
| 8 | **No barrel / importing internals** | Public surface undefined; refactors break consumers | Export the public API from `index.ts` |
| 9 | **`key={index}` on dynamic lists** | Wrong reconciliation, state bleed | Use a stable id |
| 10 | **Tests far from the slice** | Drift; orphaned tests | Co-locate `*.test.tsx` beside the component/hook |

## Error Recovery

### Cross-feature import detected

```
Symptoms: grep for `features/` inside one slice returns another feature's path.

Recovery:
1. Identify what is imported (a util, a type, a component).
2. Shared util/type/primitive → move to src/shared and update both slices.
3. Feature behavior → import the other feature's barrel (public surface), not its internals.
4. Re-run the grep check until it prints nothing.
```

### Component grows too large

```
Symptoms: a component exceeds ~250 lines or mixes fetching, state, and presentation.

Recovery:
1. Extract data/state into a custom hook (use<Name>).
2. Split the render into a pure presentational view component.
3. The container becomes: call hook → pass props to the view.
```

### Server data is stale or double-fetched

```
Symptoms: data does not refresh after a mutation, or fetches fire twice under StrictMode.

Recovery:
1. Move the fetch into a query hook with a stable query key.
2. In the mutation hook, invalidate that query key on success.
3. Remove the useEffect-based fetch; StrictMode double-invoke is then handled by the cache.
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `react-component-scaffolder` | Component-level quality (props typing, RTL test, story, a11y). Use to generate the individual components inside a slice. |
| `react-app-scaffolder` | When there is no app yet, scaffold the Vite + TS + router + Vitest skeleton first, then add slices. |
| `react-security-review` | After scaffolding, audit the slice's boundary validation, link/URL handling, and token usage against OWASP. |
| `react-architecture-checklist` | Architecture quality gate. Run after several slices to verify isolation, hooks discipline, and coupling. |
| `tdd` | Drive each hook and component test-first (RED → GREEN → REFACTOR) rather than scaffolding code ahead of tests. |
