# Options Pattern for Module Configuration

## Overview

Each DenaliDataSystems module uses the Options pattern for configuration, providing:
- Fluent API for configuration
- Strong typing for settings
- Testability (in-memory database support)
- Sensible defaults

## Options Class Pattern

### Complete Options Implementation
```csharp
// Extensions/DenaliPickListsOptions.cs
namespace DenaliDataSystems.PickLists.Extensions;

/// <summary>
/// Configuration options for the PickLists module.
/// </summary>
public sealed class DenaliPickListsOptions
{
    /// <summary>
    /// SQL Server connection string.
    /// Required when not using in-memory database.
    /// </summary>
    public string? ConnectionString { get; set; }

    /// <summary>
    /// Use in-memory database for testing.
    /// Default: false
    /// </summary>
    public bool IsInMemoryDatabase { get; set; }

    /// <summary>
    /// In-memory database name (for test isolation).
    /// Default: "DenaliPickLists"
    /// </summary>
    public string InMemoryDatabaseName { get; set; } = "DenaliPickLists";

    /// <summary>
    /// Cache expiration in minutes.
    /// Set to 0 to disable caching.
    /// Default: 30
    /// </summary>
    public int CacheExpirationMinutes { get; set; } = 30;

    /// <summary>
    /// Automatically run database migrations on startup.
    /// Default: true
    /// </summary>
    public bool AutoMigrateDatabase { get; set; } = true;

    /// <summary>
    /// Seed demo/sample data.
    /// Default: false
    /// </summary>
    public bool SeedDemoData { get; set; } = false;

    /// <summary>
    /// Enable detailed logging for debugging.
    /// Default: false
    /// </summary>
    public bool EnableDetailedLogging { get; set; } = false;

    /// <summary>
    /// Schema name for database tables.
    /// Default: "picklists"
    /// </summary>
    public string SchemaName { get; set; } = "picklists";

    // Fluent Configuration Methods

    /// <summary>
    /// Configures SQL Server with the specified connection string.
    /// </summary>
    /// <param name="connectionString">The SQL Server connection string.</param>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions UseSqlServer(string connectionString)
    {
        ConnectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        IsInMemoryDatabase = false;
        return this;
    }

    /// <summary>
    /// Configures in-memory database for testing.
    /// </summary>
    /// <param name="databaseName">Optional database name for test isolation.</param>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions UseInMemoryDatabase(string? databaseName = null)
    {
        IsInMemoryDatabase = true;
        if (databaseName != null)
        {
            InMemoryDatabaseName = databaseName;
        }
        return this;
    }

    /// <summary>
    /// Sets cache expiration time.
    /// </summary>
    /// <param name="minutes">Expiration in minutes. Use 0 to disable caching.</param>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithCacheExpiration(int minutes)
    {
        if (minutes < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(minutes), "Cache expiration cannot be negative.");
        }
        CacheExpirationMinutes = minutes;
        return this;
    }

    /// <summary>
    /// Disables caching.
    /// </summary>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithoutCaching()
    {
        CacheExpirationMinutes = 0;
        return this;
    }

    /// <summary>
    /// Enables demo data seeding.
    /// </summary>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithDemoData()
    {
        SeedDemoData = true;
        return this;
    }

    /// <summary>
    /// Disables automatic database migration.
    /// </summary>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithoutAutoMigration()
    {
        AutoMigrateDatabase = false;
        return this;
    }

    /// <summary>
    /// Enables detailed EF Core logging.
    /// </summary>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithDetailedLogging()
    {
        EnableDetailedLogging = true;
        return this;
    }

    /// <summary>
    /// Sets a custom schema name for database tables.
    /// </summary>
    /// <param name="schema">The schema name.</param>
    /// <returns>The options instance for method chaining.</returns>
    public DenaliPickListsOptions WithSchema(string schema)
    {
        SchemaName = schema ?? throw new ArgumentNullException(nameof(schema));
        return this;
    }

    /// <summary>
    /// Validates the options configuration.
    /// </summary>
    /// <exception cref="InvalidOperationException">Thrown when configuration is invalid.</exception>
    internal void Validate()
    {
        if (!IsInMemoryDatabase && string.IsNullOrWhiteSpace(ConnectionString))
        {
            throw new InvalidOperationException(
                "Connection string is required when not using in-memory database. " +
                "Call UseSqlServer() or UseInMemoryDatabase().");
        }
    }
}
```

## Dependency Injection Extension

### Module Registration Pattern
```csharp
// PickListsDependencyInjection.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using DenaliDataSystems.PickLists.Extensions;
using DenaliDataSystems.PickLists.Features.PickListFeature.Data;

namespace DenaliDataSystems.PickLists;

public static class PickListsDependencyInjection
{
    /// <summary>
    /// Registers all services for the PickLists module.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="configureOptions">Action to configure module options.</param>
    /// <returns>The service collection for method chaining.</returns>
    /// <example>
    /// services.AddDenaliPickLists(options =>
    /// {
    ///     options.UseSqlServer(connectionString);
    ///     options.WithCacheExpiration(60);
    /// });
    /// </example>
    public static IServiceCollection AddDenaliPickLists(
        this IServiceCollection services,
        Action<DenaliPickListsOptions> configureOptions)
    {
        // Build and validate options
        var options = new DenaliPickListsOptions();
        configureOptions(options);
        options.Validate();

        // Register options as singleton
        services.AddSingleton(options);

        // Register DbContext
        services.AddDbContext<PickListDbContext>((sp, opt) =>
        {
            var moduleOptions = sp.GetRequiredService<DenaliPickListsOptions>();

            if (moduleOptions.IsInMemoryDatabase)
            {
                opt.UseInMemoryDatabase(moduleOptions.InMemoryDatabaseName);
            }
            else
            {
                opt.UseSqlServer(moduleOptions.ConnectionString!);
            }

            if (moduleOptions.EnableDetailedLogging)
            {
                opt.EnableSensitiveDataLogging()
                   .EnableDetailedErrors()
                   .LogTo(Console.WriteLine, LogLevel.Information);
            }
        });

        // Register FreeMediator handlers from this assembly
        services.AddFreeMediator(typeof(PickListsDependencyInjection).Assembly);

        // Register FluentValidation validators
        services.AddValidatorsFromAssembly(typeof(PickListsDependencyInjection).Assembly);

        // Register caching if enabled
        if (options.CacheExpirationMinutes > 0)
        {
            services.AddMemoryCache();
        }

        return services;
    }

    /// <summary>
    /// Initializes the PickLists module (migrations and seeding).
    /// Call from application startup.
    /// </summary>
    public static async Task InitializeDenaliPickListsAsync(this IServiceProvider services)
    {
        using var scope = services.CreateScope();
        var options = scope.ServiceProvider.GetRequiredService<DenaliPickListsOptions>();
        var db = scope.ServiceProvider.GetRequiredService<PickListDbContext>();

        if (options.AutoMigrateDatabase && !options.IsInMemoryDatabase)
        {
            await db.Database.MigrateAsync();
        }

        if (options.SeedDemoData)
        {
            await SeedDemoDataAsync(db);
        }
    }

    private static async Task SeedDemoDataAsync(PickListDbContext db)
    {
        if (await db.PickLists.AnyAsync())
        {
            return; // Already seeded
        }

        var statusList = new PickList
        {
            Name = "Status",
            Key = "STATUS",
            Description = "General status values",
            IsActive = true,
            Items = new List<PickListItem>
            {
                new() { Text = "Active", Value = "active", SortOrder = 1, IsDefault = true },
                new() { Text = "Inactive", Value = "inactive", SortOrder = 2 },
                new() { Text = "Pending", Value = "pending", SortOrder = 3 }
            }
        };

        db.PickLists.Add(statusList);
        await db.SaveChangesAsync();
    }
}
```

## Usage Examples

### Production Configuration
```csharp
// In Program.cs
builder.Services.AddDenaliPickLists(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!);
    options.WithCacheExpiration(60);  // 60 minutes
});

// Initialize during startup
var app = builder.Build();
await app.Services.InitializeDenaliPickListsAsync();
```

### Testing Configuration
```csharp
// In test setup
services.AddDenaliPickLists(options =>
{
    options.UseInMemoryDatabase($"TestDb_{Guid.NewGuid()}");
    options.WithDemoData();
    options.WithoutCaching();
});
```

### Development Configuration
```csharp
// In Program.cs (Development environment)
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddDenaliPickLists(options =>
    {
        options.UseSqlServer(builder.Configuration.GetConnectionString("Development")!);
        options.WithDemoData();
        options.WithDetailedLogging();
    });
}
else
{
    builder.Services.AddDenaliPickLists(options =>
    {
        options.UseSqlServer(builder.Configuration.GetConnectionString("Production")!);
        options.WithCacheExpiration(120);
    });
}
```

### Configuration from appsettings.json
```csharp
// appsettings.json
{
  "DenaliPickLists": {
    "CacheExpirationMinutes": 60,
    "AutoMigrateDatabase": true,
    "SchemaName": "picklists"
  },
  "ConnectionStrings": {
    "Default": "Server=...;Database=...;..."
  }
}

// In Program.cs
builder.Services.AddDenaliPickLists(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")!);

    // Bind additional settings from config
    var configSection = builder.Configuration.GetSection("DenaliPickLists");
    options.CacheExpirationMinutes = configSection.GetValue<int>("CacheExpirationMinutes", 30);
    options.AutoMigrateDatabase = configSection.GetValue<bool>("AutoMigrateDatabase", true);
});
```

## Multi-Module Registration

```csharp
// Register multiple modules with shared connection string
var connectionString = builder.Configuration.GetConnectionString("Default")!;

builder.Services.AddDenaliPickLists(opt => opt.UseSqlServer(connectionString));
builder.Services.AddDenaliPeople(opt => opt.UseSqlServer(connectionString));
builder.Services.AddDenaliTraining(opt => opt.UseSqlServer(connectionString));
builder.Services.AddDenaliOrganization(opt => opt.UseSqlServer(connectionString));

// Initialize all modules
var app = builder.Build();
await app.Services.InitializeDenaliPickListsAsync();
await app.Services.InitializeDenaliPeopleAsync();
await app.Services.InitializeDenaliTrainingAsync();
await app.Services.InitializeDenaliOrganizationAsync();
```

## Options Naming Convention

```
Module: DenaliDataSystems.{ModuleName}
Options Class: Denali{ModuleName}Options
DI Extension: AddDenali{ModuleName}()
Initialize Method: InitializeDenali{ModuleName}Async()
```

Examples:
- `DenaliPickListsOptions` / `AddDenaliPickLists()`
- `DenaliPeopleOptions` / `AddDenaliPeople()`
- `DenaliTrainingOptions` / `AddDenaliTraining()`
- `DenaliOrganizationOptions` / `AddDenaliOrganization()`
