# Feature Folder Template (Laravel)

File-by-file content for a single feature slice. Replace `Order`/`order`/`orders` with the
feature name. All files begin with `declare(strict_types=1);`. Targets Laravel 8+; for 5.5/6.x
see the version notes at the bottom.

## `app/Features/Orders/Dtos/CreateOrderDto.php`

A `readonly` value object — the validated boundary between HTTP and the service.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Dtos;

final readonly class CreateOrderDto
{
    public function __construct(
        public int $itemId,
        public int $quantity,
    ) {
    }
}
```

## `app/Features/Orders/Requests/StoreOrderRequest.php`

Validation lives here, never in the controller. `toDto()` produces the typed object the service consumes.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Requests;

use App\Features\Orders\Dtos\CreateOrderDto;
use Illuminate\Foundation\Http\FormRequest;

final class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', \App\Models\Order::class) ?? false;
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'item_id'  => ['required', 'integer', 'exists:items,id'],
            'quantity' => ['required', 'integer', 'min:1', 'max:1000'],
        ];
    }

    public function toDto(): CreateOrderDto
    {
        return new CreateOrderDto(
            itemId: $this->integer('item_id'),
            quantity: $this->integer('quantity'),
        );
    }
}
```

## `app/Features/Orders/Services/OrderWriteService.php`

Owns command-side business logic. Receives a DTO, returns the changed aggregate.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Services;

use App\Features\Orders\Dtos\CreateOrderDto;
use App\Models\Order;
use Illuminate\Support\Facades\DB;

final class OrderWriteService
{
    public function create(CreateOrderDto $dto): Order
    {
        return DB::transaction(function () use ($dto): Order {
            // Business rules belong here, not in the controller.
            return Order::create([
                'item_id'  => $dto->itemId,
                'quantity' => $dto->quantity,
                'status'   => 'pending',
            ]);
        });
    }

    public function cancel(Order $order): Order
    {
        $order->update(['status' => 'cancelled']);

        return $order;
    }
}
```

## `app/Features/Orders/Services/OrderReadService.php`

Query-side only. Returns models/collections for the Resource to shape — never echoes raw SQL.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Services;

use App\Models\Order;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

final class OrderReadService
{
    public function show(int $id): Order
    {
        return Order::query()->findOrFail($id);
    }

    public function list(int $perPage = 20): LengthAwarePaginator
    {
        return Order::query()->latest()->paginate($perPage);
    }
}
```

## `app/Features/Orders/Resources/OrderResource.php`

The only thing that crosses the controller boundary outward.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin \App\Models\Order */
final class OrderResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'id'       => $this->id,
            'item_id'  => $this->item_id,
            'quantity' => $this->quantity,
            'status'   => $this->status,
            'created_at' => $this->created_at?->toIso8601String(),
        ];
    }
}
```

## `app/Features/Orders/Controllers/OrderController.php`

Thin. Resolve input → call service → wrap response. No branching.

```php
<?php

declare(strict_types=1);

namespace App\Features\Orders\Controllers;

use App\Features\Orders\Requests\StoreOrderRequest;
use App\Features\Orders\Resources\OrderResource;
use App\Features\Orders\Services\OrderReadService;
use App\Features\Orders\Services\OrderWriteService;
use App\Http\Controllers\Controller;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

final class OrderController extends Controller
{
    public function __construct(
        private readonly OrderReadService $read,
        private readonly OrderWriteService $write,
    ) {
    }

    public function index(): AnonymousResourceCollection
    {
        return OrderResource::collection($this->read->list());
    }

    public function show(int $id): OrderResource
    {
        return new OrderResource($this->read->show($id));
    }

    public function store(StoreOrderRequest $request): OrderResource
    {
        return new OrderResource($this->write->create($request->toDto()));
    }
}
```

## `routes/features/orders.php`

```php
<?php

declare(strict_types=1);

use App\Features\Orders\Controllers\OrderController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1/orders')
    ->middleware(['auth:sanctum', 'throttle:api'])
    ->group(function (): void {
        Route::get('/', [OrderController::class, 'index']);
        Route::get('/{id}', [OrderController::class, 'show'])->whereNumber('id');
        Route::post('/', [OrderController::class, 'store']);
    });
```

Require it from `routes/api.php`: `require __DIR__ . '/features/orders.php';`

## `tests/Feature/Orders/CreateOrderTest.php` (Pest)

```php
<?php

declare(strict_types=1);

use App\Models\Item;
use App\Models\User;
use function Pest\Laravel\actingAs;
use function Pest\Laravel\postJson;

it('creates an order for an authenticated user', function (): void {
    $user = User::factory()->create();
    $item = Item::factory()->create();

    actingAs($user)
        ->postJson('/api/v1/orders', ['item_id' => $item->id, 'quantity' => 2])
        ->assertCreated()
        ->assertJsonPath('data.status', 'pending');
});

it('rejects an invalid quantity', function (): void {
    actingAs(User::factory()->create())
        ->postJson('/api/v1/orders', ['item_id' => 1, 'quantity' => 0])
        ->assertStatus(422);
});
```

## Version notes

- **Laravel 5.5 / 6.x:** no `readonly` promoted properties (PHP < 8.1) — use a constructor that assigns
  `private` fields and add getters, or a plain array DTO. Form Requests, Resources, and the container
  API are otherwise identical.
- **Laravel 8+:** `whereNumber`, route model binding, and `Route::group` callbacks as shown.
- **Laravel 12.x/13.x:** `routes/api.php` is created by `php artisan install:api` and Sanctum is the default
  token guard. The `/api` prefix is applied automatically — do not repeat it in the slice route file.
