# Security Patterns Reference

> Extracted from minimal-api-scaffolder SKILL.md for detailed authorization, rate limiting, and CORS configuration patterns.

## Authorization

### Require Authentication for All Endpoints in a Group

```csharp
// Apply to entire endpoint group
group.RequireAuthorization();
```

### Policy-Based Authorization on Individual Endpoints

```csharp
// Specific policy on a single endpoint
group.MapDelete("/{id}", DeleteUser)
    .RequireAuthorization("AdminOnly");

// Multiple policies (all must be satisfied)
group.MapPost("/admin", CreateAdmin)
    .RequireAuthorization("AdminOnly", "CanCreateUsers");
```

### Allow Anonymous Access

```csharp
// Override group-level authorization for specific endpoints
group.MapGet("/public", GetPublicData)
    .AllowAnonymous();
```

## Claims-Based Authorization

### Defining Policies in Program.cs

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireClaim("role", "admin"));

    options.AddPolicy("CanManageUsers", policy =>
        policy.RequireClaim("permission", "users:manage"));

    options.AddPolicy("MinimumAge", policy =>
        policy.RequireAssertion(context =>
        {
            var ageClaim = context.User.FindFirst("age");
            return ageClaim != null && int.Parse(ageClaim.Value) >= 18;
        }));
});
```

### Role-Based Policies

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("RequireAdmin", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("RequireManagerOrAdmin", policy =>
        policy.RequireRole("Manager", "Admin"));
});
```

### Resource-Based Authorization

```csharp
// Register authorization handler
builder.Services.AddSingleton<IAuthorizationHandler, ResourceOwnerHandler>();

// Custom authorization handler
public class ResourceOwnerHandler
    : AuthorizationHandler<ResourceOwnerRequirement, OwnedResource>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        ResourceOwnerRequirement requirement,
        OwnedResource resource)
    {
        var userId = context.User.FindFirst("sub")?.Value;
        if (resource.OwnerId == userId)
        {
            context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}

// Use in endpoint
private static async Task<Results<Ok<UserDto>, NotFound, ForbidHttpResult>> GetUser(
    int id,
    ClaimsPrincipal user,
    IAuthorizationService authService,
    IMediator mediator,
    CancellationToken ct)
{
    var resource = await mediator.Send(new GetUserByIdQuery(id), ct);
    if (resource is null) return TypedResults.NotFound();

    var authResult = await authService.AuthorizeAsync(
        user, resource, new ResourceOwnerRequirement());

    return authResult.Succeeded
        ? TypedResults.Ok(resource)
        : TypedResults.Forbid();
}
```

## Rate Limiting

### Fixed Window Rate Limiting

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

### Sliding Window Rate Limiting

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddSlidingWindowLimiter("SlidingApi", limiterOptions =>
    {
        limiterOptions.PermitLimit = 100;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.SegmentsPerWindow = 4; // 15-second segments
    });
});
```

### Token Bucket Rate Limiting

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddTokenBucketLimiter("TokenBucket", limiterOptions =>
    {
        limiterOptions.TokenLimit = 100;
        limiterOptions.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        limiterOptions.TokensPerPeriod = 10;
    });
});
```

### Per-User Rate Limiting

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddPolicy("PerUser", httpContext =>
    {
        var userId = httpContext.User.FindFirst("sub")?.Value ?? "anonymous";

        return RateLimitPartition.GetFixedWindowLimiter(userId, _ =>
            new FixedWindowRateLimiterOptions
            {
                PermitLimit = 50,
                Window = TimeSpan.FromMinutes(1)
            });
    });
});
```

### Rate Limit Rejection Response

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

    options.OnRejected = async (context, cancellationToken) =>
    {
        context.HttpContext.Response.ContentType = "application/problem+json";
        var problem = new ProblemDetails
        {
            Status = 429,
            Title = "Rate limit exceeded",
            Detail = "Too many requests. Please try again later."
        };
        await context.HttpContext.Response.WriteAsJsonAsync(problem, cancellationToken);
    };
});

// Add to pipeline (before auth)
app.UseRateLimiter();
```

## CORS Configuration

### Basic CORS Setup

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigins", policy =>
    {
        policy.WithOrigins(
                "https://myapp.example.com",
                "https://admin.example.com")
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials();
    });
});

// Apply in pipeline (before auth, after routing)
app.UseCors("AllowSpecificOrigins");
```

### Environment-Specific CORS

```csharp
builder.Services.AddCors(options =>
{
    if (builder.Environment.IsDevelopment())
    {
        options.AddPolicy("Development", policy =>
        {
            policy.AllowAnyOrigin()
                .AllowAnyHeader()
                .AllowAnyMethod();
        });
    }
    else
    {
        var allowedOrigins = builder.Configuration
            .GetSection("Cors:AllowedOrigins")
            .Get<string[]>() ?? Array.Empty<string>();

        options.AddPolicy("Production", policy =>
        {
            policy.WithOrigins(allowedOrigins)
                .AllowAnyHeader()
                .WithMethods("GET", "POST", "PUT", "DELETE")
                .AllowCredentials()
                .SetPreflightMaxAge(TimeSpan.FromMinutes(10));
        });
    }
});
```

### Per-Endpoint CORS Override

```csharp
// Override group CORS for a specific endpoint
group.MapGet("/public-data", GetPublicData)
    .RequireCors("PublicAccess");
```

### CORS Configuration in appsettings.json

```json
{
  "Cors": {
    "AllowedOrigins": [
      "https://myapp.example.com",
      "https://admin.example.com"
    ]
  }
}
```

## Health Checks

### Basic Health Check Setup

```csharp
// In Program.cs
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database")
    .AddCheck("api-ready", () => HealthCheckResult.Healthy());

// Map health endpoint (no auth required)
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
}).AllowAnonymous();

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
}).AllowAnonymous();

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // No checks, just confirms app is running
}).AllowAnonymous();
```

## JWT Bearer Configuration

### Full JWT Setup

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Jwt:Authority"];
        options.Audience = builder.Configuration["Jwt:Audience"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ClockSkew = TimeSpan.FromMinutes(1)
        };
    });
```

### JWT Configuration in appsettings.json

```json
{
  "Jwt": {
    "Authority": "https://login.microsoftonline.com/{tenant-id}/v2.0",
    "Audience": "api://my-api-client-id"
  }
}
```
