# Domain Principles, Knowledge Lookups, and Anti-Patterns

The design judgment behind `rust-feature-slice`. SKILL.md carries the constraints and workflow;
this file carries the reasoning and the failure modes to avoid.

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Feature Isolation** | Each feature module is a self-contained unit. It owns its router, handlers, service trait, and types. It does not reach into other feature modules. Cross-feature dependencies go through shared domain types. | Enforce with `pub(crate)` on internal types; use `use crate::domain::` for shared types, never `use crate::features::other::`. |
| 2 | **Service Trait Autonomy** | The service trait defines the feature's contract. The implementation is an internal detail. Tests use mock implementations. Production uses the real implementation. The handler never knows which it is talking to. | Define `pub trait OrderService: Send + Sync` in the feature module; implement in a separate struct; inject via `Arc<dyn OrderService>`. |
| 3 | **Minimal Trait Surface** | Service traits should expose only the methods that handlers actually call. A trait with 20 methods is a god object. A trait with 3 methods is a focused contract. | Start with the minimum methods needed by the handlers. Add methods only when a new handler requires them. |
| 4 | **State Injection via `Arc`** | Axum's `State<AppState>` is the composition root. `AppState` holds `Arc<dyn Trait>` for each service. Handlers extract the service they need via `State(state): State<AppState>`. | Define `AppState` with `Arc<dyn Trait>` fields; use `FromRef` for sub-state extraction when handlers need only one service. |
| 5 | **Read/Write Trait Separation** | Query methods (read-only, no side effects) and command methods (mutate state) are defined in separate traits. This makes the CQRS boundary explicit and enables separate implementations if needed. | Define `OrderReader` and `OrderWriter` traits; implement both on `OrderRepository`; inject separately if the handler only needs one. |
| 6 | **Immutable Request Types** | Request types are plain structs with `#[derive(Deserialize)]`. They are immutable value objects. Validation happens in the handler or a dedicated validator, not in the request type itself. | Define `CreateOrderRequest` with `#[derive(Deserialize, ToSchema)]`; validate in handler before calling service. |
| 7 | **Explicit Error Types** | Each feature defines its own error type using `thiserror`. The `AppError` type in the router layer converts feature errors to HTTP responses. This keeps domain errors separate from HTTP concerns. | Define `OrderError` with `thiserror`; implement `From<OrderError> for AppError`; handlers use `?` to propagate. |
| 8 | **Validator Co-Location** | Input validation logic lives in the feature module, not in a global validator. The feature knows what valid input looks like; the framework does not. | Define validation functions or use the `validator` crate in the feature module; call from the handler before the service call. |
| 9 | **Handler Thinness** | A handler that is longer than 20 lines is doing too much. Extract business logic to the service. Extract validation to a validator. The handler's job is: extract → validate → call service → return response. | If a handler exceeds 20 lines, identify what can move to the service or validator. |
| 10 | **Test Organization** | Unit tests for the service use mock implementations of dependencies. Integration tests use `axum::test` to test the full handler stack. Both live in the feature module. | `#[cfg(test)]` module in `service.rs` for unit tests; `tests/features/<name>/` for integration tests. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Axum router handler state Arc dependency injection")` | During scaffold — verify Axum state injection patterns |
| `search_knowledge("Rust async trait service layer tokio")` | During service trait design — verify async trait patterns |
| `search_knowledge("Rust thiserror error handling Result")` | During error type design — verify thiserror patterns |
| `search_knowledge("Axum testing TestClient integration test")` | During test scaffold — verify Axum test patterns |
| `search_knowledge("Rust CQRS command query separation trait")` | During CQRS design — verify trait separation patterns |

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Cross-Feature Imports** | `use crate::features::users::User` in the orders feature creates coupling. Changes to the users feature break the orders feature. | Shared types belong in `crate::domain` or `crate::common`. Features import from there, not from each other. |
| 2 | **Concrete Types in AppState** | `Arc<OrderServiceImpl>` in AppState makes testing impossible without the real implementation. | Use `Arc<dyn OrderService>`. Inject a mock in tests, the real impl in production. |
| 3 | **Fat Handlers** | Business logic in handlers cannot be unit-tested without an HTTP request. | Move business logic to the service. Handlers are thin: extract → validate → call → respond. |
| 4 | **Mutex<ConcreteType> for State** | `Mutex<OrderRepository>` in AppState serializes all requests through a single lock. | Use `Arc<dyn OrderService>` where the service manages its own concurrency (e.g., a connection pool). |
| 5 | **God Service Trait** | A service trait with 20 methods is a god object. Every handler depends on the full trait even if it uses 2 methods. | Split into focused traits: `OrderReader` (queries) and `OrderWriter` (commands). |
| 6 | **Validation in Request Types** | Putting validation logic in `impl CreateOrderRequest` mixes data and behavior. | Validate in the handler or a dedicated validator function. Request types are pure data. |
| 7 | **Panic in Handlers** | `.unwrap()` in a handler panics the entire request, potentially crashing the server. | Return `Result<impl IntoResponse, AppError>`. Use `?` to propagate errors. |
| 8 | **String Errors in Service Traits** | `Result<T, String>` in service traits loses type information and makes error handling impossible. | Use `thiserror` error enums. Implement `From<ServiceError> for AppError`. |
| 9 | **Missing Router Registration** | Creating a feature module but forgetting to merge its Router into the app means the routes are never served. | Always verify with `cargo test` that the routes are reachable. |
| 10 | **No Integration Tests** | Unit tests for the service don't verify that the handler correctly wires the service call. | Write at least one integration test per handler using `axum::test`. |
