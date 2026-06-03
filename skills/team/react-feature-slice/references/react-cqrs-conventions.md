# Structural CQRS in React — conventions

React has no mediator, no command bus, no DI container. CQRS here is a **naming and structural
convention** enforced by review, backed by a query cache for server state. There is no library contract
to satisfy — the discipline is the contract.

## The split

| Side | Hook shape | Owns | Returns |
|------|-----------|------|---------|
| **Query (read)** | `use<Name>Query` / `use<Name>sQuery` | a stable query key + `queryFn` | cached data, `isLoading`, `isError` |
| **Mutation (write)** | `useCreate<Name>`, `useUpdate<Name>`, `useCancel<Name>` | the mutation fn + cache invalidation | `mutate`, `isPending`, `error` |

A read hook **never mutates**. A mutation hook **never returns the list** — it invalidates the query key
so the read hook refetches. This keeps a single source of truth for server state.

## Why a query cache, not `useState` + `useEffect`

| `useState` + `useEffect` | Query cache (TanStack / RTK Query) |
|--------------------------|-------------------------------------|
| Races on fast navigation | Request dedupe + cancellation |
| Re-fetches on every mount | Caches by key; serves cache then revalidates |
| Manual loading/error flags | Built-in `isLoading`/`isError`/`isFetching` |
| StrictMode double-fetch | Handled by the cache |
| No cross-component sharing | Same key = shared data everywhere |

Server state belongs in the cache. Client/UI state (form drafts, "is modal open") belongs in `useState`
or a client store (Zustand / RTK). Do not mix the two.

## Query keys

- One exported key per read hook: `export const ordersKey = ["orders"] as const;`
- Parameterized: `const orderKey = (id: string) => ["orders", id] as const;`
- Mutations invalidate the **list** key (and the item key when they change one item).

## Client state (the non-server half)

When the feature needs shared client state (not server data), introduce a provider **at the feature root**
only when prop-drilling actually hurts:

```tsx
// features/cart/CartProvider.tsx
const CartContext = createContext<CartApi | null>(null);
export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within <CartProvider>");
  return ctx;
}
```

A single-consumer value stays a prop. A store/provider is justified by ≥3 levels of drilling or a real
second consumer — the same "minimal abstractions" rule as the rest of the toolkit.

## Command/query boundary checklist

- [ ] Read hooks end in `Query`; write hooks start with a verb (`useCreate…`).
- [ ] No hook both reads and writes.
- [ ] Mutations invalidate the relevant query key(s) on success.
- [ ] Server state is in the cache; UI/draft state is local or in a client store.
- [ ] Components consume hooks; they never call the api client directly.
