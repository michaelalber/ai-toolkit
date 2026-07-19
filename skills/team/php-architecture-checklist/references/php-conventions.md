# PHP / Laravel Architecture Conventions

Reference detail for the PHP architecture checklist. Aligns with PSR-12 and the project PHP standards.

## Strict typing

Every file starts with `declare(strict_types=1);`. All parameters and return types are hinted,
including `void`, `self`, and union/nullable types where appropriate.

```php
declare(strict_types=1);

final class PriceCalculator
{
    public function total(Order $order): Money { /* ... */ }
}
```

## Service layer over facades

Business logic lives in service classes resolved via constructor injection — not static facades
reached for inside domain code. Facades are acceptable at the framework edge (controllers, jobs),
not in the domain/service layer.

```php
// AVOID in a service: Auth::user(), DB::table(...), Cache::get(...)
// PREFER: inject the contract
public function __construct(
    private readonly OrderRepository $orders,
    private readonly Clock $clock,
) {}
```

## Input validation at the boundary

Validate with Form Requests (Laravel) or an explicit validator — never trust `$request->input()`
directly in a controller or service.

```php
public function store(StoreOrderRequest $request): JsonResponse
{
    $data = $request->validated();   // already validated + typed
    // ...
}
```

## Query safety

Use Eloquent or the Query Builder with bound parameters. Never concatenate user input into SQL.

```php
// SAFE
User::where('email', $email)->first();
DB::select('select * from users where email = ?', [$email]);

// UNSAFE — flag as Critical
DB::select("select * from users where email = '$email'");
DB::raw("... {$userInput} ...");
```

## Config & secrets

Secrets live in `.env`; access them through `config()` in application code, never `env()` outside
config files (env() returns null once config is cached).

```php
// config/services.php
return ['stripe' => ['key' => env('STRIPE_KEY')]];
// application code
$key = config('services.stripe.key');
```

## Thin controllers

A controller validates, delegates to a service, and returns a response. Business rules, persistence,
and external calls belong in services.

## Tooling

```bash
phpstan analyse --level=6           # static analysis
php-cs-fixer fix --dry-run --diff   # PSR-12 style check (Laravel: `pint --test` instead)
composer outdated --direct          # dependency currency
```
