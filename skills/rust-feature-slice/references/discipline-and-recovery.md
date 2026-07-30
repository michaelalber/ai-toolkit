# AI Discipline Rules and Error Recovery

Behavioral guardrails for scaffolding and recovery procedures for when the repo doesn't match the
expected shape.

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
