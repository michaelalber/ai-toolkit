# NIST SP 800-53 Rev 5 Control Mapping

Mapping NIST SP 800-53 security controls to OWASP Top 10 and .NET implementation patterns.

---

## Control Family Overview

| Family | ID | Focus Area | Relevance to .NET Apps |
|--------|----|-----------|-----------------------|
| Access Control | AC | Who can access what | Authorization, RBAC, claims |
| Audit and Accountability | AU | Logging and monitoring | Serilog, NLog, audit trails |
| Identification and Authentication | IA | Identity verification | ASP.NET Identity, JWT, MFA |
| System and Communications Protection | SC | Data protection | TLS, encryption, FIPS crypto |
| System and Information Integrity | SI | Input validation, malware | Validation, sanitization |
| Configuration Management | CM | Secure configuration | appsettings, web.config |
| Risk Assessment | RA | Vulnerability management | Package scanning, SAST |
| Security Assessment | SA | Security design | Secure SDLC practices |

---

## Access Control (AC) Family

### AC-2: Account Management

**Requirement**: Manage system accounts including establishing, activating, modifying, reviewing, disabling, and removing accounts.

**OWASP Mapping**: A07 (Identification and Authentication Failures)

**.NET Implementation Patterns**:

```csharp
// Account creation with proper defaults
public async Task<IdentityResult> CreateUserAsync(CreateUserCommand command)
{
    var user = new ApplicationUser
    {
        UserName = command.Email,
        Email = command.Email,
        EmailConfirmed = false, // Require confirmation
        LockoutEnabled = true,  // Enable lockout
        Created = DateTime.UtcNow,
        CreatedBy = _currentUser.Id
    };

    var result = await _userManager.CreateAsync(user, command.Password);

    // AU-12: Log account creation
    _logger.LogInformation(
        "Account created: {UserId} by {CreatedBy} at {Timestamp}",
        user.Id, _currentUser.Id, DateTime.UtcNow);

    return result;
}

// Account review - periodic access review
public async Task<IEnumerable<UserReviewDto>> GetAccountsForReviewAsync()
{
    var cutoffDate = DateTime.UtcNow.AddDays(-90);
    return await _context.Users
        .Where(u => u.LastReviewDate < cutoffDate || u.LastReviewDate == null)
        .Where(u => u.IsActive)
        .Select(u => new UserReviewDto { ... })
        .ToListAsync();
}
```

**Search Patterns**:
```bash
grep -rn "CreateAsync\|CreateUser\|AddUser" --include="*.cs"
grep -rn "DisableUser\|DeleteUser\|RemoveUser\|DeactivateUser" --include="*.cs"
grep -rn "LastLogin\|LastActivity\|LastReview" --include="*.cs"
```

**Findings Language**:
> "Account management controls (AC-2) are [partially implemented/not implemented]. [Specific gap: e.g., 'No automated account review process exists for identifying dormant accounts.']"

---

### AC-3: Access Enforcement

**Requirement**: Enforce approved authorizations for logical access to information and system resources.

**OWASP Mapping**: A01 (Broken Access Control)

**.NET Implementation Patterns**:

```csharp
// Policy-based authorization (preferred)
[Authorize(Policy = "RequireManagerRole")]
public async Task<IActionResult> ApproveRequest(int requestId) { }

// Claims-based authorization
[Authorize(Policy = "CanEditDocuments")]
public async Task<IActionResult> EditDocument(int documentId)
{
    // Additional resource-level check (IDOR prevention)
    var document = await _context.Documents.FindAsync(documentId);
    if (!await _authService.CanUserAccessDocument(_currentUser.Id, document))
        return Forbid();

    return View(document);
}

// Policy definition
services.AddAuthorization(options =>
{
    options.AddPolicy("RequireManagerRole", policy =>
        policy.RequireRole("Manager", "Admin"));

    options.AddPolicy("CanEditDocuments", policy =>
        policy.RequireClaim("Permission", "Document.Edit"));
});
```

**Search Patterns**:
```bash
grep -rn "\[Authorize\]" --include="*.cs"
grep -rn "\[AllowAnonymous\]" --include="*.cs"
grep -rn "AddPolicy\|RequireRole\|RequireClaim" --include="*.cs"
grep -rn "Forbid\(\)\|Unauthorized\(\)" --include="*.cs"
```

**Findings Language**:
> "Access enforcement controls (AC-3) show gaps in [area]. Specifically, [X endpoints lack authorization attributes / resource-level authorization is missing, allowing potential IDOR attacks]."

---

### AC-6: Least Privilege

**Requirement**: Employ least privilege, allowing only authorized accesses necessary to accomplish assigned tasks.

**OWASP Mapping**: A01 (Broken Access Control)

**.NET Implementation Patterns**:

```csharp
// Fine-grained permissions instead of broad roles
public class Permissions
{
    public const string DocumentsRead = "Documents.Read";
    public const string DocumentsWrite = "Documents.Write";
    public const string DocumentsDelete = "Documents.Delete";
    public const string UsersManage = "Users.Manage";
}

// Grant minimum necessary
[Authorize(Policy = "Documents.Read")] // Not "Admin"
public async Task<IActionResult> ViewDocument(int id) { }

// Database: Application-specific account, not sa/dbo
// Connection string should use least-privilege SQL account
```

**Search Patterns**:
```bash
grep -rn "Admin\|SuperUser\|FullAccess" --include="*.cs"
grep -rn "User Id=sa\|dbo" --include="*.config" --include="*.json"
grep -rn "RequireRole.*Admin" --include="*.cs"
```

**Findings Language**:
> "Least privilege (AC-6) violations identified: [e.g., 'Application uses SQL Server sa account instead of application-specific account with limited permissions.']"

---

### AC-7: Unsuccessful Logon Attempts

**Requirement**: Enforce a limit of consecutive invalid logon attempts within a time period and automatically lock account.

**OWASP Mapping**: A07 (Identification and Authentication Failures)

**.NET Implementation Patterns**:

```csharp
// ASP.NET Core Identity configuration
services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    // AC-7: Account lockout
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.AllowedForNewUsers = true;
})
```

**Federal Requirements** (Moderate/High baseline):
- Maximum 3 consecutive failed attempts
- Lockout duration: 15+ minutes or until admin unlock
- Log all failed attempts (AU-2)

**Search Patterns**:
```bash
grep -rn "MaxFailedAccessAttempts\|Lockout" --include="*.cs"
grep -rn "LockoutEnd\|IsLockedOut\|AccessFailedCount" --include="*.cs"
```

---

### AC-11: Session Lock

**Requirement**: Prevent further access by initiating a session lock after a defined period of inactivity.

**OWASP Mapping**: A07 (Identification and Authentication Failures)

**.NET Implementation Patterns**:

```csharp
// Session/cookie timeout (federal: typically 15-30 min for Moderate)
services.ConfigureApplicationCookie(options =>
{
    options.ExpireTimeSpan = TimeSpan.FromMinutes(15);
    options.SlidingExpiration = true;
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});

// JWT token expiration
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateLifetime = true,
    ClockSkew = TimeSpan.Zero, // No tolerance
};
```

**Federal Requirements**:
- Low: 30 minutes
- Moderate: 15 minutes
- High: 15 minutes (or less)

**Search Patterns**:
```bash
grep -rn "ExpireTimeSpan\|SessionTimeout\|IdleTimeout" --include="*.cs"
grep -rn "SlidingExpiration" --include="*.cs"
```

---

### AC-17: Remote Access

**Requirement**: Establish and document usage restrictions for remote access and implement appropriate security controls.

**OWASP Mapping**: Multiple

**.NET Implementation Patterns**:

```csharp
// Require MFA for remote/VPN access
[Authorize(Policy = "RequireMFA")]
public class RemoteAccessController : Controller { }

// Conditional access based on network location
public class NetworkLocationRequirement : IAuthorizationRequirement { }

public class NetworkLocationHandler : AuthorizationHandler<NetworkLocationRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        NetworkLocationRequirement requirement)
    {
        var httpContext = _httpContextAccessor.HttpContext;
        var clientIp = httpContext.Connection.RemoteIpAddress;

        if (IsInternalNetwork(clientIp) || HasValidMFA(context.User))
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}
```

**Search Patterns**:
```bash
grep -rn "TwoFactor\|MFA\|Authenticator" --include="*.cs"
grep -rn "RemoteIpAddress\|X-Forwarded-For" --include="*.cs"
grep -rn "VPN\|ConditionalAccess" --include="*.cs"
```

---

## Audit and Accountability (AU) Family

### AU-2: Audit Events

**Requirement**: Identify events that need to be audited and specify frequency of audits.

**OWASP Mapping**: A09 (Security Logging and Monitoring Failures)

**Required Events for Federal Systems**:
| Event Type | Priority | Example |
|------------|----------|---------|
| Authentication (success/fail) | Required | Login attempts |
| Authorization decisions | Required | Access denied events |
| Account management | Required | Create, modify, delete users |
| Data access (CUI/PII) | Required | Read/write sensitive data |
| Configuration changes | Required | Settings modifications |
| System events | Required | Start, stop, errors |

**.NET Implementation**:

```csharp
// Structured audit logging with Serilog
public class AuditService : IAuditService
{
    private readonly ILogger<AuditService> _logger;

    public void LogAuthenticationEvent(string userId, bool success, string reason = null)
    {
        _logger.LogInformation(
            "AUTH_EVENT UserId={UserId} Success={Success} Reason={Reason} Timestamp={Timestamp} IP={IP}",
            userId, success, reason, DateTime.UtcNow, GetClientIp());
    }

    public void LogAuthorizationEvent(string userId, string resource, string action, bool allowed)
    {
        _logger.LogInformation(
            "AUTHZ_EVENT UserId={UserId} Resource={Resource} Action={Action} Allowed={Allowed} Timestamp={Timestamp}",
            userId, resource, action, allowed, DateTime.UtcNow);
    }

    public void LogDataAccessEvent(string userId, string dataType, string recordId, string action)
    {
        _logger.LogInformation(
            "DATA_ACCESS UserId={UserId} DataType={DataType} RecordId={RecordId} Action={Action} Timestamp={Timestamp}",
            userId, dataType, recordId, action, DateTime.UtcNow);
    }
}
```

**Search Patterns**:
```bash
grep -rn "ILogger\|Log\.\|_logger\." --include="*.cs" | head -50
grep -rn "SignInAsync\|SignOutAsync\|PasswordSignIn" --include="*.cs"
grep -rn "catch.*Exception" --include="*.cs" | grep -v "Log" | head -20
```

---

### AU-3: Content of Audit Records

**Requirement**: Audit records contain sufficient information to establish what, when, where, source, outcome, and identity.

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| What | Type of event | AUTH_SUCCESS |
| When | Timestamp (UTC) | 2024-01-15T14:30:00Z |
| Where | System/component | WebApp.AuthController |
| Source | IP address, session | 192.168.1.100, Session123 |
| Outcome | Success/failure | Success |
| Identity | User ID | user@example.com |

**.NET Implementation**:

```csharp
// Serilog enrichment for complete audit records
Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .Enrich.WithProperty("Application", "MyApp")
    .Enrich.WithClientIp()       // Custom enricher
    .Enrich.WithCorrelationId()  // Request correlation
    .CreateLogger();

// Audit record example
_logger.LogInformation(
    "AUDIT {EventType} {UserId} {Action} {Resource} {Outcome} {Details}",
    "DATA_MODIFY",
    currentUser.Id,
    "UPDATE",
    $"Document/{documentId}",
    "SUCCESS",
    new { PreviousState = previous, NewState = current });
```

---

### AU-9: Protection of Audit Information

**Requirement**: Protect audit information and audit logging tools from unauthorized access, modification, and deletion.

**.NET Implementation Considerations**:

```csharp
// Log to protected location (not web-accessible)
.WriteTo.File(
    path: @"D:\SecureLogs\app-.log",  // Outside web root
    rollingInterval: RollingInterval.Day,
    retainedFileCountLimit: 90)       // 90 days retention

// Write-only log account (SQL Server)
// CREATE USER LogWriter WITHOUT LOGIN;
// GRANT INSERT ON dbo.AuditLog TO LogWriter;
// (No SELECT, UPDATE, DELETE)

// Centralized logging (preferred for federal)
.WriteTo.Seq("https://seq.internal.lanl.gov")
// or
.WriteTo.Elasticsearch(new ElasticsearchSinkOptions(...))
```

---

### AU-12: Audit Generation

**Requirement**: Provide audit record generation capability for auditable events.

**.NET Implementation**:

```csharp
// Automatic audit generation via middleware
public class AuditMiddleware
{
    public async Task InvokeAsync(HttpContext context, IAuditService audit)
    {
        var startTime = DateTime.UtcNow;

        await _next(context);

        audit.LogRequestEvent(new RequestAuditEvent
        {
            Timestamp = startTime,
            Duration = DateTime.UtcNow - startTime,
            UserId = context.User?.Identity?.Name,
            Method = context.Request.Method,
            Path = context.Request.Path,
            StatusCode = context.Response.StatusCode,
            ClientIp = context.Connection.RemoteIpAddress?.ToString()
        });
    }
}
```

---

## Identification and Authentication (IA) Family

### IA-2: Identification and Authentication (Organizational Users)

**Requirement**: Uniquely identify and authenticate organizational users.

**.NET Implementation**:

```csharp
services.AddAuthentication(options =>
{
    options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
})
.AddCookie()
.AddOpenIdConnect(options =>
{
    // Federal: Use organizational IdP (Azure AD, ADFS, etc.)
    options.Authority = Configuration["AzureAd:Authority"];
    options.ClientId = Configuration["AzureAd:ClientId"];
    options.ResponseType = "code";
    options.UsePkce = true;
});
```

---

### IA-2(1): Multi-Factor Authentication

**Requirement**: Implement MFA for network access to privileged accounts.

**Federal Requirements**:
- Moderate baseline: MFA for privileged access
- High baseline: MFA for all network access

**.NET Implementation**:

```csharp
// ASP.NET Core Identity MFA
services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    options.SignIn.RequireConfirmedAccount = true;
})
.AddDefaultTokenProviders()
.AddTokenProvider<AuthenticatorTokenProvider<ApplicationUser>>(
    TokenOptions.DefaultAuthenticatorProvider);

// Require MFA for privileged operations
[Authorize(Policy = "RequireMFA")]
public class AdminController : Controller { }

// MFA policy
services.AddAuthorization(options =>
{
    options.AddPolicy("RequireMFA", policy =>
        policy.RequireClaim("amr", "mfa"));  // Authentication method reference
});
```

**Search Patterns**:
```bash
grep -rn "TwoFactor\|2FA\|MFA\|Authenticator" --include="*.cs"
grep -rn "amr\|mfa\|otp" --include="*.cs"
grep -rn "AddTokenProvider\|GenerateTwoFactorToken" --include="*.cs"
```

---

### IA-5: Authenticator Management

**Requirement**: Manage system authenticators by establishing minimum password complexity.

**Federal Password Requirements (NIST SP 800-63B)**:
| Requirement | Value |
|-------------|-------|
| Minimum length | 12+ characters (8 absolute minimum) |
| Complexity | No longer required, but... |
| Check against breach lists | Required |
| No password hints | Required |
| No knowledge-based auth | Required |

**.NET Implementation**:

```csharp
services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    // IA-5: Password requirements
    options.Password.RequiredLength = 12;
    options.Password.RequireDigit = false;        // NIST no longer requires
    options.Password.RequireLowercase = false;    // NIST no longer requires
    options.Password.RequireUppercase = false;    // NIST no longer requires
    options.Password.RequireNonAlphanumeric = false;
    options.Password.RequiredUniqueChars = 4;
})
.AddPasswordValidator<BreachedPasswordValidator<ApplicationUser>>();

// Custom validator to check breached passwords
public class BreachedPasswordValidator<TUser> : IPasswordValidator<TUser>
{
    public async Task<IdentityResult> ValidateAsync(
        UserManager<TUser> manager, TUser user, string password)
    {
        if (await _hibpService.IsPasswordBreached(password))
        {
            return IdentityResult.Failed(new IdentityError
            {
                Code = "BreachedPassword",
                Description = "This password has appeared in a data breach."
            });
        }
        return IdentityResult.Success;
    }
}
```

---

## System and Communications Protection (SC) Family

### SC-8: Transmission Confidentiality and Integrity

**Requirement**: Protect transmitted information confidentiality and integrity.

**.NET Implementation**:

```csharp
// Program.cs
app.UseHttpsRedirection();
app.UseHsts();

// Enforce HTTPS
services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});

// HSTS with preload
services.AddHsts(options =>
{
    options.Preload = true;
    options.IncludeSubDomains = true;
    options.MaxAge = TimeSpan.FromDays(365);
});

// Require TLS 1.2+ (web.config for IIS)
// Or Kestrel configuration
webBuilder.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(https =>
    {
        https.SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13;
    });
});
```

**Search Patterns**:
```bash
grep -rn "UseHttps\|UseHsts\|RequireHttps" --include="*.cs"
grep -rn "SslProtocols\|TLS\|SSL" --include="*.cs" --include="*.config"
```

---

### SC-13: Cryptographic Protection

**Requirement**: Implement FIPS-validated cryptography.

**See**: `fips-crypto-requirements.md` for detailed FIPS guidance.

**.NET Quick Reference**:

| Use Case | FIPS-Compliant | Non-Compliant |
|----------|---------------|---------------|
| Hashing | SHA-256, SHA-384, SHA-512 | MD5, SHA-1 |
| Symmetric | AES-128/192/256 | DES, 3DES, RC4 |
| Asymmetric | RSA (2048+), ECDSA | RSA < 2048 |
| RNG | RNGCryptoServiceProvider | System.Random |

---

### SC-28: Protection of Information at Rest

**Requirement**: Protect confidentiality and integrity of CUI at rest.

**.NET Implementation**:

```csharp
// Data Protection API
services.AddDataProtection()
    .PersistKeysToAzureBlobStorage(...)
    .ProtectKeysWithAzureKeyVault(...);

// Entity-level encryption
public class SensitiveData
{
    public int Id { get; set; }

    [PersonalData]  // Marks for encryption consideration
    [Encrypted]     // Custom attribute for auto-encryption
    public string SSN { get; set; }
}

// SQL Server Always Encrypted or TDE
// Connection string:
// "Column Encryption Setting=Enabled"
```

---

## OWASP to NIST Control Mapping Summary

| OWASP Category | Primary NIST Controls |
|---------------|----------------------|
| A01: Broken Access Control | AC-3, AC-6, AC-17 |
| A02: Cryptographic Failures | SC-12, SC-13, SC-28 |
| A03: Injection | SI-10 |
| A04: Insecure Design | SA-8, SA-17 |
| A05: Security Misconfiguration | CM-6, CM-7 |
| A06: Vulnerable Components | SI-2, RA-5 |
| A07: Authentication Failures | IA-2, IA-5, AC-7 |
| A08: Data Integrity Failures | SI-7 |
| A09: Logging Failures | AU-2, AU-3, AU-12 |
| A10: SSRF | SC-7 |

---

## References

- NIST SP 800-53 Rev 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- NIST SP 800-63B (Digital Identity): https://pages.nist.gov/800-63-3/sp800-63b.html
- FedRAMP Control Baselines: https://www.fedramp.gov/documents/
