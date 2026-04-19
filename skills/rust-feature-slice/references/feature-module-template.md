# Rust Feature Module Template

Complete scaffold template for a vertical slice feature module in Rust using Axum.
Copy and adapt for each new feature.

---

## Directory Structure

```
src/
  features/
    mod.rs                    # Feature registry
    orders/
      mod.rs                  # Re-exports
      router.rs               # Axum Router
      service.rs              # Service trait + implementation
      models.rs               # Request/response types
      errors.rs               # Feature error type
tests/
  features/
    orders/
      integration_test.rs     # Integration tests
```

---

## `src/features/mod.rs`

```rust
// <AI-Generated START>
pub mod orders;
// Add more feature modules here
// <AI-Generated END>
```

---

## `src/features/orders/mod.rs`

```rust
// <AI-Generated START>
pub mod errors;
pub mod models;
pub mod router;
pub mod service;

pub use router::orders_router;
pub use service::OrderService;
// <AI-Generated END>
```

---

## `src/features/orders/models.rs`

```rust
// <AI-Generated START>
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

/// Request body for creating a new order.
#[derive(Debug, Deserialize, ToSchema)]
pub struct CreateOrderRequest {
    pub customer_id: uuid::Uuid,
    pub items: Vec<OrderItemRequest>,
}

/// A single item in an order request.
#[derive(Debug, Deserialize, ToSchema)]
pub struct OrderItemRequest {
    pub product_id: uuid::Uuid,
    pub quantity: u32,
}

/// Response body for a created or retrieved order.
#[derive(Debug, Serialize, ToSchema)]
pub struct OrderResponse {
    pub id: uuid::Uuid,
    pub customer_id: uuid::Uuid,
    pub status: String,
    pub total_cents: i64,
    pub created_at: chrono::DateTime<chrono::Utc>,
}
// <AI-Generated END>
```

---

## `src/features/orders/errors.rs`

```rust
// <AI-Generated START>
use thiserror::Error;

/// Domain errors for the orders feature.
#[derive(Debug, Error)]
pub enum OrderError {
    #[error("Order not found: {id}")]
    NotFound { id: uuid::Uuid },

    #[error("Invalid order: {reason}")]
    Invalid { reason: String },

    #[error("Customer not found: {customer_id}")]
    CustomerNotFound { customer_id: uuid::Uuid },

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}
// <AI-Generated END>
```

---

## `src/features/orders/service.rs`

```rust
// <AI-Generated START>
use std::sync::Arc;
use uuid::Uuid;

use super::errors::OrderError;
use super::models::{CreateOrderRequest, OrderResponse};

// --- Trait Definition ---

/// Read operations for the orders feature.
/// Implement on the same struct as OrderWriter, or separately for CQRS.
#[async_trait::async_trait]  // Remove for Rust 1.75+ (use native async traits)
pub trait OrderReader: Send + Sync {
    async fn get_order(&self, id: Uuid) -> Result<OrderResponse, OrderError>;
    async fn list_orders(&self, customer_id: Uuid) -> Result<Vec<OrderResponse>, OrderError>;
}

/// Write operations for the orders feature.
#[async_trait::async_trait]  // Remove for Rust 1.75+ (use native async traits)
pub trait OrderWriter: Send + Sync {
    async fn create_order(&self, req: CreateOrderRequest) -> Result<OrderResponse, OrderError>;
    async fn cancel_order(&self, id: Uuid) -> Result<(), OrderError>;
}

// Convenience alias for handlers that need both read and write
pub trait OrderService: OrderReader + OrderWriter {}
impl<T: OrderReader + OrderWriter> OrderService for T {}

// --- Implementation ---

pub struct OrderRepository {
    db: sqlx::PgPool,
}

impl OrderRepository {
    pub fn new(db: sqlx::PgPool) -> Arc<Self> {
        Arc::new(Self { db })
    }
}

#[async_trait::async_trait]
impl OrderReader for OrderRepository {
    async fn get_order(&self, id: Uuid) -> Result<OrderResponse, OrderError> {
        let row = sqlx::query_as!(
            OrderRow,
            "SELECT id, customer_id, status, total_cents, created_at FROM orders WHERE id = $1",
            id
        )
        .fetch_optional(&self.db)
        .await?
        .ok_or(OrderError::NotFound { id })?;

        Ok(row.into())
    }

    async fn list_orders(&self, customer_id: Uuid) -> Result<Vec<OrderResponse>, OrderError> {
        let rows = sqlx::query_as!(
            OrderRow,
            "SELECT id, customer_id, status, total_cents, created_at FROM orders WHERE customer_id = $1",
            customer_id
        )
        .fetch_all(&self.db)
        .await?;

        Ok(rows.into_iter().map(Into::into).collect())
    }
}

#[async_trait::async_trait]
impl OrderWriter for OrderRepository {
    async fn create_order(&self, req: CreateOrderRequest) -> Result<OrderResponse, OrderError> {
        if req.items.is_empty() {
            return Err(OrderError::Invalid {
                reason: "Order must have at least one item".to_string(),
            });
        }

        // Implementation omitted — use sqlx::query! with transaction
        todo!("Implement create_order")
    }

    async fn cancel_order(&self, id: Uuid) -> Result<(), OrderError> {
        let rows_affected = sqlx::query!(
            "UPDATE orders SET status = 'cancelled' WHERE id = $1 AND status = 'pending'",
            id
        )
        .execute(&self.db)
        .await?
        .rows_affected();

        if rows_affected == 0 {
            return Err(OrderError::NotFound { id });
        }
        Ok(())
    }
}

// --- Internal DB row type ---
struct OrderRow {
    id: Uuid,
    customer_id: Uuid,
    status: String,
    total_cents: i64,
    created_at: chrono::DateTime<chrono::Utc>,
}

impl From<OrderRow> for OrderResponse {
    fn from(row: OrderRow) -> Self {
        Self {
            id: row.id,
            customer_id: row.customer_id,
            status: row.status,
            total_cents: row.total_cents,
            created_at: row.created_at,
        }
    }
}

// --- Unit Tests ---
#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;

    struct MockOrderService {
        orders: Mutex<Vec<OrderResponse>>,
    }

    #[async_trait::async_trait]
    impl OrderReader for MockOrderService {
        async fn get_order(&self, id: Uuid) -> Result<OrderResponse, OrderError> {
            self.orders
                .lock()
                .unwrap()
                .iter()
                .find(|o| o.id == id)
                .cloned()
                .ok_or(OrderError::NotFound { id })
        }

        async fn list_orders(&self, customer_id: Uuid) -> Result<Vec<OrderResponse>, OrderError> {
            Ok(self
                .orders
                .lock()
                .unwrap()
                .iter()
                .filter(|o| o.customer_id == customer_id)
                .cloned()
                .collect())
        }
    }

    // Add OrderWriter mock implementation and tests here
}
// <AI-Generated END>
```

---

## `src/features/orders/router.rs`

```rust
// <AI-Generated START>
use axum::{
    extract::{Path, State},
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use uuid::Uuid;

use crate::errors::AppError;
use crate::state::AppState;
use super::models::{CreateOrderRequest, OrderResponse};

/// Returns the Axum Router for the orders feature.
/// Mount at /api/v1/orders in the main app.
pub fn orders_router() -> Router<AppState> {
    Router::new()
        .route("/", post(create_order))
        .route("/:id", get(get_order))
        .route("/:id/cancel", post(cancel_order))
}

/// Create a new order.
#[utoipa::path(
    post,
    path = "/api/v1/orders",
    request_body = CreateOrderRequest,
    responses(
        (status = 201, description = "Order created", body = OrderResponse),
        (status = 400, description = "Invalid request"),
        (status = 422, description = "Validation error"),
    ),
    tag = "orders"
)]
async fn create_order(
    State(state): State<AppState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<(StatusCode, Json<OrderResponse>), AppError> {
    let order = state.order_service.create_order(req).await?;
    Ok((StatusCode::CREATED, Json(order)))
}

/// Get an order by ID.
#[utoipa::path(
    get,
    path = "/api/v1/orders/{id}",
    params(("id" = Uuid, Path, description = "Order ID")),
    responses(
        (status = 200, description = "Order found", body = OrderResponse),
        (status = 404, description = "Order not found"),
    ),
    tag = "orders"
)]
async fn get_order(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<OrderResponse>, AppError> {
    let order = state.order_service.get_order(id).await?;
    Ok(Json(order))
}

/// Cancel an order.
async fn cancel_order(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<StatusCode, AppError> {
    state.order_service.cancel_order(id).await?;
    Ok(StatusCode::NO_CONTENT)
}
// <AI-Generated END>
```

---

## `src/state.rs` (AppState)

```rust
// <AI-Generated START>
use std::sync::Arc;
use crate::features::orders::OrderService;

/// Application state — the composition root.
/// All services are Arc<dyn Trait> for testability.
#[derive(Clone)]
pub struct AppState {
    pub order_service: Arc<dyn OrderService>,
    // Add more services here
}

impl AppState {
    pub fn new(order_service: Arc<dyn OrderService>) -> Self {
        Self { order_service }
    }
}
// <AI-Generated END>
```

---

## `src/errors.rs` (AppError)

```rust
// <AI-Generated START>
use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use serde_json::json;
use crate::features::orders::errors::OrderError;

/// Application-level error type. Converts domain errors to HTTP responses.
#[derive(Debug)]
pub enum AppError {
    NotFound(String),
    BadRequest(String),
    Internal(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AppError::NotFound(msg) => (StatusCode::NOT_FOUND, msg),
            AppError::BadRequest(msg) => (StatusCode::BAD_REQUEST, msg),
            AppError::Internal(msg) => (StatusCode::INTERNAL_SERVER_ERROR, msg),
        };
        (status, Json(json!({ "error": message }))).into_response()
    }
}

impl From<OrderError> for AppError {
    fn from(err: OrderError) -> Self {
        match err {
            OrderError::NotFound { id } => AppError::NotFound(format!("Order {} not found", id)),
            OrderError::Invalid { reason } => AppError::BadRequest(reason),
            OrderError::CustomerNotFound { customer_id } => {
                AppError::NotFound(format!("Customer {} not found", customer_id))
            }
            OrderError::Database(e) => {
                tracing::error!("Database error: {}", e);
                AppError::Internal("Internal server error".to_string())
            }
        }
    }
}
// <AI-Generated END>
```

---

## `tests/features/orders/integration_test.rs`

```rust
// <AI-Generated START>
use axum::{body::Body, http::{Request, StatusCode}};
use tower::ServiceExt;
use serde_json::json;

// Import your app builder function
// use your_crate::app::create_app;

#[tokio::test]
async fn test_create_order_returns_201() {
    // let app = create_app(test_state()).await;
    // let response = app
    //     .oneshot(
    //         Request::builder()
    //             .method("POST")
    //             .uri("/api/v1/orders")
    //             .header("content-type", "application/json")
    //             .body(Body::from(serde_json::to_string(&json!({
    //                 "customer_id": "00000000-0000-0000-0000-000000000001",
    //                 "items": [{"product_id": "00000000-0000-0000-0000-000000000002", "quantity": 1}]
    //             })).unwrap()))
    //             .unwrap(),
    //     )
    //     .await
    //     .unwrap();
    // assert_eq!(response.status(), StatusCode::CREATED);
    todo!("Implement integration test with test AppState")
}

#[tokio::test]
async fn test_get_order_not_found_returns_404() {
    todo!("Implement integration test")
}
// <AI-Generated END>
```
