# API Conventions, Discipline & Recovery

Depth relocated from `SKILL.md`: the full domain-principle set, knowledge-base
lookups, AI discipline rules, anti-pattern catalog, and error-recovery procedures.

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
