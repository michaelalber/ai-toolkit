# Axum State Injection Patterns

Patterns for injecting dependencies into Axum handlers via `State<AppState>`.
Covers `AppState` design, `FromRef` for sub-state extraction, `Extension` vs. `State`,
and testing with mock service implementations.

---

## Pattern 1: Single AppState with All Services

The simplest pattern. All services live in one `AppState` struct.

```rust
// <AI-Generated START>
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub order_service: Arc<dyn OrderService>,
    pub user_service: Arc<dyn UserService>,
    pub notification_service: Arc<dyn NotificationService>,
}

// In handlers:
async fn create_order(
    State(state): State<AppState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> {
    let order = state.order_service.create_order(req).await?;
    Ok((StatusCode::CREATED, Json(order)))
}
// <AI-Generated END>
```

**When to use:** Most applications. Simple, explicit, easy to understand.

**Tradeoff:** Every handler receives the full AppState even if it only needs one service. This is fine — `Arc` is cheap to clone.

---

## Pattern 2: `FromRef` for Sub-State Extraction

When handlers should only receive the service they need, use `FromRef` to extract sub-state.

```rust
// <AI-Generated START>
use axum::extract::FromRef;
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub order_service: Arc<dyn OrderService>,
    pub user_service: Arc<dyn UserService>,
}

// Implement FromRef to extract individual services
impl FromRef<AppState> for Arc<dyn OrderService> {
    fn from_ref(state: &AppState) -> Self {
        state.order_service.clone()
    }
}

impl FromRef<AppState> for Arc<dyn UserService> {
    fn from_ref(state: &AppState) -> Self {
        state.user_service.clone()
    }
}

// Handlers can now extract just the service they need:
async fn create_order(
    State(order_service): State<Arc<dyn OrderService>>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> {
    let order = order_service.create_order(req).await?;
    Ok((StatusCode::CREATED, Json(order)))
}
// <AI-Generated END>
```

**When to use:** When you want handlers to declare their dependencies explicitly. Useful for large applications where AppState has many services.

**Tradeoff:** More boilerplate (`FromRef` implementations). Handlers are more self-documenting.

---

## Pattern 3: Nested State for Feature Isolation

Group related services into feature-specific state structs.

```rust
// <AI-Generated START>
#[derive(Clone)]
pub struct OrdersState {
    pub service: Arc<dyn OrderService>,
}

#[derive(Clone)]
pub struct UsersState {
    pub service: Arc<dyn UserService>,
}

#[derive(Clone)]
pub struct AppState {
    pub orders: OrdersState,
    pub users: UsersState,
}

impl FromRef<AppState> for OrdersState {
    fn from_ref(state: &AppState) -> Self {
        state.orders.clone()
    }
}

// Feature router uses its own state type:
pub fn orders_router() -> Router<AppState> {
    Router::new()
        .route("/", post(create_order))
}

async fn create_order(
    State(state): State<OrdersState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> {
    let order = state.service.create_order(req).await?;
    Ok((StatusCode::CREATED, Json(order)))
}
// <AI-Generated END>
```

**When to use:** Large applications with many features. Each feature router only sees its own state.

---

## Pattern 4: `Extension` vs. `State`

`State` is preferred over `Extension` for application services. Use `Extension` only for request-scoped data (e.g., authenticated user claims from middleware).

```rust
// <AI-Generated START>
// CORRECT: Use State for application services
async fn get_order(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<impl IntoResponse, AppError> {
    let order = state.order_service.get_order(id).await?;
    Ok(Json(order))
}

// CORRECT: Use Extension for request-scoped data (set by middleware)
async fn get_order_authenticated(
    State(state): State<AppState>,
    Extension(claims): Extension<Claims>,  // Set by JWT middleware
    Path(id): Path<Uuid>,
) -> Result<impl IntoResponse, AppError> {
    // Verify the user owns this order
    let order = state.order_service.get_order_for_user(id, claims.user_id).await?;
    Ok(Json(order))
}
// <AI-Generated END>
```

**Why `State` over `Extension` for services:**
- `State` is type-checked at compile time (missing state = compile error)
- `Extension` panics at runtime if the extension is not set
- `State` is more explicit about what the handler depends on

---

## Pattern 5: Testing with Mock Implementations

The key benefit of `Arc<dyn Trait>` in AppState: inject mocks in tests.

```rust
// <AI-Generated START>
#[cfg(test)]
mod tests {
    use super::*;
    use axum::{body::Body, http::{Request, StatusCode}};
    use tower::ServiceExt;
    use std::sync::Mutex;

    // Mock implementation for testing
    struct MockOrderService {
        orders: Mutex<Vec<OrderResponse>>,
    }

    impl MockOrderService {
        fn new() -> Arc<Self> {
            Arc::new(Self {
                orders: Mutex::new(vec![]),
            })
        }

        fn with_order(self: Arc<Self>, order: OrderResponse) -> Arc<Self> {
            self.orders.lock().unwrap().push(order);
            self
        }
    }

    #[async_trait::async_trait]
    impl OrderService for MockOrderService {
        async fn get_order(&self, id: Uuid) -> Result<OrderResponse, OrderError> {
            self.orders
                .lock()
                .unwrap()
                .iter()
                .find(|o| o.id == id)
                .cloned()
                .ok_or(OrderError::NotFound { id })
        }

        async fn create_order(&self, req: CreateOrderRequest) -> Result<OrderResponse, OrderError> {
            let order = OrderResponse {
                id: Uuid::new_v4(),
                customer_id: req.customer_id,
                status: "pending".to_string(),
                total_cents: 0,
                created_at: chrono::Utc::now(),
            };
            self.orders.lock().unwrap().push(order.clone());
            Ok(order)
        }
    }

    fn test_app(mock: Arc<dyn OrderService>) -> axum::Router {
        let state = AppState { order_service: mock };
        axum::Router::new()
            .nest("/api/v1/orders", orders_router())
            .with_state(state)
    }

    #[tokio::test]
    async fn test_get_order_returns_200() {
        let order_id = Uuid::new_v4();
        let mock = MockOrderService::new().with_order(OrderResponse {
            id: order_id,
            customer_id: Uuid::new_v4(),
            status: "pending".to_string(),
            total_cents: 1000,
            created_at: chrono::Utc::now(),
        });

        let app = test_app(mock);
        let response = app
            .oneshot(
                Request::builder()
                    .uri(format!("/api/v1/orders/{}", order_id))
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_get_order_not_found_returns_404() {
        let mock = MockOrderService::new();
        let app = test_app(mock);

        let response = app
            .oneshot(
                Request::builder()
                    .uri(format!("/api/v1/orders/{}", Uuid::new_v4()))
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::NOT_FOUND);
    }
}
// <AI-Generated END>
```

---

## AppState Initialization (main.rs)

```rust
// <AI-Generated START>
#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::init();

    // Database pool
    let db = sqlx::PgPool::connect(&std::env::var("DATABASE_URL").expect("DATABASE_URL required"))
        .await
        .expect("Failed to connect to database");

    // Run migrations
    sqlx::migrate!("./migrations")
        .run(&db)
        .await
        .expect("Failed to run migrations");

    // Wire services
    let order_service: Arc<dyn OrderService> = OrderRepository::new(db.clone());
    let user_service: Arc<dyn UserService> = UserRepository::new(db.clone());

    // Build app state
    let state = AppState {
        order_service,
        user_service,
    };

    // Build router
    let app = axum::Router::new()
        .nest("/api/v1/orders", orders_router())
        .nest("/api/v1/users", users_router())
        .with_state(state);

    // Start server
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080")
        .await
        .expect("Failed to bind");
    axum::serve(listener, app)
        .await
        .expect("Server error");
}
// <AI-Generated END>
```
