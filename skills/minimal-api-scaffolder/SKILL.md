---
name: minimal-api-scaffolder
description: Generates Minimal API endpoints with OpenAPI documentation, security patterns, and versioning. Use when creating REST APIs, adding endpoints, or setting up API projects. Triggers on phrases like "api endpoint", "minimal api", "create api", "openapi", "rest endpoint", "add route", "api versioning".
---

# Minimal API Scaffolder

> "Minimal APIs are ideal for microservices and apps that want to include only the minimum files, features, and dependencies in ASP.NET Core." — Microsoft

This skill generates Minimal API endpoints with OpenAPI documentation, security, and versioning for .NET 10.

## Quick Start

1. **Define endpoint group**: Resource name (e.g., `Users`, `Orders`)
2. **Generate endpoints**: CRUD operations with handlers
3. **Add OpenAPI docs**: Summaries, responses, examples
4. **Apply security**: Authorization attributes
5. **Version if needed**: URL or header versioning

## Project Setup

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <!-- OpenAPI / Swagger -->
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />

    <!-- Versioning -->
    <PackageReference Include="Asp.Versioning.Http" Version="8.1.0" />

    <!-- Validation -->
    <PackageReference Include="FluentValidation" Version="11.9.0" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.9.0" />

    <!-- CQRS -->
    <PackageReference Include="FreeMediator" Version="1.0.0" />
  </ItemGroup>

</Project>
```

## Program.cs Setup

```csharp
using Asp.Versioning;
using MyApp.Features;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new() { Title = "My API", Version = "v1" });
    options.SwaggerDoc("v2", new() { Title = "My API", Version = "v2" });
});

// API Versioning
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-Api-Version"));
});

// FreeMediator
builder.Services.AddFreeMediator(typeof(Program).Assembly);

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// DbContext
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")));

// Authentication
builder.Services.AddAuthentication().AddJwtBearer();
builder.Services.AddAuthorization();

var app = builder.Build();

// Configure pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "My API V1");
        c.SwaggerEndpoint("/swagger/v2/swagger.json", "My API V2");
    });
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

// Map endpoints
var api = app.NewVersionedApi();

api.MapUsersEndpoints();
api.MapOrdersEndpoints();
// Add more endpoint groups...

app.Run();
```

## Endpoint Group Template

### Basic Endpoint Group
```csharp
// Features/Users/UsersEndpoints.cs
using Microsoft.AspNetCore.Http.HttpResults;
using MyApp.Features.Users.Commands;
using MyApp.Features.Users.Queries;
using MyApp.Features.Users.DTOs;

namespace MyApp.Features.Users;

public static class UsersEndpoints
{
    public static IEndpointRouteBuilder MapUsersEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v{version:apiVersion}/users")
            .WithTags("Users")
            .WithOpenApi()
            .RequireAuthorization();

        group.MapGet("/", GetUsers)
            .WithName("GetUsers")
            .WithSummary("Get all users")
            .WithDescription("Returns a paginated list of users")
            .Produces<PagedResult<UserListDto>>(200)
            .Produces(401);

        group.MapGet("/{id:int}", GetUserById)
            .WithName("GetUserById")
            .WithSummary("Get user by ID")
            .Produces<UserDto>(200)
            .Produces(404)
            .Produces(401);

        group.MapPost("/", CreateUser)
            .WithName("CreateUser")
            .WithSummary("Create a new user")
            .Accepts<CreateUserRequest>("application/json")
            .Produces<UserDto>(201)
            .Produces<ValidationProblemDetails>(400)
            .Produces(401);

        group.MapPut("/{id:int}", UpdateUser)
            .WithName("UpdateUser")
            .WithSummary("Update an existing user")
            .Accepts<UpdateUserRequest>("application/json")
            .Produces(204)
            .Produces<ValidationProblemDetails>(400)
            .Produces(404)
            .Produces(401);

        group.MapDelete("/{id:int}", DeleteUser)
            .WithName("DeleteUser")
            .WithSummary("Delete a user")
            .Produces(204)
            .Produces(404)
            .Produces(401);

        return app;
    }

    // Handler methods
    private static async Task<Ok<PagedResult<UserListDto>>> GetUsers(
        [AsParameters] GetUsersRequest request,
        IMediator mediator,
        CancellationToken ct)
    {
        var result = await mediator.Send(new GetUserListQuery(
            request.Page,
            request.PageSize,
            request.Search,
            request.DepartmentId), ct);

        return TypedResults.Ok(result);
    }

    private static async Task<Results<Ok<UserDto>, NotFound>> GetUserById(
        int id,
        IMediator mediator,
        CancellationToken ct)
    {
        var user = await mediator.Send(new GetUserByIdQuery(id), ct);

        return user is not null
            ? TypedResults.Ok(user)
            : TypedResults.NotFound();
    }

    private static async Task<Results<Created<UserDto>, ValidationProblem>> CreateUser(
        CreateUserRequest request,
        IValidator<CreateUserRequest> validator,
        IMediator mediator,
        CancellationToken ct)
    {
        var validation = await validator.ValidateAsync(request, ct);
        if (!validation.IsValid)
        {
            return TypedResults.ValidationProblem(validation.ToDictionary());
        }

        var result = await mediator.Send(new CreateUserCommand(
            request.FirstName,
            request.LastName,
            request.Email,
            request.DepartmentId), ct);

        if (!result.IsSuccess)
        {
            return TypedResults.ValidationProblem(new Dictionary<string, string[]>
            {
                { "Error", new[] { result.Error! } }
            });
        }

        var user = await mediator.Send(new GetUserByIdQuery(result.Value), ct);
        return TypedResults.Created($"/api/v1/users/{result.Value}", user);
    }

    private static async Task<Results<NoContent, NotFound, ValidationProblem>> UpdateUser(
        int id,
        UpdateUserRequest request,
        IValidator<UpdateUserRequest> validator,
        IMediator mediator,
        CancellationToken ct)
    {
        var validation = await validator.ValidateAsync(request, ct);
        if (!validation.IsValid)
        {
            return TypedResults.ValidationProblem(validation.ToDictionary());
        }

        var result = await mediator.Send(new UpdateUserCommand(
            id,
            request.FirstName,
            request.LastName,
            request.Email,
            request.DepartmentId), ct);

        return result.IsSuccess
            ? TypedResults.NoContent()
            : TypedResults.NotFound();
    }

    private static async Task<Results<NoContent, NotFound>> DeleteUser(
        int id,
        IMediator mediator,
        CancellationToken ct)
    {
        var result = await mediator.Send(new DeleteUserCommand(id), ct);

        return result.IsSuccess
            ? TypedResults.NoContent()
            : TypedResults.NotFound();
    }
}
```

### Request Models
```csharp
// Features/Users/Requests/GetUsersRequest.cs
namespace MyApp.Features.Users.Requests;

public record GetUsersRequest(
    int Page = 1,
    int PageSize = 20,
    string? Search = null,
    int? DepartmentId = null);

// Features/Users/Requests/CreateUserRequest.cs
public record CreateUserRequest(
    string FirstName,
    string LastName,
    string Email,
    int DepartmentId);

// Features/Users/Requests/UpdateUserRequest.cs
public record UpdateUserRequest(
    string FirstName,
    string LastName,
    string Email,
    int DepartmentId);
```

### Validators
```csharp
// Features/Users/Validators/CreateUserRequestValidator.cs
using FluentValidation;

namespace MyApp.Features.Users.Validators;

public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.FirstName)
            .NotEmpty().WithMessage("First name is required")
            .MaximumLength(100);

        RuleFor(x => x.LastName)
            .NotEmpty().WithMessage("Last name is required")
            .MaximumLength(100);

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format")
            .MaximumLength(255);

        RuleFor(x => x.DepartmentId)
            .GreaterThan(0).WithMessage("Department is required");
    }
}
```

## OpenAPI Documentation

### Rich Documentation Example
```csharp
group.MapPost("/", CreateUser)
    .WithName("CreateUser")
    .WithSummary("Create a new user")
    .WithDescription("""
        Creates a new user in the system.

        ## Request Body
        - **firstName**: User's first name (required, max 100 chars)
        - **lastName**: User's last name (required, max 100 chars)
        - **email**: User's email address (required, must be unique)
        - **departmentId**: ID of the department (required)

        ## Response
        Returns the created user with its assigned ID.
        """)
    .WithOpenApi(operation =>
    {
        operation.RequestBody.Description = "User creation data";
        operation.Responses["201"].Description = "User created successfully";
        operation.Responses["400"].Description = "Validation failed";
        return operation;
    })
    .Accepts<CreateUserRequest>("application/json")
    .Produces<UserDto>(201)
    .ProducesValidationProblem();
```

### Response Types
```csharp
// Standard response types
.Produces<UserDto>(200)                    // Success with data
.Produces(201)                             // Created
.Produces(204)                             // No content
.Produces(400)                             // Bad request
.Produces(401)                             // Unauthorized
.Produces(403)                             // Forbidden
.Produces(404)                             // Not found
.Produces(500)                             // Server error

// Problem details
.ProducesValidationProblem()               // 400 with validation errors
.ProducesProblem(500)                      // Problem details response
```

## API Versioning

### URL Versioning (Default)
```csharp
// /api/v1/users
// /api/v2/users

var v1 = app.NewVersionedApi()
    .MapGroup("/api/v{version:apiVersion}")
    .HasApiVersion(1.0);

var v2 = app.NewVersionedApi()
    .MapGroup("/api/v{version:apiVersion}")
    .HasApiVersion(2.0);

v1.MapGet("/users", GetUsersV1);
v2.MapGet("/users", GetUsersV2);
```

### Header Versioning
```csharp
// X-Api-Version: 1.0
// X-Api-Version: 2.0

builder.Services.AddApiVersioning(options =>
{
    options.ApiVersionReader = new HeaderApiVersionReader("X-Api-Version");
});
```

### Deprecating Versions
```csharp
group.MapGet("/legacy", GetLegacyUsers)
    .WithApiVersionSet(versionSet)
    .HasDeprecatedApiVersion(1.0)
    .HasApiVersion(2.0);
```

## Security Patterns

### Authorization
```csharp
// Require authentication for all endpoints
group.RequireAuthorization();

// Specific policy
group.MapDelete("/{id}", DeleteUser)
    .RequireAuthorization("AdminOnly");

// Multiple policies
group.MapPost("/admin", CreateAdmin)
    .RequireAuthorization("AdminOnly", "CanCreateUsers");
```

### Claims-Based Authorization
```csharp
// In Program.cs
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireClaim("role", "admin"));

    options.AddPolicy("CanManageUsers", policy =>
        policy.RequireClaim("permission", "users:manage"));
});
```

### Rate Limiting
```csharp
// In Program.cs
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("Api", limiterOptions =>
    {
        limiterOptions.PermitLimit = 100;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
    });
});

// Apply to endpoint
group.MapGet("/", GetUsers)
    .RequireRateLimiting("Api");
```

## Error Handling

### Global Error Handler
```csharp
// Middleware
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        context.Response.ContentType = "application/problem+json";

        var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;

        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "An error occurred",
            Detail = app.Environment.IsDevelopment() ? exception?.Message : null
        };

        context.Response.StatusCode = problem.Status.Value;
        await context.Response.WriteAsJsonAsync(problem);
    });
});
```

### Endpoint-Level Error Handling
```csharp
private static async Task<Results<Ok<UserDto>, NotFound, Problem>> GetUserById(
    int id,
    IMediator mediator,
    CancellationToken ct)
{
    try
    {
        var user = await mediator.Send(new GetUserByIdQuery(id), ct);
        return user is not null
            ? TypedResults.Ok(user)
            : TypedResults.NotFound();
    }
    catch (Exception ex)
    {
        return TypedResults.Problem(
            detail: ex.Message,
            statusCode: 500,
            title: "An error occurred");
    }
}
```

## Output Format

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

## References

- `references/minimal-api-patterns.md` - Minimal API patterns
- `references/openapi-documentation.md` - OpenAPI documentation
- `references/api-security-patterns.md` - Security best practices
- `references/api-versioning.md` - Versioning strategies
