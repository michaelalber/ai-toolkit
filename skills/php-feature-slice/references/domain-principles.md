# Domain Principles & Knowledge Base Lookups

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature is a namespace with its own controller, request, service, resource, and tests. No feature references another feature's internals. | `App\Features\Orders` never uses `App\Features\Users\OrderHelper` — only `App\Shared\*` |
| 2 | **Service Autonomy** | Each feature's service owns its business logic. The controller calls the service; the service calls Eloquent or external APIs. | Controller: `return new OrderResource($this->service->create($request->toDto()));` |
| 3 | **Minimal Abstractions** | Add an interface only when a second implementation or a test seam earns it. A single concrete service does not need an interface. | Bind `OrderWriteService::class` directly; introduce `OrderWriteContract` only when mocked or swapped |
| 4 | **DI via the Container** | Constructor injection resolved by Laravel's container. No `new` of services in controllers, no facades for business logic, no service locator. | `public function __construct(private OrderWriteService $service) {}` |
| 5 | **Read/Write Separation** | Queries and commands live in separate service classes. Structural CQRS — no library. Read services return Resources; write services mutate and return the changed aggregate. | `OrderReadService::show()`, `OrderReadService::list()` vs `OrderWriteService::create()`, `OrderWriteService::cancel()` |
| 6 | **Validation at the Boundary** | All input validation lives in a `FormRequest`. The service receives an already-validated DTO, never the raw request. | `rules()` in `StoreOrderRequest`; controller passes `$request->toDto()` to the service |
| 7 | **Explicit Output Shaping** | Responses go through an `JsonResource`. Eloquent models never leave the controller directly — that leaks schema and sensitive columns. | `return OrderResource::collection($orders);` |
| 8 | **Controller Thinness** | A controller action contains: resolve input → call service → wrap response. If it exceeds ~10 lines, logic has leaked. | Action = `toDto()` → `service->...` → `new Resource(...)` |
| 9 | **Strict Typing** | `declare(strict_types=1)`; every method parameter and return value is type-hinted. No `mixed` without justification. | `public function create(CreateOrderDto $dto): Order` |
| 10 | **Test Proximity** | Feature tests mirror the slice. `tests/Feature/Orders/` mirrors `app/Features/Orders/`. Feature tests hit routes; unit tests mock the service. | `tests/Feature/Orders/CreateOrderTest.php`, `tests/Unit/Orders/OrderWriteServiceTest.php` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp, `collection="php"`) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Laravel Form Request validation controller", collection="php")` | At DETECT — confirm validation and controller conventions for the detected version |
| `search_knowledge("Laravel API Resource transform response", collection="php")` | When scaffolding the Resource layer |
| `search_knowledge("Laravel service container constructor injection binding", collection="php")` | When wiring services into the container |
| `search_knowledge("Laravel Eloquent query builder bound parameters", collection="php")` | When the service touches the database |
| `search_code_examples("Laravel controller form request service", language="php")` | When generating controller/service skeletons |

## Feature Folder Diagram

```
app/
├── Features/
│   └── Orders/
│       ├── Controllers/OrderController.php   ← thin: input → service → resource
│       ├── Requests/StoreOrderRequest.php    ← rules() + toDto()
│       ├── Services/OrderReadService.php      ← queries
│       ├── Services/OrderWriteService.php      ← commands
│       ├── Resources/OrderResource.php         ← output shaping
│       └── Dtos/CreateOrderDto.php             ← readonly validated DTO
├── Shared/                                     ← cross-cutting domain code
└── Providers/AppServiceProvider.php            ← container bindings
routes/features/orders.php                      ← slice route group
tests/Feature/Orders/  tests/Unit/Orders/
```
