# CUI Handling in .NET Applications

Guidance for handling Controlled Unclassified Information (CUI) in .NET applications per 32 CFR Part 2002 and NIST SP 800-171.

---

## What is CUI?

**Controlled Unclassified Information (CUI)** is information that requires safeguarding or dissemination controls pursuant to and consistent with applicable law, regulations, and government-wide policies but is not classified.

### Common CUI Categories in DOE/LANL

| Category | Marking | Examples |
|----------|---------|----------|
| Privacy | CUI//SP-PRVCY | PII, personnel records |
| Proprietary | CUI//SP-PROPIN | Trade secrets, business data |
| Export Controlled | CUI//SP-EXPT | ITAR/EAR controlled |
| Critical Infrastructure | CUI//SP-PCII | Infrastructure protection |
| Nuclear (UCNI) | CUI//SP-UCNI | Unclassified nuclear info |
| Patent | CUI//SP-PATENT | Invention disclosures |
| Official Use Only | CUI//SP-OUO | Internal government info |

### CUI Marking Examples

```
CUI//SP-PRVCY                    - Privacy information
CUI//SP-UCNI                     - Nuclear information
CUI//NOFORN                      - Not releasable to foreign nationals
CUI//SP-PRVCY//SP-PROPIN         - Multiple categories
```

---

## NIST SP 800-171 Requirements

NIST SP 800-171 specifies security requirements for protecting CUI in non-federal systems. Key requirements mapped to .NET:

### Access Control (3.1)

```csharp
// 3.1.1: Limit access to authorized users
[Authorize(Policy = "CUI_Authorized")]
public class CuiController : Controller
{
    // 3.1.2: Limit access to authorized functions
    [Authorize(Policy = "CUI_Read")]
    public async Task<IActionResult> ViewDocument(int id) { }

    [Authorize(Policy = "CUI_Write")]
    public async Task<IActionResult> EditDocument(int id) { }
}

// Policy definitions
services.AddAuthorization(options =>
{
    options.AddPolicy("CUI_Authorized", policy =>
    {
        policy.RequireClaim("CUI_Access", "true");
        policy.RequireClaim("Training_CUI", "current");
    });

    options.AddPolicy("CUI_Read", policy =>
    {
        policy.RequirePolicy("CUI_Authorized");
        policy.RequireClaim("CUI_Permission", "Read", "Write", "Admin");
    });

    options.AddPolicy("CUI_Write", policy =>
    {
        policy.RequirePolicy("CUI_Authorized");
        policy.RequireClaim("CUI_Permission", "Write", "Admin");
    });
});
```

### Audit and Accountability (3.3)

```csharp
// 3.3.1: Create and retain audit logs
// 3.3.2: Ensure actions are traceable to individual users

public class CuiAuditService : ICuiAuditService
{
    public async Task LogCuiAccess(CuiAccessEvent accessEvent)
    {
        var auditRecord = new CuiAuditRecord
        {
            Timestamp = DateTime.UtcNow,
            UserId = accessEvent.UserId,
            UserName = accessEvent.UserName,
            Action = accessEvent.Action,           // CREATE, READ, UPDATE, DELETE, EXPORT
            ResourceType = accessEvent.ResourceType,
            ResourceId = accessEvent.ResourceId,
            CuiCategory = accessEvent.CuiCategory, // CUI//SP-PRVCY, etc.
            Outcome = accessEvent.Outcome,         // SUCCESS, DENIED, ERROR
            ClientIp = accessEvent.ClientIp,
            SessionId = accessEvent.SessionId,
            Details = accessEvent.Details
        };

        await _auditRepository.SaveAsync(auditRecord);

        // 3.3.4: Alert on audit process failures
        _logger.LogInformation(
            "CUI_ACCESS {Action} {ResourceType}/{ResourceId} by {UserId} - {Outcome}",
            auditRecord.Action,
            auditRecord.ResourceType,
            auditRecord.ResourceId,
            auditRecord.UserId,
            auditRecord.Outcome);
    }

    // 3.3.1: Retain for minimum 3 years
    public async Task ArchiveOldRecords()
    {
        var cutoffDate = DateTime.UtcNow.AddYears(-3);
        // Archive, don't delete - may need for investigations
    }
}
```

### Identification and Authentication (3.5)

```csharp
// 3.5.1: Identify system users
// 3.5.2: Authenticate users before access

public class CuiAuthenticationService
{
    public async Task<AuthResult> AuthenticateForCui(LoginRequest request)
    {
        // 3.5.3: MFA required for CUI access
        var result = await _signInManager.PasswordSignInAsync(
            request.Username,
            request.Password,
            isPersistent: false,
            lockoutOnFailure: true);

        if (result.Succeeded)
        {
            // Verify MFA for CUI systems
            if (!await _userManager.GetTwoFactorEnabledAsync(user))
            {
                return AuthResult.RequireMfa();
            }
        }

        return result;
    }
}

// 3.5.7: Password complexity (see FIPS requirements)
services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    options.Password.RequiredLength = 15;
    options.Password.RequiredUniqueChars = 8;
});
```

### Media Protection (3.8)

```csharp
// 3.8.1: Protect CUI on system media
// 3.8.3: Sanitize media before disposal

public class CuiDocumentService
{
    private readonly IEncryptionService _encryption;

    // Encrypt CUI at rest
    public async Task<Document> SaveCuiDocument(CreateDocumentCommand command)
    {
        var document = new Document
        {
            Title = command.Title,
            CuiCategory = command.CuiCategory,
            // Encrypt content before storage
            Content = await _encryption.EncryptAsync(command.Content),
            IsEncrypted = true,
            CreatedBy = _currentUser.Id,
            CreatedAt = DateTime.UtcNow
        };

        await _context.Documents.AddAsync(document);
        await _context.SaveChangesAsync();

        // Audit CUI creation
        await _auditService.LogCuiAccess(new CuiAccessEvent
        {
            Action = "CREATE",
            ResourceType = "Document",
            ResourceId = document.Id.ToString(),
            CuiCategory = document.CuiCategory
        });

        return document;
    }

    // 3.8.9: Protect confidentiality on portable storage
    public async Task<byte[]> ExportForPortableMedia(int documentId)
    {
        var document = await _context.Documents.FindAsync(documentId);

        // Audit export
        await _auditService.LogCuiAccess(new CuiAccessEvent
        {
            Action = "EXPORT",
            ResourceType = "Document",
            ResourceId = documentId.ToString(),
            CuiCategory = document.CuiCategory,
            Details = "Exported for portable media"
        });

        // Return encrypted content for portable storage
        return await _encryption.EncryptForExportAsync(document);
    }
}
```

### Physical Protection (3.10)

While primarily physical, .NET apps can support:

```csharp
// 3.10.1: Limit physical access
// Support badge/physical access integration

public class PhysicalAccessService
{
    // Check user is in authorized facility
    public async Task<bool> VerifyPhysicalAccess(string userId, string facilityCode)
    {
        var physicalAccess = await _badgeSystem.GetCurrentAccessAsync(userId);
        return physicalAccess.AuthorizedFacilities.Contains(facilityCode);
    }
}

// Conditional access based on physical location
[Authorize(Policy = "CUI_PhysicalAccess")]
public async Task<IActionResult> AccessSensitiveCui()
{
    // Only accessible from authorized facilities
}
```

### System and Communications Protection (3.13)

```csharp
// 3.13.1: Monitor communications at boundaries
// 3.13.8: Implement cryptographic mechanisms (see FIPS requirements)

// Ensure TLS for all CUI transmission
public class Startup
{
    public void Configure(IApplicationBuilder app)
    {
        // Force HTTPS for all CUI applications
        app.UseHttpsRedirection();
        app.UseHsts();

        // Add security headers
        app.Use(async (context, next) =>
        {
            context.Response.Headers.Add("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
            context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
            context.Response.Headers.Add("X-Frame-Options", "DENY");
            context.Response.Headers.Add("Content-Security-Policy", "default-src 'self'");
            await next();
        });
    }
}

// 3.13.11: FIPS-validated cryptography
services.AddDataProtection()
    .UseCryptographicAlgorithms(new AuthenticatedEncryptorConfiguration
    {
        EncryptionAlgorithm = EncryptionAlgorithm.AES_256_CBC,
        ValidationAlgorithm = ValidationAlgorithm.HMACSHA256
    });
```

### System and Information Integrity (3.14)

```csharp
// 3.14.1: Identify and correct flaws in timely manner
// 3.14.6: Monitor for unauthorized access

public class CuiIntegrityService
{
    // Detect unauthorized modifications
    public async Task<bool> VerifyDocumentIntegrity(int documentId)
    {
        var document = await _context.Documents.FindAsync(documentId);
        var currentHash = ComputeHash(document.Content);

        if (currentHash != document.ContentHash)
        {
            _logger.LogCritical(
                "CUI_INTEGRITY_VIOLATION Document {Id} hash mismatch",
                documentId);

            await _alertService.RaiseSecurityAlert(new IntegrityViolation
            {
                ResourceType = "Document",
                ResourceId = documentId,
                ExpectedHash = document.ContentHash,
                ActualHash = currentHash
            });

            return false;
        }

        return true;
    }
}
```

---

## CUI Data Model

```csharp
public class CuiDocument
{
    public int Id { get; set; }
    public string Title { get; set; }

    // CUI Classification
    public string CuiCategory { get; set; }      // e.g., "CUI//SP-PRVCY"
    public string DisseminationControl { get; set; }  // e.g., "NOFORN"
    public string HandlingInstructions { get; set; }

    // Content (encrypted at rest)
    public byte[] EncryptedContent { get; set; }
    public string ContentHash { get; set; }       // For integrity verification

    // Lifecycle
    public DateTime CreatedAt { get; set; }
    public string CreatedBy { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public string ModifiedBy { get; set; }
    public DateTime? DestructionDate { get; set; }
    public bool IsDestroyed { get; set; }

    // Access tracking
    public DateTime LastAccessedAt { get; set; }
    public string LastAccessedBy { get; set; }
}

public class CuiAccessLog
{
    public long Id { get; set; }
    public DateTime Timestamp { get; set; }
    public string UserId { get; set; }
    public string UserDisplayName { get; set; }
    public string Action { get; set; }           // CREATE, READ, UPDATE, DELETE, EXPORT, PRINT
    public string ResourceType { get; set; }
    public string ResourceId { get; set; }
    public string CuiCategory { get; set; }
    public string Outcome { get; set; }          // SUCCESS, DENIED, ERROR
    public string ClientIp { get; set; }
    public string SessionId { get; set; }
    public string Details { get; set; }          // JSON with additional context
}
```

---

## CUI Marking in UI

```csharp
// Blazor component for CUI banner
@if (!string.IsNullOrEmpty(CuiCategory))
{
    <div class="cui-banner @GetBannerClass()">
        <strong>@CuiCategory</strong>
        @if (!string.IsNullOrEmpty(DisseminationControl))
        {
            <span>// @DisseminationControl</span>
        }
    </div>
}

@code {
    [Parameter]
    public string CuiCategory { get; set; }

    [Parameter]
    public string DisseminationControl { get; set; }

    private string GetBannerClass() => CuiCategory switch
    {
        var c when c.Contains("UCNI") => "cui-banner-ucni",
        var c when c.Contains("PRVCY") => "cui-banner-privacy",
        _ => "cui-banner-default"
    };
}

// CSS
.cui-banner {
    background-color: #006400;  // CUI Green
    color: white;
    padding: 8px;
    text-align: center;
    font-weight: bold;
}

.cui-banner-ucni {
    background-color: #8B0000;  // Dark red for nuclear
}
```

---

## Export/Download Controls

```csharp
[Authorize(Policy = "CUI_Export")]
public class CuiExportController : Controller
{
    [HttpGet("download/{id}")]
    public async Task<IActionResult> Download(int id)
    {
        var document = await _documentService.GetAsync(id);

        // Verify export authorization
        if (!await _authorizationService.CanExport(_currentUser, document))
        {
            await _auditService.LogCuiAccess(new CuiAccessEvent
            {
                Action = "EXPORT",
                ResourceId = id.ToString(),
                Outcome = "DENIED",
                Details = "Export not authorized for user"
            });

            return Forbid();
        }

        // Log successful export
        await _auditService.LogCuiAccess(new CuiAccessEvent
        {
            Action = "EXPORT",
            ResourceType = "Document",
            ResourceId = id.ToString(),
            CuiCategory = document.CuiCategory,
            Outcome = "SUCCESS"
        });

        // Add CUI marking to downloaded file
        var markedContent = await _markingService.ApplyCuiMarking(
            document.Content,
            document.CuiCategory);

        return File(markedContent, "application/pdf", $"{document.Title}_CUI.pdf");
    }
}
```

---

## Print Controls

```csharp
// JavaScript for print control with CUI marking
function printCuiDocument(cuiCategory) {
    // Add CUI header/footer to print
    var style = document.createElement('style');
    style.innerHTML = `
        @media print {
            @page {
                @top-center {
                    content: "${cuiCategory}";
                    font-weight: bold;
                    color: green;
                }
                @bottom-center {
                    content: "${cuiCategory}";
                    font-weight: bold;
                    color: green;
                }
            }
        }
    `;
    document.head.appendChild(style);

    // Log print action via API
    fetch('/api/audit/cui-print', {
        method: 'POST',
        body: JSON.stringify({ documentId: currentDocId, cuiCategory: cuiCategory })
    });

    window.print();
}
```

---

## Email Controls

```csharp
public class CuiEmailService : IEmailService
{
    public async Task SendCuiEmail(CuiEmailMessage message)
    {
        // Validate recipient authorization
        foreach (var recipient in message.Recipients)
        {
            if (!await _authService.CanReceiveCui(recipient, message.CuiCategory))
            {
                throw new UnauthorizedAccessException(
                    $"Recipient {recipient} not authorized for {message.CuiCategory}");
            }
        }

        // Add CUI marking to subject and body
        var markedSubject = $"[{message.CuiCategory}] {message.Subject}";
        var markedBody = $@"
{message.CuiCategory}
{new string('-', 50)}

{message.Body}

{new string('-', 50)}
{message.CuiCategory}
This email contains Controlled Unclassified Information.
Authorized recipients only.
";

        // Log email transmission
        await _auditService.LogCuiAccess(new CuiAccessEvent
        {
            Action = "EMAIL",
            Details = $"Sent to: {string.Join(", ", message.Recipients)}",
            CuiCategory = message.CuiCategory
        });

        await _emailClient.SendAsync(new EmailMessage
        {
            Subject = markedSubject,
            Body = markedBody,
            Recipients = message.Recipients
        });
    }
}
```

---

## Search Patterns

```bash
# CUI handling patterns
grep -rn "CUI\|Controlled.*Unclassified" --include="*.cs"
grep -rn "UCNI\|FOUO\|OUO\|NOFORN" --include="*.cs"

# Data classification
grep -rn "Classification\|CuiCategory\|SensitivityLevel" --include="*.cs"

# Export/download (potential exfiltration)
grep -rn "Download\|Export\|File(" --include="*.cs"

# Print functionality
grep -rn "Print\|window\.print" --include="*.cs" --include="*.js"

# Email with attachments
grep -rn "SmtpClient\|SendGrid\|Attachment\|MailMessage" --include="*.cs"

# Encryption (required for CUI)
grep -rn "Encrypt\|Decrypt\|AES\|DataProtection" --include="*.cs"

# Audit logging for CUI
grep -rn "CuiAudit\|LogCui\|AuditLog" --include="*.cs"
```

---

## CUI Compliance Checklist

### Access Control
- [ ] CUI access requires authentication
- [ ] CUI access requires authorization (role/claim-based)
- [ ] MFA required for CUI access
- [ ] Access based on need-to-know

### Audit
- [ ] All CUI access logged (CREATE, READ, UPDATE, DELETE)
- [ ] All CUI exports logged
- [ ] All CUI prints logged
- [ ] All CUI emails logged
- [ ] Audit logs retained 3+ years
- [ ] Audit logs protected from modification

### Data Protection
- [ ] CUI encrypted at rest (AES-256)
- [ ] CUI encrypted in transit (TLS 1.2+)
- [ ] FIPS-validated cryptography used
- [ ] Encryption keys protected (Key Vault/HSM)

### Marking
- [ ] CUI properly marked in UI
- [ ] CUI marked on exports/downloads
- [ ] CUI marked on prints
- [ ] CUI marked in emails

### Destruction
- [ ] CUI destruction tracked
- [ ] Destruction methods comply with policy
- [ ] Destruction logged

---

## References

- 32 CFR Part 2002: https://www.ecfr.gov/current/title-32/subtitle-B/chapter-XX/part-2002
- NIST SP 800-171 Rev 2: https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final
- CUI Registry: https://www.archives.gov/cui
- DOE CUI Program: https://www.energy.gov/management/office-management/operations-management/controlled-unclassified-information
