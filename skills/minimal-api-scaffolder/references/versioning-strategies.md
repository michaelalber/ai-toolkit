# API Versioning Strategies Reference

> Extracted from minimal-api-scaffolder SKILL.md for detailed versioning patterns, configuration, and deprecation strategies.

## Versioning Configuration in Program.cs

```csharp
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-Api-Version"));
});
```

## URL Versioning (Recommended Default)

URL-based versioning places the version directly in the route template. This is the most explicit and discoverable approach.

```csharp
// Routes: /api/v1/users, /api/v2/users

var v1 = app.NewVersionedApi()
    .MapGroup("/api/v{version:apiVersion}")
    .HasApiVersion(1.0);

var v2 = app.NewVersionedApi()
    .MapGroup("/api/v{version:apiVersion}")
    .HasApiVersion(2.0);

v1.MapGet("/users", GetUsersV1);
v2.MapGet("/users", GetUsersV2);
```

### When to Use URL Versioning

- Public-facing APIs where discoverability matters
- APIs consumed by third-party clients
- When you want explicit version awareness in logs and monitoring
- REST APIs that follow resource-oriented design

### URL Versioning with Swagger

```csharp
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new() { Title = "My API", Version = "v1" });
    options.SwaggerDoc("v2", new() { Title = "My API", Version = "v2" });
});

// In pipeline
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "My API V1");
    c.SwaggerEndpoint("/swagger/v2/swagger.json", "My API V2");
});
```

## Header Versioning

Header-based versioning uses a custom HTTP header to specify the API version. Routes stay clean but the version is less discoverable.

```csharp
// Header: X-Api-Version: 1.0
// Header: X-Api-Version: 2.0

builder.Services.AddApiVersioning(options =>
{
    options.ApiVersionReader = new HeaderApiVersionReader("X-Api-Version");
});
```

### When to Use Header Versioning

- Internal APIs where all clients are controlled
- When URL aesthetics matter (no version segment in path)
- Microservice-to-microservice communication
- APIs behind an API gateway that can inject headers

## Query String Versioning

Query string versioning appends the version as a query parameter.

```csharp
// Route: /api/users?api-version=1.0

builder.Services.AddApiVersioning(options =>
{
    options.ApiVersionReader = new QueryStringApiVersionReader("api-version");
});
```

### When to Use Query String Versioning

- Legacy systems where URL structure cannot change
- APIs that need version flexibility without route changes
- Transitional strategy when migrating from unversioned APIs

## Combined Versioning

Support multiple version readers simultaneously for maximum client flexibility.

```csharp
builder.Services.AddApiVersioning(options =>
{
    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-Api-Version"),
        new QueryStringApiVersionReader("api-version"));
});
```

## Deprecating Versions

Mark older API versions as deprecated to signal clients they should migrate.

```csharp
group.MapGet("/legacy", GetLegacyUsers)
    .WithApiVersionSet(versionSet)
    .HasDeprecatedApiVersion(1.0)
    .HasApiVersion(2.0);
```

### Deprecation Best Practices

1. **Announce deprecation early**: Add `api-deprecated` response header before removing the version
2. **Set a sunset date**: Communicate a clear timeline (typically 6-12 months)
3. **Return deprecation headers**: Use `Sunset` and `Deprecation` HTTP headers
4. **Log usage of deprecated versions**: Monitor which clients still call deprecated endpoints
5. **Provide migration guides**: Document changes between versions

### Deprecation Response Headers

```csharp
// Custom middleware to add deprecation headers
app.Use(async (context, next) =>
{
    await next();

    if (context.GetRequestedApiVersion()?.MajorVersion == 1)
    {
        context.Response.Headers["Deprecation"] = "true";
        context.Response.Headers["Sunset"] = "2025-12-31T00:00:00Z";
        context.Response.Headers["Link"] =
            "</api/v2/docs>; rel=\"successor-version\"";
    }
});
```

## Version-Specific Endpoint Groups

Structure endpoint groups to cleanly separate version-specific logic.

```csharp
// Features/Users/UsersEndpointsV1.cs
public static class UsersEndpointsV1
{
    public static IEndpointRouteBuilder MapUsersEndpointsV1(
        this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v{version:apiVersion}/users")
            .HasApiVersion(1.0)
            .WithTags("Users");

        group.MapGet("/", GetUsers);
        group.MapGet("/{id:int}", GetUserById);
        // V1-specific endpoints...

        return app;
    }
}

// Features/Users/UsersEndpointsV2.cs
public static class UsersEndpointsV2
{
    public static IEndpointRouteBuilder MapUsersEndpointsV2(
        this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/v{version:apiVersion}/users")
            .HasApiVersion(2.0)
            .WithTags("Users");

        group.MapGet("/", GetUsersV2);       // Enhanced response shape
        group.MapGet("/{id:guid}", GetUserById); // Changed from int to GUID
        group.MapGet("/search", SearchUsers);    // New V2 endpoint
        // V2-specific endpoints...

        return app;
    }
}
```

## Version Negotiation Decision Tree

```
Client sends request
|
+-- URL contains version segment? (e.g., /api/v2/users)
|   +-- YES --> Use URL version
|   +-- NO  --> Check next reader
|
+-- X-Api-Version header present?
|   +-- YES --> Use header version
|   +-- NO  --> Check next reader
|
+-- api-version query param present?
|   +-- YES --> Use query version
|   +-- NO  --> Check default
|
+-- AssumeDefaultVersionWhenUnspecified = true?
    +-- YES --> Use DefaultApiVersion
    +-- NO  --> Return 400 (API version required)
```
