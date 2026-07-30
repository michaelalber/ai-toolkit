# Domain Principles & Knowledge Base Lookups

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
