# Feature Folder Patterns

## Folder Structure Overview

Every vertical slice feature lives in its own folder under `Features/`. Features are grouped by domain area, then by specific operation.

### Standard Layout

```
src/MyApp/
  Features/
    Orders/
      CreateOrder/
        CreateOrderCommand.cs
        CreateOrderResponse.cs
        CreateOrderHandler.cs
        CreateOrderValidator.cs
        CreateOrderEndpoint.cs
      GetOrderById/
        GetOrderByIdQuery.cs
        GetOrderByIdResponse.cs
        GetOrderByIdHandler.cs
        GetOrderByIdEndpoint.cs
      GetOrdersList/
        GetOrdersListQuery.cs
        GetOrdersListResponse.cs
        GetOrdersListHandler.cs
        GetOrdersListEndpoint.cs
      CancelOrder/
        CancelOrderCommand.cs
        CancelOrderResponse.cs
        CancelOrderHandler.cs
        CancelOrderValidator.cs
        CancelOrderEndpoint.cs
      OrderPlaced/
        OrderPlacedNotification.cs
        SendOrderConfirmationHandler.cs
        UpdateInventoryHandler.cs
    Customers/
      CreateCustomer/
        ...
      GetCustomerById/
        ...
  Common/
    Models/
      PagedResult.cs
    Behaviors/
      ValidationBehavior.cs
      LoggingBehavior.cs
      TransactionBehavior.cs
  Infrastructure/
    Persistence/
      AppDbContext.cs
    ServiceRegistration.cs
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Feature folder | `VerbNoun` (PascalCase) | `CreateOrder`, `GetOrderById` |
| Command record | `[Feature]Command` | `CreateOrderCommand` |
| Query record | `[Feature]Query` | `GetOrderByIdQuery` |
| Response record | `[Feature]Response` | `CreateOrderResponse` |
| Handler class | `[Feature]Handler` | `CreateOrderHandler` |
| Validator class | `[Feature]Validator` | `CreateOrderValidator` |
| Endpoint class | `[Feature]Endpoint` | `CreateOrderEndpoint` |
| Notification record | `[DomainEvent]Notification` | `OrderPlacedNotification` |
| Notification handler | `[ActionDescription]Handler` | `SendOrderConfirmationHandler` |

## Command Pattern

Commands mutate state. They represent a user's intent to change something in the system.

### Request Record

```csharp
// Features/Orders/CreateOrder/CreateOrderCommand.cs
using FreeMediator;

namespace MyApp.Features.Orders.CreateOrder;

public record CreateOrderCommand(
    int CustomerId,
    List<OrderItemDto> Items,
    string? ShippingNotes = null
) : IRequest<CreateOrderResponse>;

public record OrderItemDto(
    int ProductId,
    int Quantity,
    decimal UnitPrice
);
```

### Response Record

```csharp
// Features/Orders/CreateOrder/CreateOrderResponse.cs
namespace MyApp.Features.Orders.CreateOrder;

public record CreateOrderResponse(
    int OrderId,
    string OrderNumber,
    decimal TotalAmount,
    DateTime CreatedAt
);
```

### Handler

```csharp
// Features/Orders/CreateOrder/CreateOrderHandler.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Features.Orders.CreateOrder;

public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, CreateOrderResponse>
{
    private readonly AppDbContext _db;

    public CreateOrderHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task<CreateOrderResponse> Handle(
        CreateOrderCommand request, CancellationToken cancellationToken)
    {
        var order = new Order
        {
            CustomerId = request.CustomerId,
            OrderNumber = GenerateOrderNumber(),
            ShippingNotes = request.ShippingNotes,
            CreatedAt = DateTime.UtcNow,
            Status = OrderStatus.Pending
        };

        foreach (var item in request.Items)
        {
            order.Items.Add(new OrderItem
            {
                ProductId = item.ProductId,
                Quantity = item.Quantity,
                UnitPrice = item.UnitPrice
            });
        }

        _db.Orders.Add(order);
        await _db.SaveChangesAsync(cancellationToken);

        return new CreateOrderResponse(
            OrderId: order.Id,
            OrderNumber: order.OrderNumber,
            TotalAmount: order.Items.Sum(i => i.Quantity * i.UnitPrice),
            CreatedAt: order.CreatedAt
        );
    }

    private static string GenerateOrderNumber()
    {
        return $"ORD-{DateTime.UtcNow:yyyyMMdd}-{Guid.NewGuid().ToString()[..8].ToUpper()}";
    }
}
```

### Validator

```csharp
// Features/Orders/CreateOrder/CreateOrderValidator.cs
using FluentValidation;

namespace MyApp.Features.Orders.CreateOrder;

public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.CustomerId)
            .GreaterThan(0)
            .WithMessage("A valid customer is required.");

        RuleFor(x => x.Items)
            .NotEmpty()
            .WithMessage("At least one item is required.");

        RuleForEach(x => x.Items).ChildRules(item =>
        {
            item.RuleFor(i => i.ProductId)
                .GreaterThan(0)
                .WithMessage("A valid product is required.");

            item.RuleFor(i => i.Quantity)
                .GreaterThan(0)
                .WithMessage("Quantity must be at least 1.");

            item.RuleFor(i => i.UnitPrice)
                .GreaterThan(0)
                .WithMessage("Unit price must be positive.");
        });

        RuleFor(x => x.ShippingNotes)
            .MaximumLength(500)
            .When(x => x.ShippingNotes is not null)
            .WithMessage("Shipping notes cannot exceed 500 characters.");
    }
}
```

### Endpoint (Minimal API)

```csharp
// Features/Orders/CreateOrder/CreateOrderEndpoint.cs
using FreeMediator;
using Microsoft.AspNetCore.Mvc;

namespace MyApp.Features.Orders.CreateOrder;

public static class CreateOrderEndpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapPost("/api/orders", async (
            [FromBody] CreateOrderCommand command,
            IMediator mediator,
            CancellationToken ct) =>
        {
            var response = await mediator.Send(command, ct);
            return Results.Created($"/api/orders/{response.OrderId}", response);
        })
        .WithName("CreateOrder")
        .WithTags("Orders")
        .Produces<CreateOrderResponse>(StatusCodes.Status201Created)
        .ProducesValidationProblem()
        .RequireAuthorization();
    }
}
```

## Query Pattern

Queries read data. They never mutate state.

### Request Record

```csharp
// Features/Orders/GetOrderById/GetOrderByIdQuery.cs
using FreeMediator;

namespace MyApp.Features.Orders.GetOrderById;

public record GetOrderByIdQuery(int OrderId) : IRequest<GetOrderByIdResponse?>;
```

### Response Record

```csharp
// Features/Orders/GetOrderById/GetOrderByIdResponse.cs
namespace MyApp.Features.Orders.GetOrderById;

public record GetOrderByIdResponse(
    int OrderId,
    string OrderNumber,
    string CustomerName,
    decimal TotalAmount,
    string Status,
    DateTime CreatedAt,
    List<OrderItemResponse> Items
);

public record OrderItemResponse(
    string ProductName,
    int Quantity,
    decimal UnitPrice,
    decimal LineTotal
);
```

### Handler

```csharp
// Features/Orders/GetOrderById/GetOrderByIdHandler.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Features.Orders.GetOrderById;

public class GetOrderByIdHandler : IRequestHandler<GetOrderByIdQuery, GetOrderByIdResponse?>
{
    private readonly AppDbContext _db;

    public GetOrderByIdHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task<GetOrderByIdResponse?> Handle(
        GetOrderByIdQuery request, CancellationToken cancellationToken)
    {
        var order = await _db.Orders
            .Include(o => o.Customer)
            .Include(o => o.Items)
                .ThenInclude(i => i.Product)
            .Where(o => o.Id == request.OrderId)
            .Select(o => new GetOrderByIdResponse(
                OrderId: o.Id,
                OrderNumber: o.OrderNumber,
                CustomerName: o.Customer.Name,
                TotalAmount: o.Items.Sum(i => i.Quantity * i.UnitPrice),
                Status: o.Status.ToString(),
                CreatedAt: o.CreatedAt,
                Items: o.Items.Select(i => new OrderItemResponse(
                    ProductName: i.Product.Name,
                    Quantity: i.Quantity,
                    UnitPrice: i.UnitPrice,
                    LineTotal: i.Quantity * i.UnitPrice
                )).ToList()
            ))
            .FirstOrDefaultAsync(cancellationToken);

        return order;
    }
}
```

### Endpoint

```csharp
// Features/Orders/GetOrderById/GetOrderByIdEndpoint.cs
using FreeMediator;

namespace MyApp.Features.Orders.GetOrderById;

public static class GetOrderByIdEndpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapGet("/api/orders/{orderId:int}", async (
            int orderId,
            IMediator mediator,
            CancellationToken ct) =>
        {
            var response = await mediator.Send(new GetOrderByIdQuery(orderId), ct);
            return response is not null
                ? Results.Ok(response)
                : Results.NotFound();
        })
        .WithName("GetOrderById")
        .WithTags("Orders")
        .Produces<GetOrderByIdResponse>()
        .Produces(StatusCodes.Status404NotFound)
        .RequireAuthorization();
    }
}
```

## Paginated Query Pattern

For list queries with pagination, sorting, and filtering.

### Request Record

```csharp
// Features/Orders/GetOrdersList/GetOrdersListQuery.cs
using FreeMediator;

namespace MyApp.Features.Orders.GetOrdersList;

public record GetOrdersListQuery(
    int Page = 1,
    int PageSize = 20,
    string? Status = null,
    string? SortBy = "CreatedAt",
    bool SortDescending = true
) : IRequest<GetOrdersListResponse>;
```

### Response Record

```csharp
// Features/Orders/GetOrdersList/GetOrdersListResponse.cs
namespace MyApp.Features.Orders.GetOrdersList;

public record GetOrdersListResponse(
    List<OrderSummaryDto> Items,
    int TotalCount,
    int Page,
    int PageSize
);

public record OrderSummaryDto(
    int OrderId,
    string OrderNumber,
    string CustomerName,
    decimal TotalAmount,
    string Status,
    DateTime CreatedAt
);
```

### Handler

```csharp
// Features/Orders/GetOrdersList/GetOrdersListHandler.cs
using FreeMediator;
using Microsoft.EntityFrameworkCore;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Features.Orders.GetOrdersList;

public class GetOrdersListHandler
    : IRequestHandler<GetOrdersListQuery, GetOrdersListResponse>
{
    private readonly AppDbContext _db;

    public GetOrdersListHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task<GetOrdersListResponse> Handle(
        GetOrdersListQuery request, CancellationToken cancellationToken)
    {
        var query = _db.Orders
            .Include(o => o.Customer)
            .Include(o => o.Items)
            .AsQueryable();

        // Apply filtering
        if (!string.IsNullOrWhiteSpace(request.Status)
            && Enum.TryParse<OrderStatus>(request.Status, out var status))
        {
            query = query.Where(o => o.Status == status);
        }

        // Get total before pagination
        var totalCount = await query.CountAsync(cancellationToken);

        // Apply sorting
        query = request.SortBy?.ToLower() switch
        {
            "ordernumber" => request.SortDescending
                ? query.OrderByDescending(o => o.OrderNumber)
                : query.OrderBy(o => o.OrderNumber),
            "totalamount" => request.SortDescending
                ? query.OrderByDescending(o => o.Items.Sum(i => i.Quantity * i.UnitPrice))
                : query.OrderBy(o => o.Items.Sum(i => i.Quantity * i.UnitPrice)),
            _ => request.SortDescending
                ? query.OrderByDescending(o => o.CreatedAt)
                : query.OrderBy(o => o.CreatedAt)
        };

        // Apply pagination
        var items = await query
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(o => new OrderSummaryDto(
                OrderId: o.Id,
                OrderNumber: o.OrderNumber,
                CustomerName: o.Customer.Name,
                TotalAmount: o.Items.Sum(i => i.Quantity * i.UnitPrice),
                Status: o.Status.ToString(),
                CreatedAt: o.CreatedAt
            ))
            .ToListAsync(cancellationToken);

        return new GetOrdersListResponse(
            Items: items,
            TotalCount: totalCount,
            Page: request.Page,
            PageSize: request.PageSize
        );
    }
}
```

## Notification Pattern

Notifications represent domain events. Multiple handlers can react to a single notification independently.

### Notification Record

```csharp
// Features/Orders/OrderPlaced/OrderPlacedNotification.cs
using FreeMediator;

namespace MyApp.Features.Orders.OrderPlaced;

public record OrderPlacedNotification(
    int OrderId,
    string OrderNumber,
    int CustomerId,
    decimal TotalAmount,
    DateTime PlacedAt
) : INotification;
```

### Notification Handlers (Multiple)

```csharp
// Features/Orders/OrderPlaced/SendOrderConfirmationHandler.cs
using FreeMediator;

namespace MyApp.Features.Orders.OrderPlaced;

public class SendOrderConfirmationHandler : INotificationHandler<OrderPlacedNotification>
{
    private readonly IEmailService _emailService;
    private readonly AppDbContext _db;

    public SendOrderConfirmationHandler(IEmailService emailService, AppDbContext db)
    {
        _emailService = emailService;
        _db = db;
    }

    public async Task Handle(
        OrderPlacedNotification notification, CancellationToken cancellationToken)
    {
        var customer = await _db.Customers.FindAsync(
            new object[] { notification.CustomerId }, cancellationToken);

        if (customer is null) return;

        await _emailService.SendAsync(
            to: customer.Email,
            subject: $"Order Confirmation - {notification.OrderNumber}",
            body: $"Your order {notification.OrderNumber} for ${notification.TotalAmount} has been placed.",
            cancellationToken: cancellationToken
        );
    }
}
```

```csharp
// Features/Orders/OrderPlaced/UpdateInventoryHandler.cs
using FreeMediator;

namespace MyApp.Features.Orders.OrderPlaced;

public class UpdateInventoryHandler : INotificationHandler<OrderPlacedNotification>
{
    private readonly AppDbContext _db;

    public UpdateInventoryHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task Handle(
        OrderPlacedNotification notification, CancellationToken cancellationToken)
    {
        var order = await _db.Orders
            .Include(o => o.Items)
            .FirstAsync(o => o.Id == notification.OrderId, cancellationToken);

        foreach (var item in order.Items)
        {
            var product = await _db.Products.FindAsync(
                new object[] { item.ProductId }, cancellationToken);

            if (product is not null)
            {
                product.StockQuantity -= item.Quantity;
            }
        }

        await _db.SaveChangesAsync(cancellationToken);
    }
}
```

### Publishing Notifications From a Command Handler

```csharp
// Inside CreateOrderHandler, after saving the order:
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, CreateOrderResponse>
{
    private readonly AppDbContext _db;
    private readonly IMediator _mediator;

    public CreateOrderHandler(AppDbContext db, IMediator mediator)
    {
        _db = db;
        _mediator = mediator;
    }

    public async Task<CreateOrderResponse> Handle(
        CreateOrderCommand request, CancellationToken cancellationToken)
    {
        // ... create and save order ...

        await _db.SaveChangesAsync(cancellationToken);

        // Publish notification after successful persistence
        await _mediator.Publish(new OrderPlacedNotification(
            OrderId: order.Id,
            OrderNumber: order.OrderNumber,
            CustomerId: order.CustomerId,
            TotalAmount: order.Items.Sum(i => i.Quantity * i.UnitPrice),
            PlacedAt: order.CreatedAt
        ), cancellationToken);

        return new CreateOrderResponse(/* ... */);
    }
}
```

## FreeMediator Registration

### Program.cs Setup

```csharp
// Program.cs
using FreeMediator;
using FluentValidation;
using MyApp.Common.Behaviors;

var builder = WebApplication.CreateBuilder(args);

// Register FreeMediator - scans the assembly for handlers
builder.Services.AddFreeMediator(cfg =>
{
    cfg.RegisterServicesFromAssembly(typeof(Program).Assembly);
});

// Register FluentValidation validators
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Register pipeline behaviors (order matters)
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(TransactionBehavior<,>));

var app = builder.Build();

// Map feature endpoints
CreateOrderEndpoint.Map(app);
GetOrderByIdEndpoint.Map(app);
GetOrdersListEndpoint.Map(app);
CancelOrderEndpoint.Map(app);

app.Run();
```

### Endpoint Registration Extension (Optional)

For projects with many features, use a convention-based registration:

```csharp
// Infrastructure/EndpointRegistration.cs
using System.Reflection;

namespace MyApp.Infrastructure;

public static class EndpointRegistration
{
    public static void MapFeatureEndpoints(this WebApplication app)
    {
        var endpointTypes = typeof(Program).Assembly
            .GetTypes()
            .Where(t => t.Name.EndsWith("Endpoint") && t.IsClass && t.IsAbstract && t.IsSealed); // static classes

        foreach (var type in endpointTypes)
        {
            var mapMethod = type.GetMethod("Map", BindingFlags.Public | BindingFlags.Static);
            mapMethod?.Invoke(null, new object[] { app });
        }
    }
}

// In Program.cs:
app.MapFeatureEndpoints();
```

## Correct vs Incorrect Folder Structures

### INCORRECT: Organized by Layer

```
src/MyApp/
  Controllers/
    OrdersController.cs        <-- All order endpoints mixed together
    CustomersController.cs
  Services/
    OrderService.cs             <-- All order logic mixed together
    CustomerService.cs
  Repositories/
    OrderRepository.cs          <-- All order data access mixed together
    CustomerRepository.cs
  Models/
    Order.cs
    Customer.cs
  DTOs/
    CreateOrderDto.cs
    GetOrderDto.cs
    OrderListDto.cs
  Validators/
    CreateOrderValidator.cs
    UpdateOrderValidator.cs
```

Problems:
- Adding a feature requires touching 5+ folders
- Deleting a feature requires finding files scattered across the project
- Two developers working on different order features will conflict in the same files
- Impossible to tell at a glance what the application does

### INCORRECT: Feature Folders But Shared Types

```
src/MyApp/
  Features/
    Orders/
      CreateOrder/
        CreateOrderHandler.cs
      GetOrderById/
        GetOrderByIdHandler.cs
    Shared/
      OrderDto.cs               <-- Shared between features!
      OrderValidator.cs         <-- Shared between features!
      IOrderService.cs          <-- Shared abstraction!
```

Problems:
- `OrderDto` changes for one feature break another
- `IOrderService` couples features through a shared interface
- Shared validator cannot handle feature-specific validation rules

### CORRECT: Fully Isolated Feature Folders

```
src/MyApp/
  Features/
    Orders/
      CreateOrder/
        CreateOrderCommand.cs       <-- Own request type
        CreateOrderResponse.cs      <-- Own response type
        CreateOrderHandler.cs       <-- Own handler
        CreateOrderValidator.cs     <-- Own validator
        CreateOrderEndpoint.cs      <-- Own endpoint
      GetOrderById/
        GetOrderByIdQuery.cs        <-- Own request type
        GetOrderByIdResponse.cs     <-- Own response type
        GetOrderByIdHandler.cs      <-- Own handler
        GetOrderByIdEndpoint.cs     <-- Own endpoint
  Common/
    Behaviors/                      <-- Infrastructure, not features
      ValidationBehavior.cs
      LoggingBehavior.cs
  Infrastructure/
    Persistence/
      AppDbContext.cs               <-- Shared infrastructure
```

Benefits:
- Each feature is a self-contained unit
- Add a feature: create one folder with its files
- Delete a feature: delete one folder
- Modify a feature: change only files in that folder
- At a glance, the folder names tell you what the application does

## Void Command Pattern

For commands that do not need to return data (e.g., delete operations):

```csharp
// Features/Orders/CancelOrder/CancelOrderCommand.cs
using FreeMediator;

namespace MyApp.Features.Orders.CancelOrder;

public record CancelOrderCommand(
    int OrderId,
    string Reason
) : IRequest;
```

```csharp
// Features/Orders/CancelOrder/CancelOrderHandler.cs
using FreeMediator;
using MyApp.Infrastructure.Persistence;

namespace MyApp.Features.Orders.CancelOrder;

public class CancelOrderHandler : IRequestHandler<CancelOrderCommand>
{
    private readonly AppDbContext _db;

    public CancelOrderHandler(AppDbContext db)
    {
        _db = db;
    }

    public async Task Handle(
        CancelOrderCommand request, CancellationToken cancellationToken)
    {
        var order = await _db.Orders.FindAsync(
            new object[] { request.OrderId }, cancellationToken)
            ?? throw new NotFoundException($"Order {request.OrderId} not found");

        order.Status = OrderStatus.Cancelled;
        order.CancellationReason = request.Reason;
        order.CancelledAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(cancellationToken);
    }
}
```

```csharp
// Features/Orders/CancelOrder/CancelOrderEndpoint.cs
using FreeMediator;
using Microsoft.AspNetCore.Mvc;

namespace MyApp.Features.Orders.CancelOrder;

public static class CancelOrderEndpoint
{
    public static void Map(IEndpointRouteBuilder app)
    {
        app.MapDelete("/api/orders/{orderId:int}", async (
            int orderId,
            [FromBody] CancelOrderRequest body,
            IMediator mediator,
            CancellationToken ct) =>
        {
            await mediator.Send(new CancelOrderCommand(orderId, body.Reason), ct);
            return Results.NoContent();
        })
        .WithName("CancelOrder")
        .WithTags("Orders")
        .Produces(StatusCodes.Status204NoContent)
        .Produces(StatusCodes.Status404NotFound)
        .RequireAuthorization();
    }
}

public record CancelOrderRequest(string Reason);
```
