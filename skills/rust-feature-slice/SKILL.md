---
name: rust-feature-slice
description: >
  Feature-based vertical slice architecture for Rust using Axum routers, handler functions,
  and service traits. No DI framework — dependencies are wired manually via Arc<dyn Trait>
  in Axum State. CQRS via trait separation: reader traits for queries, writer traits for
  commands. Use when scaffolding Rust features, creating Axum feature modules, implementing
  vertical slice architecture in Rust, adding Rust service layers, or organizing Rust code
  by feature rather than technical layer.
  Triggers on: "scaffold rust feature", "axum feature folder", "rust vertical slice",
  "add rust endpoint", "rust service layer", "rust feature module", "rust cqrs".
---

# Rust Feature Slice Architecture

> "Organize code by what it does, not by what it is. A feature folder contains everything needed to deliver a capability — not everything that happens to be a handler."
> -- Adapted from Jimmy Bogard

> "In Rust, there is no DI framework. There is ownership. Design your dependencies so that ownership is clear, and wiring becomes mechanical."
> -- Rust Architecture Principle

## Core Philosophy

Vertical slice architecture in Rust organizes code by feature (domain capability) rather than technical layer (handlers, services, repositories). Each feature is a Rust module containing everything needed to deliver that capability: router, handlers, service trait, service implementation, request/response types, and tests.

Rust has no dependency injection framework. Dependencies are wired manually using `Arc<dyn Trait>` stored in Axum's `State<AppState>`. This is not a limitation — it is explicit, compile-time-verified dependency wiring. The `AppState` struct is the composition root.

CQRS in Rust is a naming convention enforced by trait design: `OrderReader` (query methods) and `OrderWriter` (command methods) are separate traits, potentially implemented by the same struct. This separation makes the read/write boundary explicit without requiring a library.

**Non-Negotiable Constraints:**

1. **Feature module isolation** — no `use crate::features::other_feature::` in handlers. Features communicate through shared types in a `common` or `domain` module, not through direct imports.
2. **Service traits, not concrete types** — `Arc<dyn OrderService>` in `AppState`, not `Arc<OrderServiceImpl>`. This enables testing with mock implementations.
3. **`Arc<dyn Trait>` for shared state** — not `Mutex<ConcreteType>`. The trait defines the contract; the `Arc` provides shared ownership.
4. **`Result<T, AppError>` on all handlers** — handlers return `Result<impl IntoResponse, AppError>`. No panics, no unwrap in handler code.
5. **Handler thinness** — handlers extract request data, call the service, and return the response. Business logic belongs in the service, not the handler.

## Domain Principles Table

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

## Workflow

```
DETECT (before scaffolding)
    [ ] Check for existing AppState struct (src/state.rs or src/app.rs)
    [ ] Check for existing features/ directory structure
    [ ] Identify Rust edition and async runtime (Cargo.toml)
    [ ] Check for existing error types (AppError)
    [ ] Identify database access pattern (SQLx, Diesel, none)

        |
        v

SCAFFOLD (create feature module)
    [ ] Create src/features/<name>/mod.rs (re-exports)
    [ ] Create src/features/<name>/router.rs (Axum Router with State)
    [ ] Create src/features/<name>/service.rs (trait + impl)
    [ ] Create src/features/<name>/models.rs (request/response types)
    [ ] Create src/features/<name>/errors.rs (feature error type)
    [ ] Create tests/features/<name>/integration_test.rs

        |
        v

REGISTER (wire into app)
    [ ] Add service to AppState struct
    [ ] Add Arc<dyn Trait> initialization in app startup
    [ ] Merge feature Router into main app Router
    [ ] Add From<FeatureError> for AppError

        |
        v

VERIFY
    [ ] cargo build (no errors)
    [ ] cargo test (all tests pass)
    [ ] cargo clippy -- -D warnings (no warnings)
```

**Exit criteria:** Feature module created, registered in app, tests pass, Clippy clean.

## State Block

```
<rust-feature-slice-state>
phase: DETECT | SCAFFOLD | REGISTER | VERIFY | COMPLETE
feature_name: [name]
edition: [2015 | 2018 | 2021]
async_runtime: [tokio | async-std | none]
app_state_exists: [true | false]
features_dir_exists: [true | false]
app_error_exists: [true | false]
files_created: [comma-separated list]
build_status: [pass | fail | not-run]
test_status: [pass | fail | not-run]
last_action: [description]
next_action: [description]
</rust-feature-slice-state>
```

## Output Templates

### Scaffold Checklist

```markdown
## Rust Feature Slice Scaffold: [feature-name]

### Files to Create
- [ ] `src/features/[name]/mod.rs`
- [ ] `src/features/[name]/router.rs`
- [ ] `src/features/[name]/service.rs`
- [ ] `src/features/[name]/models.rs`
- [ ] `src/features/[name]/errors.rs`
- [ ] `tests/features/[name]/integration_test.rs`

### Files to Modify
- [ ] `src/state.rs` — add `Arc<dyn [Name]Service>` field
- [ ] `src/app.rs` or `src/main.rs` — merge feature Router, initialize service
- [ ] `src/errors.rs` — add `From<[Name]Error> for AppError`

### Verification
- [ ] `cargo build` passes
- [ ] `cargo test` passes
- [ ] `cargo clippy -- -D warnings` passes
```

### Feature Module Template (in output)

```rust
// src/features/orders/mod.rs
// <AI-Generated START>
pub mod errors;
pub mod models;
pub mod router;
pub mod service;

pub use router::orders_router;
pub use service::OrderService;
// <AI-Generated END>
```

## AI Discipline Rules

### CRITICAL: Service Traits, Not Concrete Types in AppState

**WRONG:**
```rust
pub struct AppState {
    pub order_service: Arc<OrderServiceImpl>,
}
```

**RIGHT:**
```rust
pub struct AppState {
    pub order_service: Arc<dyn OrderService>,
}
```

The trait in `AppState` enables mock injection in tests. The concrete type is an implementation detail.

### CRITICAL: Handlers Must Be Thin

**WRONG:**
```rust
async fn create_order(
    State(state): State<AppState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> {
    // 50 lines of business logic here
    let validated = if req.items.is_empty() { ... };
    let total = req.items.iter().map(|i| i.price * i.qty).sum();
    // ... more logic
}
```

**RIGHT:**
```rust
async fn create_order(
    State(state): State<AppState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> {
    let order = state.order_service.create_order(req).await?;
    Ok((StatusCode::CREATED, Json(order)))
}
```

### REQUIRED: async_trait or Native Async Traits

For Rust < 1.75, use `async_trait`:
```rust
#[async_trait::async_trait]
pub trait OrderService: Send + Sync {
    async fn create_order(&self, req: CreateOrderRequest) -> Result<Order, OrderError>;
}
```

For Rust 1.75+, use native async traits:
```rust
pub trait OrderService: Send + Sync {
    fn create_order(&self, req: CreateOrderRequest)
        -> impl Future<Output = Result<Order, OrderError>> + Send;
}
```

Note both patterns in the scaffold and recommend native async traits for Rust 1.75+.

## Anti-Patterns Table

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

## Error Recovery

### AppState Already Exists with Different Structure

```
Symptoms: src/state.rs exists but uses a different pattern (e.g., concrete types)

Recovery:
1. Read the existing AppState structure
2. Report the current pattern to the user
3. Ask: "The existing AppState uses [pattern]. Should I adapt the new feature
   to match the existing pattern, or refactor AppState to use Arc<dyn Trait>?"
4. Do NOT silently change the existing AppState pattern
5. If user wants to keep existing pattern: scaffold the feature to match
```

### No Existing Features Directory

```
Symptoms: src/features/ does not exist

Recovery:
1. Create src/features/mod.rs with the new feature module declaration
2. Note in the scaffold output: "Created src/features/ directory structure"
3. Add `pub mod features;` to src/lib.rs or src/main.rs
4. Proceed with the feature scaffold
```

### async_trait Version Conflict

```
Symptoms: Cargo.toml has async_trait but at an incompatible version

Recovery:
1. Check the Rust edition and version
2. If Rust 1.75+: recommend removing async_trait and using native async traits
3. If Rust < 1.75: check async_trait version compatibility
4. Report the conflict and recommended resolution before scaffolding
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `axum-scaffolder` | Provides the HTTP layer patterns (middleware, OpenAPI, auth). Use `rust-feature-slice` for module organization; use `axum-scaffolder` for HTTP infrastructure. |
| `sqlx-migration-manager` | When the feature requires database access, `sqlx-migration-manager` provides the safe migration and query patterns for the service implementation. |
| `rust-architecture-checklist` | After scaffolding, run `rust-architecture-checklist` to verify the feature follows ownership, trait, and error handling conventions. |
| `rust-security-review` | After scaffolding, run `rust-security-review` to verify the feature's auth middleware, input validation, and error handling are secure. |
| `dotnet-vertical-slice` | Parallel skill for .NET/Blazor codebases. Same vertical slice philosophy; different ecosystem. |
