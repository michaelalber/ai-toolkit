# FastAPI Scaffolder Conventions

Depth behind the Core Philosophy constraints: principles, knowledge-base grounding, discipline
rules, anti-patterns, and recovery. The complete endpoint scaffold is in `router-template.md`; JWT
and API-key patterns in `security-patterns.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Router Grouping** | One `APIRouter` per feature/resource, registered in main.py with a consistent prefix + tag. | `APIRouter(prefix="/api/v1/orders", tags=["orders"])` |
| 2 | **Request/Response Models** | All bodies/responses are Pydantic v2; request models frozen; response models expose only safe fields; never reuse one model for input and output. | Separate `CreateOrderRequest`, `UpdateOrderRequest`, `OrderResponse` |
| 3 | **Validation Integration** | Validators live in the model; handlers receive validated data; FastAPI raises 422 automatically. | `@field_validator` in the model; no manual validation in handlers |
| 4 | **OpenAPI Documentation** | Every endpoint: `summary`, `description`, `response_model`, `responses` dict, `tags`. | `@router.get(..., summary=..., response_model=..., responses={401: {...}})` |
| 5 | **Versioning Strategy** | URL-prefix versioning by default (`/api/v1/`); never mix strategies. | `APIRouter(prefix="/api/v1")` in main.py |
| 6 | **Authorization Patterns** | `Depends()` chains enforce authz; role-based via a factory; resource ownership checked in the service. | `_user: CurrentUser = Depends(require_role("admin"))` |
| 7 | **Rate Limiting** | Router-level via `slowapi`/`fastapi-limiter`; stricter on auth endpoints. | `@limiter.limit("5/minute")` on login; `100/minute` on reads |
| 8 | **Error Handling** | Custom handlers return RFC 7807 Problem Details; no stack traces; all exceptions mapped to status codes. | `@app.exception_handler(...)` → `{type,title,status}` |
| 9 | **CORS Configuration** | Explicit origins from config; `allow_origins=["*"]` with credentials is a violation; dev ≠ prod. | `CORSMiddleware(allow_origins=settings.cors_origins)` |
| 10 | **Health Checks** | `/health` (basic), `/health/ready` (deps), `/health/live` (process) for LB/k8s probes. | `@app.get("/health/ready")` checks DB connectivity |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("FastAPI APIRouter endpoint Pydantic v2 response_model")` | CONFIGURE — router/model patterns |
| `search_knowledge("FastAPI JWT authentication Depends security")` | Configuring authentication |
| `search_knowledge("FastAPI OpenAPI documentation summary description tags")` | Adding OpenAPI metadata |
| `search_knowledge("FastAPI rate limiting slowapi middleware")` | Configuring rate limiting |
| `search_knowledge("FastAPI health check endpoint lifespan")` | Adding health checks |

## Discipline Rules

- **`response_model` is not optional.** Never return an ORM object from a handler (it leaks the
  schema). Every route sets `response_model=`, a `responses` dict, and `summary`, and returns a
  Pydantic instance; raise `HTTPException(404)` for not-found.
- **Security by default.** Apply `dependencies=[Depends(get_current_user)]` at the router level so
  all routes require auth; a public route is an explicit `dependencies=[]` override, documented.
- **Versioning from day one.** `APIRouter(prefix="/api/v1/orders")`, never `prefix="/orders"`. v2 is
  a new router alongside v1, not a URL rewrite.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | No `response_model` | Leaks ORM schema; no response validation; poor docs | Always set `response_model=` |
| 2 | No versioning prefix | Breaking changes require URL changes | `/api/v1/` from day one |
| 3 | `allow_origins=["*"]` with credentials | CORS violation; enables CSRF | Exact origins; never `*` with credentials |
| 4 | Business logic in route handlers | Untestable; duplicated across routes | Move to the service layer |
| 5 | No OpenAPI metadata | Black-box API | `summary`, `description`, `responses` on every route |
| 6 | Returning `dict` instead of a model | No type safety/validation; poor docs | Return Pydantic model instances |
| 7 | No rate limiting on auth endpoints | Brute-force attacks succeed | Strict limits on login, register, password reset |
| 8 | Stack traces in error responses | Exposes internals; security risk | Custom handlers return safe messages |
| 9 | No health checks | LBs can't detect unhealthy instances | `/health`, `/health/ready`, `/health/live` |
| 10 | `DEBUG=True` in production | Exposes internals; disables security features | Environment-based config; `DEBUG=False` in prod |

## Error Recovery

**OpenAPI docs not rendering the new endpoint:**
1. Verify the router is registered (`grep include_router app/main.py`); check the prefix
2. Check for import errors (`uvicorn app.main:app --reload`); check for duplicate route paths (silently ignored)
3. Restart uvicorn after fixing

**Authentication dependency not working** (endpoints return 200 without a valid token):
1. Verify router-level vs. route-level dependency placement; check test overrides aren't leaking
2. The dependency must raise `HTTPException(401)` on failure
3. Test: `curl -H "Authorization: Bearer invalid" .../api/v1/orders/` → expect 401

**Pydantic validation errors returning 500 instead of 422:**
1. A custom catch-all exception handler is swallowing `RequestValidationError`
2. Add an explicit `@app.exception_handler(RequestValidationError)`; FastAPI's default returns 422,
   so a 500 means a handler is intercepting it
