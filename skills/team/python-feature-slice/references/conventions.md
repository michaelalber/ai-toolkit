# Python Feature Slice Conventions

Depth behind the Core Philosophy constraints: principles, knowledge-base grounding, discipline
rules, anti-patterns, and recovery. File-by-file scaffold content is in `feature-folder-template.md`;
read/write CQRS conventions in `cqrs-conventions.md`.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature is a package with its own router, service, models, tests; no imports from another feature's internals. | `features/orders/` imports only from `shared/`, never `features/users/` internals |
| 2 | **Service Autonomy** | The service owns business logic; the router calls the service; the service calls the repo/APIs. | Handler: `return await service.create_order(command)` — nothing else |
| 3 | **Minimal Abstractions** | Add a `Protocol` when there are multiple implementations or mocking needs; skip base classes for a single concrete impl. | `Protocol` for services; no ABCs unless multiple implementations exist |
| 4 | **DI via `Depends()`** | FastAPI's `Depends()` is the DI container; services created in `dependencies.py`, no service locator. | `service: OrderWriteService = Depends(get_order_write_service)` |
| 5 | **Read/Write Separation** | Structural CQRS: read services return data, write services mutate and return minimal confirmation. | `OrderReadService.get_order()` vs `OrderWriteService.create_order()` |
| 6 | **Pydantic Immutability** | Request/response models are frozen; never return ORM objects from handlers. | `model_config = ConfigDict(frozen=True)` |
| 7 | **Explicit Dependencies** | Every dependency is in the signature; no module-level singletons or request-scoped globals. | All deps appear in `Depends()` chains |
| 8 | **Validator Co-Location** | Pydantic validators live in the model; the service receives validated data. | `@field_validator("email")` in the request model |
| 9 | **Router Thinness** | Handler = extract → call service → return. > 10 lines means logic leaked in. | extract → call service → return response |
| 10 | **Test Proximity** | Tests mirror the feature: `tests/features/orders/`. Unit tests mock the service; integration uses `TestClient`. | `tests/features/orders/test_router.py`, `test_service.py` |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("FastAPI APIRouter feature folder dependency injection")` | DETECT — feature folder + DI patterns |
| `search_knowledge("Pydantic v2 model validator BaseModel ConfigDict")` | Scaffolding request/response models |
| `search_knowledge("python clean architecture service layer protocol")` | Designing service interfaces |
| `search_knowledge("pytest FastAPI TestClient async fixture")` | Scaffolding tests |
| `search_knowledge("CQRS command query separation python service")` | Designing read/write separation |

## Discipline Rules

- **No business logic in routers.** A handler that queries the DB, validates inventory, and commits
  is wrong. *Right:* `async def create_order(request, service=Depends(...)) -> OrderResponse: return
  await service.create_order(request)` with `response_model` + `status_code` set.
- **Use `Protocol` for service interfaces.** Declare `OrderWriteServiceProtocol(Protocol)` with the
  method signatures; the concrete `OrderWriteService` implements it — enables mocking in tests.
- **No cross-feature imports.** `features/orders/service.py` must not
  `from features.users.service import ...`. Use `shared/` for cross-cutting concerns, or inject the
  other feature's service via `Depends()` in the router.

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | Business logic in route handlers | Untestable handlers; logic duplicated across routes | Move all business logic to service classes |
| 2 | Cross-feature imports | Hidden coupling; one feature's change breaks another | `shared/` for cross-cutting; inject via `Depends()` |
| 3 | Returning ORM objects from routes | Exposes schema; breaks on schema change; no serialization control | Always return Pydantic response models |
| 4 | Global service instances | Prevents mocking; creates shared state | `Depends()` factory functions for all services |
| 5 | Mixing read and write in one service | Service grows unbounded; different performance profiles | Separate `ReadService` and `WriteService` |
| 6 | Validators in the service layer | Service gets unvalidated data; duplicated validation | Validators in Pydantic models |
| 7 | Synchronous I/O in async handlers | Blocks the event loop; kills concurrency | `async def` for I/O; `asyncio.to_thread()` for blocking |
| 8 | No `response_model` on routes | No response validation/docs; sensitive fields can leak | Always set `response_model=` |
| 9 | Tests in the feature folder | Mixes production and test code; complicates packaging | `tests/features/<name>/` mirroring the feature |
| 10 | One giant `features/` file | Defeats feature isolation; merge conflicts | Each feature is a directory (package), not a file |

## Error Recovery

**Cross-feature import detected** (`grep -rn "from features\." features/` shows inter-feature imports):
1. Identify what's imported (model, service, utility)
2. Shared model → `shared/models.py`; service → inject via `Depends()` in the router; utility → `shared/utils.py`
3. Update imports in both features; re-run the grep to confirm none remain

**Service grows too large** (> ~200 lines, unrelated methods):
1. Identify sub-domains (e.g., "orders" has "fulfillment" and "billing")
2. Split into sub-services (`OrderFulfillmentService`, `OrderBillingService`) in the same feature package
3. Update `dependencies.py` to provide each; route handlers inject the specific one they need

**Router handler grows too large** (> 10 lines, conditional logic):
1. Move the business logic to the service layer
2. Handler stays: extract → call service → return
3. Multiple service calls = orchestration → add an orchestration method on the service
