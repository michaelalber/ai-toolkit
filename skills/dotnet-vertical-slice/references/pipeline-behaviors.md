# FreeMediator Pipeline Behaviors

## Overview

Pipeline behaviors in FreeMediator intercept every request before (and after) it reaches the handler. They implement the decorator pattern: each behavior wraps the next behavior or the handler itself, forming a pipeline. Cross-cutting concerns like validation, logging, transactions, and caching are implemented as behaviors rather than being duplicated in every handler.

```
Request ──> LoggingBehavior ──> ValidationBehavior ──> TransactionBehavior ──> Handler
                                                                                  │
Response <── LoggingBehavior <── ValidationBehavior <── TransactionBehavior <──────┘
```

## Behavior Registration

Behaviors are registered in the DI container. **Registration order determines execution order** -- the first registered behavior is the outermost wrapper, and the last registered behavior is closest to the handler.

```csharp
// Program.cs
// Order: Logging (outermost) -> Validation -> Transaction (innermost, closest to handler)
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(TransactionBehavior<,>));
```

### Recommended Order

| Position | Behavior | Why |
|----------|----------|-----|
| 1 (outermost) | Logging | Captures the full request lifecycle, including validation failures |
| 2 | Validation | Rejects invalid requests before any business logic or transactions |
| 3 | Transaction | Wraps only the handler execution in a database transaction |
| 4 (innermost) | Caching | Sits closest to the handler to cache results before they travel back through the pipeline |

## Validation Behavior

The validation behavior runs all registered FluentValidation validators for the incoming request type. If any validation rules fail, it throws a `ValidationException` before the handler executes.

```csharp
// Common/Behaviors/ValidationBehavior.cs
using FluentValidation;
using FreeMediator;

namespace MyApp.Common.Behaviors;

public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
    {
        _validators = validators;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        if (!_validators.Any())
        {
            return await next();
        }

        var context = new ValidationContext<TRequest>(request);

        var validationResults = await Task.WhenAll(
            _validators.Select(v => v.ValidateAsync(context, cancellationToken))
        );

        var failures = validationResults
            .SelectMany(r => r.Errors)
            .Where(f => f is not null)
            .ToList();

        if (failures.Count > 0)
        {
            throw new ValidationException(failures);
        }

        return await next();
    }
}
```

### Validation Behavior for Void Commands

Commands that return `Unit` or have no response need a separate behavior signature:

```csharp
// Common/Behaviors/ValidationBehaviorVoid.cs
using FluentValidation;
using FreeMediator;

namespace MyApp.Common.Behaviors;

public class ValidationBehaviorVoid<TRequest> : IPipelineBehavior<TRequest>
    where TRequest : IRequest
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehaviorVoid(IEnumerable<IValidator<TRequest>> validators)
    {
        _validators = validators;
    }

    public async Task Handle(
        TRequest request,
        RequestHandlerDelegate next,
        CancellationToken cancellationToken)
    {
        if (!_validators.Any())
        {
            await next();
            return;
        }

        var context = new ValidationContext<TRequest>(request);

        var validationResults = await Task.WhenAll(
            _validators.Select(v => v.ValidateAsync(context, cancellationToken))
        );

        var failures = validationResults
            .SelectMany(r => r.Errors)
            .Where(f => f is not null)
            .ToList();

        if (failures.Count > 0)
        {
            throw new ValidationException(failures);
        }

        await next();
    }
}
```

### Handling Validation Exceptions in Endpoints

Map FluentValidation exceptions to HTTP problem details:

```csharp
// Infrastructure/ExceptionHandling/ValidationExceptionHandler.cs
using FluentValidation;
using Microsoft.AspNetCore.Diagnostics;

namespace MyApp.Infrastructure.ExceptionHandling;

public class ValidationExceptionHandler : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        if (exception is not ValidationException validationException)
        {
            return false;
        }

        var errors = validationException.Errors
            .GroupBy(e => e.PropertyName)
            .ToDictionary(
                g => g.Key,
                g => g.Select(e => e.ErrorMessage).ToArray()
            );

        httpContext.Response.StatusCode = StatusCodes.Status400BadRequest;

        await httpContext.Response.WriteAsJsonAsync(new
        {
            Type = "https://tools.ietf.org/html/rfc9110#section-15.5.1",
            Title = "Validation Failed",
            Status = 400,
            Errors = errors
        }, cancellationToken);

        return true;
    }
}

// Registration in Program.cs:
builder.Services.AddExceptionHandler<ValidationExceptionHandler>();
app.UseExceptionHandler();
```

## Logging Behavior

The logging behavior records request/response details for diagnostics. It wraps the entire pipeline so it captures timing, validation failures, and handler exceptions.

```csharp
// Common/Behaviors/LoggingBehavior.cs
using System.Diagnostics;
using System.Text.Json;
using FreeMediator;
using Microsoft.Extensions.Logging;

namespace MyApp.Common.Behaviors;

public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public LoggingBehavior(ILogger<LoggingBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        var requestName = typeof(TRequest).Name;
        var requestId = Guid.NewGuid().ToString()[..8];

        _logger.LogInformation(
            "[{RequestId}] Handling {RequestName}: {@Request}",
            requestId, requestName, request);

        var stopwatch = Stopwatch.StartNew();

        try
        {
            var response = await next();
            stopwatch.Stop();

            _logger.LogInformation(
                "[{RequestId}] Handled {RequestName} in {ElapsedMs}ms",
                requestId, requestName, stopwatch.ElapsedMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();

            _logger.LogError(ex,
                "[{RequestId}] {RequestName} failed after {ElapsedMs}ms: {ErrorMessage}",
                requestId, requestName, stopwatch.ElapsedMilliseconds, ex.Message);

            throw;
        }
    }
}
```

### Slow Request Warning

Extend the logging behavior to flag slow requests:

```csharp
// Common/Behaviors/PerformanceLoggingBehavior.cs
using System.Diagnostics;
using FreeMediator;
using Microsoft.Extensions.Logging;

namespace MyApp.Common.Behaviors;

public class PerformanceLoggingBehavior<TRequest, TResponse>
    : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<PerformanceLoggingBehavior<TRequest, TResponse>> _logger;
    private const int SlowRequestThresholdMs = 500;

    public PerformanceLoggingBehavior(
        ILogger<PerformanceLoggingBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        var stopwatch = Stopwatch.StartNew();
        var response = await next();
        stopwatch.Stop();

        if (stopwatch.ElapsedMilliseconds > SlowRequestThresholdMs)
        {
            _logger.LogWarning(
                "SLOW REQUEST: {RequestName} took {ElapsedMs}ms (threshold: {ThresholdMs}ms). Request: {@Request}",
                typeof(TRequest).Name,
                stopwatch.ElapsedMilliseconds,
                SlowRequestThresholdMs,
                request);
        }

        return response;
    }
}
```

## Transaction Behavior

The transaction behavior wraps handler execution in a database transaction. This ensures that all database operations within a single handler either succeed together or fail together.

### Using a Marker Interface

Not all requests need transactions. Queries should never be wrapped in a transaction. Use a marker interface to opt in:

```csharp
// Common/Interfaces/ITransactionalRequest.cs
namespace MyApp.Common.Interfaces;

/// <summary>
/// Marker interface. Requests implementing this interface will be
/// wrapped in a database transaction by the TransactionBehavior.
/// </summary>
public interface ITransactionalRequest { }
```

```csharp
// Features/Orders/CreateOrder/CreateOrderCommand.cs
using FreeMediator;
using MyApp.Common.Interfaces;

namespace MyApp.Features.Orders.CreateOrder;

public record CreateOrderCommand(
    int CustomerId,
    List<OrderItemDto> Items
) : IRequest<CreateOrderResponse>, ITransactionalRequest;
```

### Transaction Behavior Implementation

```csharp
// Common/Behaviors/TransactionBehavior.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using MyApp.Common.Interfaces;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Common.Behaviors;

public class TransactionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly AppDbContext _db;

    public TransactionBehavior(AppDbContext db)
    {
        _db = db;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        // Only wrap in a transaction if the request opts in
        if (request is not ITransactionalRequest)
        {
            return await next();
        }

        // If already in a transaction, do not nest
        if (_db.Database.CurrentTransaction is not null)
        {
            return await next();
        }

        await using var transaction = await _db.Database
            .BeginTransactionAsync(cancellationToken);

        try
        {
            var response = await next();
            await transaction.CommitAsync(cancellationToken);
            return response;
        }
        catch
        {
            await transaction.RollbackAsync(cancellationToken);
            throw;
        }
    }
}
```

### Transaction Behavior for Multiple DbContexts

When a handler touches multiple databases:

```csharp
// Common/Behaviors/DistributedTransactionBehavior.cs
using System.Transactions;
using FreeMediator;
using MyApp.Common.Interfaces;

namespace MyApp.Common.Behaviors;

public class DistributedTransactionBehavior<TRequest, TResponse>
    : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        if (request is not ITransactionalRequest)
        {
            return await next();
        }

        using var scope = new TransactionScope(
            TransactionScopeOption.Required,
            new TransactionOptions
            {
                IsolationLevel = IsolationLevel.ReadCommitted,
                Timeout = TransactionManager.DefaultTimeout
            },
            TransactionScopeAsyncFlowOption.Enabled);

        var response = await next();
        scope.Complete();
        return response;
    }
}
```

## Caching Behavior

The caching behavior caches query responses. Commands should never be cached. Use a marker interface to identify cacheable queries.

### Marker Interface

```csharp
// Common/Interfaces/ICachedQuery.cs
namespace MyApp.Common.Interfaces;

/// <summary>
/// Marker interface for queries whose responses should be cached.
/// </summary>
public interface ICachedQuery
{
    /// <summary>
    /// Unique cache key for this query instance.
    /// </summary>
    string CacheKey { get; }

    /// <summary>
    /// How long the cached response is valid.
    /// </summary>
    TimeSpan? CacheDuration => TimeSpan.FromMinutes(5);
}
```

```csharp
// Features/Orders/GetOrderById/GetOrderByIdQuery.cs
using FreeMediator;
using MyApp.Common.Interfaces;

namespace MyApp.Features.Orders.GetOrderById;

public record GetOrderByIdQuery(int OrderId) : IRequest<GetOrderByIdResponse?>, ICachedQuery
{
    public string CacheKey => $"order-{OrderId}";
    public TimeSpan? CacheDuration => TimeSpan.FromMinutes(10);
}
```

### Caching Behavior Implementation

```csharp
// Common/Behaviors/CachingBehavior.cs
using FreeMediator;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Logging;
using MyApp.Common.Interfaces;
using System.Text.Json;

namespace MyApp.Common.Behaviors;

public class CachingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<CachingBehavior<TRequest, TResponse>> _logger;

    public CachingBehavior(
        IDistributedCache cache,
        ILogger<CachingBehavior<TRequest, TResponse>> logger)
    {
        _cache = cache;
        _logger = logger;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        // Only cache if the request opts in
        if (request is not ICachedQuery cachedQuery)
        {
            return await next();
        }

        var cacheKey = cachedQuery.CacheKey;

        // Try to get from cache
        var cachedBytes = await _cache.GetAsync(cacheKey, cancellationToken);
        if (cachedBytes is not null)
        {
            _logger.LogDebug("Cache HIT for {CacheKey}", cacheKey);
            var cachedResponse = JsonSerializer.Deserialize<TResponse>(cachedBytes);
            if (cachedResponse is not null)
            {
                return cachedResponse;
            }
        }

        _logger.LogDebug("Cache MISS for {CacheKey}", cacheKey);

        // Execute the handler
        var response = await next();

        // Store in cache
        if (response is not null)
        {
            var serialized = JsonSerializer.SerializeToUtf8Bytes(response);
            var options = new DistributedCacheEntryOptions();

            if (cachedQuery.CacheDuration.HasValue)
            {
                options.AbsoluteExpirationRelativeToNow = cachedQuery.CacheDuration.Value;
            }

            await _cache.SetAsync(cacheKey, serialized, options, cancellationToken);
        }

        return response;
    }
}
```

### Cache Invalidation Pattern

Invalidate cache entries when commands mutate related data:

```csharp
// Common/Interfaces/ICacheInvalidator.cs
namespace MyApp.Common.Interfaces;

/// <summary>
/// Marker interface for commands that should invalidate cache entries.
/// </summary>
public interface ICacheInvalidator
{
    /// <summary>
    /// Cache keys to invalidate after the command executes.
    /// </summary>
    IEnumerable<string> CacheKeysToInvalidate { get; }
}
```

```csharp
// Features/Orders/CancelOrder/CancelOrderCommand.cs
using FreeMediator;
using MyApp.Common.Interfaces;

namespace MyApp.Features.Orders.CancelOrder;

public record CancelOrderCommand(int OrderId, string Reason)
    : IRequest, ITransactionalRequest, ICacheInvalidator
{
    public IEnumerable<string> CacheKeysToInvalidate => new[]
    {
        $"order-{OrderId}"
    };
}
```

```csharp
// Common/Behaviors/CacheInvalidationBehavior.cs
using FreeMediator;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Logging;
using MyApp.Common.Interfaces;

namespace MyApp.Common.Behaviors;

public class CacheInvalidationBehavior<TRequest, TResponse>
    : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<CacheInvalidationBehavior<TRequest, TResponse>> _logger;

    public CacheInvalidationBehavior(
        IDistributedCache cache,
        ILogger<CacheInvalidationBehavior<TRequest, TResponse>> logger)
    {
        _cache = cache;
        _logger = logger;
    }

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken cancellationToken)
    {
        var response = await next();

        if (request is ICacheInvalidator invalidator)
        {
            foreach (var key in invalidator.CacheKeysToInvalidate)
            {
                _logger.LogDebug("Invalidating cache key: {CacheKey}", key);
                await _cache.RemoveAsync(key, cancellationToken);
            }
        }

        return response;
    }
}
```

## Complete Registration

Putting all behaviors together in `Program.cs`:

```csharp
// Program.cs
using FreeMediator;
using FluentValidation;
using MyApp.Common.Behaviors;

var builder = WebApplication.CreateBuilder(args);

// FreeMediator
builder.Services.AddFreeMediator(cfg =>
{
    cfg.RegisterServicesFromAssembly(typeof(Program).Assembly);
});

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Pipeline behaviors (outermost to innermost)
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(TransactionBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(CachingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(CacheInvalidationBehavior<,>));

// Exception handling
builder.Services.AddExceptionHandler<ValidationExceptionHandler>();

// Distributed cache (choose one)
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});
// Or for development:
// builder.Services.AddDistributedMemoryCache();

var app = builder.Build();
app.UseExceptionHandler();
```

## Testing Pipeline Behaviors in Isolation

Each pipeline behavior should be testable independently of the handler and other behaviors.

### Testing the Validation Behavior

```csharp
using FluentAssertions;
using FluentValidation;
using FluentValidation.Results;
using FreeMediator;
using MyApp.Common.Behaviors;
using NSubstitute;
using Xunit;

namespace MyApp.Tests.Common.Behaviors;

public class ValidationBehaviorTests
{
    [Fact]
    public async Task Handle_WhenNoValidators_CallsNext()
    {
        // Arrange
        var validators = Enumerable.Empty<IValidator<TestRequest>>();
        var behavior = new ValidationBehavior<TestRequest, TestResponse>(validators);
        var nextCalled = false;

        Task<TestResponse> Next()
        {
            nextCalled = true;
            return Task.FromResult(new TestResponse("ok"));
        }

        // Act
        await behavior.Handle(new TestRequest("test"), Next, CancellationToken.None);

        // Assert
        nextCalled.Should().BeTrue();
    }

    [Fact]
    public async Task Handle_WhenValidationFails_ThrowsValidationException()
    {
        // Arrange
        var validator = Substitute.For<IValidator<TestRequest>>();
        validator.ValidateAsync(Arg.Any<ValidationContext<TestRequest>>(), Arg.Any<CancellationToken>())
            .Returns(new ValidationResult(new[]
            {
                new ValidationFailure("Name", "Name is required")
            }));

        var behavior = new ValidationBehavior<TestRequest, TestResponse>(new[] { validator });

        // Act
        var act = () => behavior.Handle(
            new TestRequest(""),
            () => Task.FromResult(new TestResponse("ok")),
            CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<ValidationException>()
            .Where(ex => ex.Errors.Any(e => e.PropertyName == "Name"));
    }

    [Fact]
    public async Task Handle_WhenValidationPasses_CallsNext()
    {
        // Arrange
        var validator = Substitute.For<IValidator<TestRequest>>();
        validator.ValidateAsync(Arg.Any<ValidationContext<TestRequest>>(), Arg.Any<CancellationToken>())
            .Returns(new ValidationResult());

        var behavior = new ValidationBehavior<TestRequest, TestResponse>(new[] { validator });
        var nextCalled = false;

        // Act
        await behavior.Handle(
            new TestRequest("valid"),
            () => { nextCalled = true; return Task.FromResult(new TestResponse("ok")); },
            CancellationToken.None);

        // Assert
        nextCalled.Should().BeTrue();
    }

    // Test types
    public record TestRequest(string Name) : IRequest<TestResponse>;
    public record TestResponse(string Result);
}
```

### Testing the Transaction Behavior

```csharp
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using MyApp.Common.Behaviors;
using MyApp.Common.Interfaces;
using MyApp.Infrastructure.Persistence;
using FreeMediator;
using Xunit;

namespace MyApp.Tests.Common.Behaviors;

public class TransactionBehaviorTests
{
    [Fact]
    public async Task Handle_WhenNotTransactional_SkipsTransaction()
    {
        // Arrange
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        var db = new AppDbContext(options);
        var behavior = new TransactionBehavior<NonTransactionalRequest, string>(db);

        // Act
        var result = await behavior.Handle(
            new NonTransactionalRequest(),
            () => Task.FromResult("done"),
            CancellationToken.None);

        // Assert
        result.Should().Be("done");
        db.Database.CurrentTransaction.Should().BeNull();
    }

    [Fact]
    public async Task Handle_WhenTransactional_CommitsOnSuccess()
    {
        // Arrange
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseSqlite("DataSource=:memory:")
            .Options;
        var db = new AppDbContext(options);
        await db.Database.OpenConnectionAsync();
        await db.Database.EnsureCreatedAsync();

        var behavior = new TransactionBehavior<TransactionalRequest, string>(db);

        // Act
        var result = await behavior.Handle(
            new TransactionalRequest(),
            () => Task.FromResult("committed"),
            CancellationToken.None);

        // Assert
        result.Should().Be("committed");
    }

    [Fact]
    public async Task Handle_WhenTransactionalAndException_Rollbacks()
    {
        // Arrange
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseSqlite("DataSource=:memory:")
            .Options;
        var db = new AppDbContext(options);
        await db.Database.OpenConnectionAsync();
        await db.Database.EnsureCreatedAsync();

        var behavior = new TransactionBehavior<TransactionalRequest, string>(db);

        // Act
        var act = () => behavior.Handle(
            new TransactionalRequest(),
            () => throw new InvalidOperationException("handler failed"),
            CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<InvalidOperationException>();
        db.Database.CurrentTransaction.Should().BeNull();
    }

    // Test types
    public record NonTransactionalRequest() : IRequest<string>;
    public record TransactionalRequest() : IRequest<string>, ITransactionalRequest;
}
```

## Behavior Design Rules

### Do

- Keep behaviors generic -- they should work with any request/response type
- Use marker interfaces to opt features into specific behaviors
- Test each behavior in isolation with mock delegates for `next()`
- Always call `next()` (or throw) -- never silently swallow the request
- Always propagate `CancellationToken`

### Do Not

- Put feature-specific logic inside a behavior (use the validator or handler instead)
- Catch and swallow exceptions in behaviors (let them propagate for logging)
- Create behaviors that depend on other behaviors (they should be independent)
- Register behaviors inside feature folders (they belong in `Common/Behaviors/` or `Infrastructure/Behaviors/`)
- Use conditional logic based on specific request types (use marker interfaces instead)
