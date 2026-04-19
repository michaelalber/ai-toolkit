---
name: axum-scaffolder
description: >
  Scaffolds Axum HTTP endpoints with OpenAPI documentation (utoipa), Tower middleware,
  JWT authentication, rate limiting, CORS, health checks, and versioning. Axum-first
  approach: typed extractors, typed responses, and compile-time route verification.
  Use when creating Rust REST APIs, scaffolding Axum endpoints, setting up Axum projects,
  configuring Tower middleware, adding OpenAPI documentation to Axum, or implementing
  JWT authentication in Axum.
  Triggers on: "scaffold axum", "create axum endpoint", "axum router", "add axum route",
  "rust rest api", "axum api", "axum openapi", "axum jwt", "axum middleware".
  Do NOT use when the existing codebase uses Actix-web — scaffolding Axum into
  an Actix project requires manual integration not covered here.
---

# Axum Scaffolder

> "An API that is not documented is an API that is not finished."
> -- API Design Principle

> "Security by default: every route is protected unless explicitly marked public."
> -- Axum Security Principle

## Core Philosophy

Axum is Rust's most ergonomic HTTP framework, built on Tower's middleware ecosystem and Tokio's async runtime. This skill scaffolds production-ready Axum APIs with OpenAPI documentation, security middleware, and proper error handling from day one.

The key design decisions enforced by this skill:
- **OpenAPI-First**: Every handler has `#[utoipa::path]` documentation. The OpenAPI spec is generated from code, not written separately.
- **Versioning from Day One**: All routes are prefixed with `/api/v1/`. Adding v2 later is a router merge, not a refactor.
- **Security by Default**: Auth middleware is applied at the router level. Anonymous access is explicit, not the default.
- **Typed Everything**: Request data via typed extractors (`Json<T>`, `Path<T>`, `Query<T>`). Response data via `impl IntoResponse`. No raw `Request` parsing.
- **Explicit Error Handling**: Custom `AppError` implementing `IntoResponse`. RFC 7807 Problem Details JSON format.

**Non-Negotiable Constraints:**

1. **OpenAPI-First** — `#[utoipa::path]` on every handler; `utoipa::OpenApi` derive on the app. The OpenAPI spec must be accurate.
2. **Versioning from Day One** — `/api/v1/` prefix on all routers. No unversioned routes.
3. **Security by Default** — Tower middleware for JWT validation; anonymous access is explicit (`/health`, `/docs`).
4. **Typed Extractors** — all request data via `axum::extract::{Json, Path, Query, State}`. No raw `Request` parsing in handlers.
5. **Typed Responses** — `impl IntoResponse` with explicit status codes. No magic number status codes in handlers.

## Domain Principles Table

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Router Organization** | One `Router` per feature, merged at startup. Feature routers are defined in feature modules and merged in `main.rs` or `app.rs`. This keeps the main router clean and feature routers self-contained. | Define `pub fn orders_router() -> Router<AppState>` in each feature; merge with `.nest("/api/v1/orders", orders_router())` in app startup. |
| 2 | **Request/Response Types** | Request types derive `Deserialize` and `ToSchema`. Response types derive `Serialize` and `ToSchema`. The `ToSchema` derive is required for OpenAPI documentation. | `#[derive(Deserialize, ToSchema)]` on request types; `#[derive(Serialize, ToSchema)]` on response types. |
| 3 | **Validation** | Input validation happens in the handler before calling the service. The `validator` crate provides derive-based validation. Validation failures return `422 Unprocessable Entity`. | Use `#[derive(Validate)]` on request types; call `req.validate()?` in handlers; map `ValidationError` to `AppError::Validation`. |
| 4 | **OpenAPI Documentation** | Every handler has `#[utoipa::path]` with request body, response types, and status codes. The `utoipa::OpenApi` derive on the app struct aggregates all paths. | Use `#[utoipa::path]` on every handler; include all response types in `components(schemas(...))`. |
| 5 | **Versioning Strategy** | URL prefix versioning (`/api/v1/`, `/api/v2/`). Version is in the URL, not in headers. New versions are new routers merged alongside old ones. Old versions are deprecated with a `Deprecation` header. | All feature routers are nested under `/api/v1/`. When v2 is needed, create new feature routers and nest under `/api/v2/`. |
| 6 | **Authorization** | Tower middleware layer validates JWT and extracts claims. Claims are injected as `Extension<Claims>`. Handlers that need authorization extract `Extension<Claims>`. | Apply auth middleware at the router level; use `Extension<Claims>` in handlers that need the authenticated user. |
| 7 | **Rate Limiting** | `tower-governor` provides per-IP rate limiting. Applied as a Tower layer. Rate limits are configurable per route group. | Apply `GovernorLayer` to the router; configure limits per route group (stricter for auth endpoints). |
| 8 | **Error Handling** | Custom `AppError` enum implementing `IntoResponse`. RFC 7807 Problem Details JSON format. Errors include a `type`, `title`, `status`, and `detail`. | Define `AppError` with `IntoResponse`; return `Result<impl IntoResponse, AppError>` from all handlers. |
| 9 | **CORS** | `tower-http::cors::CorsLayer` with explicit allowed origins. No wildcard origins in production. Credentials mode requires explicit origin allowlist. | Configure `CorsLayer` with `allow_origin(AllowOrigin::list([...]))` for production. |
| 10 | **Health Checks** | `/health` route returns `200 OK` with JSON body. Used by load balancers and Kubernetes liveness/readiness probes. No authentication required. | Add `/health` route to the app router (not nested under `/api/v1/`); return `{"status": "ok", "version": "..."}`. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Axum router handler extractor State Tower middleware")` | During scaffold — verify Axum patterns |
| `search_knowledge("utoipa OpenAPI derive macro Axum documentation")` | During OpenAPI setup — verify utoipa patterns |
| `search_knowledge("Axum JWT authentication Tower layer middleware")` | During auth setup — verify JWT middleware patterns |
| `search_knowledge("Axum error handling IntoResponse AppError")` | During error type design — verify error patterns |
| `search_knowledge("tower-http CORS rate limiting middleware")` | During middleware setup — verify Tower middleware |

## Workflow

```
DETECT (before scaffolding)
    [ ] Check for existing Cargo.toml (identify existing dependencies)
    [ ] Check for existing AppState, AppError, main router
    [ ] Identify Rust edition and Tokio version
    [ ] Check for existing utoipa setup

        |
        v

CONFIGURE (Cargo.toml dependencies and project structure)
    [ ] Add required dependencies to Cargo.toml
    [ ] Create src/errors.rs (AppError)
    [ ] Create src/state.rs (AppState)
    [ ] Create src/openapi.rs (OpenApi derive)

        |
        v

SCAFFOLD (router + handlers + models)
    [ ] Create feature router with typed handlers
    [ ] Create request/response models with ToSchema
    [ ] Add utoipa::path documentation to handlers
    [ ] Create error type with From<FeatureError> for AppError

        |
        v

SECURE (auth middleware)
    [ ] Add JWT validation middleware
    [ ] Apply to protected route groups
    [ ] Leave /health and /docs unprotected

        |
        v

DOCUMENT (utoipa OpenAPI)
    [ ] Add #[utoipa::path] to all handlers
    [ ] Add ToSchema to all request/response types
    [ ] Configure OpenApi derive with all paths and schemas
    [ ] Add /docs route serving the OpenAPI UI

        |
        v

VERIFY
    [ ] cargo build (no errors)
    [ ] cargo test (all tests pass)
    [ ] cargo clippy -- -D warnings (no warnings)
    [ ] curl /health returns 200
    [ ] curl /docs returns OpenAPI UI
```

**Exit criteria:** All routes scaffolded, documented, secured, and verified.

## State Block

```
<axum-scaffold-state>
phase: DETECT | CONFIGURE | SCAFFOLD | SECURE | DOCUMENT | VERIFY | COMPLETE
feature_name: [name]
edition: [2015 | 2018 | 2021]
tokio_version: [1.x | unknown]
utoipa_configured: true | false
auth_middleware: true | false
rate_limiting: true | false
cors_configured: true | false
health_check: true | false
openapi_ui: true | false
build_status: pass | fail | not-run
last_action: [description]
next_action: [description]
</axum-scaffold-state>
```

## Output Templates

### Scaffold Checklist

```markdown
## Axum Scaffold: [project/feature name]

### Dependencies Added (Cargo.toml)
- [ ] axum [version]
- [ ] tokio [version]
- [ ] tower [version]
- [ ] tower-http [version]
- [ ] utoipa [version]
- [ ] utoipa-swagger-ui [version]
- [ ] serde [version]
- [ ] thiserror [version]

### Files Created
- [ ] src/errors.rs (AppError)
- [ ] src/state.rs (AppState)
- [ ] src/openapi.rs (OpenApi derive)
- [ ] src/features/[name]/router.rs
- [ ] src/features/[name]/models.rs
- [ ] src/features/[name]/errors.rs

### Verification
- [ ] cargo build passes
- [ ] GET /health returns 200
- [ ] GET /docs returns OpenAPI UI
- [ ] Protected routes return 401 without token
```

### Cargo.toml Dependencies Template

```toml
[dependencies]
axum = { version = "0.7", features = ["macros"] }
tokio = { version = "1", features = ["full"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace", "compression-gzip"] }
tower-governor = "0.3"
utoipa = { version = "4", features = ["axum_extras"] }
utoipa-swagger-ui = { version = "6", features = ["axum"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
jsonwebtoken = "9"
validator = { version = "0.18", features = ["derive"] }
```

## AI Discipline Rules

### CRITICAL: OpenAPI on Every Handler

**WRONG:**
```rust
async fn create_order(
    State(state): State<AppState>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<impl IntoResponse, AppError> { ... }
```

**RIGHT:**
```rust
#[utoipa::path(
    post,
    path = "/api/v1/orders",
    request_body = CreateOrderRequest,
    responses(
        (status = 201, description = "Order created", body = OrderResponse),
        (status = 400, description = "Invalid request"),
        (status = 401, description = "Unauthorized"),
        (status = 422, description = "Validation error"),
    ),
    security(("bearer_auth" = [])),
    tag = "orders"
)]
async fn create_order(
    State(state): State<AppState>,
    Extension(claims): Extension<Claims>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<(StatusCode, Json<OrderResponse>), AppError> { ... }
```

### CRITICAL: Auth Middleware at Router Level

**WRONG:**
```rust
// Auth check inside the handler
async fn get_order(
    State(state): State<AppState>,
    headers: HeaderMap,
) -> Result<impl IntoResponse, AppError> {
    let token = headers.get("Authorization").ok_or(AppError::Unauthorized)?;
    // validate token...
}
```

**RIGHT:**
```rust
// Auth middleware applied at router level
pub fn orders_router() -> Router<AppState> {
    Router::new()
        .route("/:id", get(get_order))
        .layer(middleware::from_fn(jwt_auth_middleware))
}
```

### REQUIRED: RFC 7807 Problem Details

```rust
// <AI-Generated START>
impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_type, title, detail) = match &self {
            AppError::NotFound(msg) => (
                StatusCode::NOT_FOUND,
                "https://example.com/errors/not-found",
                "Resource Not Found",
                msg.as_str(),
            ),
            AppError::Unauthorized => (
                StatusCode::UNAUTHORIZED,
                "https://example.com/errors/unauthorized",
                "Unauthorized",
                "Authentication required",
            ),
            AppError::Validation(msg) => (
                StatusCode::UNPROCESSABLE_ENTITY,
                "https://example.com/errors/validation",
                "Validation Error",
                msg.as_str(),
            ),
            AppError::Internal(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "https://example.com/errors/internal",
                "Internal Server Error",
                "An unexpected error occurred",
            ),
        };

        let body = Json(serde_json::json!({
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

## Anti-Patterns Table

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Unversioned Routes** | Adding versioning later requires changing all client URLs. | Start with `/api/v1/` prefix on all routes. |
| 2 | **Auth in Handlers** | Per-handler auth checks are easy to forget. One missed check = security hole. | Apply auth middleware at the router level. |
| 3 | **Wildcard CORS** | `allow_any_origin()` allows any website to make requests to your API. | Use explicit origin allowlist in production. |
| 4 | **No OpenAPI Documentation** | Undocumented APIs are unusable by other teams and impossible to test with tools. | `#[utoipa::path]` on every handler from day one. |
| 5 | **Raw Request Parsing** | `req.headers().get("X-Custom")` in handlers bypasses Axum's type system. | Use typed extractors: `Extension<T>`, `TypedHeader<T>`. |
| 6 | **Panic in Handlers** | `.unwrap()` in a handler panics the request, potentially crashing the server. | Return `Result<impl IntoResponse, AppError>`. Use `?`. |
| 7 | **String Error Responses** | `(StatusCode::BAD_REQUEST, "something went wrong")` is not machine-readable. | Use RFC 7807 Problem Details JSON format. |
| 8 | **No Rate Limiting on Auth** | Unlimited login attempts enable brute-force attacks. | Apply stricter rate limits to `/auth/login` and `/auth/register`. |
| 9 | **Blocking in Handlers** | `std::thread::sleep()` in a handler blocks the Tokio executor thread. | Use `tokio::time::sleep()` and `tokio::task::spawn_blocking()`. |
| 10 | **Missing Health Check** | Load balancers and Kubernetes need a health endpoint to determine service availability. | Add `/health` returning `200 OK` with `{"status": "ok"}`. |

## Error Recovery

### utoipa Compilation Errors

```
Symptoms: cargo build fails with utoipa derive errors

Recovery:
1. Check utoipa version compatibility with axum version
2. Verify all types used in #[utoipa::path] implement ToSchema
3. Check that response types are included in OpenApi components(schemas(...))
4. Common fix: add #[derive(ToSchema)] to all request/response types
5. Check utoipa documentation for the specific error message
```

### JWT Middleware Rejects All Requests

```
Symptoms: All requests return 401 after adding auth middleware

Recovery:
1. Verify the JWT secret matches between token generation and validation
2. Check token expiration (exp claim)
3. Check the Authorization header format: "Bearer <token>"
4. Add logging to the middleware to see what is being rejected
5. Test with a freshly generated token
```

### Tower Layer Order Issues

```
Symptoms: Middleware not applied, or applied in wrong order

Recovery:
1. Tower layers are applied in reverse order (last added = outermost)
2. Auth middleware should be inner (applied after CORS, before handlers)
3. Correct order: .layer(cors).layer(trace).layer(auth)
4. Verify with a request trace log
```

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `rust-feature-slice` | Provides the feature module organization. `axum-scaffolder` provides the HTTP infrastructure (middleware, OpenAPI, auth). Use both together. |
| `rust-security-review` | After scaffolding, run `rust-security-review` to verify auth middleware, CORS, and input validation are correct. |
| `rust-architecture-checklist` | After scaffolding, run `rust-architecture-checklist` to verify handler thinness, error handling, and trait design. |
| `sqlx-migration-manager` | When the scaffolded API requires database access, use `sqlx-migration-manager` for the migration lifecycle. |
| `minimal-api-scaffolder` | Parallel skill for .NET Minimal API. Same OpenAPI-first philosophy; different ecosystem. |
