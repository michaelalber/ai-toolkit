# XML Doc Patterns Reference

## Overview

This reference covers C# XML documentation comment patterns -- the standard tags, when to use each, how to write them well, and the anti-patterns that make XML docs useless or harmful. XML doc comments are not optional decoration. They are the primary source of API documentation for consumers of your code, surfaced in IntelliSense, generated API sites, and NuGet package documentation.

## Core Tags

### `<summary>`

**Purpose**: One to three sentence description of what the member does and why a caller would use it.

**When to use**: Every public and protected member. No exceptions.

**Pattern**:
```csharp
/// <summary>
/// Retrieves the user profile from the cache, falling back to the database
/// if the cache entry has expired. Returns null if the user does not exist.
/// </summary>
public UserProfile? GetUserProfile(int userId)
```

**Anti-pattern -- The Parrot**:
```csharp
// BAD: Restates the method name. Adds zero information.
/// <summary>
/// Gets the user profile.
/// </summary>
public UserProfile? GetUserProfile(int userId)
```

**Anti-pattern -- The Novel**:
```csharp
// BAD: Too long. Summaries are for quick scanning, not deep reading.
/// <summary>
/// This method is responsible for retrieving user profiles from the system.
/// It first checks the distributed cache layer using the user ID as the key.
/// If the cache contains a valid entry that has not expired based on the
/// configured TTL of 30 minutes, that entry is returned directly. If the
/// cache does not contain the entry or it has expired, the method falls back
/// to querying the PostgreSQL database using the UserRepository...
/// </summary>
public UserProfile? GetUserProfile(int userId)
```

**Quality checklist**:
- [ ] Does not merely restate the member name
- [ ] Answers "why would I call this?" or "what does this represent?"
- [ ] Fits in 1-3 sentences
- [ ] Uses third-person declarative voice ("Retrieves..." not "This method retrieves...")

### `<param>`

**Purpose**: Documents a single parameter -- its meaning, valid ranges, and constraints.

**When to use**: Every parameter on every public/protected method. No exceptions.

**Pattern**:
```csharp
/// <param name="userId">
/// The unique identifier of the user. Must be greater than zero.
/// </param>
/// <param name="includeInactive">
/// When true, includes users marked as inactive in the result.
/// Defaults to false if not specified.
/// </param>
public UserProfile? GetUserProfile(int userId, bool includeInactive = false)
```

**Anti-pattern -- The Label**:
```csharp
// BAD: Just restates the parameter name. "The user ID" adds nothing to "userId".
/// <param name="userId">The user ID.</param>
```

**Anti-pattern -- Name Mismatch**:
```csharp
// BAD: Param name does not match actual parameter. This happens when
// parameters are renamed but docs are not updated.
/// <param name="id">The user identifier.</param>
public UserProfile? GetUserProfile(int userId)
```

**Quality checklist**:
- [ ] Name attribute exactly matches the parameter name (case-sensitive)
- [ ] Describes meaning beyond what the name and type already convey
- [ ] Documents valid ranges and constraints (e.g., "must be positive", "cannot be empty")
- [ ] Documents null behavior if the parameter is nullable

### `<returns>`

**Purpose**: Documents the return value -- what it represents and all possible outcomes.

**When to use**: Every non-void public/protected method. Omit for void methods.

**Pattern**:
```csharp
/// <returns>
/// The user profile if found; null if no user exists with the specified ID.
/// The returned profile always has its <see cref="UserProfile.LastAccessed"/>
/// timestamp updated to the current time.
/// </returns>
public UserProfile? GetUserProfile(int userId)
```

**Anti-pattern -- The Type Restatement**:
```csharp
// BAD: Just restates the return type. The developer can see it is a UserProfile.
/// <returns>A UserProfile.</returns>
public UserProfile? GetUserProfile(int userId)
```

**Anti-pattern -- Missing Null Documentation**:
```csharp
// BAD: Does not explain when null is returned. Callers must guess.
/// <returns>The user profile.</returns>
public UserProfile? GetUserProfile(int userId)
```

**Quality checklist**:
- [ ] Describes all possible return values (including null, empty collections, defaults)
- [ ] Does not merely restate the return type
- [ ] Documents any side effects on the returned object
- [ ] Omitted entirely for void methods (do not add empty returns tags)

### `<exception>`

**Purpose**: Documents exceptions that callers should expect and handle.

**When to use**: Every exception explicitly thrown by the method, plus known exceptions from called methods that are not caught internally.

**Pattern**:
```csharp
/// <exception cref="ArgumentOutOfRangeException">
/// Thrown when <paramref name="userId"/> is less than or equal to zero.
/// </exception>
/// <exception cref="InvalidOperationException">
/// Thrown when the database connection is not available and the cache
/// does not contain the requested profile.
/// </exception>
public UserProfile? GetUserProfile(int userId)
```

**Anti-pattern -- Missing Exception Docs**:
```csharp
// BAD: Method throws but docs do not mention it. Callers are surprised at runtime.
/// <summary>Gets the user profile.</summary>
public UserProfile? GetUserProfile(int userId)
{
    if (userId <= 0) throw new ArgumentOutOfRangeException(nameof(userId));
    // ...
}
```

**Anti-pattern -- Vague Conditions**:
```csharp
// BAD: Does not explain WHEN the exception is thrown.
/// <exception cref="ArgumentException">Thrown when argument is invalid.</exception>
```

**Quality checklist**:
- [ ] Every `throw` statement in the method has a corresponding exception tag
- [ ] The `cref` references the correct exception type
- [ ] The description explains the specific condition that triggers the exception
- [ ] Uses `<paramref>` to reference the offending parameter when applicable

### `<remarks>`

**Purpose**: Extended discussion -- threading, performance, edge cases, usage guidance that does not fit in the summary.

**When to use**: When the summary alone is insufficient. Not every member needs remarks.

**Pattern**:
```csharp
/// <remarks>
/// This method is thread-safe. Multiple concurrent calls with the same
/// <paramref name="userId"/> will result in a single database query; subsequent
/// callers will wait for and share the cached result.
///
/// The cache TTL is configured via <see cref="CacheOptions.ProfileTtl"/> and
/// defaults to 30 minutes. Setting it to <see cref="TimeSpan.Zero"/> disables
/// caching entirely.
/// </remarks>
```

**Quality checklist**:
- [ ] Contains information that does not fit in the summary
- [ ] Covers threading, performance, or lifecycle concerns when relevant
- [ ] Cross-references configuration or related members
- [ ] Is not used as overflow for a too-long summary

### `<example>`

**Purpose**: Demonstrates typical usage with compilable code.

**When to use**: When the API is non-obvious or has multiple valid usage patterns.

**Pattern**:
```csharp
/// <example>
/// Retrieve a user profile with inactive user inclusion:
/// <code>
/// var service = new UserService(cache, repository);
/// var profile = service.GetUserProfile(42, includeInactive: true);
/// if (profile is not null)
/// {
///     Console.WriteLine($"Found: {profile.DisplayName}");
/// }
/// </code>
/// </example>
```

**Anti-pattern -- Pseudocode**:
```csharp
// BAD: Not real code. Will not compile. Teaches wrong syntax.
/// <example>
/// <code>
/// call GetUserProfile with user id
/// check if result is not empty
/// </code>
/// </example>
```

**Quality checklist**:
- [ ] Code is syntactically valid C#
- [ ] Uses current API signatures (not historical ones)
- [ ] Demonstrates the primary use case, not an edge case
- [ ] Includes enough context to be self-contained (variable declarations, etc.)

### `<see>` and `<seealso>`

**Purpose**: Cross-reference to related types, members, or external resources.

**When to use**: Whenever mentioning another type or member in documentation text, and for listing related APIs.

**Pattern**:
```csharp
/// <summary>
/// Retrieves the user profile. Use <see cref="UpdateUserProfile"/> to modify
/// the returned profile, or <see cref="DeleteUserProfile"/> to remove it.
/// </summary>
/// <seealso cref="UserProfile"/>
/// <seealso cref="IUserRepository"/>
```

**Quality checklist**:
- [ ] Every `cref` target exists in the codebase
- [ ] `<see>` is used inline within prose
- [ ] `<seealso>` is used as a standalone list at the end
- [ ] Does not reference internal or private members from public docs

## Tag Usage by Member Type

| Member Type | summary | param | returns | exception | remarks | example |
|-------------|---------|-------|---------|-----------|---------|---------|
| Class | Required | N/A | N/A | N/A | When complex | Rarely |
| Interface | Required | N/A | N/A | N/A | When complex | Sometimes |
| Constructor | Required | If params | N/A | If throws | If complex | Sometimes |
| Method | Required | If params | If non-void | If throws | If complex | If non-obvious |
| Property | Required | N/A | N/A | If throws | If complex | Rarely |
| Event | Required | N/A | N/A | N/A | If complex | Sometimes |
| Enum | Required | N/A | N/A | N/A | Rarely | N/A |
| Enum member | Required | N/A | N/A | N/A | Rarely | N/A |

## Type-Level Documentation Patterns

### Class Documentation
```csharp
/// <summary>
/// Manages user profile retrieval, caching, and updates for the identity subsystem.
/// </summary>
/// <remarks>
/// This class is registered as a scoped service in the DI container.
/// It requires <see cref="IDistributedCache"/> and <see cref="IUserRepository"/>
/// to be registered. Thread-safety is guaranteed for all public methods.
/// </remarks>
/// <seealso cref="UserProfile"/>
/// <seealso cref="IUserRepository"/>
public class UserService
```

### Interface Documentation
```csharp
/// <summary>
/// Defines the contract for user persistence operations. Implementations must
/// be thread-safe and handle their own connection management.
/// </summary>
/// <remarks>
/// The default implementation is <see cref="SqlUserRepository"/>.
/// For testing, use <see cref="InMemoryUserRepository"/>.
/// </remarks>
public interface IUserRepository
```

### Enum Documentation
```csharp
/// <summary>
/// Specifies the current status of a user account in the identity system.
/// </summary>
public enum UserStatus
{
    /// <summary>
    /// Account is active and the user can authenticate.
    /// </summary>
    Active,

    /// <summary>
    /// Account is suspended by an administrator. The user cannot authenticate
    /// but the account data is retained.
    /// </summary>
    Suspended,

    /// <summary>
    /// Account is pending email verification. The user cannot authenticate
    /// until verification is complete via <see cref="IUserService.VerifyEmail"/>.
    /// </summary>
    PendingVerification
}
```

## Common Anti-Patterns Summary

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Parrot Summary | "Gets the value" on GetValue() | Explain what value, why, and when to call |
| Type Restatement | "Returns a string" | Describe what the string contains and when it varies |
| Missing Nullability | No mention of null return | Document every null/empty case explicitly |
| Name Mismatch | `<param name="id">` when param is `userId` | Verify names match exactly after every rename |
| Stale Examples | Example uses removed overload | Verify examples against current signatures |
| Missing Exceptions | Method throws but docs are silent | Trace every throw path and document it |
| Novel Summaries | 10-line summary with implementation details | Move details to remarks; keep summary to 1-3 sentences |
| Orphaned Docs | Docs on a member that no longer exists | Remove during staleness detection pass |
| Empty Tags | `<returns></returns>` with no content | Either fill with meaningful content or remove |
| Internal Leaks | Public docs referencing private members | Only reference publicly visible members in public docs |
