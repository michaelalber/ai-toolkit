# Vertical Slice Testing Patterns

## Overview

Testing vertical slices follows the same isolation principle as the architecture itself: each feature's tests are self-contained and independent. Tests are organized to mirror the feature folder structure, making it easy to find, run, and maintain tests for any given feature.

## Test Project Structure

```
tests/MyApp.Tests/
  Features/
    Orders/
      CreateOrder/
        CreateOrderHandlerTests.cs
        CreateOrderValidatorTests.cs
        CreateOrderEndpointTests.cs
      GetOrderById/
        GetOrderByIdHandlerTests.cs
        GetOrderByIdEndpointTests.cs
      GetOrdersList/
        GetOrdersListHandlerTests.cs
      CancelOrder/
        CancelOrderHandlerTests.cs
        CancelOrderValidatorTests.cs
      OrderPlaced/
        SendOrderConfirmationHandlerTests.cs
        UpdateInventoryHandlerTests.cs
  Common/
    Behaviors/
      ValidationBehaviorTests.cs
      LoggingBehaviorTests.cs
      TransactionBehaviorTests.cs
  Infrastructure/
    TestDbContextFactory.cs
    WebAppFactory.cs
    TestFixtures.cs
```

### Naming Conventions

| Test Type | Naming Pattern | Example |
|-----------|---------------|---------|
| Handler unit test | `[Feature]HandlerTests` | `CreateOrderHandlerTests` |
| Validator test | `[Feature]ValidatorTests` | `CreateOrderValidatorTests` |
| Endpoint integration test | `[Feature]EndpointTests` | `CreateOrderEndpointTests` |
| Notification handler test | `[HandlerName]Tests` | `SendOrderConfirmationHandlerTests` |

## Unit Testing Handlers

Handler tests verify business logic in isolation. The handler is instantiated directly with its dependencies -- no FreeMediator pipeline, no HTTP layer.

### Basic Handler Test

```csharp
// tests/MyApp.Tests/Features/Orders/CreateOrder/CreateOrderHandlerTests.cs
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using MyApp.Features.Orders.CreateOrder;
using MyApp.Infrastructure.Persistence;
using Xunit;

namespace MyApp.Tests.Features.Orders.CreateOrder;

public class CreateOrderHandlerTests : IDisposable
{
    private readonly AppDbContext _db;
    private readonly CreateOrderHandler _handler;

    public CreateOrderHandlerTests()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _db = new AppDbContext(options);
        _handler = new CreateOrderHandler(_db);
    }

    [Fact]
    public async Task Handle_WithValidCommand_CreatesOrderAndReturnsResponse()
    {
        // Arrange
        var customer = new Customer { Id = 1, Name = "Alice", Email = "alice@example.com" };
        _db.Customers.Add(customer);
        await _db.SaveChangesAsync();

        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 2, UnitPrice: 25.00m),
                new(ProductId: 20, Quantity: 1, UnitPrice: 50.00m)
            }
        );

        // Act
        var response = await _handler.Handle(command, CancellationToken.None);

        // Assert
        response.OrderId.Should().BeGreaterThan(0);
        response.OrderNumber.Should().StartWith("ORD-");
        response.TotalAmount.Should().Be(100.00m);
        response.CreatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task Handle_WithMultipleItems_CalculatesTotalCorrectly()
    {
        // Arrange
        _db.Customers.Add(new Customer { Id = 1, Name = "Bob", Email = "bob@example.com" });
        await _db.SaveChangesAsync();

        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 1, Quantity: 3, UnitPrice: 10.00m),
                new(ProductId: 2, Quantity: 2, UnitPrice: 15.00m),
                new(ProductId: 3, Quantity: 1, UnitPrice: 100.00m)
            }
        );

        // Act
        var response = await _handler.Handle(command, CancellationToken.None);

        // Assert
        response.TotalAmount.Should().Be(160.00m); // (3*10) + (2*15) + (1*100)
    }

    [Fact]
    public async Task Handle_PersistsOrderToDatabase()
    {
        // Arrange
        _db.Customers.Add(new Customer { Id = 1, Name = "Carol", Email = "carol@example.com" });
        await _db.SaveChangesAsync();

        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 5, Quantity: 1, UnitPrice: 42.00m)
            }
        );

        // Act
        var response = await _handler.Handle(command, CancellationToken.None);

        // Assert
        var savedOrder = await _db.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == response.OrderId);

        savedOrder.Should().NotBeNull();
        savedOrder!.CustomerId.Should().Be(1);
        savedOrder.Items.Should().HaveCount(1);
        savedOrder.Items.First().Quantity.Should().Be(1);
        savedOrder.Status.Should().Be(OrderStatus.Pending);
    }

    public void Dispose()
    {
        _db.Dispose();
    }
}
```

### Testing Handlers With External Dependencies

Use NSubstitute to mock infrastructure services that the handler depends on:

```csharp
// tests/MyApp.Tests/Features/Orders/OrderPlaced/SendOrderConfirmationHandlerTests.cs
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using MyApp.Features.Orders.OrderPlaced;
using MyApp.Infrastructure.Persistence;
using NSubstitute;
using Xunit;

namespace MyApp.Tests.Features.Orders.OrderPlaced;

public class SendOrderConfirmationHandlerTests : IDisposable
{
    private readonly AppDbContext _db;
    private readonly IEmailService _emailService;
    private readonly SendOrderConfirmationHandler _handler;

    public SendOrderConfirmationHandlerTests()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _db = new AppDbContext(options);
        _emailService = Substitute.For<IEmailService>();
        _handler = new SendOrderConfirmationHandler(_emailService, _db);
    }

    [Fact]
    public async Task Handle_SendsEmailToCustomer()
    {
        // Arrange
        _db.Customers.Add(new Customer
        {
            Id: 1, Name = "Alice", Email = "alice@example.com"
        });
        await _db.SaveChangesAsync();

        var notification = new OrderPlacedNotification(
            OrderId: 42,
            OrderNumber: "ORD-20250115-ABC12345",
            CustomerId: 1,
            TotalAmount: 150.00m,
            PlacedAt: DateTime.UtcNow
        );

        // Act
        await _handler.Handle(notification, CancellationToken.None);

        // Assert
        await _emailService.Received(1).SendAsync(
            to: "alice@example.com",
            subject: Arg.Is<string>(s => s.Contains("ORD-20250115-ABC12345")),
            body: Arg.Is<string>(b => b.Contains("$150.00")),
            cancellationToken: Arg.Any<CancellationToken>()
        );
    }

    [Fact]
    public async Task Handle_WhenCustomerNotFound_DoesNotSendEmail()
    {
        // Arrange
        var notification = new OrderPlacedNotification(
            OrderId: 42,
            OrderNumber: "ORD-123",
            CustomerId: 999, // does not exist
            TotalAmount: 50.00m,
            PlacedAt: DateTime.UtcNow
        );

        // Act
        await _handler.Handle(notification, CancellationToken.None);

        // Assert
        await _emailService.DidNotReceive().SendAsync(
            Arg.Any<string>(), Arg.Any<string>(), Arg.Any<string>(),
            Arg.Any<CancellationToken>()
        );
    }

    public void Dispose()
    {
        _db.Dispose();
    }
}
```

### Testing Query Handlers

Query handlers project data into response types. Verify the projection is correct:

```csharp
// tests/MyApp.Tests/Features/Orders/GetOrderById/GetOrderByIdHandlerTests.cs
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using MyApp.Features.Orders.GetOrderById;
using MyApp.Infrastructure.Persistence;
using Xunit;

namespace MyApp.Tests.Features.Orders.GetOrderById;

public class GetOrderByIdHandlerTests : IDisposable
{
    private readonly AppDbContext _db;
    private readonly GetOrderByIdHandler _handler;

    public GetOrderByIdHandlerTests()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _db = new AppDbContext(options);
        _handler = new GetOrderByIdHandler(_db);
    }

    [Fact]
    public async Task Handle_WhenOrderExists_ReturnsOrderWithItems()
    {
        // Arrange
        var customer = new Customer { Id = 1, Name = "Alice", Email = "alice@example.com" };
        var product = new Product { Id = 10, Name = "Widget" };
        var order = new Order
        {
            Id = 1,
            OrderNumber = "ORD-TEST-001",
            CustomerId = 1,
            Customer = customer,
            Status = OrderStatus.Pending,
            CreatedAt = new DateTime(2025, 1, 15, 10, 0, 0, DateTimeKind.Utc),
            Items = new List<OrderItem>
            {
                new() { ProductId = 10, Product = product, Quantity = 3, UnitPrice = 25.00m }
            }
        };

        _db.Customers.Add(customer);
        _db.Products.Add(product);
        _db.Orders.Add(order);
        await _db.SaveChangesAsync();

        // Act
        var response = await _handler.Handle(
            new GetOrderByIdQuery(OrderId: 1), CancellationToken.None);

        // Assert
        response.Should().NotBeNull();
        response!.OrderId.Should().Be(1);
        response.OrderNumber.Should().Be("ORD-TEST-001");
        response.CustomerName.Should().Be("Alice");
        response.TotalAmount.Should().Be(75.00m);
        response.Status.Should().Be("Pending");
        response.Items.Should().HaveCount(1);
        response.Items.First().ProductName.Should().Be("Widget");
        response.Items.First().LineTotal.Should().Be(75.00m);
    }

    [Fact]
    public async Task Handle_WhenOrderDoesNotExist_ReturnsNull()
    {
        // Act
        var response = await _handler.Handle(
            new GetOrderByIdQuery(OrderId: 999), CancellationToken.None);

        // Assert
        response.Should().BeNull();
    }

    public void Dispose()
    {
        _db.Dispose();
    }
}
```

## Testing Validators

Validator tests verify FluentValidation rules in isolation. No handler, no database, no HTTP.

```csharp
// tests/MyApp.Tests/Features/Orders/CreateOrder/CreateOrderValidatorTests.cs
using FluentAssertions;
using FluentValidation.TestHelper;
using MyApp.Features.Orders.CreateOrder;
using Xunit;

namespace MyApp.Tests.Features.Orders.CreateOrder;

public class CreateOrderValidatorTests
{
    private readonly CreateOrderValidator _validator = new();

    [Fact]
    public void Validate_WithValidCommand_HasNoErrors()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 2, UnitPrice: 25.00m)
            }
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldNotHaveAnyValidationErrors();
    }

    [Fact]
    public void Validate_WithZeroCustomerId_HasError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 0,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 1, UnitPrice: 10.00m)
            }
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor(x => x.CustomerId)
            .WithErrorMessage("A valid customer is required.");
    }

    [Fact]
    public void Validate_WithEmptyItems_HasError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>()
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor(x => x.Items)
            .WithErrorMessage("At least one item is required.");
    }

    [Fact]
    public void Validate_WithZeroQuantity_HasError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 0, UnitPrice: 25.00m)
            }
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor("Items[0].Quantity")
            .WithErrorMessage("Quantity must be at least 1.");
    }

    [Fact]
    public void Validate_WithNegativeUnitPrice_HasError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 1, UnitPrice: -5.00m)
            }
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor("Items[0].UnitPrice")
            .WithErrorMessage("Unit price must be positive.");
    }

    [Fact]
    public void Validate_WithLongShippingNotes_HasError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 1, UnitPrice: 10.00m)
            },
            ShippingNotes: new string('A', 501)
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor(x => x.ShippingNotes)
            .WithErrorMessage("Shipping notes cannot exceed 500 characters.");
    }

    [Fact]
    public void Validate_WithNullShippingNotes_HasNoError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 1, UnitPrice: 10.00m)
            },
            ShippingNotes: null
        );

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldNotHaveValidationErrorFor(x => x.ShippingNotes);
    }
}
```

## Integration Testing With WebApplicationFactory

Integration tests verify the full pipeline: HTTP request -> endpoint -> mediator -> pipeline behaviors -> handler -> database -> response.

### Custom WebApplicationFactory

```csharp
// tests/MyApp.Tests/Infrastructure/WebAppFactory.cs
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Tests.Infrastructure;

public class WebAppFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Remove the existing DbContext registration
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));

            if (descriptor is not null)
            {
                services.Remove(descriptor);
            }

            // Add in-memory database for testing
            services.AddDbContext<AppDbContext>(options =>
            {
                options.UseInMemoryDatabase($"TestDb-{Guid.NewGuid()}");
            });

            // Ensure the database is created
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.EnsureCreated();
        });

        builder.UseEnvironment("Testing");
    }

    /// <summary>
    /// Seed data for a specific test. Each test gets its own scope.
    /// </summary>
    public async Task SeedDataAsync(Func<AppDbContext, Task> seedAction)
    {
        using var scope = Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await seedAction(db);
    }
}
```

### Endpoint Integration Tests

```csharp
// tests/MyApp.Tests/Features/Orders/CreateOrder/CreateOrderEndpointTests.cs
using System.Net;
using System.Net.Http.Json;
using FluentAssertions;
using MyApp.Features.Orders.CreateOrder;
using MyApp.Infrastructure.Persistence;
using MyApp.Tests.Infrastructure;
using Xunit;

namespace MyApp.Tests.Features.Orders.CreateOrder;

public class CreateOrderEndpointTests : IClassFixture<WebAppFactory>
{
    private readonly HttpClient _client;
    private readonly WebAppFactory _factory;

    public CreateOrderEndpointTests(WebAppFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task Post_WithValidOrder_Returns201Created()
    {
        // Arrange
        await _factory.SeedDataAsync(async db =>
        {
            db.Customers.Add(new Customer { Id = 1, Name = "Alice", Email = "alice@example.com" });
            await db.SaveChangesAsync();
        });

        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 2, UnitPrice: 25.00m)
            }
        );

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", command);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var body = await response.Content.ReadFromJsonAsync<CreateOrderResponse>();
        body.Should().NotBeNull();
        body!.OrderId.Should().BeGreaterThan(0);
        body.TotalAmount.Should().Be(50.00m);

        response.Headers.Location.Should().NotBeNull();
        response.Headers.Location!.ToString().Should().Contain($"/api/orders/{body.OrderId}");
    }

    [Fact]
    public async Task Post_WithEmptyItems_Returns400ValidationError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 1,
            Items: new List<OrderItemDto>()
        );

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", command);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        var body = await response.Content.ReadAsStringAsync();
        body.Should().Contain("At least one item is required");
    }

    [Fact]
    public async Task Post_WithInvalidCustomerId_Returns400ValidationError()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 0,
            Items: new List<OrderItemDto>
            {
                new(ProductId: 10, Quantity: 1, UnitPrice: 10.00m)
            }
        );

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", command);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);

        var body = await response.Content.ReadAsStringAsync();
        body.Should().Contain("A valid customer is required");
    }
}
```

```csharp
// tests/MyApp.Tests/Features/Orders/GetOrderById/GetOrderByIdEndpointTests.cs
using System.Net;
using System.Net.Http.Json;
using FluentAssertions;
using MyApp.Features.Orders.GetOrderById;
using MyApp.Infrastructure.Persistence;
using MyApp.Tests.Infrastructure;
using Xunit;

namespace MyApp.Tests.Features.Orders.GetOrderById;

public class GetOrderByIdEndpointTests : IClassFixture<WebAppFactory>
{
    private readonly HttpClient _client;
    private readonly WebAppFactory _factory;

    public GetOrderByIdEndpointTests(WebAppFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task Get_WhenOrderExists_Returns200WithOrder()
    {
        // Arrange
        await _factory.SeedDataAsync(async db =>
        {
            var customer = new Customer { Id = 1, Name = "Alice", Email = "alice@example.com" };
            var product = new Product { Id = 10, Name = "Widget" };
            db.Customers.Add(customer);
            db.Products.Add(product);
            db.Orders.Add(new Order
            {
                Id = 1,
                OrderNumber = "ORD-TEST",
                CustomerId = 1,
                Customer = customer,
                Status = OrderStatus.Pending,
                CreatedAt = DateTime.UtcNow,
                Items = new List<OrderItem>
                {
                    new() { ProductId = 10, Product = product, Quantity = 2, UnitPrice = 25.00m }
                }
            });
            await db.SaveChangesAsync();
        });

        // Act
        var response = await _client.GetAsync("/api/orders/1");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var body = await response.Content.ReadFromJsonAsync<GetOrderByIdResponse>();
        body.Should().NotBeNull();
        body!.OrderNumber.Should().Be("ORD-TEST");
        body.CustomerName.Should().Be("Alice");
        body.Items.Should().HaveCount(1);
    }

    [Fact]
    public async Task Get_WhenOrderDoesNotExist_Returns404()
    {
        // Act
        var response = await _client.GetAsync("/api/orders/999");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

## Testing Pipeline Behaviors

Pipeline behaviors are infrastructure. Test them in isolation -- see [Pipeline Behaviors](pipeline-behaviors.md) for complete behavior test examples.

Summary of what to test for each behavior:

### Validation Behavior
```
┌──────────────────────────────────────────────────────────┐
│ Validation Behavior Test Checklist                        │
├──────────────────────────────────────────────────────────┤
│ [ ] No validators registered -> calls next()             │
│ [ ] Validation passes -> calls next()                    │
│ [ ] Validation fails -> throws ValidationException       │
│ [ ] Multiple validators -> all are executed              │
│ [ ] Failure contains correct property names and messages │
│ [ ] next() is NOT called when validation fails           │
└──────────────────────────────────────────────────────────┘
```

### Logging Behavior
```
┌──────────────────────────────────────────────────────────┐
│ Logging Behavior Test Checklist                           │
├──────────────────────────────────────────────────────────┤
│ [ ] Logs request name and payload on entry               │
│ [ ] Logs elapsed time on success                         │
│ [ ] Logs error details on exception                      │
│ [ ] Exception is re-thrown (not swallowed)               │
│ [ ] Slow requests trigger warning log                    │
└──────────────────────────────────────────────────────────┘
```

### Transaction Behavior
```
┌──────────────────────────────────────────────────────────┐
│ Transaction Behavior Test Checklist                       │
├──────────────────────────────────────────────────────────┤
│ [ ] Non-transactional request -> no transaction          │
│ [ ] Transactional request -> wraps in transaction        │
│ [ ] Handler success -> transaction committed             │
│ [ ] Handler exception -> transaction rolled back         │
│ [ ] Already in transaction -> does not nest              │
└──────────────────────────────────────────────────────────┘
```

### Caching Behavior
```
┌──────────────────────────────────────────────────────────┐
│ Caching Behavior Test Checklist                           │
├──────────────────────────────────────────────────────────┤
│ [ ] Non-cacheable request -> calls next() directly       │
│ [ ] Cache miss -> calls next(), stores result            │
│ [ ] Cache hit -> returns cached value, skips next()      │
│ [ ] Null response -> not cached                          │
│ [ ] Cache duration is respected                          │
│ [ ] Cache invalidation removes the correct keys          │
└──────────────────────────────────────────────────────────┘
```

## Test Helpers and Utilities

### In-Memory DbContext Factory

```csharp
// tests/MyApp.Tests/Infrastructure/TestDbContextFactory.cs
using Microsoft.EntityFrameworkCore;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Tests.Infrastructure;

public static class TestDbContextFactory
{
    public static AppDbContext Create()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        var db = new AppDbContext(options);
        db.Database.EnsureCreated();
        return db;
    }

    public static AppDbContext CreateWithSeed(Action<AppDbContext> seed)
    {
        var db = Create();
        seed(db);
        db.SaveChanges();
        return db;
    }
}
```

### Usage in Tests

```csharp
public class GetOrderByIdHandlerTests
{
    [Fact]
    public async Task Handle_ReturnsCorrectOrder()
    {
        // Arrange
        using var db = TestDbContextFactory.CreateWithSeed(db =>
        {
            db.Customers.Add(new Customer { Id = 1, Name = "Alice", Email = "alice@example.com" });
            db.Orders.Add(new Order
            {
                Id = 1,
                OrderNumber = "ORD-001",
                CustomerId = 1,
                Status = OrderStatus.Pending,
                CreatedAt = DateTime.UtcNow
            });
        });

        var handler = new GetOrderByIdHandler(db);

        // Act
        var result = await handler.Handle(
            new GetOrderByIdQuery(1), CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result!.OrderNumber.Should().Be("ORD-001");
    }
}
```

### Custom FluentAssertions Extensions

```csharp
// tests/MyApp.Tests/Infrastructure/AssertionExtensions.cs
using FluentAssertions;
using FluentAssertions.Primitives;

namespace MyApp.Tests.Infrastructure;

public static class AssertionExtensions
{
    /// <summary>
    /// Asserts that a response indicates a newly created resource.
    /// </summary>
    public static void BeAValidCreationResponse<T>(
        this ObjectAssertions assertions,
        Action<T>? additionalChecks = null) where T : class
    {
        var subject = assertions.Subject as T;
        subject.Should().NotBeNull("response should be of type {0}", typeof(T).Name);

        additionalChecks?.Invoke(subject!);
    }
}
```

## Test Execution Patterns

### Running Tests by Feature

```bash
# Run all tests for a specific feature
dotnet test --filter "FullyQualifiedName~Features.Orders.CreateOrder"

# Run only handler tests for a feature
dotnet test --filter "FullyQualifiedName~CreateOrderHandlerTests"

# Run only validator tests for a feature
dotnet test --filter "FullyQualifiedName~CreateOrderValidatorTests"

# Run only endpoint (integration) tests for a feature
dotnet test --filter "FullyQualifiedName~CreateOrderEndpointTests"

# Run all tests for a domain area
dotnet test --filter "FullyQualifiedName~Features.Orders"
```

### Test Categories With Traits

Use xUnit traits to categorize tests:

```csharp
[Fact]
[Trait("Category", "Unit")]
[Trait("Feature", "CreateOrder")]
public async Task Handle_WithValidCommand_CreatesOrder()
{
    // ...
}

[Fact]
[Trait("Category", "Integration")]
[Trait("Feature", "CreateOrder")]
public async Task Post_WithValidOrder_Returns201()
{
    // ...
}
```

```bash
# Run only unit tests
dotnet test --filter "Category=Unit"

# Run only integration tests
dotnet test --filter "Category=Integration"

# Run all tests for a feature across all categories
dotnet test --filter "Feature=CreateOrder"
```

## Test Design Rules

### Do

- Mirror the feature folder structure in the test project
- Test handlers directly for unit tests (no mediator pipeline)
- Use `WebApplicationFactory` for integration tests that verify the full pipeline
- Test validators using FluentValidation's `TestValidate` extension
- Test each validator rule independently with a dedicated test
- Use `IDisposable` on test classes to clean up `DbContext`
- Use unique in-memory database names per test class (`Guid.NewGuid()`)

### Do Not

- Share test data between test classes (violates test isolation)
- Test handler logic through the HTTP endpoint in unit tests (too much ceremony)
- Mock the mediator in handler tests (the handler IS the unit under test)
- Create shared test base classes for handlers (same anti-pattern as production code)
- Test internal implementation details (test behavior: what goes in, what comes out)
- Use a real database for unit tests (use in-memory or SQLite in-memory)
- Skip testing validators ("the validation is simple" -- it always grows)
