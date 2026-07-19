# Feature folder template — file by file

Reference content for a Vue feature slice. Replace `Order`/`order`/`orders` with the feature name.
TypeScript `strict` assumed throughout. These are skeletons — drive the real implementation test-first.

## `data/schema.ts` — boundary types

```ts
import { z } from "zod";

export const OrderSchema = z.object({
  id: z.string(),
  total: z.number().nonnegative(),
  status: z.enum(["open", "paid", "cancelled"]),
});

export type Order = z.infer<typeof OrderSchema>;

export const CreateOrderSchema = z.object({
  itemId: z.string(),
  quantity: z.number().int().positive(),
});
export type CreateOrderInput = z.infer<typeof CreateOrderSchema>;
```

## `data/api.ts` — the only I/O in the slice

```ts
import { http } from "@/shared/http";
import { OrderSchema, type Order, type CreateOrderInput } from "./schema";
import { z } from "zod";

export async function fetchOrders(): Promise<Order[]> {
  const res = await http.get("/api/v1/orders");
  return z.array(OrderSchema).parse(res.data);   // parse → typed, never `any`
}

export async function createOrder(input: CreateOrderInput): Promise<Order> {
  const res = await http.post("/api/v1/orders", input);
  return OrderSchema.parse(res.data);
}
```

## `composables/useOrdersQuery.ts` — read (query composable)

```ts
import { useQuery } from "@tanstack/vue-query";
import { fetchOrders } from "../data/api";

export const ordersKey = ["orders"] as const;

export function useOrdersQuery() {
  return useQuery({ queryKey: ordersKey, queryFn: fetchOrders });
}
```

## `composables/useCreateOrder.ts` — write (mutation composable, invalidates cache)

```ts
import { useMutation, useQueryClient } from "@tanstack/vue-query";
import { createOrder } from "../data/api";
import { ordersKey } from "./useOrdersQuery";

export function useCreateOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createOrder,
    onSuccess: () => qc.invalidateQueries({ queryKey: ordersKey }),
  });
}
```

## `components/OrderListView.vue` — presentational (pure)

```vue
<script setup lang="ts">
import type { Order } from "../data/schema";

defineProps<{
  orders: Order[];
}>();
const emit = defineEmits<{ select: [id: string] }>();
</script>

<template>
  <ul>
    <li v-for="o in orders" :key="o.id">
      <button type="button" @click="emit('select', o.id)">
        {{ o.id }} — {{ o.status }}
      </button>
    </li>
  </ul>
</template>
```

## `components/OrderList.vue` — container (wires composable → view)

```vue
<script setup lang="ts">
import { useOrdersQuery } from "../composables/useOrdersQuery";
import OrderListView from "./OrderListView.vue";

defineEmits<{ select: [id: string] }>();
const { data: orders, isLoading, isError } = useOrdersQuery();
</script>

<template>
  <p v-if="isLoading">Loading…</p>
  <p v-else-if="isError" role="alert">Could not load orders.</p>
  <OrderListView v-else :orders="orders ?? []" @select="$emit('select', $event)" />
</template>
```

## `index.ts` — barrel (public surface)

```ts
export { default as OrderList } from "./components/OrderList.vue";
export { useOrdersQuery } from "./composables/useOrdersQuery";
export type { Order } from "./data/schema";
// Do NOT export internals (api.ts, *View.vue, schema internals) — those stay private to the slice.
```

## `OrderListView.test.ts` — component test (co-located)

```ts
import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import OrderListView from "./components/OrderListView.vue";

test("renders an order and fires select", async () => {
  const { emitted } = render(OrderListView, {
    props: { orders: [{ id: "o1", total: 9, status: "open" }] },
  });
  await userEvent.click(screen.getByRole("button", { name: /o1/ }));
  expect(emitted().select[0]).toEqual(["o1"]);
});
```

## Naming rules

- Container component: `OrderList` · Presentational: `OrderListView`.
- Read composable ends `Query`; write composable starts `use<Verb>` (`useCreateOrder`, `useCancelOrder`).
- Only the barrel (`index.ts`) is importable from other features. Everything else is slice-private.
