# Structural CQRS Conventions (Laravel, no library)

Laravel has no mediator. CQRS here is a **naming and structural** convention enforced by review, not a
framework contract. The goal: commands and queries have different shapes, different failure modes, and
different performance profiles, so they live in different classes.

## The split

| Concern | Class | Returns | Touches |
|---------|-------|---------|---------|
| Query (read) | `<Feature>ReadService` | Models / paginators for a Resource to shape | Read replicas, eager loads, projections |
| Command (write) | `<Feature>WriteService` | The changed aggregate (one model) | Transactions, events, write DB |

A controller may depend on both, but a single action uses exactly one side.

## Why separate classes, not one service with read+write methods

1. **Different evolution.** Read models grow projections, joins, and caching. Write models grow
   invariants, transactions, and events. Mixed, every change risks the other side.
2. **Different testing.** Reads are asserted on returned data; writes are asserted on persisted state
   and emitted events. Splitting keeps each test class focused.
3. **Different scaling.** Reads can target a replica connection; writes must hit the primary. Separation
   makes the connection choice explicit per class.

## Wiring without an interface (the default)

Bind nothing. The container auto-resolves a concrete service via constructor injection:

```php
public function __construct(
    private readonly OrderReadService $read,
    private readonly OrderWriteService $write,
) {}
```

YAGNI: do **not** create `OrderWriteContract` until a second implementation or a test double earns it.

## Wiring with an interface (only when earned)

Introduce a contract when you must swap the implementation at runtime or inject a fake in a unit test
that cannot use the real database cheaply:

```php
// app/Features/Orders/Contracts/OrderWriteContract.php
interface OrderWriteContract
{
    public function create(CreateOrderDto $dto): Order;
}

// app/Providers/AppServiceProvider.php
$this->app->bind(OrderWriteContract::class, OrderWriteService::class);
```

With Laravel's TestContainers-equivalent (`RefreshDatabase` + SQLite in-memory), most write-service
tests can use the real database — so an interface is usually unnecessary. This mirrors the DIP guidance:
add the abstraction only when a real fake or a real swap exists.

## Read connection selection (optional)

```php
final class OrderReadService
{
    public function list(int $perPage = 20): LengthAwarePaginator
    {
        return Order::on('mysql_read')->latest()->paginate($perPage);
    }
}
```

Only introduce a read connection when a replica actually exists. Until then, the default connection is
correct and the class boundary alone is the CQRS signal.

## Events at the command boundary

Write services emit domain events; read services never do.

```php
public function create(CreateOrderDto $dto): Order
{
    return DB::transaction(function () use ($dto): Order {
        $order = Order::create([...]);
        OrderPlaced::dispatch($order);   // command side only
        return $order;
    });
}
```

## Anti-patterns specific to the split

| Anti-pattern | Fix |
|--------------|-----|
| `OrderService` with `create()` and `list()` together | Split into `OrderWriteService` / `OrderReadService` |
| Read service mutating state (`->update()` inside a "get") | Move the mutation to the write service |
| Write service returning a Resource | Return the model; let the controller wrap it |
| Controller calling Eloquent directly "just for a quick read" | Even one-line reads go through the read service |
