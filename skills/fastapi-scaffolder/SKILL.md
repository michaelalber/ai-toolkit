---
name: fastapi-scaffolder
description: Scaffolds FastAPI endpoints with OpenAPI documentation, Pydantic v2 request/response models, JWT authentication, rate limiting, and health checks. Python analog of minimal-api-scaffolder. Use when creating REST APIs, adding endpoints, setting up FastAPI projects, or configuring API infrastructure. Triggers on phrases like "scaffold fastapi", "create fastapi endpoint", "fastapi router", "add fastapi route", "fastapi api", "python rest api", "fastapi project setup", "fastapi authentication", "fastapi openapi".
---

# FastAPI Scaffolder

> "An API is a contract. Make it explicit, make it versioned, make it documented."
> -- Adapted from API design practice

> "Security by default means the insecure path requires more work than the secure path."
> -- OWASP Secure Design Principles

## Core Philosophy

FastAPI has OpenAPI documentation built in — but built-in does not mean automatic. Every endpoint requires explicit metadata (`summary`, `description`, `response_model`, `responses`) to produce documentation that is useful to API consumers. An endpoint without metadata is a black box.

Security by default means every router requires authentication unless explicitly opted out. The opt-out must be intentional and documented. An unauthenticated endpoint is a deliberate decision, not an oversight.

**Non-Negotiable Constraints:**
1. **OpenAPI-First** — every endpoint has `summary`, `description`, `response_model`, and `responses` dict
2. **Versioning from Day One** — `/api/v1/` prefix via `APIRouter(prefix="/api/v1")`; changing this later is a breaking change
3. **Security by Default** — `Depends(get_current_user)` on all routers; anonymous access is explicit opt-out
4. **Pydantic v2 Models** — all request/response types are `BaseModel` subclasses; no bare `dict` or `Any` returns
5. **Typed Responses** — explicit `response_model=` on every route; no implicit response type inference

**What this skill is NOT:**
- It is NOT a FastAPI tutorial — it assumes FastAPI knowledge
- It is NOT a database guide — use `alembic-migration-manager` for schema changes
- It is NOT a deployment guide — it covers the application layer only

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Router Grouping** | One `APIRouter` per feature or resource. Routers are registered in `main.py` with a consistent prefix and tag. | `APIRouter(prefix="/api/v1/orders", tags=["orders"])` |
| 2 | **Request/Response Models** | All request bodies and responses are Pydantic v2 `BaseModel` subclasses. Request models are frozen (`ConfigDict(frozen=True)`). Response models include only fields safe to expose. | Separate `CreateOrderRequest`, `UpdateOrderRequest`, `OrderResponse` — never reuse the same model for input and output |
| 3 | **Validation Integration** | Pydantic validators live in the model. The route handler receives already-validated data. `HTTPException(422)` is raised automatically by FastAPI for validation failures. | `@field_validator` in the model; no manual validation in route handlers |
| 4 | **OpenAPI Documentation** | Every endpoint has: `summary` (1 line), `description` (multi-line if needed), `response_model`, `responses` dict (all possible status codes), `tags`. | `@router.get("/", summary="List orders", response_model=OrderListResponse, responses={401: {"description": "Unauthorized"}})` |
| 5 | **Versioning Strategy** | URL prefix versioning is the default (`/api/v1/`). Header versioning is an alternative for APIs that cannot change URLs. Never mix versioning strategies. | `APIRouter(prefix="/api/v1")` registered in `main.py` |
| 6 | **Authorization Patterns** | `Depends()` chains enforce authorization. Role-based access uses a factory: `Depends(require_role("admin"))`. Resource-level access checks ownership in the service layer. | `_user: CurrentUser = Depends(require_role("admin"))` |
| 7 | **Rate Limiting** | Rate limiting is applied at the router level using `slowapi` or `fastapi-limiter`. Authentication endpoints have stricter limits than read endpoints. | `@limiter.limit("5/minute")` on login; `@limiter.limit("100/minute")` on read endpoints |
| 8 | **Error Handling** | Custom exception handlers return RFC 7807 Problem Details format. No stack traces in responses. All exceptions are caught and mapped to appropriate HTTP status codes. | `@app.exception_handler(ValidationError)` returns `{"type": "...", "title": "...", "status": 422}` |
| 9 | **CORS Configuration** | CORS origins are explicit and loaded from configuration. `allow_origins=["*"]` with `allow_credentials=True` is a security violation. Development and production CORS configs differ. | `CORSMiddleware(allow_origins=settings.cors_origins)` |
| 10 | **Health Checks** | Three health endpoints: `/health` (basic), `/health/ready` (dependencies ready), `/health/live` (process alive). Used by load balancers and Kubernetes probes. | `@app.get("/health/ready")` checks database connectivity |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("FastAPI APIRouter endpoint Pydantic v2 response_model")` | At CONFIGURE phase — confirm router and model patterns |
| `search_knowledge("FastAPI JWT authentication Depends security")` | When configuring authentication |
| `search_knowledge("FastAPI OpenAPI documentation summary description tags")` | When adding OpenAPI metadata |
| `search_knowledge("FastAPI rate limiting slowapi middleware")` | When configuring rate limiting |
| `search_knowledge("FastAPI health check endpoint lifespan")` | When adding health checks |

## Workflow

### Phase 1: DETECT

**Objective:** Understand the existing project structure before scaffolding.

```bash
# Find FastAPI app entry point
find . -name "main.py" -o -name "app.py" | head -5

# Check existing versioning
grep -rn "prefix.*api" --include="*.py" | head -10

# Check existing auth
grep -rn "get_current_user\|OAuth2\|APIKeyHeader\|HTTPBearer" --include="*.py" | head -10

# Check existing middleware
grep -rn "CORSMiddleware\|add_middleware" --include="*.py" | head -10
```

### Phase 2: CONFIGURE

**Objective:** Set up project-level configuration (versioning, auth, CORS, error handling).

**Project structure:**

```
app/
  main.py              # FastAPI app creation, middleware, router registration
  config.py            # Settings (pydantic-settings BaseSettings)
  dependencies.py      # Shared dependencies (get_db, get_current_user)
  exceptions.py        # Custom exception handlers
  health.py            # Health check endpoints
  routers/
    __init__.py
    v1/
      __init__.py
      [feature].py     # Feature routers
```

### Phase 3: SCAFFOLD

**Objective:** Create the endpoint with full OpenAPI metadata, security, and validation.

See `references/router-template.md` for complete endpoint scaffold.

### Phase 4: SECURE

**Objective:** Add authentication, authorization, and rate limiting.

See `references/security-patterns.md` for JWT and API key patterns.

### Phase 5: DOCUMENT

**Objective:** Verify OpenAPI documentation is complete and accurate.

```bash
# Start the app
uvicorn app.main:app --reload

# Verify OpenAPI spec
curl http://localhost:8000/openapi.json | python -m json.tool | head -50

# Verify docs render
curl -s http://localhost:8000/docs | grep -c "swagger"
```

### Phase 6: VERIFY

**Objective:** Confirm the scaffold is correct and the app starts cleanly.

```bash
# App starts without errors
uvicorn app.main:app --reload &
sleep 2

# Health check passes
curl http://localhost:8000/health

# OpenAPI docs render
curl -s http://localhost:8000/docs | grep -c "swagger"

# Run tests
pytest tests/ -v

# Lint
ruff check .
mypy app/
```

## State Block

```xml
<fastapi-scaffold-state>
  phase: DETECT | CONFIGURE | SCAFFOLD | SECURE | DOCUMENT | VERIFY | COMPLETE
  project_structure: new | existing
  versioning_configured: true | false
  auth_configured: true | false
  cors_configured: true | false
  rate_limiting_configured: true | false
  health_checks_added: true | false
  openapi_complete: true | false
  last_action: [description]
  next_action: [description]
</fastapi-scaffold-state>
```

## Output Templates

### Scaffold Checklist

```markdown
## FastAPI Endpoint Scaffold: [Endpoint Name]

### Endpoint Configuration
- [ ] Router created with `prefix` and `tags`
- [ ] Versioning prefix set: `/api/v1/`
- [ ] Authentication dependency added

### Models
- [ ] Request model(s) created (Pydantic v2, frozen)
- [ ] Response model(s) created
- [ ] Field validators added where needed

### OpenAPI Documentation
- [ ] `summary` set on every route
- [ ] `description` set on routes with complex behavior
- [ ] `response_model` set on every route
- [ ] `responses` dict includes all possible status codes
- [ ] `tags` set on router

### Security
- [ ] Authentication dependency applied
- [ ] Authorization (role/permission) applied if needed
- [ ] Rate limiting applied

### Tests
- [ ] Unit tests for service layer
- [ ] Integration tests with TestClient
- [ ] Authentication tested (valid token, invalid token, missing token)

### Verification
- [ ] App starts without errors
- [ ] `/docs` renders the new endpoints
- [ ] All tests pass
- [ ] `ruff check` passes
- [ ] `mypy` passes
```

## AI Discipline Rules

### CRITICAL: `response_model` Is Not Optional

**WRONG:**
```python
@router.get("/orders/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    return await db.get(Order, order_id)  # Returns ORM object — leaks schema
```

**RIGHT:**
```python
@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    responses={404: {"description": "Order not found"}},
    summary="Get order by ID",
)
async def get_order(
    order_id: int,
    service: OrderReadService = Depends(get_order_read_service),
    _user: CurrentUser = Depends(get_current_user),
) -> OrderResponse:
    order = await service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

### REQUIRED: Security by Default

**WRONG:**
```python
router = APIRouter(prefix="/api/v1/orders")
# No authentication — all endpoints are public
```

**RIGHT:**
```python
router = APIRouter(
    prefix="/api/v1/orders",
    tags=["orders"],
    dependencies=[Depends(get_current_user)],  # Applied to all routes
)
# To make a specific route public, explicitly override:
# @router.get("/public", dependencies=[])
```

### CRITICAL: Versioning from Day One

**WRONG:**
```python
router = APIRouter(prefix="/orders")  # No version prefix
```

**RIGHT:**
```python
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
# When v2 is needed: add /api/v2/orders router alongside v1
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **No `response_model`** | Leaks ORM schema; no response validation; poor OpenAPI docs | Always specify `response_model=` |
| 2 | **No versioning prefix** | Breaking changes require URL changes; no migration path | Use `/api/v1/` from day one |
| 3 | **`allow_origins=["*"]` with credentials** | CORS security violation; enables CSRF | Specify exact origins; never combine `*` with credentials |
| 4 | **Business logic in route handlers** | Untestable; duplicated across routes | Move to service layer |
| 5 | **No OpenAPI metadata** | Black-box API; consumers cannot understand behavior | Add `summary`, `description`, `responses` to every route |
| 6 | **Returning `dict` instead of Pydantic model** | No type safety; no validation; poor docs | Always return Pydantic model instances |
| 7 | **No rate limiting on auth endpoints** | Brute force attacks succeed | Apply strict rate limits to login, register, password reset |
| 8 | **Stack traces in error responses** | Exposes internal implementation; security risk | Custom exception handlers return safe error messages |
| 9 | **No health checks** | Load balancers cannot detect unhealthy instances | Add `/health`, `/health/ready`, `/health/live` |
| 10 | **`DEBUG=True` in production** | Exposes internal details; disables security features | Use environment-based configuration; `DEBUG=False` in production |

## Error Recovery

### OpenAPI docs not rendering new endpoint

```
Symptoms: /docs does not show the new endpoint after adding it

Recovery:
1. Verify the router is registered: grep -r "include_router" app/main.py
2. Verify the prefix is correct: check router prefix vs. expected URL
3. Verify there are no import errors: uvicorn app.main:app --reload shows errors
4. Check for duplicate route paths (FastAPI silently ignores duplicates)
5. Restart uvicorn after fixing
```

### Authentication dependency not working

```
Symptoms: Endpoints return 200 without a valid token

Recovery:
1. Verify the dependency is applied: check router-level vs. route-level dependencies
2. Verify the dependency is not overridden in tests leaking to production
3. Check the dependency function signature: it must raise HTTPException(401) on failure
4. Test with curl: curl -H "Authorization: Bearer invalid" http://localhost:8000/api/v1/orders/
5. Expected: 401 Unauthorized
```

### Pydantic validation errors returning 500

```
Symptoms: Invalid request body returns 500 instead of 422

Recovery:
1. Check for a custom exception handler that catches all exceptions
2. Verify the exception handler does not swallow RequestValidationError
3. Add explicit handler: @app.exception_handler(RequestValidationError)
4. FastAPI's default behavior returns 422 for validation errors — a 500 means a handler is catching it
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `python-feature-slice` | Feature slice provides the service layer; this skill provides the endpoint quality (OpenAPI, security, rate limiting). Use together for complete feature scaffolding. |
| `python-security-review` | After scaffolding, run a security review to verify authentication, authorization, and input validation. |
| `alembic-migration-manager` | When new endpoints require new database schema, use this skill for the migration lifecycle. |
| `pypi-package-scaffold` | When the FastAPI application is packaged as a library, use this skill for package setup. |
