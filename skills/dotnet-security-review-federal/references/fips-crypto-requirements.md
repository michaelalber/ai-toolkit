# FIPS 140-2/3 Cryptographic Requirements

Federal Information Processing Standard (FIPS) 140-2/3 compliant cryptography requirements for .NET applications in federal environments.

---

## Overview

Federal systems processing CUI, PII, or other sensitive data must use FIPS 140-2/3 validated cryptographic modules.

### Windows FIPS Mode

Windows can enforce FIPS-compliant algorithms via Group Policy:
- **Policy**: Computer Configuration > Windows Settings > Security Settings > Local Policies > Security Options
- **Setting**: "System cryptography: Use FIPS compliant algorithms"

### .NET FIPS Compliance

.NET can operate in FIPS-compliant mode, but developers must ensure only approved algorithms are used.

---

## Approved vs Non-Approved Algorithms

### Hash Functions

| Algorithm | FIPS Status | .NET Class | Use Case |
|-----------|-------------|------------|----------|
| SHA-256 | Approved | SHA256.Create() | General hashing |
| SHA-384 | Approved | SHA384.Create() | Higher security |
| SHA-512 | Approved | SHA512.Create() | Highest security |
| SHA-1 | **Deprecated** | SHA1.Create() | Legacy only (not for security) |
| MD5 | **NOT Approved** | MD5.Create() | Never use for security |

```csharp
// FIPS-COMPLIANT: SHA-256
using var sha256 = SHA256.Create();
var hash = sha256.ComputeHash(data);

// NON-COMPLIANT: MD5 (will throw in FIPS mode)
using var md5 = MD5.Create();  // FIPS violation
```

### Symmetric Encryption

| Algorithm | FIPS Status | Key Sizes | .NET Class |
|-----------|-------------|-----------|------------|
| AES | Approved | 128, 192, 256 | Aes.Create() |
| 3DES (TDEA) | **Deprecated** | 168 | TripleDES.Create() |
| DES | **NOT Approved** | 56 | DES.Create() |
| RC4 | **NOT Approved** | Variable | N/A |
| Blowfish | **NOT Approved** | Variable | N/A |

```csharp
// FIPS-COMPLIANT: AES-256
using var aes = Aes.Create();
aes.KeySize = 256;  // Use 256-bit key
aes.Mode = CipherMode.CBC;  // Or GCM for authenticated encryption
aes.Padding = PaddingMode.PKCS7;

// Generate secure key
using var rng = RandomNumberGenerator.Create();
var key = new byte[32];  // 256 bits
rng.GetBytes(key);
aes.Key = key;

// NON-COMPLIANT: DES
using var des = DES.Create();  // FIPS violation
```

### Asymmetric Encryption / Digital Signatures

| Algorithm | FIPS Status | Minimum Key Size | .NET Class |
|-----------|-------------|------------------|------------|
| RSA | Approved | 2048 bits | RSA.Create() |
| ECDSA | Approved | P-256, P-384, P-521 | ECDsa.Create() |
| ECDH | Approved | P-256, P-384, P-521 | ECDiffieHellman.Create() |
| DSA | Approved | 2048 bits | DSA.Create() |
| RSA < 2048 | **NOT Approved** | - | - |

```csharp
// FIPS-COMPLIANT: RSA 2048+
using var rsa = RSA.Create(2048);  // Minimum 2048 bits

// FIPS-COMPLIANT: ECDSA P-256
using var ecdsa = ECDsa.Create(ECCurve.NamedCurves.nistP256);

// NON-COMPLIANT: RSA 1024
using var rsa = RSA.Create(1024);  // Too small
```

### Key Derivation Functions

| Algorithm | FIPS Status | .NET Class |
|-----------|-------------|------------|
| PBKDF2 (HMAC-SHA256) | Approved | Rfc2898DeriveBytes |
| HKDF | Approved | HKDF.DeriveKey() (.NET 5+) |
| Argon2 | Not FIPS-validated | Third-party |
| bcrypt | Not FIPS-validated | Third-party |

```csharp
// FIPS-COMPLIANT: PBKDF2 with SHA-256
using var pbkdf2 = new Rfc2898DeriveBytes(
    password,
    salt,
    iterations: 600000,  // OWASP 2023 recommendation
    HashAlgorithmName.SHA256);
var key = pbkdf2.GetBytes(32);

// Note: While Argon2 is recommended by OWASP, it's not FIPS-validated
// For federal systems, use PBKDF2 with high iteration count
```

### Random Number Generation

| Generator | FIPS Status | .NET Class |
|-----------|-------------|------------|
| CSPRNG | Approved | RandomNumberGenerator.Create() |
| System.Random | **NOT Approved** | System.Random |

```csharp
// FIPS-COMPLIANT: Cryptographic RNG
using var rng = RandomNumberGenerator.Create();
var randomBytes = new byte[32];
rng.GetBytes(randomBytes);

// For random integers
var randomInt = RandomNumberGenerator.GetInt32(1, 100);

// NON-COMPLIANT: System.Random (predictable)
var random = new Random();  // Never use for security
```

---

## .NET Implementation Patterns

### Enforcing FIPS Mode

```csharp
// Check if FIPS mode is enforced
public static class FipsCompliance
{
    public static bool IsFipsModeEnabled()
    {
        try
        {
            // Attempting to create non-FIPS algorithm will throw
            // in FIPS mode
            return CryptoConfig.AllowOnlyFipsAlgorithms;
        }
        catch
        {
            return false;
        }
    }

    public static void ValidateFipsCompliance()
    {
        if (!IsFipsModeEnabled())
        {
            // Log warning but don't block (policy decision)
            Log.Warning("FIPS mode is not enforced on this system");
        }
    }
}
```

### FIPS-Compliant Encryption Service

```csharp
public class FipsEncryptionService : IEncryptionService
{
    private readonly ILogger<FipsEncryptionService> _logger;

    public byte[] Encrypt(byte[] data, byte[] key)
    {
        if (key.Length < 32) // 256 bits minimum
            throw new ArgumentException("Key must be at least 256 bits");

        using var aes = Aes.Create();
        aes.KeySize = 256;
        aes.Mode = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;
        aes.Key = key;

        // Generate random IV
        using var rng = RandomNumberGenerator.Create();
        var iv = new byte[16];
        rng.GetBytes(iv);
        aes.IV = iv;

        using var encryptor = aes.CreateEncryptor();
        var encrypted = encryptor.TransformFinalBlock(data, 0, data.Length);

        // Prepend IV to ciphertext
        var result = new byte[iv.Length + encrypted.Length];
        Buffer.BlockCopy(iv, 0, result, 0, iv.Length);
        Buffer.BlockCopy(encrypted, 0, result, iv.Length, encrypted.Length);

        _logger.LogDebug("Encrypted {Length} bytes using AES-256-CBC", data.Length);
        return result;
    }

    public byte[] Decrypt(byte[] encryptedData, byte[] key)
    {
        if (encryptedData.Length < 16)
            throw new ArgumentException("Invalid encrypted data");

        using var aes = Aes.Create();
        aes.KeySize = 256;
        aes.Mode = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;
        aes.Key = key;

        // Extract IV from beginning
        var iv = new byte[16];
        Buffer.BlockCopy(encryptedData, 0, iv, 0, 16);
        aes.IV = iv;

        var ciphertext = new byte[encryptedData.Length - 16];
        Buffer.BlockCopy(encryptedData, 16, ciphertext, 0, ciphertext.Length);

        using var decryptor = aes.CreateDecryptor();
        return decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
    }
}
```

### FIPS-Compliant Hashing Service

```csharp
public class FipsHashingService : IHashingService
{
    public byte[] ComputeHash(byte[] data)
    {
        using var sha256 = SHA256.Create();
        return sha256.ComputeHash(data);
    }

    public byte[] ComputeHash(Stream stream)
    {
        using var sha256 = SHA256.Create();
        return sha256.ComputeHash(stream);
    }

    public bool VerifyHash(byte[] data, byte[] expectedHash)
    {
        var actualHash = ComputeHash(data);
        return CryptographicOperations.FixedTimeEquals(actualHash, expectedHash);
    }
}
```

### FIPS-Compliant Password Hashing

```csharp
public class FipsPasswordHasher : IPasswordHasher<ApplicationUser>
{
    private const int SaltSize = 16;
    private const int HashSize = 32;
    private const int Iterations = 600000;  // OWASP 2023

    public string HashPassword(ApplicationUser user, string password)
    {
        using var rng = RandomNumberGenerator.Create();
        var salt = new byte[SaltSize];
        rng.GetBytes(salt);

        using var pbkdf2 = new Rfc2898DeriveBytes(
            password,
            salt,
            Iterations,
            HashAlgorithmName.SHA256);

        var hash = pbkdf2.GetBytes(HashSize);

        // Format: iterations.salt.hash (all base64)
        return $"{Iterations}.{Convert.ToBase64String(salt)}.{Convert.ToBase64String(hash)}";
    }

    public PasswordVerificationResult VerifyHashedPassword(
        ApplicationUser user,
        string hashedPassword,
        string providedPassword)
    {
        var parts = hashedPassword.Split('.');
        if (parts.Length != 3)
            return PasswordVerificationResult.Failed;

        var iterations = int.Parse(parts[0]);
        var salt = Convert.FromBase64String(parts[1]);
        var storedHash = Convert.FromBase64String(parts[2]);

        using var pbkdf2 = new Rfc2898DeriveBytes(
            providedPassword,
            salt,
            iterations,
            HashAlgorithmName.SHA256);

        var computedHash = pbkdf2.GetBytes(HashSize);

        if (CryptographicOperations.FixedTimeEquals(storedHash, computedHash))
        {
            // Rehash if iterations have increased
            if (iterations < Iterations)
                return PasswordVerificationResult.SuccessRehashNeeded;

            return PasswordVerificationResult.Success;
        }

        return PasswordVerificationResult.Failed;
    }
}
```

### FIPS-Compliant Digital Signatures

```csharp
public class FipsSigningService : ISigningService
{
    public byte[] Sign(byte[] data, RSA privateKey)
    {
        return privateKey.SignData(
            data,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1);
    }

    public bool Verify(byte[] data, byte[] signature, RSA publicKey)
    {
        return publicKey.VerifyData(
            data,
            signature,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1);
    }

    // ECDSA (preferred for new implementations)
    public byte[] SignEcdsa(byte[] data, ECDsa privateKey)
    {
        return privateKey.SignData(data, HashAlgorithmName.SHA256);
    }

    public bool VerifyEcdsa(byte[] data, byte[] signature, ECDsa publicKey)
    {
        return publicKey.VerifyData(data, signature, HashAlgorithmName.SHA256);
    }
}
```

---

## TLS Configuration

### Approved TLS Versions

| Version | FIPS Status | Recommendation |
|---------|-------------|----------------|
| TLS 1.3 | Approved | Preferred |
| TLS 1.2 | Approved | Minimum acceptable |
| TLS 1.1 | **Deprecated** | Disable |
| TLS 1.0 | **Deprecated** | Disable |
| SSL 3.0 | **NOT Approved** | Disable |

### .NET TLS Configuration

```csharp
// Kestrel configuration
webBuilder.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(https =>
    {
        https.SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13;
    });
});

// HttpClient configuration
var handler = new HttpClientHandler
{
    SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13
};
var client = new HttpClient(handler);
```

### web.config (IIS/.NET Framework)

```xml
<system.web>
  <httpRuntime targetFramework="4.8" />
</system.web>
<system.webServer>
  <security>
    <access sslFlags="Ssl, SslNegotiateCert, SslRequireCert" />
  </security>
</system.webServer>
```

### Registry Settings (Windows Server)

```powershell
# Disable TLS 1.0
New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server' -Force
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server' -Name 'Enabled' -Value 0

# Disable TLS 1.1
New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server' -Force
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server' -Name 'Enabled' -Value 0
```

---

## Search Patterns for Non-Compliance

```bash
# Non-compliant hash algorithms
grep -rn "MD5\|\.MD5\|MD5\.Create" --include="*.cs"
grep -rn "SHA1\|\.SHA1\|SHA1\.Create" --include="*.cs"

# Non-compliant symmetric algorithms
grep -rn "DES\|TripleDES\|3DES\|DESCryptoServiceProvider" --include="*.cs"
grep -rn "RC2\|RC4\|Rijndael" --include="*.cs"

# Weak RSA key sizes
grep -rn "RSA\.Create\s*(1024)\|RSA\.Create\s*(512)" --include="*.cs"

# Non-cryptographic random
grep -rn "new Random\(\)\|System\.Random" --include="*.cs"

# Weak TLS
grep -rn "Tls11\|Tls10\|Ssl3" --include="*.cs"

# Hardcoded keys (never compliant)
grep -rn "private.*key.*=.*\"\|secret.*=.*\"" --include="*.cs"
```

---

## Common Findings

### Critical

| Finding | Issue | Remediation |
|---------|-------|-------------|
| MD5 for password hashing | Non-FIPS, easily cracked | Use PBKDF2-SHA256 |
| DES/3DES encryption | Deprecated, weak | Use AES-256 |
| RSA < 2048 | Key too small | Use RSA-2048+ or ECDSA |
| System.Random for tokens | Predictable | Use RandomNumberGenerator |
| Hardcoded encryption keys | Key exposure | Use Key Vault or HSM |

### High

| Finding | Issue | Remediation |
|---------|-------|-------------|
| SHA-1 for integrity | Deprecated | Use SHA-256+ |
| TLS 1.0/1.1 enabled | Deprecated protocols | Require TLS 1.2+ |
| Low PBKDF2 iterations | Brute-force vulnerable | Use 600,000+ iterations |

### Medium

| Finding | Issue | Remediation |
|---------|-------|-------------|
| Missing FIPS mode check | Compliance verification | Add runtime check |
| AES-128 (vs 256) | Lower security margin | Prefer AES-256 |

---

## FIPS Compliance Checklist

- [ ] All hashing uses SHA-256 or stronger
- [ ] No MD5 or SHA-1 for security purposes
- [ ] Symmetric encryption uses AES (128/192/256)
- [ ] No DES, 3DES, RC2, RC4
- [ ] RSA keys are 2048 bits or larger
- [ ] ECDSA uses NIST curves (P-256, P-384, P-521)
- [ ] Random numbers from RandomNumberGenerator
- [ ] No System.Random for security
- [ ] Password hashing uses PBKDF2-SHA256 with 600K+ iterations
- [ ] TLS 1.2 or 1.3 only
- [ ] No TLS 1.0, 1.1, or SSL
- [ ] Keys stored in Key Vault or HSM (not code)

---

## References

- FIPS 140-3: https://csrc.nist.gov/publications/detail/fips/140/3/final
- NIST SP 800-131A Rev 2: https://csrc.nist.gov/publications/detail/sp/800-131a/rev-2/final
- CMVP Validated Modules: https://csrc.nist.gov/projects/cryptographic-module-validation-program/validated-modules
- .NET Cryptography Model: https://docs.microsoft.com/en-us/dotnet/standard/security/cryptography-model
