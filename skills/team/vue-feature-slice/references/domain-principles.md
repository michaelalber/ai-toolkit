# Domain Principles & Knowledge Base Lookups

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature is a folder with its own components, composables, data, types, and tests. No feature reaches into another feature's internals. | `features/checkout` never imports `features/cart/internal/cartMath` — only `features/cart` (barrel) or `shared/*` |
| 2 | **Data-Layer Autonomy** | Each feature's data layer (an `api.ts` + query/mutation composables) owns I/O. Components call composables; composables call the api client. | Component: `const { data } = useOrdersQuery();` — never `fetch('/api/orders')` in a component |
| 3 | **Minimal Abstractions** | Add a `provide`/`inject` context only when prop-drilling actually hurts or a real second consumer exists. A single-use value stays a prop. | Introduce a `CartKey` provide/inject when ≥3 levels drill the cart; otherwise pass props |
| 4 | **DI via Props & Provide/Inject** | Dependencies (services, config, the api client) flow through props or `provide`/`inject` — never imported as module singletons inside presentational components. | `<OrderList @select="…" />`; cross-cutting deps via `provide` at the feature root |
| 5 | **Read/Write Separation** | Queries and commands are separate composables. Structural CQRS — no library. Query composables read+cache; mutation composables mutate and invalidate. | `useOrdersQuery()`, `useOrderQuery(id)` vs `useCreateOrder()`, `useCancelOrder()` |
| 6 | **Validation at the Boundary** | Inbound form data and API responses are validated/parsed at the edge (e.g. zod) into typed models before they enter the feature. | `OrderSchema.parse(res)` in `api.ts`; the component receives a typed `Order`, never `any` JSON |
| 7 | **Presentational Purity** | Presentational components take data + emits and render. Container components/composables own state and effects. | `OrderListView` (pure) vs `OrderList` (wires the query composable to the view) |
| 8 | **Component Thinness** | A component renders; logic lives in composables. If a component's `<script setup>` grows branching business logic, extract a composable. | `useCheckout()` holds the flow; `<Checkout/>` renders its result |
| 9 | **Strict Typing** | `strict: true`; `defineProps<Props>()` explicit; API models typed; no untyped `any` crossing a boundary. | `defineProps<{ orders: Order[]; onSelect: (id: string) => void }>()` |
| 10 | **Test Proximity** | Tests live beside the slice. Component tests render the SFC; composable tests call the function directly (composables are just functions outside setup, or wrapped with a test host component). | `features/orders/OrderList.test.ts`, `features/orders/useCreateOrder.test.ts` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions. The KB has a Vue 2/3 corpus under
`collection="javascript"` (alongside TypeScript) — these queries cover TypeScript and accessible UI;
cite **vuejs.org** for Vue-specific patterns.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("TypeScript discriminated unions narrowing", collection="javascript")` | When typing feature models and state |
| `search_knowledge("Vue composition API composables TypeScript", collection="javascript")` | When typing composables and props |
| `search_knowledge("accessible component keyboard focus", collection="ui_ux")` | When scaffolding interactive presentational components |
| `search_knowledge("WCAG form labels error messaging", collection="ui_ux")` | When the slice includes a form |
| `search_code_examples("vue composable data fetching", language="typescript")` | When generating query/mutation composable skeletons |
