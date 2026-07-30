# Security & Testing Reference

> Authorization, CORS, rate limiting, and integration-test patterns for controller-based
> Web APIs. Inherit existing middleware configuration — these templates are for matching
> what the project already does, not for adding a second, competing configuration.

## Authorization

Match the project's default. The preferred baseline: authorize at the class level and
opt out explicitly.

```csharp
[ApiController]
[Authorize]                                   // default for the whole controller
[Route("api/v{version:apiVersion}/[controller]")]
public sealed class UsersController : ControllerBase
{
    [HttpGet("public-stats")]
    [AllowAnonymous]                          // explicit opt-out, never implicit
    public Task<ActionResult<StatsDto>> Stats(CancellationToken ct) => /* ... */;

    [HttpDelete("{id:int}")]
    [Authorize(Policy = "AdminOnly")]         // reuse an existing policy name
    public Task<IActionResult> Delete(int id, CancellationToken ct) => /* ... */;
}
```

Reuse existing policy names found during DETECT (`grep -rE "AddPolicy"`). Do not invent a
new policy when one with the same intent already exists.

## CORS

CORS is configured once, in `Program.cs`/`Startup.cs`, and inherited by controllers. Do
**not** add a second policy for a new controller. Confirm the existing named policy and,
if a controller needs a specific one, apply `[EnableCors("PolicyName")]` referencing the
already-registered policy.

```csharp
// Program.cs — existing pattern to match (origins from configuration, never AllowAnyOrigin in prod)
builder.Services.AddCors(o => o.AddPolicy("Default", p => p
    .WithOrigins(builder.Configuration.GetSection("Cors:Origins").Get<string[]>()!)
    .AllowAnyHeader()
    .AllowAnyMethod()));
```

## Rate limiting

If the project uses the built-in rate limiter, apply an existing named policy to a
controller or action; do not register a new limiter unless asked.

```csharp
[EnableRateLimiting("api")]            // references a policy registered in Program.cs
[HttpPost("bulk")]
public Task<IActionResult> Bulk(/* ... */) => /* ... */;
```

## Integration tests (WebApplicationFactory)

Generate tests in the project's existing test framework (detect xUnit/NUnit/MSTest first).
xUnit example:

```csharp
public sealed class UsersControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public UsersControllerTests(WebApplicationFactory<Program> factory)
        => _client = factory.CreateClient();

    [Fact]
    public async Task GetById_ReturnsNotFound_ForMissingUser()
    {
        // Arrange — authenticate per the project's test auth scheme if one exists
        // Act
        var response = await _client.GetAsync("/api/v1/users/999999");
        // Assert
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    [Fact]
    public async Task Create_ReturnsValidationProblem_ForInvalidEmail()
    {
        var request = new { firstName = "A", lastName = "B", email = "not-an-email", departmentId = 1 };
        var response = await _client.PostAsJsonAsync("/api/v1/users", request);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        var problem = await response.Content.ReadFromJsonAsync<ValidationProblemDetails>();
        Assert.Contains("Email", problem!.Errors.Keys);
    }
}
```

For controllers behind `[Authorize]`, match how the existing test suite authenticates
(test authentication handler, seeded JWT, or `WithWebHostBuilder` overriding the auth
scheme). Do not disable authorization globally in tests — that hides real auth defects.

## Security checklist for a new controller

- [ ] Class-level `[Authorize]`; every `[AllowAnonymous]` is intentional
- [ ] Mutating actions are not reachable anonymously
- [ ] DTOs in, DTOs out — no entity binding (guards against over-posting)
- [ ] Validation present in the project's style; no unvalidated input reaches the service
- [ ] No secrets/connection strings introduced inline
- [ ] CORS/rate-limit inherited, not duplicated
- [ ] Route ids typed (`{id:int}`) to constrain binding

Hand off to `dotnet-security-review` for a full OWASP pass on the new surface.
