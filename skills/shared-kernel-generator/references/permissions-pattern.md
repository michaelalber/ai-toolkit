# Permission Model Pattern

## Overview

DenaliDataSystems modules use a hierarchical permission model following the format:

```
{Module}.{Resource}.{Action}
```

This pattern provides:
- Clear permission boundaries per module
- Fine-grained access control
- Easy integration with authorization middleware
- Self-documenting permission names

## Permission Format

### Structure
```
ModuleName.ResourceName.ActionName
```

### Examples
| Permission | Description |
|------------|-------------|
| `PickLists.PickList.Manage` | Full access to pick lists |
| `PickLists.PickList.Read` | Read-only access to pick lists |
| `PickLists.PickListItem.Create` | Create pick list items |
| `People.Employee.Read` | Read employee data |
| `People.Employee.Update` | Update employee data |
| `Training.TrainingRecord.Delete` | Delete training records |

## Permission Constants Class

### Standard Implementation
```csharp
// Permissions/PickListPermissions.cs
namespace DenaliDataSystems.PickLists.Permissions;

/// <summary>
/// Permission constants for the PickLists module.
/// Format: Module.Resource.Action
/// </summary>
public static class PickListPermissions
{
    /// <summary>
    /// Full management access to pick lists.
    /// Includes Create, Read, Update, Delete operations.
    /// </summary>
    public const string Manage = "PickLists.PickList.Manage";

    /// <summary>
    /// Read-only access to pick lists.
    /// </summary>
    public const string Read = "PickLists.PickList.Read";

    /// <summary>
    /// Create new pick lists.
    /// </summary>
    public const string Create = "PickLists.PickList.Create";

    /// <summary>
    /// Update existing pick lists.
    /// </summary>
    public const string Update = "PickLists.PickList.Update";

    /// <summary>
    /// Delete pick lists (soft delete).
    /// </summary>
    public const string Delete = "PickLists.PickList.Delete";

    /// <summary>
    /// Export pick lists to file.
    /// </summary>
    public const string Export = "PickLists.PickList.Export";

    /// <summary>
    /// Import pick lists from file.
    /// </summary>
    public const string Import = "PickLists.PickList.Import";

    /// <summary>
    /// All permissions for the PickList resource.
    /// </summary>
    public static readonly string[] All = { Manage, Read, Create, Update, Delete, Export, Import };
}

/// <summary>
/// Permission constants for pick list items.
/// </summary>
public static class PickListItemPermissions
{
    public const string Manage = "PickLists.PickListItem.Manage";
    public const string Read = "PickLists.PickListItem.Read";
    public const string Create = "PickLists.PickListItem.Create";
    public const string Update = "PickLists.PickListItem.Update";
    public const string Delete = "PickLists.PickListItem.Delete";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete };
}
```

### People Module Example
```csharp
// Permissions/PersonPermissions.cs
namespace DenaliDataSystems.People.Permissions;

public static class PersonPermissions
{
    public const string Manage = "People.Person.Manage";
    public const string Read = "People.Person.Read";
    public const string Create = "People.Person.Create";
    public const string Update = "People.Person.Update";
    public const string Delete = "People.Person.Delete";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete };
}

public static class EmployeePermissions
{
    public const string Manage = "People.Employee.Manage";
    public const string Read = "People.Employee.Read";
    public const string Create = "People.Employee.Create";
    public const string Update = "People.Employee.Update";
    public const string Delete = "People.Employee.Delete";
    public const string ViewSensitive = "People.Employee.ViewSensitive";
    public const string ManageClearance = "People.Employee.ManageClearance";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete, ViewSensitive, ManageClearance };
}
```

### Training Module Example
```csharp
// Permissions/TrainingPermissions.cs
namespace DenaliDataSystems.Training.Permissions;

public static class TrainingCoursePermissions
{
    public const string Manage = "Training.TrainingCourse.Manage";
    public const string Read = "Training.TrainingCourse.Read";
    public const string Create = "Training.TrainingCourse.Create";
    public const string Update = "Training.TrainingCourse.Update";
    public const string Delete = "Training.TrainingCourse.Delete";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete };
}

public static class TrainingRecordPermissions
{
    public const string Manage = "Training.TrainingRecord.Manage";
    public const string Read = "Training.TrainingRecord.Read";
    public const string Create = "Training.TrainingRecord.Create";
    public const string Update = "Training.TrainingRecord.Update";
    public const string Delete = "Training.TrainingRecord.Delete";
    public const string Certify = "Training.TrainingRecord.Certify";
    public const string ViewAll = "Training.TrainingRecord.ViewAll";

    public static readonly string[] All = { Manage, Read, Create, Update, Delete, Certify, ViewAll };
}
```

## Permission Hierarchy

### Manage Permission
The `Manage` permission implies all other permissions for that resource:

```csharp
// Permission hierarchy
Manage → Create, Read, Update, Delete

// Check logic
bool HasPermission(string permission)
{
    var resource = GetResource(permission); // e.g., "PickLists.PickList"
    var managePermission = $"{resource}.Manage";

    return userPermissions.Contains(permission) ||
           userPermissions.Contains(managePermission);
}
```

## Usage in Commands/Queries

### Attribute-Based Authorization
```csharp
// In command handler
using Microsoft.AspNetCore.Authorization;

namespace DenaliDataSystems.PickLists.Features.PickListFeature.Commands.CreatePickList;

[Authorize(Policy = PickListPermissions.Create)]
public sealed record CreatePickListCommand(string Name, string Key) : IRequest<int>;
```

### Imperative Authorization
```csharp
// In handler
internal sealed class CreatePickListHandler(
    PickListDbContext db,
    IAuthorizationService authService,
    IHttpContextAccessor httpContext) : IRequestHandler<CreatePickListCommand, int>
{
    public async Task<int> Handle(CreatePickListCommand request, CancellationToken ct)
    {
        var user = httpContext.HttpContext?.User;
        var authResult = await authService.AuthorizeAsync(user, PickListPermissions.Create);

        if (!authResult.Succeeded)
        {
            throw new UnauthorizedAccessException(
                $"Permission '{PickListPermissions.Create}' is required.");
        }

        // Proceed with command...
    }
}
```

## Policy Configuration

### In Program.cs / Startup.cs
```csharp
builder.Services.AddAuthorization(options =>
{
    // PickLists module policies
    options.AddPolicy(PickListPermissions.Manage, policy =>
        policy.RequireClaim("permission", PickListPermissions.Manage));

    options.AddPolicy(PickListPermissions.Read, policy =>
        policy.RequireAssertion(context =>
            context.User.HasClaim("permission", PickListPermissions.Read) ||
            context.User.HasClaim("permission", PickListPermissions.Manage)));

    options.AddPolicy(PickListPermissions.Create, policy =>
        policy.RequireAssertion(context =>
            context.User.HasClaim("permission", PickListPermissions.Create) ||
            context.User.HasClaim("permission", PickListPermissions.Manage)));

    // ... other policies
});
```

### Dynamic Policy Registration
```csharp
// Extension method for automatic policy registration
public static class PermissionPolicyExtensions
{
    public static AuthorizationOptions AddModulePermissions<TPermissionClass>(
        this AuthorizationOptions options) where TPermissionClass : class
    {
        var fields = typeof(TPermissionClass)
            .GetFields(BindingFlags.Public | BindingFlags.Static)
            .Where(f => f.FieldType == typeof(string));

        foreach (var field in fields)
        {
            var permission = (string)field.GetValue(null)!;

            options.AddPolicy(permission, policy =>
                policy.RequireAssertion(context =>
                    context.User.HasClaim("permission", permission) ||
                    HasManagePermission(context.User, permission)));
        }

        return options;
    }

    private static bool HasManagePermission(ClaimsPrincipal user, string permission)
    {
        var parts = permission.Split('.');
        if (parts.Length >= 2)
        {
            var managePermission = $"{parts[0]}.{parts[1]}.Manage";
            return user.HasClaim("permission", managePermission);
        }
        return false;
    }
}

// Usage
builder.Services.AddAuthorization(options =>
{
    options.AddModulePermissions<PickListPermissions>();
    options.AddModulePermissions<PickListItemPermissions>();
    options.AddModulePermissions<EmployeePermissions>();
});
```

## Blazor Component Authorization

### Using AuthorizeView
```razor
@using DenaliDataSystems.PickLists.Permissions

<AuthorizeView Policy="@PickListPermissions.Manage">
    <Authorized>
        <TelerikButton OnClick="@CreateNew" ThemeColor="primary">
            Add New Pick List
        </TelerikButton>
    </Authorized>
</AuthorizeView>

<AuthorizeView Policy="@PickListPermissions.Delete">
    <Authorized>
        <TelerikButton OnClick="@Delete" ThemeColor="error">
            Delete
        </TelerikButton>
    </Authorized>
</AuthorizeView>
```

### Using IAuthorizationService
```csharp
// In code-behind
@inject IAuthorizationService AuthService

private bool canManage;
private bool canDelete;

protected override async Task OnInitializedAsync()
{
    var authState = await AuthenticationStateProvider.GetAuthenticationStateAsync();
    var user = authState.User;

    canManage = (await AuthService.AuthorizeAsync(user, PickListPermissions.Manage)).Succeeded;
    canDelete = (await AuthService.AuthorizeAsync(user, PickListPermissions.Delete)).Succeeded;
}
```

## Role-to-Permission Mapping

### Example Role Definitions
```csharp
public static class Roles
{
    public static readonly Dictionary<string, string[]> RolePermissions = new()
    {
        ["Administrator"] = new[]
        {
            PickListPermissions.Manage,
            EmployeePermissions.Manage,
            TrainingCoursePermissions.Manage,
            TrainingRecordPermissions.Manage
        },

        ["Manager"] = new[]
        {
            PickListPermissions.Read,
            EmployeePermissions.Read,
            EmployeePermissions.Update,
            TrainingRecordPermissions.Manage
        },

        ["User"] = new[]
        {
            PickListPermissions.Read,
            EmployeePermissions.Read,
            TrainingRecordPermissions.Read
        },

        ["ReadOnly"] = new[]
        {
            PickListPermissions.Read,
            EmployeePermissions.Read,
            TrainingRecordPermissions.Read
        }
    };
}
```

## Permission Discovery

### Get All Module Permissions
```csharp
public static class PermissionDiscovery
{
    public static IEnumerable<string> GetAllPermissions(Assembly moduleAssembly)
    {
        return moduleAssembly.GetTypes()
            .Where(t => t.Name.EndsWith("Permissions") && t.IsClass && t.IsAbstract && t.IsSealed)
            .SelectMany(t => t.GetFields(BindingFlags.Public | BindingFlags.Static)
                .Where(f => f.FieldType == typeof(string))
                .Select(f => (string)f.GetValue(null)!))
            .Distinct();
    }
}

// Usage
var pickListPermissions = PermissionDiscovery.GetAllPermissions(typeof(PickListPermissions).Assembly);
// Returns: ["PickLists.PickList.Manage", "PickLists.PickList.Read", ...]
```

## Naming Conventions

| Component | Format | Example |
|-----------|--------|---------|
| Permission Class | `{Resource}Permissions` | `PickListPermissions` |
| Permission Constant | `{Action}` | `Manage`, `Read`, `Create` |
| Permission Value | `{Module}.{Resource}.{Action}` | `PickLists.PickList.Manage` |
| Policy Name | Same as Permission Value | `PickLists.PickList.Manage` |

## Standard Actions

| Action | Description | Implied by Manage |
|--------|-------------|-------------------|
| `Manage` | Full access | N/A (highest level) |
| `Read` | View resources | Yes |
| `Create` | Create new resources | Yes |
| `Update` | Modify existing resources | Yes |
| `Delete` | Remove resources (soft delete) | Yes |
| `Export` | Export data to file | Sometimes |
| `Import` | Import data from file | Sometimes |
| `ViewAll` | View all records (bypasses row-level security) | No |
| `ViewSensitive` | View sensitive fields (PII, etc.) | No |
