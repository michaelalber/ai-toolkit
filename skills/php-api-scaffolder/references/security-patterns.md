# API Security Patterns (Laravel)

Auth, rate limiting, CORS, and a consistent error envelope. Aligned with OWASP API Security Top 10.

## Sanctum token authentication

Install (Laravel 11-13): `php artisan install:api` — adds Sanctum, `routes/api.php`, and the
`HasApiTokens` trait wiring. For ≤10: `composer require laravel/sanctum` then publish + migrate.

Issue a token:

```php
$token = $user->createToken('mobile', ['orders:read', 'orders:write'])->plainTextToken;
```

Protect routes and check abilities (least privilege — authentication is not authorization):

```php
Route::middleware(['auth:sanctum'])->group(function (): void {
    Route::post('/orders', [OrderController::class, 'store'])
        ->middleware('ability:orders:write');
});
```

In the action, still authorize the specific record via a Policy:

```php
$this->authorize('update', $order);   // 403 if the policy denies
```

## Rate limiting

Define named limiters in a service provider (`App\Providers\AppServiceProvider::boot` on 11/12, or
`RouteServiceProvider` on ≤10). Authenticated users get a higher, per-user limit; anonymous traffic is
limited by IP.

```php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Support\Facades\RateLimiter;

RateLimiter::for('api', function (Request $request): Limit {
    return $request->user()
        ? Limit::perMinute(120)->by($request->user()->id)
        : Limit::perMinute(30)->by($request->ip());
});

// A stricter limiter for auth/login endpoints (credential stuffing defense)
RateLimiter::for('auth', fn (Request $r) => Limit::perMinute(5)->by($r->ip()));
```

Apply with `->middleware('throttle:api')` / `->middleware('throttle:auth')`. Exceeding the limit returns
`429` with `Retry-After` and `X-RateLimit-*` headers automatically.

## CORS

Laravel ships `config/cors.php`. Restrict origins — never ship `'allowed_origins' => ['*']` with
credentials.

```php
return [
    'paths' => ['api/*'],
    'allowed_methods' => ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    'allowed_origins' => [env('FRONTEND_URL', 'https://app.example.com')],
    'allowed_headers' => ['Content-Type', 'Authorization', 'Accept'],
    'supports_credentials' => true,
];
```

## Consistent error envelope

Centralize exception rendering so every error has one shape. Laravel 11+ (`bootstrap/app.php`):

```php
->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->render(function (Throwable $e, Request $request) {
        if (! $request->is('api/*')) {
            return null; // default handling for web
        }

        $status = match (true) {
            $e instanceof ValidationException        => 422,
            $e instanceof AuthenticationException     => 401,
            $e instanceof AuthorizationException      => 403,
            $e instanceof ModelNotFoundException,
            $e instanceof NotFoundHttpException        => 404,
            $e instanceof ThrottleRequestsException   => 429,
            default                                    => 500,
        };

        return response()->json([
            'error' => [
                'status'  => $status,
                'message' => $status >= 500 ? 'Server error' : $e->getMessage(),
                'errors'  => $e instanceof ValidationException ? $e->errors() : null,
            ],
        ], $status);
    });
});
```

For Laravel ≤11, register the same closures in `app/Exceptions/Handler.php::register()`.

**Never** include stack traces, SQL, or file paths in production responses — gate verbose output behind
`config('app.debug')`, which must be `false` in production.

## Mass-assignment protection

Validate explicitly and pass only validated keys to `create()`/`update()`:

```php
$user = User::create($request->validated());   // not $request->all()
```

Keep `$fillable` (allow-list) on models — never `$guarded = []`.

## Security headers (optional middleware)

```php
$response->headers->set('X-Content-Type-Options', 'nosniff');
$response->headers->set('X-Frame-Options', 'DENY');
$response->headers->set('Referrer-Policy', 'no-referrer');
```

## Checklist

- [ ] Sanctum installed; `auth:sanctum` on every non-public route
- [ ] Token abilities + per-record Policy checks (authz ≠ authn)
- [ ] `throttle:` limiter on every group; stricter limiter on auth endpoints
- [ ] CORS origins restricted; no wildcard with credentials
- [ ] One JSON error envelope; no stack traces in production
- [ ] `validated()` only — never `$request->all()` into `create()`
- [ ] `APP_DEBUG=false` in production
