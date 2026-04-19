# Tower Middleware Patterns for Axum

Patterns for composing Tower middleware in Axum applications.
Covers JWT auth, CORS, rate limiting, tracing, compression, and timeouts.

---

## Layer Ordering

Tower layers are applied in reverse order — the last `.layer()` call wraps the outermost layer.

```
Request flow:
  TraceLayer (outermost — logs every request)
    → CorsLayer (handles CORS preflight)
      → TimeoutLayer (enforces request timeout)
        → GovernorLayer (rate limiting)
          → AuthLayer (JWT validation)
            → Handler (innermost)

Response flow (reverse):
  Handler → AuthLayer → GovernorLayer → TimeoutLayer → CorsLayer → TraceLayer
```

```rust
// <AI-Generated START>
// Correct layer order (last added = outermost):
Router::new()
    .route("/", get(handler))
    .layer(middleware::from_fn(jwt_auth_middleware))  // innermost (applied last to request)
    .layer(GovernorLayer::new(governor_config))
    .layer(TimeoutLayer::new(Duration::from_secs(30)))
    .layer(CorsLayer::new()...)
    .layer(TraceLayer::new_for_http());               // outermost (applied first to request)
// <AI-Generated END>
```

---

## JWT Authentication Middleware

```rust
// <AI-Generated START>
use axum::{
    extract::Request,
    http::{header, StatusCode},
    middleware::Next,
    response::Response,
};
use jsonwebtoken::{decode, DecodingKey, Validation};

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

    let secret = std::env::var("JWT_SECRET")
        .expect("JWT_SECRET environment variable must be set");

    let claims = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_bytes()),
        &Validation::default(),
    )
    .map_err(|e| {
        tracing::warn!("JWT validation failed: {}", e);
        StatusCode::UNAUTHORIZED
    })?
    .claims;

    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}

// Usage in handler:
async fn protected_handler(
    Extension(claims): Extension<Claims>,
    // ...
) -> Result<impl IntoResponse, AppError> {
    tracing::info!("Request from user: {}", claims.sub);
    // ...
}
// <AI-Generated END>
```

---

## CORS Configuration

```rust
// <AI-Generated START>
use tower_http::cors::{AllowOrigin, CorsLayer};
use axum::http::{header, Method};

// Production: explicit origin allowlist
fn production_cors() -> CorsLayer {
    CorsLayer::new()
        .allow_origin(AllowOrigin::list([
            "https://app.example.com".parse().unwrap(),
            "https://admin.example.com".parse().unwrap(),
        ]))
        .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE, Method::OPTIONS])
        .allow_headers([header::CONTENT_TYPE, header::AUTHORIZATION, header::ACCEPT])
        .allow_credentials(true)
        .max_age(Duration::from_secs(3600))
}

// Development: permissive (DO NOT use in production)
fn development_cors() -> CorsLayer {
    CorsLayer::permissive()
}

// Conditional based on environment:
fn cors_layer() -> CorsLayer {
    if std::env::var("ENVIRONMENT").as_deref() == Ok("production") {
        production_cors()
    } else {
        development_cors()
    }
}
// <AI-Generated END>
```

---

## Rate Limiting with tower-governor

```rust
// <AI-Generated START>
use tower_governor::{
    governor::GovernorConfigBuilder,
    key_extractor::SmartIpKeyExtractor,
    GovernorLayer,
};
use std::sync::Arc;

// Standard API rate limit: 100 requests per second per IP
fn api_rate_limit() -> GovernorLayer<SmartIpKeyExtractor> {
    let config = Arc::new(
        GovernorConfigBuilder::default()
            .per_second(100)
            .burst_size(200)
            .use_headers()  // Include rate limit headers in response
            .finish()
            .unwrap(),
    );
    GovernorLayer { config }
}

// Strict rate limit for auth endpoints: 5 requests per minute per IP
fn auth_rate_limit() -> GovernorLayer<SmartIpKeyExtractor> {
    let config = Arc::new(
        GovernorConfigBuilder::default()
            .per_minute(5)
            .burst_size(10)
            .use_headers()
            .finish()
            .unwrap(),
    );
    GovernorLayer { config }
}

// Apply different limits to different route groups:
let auth_routes = Router::new()
    .route("/login", post(login))
    .route("/register", post(register))
    .layer(auth_rate_limit());

let api_routes = Router::new()
    .nest("/orders", orders_router())
    .layer(api_rate_limit());
// <AI-Generated END>
```

---

## Request Tracing with tower-http

```rust
// <AI-Generated START>
use tower_http::trace::{DefaultMakeSpan, DefaultOnResponse, TraceLayer};
use tracing::Level;

fn trace_layer() -> TraceLayer<tower_http::classify::SharedClassifier<tower_http::classify::ServerErrorsAsFailures>> {
    TraceLayer::new_for_http()
        .make_span_with(
            DefaultMakeSpan::new()
                .level(Level::INFO)
                .include_headers(false),  // Don't log headers (may contain tokens)
        )
        .on_response(
            DefaultOnResponse::new()
                .level(Level::INFO)
                .latency_unit(tower_http::LatencyUnit::Millis),
        )
}
// <AI-Generated END>
```

---

## Request Timeout

```rust
// <AI-Generated START>
use tower_http::timeout::TimeoutLayer;
use std::time::Duration;

// Apply a 30-second timeout to all requests
let timeout = TimeoutLayer::new(Duration::from_secs(30));

// For specific route groups with different timeouts:
let slow_routes = Router::new()
    .route("/export", get(export_handler))
    .layer(TimeoutLayer::new(Duration::from_secs(300)));  // 5 minutes for exports

let fast_routes = Router::new()
    .route("/health", get(health_check))
    .layer(TimeoutLayer::new(Duration::from_secs(5)));  // 5 seconds for health
// <AI-Generated END>
```

---

## Response Compression

```rust
// <AI-Generated START>
use tower_http::compression::CompressionLayer;

// Compress responses with gzip/brotli/deflate based on Accept-Encoding
let compression = CompressionLayer::new()
    .gzip(true)
    .br(true)
    .deflate(true);
// <AI-Generated END>
```

---

## Security Headers Middleware

```rust
// <AI-Generated START>
use axum::{extract::Request, middleware::Next, response::Response};
use axum::http::header;

/// Add security headers to all responses.
pub async fn security_headers_middleware(
    req: Request,
    next: Next,
) -> Response {
    let mut response = next.run(req).await;
    let headers = response.headers_mut();

    headers.insert(
        header::X_CONTENT_TYPE_OPTIONS,
        "nosniff".parse().unwrap(),
    );
    headers.insert(
        header::X_FRAME_OPTIONS,
        "DENY".parse().unwrap(),
    );
    headers.insert(
        "X-XSS-Protection".parse::<header::HeaderName>().unwrap(),
        "1; mode=block".parse().unwrap(),
    );
    headers.insert(
        header::STRICT_TRANSPORT_SECURITY,
        "max-age=31536000; includeSubDomains".parse().unwrap(),
    );

    response
}
// <AI-Generated END>
```

---

## Complete Middleware Stack

```rust
// <AI-Generated START>
pub fn create_app(state: AppState) -> Router {
    // Protected API routes
    let api_v1 = Router::new()
        .nest("/orders", orders_router())
        .layer(middleware::from_fn(jwt_auth_middleware))
        .layer(api_rate_limit());

    // Auth routes (stricter rate limiting, no JWT required)
    let auth_routes = Router::new()
        .route("/login", post(login))
        .route("/register", post(register))
        .layer(auth_rate_limit());

    // Public routes
    let public = Router::new()
        .route("/health", get(health_check))
        .merge(swagger_ui());

    Router::new()
        .nest("/api/v1", api_v1)
        .nest("/auth", auth_routes)
        .merge(public)
        // Middleware applied to all routes (outermost first):
        .layer(middleware::from_fn(security_headers_middleware))
        .layer(CompressionLayer::new().gzip(true))
        .layer(TimeoutLayer::new(Duration::from_secs(30)))
        .layer(cors_layer())
        .layer(trace_layer())
        .with_state(state)
}
// <AI-Generated END>
```
