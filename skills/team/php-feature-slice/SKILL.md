---
name: php-feature-slice
audience: team
description: >
  Scaffolds feature-based PHP / Laravel architecture using feature folders, thin controllers,
  Form Requests, a service/action layer, and API Resources. PHP analog of dotnet-vertical-slice
  and python-feature-slice — no mediator library; uses the Laravel service container for
  dependency injection and structural CQRS conventions. Use when creating feature-based PHP
  projects, adding Laravel features, scaffolding service layers, or organizing PHP code by
  feature rather than by technical layer.
---

# PHP Feature Slice Architecture

> "The best code is code that never has to be written."
> -- Jeff Atwood

> "Organize around business capabilities, not technical layers."
> -- Sam Newman, *Building Microservices*

## Core Philosophy

Feature slice architecture organizes code by business capability, not by technical layer. Laravel's default skeleton is layer-based — `app/Http/Controllers`, `app/Models`, `app/Services` spread one feature across many directories. This skill replaces that with self-contained vertical slices: `app/Features/Orders/`, `app/Features/Users/`, each owning its full stack — controller, Form Request, service, API Resource, and tests.

In PHP with Laravel, the mediator pattern (FreeMediator in .NET) is replaced by Laravel's **service container**. Service classes are constructor-injected into controllers; the container resolves them automatically. CQRS separation is a structural and naming convention — `OrderReadService` vs `OrderWriteService` — not a library contract.

**Non-Negotiable Constraints:**
1. **`declare(strict_types=1)`** at the top of every PHP file
2. **Feature isolation** — no cross-feature imports; features communicate through shared domain code only
3. **Service layer owns business logic** — controllers are thin; no business logic in controllers
4. **Form Requests for all input** — never trust raw `$request->input()`; validation lives in `FormRequest::rules()`
5. **API Resources for all output** — never return Eloquent models directly from controllers
6. **Eloquent or bound parameters only** — never string-concatenated SQL

**What this skill is NOT:**
- It is NOT a microservices guide — feature slices live within a single Laravel application
- It is NOT prescriptive about feature count — start with the features you have
- It is NOT a replacement for DDD — it is compatible with DDD but does not require it

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

## Workflow

### Phase 1: DETECT

**Objective:** Understand the existing structure before scaffolding.

```bash
# PHP and Laravel version
php -v | head -1
grep -E '"(php|laravel/framework)"' composer.json

# Existing structure — layered, modular, or already feature-based
find app -type d -not -path '*/vendor/*' | head -30

# Existing route registration and service bindings
grep -rn "Route::" routes/ | head -20
grep -rn "->bind\|->singleton" app/Providers/ | head -20
```

Record: PHP version, Laravel version (5.5 / 6.x / 8+ / 12.x), current layout, route file (`routes/api.php` vs `web.php`), auth pattern.

### Phase 2: SCAFFOLD

Create the feature namespace. See `references/feature-folder-template.md` for file-by-file content.

```
app/Features/<Name>/
  Controllers/<Name>Controller.php   # thin; resolve → call service → resource
  Requests/Store<Name>Request.php     # FormRequest: rules() + toDto()
  Requests/Update<Name>Request.php
  Services/<Name>ReadService.php       # queries
  Services/<Name>WriteService.php      # commands
  Resources/<Name>Resource.php         # JsonResource output shaping
  Dtos/Create<Name>Dto.php             # validated, readonly transfer object
routes/features/<name>.php             # route group for the slice
tests/Feature/<Name>/Create<Name>Test.php
tests/Unit/<Name>/<Name>WriteServiceTest.php
```

### Phase 3: REGISTER

Wire the slice into routing and (only if an interface exists) the container.

```php
// routes/api.php
require __DIR__ . '/features/orders.php';

// app/Providers/AppServiceProvider.php — only when an interface is introduced
$this->app->bind(OrderWriteContract::class, OrderWriteService::class);
```

### Phase 4: VERIFY

```bash
php artisan route:list --path=api/v1/<name>     # routes registered
vendor/bin/pest tests/Feature/<Name> tests/Unit/<Name>   # or phpunit
# Cross-feature import check — should print nothing
grep -rn "use App\\\\Features\\\\" app/Features/<Name> | grep -v "App\\\\Features\\\\<Name>"
```

## State Block

```xml
<php-feature-slice-state>
  phase: DETECT | SCAFFOLD | REGISTER | VERIFY | COMPLETE
  feature_name: [name]
  laravel_version: [detected]
  existing_structure: layered | modular | feature-based | unknown
  routes_registered: true | false
  read_service_created: true | false
  write_service_created: true | false
  tests_scaffolded: true | false
  last_action: [description]
  next_action: [description]
</php-feature-slice-state>
```

## Output Templates

### Feature Slice Scaffold: [Feature Name]

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `app/Features/<Name>/Controllers/<Name>Controller.php`
- [ ] `app/Features/<Name>/Requests/Store<Name>Request.php`
- [ ] `app/Features/<Name>/Requests/Update<Name>Request.php`
- [ ] `app/Features/<Name>/Services/<Name>ReadService.php`
- [ ] `app/Features/<Name>/Services/<Name>WriteService.php`
- [ ] `app/Features/<Name>/Resources/<Name>Resource.php`
- [ ] `app/Features/<Name>/Dtos/Create<Name>Dto.php`
- [ ] `routes/features/<name>.php`
- [ ] `tests/Feature/<Name>/Create<Name>Test.php`
- [ ] `tests/Unit/<Name>/<Name>WriteServiceTest.php`

### Registration
- [ ] Route group required into `routes/api.php`
- [ ] Prefix set: `/api/v1/<name>`; middleware: `['api', 'auth:sanctum']`

### Verification
- [ ] `php artisan route:list` shows the new routes
- [ ] `pest` / `phpunit` green for the slice
- [ ] No cross-feature imports detected
```

### Feature Folder Diagram

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

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `php-api-scaffolder` | Endpoint-level quality (Sanctum auth, throttle, versioning, OpenAPI). Use together when a new slice needs production-grade endpoints. |
| `php-migration-manager` | When a slice needs schema changes, manage the Laravel migration lifecycle and rollback safety. |
| `php-security-review` | After scaffolding, audit the slice's validation, authorization, and query safety against OWASP. |
| `php-architecture-checklist` | Architecture quality gate. Run after several slices to verify isolation and coupling. |
| `tdd` | Drive each service method test-first (RED → GREEN → REFACTOR) rather than scaffolding code ahead of tests. |
