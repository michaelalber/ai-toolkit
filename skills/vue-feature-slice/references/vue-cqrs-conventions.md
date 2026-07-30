# Structural CQRS in Vue — conventions

Vue has no mediator, no command bus, no DI container. CQRS here is a **naming and structural
convention** enforced by review, backed by a query layer for server state. There is no library contract
to satisfy — the discipline is the contract.

## The split

| Side | Composable shape | Owns | Returns |
|------|-----------|------|---------|
| **Query (read)** | `use<Name>Query` / `use<Name>sQuery` | a stable query key + `queryFn` | cached data (as `Ref`s), `isLoading`, `isError` |
| **Mutation (write)** | `useCreate<Name>`, `useUpdate<Name>`, `useCancel<Name>` | the mutation fn + cache invalidation | `mutate`, `isPending`, `error` |

A read composable **never mutates**. A mutation composable **never returns the list** — it invalidates
the query key so the read composable refetches. This keeps a single source of truth for server state.

## Why a query layer, not `ref` + `onMounted`

| `ref` + `onMounted` | Query layer (TanStack Query for Vue) |
|--------------------------|-------------------------------------|
| Races on fast navigation | Request dedupe + cancellation |
| Re-fetches on every mount | Caches by key; serves cache then revalidates |
| Manual loading/error flags | Built-in `isLoading`/`isError`/`isFetching` (as refs) |
| No cross-component sharing | Same key = shared data everywhere |
| No automatic refetch-on-focus | Configurable, built-in |

Server state belongs in the query layer. Client/UI state (form drafts, "is modal open") belongs in
`ref`/`reactive` or a client store (Pinia). Do not mix the two.

## Query keys

- One exported key per read composable: `export const ordersKey = ["orders"] as const;`
- Parameterized: `const orderKey = (id: string) => ["orders", id] as const;`
- Mutations invalidate the **list** key (and the item key when they change one item).

## Client state (the non-server half)

When the feature needs shared client state (not server data), use `provide`/`inject` **at the feature
root** only when prop-drilling actually hurts:

```ts
// features/cart/cart.ts
import { provide, inject, type InjectionKey } from "vue";

export const CartKey: InjectionKey<CartApi> = Symbol("cart");

export function useCart() {
  const cart = inject(CartKey);
  if (!cart) throw new Error("useCart must be called within a component that provides CartKey");
  return cart;
}
```

```vue
<!-- features/cart/CartProvider.vue -->
<script setup lang="ts">
import { provide } from "vue";
import { CartKey } from "./cart";
const cart = /* build the cart api */;
provide(CartKey, cart);
</script>
<template><slot /></template>
```

A single-consumer value stays a prop. A store/provide is justified by ≥3 levels of drilling or a real
second consumer — the same "minimal abstractions" rule as the rest of the toolkit. Pinia is the right
choice when the state is genuinely app-wide (auth session, feature flags) rather than feature-local.

## Command/query boundary checklist

- [ ] Read composables end in `Query`; write composables start with a verb (`useCreate…`).
- [ ] No composable both reads and writes.
- [ ] Mutations invalidate the relevant query key(s) on success.
- [ ] Server state is in the query layer; UI/draft state is local `ref` or a client store.
- [ ] Components consume composables; they never call the api client directly.
