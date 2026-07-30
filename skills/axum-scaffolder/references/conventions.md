# Axum Scaffolder Conventions

Depth behind the Core Philosophy constraints. Code for every rule lives in `router-template.md`
(Cargo.toml, errors/AppError, auth/JWT, openapi, main, health) and `middleware-patterns.md`
(layer ordering, JWT, CORS, rate limiting, tracing, timeout, compression, security headers).

## Domain Principles

| # | Principle | Description | Applied As |
|---|-----------|-------------|------------|
| 1 | **Router Organization** | One `Router` per feature, merged at startup; keeps the main router clean and feature routers self-contained. | `pub fn orders_router() -> Router<AppState>` per feature; merge with `.nest("/api/v1/orders", orders_router())`. |
| 2 | **Request/Response Types** | Request types derive `Deserialize` + `ToSchema`; response types derive `Serialize` + `ToSchema`. `ToSchema` is required for OpenAPI. | `#[derive(Deserialize, ToSchema)]` / `#[derive(Serialize, ToSchema)]`. |
| 3 | **Validation** | Validate in the handler before calling the service; failures return `422`. | `#[derive(Validate)]`; `req.validate()?`; map to `AppError::Validation`. |
| 4 | **OpenAPI Documentation** | Every handler has `#[utoipa::path]` with body, responses, status codes; `OpenApi` derive aggregates paths. | `#[utoipa::path]` on every handler; all response types in `components(schemas(...))`. |
| 5 | **Versioning Strategy** | URL-prefix versioning (`/api/v1/`); new versions are new routers merged alongside; deprecate old with a `Deprecation` header. | Nest feature routers under `/api/v1/`; add `/api/v2/` later. |
| 6 | **Authorization** | Tower middleware validates JWT and injects `Extension<Claims>`. | Apply auth at router level; extract `Extension<Claims>` where needed. |
| 7 | **Rate Limiting** | `tower-governor` per-IP limits as a Tower layer, configurable per route group. | `GovernorLayer`; stricter limits on auth endpoints. |
| 8 | **Error Handling** | Custom `AppError` implementing `IntoResponse`; RFC 7807 Problem Details. | `Result<impl IntoResponse, AppError>` from all handlers. |
| 9 | **CORS** | `tower-http::cors::CorsLayer` with explicit origins; no wildcard in production. | `allow_origin(AllowOrigin::list([...]))`. |
| 10 | **Health Checks** | `/health` returns `200 OK` JSON, no auth; for LB/k8s probes. | `/health` outside `/api/v1/`; `{"status":"ok","version":"..."}`. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("Axum router handler extractor State Tower middleware")` | During scaffold — verify Axum patterns |
| `search_knowledge("utoipa OpenAPI derive macro Axum documentation")` | During OpenAPI setup |
| `search_knowledge("Axum JWT authentication Tower layer middleware")` | During auth setup |
| `search_knowledge("Axum error handling IntoResponse AppError")` | During error type design |
| `search_knowledge("tower-http CORS rate limiting middleware")` | During middleware setup |

## Discipline Rules

Full code in `router-template.md` / `middleware-patterns.md`.

- **OpenAPI on every handler.** A bare `async fn create_order(...)` is wrong; every handler carries
  `#[utoipa::path(post, path=..., request_body=..., responses(...), security(...), tag=...)]` and
  returns a typed response like `(StatusCode, Json<OrderResponse>)`.
- **Auth middleware at router level, never in handlers.** Don't read `Authorization` headers inside
  a handler; apply `middleware::from_fn(jwt_auth_middleware)` as a `.layer(...)` on the protected
  router so a route cannot accidentally ship unprotected.
- **RFC 7807 Problem Details.** `AppError`'s `IntoResponse` maps each variant to `{type, title,
  status, detail}` JSON — never a bare string body. (Full `impl` in `router-template.md`.)

## Anti-Patterns

| # | Anti-Pattern | Why It Fails | Correct Approach |
|---|-------------|-------------|-----------------|
| 1 | **Unversioned routes** | Adding versioning later changes all client URLs | Start with `/api/v1/` on all routes |
| 2 | **Auth in handlers** | Per-handler checks are easy to forget; one miss = security hole | Auth middleware at router level |
| 3 | **Wildcard CORS** | `allow_any_origin()` lets any site call your API | Explicit origin allowlist in production |
| 4 | **No OpenAPI docs** | Undocumented APIs are unusable by other teams | `#[utoipa::path]` on every handler from day one |
| 5 | **Raw request parsing** | `req.headers().get(...)` bypasses Axum's type system | Typed extractors: `Extension<T>`, `TypedHeader<T>` |
| 6 | **Panic in handlers** | `.unwrap()` panics the request, can crash the server | Return `Result<impl IntoResponse, AppError>`; use `?` |
| 7 | **String error responses** | Not machine-readable | RFC 7807 Problem Details JSON |
| 8 | **No rate limiting on auth** | Unlimited login attempts enable brute force | Stricter limits on `/auth/login`, `/auth/register` |
| 9 | **Blocking in handlers** | `std::thread::sleep()` blocks the Tokio executor | `tokio::time::sleep()`, `tokio::task::spawn_blocking()` |
| 10 | **Missing health check** | LB/k8s need a health endpoint | `/health` → `200 OK` `{"status":"ok"}` |

## Error Recovery

**utoipa compilation errors** (cargo build fails with utoipa derive errors):
1. Check utoipa/axum version compatibility
2. Verify all types in `#[utoipa::path]` implement `ToSchema`
3. Ensure response types are in `OpenApi components(schemas(...))`
4. Common fix: add `#[derive(ToSchema)]` to all request/response types

**JWT middleware rejects all requests** (everything returns 401 after adding auth):
1. Verify the JWT secret matches between generation and validation
2. Check token expiration (`exp` claim)
3. Check the header format: `Authorization: Bearer <token>`
4. Add logging in the middleware; test with a freshly generated token

**Tower layer order issues** (middleware not applied, or wrong order):
1. Layers apply in reverse order (last added = outermost)
2. Auth should be inner (after CORS, before handlers)
3. Correct order: `.layer(cors).layer(trace).layer(auth)`; verify with a request trace log
