---
name: php-api-scaffolder
audience: team
description: >
  Scaffolds Laravel API endpoints with API Resource responses, Form Request validation, Sanctum
  authentication, throttle-based rate limiting, URI versioning, OpenAPI documentation, and
  health checks. PHP analog of fastapi-scaffolder, minimal-api-scaffolder, and axum-scaffolder.
  Use when creating REST APIs in Laravel, adding API endpoints, setting up API routing and
  middleware, or configuring API infrastructure.
---

# PHP API Scaffolder (Laravel)

> "A good API is easy to use correctly and hard to use incorrectly."
> -- Joshua Bloch

> "Be conservative in what you send, be liberal in what you accept."
> -- Postel's Law

## Core Philosophy

This skill scaffolds **production-grade Laravel API endpoints** — not just a route and a closure. Every
endpoint ships with input validation (Form Request), output shaping (API Resource), authentication
(Sanctum), rate limiting (throttle), a version prefix, a documented OpenAPI contract, and a consistent
error envelope. The default is `routes/api.php` with the `api` middleware group, which is stateless and
already namespaced under `/api`.

The endpoint is a boundary. Untrusted input is validated and typed before it reaches any service; output
is shaped through a Resource so schema and sensitive columns never leak. Errors return a predictable JSON
shape with the correct HTTP status — `422` for validation, `401`/`403` for auth, `429` for throttling.

**Non-Negotiable Constraints:**
1. **`declare(strict_types=1)`** in every generated PHP file
2. **Form Request validation** on every write endpoint — never raw `$request->input()`
3. **API Resource** on every response — never return Eloquent models or arrays directly
4. **Versioned URIs** — `/api/v1/...`; breaking changes bump the version, never mutate `v1`
5. **Auth + throttle middleware** declared on every non-public route
6. **OpenAPI annotations** kept next to the controller action they describe

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Validate at the edge** | Input is validated and typed in a Form Request before the controller runs. | `public function store(StoreUserRequest $request)` — invalid input never reaches the action |
| 2 | **Shape every response** | Responses go through a `JsonResource`; the model never serializes itself to the client. | `return new UserResource($user);` — `data` envelope, controlled fields |
| 3 | **Version in the URI** | Major version in the path. `v1` is frozen once published; additive changes are fine, breaking changes mean `v2`. | `Route::prefix('v1')` group; `v2` is a new group, not an edit |
| 4 | **Stateless auth** | Token auth via Sanctum on `routes/api.php`; no session for pure APIs. | `->middleware('auth:sanctum')` |
| 5 | **Rate-limit by default** | Every route group carries a named throttle limiter; public and authenticated limits differ. | `->middleware('throttle:api')`, limiter defined in a service provider |
| 6 | **Consistent errors** | One JSON error envelope across the API; map exceptions centrally, not per-action. | Custom render in `bootstrap/app.php` (12.x) or `Handler::register` (≤11) |
| 7 | **Document at the source** | OpenAPI annotations (attributes) live on the action; the spec is generated, not hand-maintained. | `#[OA\Post(...)]` above `store()`; `l5-swagger`/`scribe` generates the doc |
| 8 | **Health is an endpoint** | A liveness route returns build/version and dependency status without auth. | `GET /api/health` → `{ "status": "ok" }` |
| 9 | **Idempotent reads** | `GET`/`HEAD` never mutate; pagination is explicit and bounded. | `->paginate($perPage)` with a capped `$perPage` |
| 10 | **Least privilege** | Authorization checked in the Form Request `authorize()` or a Policy, not assumed from authentication. | `return $this->user()->can('update', $post);` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp, `collection="php"`).

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Laravel routes api middleware group versioning", collection="php")` | At DETECT — confirm routing/version conventions |
| `search_knowledge("Laravel Sanctum API token authentication protect routes", collection="php")` | When wiring auth |
| `search_knowledge("Laravel rate limiting throttle RateLimiter", collection="php")` | When configuring limiters |
| `search_knowledge("Laravel API Resource pagination response", collection="php")` | When shaping responses |
| `search_knowledge("Laravel exception handler json response", collection="php")` | When standardizing the error envelope |

## Workflow

### Phase 1: DETECT

```bash
php -v | head -1
grep -E '"(php|laravel/framework)"' composer.json
# Does an API route file / Sanctum exist yet?
ls routes/api.php 2>/dev/null && grep -rn "Sanctum\|auth:sanctum" routes/ app/ | head
# Existing version prefixes and limiters
grep -rn "prefix('v" routes/ ; grep -rn "RateLimiter::for" app/
```

If `routes/api.php` is absent on Laravel 11/12, run `php artisan install:api` (installs Sanctum, creates
the file). Record version, whether Sanctum is present, existing limiters, and the OpenAPI tool in use
(`l5-swagger`, `scribe`, or none).

### Phase 2: SCAFFOLD

See `references/route-template.md` for full controller, request, resource, and route content, and
`references/security-patterns.md` for auth, throttle, CORS, and the error envelope.

```
app/Http/Controllers/Api/V1/<Name>Controller.php   # OpenAPI annotations + thin actions
app/Http/Requests/Api/V1/Store<Name>Request.php
app/Http/Resources/V1/<Name>Resource.php
routes/api.php                                       # v1 group: auth + throttle
app/Providers/AppServiceProvider.php / RouteServiceProvider  # RateLimiter::for('api', ...)
tests/Feature/Api/V1/<Name>EndpointTest.php
```

### Phase 3: SECURE & DOCUMENT

```php
// routes/api.php
Route::get('/health', HealthController::class);     // public liveness

Route::prefix('v1')->middleware(['auth:sanctum', 'throttle:api'])->group(function (): void {
    Route::apiResource('users', UserController::class);
});
```

Generate the spec: `php artisan l5-swagger:generate` (or `php artisan scribe:generate`).

### Phase 4: VERIFY

```bash
php artisan route:list --path=api
vendor/bin/pest tests/Feature/Api          # or phpunit
curl -s localhost:8000/api/health          # {"status":"ok"}
# 429 after exceeding the limiter; 422 on bad input; 401 without a token
```

## State Block

```xml
<php-api-scaffolder-state>
  phase: DETECT | SCAFFOLD | SECURE | VERIFY | COMPLETE
  endpoint: [resource name]
  laravel_version: [detected]
  api_version: v1
  sanctum_installed: true | false
  throttle_configured: true | false
  openapi_tool: l5-swagger | scribe | none
  resource_created: true | false
  request_created: true | false
  tests_scaffolded: true | false
  last_action: [description]
</php-api-scaffolder-state>
```

## Output Templates

### Laravel API Endpoint Scaffold: [Endpoint Name]

```markdown
## API Endpoint Scaffold: [Endpoint Name]

### Files Created
- [ ] `app/Http/Controllers/Api/V1/<Name>Controller.php` (OpenAPI annotated)
- [ ] `app/Http/Requests/Api/V1/Store<Name>Request.php`
- [ ] `app/Http/Resources/V1/<Name>Resource.php`
- [ ] `tests/Feature/Api/V1/<Name>EndpointTest.php`

### Routing & Middleware
- [ ] Registered under `Route::prefix('v1')`
- [ ] `auth:sanctum` applied (or documented as public)
- [ ] `throttle:api` applied; limiter defined
- [ ] Health route `GET /api/health` present

### Contract
- [ ] OpenAPI annotations on each action
- [ ] Spec regenerated (`l5-swagger:generate` / `scribe:generate`)
- [ ] Error envelope consistent (422 / 401 / 403 / 429)

### Verification
- [ ] `route:list` shows versioned routes
- [ ] Feature tests green (happy path + 422 + 401 + 429)
```

## AI Discipline Rules

### CRITICAL: Never Return a Model Directly

**WRONG:**
```php
public function show(User $user) { return $user; }      // leaks every column incl. hidden casts
```
**RIGHT:**
```php
public function show(User $user): UserResource { return new UserResource($user); }
```

### REQUIRED: Throttle and Auth Are Declared, Not Assumed

```php
Route::prefix('v1')
    ->middleware(['auth:sanctum', 'throttle:api'])   // explicit on the group
    ->group(fn () => Route::apiResource('orders', OrderController::class));
```

### CRITICAL: Freeze Published Versions

Never edit a `v1` response shape that clients depend on. Add fields additively, or create `v2`. A
breaking change inside `v1` is an outage for every consumer.

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Returning models/arrays from actions** | Leaks schema and hidden fields; no contract | Always wrap in a `JsonResource` |
| 2 | **`$request->input()` without validation** | Untrusted, untyped data enters logic | Form Request with `rules()` |
| 3 | **No version prefix** | First breaking change breaks every client | `Route::prefix('v1')` from day one |
| 4 | **Editing a published `v1` shape** | Silent client breakage | Additive change or new `v2` |
| 5 | **No rate limiting** | Brute-force and scraping exposure | `throttle:` limiter on every group |
| 6 | **Session auth on a pure API** | CSRF surface, stateful coupling | Sanctum token guard on `routes/api.php` |
| 7 | **Per-action error formatting** | Inconsistent envelopes confuse clients | Centralize exception rendering |
| 8 | **Hand-written OpenAPI drifting from code** | Docs lie | Annotate the action; generate the spec |
| 9 | **Unbounded `paginate()` / `all()`** | Memory blowups, slow queries | Cap `perPage`; require pagination |
| 10 | **Auth implies authz** | Any logged-in user can act on any record | Check a Policy / `authorize()` per action |

## Error Recovery

### 419 / CSRF errors on API calls

```
Symptom: POST returns 419 "page expired".
Cause: route is in web.php (session + CSRF), not api.php.
Fix: move the route to routes/api.php under the `api` group; use Sanctum token auth.
```

### Throttle not triggering

```
Symptom: requests never return 429.
Cause: no RateLimiter::for('api', ...) defined, or `throttle:` missing on the group.
Fix: define the limiter in a service provider; add `throttle:api` to the route group; re-test with a loop.
```

### OpenAPI spec out of date

```
Symptom: /api/documentation shows stale endpoints.
Fix: re-run l5-swagger:generate / scribe:generate; ensure annotations are on the action, not a removed file;
add generation to CI so the spec cannot drift.
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `php-feature-slice` | Provides the feature folder + service layer the controller delegates to. Use together for a full slice with production endpoints. |
| `php-security-review` | Audit the new endpoints for OWASP API risks (authz, mass assignment, rate limits) after scaffolding. |
| `php-migration-manager` | When an endpoint needs new tables/columns, manage the migration lifecycle. |
| `php-package-scaffold` | When the API client/SDK is published as a Composer package. |
| `tdd` | Drive each endpoint test-first (request → 422/401/200) before generating the action. |
