---
name: python-feature-slice
description: Scaffolds feature-based Python architecture using FastAPI routers, Pydantic v2 models, and a service layer. Python analog of dotnet-vertical-slice — no mediator library, uses FastAPI Depends() for dependency injection and structural CQRS conventions. Use when creating feature-based Python projects, adding FastAPI features, scaffolding service layers, or organizing Python code by feature. Triggers on phrases like "scaffold python feature", "create python slice", "fastapi feature folder", "python vertical slice", "add python endpoint", "python feature architecture", "python service layer".
---

# Python Feature Slice Architecture

> "The best code is code that never has to be written."
> -- Jeff Atwood

> "Organize around business capabilities, not technical layers."
> -- Sam Newman, *Building Microservices*

## Core Philosophy

Feature slice architecture organizes code by business capability, not by technical layer. Instead of `controllers/`, `services/`, `repositories/`, you have `features/orders/`, `features/users/`, `features/payments/`. Each feature is a self-contained vertical slice through the application stack.

In Python with FastAPI, the mediator pattern (FreeMediator in .NET) is replaced by FastAPI's native `Depends()` system. Service classes are injected directly into route handlers via dependency injection. CQRS separation is a structural and naming convention — `OrderReadService` vs `OrderWriteService` — not a library contract.

**Non-Negotiable Constraints:**
1. **Feature isolation** — no cross-feature imports; features communicate through shared domain models only
2. **Service layer owns business logic** — routers are thin; no business logic in route handlers
3. **Pydantic v2 models** for all request/response types — no bare `dict` returns
4. **`typing.Protocol`** for service interfaces — enables testing without concrete implementations
5. **Async-first** — all I/O operations use `async def`; no blocking calls in async context

**What this skill is NOT:**
- It is NOT a microservices guide — feature slices are within a single application
- It is NOT prescriptive about the number of features — start with what you have
- It is NOT a replacement for domain-driven design — it is compatible with DDD but does not require it

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature is a Python package with its own router, service, models, and tests. No feature imports from another feature's internal modules. | `features/orders/` never imports from `features/users/` internals — only from `shared/` |
| 2 | **Service Autonomy** | Each feature's service class owns its business logic. The router calls the service; the service calls the repository or external APIs. The router never contains business logic. | Route handler: `return await service.create_order(command)` — nothing else |
| 3 | **Minimal Abstractions** | Add abstractions only when they earn their complexity. A `Protocol` interface is worth it when you have multiple implementations or need to mock in tests. A base class is not worth it for a single concrete implementation. | Use `Protocol` for services; avoid abstract base classes unless multiple implementations exist |
| 4 | **Dependency Injection via `Depends()`** | FastAPI's `Depends()` is the DI container. Service instances are created in `dependencies.py` and injected into route handlers. No global state, no service locator pattern. | `async def create_order(command: CreateOrderCommand, service: OrderWriteService = Depends(get_order_write_service))` |
| 5 | **Read/Write Service Separation** | Read operations (queries) and write operations (commands) are in separate service classes. This is structural CQRS — no library required. Read services return data; write services mutate state and return minimal confirmation. | `OrderReadService.get_order()`, `OrderReadService.list_orders()` vs `OrderWriteService.create_order()`, `OrderWriteService.cancel_order()` |
| 6 | **Pydantic Model Immutability** | Request and response models are immutable (`model_config = ConfigDict(frozen=True)`). Domain models may be mutable. Never return ORM objects directly from route handlers. | `class CreateOrderRequest(BaseModel): model_config = ConfigDict(frozen=True)` |
| 7 | **Explicit Dependencies** | Every dependency is explicit in the function signature. No hidden global state, no thread-local storage, no request-scoped globals. | All dependencies appear in `Depends()` chains — nothing is imported as a module-level singleton |
| 8 | **Validator Co-Location** | Pydantic validators live in the model file, not in the service. The service receives already-validated data. | `@field_validator("email")` in `CreateUserRequest`, not in `UserWriteService` |
| 9 | **Router Thinness** | Route handlers contain: parameter extraction, service call, response mapping. Nothing else. If a route handler is more than 10 lines, business logic has leaked into it. | Route handler = extract → call service → return response |
| 10 | **Test Proximity** | Tests live next to the feature they test. `tests/features/orders/` mirrors `features/orders/`. Unit tests mock the service; integration tests use `TestClient`. | `tests/features/orders/test_router.py`, `tests/features/orders/test_service.py` |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions in authoritative references.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("FastAPI APIRouter feature folder dependency injection")` | At DETECT phase — confirm feature folder and DI patterns |
| `search_knowledge("Pydantic v2 model validator BaseModel ConfigDict")` | When scaffolding request/response models |
| `search_knowledge("python clean architecture service layer protocol")` | When designing service interfaces |
| `search_knowledge("pytest FastAPI TestClient async fixture")` | When scaffolding tests |
| `search_knowledge("CQRS command query separation python service")` | When designing read/write service separation |

## Workflow

### Phase 1: DETECT

**Objective:** Understand the existing codebase structure before scaffolding.

**Steps:**

1. Identify existing project structure (flat, layered, or already feature-based)
2. Identify the FastAPI app entry point (`main.py`, `app.py`, or `app/__init__.py`)
3. Identify existing router registration pattern
4. Identify existing database/ORM setup (SQLAlchemy, Tortoise, raw)
5. Identify existing authentication/authorization pattern

```bash
# Find FastAPI app entry point
find . -name "main.py" -o -name "app.py" | head -5

# Find existing routers
grep -rn "APIRouter\|include_router" --include="*.py" | head -20

# Find existing project structure
find . -type d -not -path "./.git/*" -not -path "./__pycache__/*" | head -30
```

### Phase 2: SCAFFOLD

**Objective:** Create the feature folder structure with all required files.

**Feature folder structure:**

```
features/
  <name>/
    __init__.py          # Empty or exports public API
    router.py            # FastAPI APIRouter — thin handlers only
    service.py           # Protocol interface + concrete implementation
    models.py            # Pydantic v2 request/response models
    dependencies.py      # Depends() factory functions
tests/
  features/
    <name>/
      __init__.py
      test_router.py     # Integration tests with TestClient
      test_service.py    # Unit tests with mocked dependencies
```

See `references/feature-folder-template.md` for file-by-file content.

### Phase 3: REGISTER

**Objective:** Wire the new feature router into the FastAPI application.

```python
# In main.py or app/routers.py
from features.orders.router import router as orders_router

app.include_router(orders_router, prefix="/api/v1")
```

### Phase 4: VERIFY

**Objective:** Confirm the scaffold is correct and tests pass.

```bash
# Verify the app starts without errors
uvicorn app.main:app --reload &
sleep 2
curl http://localhost:8000/docs  # OpenAPI UI should render

# Run tests
pytest tests/features/<name>/ -v

# Check for cross-feature imports (should return empty)
grep -rn "from features\." features/ --include="*.py" | grep -v "from features\.<name>"
```

## State Block

```xml
<python-feature-slice-state>
  phase: DETECT | SCAFFOLD | REGISTER | VERIFY | COMPLETE
  feature_name: [name]
  existing_structure: flat | layered | feature-based | unknown
  app_entry_point: [file path]
  router_registered: true | false
  tests_scaffolded: true | false
  read_service_created: true | false
  write_service_created: true | false
  last_action: [description]
  next_action: [description]
</python-feature-slice-state>
```

## Output Templates

### Scaffold Checklist

```markdown
## Feature Slice Scaffold: [Feature Name]

### Files Created
- [ ] `features/<name>/__init__.py`
- [ ] `features/<name>/router.py`
- [ ] `features/<name>/service.py`
- [ ] `features/<name>/models.py`
- [ ] `features/<name>/dependencies.py`
- [ ] `tests/features/<name>/__init__.py`
- [ ] `tests/features/<name>/test_router.py`
- [ ] `tests/features/<name>/test_service.py`

### Registration
- [ ] Router added to `main.py` / `app/routers.py`
- [ ] Prefix set: `/api/v1/<name>`
- [ ] Tags set: `["<name>"]`

### Verification
- [ ] `uvicorn` starts without errors
- [ ] `/docs` renders the new endpoints
- [ ] `pytest tests/features/<name>/` passes
- [ ] No cross-feature imports detected
```

### Feature Folder Structure Diagram

```
project/
├── features/
│   └── orders/
│       ├── __init__.py
│       ├── router.py          ← thin: extract, call service, return
│       ├── service.py         ← business logic; Protocol + concrete
│       ├── models.py          ← Pydantic v2 request/response models
│       └── dependencies.py    ← Depends() factory functions
├── shared/
│   ├── database.py            ← SQLAlchemy session factory
│   └── auth.py                ← get_current_user dependency
├── tests/
│   └── features/
│       └── orders/
│           ├── test_router.py ← TestClient integration tests
│           └── test_service.py← unit tests with mocked deps
└── main.py                    ← app creation + router registration
```

## AI Discipline Rules

### CRITICAL: No Business Logic in Routers

**WRONG:**
```python
@router.post("/orders")
async def create_order(request: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    # Validate inventory
    item = await db.execute(select(Item).where(Item.id == request.item_id))
    if item.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # Create order
    order = Order(item_id=request.item_id, quantity=request.quantity)
    db.add(order)
    await db.commit()
    return order
```

**RIGHT:**
```python
@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    service: OrderWriteService = Depends(get_order_write_service)
) -> OrderResponse:
    return await service.create_order(request)
```

### REQUIRED: Use Protocol for Service Interfaces

**WRONG:**
```python
class OrderWriteService:
    def __init__(self, db: AsyncSession):
        self.db = db
```

**RIGHT:**
```python
from typing import Protocol

class OrderWriteServiceProtocol(Protocol):
    async def create_order(self, request: CreateOrderRequest) -> OrderResponse: ...
    async def cancel_order(self, order_id: int) -> None: ...

class OrderWriteService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        ...
```

### CRITICAL: No Cross-Feature Imports

**WRONG:**
```python
# In features/orders/service.py
from features.users.service import UserReadService  # Cross-feature import!
```

**RIGHT:**
```python
# In features/orders/service.py
from shared.auth import get_current_user  # Shared module — OK
# Or inject UserReadService via Depends() in the router
```

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Business logic in route handlers** | Route handlers become untestable; logic is duplicated across routes | Move all business logic to service classes |
| 2 | **Cross-feature imports** | Creates hidden coupling; changing one feature breaks another | Use `shared/` for cross-cutting concerns; inject via `Depends()` |
| 3 | **Returning ORM objects from routes** | Exposes database schema; breaks when schema changes; no serialization control | Always return Pydantic response models |
| 4 | **Global service instances** | Prevents testing with mocks; creates shared state | Use `Depends()` factory functions for all service instances |
| 5 | **Mixing read and write in one service** | Service grows unbounded; read and write have different performance profiles | Separate `ReadService` and `WriteService` per feature |
| 6 | **Validators in service layer** | Service receives unvalidated data; validation logic is duplicated | Validators belong in Pydantic models; service receives validated data |
| 7 | **Synchronous I/O in async handlers** | Blocks the event loop; destroys FastAPI's concurrency advantage | Use `async def` for all I/O; use `asyncio.to_thread()` for blocking calls |
| 8 | **No `response_model` on routes** | FastAPI cannot validate or document the response; sensitive fields may leak | Always specify `response_model=` on every route |
| 9 | **Tests in the feature folder** | Mixes production code and test code; complicates packaging | Tests live in `tests/features/<name>/` mirroring the feature structure |
| 10 | **One giant `features/` file** | Defeats the purpose of feature isolation; creates merge conflicts | Each feature is a directory (Python package), not a file |

## Error Recovery

### Cross-feature import detected

```
Symptoms: `grep -rn "from features\." features/` returns imports between features

Recovery:
1. Identify what is being imported (a model, a service, a utility)
2. If it is a shared model: move it to `shared/models.py`
3. If it is a service: inject it via `Depends()` in the router, not imported in the service
4. If it is a utility: move it to `shared/utils.py`
5. Update imports in both features
6. Re-run the grep check to confirm no cross-feature imports remain
```

### Service grows too large

```
Symptoms: Service file exceeds ~200 lines; methods are unrelated to each other

Recovery:
1. Identify sub-domains within the feature (e.g., "orders" has "fulfillment" and "billing")
2. Split into sub-services: `OrderFulfillmentService`, `OrderBillingService`
3. Keep the feature folder — sub-services live in the same feature package
4. Update `dependencies.py` to provide each sub-service
5. Update route handlers to inject the specific sub-service they need
```

### Router handler grows too large

```
Symptoms: Route handler exceeds 10 lines; contains conditional logic

Recovery:
1. Identify the business logic in the handler
2. Move it to the service layer
3. The handler should be: extract parameters → call service → return response
4. If the handler needs multiple service calls, that is an orchestration concern — create an orchestration method in the service
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `fastapi-scaffolder` | Provides endpoint-level scaffolding patterns (OpenAPI metadata, security, rate limiting). Use together when scaffolding a new feature with full endpoint quality. |
| `alembic-migration-manager` | When a new feature requires database schema changes, use this skill to manage the migration lifecycle. |
| `python-security-review` | After scaffolding, run a security review to verify the new feature's authentication, authorization, and input validation. |
| `python-arch-review` | Architecture quality gate. Run after scaffolding multiple features to verify the feature isolation and coupling metrics. |
