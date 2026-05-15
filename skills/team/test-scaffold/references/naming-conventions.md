# Test Naming Conventions and File Organization

## Overview

Consistent naming makes test suites self-documenting. When a test fails, its name should tell you exactly what broke without reading the test body. This reference covers method naming, class naming, file placement, and project-level organization for .NET test projects using xUnit.

## Test Method Naming

### Pattern: `MethodName_Scenario_ExpectedResult`

Every test method name has three parts separated by underscores:

```
[MethodUnderTest]_[WhenConditionOrInput]_[ExpectedBehavior]
```

### Part 1: MethodUnderTest

The name of the public method being tested. Use the exact method name from the source code.

| Source Method | Test Prefix |
|--------------|-------------|
| `Handle(...)` | `Handle_` |
| `CreateAsync(...)` | `CreateAsync_` |
| `Validate(...)` | `Validate_` |
| Constructor | `Constructor_` or `Ctor_` |
| Property getter | `PropertyName_` |

### Part 2: Scenario (When / With / Given)

Describes the precondition, input state, or specific context. Start with `When`, `With`, or `Given` for clarity.

| Scenario Type | Example Prefix |
|--------------|----------------|
| Valid input | `WithValidCommand_` |
| Invalid input | `WithNullOrder_` |
| Entity exists | `WhenOrderExists_` |
| Entity missing | `WhenOrderNotFound_` |
| State condition | `WhenOrderIsAlreadyCancelled_` |
| Permission | `WhenUserIsNotAuthorized_` |
| Edge case | `WithEmptyItemsList_` |
| Boundary | `WithMaxIntQuantity_` |

### Part 3: ExpectedResult

Describes what the method should do under the given scenario. Use active verbs.

| Result Type | Example Suffix |
|-------------|----------------|
| Returns value | `ReturnsOrder` |
| Returns null | `ReturnsNull` |
| Returns empty | `ReturnsEmptyList` |
| Creates entity | `CreatesOrderInDatabase` |
| Throws exception | `ThrowsArgumentNullException` |
| Throws specific | `ThrowsOrderNotFoundException` |
| Side effect | `SendsConfirmationEmail` |
| State change | `SetsStatusToCancelled` |
| No error | `DoesNotThrow` |
| Validation | `HasValidationErrorForCustomerId` |
| No validation error | `HasNoValidationErrors` |

### Complete Examples

```csharp
// Handler tests
Handle_WithValidCommand_CreatesOrderAndReturnsId
Handle_WhenCustomerNotFound_ThrowsNotFoundException
Handle_WithNullCommand_ThrowsArgumentNullException
Handle_WhenOrderAlreadyCancelled_ThrowsInvalidOperationException
Handle_WithMultipleItems_CalculatesTotalCorrectly
Handle_WhenRepositoryThrows_PropagatesException

// Query handler tests
Handle_WhenOrderExists_ReturnsOrderWithItems
Handle_WhenOrderNotFound_ReturnsNull
Handle_WithPagination_ReturnsCorrectPage

// Validator tests
Validate_WithValidCommand_HasNoErrors
Validate_WithZeroCustomerId_HasErrorForCustomerId
Validate_WithEmptyItems_HasErrorForItems
Validate_WithNegativeUnitPrice_HasErrorForUnitPrice
Validate_WithNullShippingNotes_HasNoErrorForShippingNotes

// Endpoint / integration tests
Post_WithValidOrder_Returns201Created
Post_WithInvalidCommand_Returns400BadRequest
Get_WhenOrderExists_Returns200WithOrder
Get_WhenOrderNotFound_Returns404NotFound
Delete_WhenOrderIsPending_Returns204NoContent
```

## Test Class Naming

### Pattern: `[SourceClassName]Tests`

```
SourceClass             → TestClass
CreateOrderHandler      → CreateOrderHandlerTests
CreateOrderValidator    → CreateOrderValidatorTests
OrderService            → OrderServiceTests
PaymentGatewayClient    → PaymentGatewayClientTests
ValidationBehavior      → ValidationBehaviorTests
```

### Endpoint Test Classes

For integration tests that verify HTTP endpoints, use the feature name:

```
Feature                 → TestClass
CreateOrder endpoint    → CreateOrderEndpointTests
GetOrderById endpoint   → GetOrderByIdEndpointTests
```

### When a Class Has Many Tests

If a test class grows beyond 15-20 test methods, consider splitting by method:

```
CreateOrderHandlerTests.cs              (all methods, if manageable)

// OR split by method:
CreateOrderHandler_HandleTests.cs       (Handle method tests)
CreateOrderHandler_ValidateTests.cs     (Validate method tests)
```

Use partial classes to split into files while keeping them logically grouped:

```csharp
// CreateOrderHandlerTests.Handle.cs
public partial class CreateOrderHandlerTests
{
    [Fact]
    public async Task Handle_WithValidCommand_CreatesOrder() { ... }
}

// CreateOrderHandlerTests.EdgeCases.cs
public partial class CreateOrderHandlerTests
{
    [Fact]
    public async Task Handle_WithMaxIntQuantity_DoesNotOverflow() { ... }
}
```

## File Organization

### Mirror the Source Structure

Test files mirror the source project's folder structure exactly:

```
src/MyApp/                              tests/MyApp.Tests/
  Features/                               Features/
    Orders/                                 Orders/
      CreateOrder/                            CreateOrder/
        CreateOrderCommand.cs                   CreateOrderHandlerTests.cs
        CreateOrderHandler.cs                   CreateOrderValidatorTests.cs
        CreateOrderValidator.cs                 CreateOrderEndpointTests.cs
        CreateOrderEndpoint.cs
      GetOrderById/                           GetOrderById/
        GetOrderByIdQuery.cs                    GetOrderByIdHandlerTests.cs
        GetOrderByIdHandler.cs                  GetOrderByIdEndpointTests.cs
        GetOrderByIdEndpoint.cs
  Services/                               Services/
    EmailService.cs                         EmailServiceTests.cs
    PaymentGateway.cs                       PaymentGatewayTests.cs
  Common/                                 Common/
    Behaviors/                              Behaviors/
      ValidationBehavior.cs                   ValidationBehaviorTests.cs
      LoggingBehavior.cs                      LoggingBehaviorTests.cs
```

### Namespace Convention

Test namespaces mirror source namespaces with `.Tests` suffix:

```csharp
// Source namespace
namespace MyApp.Features.Orders.CreateOrder;

// Test namespace
namespace MyApp.Tests.Features.Orders.CreateOrder;
```

### Infrastructure Folder

Test infrastructure (factories, builders, fakes) lives in `Infrastructure/`:

```
tests/MyApp.Tests/
  Infrastructure/
    TestDbContextFactory.cs         # Creates in-memory DbContext instances
    WebAppFactory.cs                # Custom WebApplicationFactory for integration tests
    Builders/
      OrderBuilder.cs              # Test data builder for Order entities
      CustomerBuilder.cs           # Test data builder for Customer entities
    Fakes/
      FakeHttpMessageHandler.cs    # Fake HTTP handler for testing HTTP clients
      FakeTimeProvider.cs          # Controllable clock for time-dependent tests
      FakeEmailService.cs          # In-memory email service for verification
```

## Test Categorization With Traits

Use xUnit `[Trait]` attributes to categorize tests for selective execution:

### Standard Trait Categories

```csharp
// Category trait -- test type
[Trait("Category", "Unit")]
[Trait("Category", "Integration")]
[Trait("Category", "EndToEnd")]

// Feature trait -- domain feature
[Trait("Feature", "CreateOrder")]
[Trait("Feature", "CancelOrder")]

// Layer trait -- architectural layer
[Trait("Layer", "Handler")]
[Trait("Layer", "Validator")]
[Trait("Layer", "Endpoint")]
```

### Applying Traits

```csharp
[Fact]
[Trait("Category", "Unit")]
[Trait("Feature", "CreateOrder")]
[Trait("Layer", "Handler")]
public async Task Handle_WithValidCommand_CreatesOrder()
{
    // ...
}
```

### Running Tests by Trait

```bash
# Run only unit tests
dotnet test --filter "Category=Unit"

# Run only integration tests
dotnet test --filter "Category=Integration"

# Run all tests for a feature
dotnet test --filter "Feature=CreateOrder"

# Run only handler unit tests
dotnet test --filter "Category=Unit&Layer=Handler"

# Run all tests for a specific feature folder
dotnet test --filter "FullyQualifiedName~Features.Orders.CreateOrder"
```

## Test Method Organization Within a Class

Order test methods within a class consistently:

```csharp
public class CreateOrderHandlerTests : IDisposable
{
    // 1. Fields
    private readonly AppDbContext _db;
    private readonly IEmailService _emailService;
    private readonly CreateOrderHandler _handler;

    // 2. Constructor (test setup)
    public CreateOrderHandlerTests()
    {
        _db = TestDbContextFactory.Create();
        _emailService = Substitute.For<IEmailService>();
        _handler = new CreateOrderHandler(_db, _emailService);
    }

    // 3. Happy path tests (most important first)
    [Fact]
    public async Task Handle_WithValidCommand_CreatesOrder() { }

    [Fact]
    public async Task Handle_WithMultipleItems_CalculatesTotalCorrectly() { }

    // 4. Validation / guard clause tests
    [Fact]
    public async Task Handle_WithNullCommand_ThrowsArgumentNullException() { }

    [Fact]
    public async Task Handle_WithZeroCustomerId_ThrowsValidationException() { }

    // 5. Error path tests
    [Fact]
    public async Task Handle_WhenCustomerNotFound_ThrowsNotFoundException() { }

    [Fact]
    public async Task Handle_WhenDatabaseFails_PropagatesException() { }

    // 6. Edge case tests
    [Fact]
    public async Task Handle_WithSingleItem_SetsCorrectTotal() { }

    [Fact]
    public async Task Handle_WithMaxDecimalPrice_DoesNotOverflow() { }

    // 7. Side effect tests
    [Fact]
    public async Task Handle_AfterCreating_SendsConfirmationEmail() { }

    // 8. Helper methods (private, at the bottom)
    private static CreateOrderCommand ValidCommand() =>
        new(CustomerId: 1, Items: new[] { new OrderItemDto(1, 1, 10.00m) });

    // 9. Dispose
    public void Dispose() => _db.Dispose();
}
```

## Theory and InlineData Naming

When using `[Theory]` with `[InlineData]`, the method name should describe the pattern, and inline data provides the variations:

```csharp
[Theory]
[InlineData(0)]
[InlineData(-1)]
[InlineData(-100)]
public void Validate_WithInvalidCustomerId_HasError(int customerId)
{
    // Arrange
    var command = new CreateOrderCommand(CustomerId: customerId, Items: new[] { ValidItem() });

    // Act
    var result = _validator.TestValidate(command);

    // Assert
    result.ShouldHaveValidationErrorFor(x => x.CustomerId);
}

[Theory]
[InlineData("")]
[InlineData(" ")]
[InlineData(null)]
public void Validate_WithEmptyOrNullName_HasError(string? name)
{
    // Arrange
    var command = new CreateCustomerCommand(Name: name!, Email: "test@example.com");

    // Act
    var result = _validator.TestValidate(command);

    // Assert
    result.ShouldHaveValidationErrorFor(x => x.Name);
}
```

## Summary Checklist

When creating a new test file, verify:

- [ ] Test class name ends with `Tests`
- [ ] Test class is in the correct namespace (mirrors source + `.Tests`)
- [ ] Test file is in the correct folder (mirrors source structure)
- [ ] Every test method follows `MethodName_Scenario_ExpectedResult`
- [ ] Happy path tests come first, edge cases last
- [ ] Private helper methods are at the bottom of the class
- [ ] `IDisposable` is implemented if DbContext or other resources are used
- [ ] No test depends on another test's execution or state
