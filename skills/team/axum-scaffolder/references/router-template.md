# Axum Router Template

Complete scaffold template for an Axum application with OpenAPI documentation,
JWT authentication, rate limiting, CORS, and health checks.

---

## `Cargo.toml` Dependencies

```toml
# <AI-Generated START>
[dependencies]
axum = { version = "0.7", features = ["macros"] }
tokio = { version = "1", features = ["full"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace", "compression-gzip", "timeout"] }
tower-governor = "0.3"
utoipa = { version = "4", features = ["axum_extras", "uuid", "chrono"] }
utoipa-swagger-ui = { version = "6", features = ["axum"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }
jsonwebtoken = "9"
validator = { version = "0.18", features = ["derive"] }

[dev-dependencies]
axum-test = "14"
tokio = { version = "1", features = ["full"] }
# <AI-Generated END>
```

---

## `src/errors.rs` — AppError

```rust
// <AI-Generated START>
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use utoipa::ToSchema;

/// Application-level error type. Converts domain errors to RFC 7807 Problem Details responses.
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Unauthorized")]
    Unauthorized,

    #[error("Forbidden")]
    Forbidden,

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Conflict: {0}")]
    Conflict(String),

    #[error("Internal server error")]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_type, title, detail) = match &self {
            AppError::NotFound(msg) => (
                StatusCode::NOT_FOUND,
                "/errors/not-found",
                "Resource Not Found",
                msg.as_str(),
            ),
            AppError::Unauthorized => (
                StatusCode::UNAUTHORIZED,
                "/errors/unauthorized",
                "Unauthorized",
                "Authentication is required to access this resource",
            ),
            AppError::Forbidden => (
                StatusCode::FORBIDDEN,
                "/errors/forbidden",
                "Forbidden",
                "You do not have permission to access this resource",
            ),
            AppError::Validation(msg) => (
                StatusCode::UNPROCESSABLE_ENTITY,
                "/errors/validation",
                "Validation Error",
                msg.as_str(),
            ),
            AppError::Conflict(msg) => (
                StatusCode::CONFLICT,
                "/errors/conflict",
                "Conflict",
                msg.as_str(),
            ),
            AppError::Internal(e) => {
                tracing::error!("Internal error: {:?}", e);
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "/errors/internal",
                    "Internal Server Error",
                    "An unexpected error occurred",
                )
            }
        };

        let body = Json(json!({
            "type": error_type,
            "title": title,
            "status": status.as_u16(),
            "detail": detail,
        }));

        (status, body).into_response()
    }
}
// <AI-Generated END>
```

---

## `src/auth.rs` — JWT Middleware

```rust
// <AI-Generated START>
use axum::{
    extract::Request,
    http::{header, StatusCode},
    middleware::Next,
    response::Response,
    Extension,
};
use jsonwebtoken::{decode, DecodingKey, Validation};
use serde::{Deserialize, Serialize};

/// JWT claims extracted from the Authorization header.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,      // Subject (user ID)
    pub exp: usize,       // Expiration time
    pub iat: usize,       // Issued at
    pub roles: Vec<String>,
}

/// JWT authentication middleware.
/// Extracts and validates the Bearer token from the Authorization header.
/// Injects Claims as an Extension for downstream handlers.
pub async fn jwt_auth_middleware(
    mut req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token = req
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .ok_or(StatusCode::UNAUTHORIZED)?;

    let secret = std::env::var("JWT_SECRET").expect("JWT_SECRET must be set");
    let key = DecodingKey::from_secret(secret.as_bytes());

    let claims = decode::<Claims>(token, &key, &Validation::default())
        .map_err(|e| {
            tracing::warn!("JWT validation failed: {}", e);
            StatusCode::UNAUTHORIZED
        })?
        .claims;

    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}
// <AI-Generated END>
```

---

## `src/openapi.rs` — OpenAPI Configuration

```rust
// <AI-Generated START>
use utoipa::{
    openapi::security::{HttpAuthScheme, HttpBuilder, SecurityScheme},
    Modify, OpenApi,
};

/// OpenAPI specification for the application.
/// Add all paths and schemas here.
#[derive(OpenApi)]
#[openapi(
    paths(
        crate::features::orders::router::create_order,
        crate::features::orders::router::get_order,
        crate::health::health_check,
    ),
    components(
        schemas(
            crate::features::orders::models::CreateOrderRequest,
            crate::features::orders::models::OrderResponse,
        )
    ),
    modifiers(&SecurityAddon),
    tags(
        (name = "orders", description = "Order management"),
        (name = "health", description = "Health checks"),
    ),
    info(
        title = "My API",
        version = "1.0.0",
        description = "API description",
    )
)]
pub struct ApiDoc;

struct SecurityAddon;

impl Modify for SecurityAddon {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        if let Some(components) = openapi.components.as_mut() {
            components.add_security_scheme(
                "bearer_auth",
                SecurityScheme::Http(
                    HttpBuilder::new()
                        .scheme(HttpAuthScheme::Bearer)
                        .bearer_format("JWT")
                        .build(),
                ),
            );
        }
    }
}
// <AI-Generated END>
```

---

## `src/main.rs` — Application Entry Point

```rust
// <AI-Generated START>
use axum::{middleware, routing::get, Router};
use std::sync::Arc;
use tower_http::{
    cors::{AllowOrigin, CorsLayer},
    trace::TraceLayer,
};
use utoipa_swagger_ui::SwaggerUi;

mod auth;
mod errors;
mod features;
mod health;
mod openapi;
mod state;

use openapi::ApiDoc;
use state::AppState;

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("my_app=debug".parse().unwrap()),
        )
        .init();

    // Build app state
    let state = AppState::new(/* inject services */);

    // Build the application
    let app = create_app(state);

    // Start server
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080")
        .await
        .expect("Failed to bind");

    tracing::info!("Listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.expect("Server error");
}

pub fn create_app(state: AppState) -> Router {
    // Protected API routes (require JWT)
    let api_v1 = Router::new()
        .nest("/orders", features::orders::router::orders_router())
        // Add more feature routers here
        .layer(middleware::from_fn(auth::jwt_auth_middleware));

    // Public routes (no auth required)
    let public = Router::new()
        .route("/health", get(health::health_check))
        .merge(SwaggerUi::new("/docs").url("/api-docs/openapi.json", ApiDoc::openapi()));

    Router::new()
        .nest("/api/v1", api_v1)
        .merge(public)
        .layer(
            CorsLayer::new()
                .allow_origin(AllowOrigin::list([
                    "https://app.example.com".parse().unwrap(),
                ]))
                .allow_methods([
                    axum::http::Method::GET,
                    axum::http::Method::POST,
                    axum::http::Method::PUT,
                    axum::http::Method::DELETE,
                ])
                .allow_headers([axum::http::header::CONTENT_TYPE, axum::http::header::AUTHORIZATION]),
        )
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}
// <AI-Generated END>
```

---

## `src/health.rs` — Health Check

```rust
// <AI-Generated START>
use axum::Json;
use serde_json::{json, Value};

/// Health check endpoint.
/// Returns 200 OK with service status.
/// Used by load balancers and Kubernetes probes.
#[utoipa::path(
    get,
    path = "/health",
    responses(
        (status = 200, description = "Service is healthy", body = Value),
    ),
    tag = "health"
)]
pub async fn health_check() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "version": env!("CARGO_PKG_VERSION"),
    }))
}
// <AI-Generated END>
```
