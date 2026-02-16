# .NET Security Checklist

Framework-specific security checks for .NET and .NET Framework applications.

---

## Authentication & Identity

### ASP.NET Core Identity

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Password complexity configured | `grep -rn "Password\." --include="*.cs"` | High |
| Account lockout enabled | `grep -rn "Lockout\." --include="*.cs"` | High |
| 2FA available for sensitive apps | `grep -rn "TwoFactor\|2FA\|MFA" --include="*.cs"` | Medium |
| Password hasher is default (PBKDF2) or stronger | Check for custom `IPasswordHasher` | Medium |

### JWT Configuration

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Token expiration set | `grep -rn "Expires\|ValidFor" --include="*.cs"` | High |
| Issuer validation enabled | `grep -rn "ValidateIssuer.*false" --include="*.cs"` | High |
| Audience validation enabled | `grep -rn "ValidateAudience.*false" --include="*.cs"` | High |
| Strong signing key | `grep -rn "SymmetricSecurityKey\|SigningCredentials" --include="*.cs"` | Critical |
| Key not hardcoded | Check for keys in code vs configuration | Critical |

### Cookie Security

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| HttpOnly flag set | `grep -rn "HttpOnly" --include="*.cs"` | High |
| Secure flag set | `grep -rn "SecurePolicy" --include="*.cs"` | High |
| SameSite configured | `grep -rn "SameSite" --include="*.cs"` | Medium |

---

## Data Protection

### Entity Framework

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| No raw SQL with concatenation | `grep -rn "FromSqlRaw\|ExecuteSqlRaw" --include="*.cs"` | Critical |
| Parameterized queries used | Check SQL patterns | Critical |
| No SQL in string interpolation | `grep -rn '\$".*SELECT\|$".*INSERT\|$".*UPDATE' --include="*.cs"` | Critical |
| Async methods used correctly | `grep -rn "\.Result\|\.Wait()" --include="*.cs"` | Low |

### Connection Strings

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| No hardcoded connection strings | `grep -rn "Server=.*Password=" --include="*.cs"` | Critical |
| Stored in configuration | Check appsettings.json, secrets | High |
| Encrypted in .NET Framework | Check web.config encryption | High |
| Integrated Security preferred | `grep -rn "Integrated Security\|Trusted_Connection" --include="*.config" --include="*.json"` | Medium |

### Sensitive Data

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| PII encrypted at rest | Review data models | High |
| Secrets in User Secrets / Key Vault | `grep -rn "AddUserSecrets\|AddAzureKeyVault" --include="*.cs"` | High |
| No sensitive data in logs | `grep -rn "Log.*password\|Log.*token\|Log.*key" -i --include="*.cs"` | High |
| Data Protection API used | `grep -rn "IDataProtector\|DataProtection" --include="*.cs"` | Medium |

---

## Input Validation

### Model Validation

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| DataAnnotations used | `grep -rn "\[Required\]\|\[StringLength\]\|\[Range\]" --include="*.cs"` | Medium |
| ModelState validated | `grep -rn "ModelState\.IsValid" --include="*.cs"` | Medium |
| Custom validation for business rules | Review validators | Medium |
| FluentValidation configured | `grep -rn "AbstractValidator\|IRuleBuilder" --include="*.cs"` | Low |

### FluentValidation Security Patterns

FluentValidation provides powerful validation but must be configured securely.

| Check | Issue | Severity |
|-------|-------|----------|
| Validators registered | All command/request DTOs have validators | High |
| String length limits | `MaximumLength()` on all string properties | Medium |
| Email validation | `EmailAddress()` for email fields | Medium |
| URL validation | Custom validator for URLs | Medium |
| No SQL/script injection | `Matches()` with safe patterns | High |
| Async validation secured | No sensitive data in async validators | Medium |

**Secure FluentValidation Patterns:**

```csharp
public class CreateUserCommandValidator : AbstractValidator<CreateUserCommand>
{
    public CreateUserCommandValidator()
    {
        // Required fields
        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .MaximumLength(256);

        RuleFor(x => x.Username)
            .NotEmpty()
            .MinimumLength(3)
            .MaximumLength(50)
            .Matches(@"^[a-zA-Z0-9_]+$")
            .WithMessage("Username can only contain letters, numbers, and underscores");

        // Prevent injection in free-text fields
        RuleFor(x => x.DisplayName)
            .MaximumLength(100)
            .Must(NotContainDangerousPatterns)
            .WithMessage("Invalid characters in display name");

        // URL validation
        RuleFor(x => x.WebsiteUrl)
            .Must(BeAValidUrl)
            .When(x => !string.IsNullOrEmpty(x.WebsiteUrl))
            .WithMessage("Invalid URL format");
    }

    private bool NotContainDangerousPatterns(string value)
    {
        if (string.IsNullOrEmpty(value)) return true;

        var dangerous = new[] { "<script", "javascript:", "onerror=", "onclick=" };
        return !dangerous.Any(d => value.Contains(d, StringComparison.OrdinalIgnoreCase));
    }

    private bool BeAValidUrl(string url)
    {
        if (string.IsNullOrEmpty(url)) return true;

        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri))
            return false;

        // Only allow http/https
        return uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps;
    }
}
```

**Validator Registration (CQRS with FreeMediator):**

```csharp
// Ensure all commands have validators
services.AddValidatorsFromAssemblyContaining<CreateUserCommandValidator>();

// Pipeline behavior for automatic validation
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
    {
        _validators = validators;
    }

    public async Task<TResponse> Handle(TRequest request, CancellationToken ct, RequestHandlerDelegate<TResponse> next)
    {
        var context = new ValidationContext<TRequest>(request);
        var failures = _validators
            .Select(v => v.Validate(context))
            .SelectMany(r => r.Errors)
            .Where(f => f != null)
            .ToList();

        if (failures.Any())
            throw new ValidationException(failures);

        return await next();
    }
}
```

### Search Commands (FluentValidation)

```bash
# Find validators
grep -rn "AbstractValidator\|IValidator" --include="*.cs"

# Check for string length validation
grep -rn "MaximumLength\|MinimumLength" --include="*.cs"

# Check for pattern validation
grep -rn "Matches\|Must(" --include="*.cs"

# Commands without validators (potential gap)
grep -rn "class.*Command\|class.*Request" --include="*.cs" | grep -v "Validator"
```

### Anti-Forgery (CSRF)

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| AntiForgery enabled | `grep -rn "ValidateAntiForgeryToken\|AntiForgery" --include="*.cs"` | High |
| Global filter for MVC | `grep -rn "AutoValidateAntiforgeryToken" --include="*.cs"` | High |
| Blazor uses built-in protection | Automatic in Blazor | N/A |

### File Upload

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| File type validation | `grep -rn "IFormFile\|ContentType" --include="*.cs"` | High |
| File size limits | `grep -rn "RequestSizeLimit\|MaxRequestBodySize" --include="*.cs"` | Medium |
| Safe storage location | Review file save paths | High |
| Filename sanitization | `grep -rn "Path\.GetFileName\|Path\.Combine" --include="*.cs"` | High |

---

## Security Headers & HTTPS

### Required Headers

| Header | Implementation | Severity |
|--------|---------------|----------|
| HSTS | `app.UseHsts()` | High |
| HTTPS Redirection | `app.UseHttpsRedirection()` | High |
| X-Content-Type-Options | Add `nosniff` header | Medium |
| X-Frame-Options | Add `DENY` or `SAMEORIGIN` | Medium |
| Content-Security-Policy | Configure CSP | Medium |
| X-XSS-Protection | Add header (legacy browsers) | Low |

### Search Commands

```bash
# Check for security middleware
grep -rn "UseHsts\|UseHttpsRedirection" --include="*.cs"

# Check for custom headers
grep -rn "X-Content-Type-Options\|X-Frame-Options\|Content-Security-Policy" --include="*.cs"

# Check for HTTPS requirement
grep -rn "RequireHttps\|HttpsOnly" --include="*.cs"
```

---

## .NET Framework Specific

### web.config Security

| Check | Pattern | Severity |
|-------|---------|----------|
| Custom errors enabled | `<customErrors mode="On">` | High |
| Debug disabled | `<compilation debug="false">` | High |
| Trace disabled | `<trace enabled="false">` | Medium |
| Request validation enabled | `requestValidationMode` | Medium |
| HTTP-only cookies | `httpOnlyCookies="true"` | High |
| Require SSL | `requireSSL="true"` | High |

### Search Commands

```bash
# Check web.config settings
grep -rn "debug=\"true\"\|trace enabled=\"true\"" --include="*.config"
grep -rn "customErrors mode=\"Off\"" --include="*.config"
grep -rn "httpOnlyCookies\|requireSSL" --include="*.config"
```

### ViewState (.NET Framework WebForms)

| Check | Pattern | Severity |
|-------|---------|----------|
| ViewState MAC enabled | `enableViewStateMac="true"` | Critical |
| ViewState encryption | `viewStateEncryptionMode` | High |

---

## API Security

### Rate Limiting

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Rate limiting configured | `grep -rn "RateLimiter\|AddRateLimiter" --include="*.cs"` | Medium |
| Per-endpoint limits | `grep -rn "EnableRateLimiting\|DisableRateLimiting" --include="*.cs"` | Medium |

### API Versioning

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Versioning implemented | `grep -rn "ApiVersion\|AddApiVersioning" --include="*.cs"` | Low |

### Output Filtering

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| DTOs used (not entities) | Review controller returns | Medium |
| [JsonIgnore] on sensitive props | `grep -rn "JsonIgnore\|IgnoreDataMember" --include="*.cs"` | Medium |
| No stack traces in responses | Check error handling | High |

---

## Dependency Injection & Scoping

### DbContext Lifetime

| Check | Issue | Severity |
|-------|-------|----------|
| DbContext is Scoped | Should not be Singleton or Transient in web apps | Critical |
| No captured DbContext | Don't store in fields of Singleton services | Critical |

### Search Commands

```bash
# Check DbContext registration
grep -rn "AddDbContext\|AddScoped.*DbContext\|AddSingleton.*DbContext" --include="*.cs"
```

---

## Telerik UI Components (Critical)

Telerik components have significant CVE history requiring careful review.

### Version Security

| Check | Issue | Severity |
|-------|-------|----------|
| Telerik version current | Check against CVE list | Critical |
| No CVE-2019-18935 | RadAsyncUpload RCE (before 2020.1.114) | Critical |
| No CVE-2017-11317 | RadAsyncUpload RCE (before 2017.2.621) | Critical |
| No CVE-2017-9248 | Crypto weakness (before 2017.2.621) | Critical |

### RadAsyncUpload Security

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Custom encryption keys | `grep -rn "ConfigurationEncryptionKey" --include="*.config"` | Critical |
| Custom hash key | `grep -rn "ConfigurationHashKey" --include="*.config"` | Critical |
| File type restrictions | Check `AllowedFileExtensions` in markup | High |
| Upload folder outside web root | Review `TargetFolder` configuration | High |

### RadEditor Security

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Content filters enabled | Check `ContentFilters` attribute | High |
| DialogHandler restricted | `grep -rn "DialogHandler" --include="*.config"` | High |
| RemoveScripts filter active | Check for script stripping | High |

### Machine Keys (.NET Framework)

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Custom machine keys | `grep -rn "machineKey" --include="*.config"` | Critical |
| Not using AutoGenerate | Check for explicit keys | Critical |
| HMACSHA256 validation | `validation="HMACSHA256"` | High |
| AES decryption | `decryption="AES"` | High |

### Search Commands

```bash
# Find Telerik usage
grep -rn "Telerik\|RadAsyncUpload\|RadEditor" --include="*.aspx" --include="*.ascx" --include="*.cs" --include="*.config"

# Check encryption keys
grep -rn "ConfigurationEncryptionKey\|ConfigurationHashKey\|DialogParametersEncryptionKey" --include="*.config"

# Check machine keys
grep -rn "machineKey\|validationKey\|decryptionKey" --include="*.config"
```

---

## jQuery/JavaScript XSS Prevention

### DOM XSS Patterns

| Check | Bad Pattern | Good Pattern | Severity |
|-------|-------------|--------------|----------|
| Text insertion | `.html(userInput)` | `.text(userInput)` | High |
| Element creation | `.append('<div>' + input)` | `$('<div>').text(input)` | High |
| URL handling | `.attr('href', userUrl)` | Validate URL protocol first | High |

### Dangerous Patterns to Flag

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| jQuery .html() with variables | `grep -rn "\.html(" --include="*.js"` | High |
| eval usage | `grep -rn "eval(" --include="*.js"` | High |
| new Function | `grep -rn "new Function(" --include="*.js"` | High |
| setTimeout with string | `grep -rn "setTimeout.*\"" --include="*.js"` | Medium |
| innerHTML assignment | `grep -rn "innerHTML\s*=" --include="*.js"` | High |
| document.write | `grep -rn "document\.write" --include="*.js"` | High |

### AJAX Security

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| CSRF tokens in AJAX | Check for `__RequestVerificationToken` | High |
| JSON responses vs HTML | Prefer JSON, build DOM safely | Medium |
| Validate AJAX response data | Don't trust server HTML fragments | Medium |

### URL Parameter Handling

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| location.search usage | `grep -rn "location\.search" --include="*.js"` | Medium |
| URLSearchParams usage | `grep -rn "URLSearchParams" --include="*.js"` | Medium |
| Encoded before DOM insertion | Check for proper escaping | High |

### Search Commands

```bash
# Dangerous jQuery patterns
grep -rn "\.html(\|\.append(\|\.prepend(" --include="*.js" --include="*.ts"

# eval and friends
grep -rn "eval(\|new Function(\|setTimeout.*\"" --include="*.js"

# AJAX calls
grep -rn "\$\.ajax\|\$\.post\|\$\.get\|fetch(" --include="*.js" --include="*.ts"

# URL parameter usage
grep -rn "location\.search\|location\.hash\|URLSearchParams" --include="*.js"
```

---

## SQL Server Stored Procedures

### Dynamic SQL Security

| Check | Bad Pattern | Good Pattern | Severity |
|-------|-------------|--------------|----------|
| String concatenation | `EXEC('SELECT * FROM ' + @table)` | Use `sp_executesql` | Critical |
| Dynamic object names | `@table` without validation | Use `QUOTENAME(@table)` | High |
| User input in SQL | Direct concatenation | Parameterized queries | Critical |

### Database Account Security

| Check | Command/Pattern | Severity |
|-------|-----------------|----------|
| Not using sa account | `grep -rn "User Id=sa\|User=sa" --include="*.config" --include="*.json"` | Critical |
| Not using dbo | Check connection string users | High |
| Application-specific account | Least privilege principle | High |
| Integrated Security preferred | `grep -rn "Integrated Security=True" --include="*.config"` | Medium |

### Search Commands

```bash
# Find EXEC with concatenation (vulnerable)
grep -rn "EXEC\s*(" --include="*.sql" | grep -v "sp_executesql"

# Find safe sp_executesql usage
grep -rn "sp_executesql" --include="*.sql"

# Check for QUOTENAME usage
grep -rn "QUOTENAME" --include="*.sql"

# Check connection string accounts
grep -rn "User Id=\|User=" --include="*.config" --include="*.json" --include="*.cs"
```

---

## Blazor-Specific

### Blazor Server

| Check | Issue | Severity |
|-------|-------|----------|
| Circuit state limited | Don't store sensitive data in circuit | High |
| SignalR configured | Check hub security | Medium |
| Reconnection handling | Check for state leaks | Medium |

### Blazor WebAssembly

| Check | Issue | Severity |
|-------|-------|----------|
| No secrets in WASM | All code is client-visible | Critical |
| API authorization | Backend must validate all requests | Critical |
| Token storage | Use secure browser storage | High |

### Search Commands

```bash
# Blazor security patterns
grep -rn "AuthorizeView\|CascadingAuthenticationState" --include="*.razor"
grep -rn "localStorage\|sessionStorage" --include="*.cs" --include="*.razor"
```

---

## Logging Security

Proper logging is critical for security monitoring, but logs must not contain sensitive data.

### Serilog (.NET 9+ / Blazor)

| Check | Issue | Severity |
|-------|-------|----------|
| No PII in logs | Passwords, SSN, credit cards | Critical |
| No tokens/secrets | API keys, JWT tokens, connection strings | Critical |
| Structured logging used | Use templates, not string interpolation | Medium |
| Destructuring controlled | Sensitive objects not fully logged | High |
| Log levels appropriate | Debug/Verbose not in production | Medium |

**Serilog Security Configuration:**

```csharp
// Program.cs - Secure Serilog setup
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    // Destructure only safe properties
    .Destructure.ByTransforming<User>(u => new { u.Id, u.Email }) // Exclude Password, etc.
    .WriteTo.Console()
    .WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();
```

**Secure Logging Patterns:**

```csharp
// GOOD: Structured logging with safe data
_logger.LogInformation("User {UserId} logged in from {IpAddress}", user.Id, ipAddress);
_logger.LogWarning("Failed login attempt for {Username}", username);
_logger.LogError(ex, "Error processing order {OrderId}", orderId);

// BAD: Logging sensitive data
_logger.LogInformation($"User login: {username}, password: {password}"); // NEVER
_logger.LogDebug("API response: {Response}", apiResponse); // May contain tokens
_logger.LogInformation("Connection string: {ConnectionString}", connString); // NEVER
```

**Sensitive Data Masking:**

```csharp
public static class LoggingExtensions
{
    public static string MaskSensitive(this string value, int visibleChars = 4)
    {
        if (string.IsNullOrEmpty(value) || value.Length <= visibleChars)
            return "****";

        return new string('*', value.Length - visibleChars) + value[^visibleChars..];
    }
}

// Usage
_logger.LogInformation("Processing card ending in {CardLast4}", cardNumber.MaskSensitive());
```

### NLog (.NET Framework 4.8)

| Check | Issue | Severity |
|-------|-------|----------|
| No PII in logs | Passwords, SSN, credit cards | Critical |
| No tokens/secrets | API keys, session IDs | Critical |
| Archive settings secure | Old logs protected/deleted | Medium |
| Exception details filtered | Stack traces don't leak secrets | High |
| Internal logging disabled | NLog internal logs in production | Low |

**NLog Security Configuration (NLog.config):**

```xml
<?xml version="1.0" encoding="utf-8" ?>
<nlog xmlns="http://www.nlog-project.org/schemas/NLog.xsd"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      autoReload="true"
      throwConfigExceptions="true"
      internalLogLevel="Off">

  <targets>
    <target xsi:type="File" name="file"
            fileName="${basedir}/logs/${shortdate}.log"
            layout="${longdate}|${level:uppercase=true}|${logger}|${message}|${exception:format=tostring}"
            archiveEvery="Day"
            archiveNumbering="Rolling"
            maxArchiveFiles="30"
            concurrentWrites="true"
            keepFileOpen="false" />

    <target xsi:type="Console" name="console"
            layout="${longdate}|${level:uppercase=true}|${message}" />
  </targets>

  <rules>
    <!-- Skip sensitive Microsoft logs -->
    <logger name="Microsoft.*" maxlevel="Info" final="true" />
    <logger name="System.Net.Http.*" maxlevel="Info" final="true" />

    <logger name="*" minlevel="Info" writeTo="file,console" />
  </rules>
</nlog>
```

**Secure NLog Patterns (.NET Framework):**

```csharp
private static readonly Logger _logger = LogManager.GetCurrentClassLogger();

// GOOD: Safe structured logging
_logger.Info("User {UserId} performed action {Action}", userId, actionName);
_logger.Warn("Failed authentication for user {Username}", username);
_logger.Error(ex, "Error in order processing for OrderId={OrderId}", orderId);

// BAD: Sensitive data
_logger.Info($"User {username} logged in with password {password}"); // NEVER
_logger.Debug("Session data: " + JsonConvert.SerializeObject(session)); // Risky
_logger.Info("API Key: " + apiKey); // NEVER
```

**Exclude Sensitive Properties:**

```csharp
// Custom layout renderer to mask sensitive data
[LayoutRenderer("masked")]
public class MaskedLayoutRenderer : LayoutRenderer
{
    [RequiredParameter]
    public string Value { get; set; }

    protected override void Append(StringBuilder builder, LogEventInfo logEvent)
    {
        var value = Value;
        if (!string.IsNullOrEmpty(value) && value.Length > 4)
        {
            builder.Append(new string('*', value.Length - 4));
            builder.Append(value.Substring(value.Length - 4));
        }
        else
        {
            builder.Append("****");
        }
    }
}
```

### Sensitive Data Patterns to Detect

```bash
# Serilog - Check for potential PII logging
grep -rn "Log.*password\|Log.*Password\|Log.*ssn\|Log.*creditcard" -i --include="*.cs"
grep -rn "LogInformation.*\$\"\|LogDebug.*\$\"" --include="*.cs"

# NLog - Check for potential PII logging
grep -rn "_logger.*password\|_logger.*Password\|\.Info.*password" -i --include="*.cs"
grep -rn "Logger\..*\$\"\|_logger\..*\$\"" --include="*.cs"

# Both - Token/secret logging
grep -rn "Log.*apiKey\|Log.*token\|Log.*secret\|Log.*connectionString" -i --include="*.cs"

# Check for full object logging (risky)
grep -rn "Log.*JsonConvert\|Log.*Serialize" --include="*.cs"
```

### Logging Security Checklist

- [ ] No passwords logged
- [ ] No API keys/tokens logged
- [ ] No PII (SSN, DOB, credit cards) logged
- [ ] No connection strings logged
- [ ] No session IDs logged
- [ ] Structured logging used (not string interpolation)
- [ ] Exception messages reviewed for sensitive data
- [ ] Log files protected with appropriate permissions
- [ ] Old logs archived/deleted per retention policy
- [ ] Debug logging disabled in production

---

## Quick Scan Script

Run these commands for a quick security overview:

```bash
echo "=== Critical Security Patterns ==="

echo "\n--- Hardcoded Secrets ---"
grep -rn "password\s*=\s*\"\|Password\s*=\s*\"" --include="*.cs" --include="*.json" --include="*.config" | grep -v "PasswordHash\|PasswordSalt"

echo "\n--- SQL Injection Risk ---"
grep -rn "FromSqlRaw\|ExecuteSqlRaw\|SqlCommand\|OleDbCommand" --include="*.cs"

echo "\n--- Insecure Deserialization ---"
grep -rn "BinaryFormatter\|TypeNameHandling" --include="*.cs"

echo "\n--- Debug Mode ---"
grep -rn "debug=\"true\"\|\"Debug\"\s*:\s*true" --include="*.config" --include="*.json"

echo "\n--- Missing Authorization ---"
grep -rn "\[AllowAnonymous\]" --include="*.cs"

echo "\n--- Raw HTML Output ---"
grep -rn "Html\.Raw\|MarkupString" --include="*.cs" --include="*.cshtml" --include="*.razor"

echo "\n--- Telerik Components ---"
grep -rn "Telerik\|RadAsyncUpload\|RadEditor" --include="*.csproj" --include="packages.config" --include="*.config"

echo "\n--- Telerik Encryption Keys ---"
grep -rn "ConfigurationEncryptionKey\|ConfigurationHashKey" --include="*.config"

echo "\n--- Machine Keys ---"
grep -rn "machineKey" --include="*.config"

echo "\n--- jQuery XSS Risk ---"
grep -rn "\.html(\|innerHTML\s*=" --include="*.js" --include="*.ts"

echo "\n--- Dangerous JS Patterns ---"
grep -rn "eval(\|new Function(" --include="*.js" --include="*.ts"

echo "\n--- SQL Server Dynamic SQL ---"
grep -rn "EXEC\s*(" --include="*.sql" | grep -v "sp_executesql"

echo "\n--- SA Account Usage ---"
grep -rn "User Id=sa\|User=sa\|uid=sa" --include="*.config" --include="*.json"

echo "\n--- FluentValidation Coverage ---"
grep -rn "AbstractValidator\|IValidator" --include="*.cs" | head -10

echo "\n--- Sensitive Data in Logs (Serilog) ---"
grep -rn "Log.*password\|Log.*token\|Log.*apiKey" -i --include="*.cs"

echo "\n--- Sensitive Data in Logs (NLog) ---"
grep -rn "_logger.*password\|_logger.*token\|_logger.*secret" -i --include="*.cs"

echo "\n--- String Interpolation in Logs ---"
grep -rn "LogInformation.*\$\"\|LogDebug.*\$\"\|\.Info.*\$\"" --include="*.cs"
```

---

## Severity Quick Reference

| Severity | Response Time | Examples |
|----------|---------------|----------|
| Critical | Immediate | Hardcoded secrets, SQL injection, RCE |
| High | 1 week | Auth bypass, missing encryption, XSS |
| Medium | 1 month | Missing headers, weak passwords, verbose errors |
| Low | Backlog | Best practices, hardening opportunities |
