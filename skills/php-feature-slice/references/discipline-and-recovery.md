# AI Discipline Rules, Anti-Patterns & Error Recovery

## AI Discipline Rules

### CRITICAL: No Business Logic in Controllers

**WRONG:**
```php
public function store(Request $request)
{
    $request->validate(['item_id' => 'required']);          // validation in controller
    $item = DB::select("SELECT * FROM items WHERE id = {$request->item_id}"); // SQL injection
    if (!$item) { abort(404); }
    $order = Order::create(['item_id' => $request->item_id]); // logic in controller
    return $order;                                            // model leaked
}
```

**RIGHT:**
```php
public function store(StoreOrderRequest $request): OrderResource
{
    return new OrderResource($this->writeService->create($request->toDto()));
}
```

### REQUIRED: Form Request + DTO at the Boundary

```php
final class StoreOrderRequest extends FormRequest
{
    public function rules(): array
    {
        return ['item_id' => ['required', 'integer', 'exists:items,id'],
                'quantity' => ['required', 'integer', 'min:1']];
    }

    public function toDto(): CreateOrderDto
    {
        return new CreateOrderDto($this->integer('item_id'), $this->integer('quantity'));
    }
}
```

### CRITICAL: No Cross-Feature Imports

```php
// WRONG — in app/Features/Orders/Services/OrderWriteService.php
use App\Features\Users\Services\UserReadService;   // cross-feature coupling

// RIGHT — depend on shared code, or inject via the container at the edge
use App\Shared\Contracts\CurrentUser;
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Business logic in controllers** | Untestable; duplicated across actions | Move all logic to a service class |
| 2 | **Cross-feature imports** | Hidden coupling; one feature breaks another | Use `App\Shared\*`; inject at the controller edge |
| 3 | **Returning Eloquent models from controllers** | Leaks schema and hidden columns; no serialization control | Always return a `JsonResource` |
| 4 | **Raw `$request->input()` in services** | Unvalidated, untyped data flows into business logic | Validate in a `FormRequest`; pass a typed DTO |
| 5 | **`DB::raw` / string-concatenated SQL** | SQL injection | Eloquent or bound query-builder parameters only |
| 6 | **Facades for business logic** | Hides dependencies; defeats injection and mocking | Constructor-inject the service |
| 7 | **Mixing read and write in one service** | Service grows unbounded; different perf profiles | Separate `ReadService` and `WriteService` |
| 8 | **No `declare(strict_types=1)`** | Silent type coercion hides bugs | First line of every PHP file |
| 9 | **Tests under `app/Features/`** | Mixes production and test code; breaks autoloading | Tests live in `tests/Feature` and `tests/Unit` mirrors |
| 10 | **One god service per feature** | Defeats cohesion; merge-conflict magnet | Split by sub-capability (`Fulfillment`, `Billing`) within the slice |

## Error Recovery

### Cross-feature import detected

```
Symptoms: grep for `use App\Features\` inside one slice returns another slice's namespace.

Recovery:
1. Identify what is imported (a model, a service, a value object).
2. Shared model/value object → move to App\Shared and update both slices.
3. Service behavior → inject the contract via the container at the controller edge, not inside the service.
4. Re-run the grep check until it prints nothing.
```

### Service grows too large

```
Symptoms: a service exceeds ~200 lines or holds unrelated methods.

Recovery:
1. Identify sub-capabilities (e.g., Orders has Fulfillment and Billing).
2. Split into OrderFulfillmentService / OrderBillingService — still inside the Orders slice.
3. Update controller constructor injection to the specific service each action needs.
```

### Controller action grows too large

```
Symptoms: an action exceeds ~10 lines or contains conditionals.

Recovery:
1. Move the branching/business logic into the service.
2. Action becomes: $request->toDto() → service call → Resource.
3. If multiple service calls are needed, add one orchestration method to the service.
```
