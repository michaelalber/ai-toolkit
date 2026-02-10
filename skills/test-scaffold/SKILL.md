---
name: test-scaffold
description: Test generation conventions, naming patterns, mock strategies, and project structure for .NET test suites. Use when generating tests for C#/.NET projects with xUnit, FluentAssertions, and NSubstitute.
---

# Test Scaffold

> "The ratio of time spent reading versus writing code is well over 10 to 1. Tests should be the most readable code in the project."
> -- Robert C. Martin

## Core Philosophy

This skill provides the conventions, patterns, and structural guidance for generating .NET test suites. It covers test naming, file organization, mock patterns, the AAA (Arrange-Act-Assert) structure, and test project setup. Apply these conventions consistently across all generated tests.

**Non-Negotiable Constraints:**

1. **AAA Pattern Always** -- Every test method follows Arrange-Act-Assert with explicit comment markers separating each section. No exceptions.
2. **Descriptive Naming** -- Every test method name follows `MethodName_Scenario_ExpectedResult` format. The name must be a complete sentence describing what is being tested.
3. **One Assert Concept Per Test** -- Each test verifies one logical concept. Multiple assertions are acceptable when they all verify different aspects of the same single concept (e.g., multiple properties of a response object).
4. **No Test Interdependence** -- Tests must not depend on execution order. Each test sets up its own state, executes in isolation, and cleans up after itself.
5. **Mock Only What You Own** -- Mock interfaces you control. For third-party libraries, use their built-in test helpers or wrap them in your own interface first.

## Test Project Structure

### Standard .NET Test Project Layout

```
tests/
  MyApp.Tests/
    MyApp.Tests.csproj
    GlobalUsings.cs
    Features/                          # Mirrors src/MyApp/Features/
      Orders/
        CreateOrder/
          CreateOrderHandlerTests.cs
          CreateOrderValidatorTests.cs
          CreateOrderEndpointTests.cs
        GetOrderById/
          GetOrderByIdHandlerTests.cs
          GetOrderByIdEndpointTests.cs
        CancelOrder/
          CancelOrderHandlerTests.cs
          CancelOrderValidatorTests.cs
      Customers/
        CreateCustomer/
          CreateCustomerHandlerTests.cs
          CreateCustomerValidatorTests.cs
    Services/                          # Mirrors src/MyApp/Services/
      EmailServiceTests.cs
      PaymentGatewayTests.cs
    Common/
      Behaviors/
        ValidationBehaviorTests.cs
        LoggingBehaviorTests.cs
    Infrastructure/                    # Test utilities
      TestDbContextFactory.cs
      WebAppFactory.cs
      Builders/                        # Test data builders
        OrderBuilder.cs
        CustomerBuilder.cs
      Fakes/                           # Fake implementations
        FakeEmailService.cs
        FakeTimeProvider.cs
```

### Test Project Dependencies (.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
    <PackageReference Include="xunit" Version="2.*" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
    <PackageReference Include="FluentAssertions" Version="7.*" />
    <PackageReference Include="NSubstitute" Version="5.*" />
    <PackageReference Include="NSubstitute.Analyzers.CSharp" Version="1.*" />
    <PackageReference Include="FluentValidation.TestHelper" Version="11.*" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="9.*" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="9.*" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\MyApp\MyApp.csproj" />
  </ItemGroup>
</Project>
```

### GlobalUsings.cs

```csharp
global using Xunit;
global using FluentAssertions;
global using NSubstitute;
```

## AAA Pattern -- Arrange, Act, Assert

Every test method must have three clearly separated sections:

### Basic AAA Structure

```csharp
[Fact]
public async Task Handle_WithValidCommand_CreatesOrderAndReturnsId()
{
    // Arrange
    var repository = Substitute.For<IOrderRepository>();
    var handler = new CreateOrderHandler(repository);
    var command = new CreateOrderCommand(CustomerId: 1, ProductId: 10, Quantity: 2);

    repository.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>())
        .Returns(Task.FromResult(new Order { Id = 42 }));

    // Act
    var result = await handler.Handle(command, CancellationToken.None);

    // Assert
    result.OrderId.Should().Be(42);
    await repository.Received(1).AddAsync(
        Arg.Is<Order>(o => o.CustomerId == 1 && o.Quantity == 2),
        Arg.Any<CancellationToken>());
}
```

### AAA Rules

| Section | What Belongs Here | What Does NOT Belong |
|---------|-------------------|----------------------|
| **Arrange** | Object construction, mock setup, test data creation, database seeding | Assertions, method calls under test |
| **Act** | ONE call to the method under test. Store the result or capture the exception. | Multiple calls, assertions, additional setup |
| **Assert** | Assertions on the result, mock verification, state verification | Additional method calls, setup, side effects |

### Common AAA Mistakes

```csharp
// WRONG: Act and Assert mixed together
[Fact]
public void GetById_ReturnsOrder()
{
    // Arrange
    var repo = SetupRepo();

    // This is Act AND Assert combined -- avoid this
    repo.GetById(1).Should().NotBeNull();
}

// RIGHT: Act and Assert separated
[Fact]
public async Task GetById_WhenOrderExists_ReturnsOrder()
{
    // Arrange
    var repo = SetupRepo();

    // Act
    var result = await repo.GetByIdAsync(1);

    // Assert
    result.Should().NotBeNull();
    result!.Id.Should().Be(1);
}
```

## Test Naming Convention

### Pattern: `MethodName_Scenario_ExpectedResult`

```
[MethodUnderTest]_[StateOrInput]_[ExpectedBehavior]
```

### Examples by Category

| Category | Test Name | What It Tests |
|----------|-----------|---------------|
| Happy path | `Handle_WithValidCommand_CreatesOrder` | Normal successful operation |
| Not found | `Handle_WhenOrderNotFound_ReturnsNull` | Missing entity handling |
| Validation | `Validate_WithEmptyName_HasValidationError` | Input validation rules |
| Exception | `Handle_WhenRepositoryThrows_PropagatesException` | Error propagation |
| Guard clause | `Handle_WithNullCommand_ThrowsArgumentNullException` | Null parameter check |
| Edge case | `Handle_WithMaxIntQuantity_DoesNotOverflow` | Boundary condition |
| State change | `Handle_CancelsPendingOrder_SetsStatusToCancelled` | State mutation |
| Side effect | `Handle_AfterCreatingOrder_SendsConfirmationEmail` | External effect |

### Test Class Naming

| Source Class | Test Class | File Name |
|-------------|------------|-----------|
| `CreateOrderHandler` | `CreateOrderHandlerTests` | `CreateOrderHandlerTests.cs` |
| `CreateOrderValidator` | `CreateOrderValidatorTests` | `CreateOrderValidatorTests.cs` |
| `OrderService` | `OrderServiceTests` | `OrderServiceTests.cs` |
| `PaymentGateway` | `PaymentGatewayTests` | `PaymentGatewayTests.cs` |

## Mock Patterns

### NSubstitute Fundamentals

```csharp
// Create a substitute (mock)
var repository = Substitute.For<IOrderRepository>();

// Configure return values
repository.GetByIdAsync(1, Arg.Any<CancellationToken>())
    .Returns(new Order { Id = 1, Status = OrderStatus.Pending });

// Configure async return values
repository.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>())
    .Returns(Task.CompletedTask);

// Verify a call was made
await repository.Received(1).AddAsync(
    Arg.Is<Order>(o => o.CustomerId == 1),
    Arg.Any<CancellationToken>());

// Verify a call was NOT made
await repository.DidNotReceive().DeleteAsync(Arg.Any<int>(), Arg.Any<CancellationToken>());

// Configure to throw
repository.GetByIdAsync(Arg.Any<int>(), Arg.Any<CancellationToken>())
    .ThrowsAsync(new DbException("Connection lost"));
```

### What to Mock and What Not To Mock

| Component | Mock? | Reason |
|-----------|-------|--------|
| Repository interfaces | Yes | Isolates business logic from data access |
| Email / SMS services | Yes | Avoids sending real messages in tests |
| External HTTP APIs | Yes | Avoids network calls, controls responses |
| FreeMediator `ISender` | Yes | When testing code that dispatches commands |
| `ILogger<T>` | Usually no | Logging rarely needs assertion; pass `NullLogger<T>.Instance` |
| `DbContext` (EF Core) | No -- use InMemory | InMemoryDatabase is simpler and more realistic than mocking |
| Value objects / records | No | Use real instances -- they are simple data containers |
| Static utility methods | No | Wrap in an interface if mocking is needed |

## Test Data Patterns

### Builder Pattern for Test Data

```csharp
public class OrderBuilder
{
    private int _id = 1;
    private int _customerId = 1;
    private OrderStatus _status = OrderStatus.Pending;
    private decimal _total = 100.00m;
    private List<OrderItem> _items = new();

    public OrderBuilder WithId(int id) { _id = id; return this; }
    public OrderBuilder WithCustomerId(int id) { _customerId = id; return this; }
    public OrderBuilder WithStatus(OrderStatus s) { _status = s; return this; }
    public OrderBuilder WithTotal(decimal t) { _total = t; return this; }
    public OrderBuilder WithItem(int productId, int qty, decimal price)
    {
        _items.Add(new OrderItem { ProductId = productId, Quantity = qty, UnitPrice = price });
        return this;
    }

    public Order Build() => new()
    {
        Id = _id,
        CustomerId = _customerId,
        Status = _status,
        TotalAmount = _total,
        Items = _items,
        CreatedAt = DateTime.UtcNow
    };
}

// Usage in tests:
var order = new OrderBuilder()
    .WithStatus(OrderStatus.Pending)
    .WithItem(productId: 10, qty: 2, price: 25.00m)
    .Build();
```

### InMemory DbContext Factory

```csharp
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

## FluentValidation Testing

```csharp
public class CreateOrderValidatorTests
{
    private readonly CreateOrderValidator _validator = new();

    [Fact]
    public void Validate_WithValidCommand_HasNoErrors()
    {
        // Arrange
        var command = new CreateOrderCommand(CustomerId: 1, Items: new[] { ValidItem() });

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldNotHaveAnyValidationErrors();
    }

    [Fact]
    public void Validate_WithZeroCustomerId_HasErrorForCustomerId()
    {
        // Arrange
        var command = new CreateOrderCommand(CustomerId: 0, Items: new[] { ValidItem() });

        // Act
        var result = _validator.TestValidate(command);

        // Assert
        result.ShouldHaveValidationErrorFor(x => x.CustomerId)
            .WithErrorMessage("A valid customer is required.");
    }

    private static OrderItemDto ValidItem() =>
        new(ProductId: 1, Quantity: 1, UnitPrice: 10.00m);
}
```

## Integration Testing With WebApplicationFactory

```csharp
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
            db.Customers.Add(new Customer { Id = 1, Name = "Alice" });
            await db.SaveChangesAsync();
        });

        var payload = new { CustomerId = 1, Items = new[] { new { ProductId = 10, Quantity = 2, UnitPrice = 25.00m } } };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", payload);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }
}
```

## When to Use Each Test Type

```
Decision: What kind of test do I write?
│
├── Testing a handler's business logic in isolation?
│   └── UNIT TEST with mocked dependencies
│
├── Testing a FluentValidation validator?
│   └── UNIT TEST using TestValidate() extension
│
├── Testing the full HTTP pipeline (endpoint → mediator → handler → DB)?
│   └── INTEGRATION TEST with WebApplicationFactory
│
├── Testing a pipeline behavior (validation, logging, transactions)?
│   └── UNIT TEST with mocked RequestHandlerDelegate
│
├── Testing database queries or EF Core mappings?
│   └── UNIT TEST with InMemory DbContext
│
└── Testing external service interaction?
    └── UNIT TEST with mocked interface + optional INTEGRATION TEST with real service
```

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Testing private methods | Couples tests to implementation | Test through the public API |
| Excessive mocking | Tests become brittle and hard to read | Mock only external boundaries |
| Shared mutable state between tests | Tests fail intermittently | Each test creates its own state |
| Not disposing DbContext | Memory leaks in test runner | Implement `IDisposable` on test class |
| Hardcoded GUIDs/dates | Tests break across environments | Use `Guid.NewGuid()` and `DateTime.UtcNow` |
| Testing framework code | Wasted effort verifying EF Core or ASP.NET | Test YOUR logic, trust the framework |

## Reference Files

See detailed patterns and code examples:
- [Mock Patterns](references/mock-patterns.md) -- Mock, stub, and fake patterns for repositories, mediator, HttpClient, DbContext, and common .NET infrastructure
- [Naming Conventions](references/naming-conventions.md) -- Test naming patterns, file organization rules, and test project structure conventions
