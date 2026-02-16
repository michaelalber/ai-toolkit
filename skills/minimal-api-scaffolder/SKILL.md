---
name: minimal-api-scaffolder
description: Scaffolds .NET 10 Minimal API endpoints with OpenAPI documentation, versioning strategies, and security patterns. Use when creating REST APIs, adding endpoints, setting up API projects, or configuring API infrastructure. Triggers on phrases like "scaffold API", "minimal API", "create endpoint", "API versioning", "api endpoint", "rest endpoint", "add route", "openapi", "create api".
---

# .NET 10 Minimal API Scaffolder

> "Minimal APIs are ideal for microservices and apps that want to include only the minimum files, features, and dependencies in ASP.NET Core."
> -- Microsoft Documentation

> "A good API is not just easy to use but also hard to misuse."
> -- Joshua Bloch

## Core Philosophy

This skill scaffolds and maintains Minimal API endpoints in .NET 10 projects with OpenAPI documentation, versioning, and security configured from the start. Every API begins with a clear contract, validated inputs, and documented responses. Minimal APIs are first-class citizens in .NET -- not a simplified alternative to controllers, but the preferred approach for building focused, performant HTTP endpoints.

**Non-Negotiable Constraints:**

1. **OpenAPI-First Design** -- Every endpoint must have OpenAPI metadata: name, summary, request/response types, and status codes. An undocumented endpoint is an incomplete endpoint. No endpoint ships without `.WithName()`, `.WithSummary()`, and `.Produces<T>()`.
2. **Versioning from Day One** -- API versioning is configured at project creation, not retrofitted. Every endpoint group includes a version segment. There is no "we'll add versioning later."
3. **Security by Default** -- Authentication and authorization are configured in the pipeline before any endpoint is mapped. Groups default to `.RequireAuthorization()`. Anonymous access is an explicit opt-in, never an implicit default.
4. **Convention over Configuration** -- Endpoint groups follow a consistent pattern: group creation with tags, OpenAPI metadata, typed results, and FluentValidation integration. Every new endpoint group mirrors the established convention.
5. **Typed Results, Not Raw Responses** -- All handlers return `TypedResults` with explicit union return types (`Results<Ok<T>, NotFound, ValidationProblem>`). No raw `IResult`, no untyped `Results.Ok()`, no status code magic numbers in handler bodies.

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Endpoint Grouping** | Related endpoints are organized into static extension method classes (e.g., `UsersEndpoints`, `OrdersEndpoints`). Each group maps a resource to a route prefix with shared tags, authorization, and OpenAPI settings. | Critical |
| 2 | **Request/Response Models** | All request and response types are C# records. Request models use `[AsParameters]` for GET queries. POST/PUT bodies are strongly typed. No anonymous objects, no `dynamic`, no `Dictionary<string, object>`. | Critical |
| 3 | **FluentValidation Integration** | Every mutating endpoint (POST, PUT, PATCH) injects and executes an `IValidator<TRequest>` before processing. Validation is explicit in the handler, not hidden in middleware. | Critical |
| 4 | **OpenAPI Documentation** | Every endpoint declares `.WithName()`, `.WithSummary()`, `.Produces<T>()` for all possible status codes, and `.Accepts<T>()` for request bodies. Rich descriptions use `.WithDescription()` and `.WithOpenApi()`. | Critical |
| 5 | **Versioning Strategy** | The project chooses a versioning strategy (URL, header, or query string) at setup time and applies it consistently. URL versioning (`/api/v{version:apiVersion}/`) is the recommended default. | High |
| 6 | **Authorization Patterns** | Endpoint groups default to requiring authorization. Individual endpoints may override with specific policies (`RequireAuthorization("AdminOnly")`) or anonymous access (`AllowAnonymous()`). Policies are defined in `Program.cs`. | Critical |
| 7 | **Rate Limiting** | Public and high-traffic endpoints configure rate limiting policies. Rate limiters are defined as named policies in `Program.cs` and applied per-endpoint or per-group with `.RequireRateLimiting()`. | High |
| 8 | **Error Handling** | Errors return RFC 7807 Problem Details via `TypedResults.Problem()` or `TypedResults.ValidationProblem()`. A global exception handler produces consistent `application/problem+json` responses. | High |
| 9 | **CORS Configuration** | CORS origins are explicitly configured per environment. Development may use permissive settings; production must whitelist specific origins from configuration. Never use `AllowAnyOrigin()` in production. | High |
| 10 | **Health Checks** | Every API project includes health check endpoints (`/health`, `/health/ready`, `/health/live`) mapped with `.AllowAnonymous()`. Database connectivity and critical dependencies are included in readiness checks. | Medium |

## Workflow

### Minimal API Scaffold Lifecycle

```
+----------------------------------------------------------------------+
|                  Minimal API Scaffold Lifecycle                       |
|                                                                      |
|  +-----------+   +----------+   +--------+   +----------+            |
|  | CONFIGURE |-->| SCAFFOLD |-->| SECURE |-->| DOCUMENT |            |
|  | Project   |   | Endpoints|   | Auth & |   | OpenAPI  |            |
|  | Setup     |   | & Models |   | Limits |   | & Verify |            |
|  +-----------+   +----------+   +--------+   +----------+            |
|       |               |              |             |                  |
|       v               v              v             v                  |
|  Program.cs      Endpoint       Auth policies  Swagger UI            |
|  Packages        groups         Rate limiting  Version docs          |
|  DbContext       Validators     CORS config    Response schemas      |
|  Versioning      Request DTOs   Health checks  API testing           |
+----------------------------------------------------------------------+
```

### Phase 1: CONFIGURE

Set up the project foundation before any endpoints are created.

- [ ] Create or verify `.csproj` with required packages (see `references/endpoint-patterns.md`)
- [ ] Configure `Program.cs` with service registrations: OpenAPI, versioning, FreeMediator, FluentValidation, DbContext
- [ ] Set up authentication and authorization pipeline
- [ ] Configure API versioning strategy (URL recommended)
- [ ] Register rate limiting policies
- [ ] Configure CORS for target environments

### Phase 2: SCAFFOLD

Create endpoint groups, request/response models, and validators.

- [ ] Create endpoint group static class with extension method pattern
- [ ] Define all CRUD operations with typed results
- [ ] Create request records for each mutating operation
- [ ] Create response DTOs for each query operation
- [ ] Implement FluentValidation validators for all request models
- [ ] Wire endpoint group into `Program.cs` via `api.Map{Resource}Endpoints()`

### Phase 3: SECURE

Apply authorization, rate limiting, and CORS to all endpoints.

- [ ] Apply `.RequireAuthorization()` to endpoint groups
- [ ] Define and apply specific policies for sensitive operations
- [ ] Apply rate limiting to public-facing or high-traffic endpoints
- [ ] Verify CORS is configured for all consuming origins
- [ ] Add health check endpoints with anonymous access
- [ ] Verify authentication middleware is in the pipeline

### Phase 4: DOCUMENT

Ensure every endpoint is fully documented via OpenAPI metadata.

- [ ] Verify every endpoint has `.WithName()` and `.WithSummary()`
- [ ] Verify every endpoint declares all `.Produces<T>()` responses
- [ ] Add `.WithDescription()` for complex endpoints
- [ ] Test Swagger UI renders correctly for all versions
- [ ] Verify versioned Swagger docs are accessible
- [ ] Confirm request/response schemas appear in OpenAPI spec

## State Block Format

Maintain state across conversation turns using this block:

```
<api-scaffold-state>
mode: [CONFIGURE | SCAFFOLD | SECURE | DOCUMENT]
project_name: [name of the project]
dotnet_version: [net10.0]
endpoints_created: [list of endpoint groups created]
versioning_strategy: [url | header | query | combined]
auth_configured: [true | false]
openapi_configured: [true | false]
last_action: [what was just done]
next_action: [what should happen next]
</api-scaffold-state>
```

### Example State Progression

```
<api-scaffold-state>
mode: CONFIGURE
project_name: MyApp.Api
dotnet_version: net10.0
endpoints_created: []
versioning_strategy: url
auth_configured: false
openapi_configured: false
last_action: Created project with required NuGet packages
next_action: Configure Program.cs with versioning and OpenAPI
</api-scaffold-state>
```

```
<api-scaffold-state>
mode: SCAFFOLD
project_name: MyApp.Api
dotnet_version: net10.0
endpoints_created: [UsersEndpoints]
versioning_strategy: url
auth_configured: true
openapi_configured: true
last_action: Scaffolded UsersEndpoints with full CRUD
next_action: Create OrdersEndpoints group
</api-scaffold-state>
```

```
<api-scaffold-state>
mode: DOCUMENT
project_name: MyApp.Api
dotnet_version: net10.0
endpoints_created: [UsersEndpoints, OrdersEndpoints]
versioning_strategy: url
auth_configured: true
openapi_configured: true
last_action: Applied authorization policies and rate limiting
next_action: Verify OpenAPI docs render correctly in Swagger UI
</api-scaffold-state>
```

## Output Templates

### Project Setup Checklist

```markdown
## API Project Setup: [Project Name]

**Framework**: .NET 10
**Versioning**: [URL | Header | Query String]
**Authentication**: [JWT Bearer | Azure AD | Custom]

### Packages Installed
| Package | Version | Purpose |
|---------|---------|---------|
| Swashbuckle.AspNetCore | 6.5.0 | OpenAPI / Swagger |
| Asp.Versioning.Http | 8.1.0 | API versioning |
| FluentValidation | 11.9.0 | Request validation |
| FreeMediator | 1.0.0 | CQRS / Mediator |

### Program.cs Configuration
- [x] OpenAPI with versioned swagger docs
- [x] API versioning with [strategy]
- [x] FreeMediator registered
- [x] FluentValidation registered
- [x] Authentication pipeline configured
- [x] CORS configured for [environments]

<api-scaffold-state>
mode: CONFIGURE
project_name: [name]
...
</api-scaffold-state>
```

### Endpoint Group Report

```markdown
## Minimal API Endpoint Group: [Resource Name]

**Base Path**: `/api/v{version}/[resource]`
**Tags**: [Resource]
**Authentication**: Required

### Endpoints

| Method | Path | Name | Description |
|--------|------|------|-------------|
| GET | / | Get[Resource]s | List all with pagination |
| GET | /{id} | Get[Resource]ById | Get single by ID |
| POST | / | Create[Resource] | Create new |
| PUT | /{id} | Update[Resource] | Update existing |
| DELETE | /{id} | Delete[Resource] | Delete by ID |

### Request/Response Models

#### CreateRequest
```json
{
  "field1": "string",
  "field2": 0
}
```

#### Response
```json
{
  "id": 1,
  "field1": "string",
  "field2": 0,
  "createdDate": "2024-01-01T00:00:00Z"
}
```

### Authorization

| Endpoint | Policy |
|----------|--------|
| GET / | Default |
| POST / | CanCreate |
| DELETE /{id} | AdminOnly |

### Error Responses

| Status | Description |
|--------|-------------|
| 400 | Validation failed |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Resource not found |
| 500 | Server error |
```

### Validation Report

```markdown
## Validation Summary: [Resource]

| Validator | Field | Rule | Message |
|-----------|-------|------|---------|
| Create[Resource]Validator | FirstName | NotEmpty | First name is required |
| Create[Resource]Validator | FirstName | MaxLength(100) | - |
| Create[Resource]Validator | Email | EmailAddress | Invalid email format |
| Update[Resource]Validator | ... | ... | ... |
```

### API Documentation Summary

```markdown
## API Documentation: [Project Name]

**Swagger UI**: https://localhost:5001/swagger
**OpenAPI Spec**: https://localhost:5001/swagger/v1/swagger.json

### Versions Available
| Version | Status | Swagger Doc |
|---------|--------|-------------|
| v1 | Active | /swagger/v1/swagger.json |
| v2 | Active | /swagger/v2/swagger.json |

### Endpoint Groups
| Group | Endpoints | Auth | Rate Limited |
|-------|-----------|------|-------------|
| Users | 5 | Yes | Yes |
| Orders | 5 | Yes | Yes |

### Health Checks
| Endpoint | Purpose | Auth |
|----------|---------|------|
| /health | Overall | Anonymous |
| /health/ready | Readiness | Anonymous |
| /health/live | Liveness | Anonymous |
```

## AI Discipline Rules

### CRITICAL: Always Add FluentValidation to Mutating Endpoints

Before completing any POST, PUT, or PATCH endpoint, verify:

1. A `FluentValidation` validator class exists for the request type
2. The handler injects `IValidator<TRequest>` as a parameter
3. `ValidateAsync()` is called before any business logic
4. Validation failures return `TypedResults.ValidationProblem(validation.ToDictionary())`

Never rely on model binding validation alone. FluentValidation provides richer rules and consistent error formatting.

```csharp
// WRONG: No validation
private static async Task<Created<UserDto>> CreateUser(
    CreateUserRequest request,
    IMediator mediator,
    CancellationToken ct)
{
    var result = await mediator.Send(new CreateUserCommand(...), ct);
    return TypedResults.Created($"/api/v1/users/{result.Value}", result);
}

// RIGHT: Explicit FluentValidation
private static async Task<Results<Created<UserDto>, ValidationProblem>> CreateUser(
    CreateUserRequest request,
    IValidator<CreateUserRequest> validator,
    IMediator mediator,
    CancellationToken ct)
{
    var validation = await validator.ValidateAsync(request, ct);
    if (!validation.IsValid)
        return TypedResults.ValidationProblem(validation.ToDictionary());
    // ... proceed with business logic
}
```

### CRITICAL: Never Create Endpoints Without OpenAPI Metadata

Every endpoint must have at minimum:

1. `.WithName("OperationId")` -- unique operation identifier
2. `.WithSummary("Brief description")` -- short description for Swagger UI
3. `.Produces<T>(statusCode)` for every possible response status code
4. `.Accepts<T>("application/json")` for POST/PUT endpoints

An endpoint without OpenAPI metadata is invisible to API consumers and tooling.

### CRITICAL: Always Configure CORS Explicitly

Never deploy with `AllowAnyOrigin()` outside development. CORS must be:

1. Configured per-environment (development vs. production)
2. Origins loaded from configuration, not hardcoded
3. Applied in the middleware pipeline before authentication
4. Credentials allowed only when specific origins are listed

### CRITICAL: Use Typed Results, Not Raw Strings or Status Codes

All endpoint handlers must use `TypedResults` with union return types:

```csharp
// WRONG: Raw result with magic status code
private static IResult GetUser(int id) =>
    Results.Json(new { Name = "John" }, statusCode: 200);

// RIGHT: Typed results with explicit union type
private static async Task<Results<Ok<UserDto>, NotFound>> GetUser(
    int id, IMediator mediator, CancellationToken ct)
{
    var user = await mediator.Send(new GetUserByIdQuery(id), ct);
    return user is not null
        ? TypedResults.Ok(user)
        : TypedResults.NotFound();
}
```

### CRITICAL: Group Related Endpoints Together

Never scatter endpoints for the same resource across multiple files or registration points. A single static class per resource maps all related endpoints:

1. One `Map{Resource}Endpoints()` extension method per resource
2. Called from a single location in `Program.cs`
3. Shared group configuration (tags, auth, OpenAPI) at the group level
4. Individual endpoint overrides only where necessary

### CRITICAL: Versioning Must Be Structural

Version segments must appear in the route template, not be inferred. Use `app.NewVersionedApi()` with explicit `.HasApiVersion()` on groups. When a breaking change occurs, create a new version-specific endpoint class rather than adding conditional logic inside an existing handler.

## Anti-Patterns Table

| # | Anti-Pattern | Problem | Correct Approach |
|---|-------------|---------|------------------|
| 1 | **Fat Program.cs** | All endpoint registrations, service configs, and middleware in one massive file | Extract endpoint groups to static extension classes; use extension methods for service registration |
| 2 | **Endpoints Without Validation** | Request data flows directly to business logic without validation | Always inject and call `IValidator<T>` in mutating endpoints |
| 3 | **Missing OpenAPI Tags** | Endpoints appear as ungrouped in Swagger UI, making the API undiscoverable | Apply `.WithTags()` at the group level and `.WithName()`/`.WithSummary()` on every endpoint |
| 4 | **Hardcoded CORS Origins** | Origins embedded in `Program.cs` cannot be changed per environment | Load origins from `appsettings.json` or environment variables |
| 5 | **No Versioning Strategy** | API changes break existing clients with no migration path | Configure versioning at project creation; use URL versioning as default |
| 6 | **Mixing Controllers and Minimal APIs** | Two routing systems in one project create confusion about conventions | Choose one approach per project; minimal APIs for new .NET 10 projects |
| 7 | **Returning Raw Strings** | `return Results.Ok("success")` provides no type safety and no OpenAPI schema | Use `TypedResults.Ok(typedObject)` with strongly typed response records |
| 8 | **Catch-All Exception Handlers in Endpoints** | `try/catch` in every handler duplicates error handling logic | Use global exception handler middleware; let exceptions propagate to it |
| 9 | **Anonymous Endpoints by Default** | Forgetting `.RequireAuthorization()` leaves endpoints publicly accessible | Apply auth at the group level; use `.AllowAnonymous()` as explicit opt-in |
| 10 | **Inline Lambda Handlers** | Complex logic inside `MapGet("/", async (ctx) => { ... })` is untestable | Extract handlers to named static methods; inject dependencies as parameters |

## Error Recovery

### Scenario 1: Project Already Has Controllers

**Symptom**: The project uses `[ApiController]` classes and controller-based routing.

**Recovery Steps**:

1. Do NOT attempt to convert existing controllers to minimal APIs in place
2. Create a new `Features/` directory for minimal API endpoints alongside existing `Controllers/`
3. Configure both routing systems in `Program.cs` (`app.MapControllers()` and minimal API groups)
4. Migrate one resource at a time: create the minimal API endpoint group, verify it works, then deprecate the controller
5. Update Swagger documentation to show both old and new endpoints during migration

**Guard**: Ask the developer before mixing paradigms. A gradual migration is acceptable; a hybrid architecture with no migration plan is not.

### Scenario 2: Conflicting Versioning Approaches

**Symptom**: Different parts of the codebase use different versioning strategies (some URL, some header, some query string), or versioning is partially configured.

**Recovery Steps**:

1. Audit all existing endpoints for version annotations
2. Identify the dominant versioning strategy already in use
3. Configure `ApiVersionReader.Combine()` to support existing clients during migration
4. Standardize all new endpoints on the chosen strategy (URL recommended)
5. Set a deprecation timeline for non-standard version readers
6. Document the canonical versioning approach in the project README

**Guard**: Never remove a working version reader without a client migration plan. Use combined readers as a bridge.

### Scenario 3: OpenAPI Generation Failures

**Symptom**: Swagger UI fails to render, shows missing schemas, or throws errors on specific endpoints.

**Recovery Steps**:

1. Check for endpoints missing `.Produces<T>()` annotations -- Swashbuckle cannot infer response types from minimal APIs
2. Verify all response types are public records/classes (internal types are invisible to Swagger)
3. Check for duplicate `.WithName()` values -- operation IDs must be unique across all endpoints
4. Verify versioned Swagger docs are configured: `options.SwaggerDoc("v1", ...)` for each version
5. Check that `app.UseSwagger()` and `app.UseSwaggerUI()` are in the correct pipeline order (after routing, before endpoints)
6. Run the API and inspect `/swagger/v1/swagger.json` directly for schema errors

**Guard**: After any endpoint change, visually verify Swagger UI renders the updated endpoint correctly.

### Scenario 4: Rate Limiting Not Taking Effect

**Symptom**: Endpoints accept unlimited requests despite rate limiting configuration.

**Recovery Steps**:

1. Verify `app.UseRateLimiter()` is in the pipeline (must be after routing, before auth)
2. Check that rate limiter policies are registered with matching names
3. Verify endpoints reference the correct policy name in `.RequireRateLimiting("PolicyName")`
4. Test with a tool like `bombardier` or `hey` to confirm rate limiting works under load
5. Check that the `OnRejected` handler returns proper 429 responses

## Integration with Other Skills

| Skill | Integration Point | When to Use |
|-------|-------------------|-------------|
| **dotnet-vertical-slice** | Feature architecture for handlers behind endpoints | Use to scaffold the CQRS handlers, commands, queries, and validators that endpoint groups delegate to |
| **dotnet-architecture-checklist** | Review scaffolded API projects | Run after scaffolding to verify the API follows architectural best practices |
| **test-scaffold** | Generate API integration tests | Use to create test classes that exercise endpoints via `WebApplicationFactory<Program>` |
| **dotnet-security-review** | Security audit of API configuration | Run to verify JWT configuration, authorization policies, CORS settings, and rate limiting |
| **ef-migration-manager** | Database setup for API data access | Use when endpoints need new entities or schema changes |

## References

- `references/endpoint-patterns.md` -- Full endpoint group templates, request models, validators, OpenAPI documentation, and error handling patterns
- `references/versioning-strategies.md` -- URL, header, and query string versioning with deprecation strategies
- `references/security-patterns.md` -- Authorization, rate limiting, CORS configuration, health checks, and JWT setup
