# AI Discipline Rules, Anti-Patterns & Error Recovery

## AI Discipline Rules

### CRITICAL: No Data Fetching in Components

**WRONG:**
```vue
<script setup lang="ts">
import { ref, onMounted } from "vue";
const orders = ref<any[]>([]);                                    // untyped server state
onMounted(async () => {
  const res = await fetch("/api/orders");                          // race, no cache
  orders.value = await res.json();
});
</script>
<template>
  <ul><li v-for="o in orders" :key="o.id">{{ o.total }}</li></ul>
</template>
```

**RIGHT:**
```vue
<script setup lang="ts">
import { useOrdersQuery } from "../composables/useOrdersQuery"; // composable owns I/O + cache
import { OrderListView } from "./OrderListView.vue";
const { data: orders, isLoading } = useOrdersQuery();
</script>
<template>
  <Spinner v-if="isLoading" />
  <OrderListView v-else :orders="orders ?? []" @select="…" />    <!-- presentational view -->
</template>
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
// WRONG — in src/features/checkout/composables/useCheckout.ts
import { cartTotal } from "@/features/cart/internal/cartMath";   // reaching into internals

// RIGHT — import the feature's barrel, or shared code
import { useCart } from "@/features/cart";        // public surface
import { formatMoney } from "@/shared/money";
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **`fetch` inside a component** | Races, no cache, untestable | Move I/O to a query/mutation composable + api client |
| 2 | **Server state in `ref` + `onMounted`** | Re-implements caching badly; stale data | Use a query layer (TanStack Query for Vue) |
| 3 | **Cross-feature deep imports** | Hidden coupling; one feature breaks another | Import the barrel, or move code to `shared/` |
| 4 | **`any` on props or API data** | No type safety; bugs surface at runtime | Type props with `defineProps<Props>()`; parse API data with zod at the boundary |
| 5 | **God component** | 400-line SFC mixing fetch, state, render | Split container/presentational; extract composables |
| 6 | **Business logic in `<template>` expressions** | Untestable, unreadable | Move to a composable or `computed` |
| 7 | **Global Pinia store for ephemeral UI state** | Couples unrelated UI; bloats store | Keep local `ref` |
| 8 | **No barrel / importing internals** | Public surface undefined; refactors break consumers | Export the public API from `index.ts` |
| 9 | **`:key="index"` on dynamic lists** | Wrong reconciliation, state bleed | Use a stable id |
| 10 | **Tests far from the slice** | Drift; orphaned tests | Co-locate `*.test.ts` beside the component/composable |

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
Symptoms: an SFC exceeds ~250 lines or mixes fetching, state, and presentation.

Recovery:
1. Extract data/state into a custom composable (use<Name>).
2. Split the render into a pure presentational view component.
3. The container becomes: call composable → pass props to the view.
```

### Server data is stale or double-fetched

```
Symptoms: data does not refresh after a mutation, or fetches fire twice.

Recovery:
1. Move the fetch into a query composable with a stable query key.
2. In the mutation composable, invalidate that query key on success.
3. Remove the onMounted-based fetch; the query layer owns the cache lifecycle.
```
