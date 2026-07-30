# Mock, Stub, and Fake Patterns for .NET Testing

## Overview

This reference covers mock, stub, and fake patterns for the most common .NET infrastructure dependencies. All examples use NSubstitute as the mocking framework and follow the conventions established in the test-scaffold skill.

The general rule: **mock interfaces you own, wrap interfaces you don't, and use in-memory alternatives where they exist.**

## Repository Mocking

Repositories are the most commonly mocked dependency in handler unit tests. They represent the boundary between business logic and data access.

### Basic Repository Mock

```csharp
public class GetOrderHandlerTests
{
    private readonly IOrderRepository _repository;
    private readonly GetOrderHandler _handler;

    public GetOrderHandlerTests()
    {
        _repository = Substitute.For<IOrderRepository>();
        _handler = new GetOrderHandler(_repository);
    }

    [Fact]
    public async Task Handle_WhenOrderExists_ReturnsOrder()
    {
        // Arrange
        var order = new Order { Id = 1, CustomerId = 5, Status = OrderStatus.Pending };
        _repository.GetByIdAsync(1, Arg.Any<CancellationToken>())
            .Returns(order);

        // Act
        var result = await _handler.Handle(new GetOrderQuery(1), CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(1);
    }

    [Fact]
    public async Task Handle_WhenOrderNotFound_ReturnsNull()
    {
        // Arrange
        _repository.GetByIdAsync(999, Arg.Any<CancellationToken>())
            .Returns((Order?)null);

        // Act
        var result = await _handler.Handle(new GetOrderQuery(999), CancellationToken.None);

        // Assert
        result.Should().BeNull();
    }
}
```

### Repository Write Verification

```csharp
[Fact]
public async Task Handle_WithValidCommand_PersistsOrder()
{
    // Arrange
    _repository.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>())
        .Returns(Task.CompletedTask);

    var command = new CreateOrderCommand(CustomerId: 1, ProductId: 10, Quantity: 3);

    // Act
    await _handler.Handle(command, CancellationToken.None);

    // Assert
    await _repository.Received(1).AddAsync(
        Arg.Is<Order>(o =>
            o.CustomerId == 1 &&
            o.Items.Count == 1 &&
            o.Items.First().ProductId == 10 &&
            o.Items.First().Quantity == 3),
        Arg.Any<CancellationToken>());
}
```

### Repository With Conditional Returns

```csharp
[Fact]
public async Task Handle_WhenCustomerHasExistingOrders_AppliesDiscount()
{
    // Arrange
    _repository.GetOrderCountByCustomerAsync(1, Arg.Any<CancellationToken>())
        .Returns(5); // Returning customer

    _repository.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>())
        .Returns(Task.CompletedTask);

    var command = new CreateOrderCommand(CustomerId: 1, ProductId: 10, Quantity: 1);

    // Act
    var result = await _handler.Handle(command, CancellationToken.None);

    // Assert
    result.DiscountApplied.Should().BeTrue();
    result.DiscountPercentage.Should().Be(10);
}
```

## FreeMediator / ISender Mocking

Mock the mediator when testing code that dispatches commands or queries to other handlers.

### Mocking ISender for Command Dispatch

```csharp
public class OrderOrchestratorTests
{
    private readonly ISender _sender;
    private readonly OrderOrchestrator _orchestrator;

    public OrderOrchestratorTests()
    {
        _sender = Substitute.For<ISender>();
        _orchestrator = new OrderOrchestrator(_sender);
    }

    [Fact]
    public async Task Process_CreatesOrderViaMediator()
    {
        // Arrange
        var expectedResponse = new CreateOrderResponse(OrderId: 42);
        _sender.Send(Arg.Any<CreateOrderCommand>(), Arg.Any<CancellationToken>())
            .Returns(expectedResponse);

        // Act
        var result = await _orchestrator.ProcessAsync(new OrderRequest { CustomerId = 1 });

        // Assert
        result.OrderId.Should().Be(42);
        await _sender.Received(1).Send(
            Arg.Is<CreateOrderCommand>(c => c.CustomerId == 1),
            Arg.Any<CancellationToken>());
    }
}
```

### Mocking IPublisher for Notification Dispatch

```csharp
[Fact]
public async Task Handle_AfterCreatingOrder_PublishesOrderPlacedNotification()
{
    // Arrange
    var publisher = Substitute.For<IPublisher>();
    var handler = new CreateOrderHandler(_repository, publisher);

    _repository.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>())
        .Returns(callInfo =>
        {
            var order = callInfo.Arg<Order>();
            order.Id = 42;
            return Task.CompletedTask;
        });

    // Act
    await handler.Handle(new CreateOrderCommand(CustomerId: 1), CancellationToken.None);

    // Assert
    await publisher.Received(1).Publish(
        Arg.Is<OrderPlacedNotification>(n =>
            n.OrderId == 42 &&
            n.CustomerId == 1),
        Arg.Any<CancellationToken>());
}
```

## HttpClient Mocking

For testing code that calls external HTTP APIs, use a custom `HttpMessageHandler` rather than mocking `HttpClient` directly.

### Custom Test HttpMessageHandler

```csharp
public class FakeHttpMessageHandler : HttpMessageHandler
{
    private readonly Dictionary<string, HttpResponseMessage> _responses = new();

    public void SetupResponse(string url, HttpStatusCode statusCode, string content)
    {
        _responses[url] = new HttpResponseMessage(statusCode)
        {
            Content = new StringContent(content, Encoding.UTF8, "application/json")
        };
    }

    public void SetupResponse(string url, HttpStatusCode statusCode, object content)
    {
        var json = JsonSerializer.Serialize(content);
        SetupResponse(url, statusCode, json);
    }

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var url = request.RequestUri!.ToString();

        if (_responses.TryGetValue(url, out var response))
            return Task.FromResult(response);

        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound)
        {
            Content = new StringContent($"No fake response configured for {url}")
        });
    }
}
```

### Using the Fake Handler in Tests

```csharp
public class PaymentGatewayClientTests
{
    private readonly FakeHttpMessageHandler _fakeHandler;
    private readonly PaymentGatewayClient _client;

    public PaymentGatewayClientTests()
    {
        _fakeHandler = new FakeHttpMessageHandler();
        var httpClient = new HttpClient(_fakeHandler)
        {
            BaseAddress = new Uri("https://api.payments.example.com")
        };
        _client = new PaymentGatewayClient(httpClient);
    }

    [Fact]
    public async Task ChargeAsync_WhenSuccessful_ReturnsTransactionId()
    {
        // Arrange
        _fakeHandler.SetupResponse(
            "https://api.payments.example.com/charge",
            HttpStatusCode.OK,
            new { TransactionId = "txn_abc123", Status = "succeeded" });

        // Act
        var result = await _client.ChargeAsync(new ChargeRequest
        {
            Amount = 100.00m,
            Currency = "USD",
            Token = "tok_visa_4242"
        });

        // Assert
        result.TransactionId.Should().Be("txn_abc123");
        result.Status.Should().Be("succeeded");
    }

    [Fact]
    public async Task ChargeAsync_WhenDeclined_ThrowsPaymentDeclinedException()
    {
        // Arrange
        _fakeHandler.SetupResponse(
            "https://api.payments.example.com/charge",
            HttpStatusCode.PaymentRequired,
            new { Error = "card_declined", Message = "Insufficient funds" });

        // Act
        var act = () => _client.ChargeAsync(new ChargeRequest
        {
            Amount = 100.00m,
            Currency = "USD",
            Token = "tok_declined"
        });

        // Assert
        await act.Should().ThrowAsync<PaymentDeclinedException>()
            .WithMessage("*Insufficient funds*");
    }
}
```

## DbContext -- InMemory Provider

For testing data access logic, prefer EF Core's InMemory provider over mocking `DbContext`. Mocking `DbSet<T>` is fragile and does not test LINQ translation.

### InMemory DbContext Pattern

```csharp
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
    public async Task Handle_PersistsOrderToDatabase()
    {
        // Arrange
        _db.Customers.Add(new Customer { Id = 1, Name = "Alice" });
        await _db.SaveChangesAsync();

        var command = new CreateOrderCommand(CustomerId: 1, ProductId: 10, Quantity: 2);

        // Act
        var response = await _handler.Handle(command, CancellationToken.None);

        // Assert
        var savedOrder = await _db.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == response.OrderId);

        savedOrder.Should().NotBeNull();
        savedOrder!.CustomerId.Should().Be(1);
        savedOrder.Items.Should().HaveCount(1);
        savedOrder.Items.First().Quantity.Should().Be(2);
    }

    public void Dispose() => _db.Dispose();
}
```

### When InMemory Is Not Enough

The InMemory provider does not support:
- Transactions (`BeginTransactionAsync`)
- Raw SQL (`FromSqlRaw`)
- Database-specific behavior (JSON columns, full-text search)
- Concurrency token enforcement

For these scenarios, use SQLite in-memory mode:

```csharp
public static AppDbContext CreateSqliteInMemory()
{
    var connection = new SqliteConnection("DataSource=:memory:");
    connection.Open();

    var options = new DbContextOptionsBuilder<AppDbContext>()
        .UseSqlite(connection)
        .Options;

    var db = new AppDbContext(options);
    db.Database.EnsureCreated();
    return db;
}
```

## Pipeline Behavior Mocking

When testing FreeMediator pipeline behaviors, mock the `RequestHandlerDelegate<TResponse>` to simulate the next handler in the pipeline.

```csharp
public class ValidationBehaviorTests
{
    [Fact]
    public async Task Handle_WhenValidationPasses_CallsNext()
    {
        // Arrange
        var validators = new List<IValidator<CreateOrderCommand>>
        {
            new CreateOrderValidator()
        };
        var behavior = new ValidationBehavior<CreateOrderCommand, CreateOrderResponse>(validators);

        var validCommand = new CreateOrderCommand(CustomerId: 1, Items: new[] { ValidItem() });
        var expectedResponse = new CreateOrderResponse(OrderId: 42);

        RequestHandlerDelegate<CreateOrderResponse> next = () =>
            Task.FromResult(expectedResponse);

        // Act
        var result = await behavior.Handle(validCommand, next, CancellationToken.None);

        // Assert
        result.OrderId.Should().Be(42);
    }

    [Fact]
    public async Task Handle_WhenValidationFails_ThrowsValidationException()
    {
        // Arrange
        var validators = new List<IValidator<CreateOrderCommand>>
        {
            new CreateOrderValidator()
        };
        var behavior = new ValidationBehavior<CreateOrderCommand, CreateOrderResponse>(validators);

        var invalidCommand = new CreateOrderCommand(CustomerId: 0, Items: new List<OrderItemDto>());

        RequestHandlerDelegate<CreateOrderResponse> next = () =>
            Task.FromResult(new CreateOrderResponse(OrderId: 0));

        // Act
        var act = () => behavior.Handle(invalidCommand, next, CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<ValidationException>();
    }
}
```

## Email / Notification Service Mocking

```csharp
[Fact]
public async Task Handle_SendsConfirmationEmail()
{
    // Arrange
    var emailService = Substitute.For<IEmailService>();
    var handler = new OrderConfirmationHandler(emailService, _db);

    // Act
    await handler.Handle(new OrderPlacedNotification(OrderId: 1, CustomerId: 1),
        CancellationToken.None);

    // Assert
    await emailService.Received(1).SendAsync(
        to: "customer@example.com",
        subject: Arg.Is<string>(s => s.Contains("Order Confirmation")),
        body: Arg.Is<string>(b => b.Contains("Order #1")),
        cancellationToken: Arg.Any<CancellationToken>());
}

[Fact]
public async Task Handle_WhenEmailFails_DoesNotThrow()
{
    // Arrange
    var emailService = Substitute.For<IEmailService>();
    emailService.SendAsync(Arg.Any<string>(), Arg.Any<string>(),
        Arg.Any<string>(), Arg.Any<CancellationToken>())
        .ThrowsAsync(new SmtpException("Connection refused"));

    var handler = new OrderConfirmationHandler(emailService, _db);

    // Act
    var act = () => handler.Handle(
        new OrderPlacedNotification(OrderId: 1, CustomerId: 1),
        CancellationToken.None);

    // Assert -- handler should swallow email failures gracefully
    await act.Should().NotThrowAsync();
}
```

## ILogger -- Usually Do Not Mock

Logging is a cross-cutting concern that rarely needs assertion in unit tests. Use `NullLogger<T>` to satisfy the dependency without adding noise:

```csharp
using Microsoft.Extensions.Logging.Abstractions;

public class OrderHandlerTests
{
    private readonly ILogger<OrderHandler> _logger = NullLogger<OrderHandler>.Instance;
    private readonly OrderHandler _handler;

    public OrderHandlerTests()
    {
        _handler = new OrderHandler(_repository, _logger);
    }
}
```

If you DO need to verify logging (e.g., audit logging), use a fake:

```csharp
public class FakeLogger<T> : ILogger<T>
{
    public List<(LogLevel Level, string Message)> Entries { get; } = new();

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state,
        Exception? exception, Func<TState, Exception?, string> formatter)
    {
        Entries.Add((logLevel, formatter(state, exception)));
    }

    public bool IsEnabled(LogLevel logLevel) => true;
    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
}
```

## ITimeProvider / IClock Faking

For time-dependent logic, inject a clock interface rather than using `DateTime.UtcNow` directly:

```csharp
public class FakeTimeProvider : TimeProvider
{
    private DateTimeOffset _now;

    public FakeTimeProvider(DateTimeOffset now) => _now = now;

    public override DateTimeOffset GetUtcNow() => _now;

    public void Advance(TimeSpan duration) => _now = _now.Add(duration);
}

// In tests:
[Fact]
public async Task Handle_SetsCreatedAtToCurrentTime()
{
    // Arrange
    var fixedTime = new DateTimeOffset(2025, 6, 15, 10, 0, 0, TimeSpan.Zero);
    var clock = new FakeTimeProvider(fixedTime);
    var handler = new CreateOrderHandler(_repository, clock);

    // Act
    var result = await handler.Handle(command, CancellationToken.None);

    // Assert
    result.CreatedAt.Should().Be(fixedTime);
}
```

## Summary: Mock Decision Matrix

| Dependency Type | Technique | Framework |
|----------------|-----------|-----------|
| Repository interface | Substitute | NSubstitute |
| ISender / IPublisher (FreeMediator) | Substitute | NSubstitute |
| IEmailService, INotificationService | Substitute | NSubstitute |
| HttpClient | FakeHttpMessageHandler | Custom |
| DbContext | InMemory provider | EF Core InMemory |
| ILogger<T> | NullLogger<T> | Microsoft.Extensions |
| TimeProvider | FakeTimeProvider | Custom |
| IValidator<T> | Real instance | FluentValidation |
| Value objects / records | Real instance | None |
