---
name: vertical-slice-scaffolder
description: Generates feature folders with FreeMediator CQRS pattern and Telerik Blazor components. Use when creating new features, scaffolding CQRS commands/queries, or setting up vertical slices. Triggers on phrases like "scaffold feature", "create slice", "new feature", "generate cqrs", "add command", "add query", "create handler".
---

# Vertical Slice Scaffolder

> "Vertical slices ensure that each feature is self-contained, making the codebase easier to understand, test, and maintain."

This skill generates complete vertical slice feature folders with FreeMediator CQRS pattern and Telerik Blazor UI components.

## Quick Start

1. **Name the feature**: Use domain noun (e.g., `Users`, `Orders`, `Trainings`)
2. **Generate structure**: Commands, Queries, DTOs, Pages, Tests
3. **Implement handlers**: Business logic in handlers
4. **Create UI**: Telerik Blazor components

## Generated Structure

```
Features/{FeatureName}/
├── Commands/
│   ├── Create{Entity}/
│   │   ├── Create{Entity}Command.cs
│   │   ├── Create{Entity}Handler.cs
│   │   └── Create{Entity}Validator.cs
│   ├── Update{Entity}/
│   │   ├── Update{Entity}Command.cs
│   │   ├── Update{Entity}Handler.cs
│   │   └── Update{Entity}Validator.cs
│   └── Delete{Entity}/
│       ├── Delete{Entity}Command.cs
│       └── Delete{Entity}Handler.cs
├── Queries/
│   ├── Get{Entity}ById/
│   │   ├── Get{Entity}ByIdQuery.cs
│   │   └── Get{Entity}ByIdHandler.cs
│   └── Get{Entity}List/
│       ├── Get{Entity}ListQuery.cs
│       └── Get{Entity}ListHandler.cs
├── DTOs/
│   ├── {Entity}Dto.cs
│   └── {Entity}ListDto.cs
├── Pages/
│   ├── {Entity}List.razor
│   └── {Entity}Edit.razor
├── Mapping/
│   └── {Entity}MappingConfig.cs
└── Tests/
    ├── Create{Entity}Tests.cs
    ├── Update{Entity}Tests.cs
    └── Get{Entity}ListTests.cs
```

## Command Templates

### Create Command
```csharp
// Features/Users/Commands/CreateUser/CreateUserCommand.cs
using FreeMediator;

namespace MyApp.Features.Users.Commands.CreateUser;

public record CreateUserCommand(
    string FirstName,
    string LastName,
    string Email,
    int DepartmentId
) : IRequest<Result<int>>;
```

### Create Handler
```csharp
// Features/Users/Commands/CreateUser/CreateUserHandler.cs
using FreeMediator;
using Mapster;
using MyApp.Domain.Entities;
using MyApp.Infrastructure.Data;

namespace MyApp.Features.Users.Commands.CreateUser;

public class CreateUserHandler : IRequestHandler<CreateUserCommand, Result<int>>
{
    private readonly AppDbContext _db;
    private readonly ILogger<CreateUserHandler> _logger;

    public CreateUserHandler(AppDbContext db, ILogger<CreateUserHandler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<Result<int>> Handle(CreateUserCommand request, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Creating user: {Email}", request.Email);

        // Check for duplicate email
        var exists = await _db.Users.AnyAsync(u => u.Email == request.Email, cancellationToken);
        if (exists)
        {
            return Result<int>.Failure("Email already exists");
        }

        var user = request.Adapt<User>();
        user.CreatedDate = DateTime.UtcNow;

        _db.Users.Add(user);
        await _db.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Created user {Id}: {Email}", user.Id, user.Email);

        return Result<int>.Success(user.Id);
    }
}
```

### Create Validator
```csharp
// Features/Users/Commands/CreateUser/CreateUserValidator.cs
using FluentValidation;

namespace MyApp.Features.Users.Commands.CreateUser;

public class CreateUserValidator : AbstractValidator<CreateUserCommand>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.FirstName)
            .NotEmpty().WithMessage("First name is required")
            .MaximumLength(100);

        RuleFor(x => x.LastName)
            .NotEmpty().WithMessage("Last name is required")
            .MaximumLength(100);

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format")
            .MaximumLength(255);

        RuleFor(x => x.DepartmentId)
            .GreaterThan(0).WithMessage("Department is required");
    }
}
```

### Update Command
```csharp
// Features/Users/Commands/UpdateUser/UpdateUserCommand.cs
public record UpdateUserCommand(
    int Id,
    string FirstName,
    string LastName,
    string Email,
    int DepartmentId
) : IRequest<Result>;
```

### Update Handler
```csharp
// Features/Users/Commands/UpdateUser/UpdateUserHandler.cs
public class UpdateUserHandler : IRequestHandler<UpdateUserCommand, Result>
{
    private readonly AppDbContext _db;
    private readonly ILogger<UpdateUserHandler> _logger;

    public UpdateUserHandler(AppDbContext db, ILogger<UpdateUserHandler> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<Result> Handle(UpdateUserCommand request, CancellationToken cancellationToken)
    {
        var user = await _db.Users.FindAsync(new object[] { request.Id }, cancellationToken);
        if (user == null)
        {
            return Result.NotFound($"User {request.Id} not found");
        }

        // Check for duplicate email (excluding current user)
        var emailExists = await _db.Users
            .AnyAsync(u => u.Email == request.Email && u.Id != request.Id, cancellationToken);
        if (emailExists)
        {
            return Result.Failure("Email already in use by another user");
        }

        request.Adapt(user);
        user.ModifiedDate = DateTime.UtcNow;

        await _db.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Updated user {Id}", user.Id);

        return Result.Success();
    }
}
```

### Delete Command
```csharp
// Features/Users/Commands/DeleteUser/DeleteUserCommand.cs
public record DeleteUserCommand(int Id) : IRequest<Result>;

// Features/Users/Commands/DeleteUser/DeleteUserHandler.cs
public class DeleteUserHandler : IRequestHandler<DeleteUserCommand, Result>
{
    private readonly AppDbContext _db;

    public DeleteUserHandler(AppDbContext db) => _db = db;

    public async Task<Result> Handle(DeleteUserCommand request, CancellationToken cancellationToken)
    {
        var user = await _db.Users.FindAsync(new object[] { request.Id }, cancellationToken);
        if (user == null)
        {
            return Result.NotFound($"User {request.Id} not found");
        }

        // Soft delete
        user.IsDeleted = true;
        user.ModifiedDate = DateTime.UtcNow;

        // Or hard delete:
        // _db.Users.Remove(user);

        await _db.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
```

## Query Templates

### Get By Id Query
```csharp
// Features/Users/Queries/GetUserById/GetUserByIdQuery.cs
public record GetUserByIdQuery(int Id) : IRequest<UserDto?>;

// Features/Users/Queries/GetUserById/GetUserByIdHandler.cs
public class GetUserByIdHandler : IRequestHandler<GetUserByIdQuery, UserDto?>
{
    private readonly AppDbContext _db;

    public GetUserByIdHandler(AppDbContext db) => _db = db;

    public async Task<UserDto?> Handle(GetUserByIdQuery request, CancellationToken cancellationToken)
    {
        return await _db.Users
            .Where(u => u.Id == request.Id)
            .ProjectToType<UserDto>()
            .FirstOrDefaultAsync(cancellationToken);
    }
}
```

### Get List Query
```csharp
// Features/Users/Queries/GetUserList/GetUserListQuery.cs
public record GetUserListQuery(
    int Page = 1,
    int PageSize = 20,
    string? SearchTerm = null,
    int? DepartmentId = null
) : IRequest<PagedResult<UserListDto>>;

// Features/Users/Queries/GetUserList/GetUserListHandler.cs
public class GetUserListHandler : IRequestHandler<GetUserListQuery, PagedResult<UserListDto>>
{
    private readonly AppDbContext _db;

    public GetUserListHandler(AppDbContext db) => _db = db;

    public async Task<PagedResult<UserListDto>> Handle(GetUserListQuery request, CancellationToken cancellationToken)
    {
        var query = _db.Users.AsQueryable();

        // Apply filters
        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            var term = request.SearchTerm.ToLower();
            query = query.Where(u =>
                u.FirstName.ToLower().Contains(term) ||
                u.LastName.ToLower().Contains(term) ||
                u.Email.ToLower().Contains(term));
        }

        if (request.DepartmentId.HasValue)
        {
            query = query.Where(u => u.DepartmentId == request.DepartmentId);
        }

        var totalCount = await query.CountAsync(cancellationToken);

        var items = await query
            .OrderBy(u => u.LastName)
            .ThenBy(u => u.FirstName)
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .ProjectToType<UserListDto>()
            .ToListAsync(cancellationToken);

        return new PagedResult<UserListDto>(items, totalCount, request.Page, request.PageSize);
    }
}
```

## DTO Templates

```csharp
// Features/Users/DTOs/UserDto.cs
namespace MyApp.Features.Users.DTOs;

public class UserDto
{
    public int Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public int DepartmentId { get; set; }
    public string? DepartmentName { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime ModifiedDate { get; set; }

    public string FullName => $"{FirstName} {LastName}";
}

// Features/Users/DTOs/UserListDto.cs
public class UserListDto
{
    public int Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string DepartmentName { get; set; } = string.Empty;
    public bool IsActive { get; set; }

    public string FullName => $"{FirstName} {LastName}";
}
```

## Mapping Configuration

```csharp
// Features/Users/Mapping/UserMappingConfig.cs
using Mapster;
using MyApp.Domain.Entities;
using MyApp.Features.Users.Commands.CreateUser;
using MyApp.Features.Users.DTOs;

namespace MyApp.Features.Users.Mapping;

public class UserMappingConfig : IRegister
{
    public void Register(TypeAdapterConfig config)
    {
        // Command to Entity
        config.NewConfig<CreateUserCommand, User>()
            .Ignore(dest => dest.Id)
            .Ignore(dest => dest.CreatedDate)
            .Ignore(dest => dest.ModifiedDate);

        // Entity to DTO
        config.NewConfig<User, UserDto>()
            .Map(dest => dest.DepartmentName, src => src.Department != null ? src.Department.Name : null);

        config.NewConfig<User, UserListDto>()
            .Map(dest => dest.DepartmentName, src => src.Department != null ? src.Department.Name : string.Empty);
    }
}
```

## Blazor Page Templates

### List Page
```razor
@* Features/Users/Pages/UserList.razor *@
@page "/users"
@inject IMediator Mediator
@inject NavigationManager Navigation

<PageTitle>Users</PageTitle>

<h1>Users</h1>

<TelerikGrid Data="@users"
             TItem="UserListDto"
             Pageable="true"
             PageSize="20"
             Sortable="true"
             FilterMode="GridFilterMode.FilterRow"
             OnRead="@OnGridRead"
             Height="600px">

    <GridToolBarTemplate>
        <TelerikButton OnClick="@CreateNew" ThemeColor="@ThemeConstants.Button.ThemeColor.Primary" Icon="@SvgIcon.Plus">
            Add User
        </TelerikButton>
    </GridToolBarTemplate>

    <GridColumns>
        <GridColumn Field="@nameof(UserListDto.Id)" Title="ID" Width="80px" />
        <GridColumn Field="@nameof(UserListDto.FullName)" Title="Name" />
        <GridColumn Field="@nameof(UserListDto.Email)" Title="Email" />
        <GridColumn Field="@nameof(UserListDto.DepartmentName)" Title="Department" />
        <GridColumn Field="@nameof(UserListDto.IsActive)" Title="Active" Width="100px">
            <Template>
                @{
                    var item = context as UserListDto;
                    <TelerikCheckBox Value="@item!.IsActive" Enabled="false" />
                }
            </Template>
        </GridColumn>

        <GridCommandColumn Width="200px">
            <GridCommandButton Icon="@SvgIcon.Pencil" OnClick="@(args => Edit(args.Item as UserListDto))">Edit</GridCommandButton>
            <GridCommandButton Icon="@SvgIcon.Trash" OnClick="@(args => Delete(args.Item as UserListDto))">Delete</GridCommandButton>
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

<TelerikDialog @bind-Visible="@showDeleteDialog" Title="Confirm Delete">
    <DialogContent>
        <p>Are you sure you want to delete @userToDelete?.FullName?</p>
    </DialogContent>
    <DialogButtons>
        <TelerikButton OnClick="@ConfirmDelete" ThemeColor="@ThemeConstants.Button.ThemeColor.Error">Delete</TelerikButton>
        <TelerikButton OnClick="@CancelDelete">Cancel</TelerikButton>
    </DialogButtons>
</TelerikDialog>

@code {
    private List<UserListDto> users = new();
    private bool showDeleteDialog = false;
    private UserListDto? userToDelete;

    private async Task OnGridRead(GridReadEventArgs args)
    {
        var result = await Mediator.Send(new GetUserListQuery(
            Page: args.Request.Page,
            PageSize: args.Request.PageSize));

        users = result.Items.ToList();
        args.Total = result.TotalCount;
    }

    private void CreateNew() => Navigation.NavigateTo("/users/edit");

    private void Edit(UserListDto? user)
    {
        if (user != null)
            Navigation.NavigateTo($"/users/edit/{user.Id}");
    }

    private void Delete(UserListDto? user)
    {
        userToDelete = user;
        showDeleteDialog = true;
    }

    private async Task ConfirmDelete()
    {
        if (userToDelete != null)
        {
            await Mediator.Send(new DeleteUserCommand(userToDelete.Id));
            showDeleteDialog = false;
            await InvokeAsync(StateHasChanged);
        }
    }

    private void CancelDelete()
    {
        showDeleteDialog = false;
        userToDelete = null;
    }
}
```

### Edit Page
```razor
@* Features/Users/Pages/UserEdit.razor *@
@page "/users/edit/{Id:int?}"
@inject IMediator Mediator
@inject NavigationManager Navigation

<PageTitle>@(Id.HasValue ? "Edit User" : "New User")</PageTitle>

<h1>@(Id.HasValue ? "Edit User" : "New User")</h1>

<TelerikForm Model="@user" OnValidSubmit="@HandleSubmit" Width="500px">
    <FormValidation>
        <FluentValidationValidator />
    </FormValidation>

    <FormItems>
        <FormItem Field="@nameof(UserDto.FirstName)" LabelText="First Name">
            <Template>
                <TelerikTextBox @bind-Value="@user.FirstName" Width="100%" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(UserDto.LastName)" LabelText="Last Name">
            <Template>
                <TelerikTextBox @bind-Value="@user.LastName" Width="100%" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(UserDto.Email)" LabelText="Email">
            <Template>
                <TelerikTextBox @bind-Value="@user.Email" Width="100%" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(UserDto.DepartmentId)" LabelText="Department">
            <Template>
                <TelerikDropDownList @bind-Value="@user.DepartmentId"
                                     Data="@departments"
                                     TextField="Name"
                                     ValueField="Id"
                                     DefaultText="Select Department..."
                                     Width="100%" />
            </Template>
        </FormItem>
    </FormItems>

    <FormButtons>
        <TelerikButton ButtonType="ButtonType.Submit" ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            Save
        </TelerikButton>
        <TelerikButton ButtonType="ButtonType.Button" OnClick="@Cancel">
            Cancel
        </TelerikButton>
    </FormButtons>
</TelerikForm>

@code {
    [Parameter] public int? Id { get; set; }

    private UserDto user = new();
    private List<DepartmentDto> departments = new();

    protected override async Task OnInitializedAsync()
    {
        departments = await Mediator.Send(new GetDepartmentListQuery());

        if (Id.HasValue)
        {
            var loaded = await Mediator.Send(new GetUserByIdQuery(Id.Value));
            if (loaded != null)
                user = loaded;
        }
    }

    private async Task HandleSubmit()
    {
        Result result;

        if (Id.HasValue)
        {
            result = await Mediator.Send(new UpdateUserCommand(
                Id.Value, user.FirstName, user.LastName, user.Email, user.DepartmentId));
        }
        else
        {
            var createResult = await Mediator.Send(new CreateUserCommand(
                user.FirstName, user.LastName, user.Email, user.DepartmentId));
            result = createResult.IsSuccess ? Result.Success() : Result.Failure(createResult.Error);
        }

        if (result.IsSuccess)
        {
            Navigation.NavigateTo("/users");
        }
    }

    private void Cancel() => Navigation.NavigateTo("/users");
}
```

## Test Templates

```csharp
// Features/Users/Tests/CreateUserTests.cs
using Xunit;
using Moq;
using FluentAssertions;
using MyApp.Features.Users.Commands.CreateUser;

namespace MyApp.Tests.Features.Users;

public class CreateUserTests
{
    [Fact]
    public async Task CreateUser_WithValidData_ReturnsSuccessWithId()
    {
        // Arrange
        var db = TestDbContext.Create();
        var handler = new CreateUserHandler(db, Mock.Of<ILogger<CreateUserHandler>>());

        var command = new CreateUserCommand(
            FirstName: "John",
            LastName: "Doe",
            Email: "john.doe@example.com",
            DepartmentId: 1);

        // Act
        var result = await handler.Handle(command, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.Should().BeGreaterThan(0);

        var user = await db.Users.FindAsync(result.Value);
        user.Should().NotBeNull();
        user!.FirstName.Should().Be("John");
        user.Email.Should().Be("john.doe@example.com");
    }

    [Fact]
    public async Task CreateUser_WithDuplicateEmail_ReturnsFailure()
    {
        // Arrange
        var db = TestDbContext.Create();
        db.Users.Add(new User { Email = "existing@example.com" });
        await db.SaveChangesAsync();

        var handler = new CreateUserHandler(db, Mock.Of<ILogger<CreateUserHandler>>());

        var command = new CreateUserCommand(
            FirstName: "Jane",
            LastName: "Doe",
            Email: "existing@example.com",
            DepartmentId: 1);

        // Act
        var result = await handler.Handle(command, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeFalse();
        result.Error.Should().Contain("already exists");
    }
}
```

## Scaffold Command

Generate a new feature with this structure:

```bash
# From project root
mkdir -p Features/Users/Commands/CreateUser
mkdir -p Features/Users/Commands/UpdateUser
mkdir -p Features/Users/Commands/DeleteUser
mkdir -p Features/Users/Queries/GetUserById
mkdir -p Features/Users/Queries/GetUserList
mkdir -p Features/Users/DTOs
mkdir -p Features/Users/Pages
mkdir -p Features/Users/Mapping
mkdir -p Features/Users/Tests
```

## References

- `references/cqrs-patterns.md` - CQRS implementation patterns
- `references/handler-patterns.md` - Handler best practices
- `references/telerik-component-patterns.md` - Telerik Blazor patterns
- `references/test-patterns.md` - Unit test patterns
- `references/validation-patterns.md` - FluentValidation patterns
