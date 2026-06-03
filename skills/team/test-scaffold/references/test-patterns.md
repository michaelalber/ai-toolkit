# .NET Test Patterns

Code patterns and decision tables for scaffolding .NET test suites. Mock/stub/fake patterns are in
`mock-patterns.md`; test naming and file organization in `naming-conventions.md`.

## Test Project Structure

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
      Customers/
        CreateCustomer/
          CreateCustomerHandlerTests.cs
          CreateCustomerValidatorTests.cs
    Services/                          # Mirrors src/MyApp/Services/
      EmailServiceTests.cs
    Common/
      Behaviors/
        ValidationBehaviorTests.cs
    Infrastructure/                    # Test utilities
      TestDbContextFactory.cs
      WebAppFactory.cs
      Builders/                        # Test data builders
        OrderBuilder.cs
      Fakes/                           # Fake implementations
        FakeEmailService.cs
```

## Test Project Dependencies (.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
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

```csharp
// GlobalUsings.cs
global using Xunit;
global using FluentAssertions;
global using NSubstitute;
```

## AAA Pattern — Arrange, Act, Assert

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

| Section | What Belongs Here | What Does NOT Belong |
|---------|-------------------|----------------------|
| **Arrange** | Object construction, mock setup, test data creation, database seeding | Assertions, method calls under test |
| **Act** | ONE call to the method under test. Store the result or capture the exception. | Multiple calls, assertions, additional setup |
| **Assert** | Assertions on the result, mock verification, state verification | Additional method calls, setup, side effects |

Do not mix Act and Assert in one expression (`repo.GetById(1).Should().NotBeNull()`). Store the
result from Act, then assert on it separately.

## Naming (quick reference)

Pattern: `MethodName_Scenario_ExpectedResult`. Full guidance in `naming-conventions.md`.

| Category | Test Name |
|----------|-----------|
| Happy path | `Handle_WithValidCommand_CreatesOrder` |
| Not found | `Handle_WhenOrderNotFound_ReturnsNull` |
| Validation | `Validate_WithEmptyName_HasValidationError` |
| Exception | `Handle_WhenRepositoryThrows_PropagatesException` |
| Guard clause | `Handle_WithNullCommand_ThrowsArgumentNullException` |
| Edge case | `Handle_WithMaxIntQuantity_DoesNotOverflow` |
| State change | `Handle_CancelsPendingOrder_SetsStatusToCancelled` |
| Side effect | `Handle_AfterCreatingOrder_SendsConfirmationEmail` |

Source class `CreateOrderHandler` → test class `CreateOrderHandlerTests` → file `CreateOrderHandlerTests.cs`.

## What to Mock and What Not To Mock

NSubstitute fundamentals and full mock/stub/fake patterns are in `mock-patterns.md`.

| Component | Mock? | Reason |
|-----------|-------|--------|
| Repository interfaces | Yes | Isolates business logic from data access |
| Email / SMS services | Yes | Avoids sending real messages in tests |
| External HTTP APIs | Yes | Avoids network calls, controls responses |
| FreeMediator `ISender` | Yes | When testing code that dispatches commands |
| `ILogger<T>` | Usually no | Pass `NullLogger<T>.Instance` |
| `DbContext` (EF Core) | No — use InMemory | InMemoryDatabase is simpler and more realistic |
| Value objects / records | No | Use real instances — simple data containers |
| Static utility methods | No | Wrap in an interface if mocking is needed |

## Test Data Builder

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
```

## InMemory DbContext Factory

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
        var command = new CreateOrderCommand(CustomerId: 1, Items: new[] { ValidItem() });
        var result = _validator.TestValidate(command);
        result.ShouldNotHaveAnyValidationErrors();
    }

    [Fact]
    public void Validate_WithZeroCustomerId_HasErrorForCustomerId()
    {
        var command = new CreateOrderCommand(CustomerId: 0, Items: new[] { ValidItem() });
        var result = _validator.TestValidate(command);
        result.ShouldHaveValidationErrorFor(x => x.CustomerId)
            .WithErrorMessage("A valid customer is required.");
    }

    private static OrderItemDto ValidItem() =>
        new(ProductId: 1, Quantity: 1, UnitPrice: 10.00m);
}
```

## Integration Testing with WebApplicationFactory

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

| Scenario | Test Type |
|----------|-----------|
| Handler's business logic in isolation | Unit test with mocked dependencies |
| FluentValidation validator | Unit test using `TestValidate()` extension |
| Full HTTP pipeline (endpoint → mediator → handler → DB) | Integration test with WebApplicationFactory |
| Pipeline behavior (validation, logging, transactions) | Unit test with mocked `RequestHandlerDelegate` |
| Database queries or EF Core mappings | Unit test with InMemory DbContext |
| External service interaction | Unit test with mocked interface + optional integration test |

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Testing private methods | Couples tests to implementation | Test through the public API |
| Excessive mocking | Tests become brittle and hard to read | Mock only external boundaries |
| Shared mutable state between tests | Tests fail intermittently | Each test creates its own state |
| Not disposing DbContext | Memory leaks in test runner | Implement `IDisposable` on the test class |
| Hardcoded GUIDs/dates | Tests break across environments | Use `Guid.NewGuid()` and `DateTime.UtcNow` |
| Testing framework code | Wasted effort | Test YOUR logic, trust the framework |
