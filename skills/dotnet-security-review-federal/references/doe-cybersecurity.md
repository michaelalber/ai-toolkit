# DOE Cybersecurity Requirements

Security requirements specific to Department of Energy environments, including LANL and other DOE/NNSA facilities.

---

## Applicable Directives

| Directive | Title | Relevance |
|-----------|-------|-----------|
| DOE Order 205.1B | Department of Energy Cyber Security Program | Primary cybersecurity policy |
| DOE Order 206.1 | Department of Energy Privacy Program | PII handling |
| DOE Order 206.2 | Identity, Credential, and Access Management | ICAM requirements |
| DOE Order 471.6 | Information Security | Classification and CUI |
| NNSA NAP 70.4 | Information Security | NNSA-specific requirements |

---

## DOE Order 205.1B Key Requirements

### System Categorization

DOE systems are categorized based on potential impact:

| Impact Level | Confidentiality | Integrity | Availability |
|--------------|-----------------|-----------|--------------|
| Low | Limited adverse effect | Limited adverse effect | Limited adverse effect |
| Moderate | Serious adverse effect | Serious adverse effect | Serious adverse effect |
| High | Severe/catastrophic effect | Severe/catastrophic effect | Severe/catastrophic effect |

**Most LANL internal systems are Moderate or High impact.**

### Required Security Controls

DOE 205.1B incorporates NIST SP 800-53 controls with DOE-specific parameters:

#### Authentication Requirements

```csharp
// DOE requires stronger authentication for Moderate/High systems

// Minimum password requirements (DOE exceeds NIST minimums)
services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    options.Password.RequiredLength = 15;  // DOE: 15+ for Moderate/High
    options.Password.RequiredUniqueChars = 8;

    // Lockout: More restrictive than baseline
    options.Lockout.MaxFailedAccessAttempts = 3;  // DOE: 3 attempts
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(30);
});

// MFA required for:
// - All privileged access
// - Remote access
// - Access to High-impact systems
// - Access to CUI/UCNI
```

#### Session Management

```csharp
// DOE session timeout requirements
services.ConfigureApplicationCookie(options =>
{
    // DOE Moderate: 15 minutes inactivity
    // DOE High: 10 minutes inactivity (or less)
    options.ExpireTimeSpan = TimeSpan.FromMinutes(15);
    options.SlidingExpiration = true;

    // Concurrent session control
    options.Cookie.Name = ".DOE.Session";
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Strict;
});
```

#### Audit Requirements

DOE requires comprehensive audit logging beyond standard NIST requirements:

```csharp
// Required audit events for DOE systems
public interface IDoeAuditService
{
    // Authentication events
    void LogAuthentication(string userId, bool success, string method);
    void LogLogoff(string userId, string reason);

    // Authorization events
    void LogAuthorizationDecision(string userId, string resource, bool allowed);
    void LogPrivilegeEscalation(string userId, string newRole);

    // Data access events (required for CUI/UCNI)
    void LogDataAccess(string userId, string dataClassification, string action);
    void LogDataExport(string userId, string dataType, string destination);

    // Administrative events
    void LogConfigurationChange(string userId, string setting, string oldValue, string newValue);
    void LogUserAccountChange(string adminId, string targetUserId, string changeType);

    // Security events
    void LogSecurityIncident(string description, string severity);
    void LogMalwareDetection(string location, string signature);
}

// Audit record retention: Minimum 3 years (DOE 205.1B)
```

---

## LANL-Specific Requirements

### Network Zones

LANL operates multiple network security zones:

| Zone | Access | Systems | Additional Controls |
|------|--------|---------|---------------------|
| Yellow (Open) | Internet accessible | Public web apps | WAF, DDoS protection |
| Green (Internal) | LANL network only | Business systems | Internal firewall |
| Turquoise (Restricted) | Need-to-know | CUI systems | Enhanced monitoring |
| Red (Classified) | Cleared personnel | Classified systems | Air-gapped, TEMPEST |

**Application considerations:**

```csharp
// Network zone-aware authorization
public class NetworkZoneRequirement : IAuthorizationRequirement
{
    public string RequiredZone { get; set; }
}

public class NetworkZoneHandler : AuthorizationHandler<NetworkZoneRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        NetworkZoneRequirement requirement)
    {
        var clientNetwork = GetClientNetworkZone();

        if (IsZoneAuthorized(clientNetwork, requirement.RequiredZone))
        {
            context.Succeed(requirement);
        }
        else
        {
            _logger.LogWarning(
                "ZONE_VIOLATION User={User} RequiredZone={Required} ActualZone={Actual}",
                context.User.Identity.Name, requirement.RequiredZone, clientNetwork);
        }

        return Task.CompletedTask;
    }
}
```

### CUI/UCNI Handling

LANL handles Controlled Unclassified Information (CUI) and Unclassified Controlled Nuclear Information (UCNI):

```csharp
// Data classification markers
public enum DataClassification
{
    Public,
    Internal,              // Official Use Only (OUO)
    CUI,                   // Controlled Unclassified Information
    UCNI,                  // Unclassified Controlled Nuclear Information
    // Classified (CNSI, RD, FRD) should NOT be in unclassified systems
}

// Enforce classification-based access
[Authorize(Policy = "CUI_Access")]
public async Task<IActionResult> GetCuiDocument(int id)
{
    // Log CUI access (required)
    _auditService.LogDataAccess(
        _currentUser.Id,
        "CUI",
        $"READ Document/{id}");

    return View(document);
}

// CUI access policy
services.AddAuthorization(options =>
{
    options.AddPolicy("CUI_Access", policy =>
        policy.RequireClaim("CUI_Authorized", "true")
              .RequireClaim("Training_CUI_Current", "true"));
});
```

### Privileged Access Management

DOE/LANL requires strict privileged access controls:

```csharp
// Privileged operations require additional authentication
[Authorize(Policy = "PrivilegedAccess")]
public class AdminController : Controller
{
    // Re-authentication for sensitive operations
    [RequireReauthentication]
    public async Task<IActionResult> ModifySecuritySettings() { }
}

// Privileged access policy
services.AddAuthorization(options =>
{
    options.AddPolicy("PrivilegedAccess", policy =>
    {
        policy.RequireRole("Administrator", "SecurityAdmin");
        policy.RequireClaim("amr", "mfa");  // MFA required
        policy.RequireClaim("Training_Privileged_Current", "true");
        policy.AddRequirements(new NetworkZoneRequirement { RequiredZone = "Green" });
    });
});
```

### Separation of Duties

```csharp
// DOE requires separation of duties for critical functions
public class SeparationOfDutiesService
{
    public async Task<bool> CanApprove(string userId, string requestType, string requesterId)
    {
        // Users cannot approve their own requests
        if (userId == requesterId)
        {
            _logger.LogWarning("SOD_VIOLATION User {User} attempted self-approval", userId);
            return false;
        }

        // Check for conflicting roles
        var userRoles = await _userManager.GetRolesAsync(user);
        if (HasConflictingRoles(userRoles, requestType))
        {
            _logger.LogWarning("SOD_VIOLATION User {User} has conflicting roles for {RequestType}",
                userId, requestType);
            return false;
        }

        return true;
    }
}
```

---

## Security Assessment Requirements

### Continuous Monitoring

DOE requires continuous monitoring per NIST SP 800-137:

```csharp
// Security metrics collection
public class SecurityMetricsService
{
    public async Task CollectDailyMetrics()
    {
        var metrics = new SecurityMetrics
        {
            Date = DateTime.UtcNow.Date,
            FailedLoginAttempts = await CountFailedLogins(24),
            LockedAccounts = await CountLockedAccounts(),
            PrivilegedAccessEvents = await CountPrivilegedAccess(24),
            CuiAccessEvents = await CountCuiAccess(24),
            ConfigurationChanges = await CountConfigChanges(24),
            VulnerabilitiesOpen = await CountOpenVulnerabilities(),
            PatchCompliancePercent = await CalculatePatchCompliance()
        };

        await _repository.SaveMetricsAsync(metrics);

        // Alert on anomalies
        if (metrics.FailedLoginAttempts > Threshold)
        {
            await _alertService.SendSecurityAlert("High failed login attempts");
        }
    }
}
```

### Incident Response

```csharp
// DOE incident reporting requirements
public class IncidentService
{
    public async Task ReportIncident(SecurityIncident incident)
    {
        // Categorize per DOE incident categories
        incident.Category = CategorizeIncident(incident);

        // Determine reporting timeline
        var reportingDeadline = GetReportingDeadline(incident.Category);

        // CAT 1 (Root compromise, APT): 1 hour
        // CAT 2 (Denial of service, unauthorized access): 2 hours
        // CAT 3 (Malicious code, improper usage): 1 day
        // CAT 4 (Investigation): 1 week

        _logger.LogCritical(
            "SECURITY_INCIDENT Category={Category} Deadline={Deadline} Description={Desc}",
            incident.Category, reportingDeadline, incident.Description);

        // Notify SOC
        await _socNotification.NotifyAsync(incident);
    }
}
```

---

## Development and Deployment Requirements

### Secure Development

DOE requires secure SDLC practices:

| Phase | Requirement | .NET Implementation |
|-------|------------|---------------------|
| Design | Threat modeling | STRIDE analysis |
| Development | Secure coding | OWASP guidelines |
| Testing | Security testing | SAST/DAST scans |
| Deployment | Hardened configs | CIS benchmarks |
| Operations | Vulnerability management | Patch within 30 days (critical) |

### Configuration Management

```csharp
// Approved configurations only (no developer overrides in production)
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Load from approved configuration sources only
        if (_env.IsProduction())
        {
            // No appsettings.Development.json
            // No environment variable overrides for security settings
            // Configuration from approved CM database or vault
        }
    }
}

// Security settings must be in approved configuration management
public class SecuritySettings
{
    public int SessionTimeoutMinutes { get; init; } = 15;  // Immutable in production
    public int MaxLoginAttempts { get; init; } = 3;
    public bool RequireMfa { get; init; } = true;
}
```

### Change Management

All changes to DOE systems require:
1. Change request documentation
2. Security impact assessment
3. Approval workflow
4. Implementation verification
5. Rollback plan

---

## Search Patterns for DOE Compliance

```bash
# Authentication strength
grep -rn "RequiredLength\|MaxFailedAccessAttempts" --include="*.cs"

# Session management
grep -rn "ExpireTimeSpan\|SessionTimeout" --include="*.cs"

# MFA requirements
grep -rn "TwoFactor\|MFA\|amr" --include="*.cs"

# CUI/UCNI handling
grep -rn "CUI\|UCNI\|OUO\|Classification" --include="*.cs"

# Audit logging
grep -rn "LogInformation\|LogWarning\|LogError\|AuditLog" --include="*.cs"

# Network zone awareness
grep -rn "NetworkZone\|RemoteIpAddress\|ClientIp" --include="*.cs"

# Privileged access
grep -rn "Admin\|Privileged\|Elevated" --include="*.cs"

# Separation of duties
grep -rn "SelfApproval\|SeparationOfDuties\|Approve.*Own" --include="*.cs"
```

---

## Compliance Checklist

### Authentication (IA)
- [ ] Passwords 15+ characters
- [ ] Account lockout after 3 failures
- [ ] MFA for privileged access
- [ ] MFA for remote access
- [ ] Session timeout 15 min (Moderate) or 10 min (High)

### Access Control (AC)
- [ ] Role-based access control implemented
- [ ] Least privilege enforced
- [ ] Separation of duties for critical functions
- [ ] Network zone restrictions enforced

### Audit (AU)
- [ ] All authentication events logged
- [ ] All authorization decisions logged
- [ ] CUI/UCNI access logged
- [ ] Privileged operations logged
- [ ] Audit records retained 3+ years

### Data Protection (SC)
- [ ] TLS 1.2+ for all transmission
- [ ] FIPS-validated cryptography
- [ ] CUI encrypted at rest
- [ ] PII encrypted at rest

### Incident Response (IR)
- [ ] Incident detection capability
- [ ] Incident categorization process
- [ ] SOC notification integration
- [ ] Incident logging

---

## References

- DOE Order 205.1B: https://www.directives.doe.gov/directives-documents/200-series/0205.1-BOrder-b
- DOE Order 206.1: https://www.directives.doe.gov/directives-documents/200-series/0206.1-BOrder
- NIST SP 800-53 Rev 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- NIST SP 800-137: https://csrc.nist.gov/publications/detail/sp/800-137/final
- CUI Registry: https://www.archives.gov/cui
