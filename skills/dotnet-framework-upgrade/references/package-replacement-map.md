# Package Replacement Map: .NET Framework to .NET 10

## Web Packages

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Microsoft.AspNet.Mvc` | Built-in (Microsoft.NET.Sdk.Web) | Part of ASP.NET Core |
| `Microsoft.AspNet.WebApi` | Built-in (Microsoft.NET.Sdk.Web) | Controllers unified |
| `Microsoft.AspNet.WebApi.Client` | Built-in | Use `System.Net.Http.Json` |
| `Microsoft.AspNet.WebApi.Core` | Built-in | Part of ASP.NET Core |
| `Microsoft.AspNet.WebPages` | Blazor or Razor Pages | Different architecture |
| `Microsoft.AspNet.Identity.Core` | `Microsoft.AspNetCore.Identity` | Similar API |
| `Microsoft.AspNet.Identity.EntityFramework` | `Microsoft.AspNetCore.Identity.EntityFrameworkCore` | |
| `Microsoft.AspNet.SignalR` | `Microsoft.AspNetCore.SignalR` | API changes |
| `Microsoft.Owin` | Built-in middleware | Different architecture |
| `Microsoft.Owin.Security.OAuth` | `Microsoft.AspNetCore.Authentication.JwtBearer` | |

## Entity Framework

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `EntityFramework` (EF6) | `Microsoft.EntityFrameworkCore.SqlServer` | Different API |
| `EntityFramework.SqlServer` | `Microsoft.EntityFrameworkCore.SqlServer` | |
| `EntityFramework.SqlServerCompact` | Not available | Use full SQL Server |

### EF Core Required Packages
```xml
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="10.0.0" PrivateAssets="all" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="10.0.0" PrivateAssets="all" />
```

## Logging

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `log4net` | `Serilog.Extensions.Logging` | Or Microsoft.Extensions.Logging |
| `NLog` | `NLog.Extensions.Logging` | NLog supports .NET 10 |
| `Common.Logging` | `Microsoft.Extensions.Logging` | |
| `Enterprise Library Logging` | `Microsoft.Extensions.Logging` | |

### Recommended Logging Setup
```xml
<PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
<PackageReference Include="Serilog.Sinks.Console" Version="5.0.1" />
<PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />
```

## Dependency Injection

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Unity` | `Microsoft.Extensions.DependencyInjection` | Built-in |
| `Autofac` | `Autofac.Extensions.DependencyInjection` | Or use built-in |
| `Ninject` | `Microsoft.Extensions.DependencyInjection` | Built-in preferred |
| `StructureMap` | `Microsoft.Extensions.DependencyInjection` | Built-in preferred |
| `Castle.Windsor` | `Microsoft.Extensions.DependencyInjection` | Built-in preferred |

### Built-in DI Example
```csharp
// In Program.cs
builder.Services.AddScoped<IMyService, MyService>();
builder.Services.AddSingleton<ICacheService, CacheService>();
builder.Services.AddTransient<IEmailService, EmailService>();
```

## JSON Serialization

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Newtonsoft.Json` | `System.Text.Json` (built-in) | Or keep Newtonsoft |

### System.Text.Json Migration
```csharp
// Newtonsoft.Json
var json = JsonConvert.SerializeObject(obj);
var obj = JsonConvert.DeserializeObject<MyType>(json);

// System.Text.Json
var json = JsonSerializer.Serialize(obj);
var obj = JsonSerializer.Deserialize<MyType>(json);
```

### Keep Newtonsoft for Complex Scenarios
```xml
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
<PackageReference Include="Microsoft.AspNetCore.Mvc.NewtonsoftJson" Version="10.0.0" />
```

## Validation

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `FluentValidation` | `FluentValidation` | Works on .NET 10 |
| `DataAnnotations` | `System.ComponentModel.DataAnnotations` | Built-in |

```xml
<PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
```

## HTTP Client

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Microsoft.Net.Http` | Built-in `System.Net.Http` | |
| `RestSharp` | `RestSharp` or `HttpClient` | RestSharp supports .NET 10 |
| `Flurl.Http` | `Flurl.Http` | Works on .NET 10 |

### Recommended Pattern
```csharp
// Use IHttpClientFactory
services.AddHttpClient<MyApiClient>(client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
});
```

## Authentication / Authorization

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Microsoft.Owin.Security.Cookies` | Built-in cookie auth | |
| `Microsoft.Owin.Security.OAuth` | `Microsoft.AspNetCore.Authentication.JwtBearer` | |
| `IdentityServer3` | `Duende.IdentityServer` or `OpenIddict` | |

```xml
<PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="10.0.0" />
```

## Caching

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `System.Runtime.Caching` | `Microsoft.Extensions.Caching.Memory` | |
| `StackExchange.Redis` | `StackExchange.Redis` | Works on .NET 10 |

```xml
<PackageReference Include="Microsoft.Extensions.Caching.Memory" Version="10.0.0" />
<PackageReference Include="Microsoft.Extensions.Caching.StackExchangeRedis" Version="10.0.0" />
```

## Testing

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `MSTest.TestFramework` | `MSTest.TestFramework` | Works on .NET 10 |
| `NUnit` | `NUnit` | Works on .NET 10 |
| `xunit` | `xunit` | Works on .NET 10 |
| `Moq` | `Moq` | Works on .NET 10 |
| `NSubstitute` | `NSubstitute` | Works on .NET 10 |

```xml
<PackageReference Include="xunit" Version="2.6.6" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.5.6" PrivateAssets="all" />
<PackageReference Include="Moq" Version="4.20.70" />
```

## Mapping

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `AutoMapper` | `AutoMapper` or `Mapster` | Both work on .NET 10 |

```xml
<!-- Recommended: Mapster (faster, simpler) -->
<PackageReference Include="Mapster" Version="7.4.0" />

<!-- Or AutoMapper -->
<PackageReference Include="AutoMapper.Extensions.Microsoft.DependencyInjection" Version="12.0.1" />
```

## PDF / Reporting

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `iTextSharp` | `itext7` | License changed |
| `Crystal Reports` | Telerik Reporting or SSRS | |
| `Microsoft.Reporting.WebForms` | SSRS or third-party | |

```xml
<PackageReference Include="QuestPDF" Version="2024.3.0" />
<!-- or -->
<PackageReference Include="itext7" Version="8.0.2" />
```

## Excel / Office

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Microsoft.Office.Interop.Excel` | `ClosedXML` or `EPPlus` | No COM dependency |
| `EPPlus` | `EPPlus` | Works on .NET 10 (license changed) |

```xml
<PackageReference Include="ClosedXML" Version="0.102.2" />
<!-- or -->
<PackageReference Include="EPPlus" Version="7.0.9" />
```

## Image Processing

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `System.Drawing.Common` | `SixLabors.ImageSharp` | Cross-platform |

```xml
<PackageReference Include="SixLabors.ImageSharp" Version="3.1.2" />
```

## Scheduling

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `Quartz` | `Quartz` | Works on .NET 10 |
| `Hangfire` | `Hangfire` | Works on .NET 10 |

```xml
<PackageReference Include="Hangfire.AspNetCore" Version="1.8.9" />
<PackageReference Include="Hangfire.SqlServer" Version="1.8.9" />
```

## CQRS / Mediator

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `MediatR` | `FreeMediator` | Recommended (Apache 2.0) |

```xml
<PackageReference Include="FreeMediator" Version="1.0.0" />
```

## Configuration Packages

| .NET Framework Package | .NET 10 Replacement | Notes |
|------------------------|---------------------|-------|
| `System.Configuration` | `Microsoft.Extensions.Configuration` | Built-in |
| `System.Configuration.ConfigurationManager` | `Microsoft.Extensions.Configuration.Json` | |

```xml
<PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="10.0.0" />
<PackageReference Include="Microsoft.Extensions.Configuration.EnvironmentVariables" Version="10.0.0" />
<PackageReference Include="Microsoft.Extensions.Configuration.UserSecrets" Version="10.0.0" />
```

## Removed Without Replacement

| Package | Alternative |
|---------|-------------|
| `System.Web.*` | Rewrite to ASP.NET Core |
| `Microsoft.VisualBasic.ApplicationServices` | Manual implementation |
| `System.EnterpriseServices` | Manual implementation |
| `System.Messaging` (MSMQ) | Azure Service Bus, RabbitMQ |
| `System.Transactions.TransactionScope` | Use EF Core transactions |

## Migration Script

Generate a package migration report:

```bash
# Extract current packages from packages.config
grep -h "<package id=" packages.config | \
  sed 's/.*id="\([^"]*\)".*/\1/' | sort -u

# Extract from SDK-style csproj
grep -h "PackageReference Include=" *.csproj | \
  sed 's/.*Include="\([^"]*\)".*/\1/' | sort -u
```
