# Feature folder template — file by file

Reference content for a React feature slice. Replace `Order`/`order`/`orders` with the feature name.
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

## `hooks/useOrdersQuery.ts` — read (query hook)

```ts
import { useQuery } from "@tanstack/react-query";
import { fetchOrders } from "../data/api";

export const ordersKey = ["orders"] as const;

export function useOrdersQuery() {
  return useQuery({ queryKey: ordersKey, queryFn: fetchOrders });
}
```

## `hooks/useCreateOrder.ts` — write (mutation hook, invalidates cache)

```ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
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

## `components/OrderListView.tsx` — presentational (pure)

```tsx
export type OrderListProps = {
  orders: Order[];
  onSelect: (id: string) => void;
};

export function OrderListView({ orders, onSelect }: OrderListProps) {
  return (
    <ul>
      {orders.map((o) => (
        <li key={o.id}>
          <button type="button" onClick={() => onSelect(o.id)}>
            {o.id} — {o.status}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

## `components/OrderList.tsx` — container (wires hook → view)

```tsx
import { useOrdersQuery } from "../hooks/useOrdersQuery";
import { OrderListView } from "./OrderListView";

export function OrderList({ onSelect }: { onSelect: (id: string) => void }) {
  const { data: orders = [], isLoading, isError } = useOrdersQuery();
  if (isLoading) return <p>Loading…</p>;
  if (isError) return <p role="alert">Could not load orders.</p>;
  return <OrderListView orders={orders} onSelect={onSelect} />;
}
```

## `index.ts` — barrel (public surface)

```ts
export { OrderList } from "./components/OrderList";
export { useOrdersQuery } from "./hooks/useOrdersQuery";
export type { Order } from "./data/schema";
// Do NOT export internals (api.ts, *View, schema internals) — those stay private to the slice.
```

## `OrderList.test.tsx` — RTL test (co-located)

```tsx
import { render, screen } from "@testing-library/react";
import { OrderListView } from "./components/OrderListView";

test("renders an order and fires onSelect", async () => {
  const onSelect = vi.fn();
  render(<OrderListView orders={[{ id: "o1", total: 9, status: "open" }]} onSelect={onSelect} />);
  await userEvent.click(screen.getByRole("button", { name: /o1/ }));
  expect(onSelect).toHaveBeenCalledWith("o1");
});
```

## Naming rules

- Container component: `OrderList` · Presentational: `OrderListView`.
- Read hook ends `Query`; write hook starts `use<Verb>` (`useCreateOrder`, `useCancelOrder`).
- Only the barrel (`index.ts`) is importable from other features. Everything else is slice-private.
