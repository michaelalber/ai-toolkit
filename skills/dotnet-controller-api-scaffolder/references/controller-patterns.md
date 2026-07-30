# Controller Patterns Reference

> Templates for controller-based ASP.NET Core Web API endpoints. Pick the variant that
> matches the detected convention profile (see `convention-detection.md`). These are
> shapes to conform to, not a structure to impose — adapt naming, routing, and the
> response shape to the existing project.

## Variant A — Service layer + DataAnnotations (most common N-tier)

```csharp
// Controllers/UsersController.cs
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MyApp.Api.Dtos.Users;
using MyApp.Api.Services;

namespace MyApp.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
public sealed class UsersController : ControllerBase   // or : ApiControllerBase if one exists
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService) => _userService = userService;

    /// <summary>Returns a paged list of users.</summary>
    [HttpGet]
    [ProducesResponseType<PagedResult<UserDto>>(StatusCodes.Status200OK)]
    public async Task<ActionResult<PagedResult<UserDto>>> GetAll(
        [FromQuery] GetUsersQuery query, CancellationToken ct)
    {
        var result = await _userService.GetPagedAsync(query, ct);
        return Ok(result);
    }

    /// <summary>Returns a single user by id.</summary>
    [HttpGet("{id:int}")]
    [ProducesResponseType<UserDto>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserDto>> GetById(int id, CancellationToken ct)
    {
        var user = await _userService.GetByIdAsync(id, ct);
        return user is null ? NotFound() : Ok(user);
    }

    /// <summary>Creates a new user.</summary>
    [HttpPost]
    [ProducesResponseType<UserDto>(StatusCodes.Status201Created)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<UserDto>> Create(
        CreateUserRequest request, CancellationToken ct)
    {
        // [ApiController] + DataAnnotations => model-state 400 is automatic; no manual check.
        var created = await _userService.CreateAsync(request, ct);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    /// <summary>Updates an existing user.</summary>
    [HttpPut("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Update(
        int id, UpdateUserRequest request, CancellationToken ct)
    {
        var updated = await _userService.UpdateAsync(id, request, ct);
        return updated ? NoContent() : NotFound();
    }

    /// <summary>Deletes a user.</summary>
    [HttpDelete("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        var deleted = await _userService.DeleteAsync(id, ct);
        return deleted ? NoContent() : NotFound();
    }
}
```

### DTOs (records) with DataAnnotations

```csharp
// Dtos/Users/CreateUserRequest.cs
using System.ComponentModel.DataAnnotations;

namespace MyApp.Api.Dtos.Users;

public sealed record CreateUserRequest(
    [property: Required, StringLength(100)] string FirstName,
    [property: Required, StringLength(100)] string LastName,
    [property: Required, EmailAddress, StringLength(255)] string Email,
    [property: Range(1, int.MaxValue)] int DepartmentId);

public sealed record UpdateUserRequest(
    [property: Required, StringLength(100)] string FirstName,
    [property: Required, StringLength(100)] string LastName,
    [property: Required, EmailAddress, StringLength(255)] string Email,
    [property: Range(1, int.MaxValue)] int DepartmentId);

public sealed record GetUsersQuery(int Page = 1, int PageSize = 20, string? Search = null);

public sealed record UserDto(int Id, string FirstName, string LastName, string Email, int DepartmentId);

public sealed record PagedResult<T>(IReadOnlyList<T> Items, int Page, int PageSize, int TotalCount);
```

### Service interface + registration

```csharp
// Services/IUserService.cs
public interface IUserService
{
    Task<PagedResult<UserDto>> GetPagedAsync(GetUsersQuery query, CancellationToken ct);
    Task<UserDto?> GetByIdAsync(int id, CancellationToken ct);
    Task<UserDto> CreateAsync(CreateUserRequest request, CancellationToken ct);
    Task<bool> UpdateAsync(int id, UpdateUserRequest request, CancellationToken ct);
    Task<bool> DeleteAsync(int id, CancellationToken ct);
}

// Program.cs — register at the existing site, matching the existing lifetime
builder.Services.AddScoped<IUserService, UserService>();
```

## Variant B — Mediator boundary + FluentValidation

Use only when the project already uses a mediator (`Send()`) and FluentValidation.

```csharp
[ApiController]
[Authorize]
[Route("api/v{version:apiVersion}/[controller]")]
public sealed class OrdersController : ControllerBase
{
    private readonly ISender _mediator;
    public OrdersController(ISender mediator) => _mediator = mediator;

    [HttpGet("{id:int}")]
    [ProducesResponseType<OrderDto>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<OrderDto>> GetById(int id, CancellationToken ct)
    {
        var order = await _mediator.Send(new GetOrderByIdQuery(id), ct);
        return order is null ? NotFound() : Ok(order);
    }

    [HttpPost]
    [ProducesResponseType<OrderDto>(StatusCodes.Status201Created)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<OrderDto>> Create(
        CreateOrderCommand command,
        IValidator<CreateOrderCommand> validator,
        CancellationToken ct)
    {
        // Use this explicit path only if automatic model-state filtering is suppressed.
        var validation = await validator.ValidateAsync(command, ct);
        if (!validation.IsValid)
        {
            validation.AddToModelState(ModelState);
            return ValidationProblem(ModelState);
        }

        var created = await _mediator.Send(command, ct);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }
}
```

```csharp
// FluentValidation validator
public sealed class CreateOrderCommandValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderCommandValidator()
    {
        RuleFor(x => x.CustomerId).GreaterThan(0);
        RuleFor(x => x.Lines).NotEmpty();
        RuleForEach(x => x.Lines).ChildRules(line =>
            line.RuleFor(l => l.Quantity).GreaterThan(0));
    }
}
```

## Variant C — Custom response envelope

If existing actions return an `ApiResponse<T>` envelope, match it exactly:

```csharp
[HttpGet("{id:int}")]
[ProducesResponseType<ApiResponse<UserDto>>(StatusCodes.Status200OK)]
[ProducesResponseType<ApiResponse<UserDto>>(StatusCodes.Status404NotFound)]
public async Task<ActionResult<ApiResponse<UserDto>>> GetById(int id, CancellationToken ct)
{
    var user = await _userService.GetByIdAsync(id, ct);
    return user is null
        ? NotFound(ApiResponse<UserDto>.Fail("User not found"))
        : Ok(ApiResponse<UserDto>.Ok(user));
}
```

## Error handling — ProblemDetails (global, not per-action)

Prefer a global handler over `try/catch` in each action. With `[ApiController]`, unhandled
exceptions and validation already map to `application/problem+json`.

```csharp
// Program.cs (.NET 8+)
builder.Services.AddProblemDetails();
var app = builder.Build();
app.UseExceptionHandler();   // emits ProblemDetails for unhandled exceptions
```

For domain "not found"/"conflict" semantics, return the matching status from the action
(`NotFound()`, `Conflict()`); reserve the global handler for unexpected failures. If the
project already has a custom exception-handling middleware or `IExceptionHandler`, match it
rather than adding `UseExceptionHandler` a second time.
