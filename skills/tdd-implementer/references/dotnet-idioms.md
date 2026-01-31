# .NET Implementation Idioms

## Minimal Class Patterns

### Simple POCO

```csharp
// Test
[Fact]
public void User_Has_Email()
{
    var user = new User("alice@example.com");
    Assert.Equal("alice@example.com", user.Email);
}

// Minimal
public class User
{
    public string Email { get; }
    public User(string email) => Email = email;
}
```

No validation, no other properties, no ToString(), no Equals().

### Record Type (C# 9+)

When testing value semantics:

```csharp
// Test expects equality
[Fact]
public void Users_With_Same_Email_Are_Equal()
{
    var user1 = new User("alice@example.com");
    var user2 = new User("alice@example.com");
    Assert.Equal(user1, user2);
}

// Minimal with record
public record User(string Email);
```

### Interface Implementation

```csharp
// Test
[Fact]
public void Repository_Saves_User()
{
    var mockDb = new Mock<IDatabase>();
    var repo = new UserRepository(mockDb.Object);
    var user = new User("Alice");

    repo.Save(user);

    mockDb.Verify(db => db.Insert("users", user), Times.Once);
}

// Minimal
public class UserRepository
{
    private readonly IDatabase _db;
    public UserRepository(IDatabase db) => _db = db;
    public void Save(User user) => _db.Insert("users", user);
}
```

## Test Framework Patterns

### xUnit Minimal Test

```csharp
public class CalculatorTests
{
    [Fact]
    public void Add_Returns_Sum()
    {
        Assert.Equal(5, Calculator.Add(2, 3));
    }
}
```

### NUnit Minimal Test

```csharp
[TestFixture]
public class CalculatorTests
{
    [Test]
    public void Add_Returns_Sum()
    {
        Assert.That(Calculator.Add(2, 3), Is.EqualTo(5));
    }
}
```

### MSTest Minimal Test

```csharp
[TestClass]
public class CalculatorTests
{
    [TestMethod]
    public void Add_Returns_Sum()
    {
        Assert.AreEqual(5, Calculator.Add(2, 3));
    }
}
```

## Running Tests

```bash
# Run all tests
dotnet test

# Run specific test
dotnet test --filter "FullyQualifiedName~CalculatorTests.Add_Returns_Sum"

# Run tests in specific project
dotnet test ./tests/MyProject.Tests.csproj

# Run with verbosity
dotnet test -v normal
```

## Exception Handling

```csharp
// Test
[Fact]
public void Divide_By_Zero_Throws()
{
    Assert.Throws<DivideByZeroException>(() => Calculator.Divide(10, 0));
}

// Minimal
public static int Divide(int a, int b)
{
    if (b == 0) throw new DivideByZeroException();
    return a / b;
}
```

## Async Patterns

```csharp
// Test
[Fact]
public async Task GetUser_Returns_User()
{
    var user = await _service.GetUserAsync(1);
    Assert.Equal("Alice", user.Name);
}

// Minimal (when mocking is involved)
public async Task<User> GetUserAsync(int id)
{
    return await _db.FindAsync<User>(id);
}

// Minimal (when faking)
public Task<User> GetUserAsync(int id)
{
    return Task.FromResult(new User("Alice"));
}
```

## Dependency Injection

Only add DI infrastructure when tests require it:

```csharp
// Test requires injectable dependency
[Fact]
public void Service_Uses_Repository()
{
    var mockRepo = new Mock<IUserRepository>();
    var service = new UserService(mockRepo.Object);
    // ...
}

// Minimal - just accept the dependency
public class UserService
{
    private readonly IUserRepository _repo;
    public UserService(IUserRepository repo) => _repo = repo;
}
```

Don't add:
- Service collection registration
- Interface if only one implementation
- Factory patterns
- Lifetime management

## Common Minimal Implementations

### Getter Property
```csharp
public string Name { get; }
```

### Computed Property
```csharp
public string FullName => $"{FirstName} {LastName}";
```

### Method Delegation
```csharp
public void Save(Entity entity) => _repository.Save(entity);
```

### Simple Transformation
```csharp
public int Double(int value) => value * 2;
```

### Collection Return
```csharp
public IEnumerable<User> GetAll() => _users;
```

## What NOT to Add

Unless tested:
- `IDisposable` implementation
- `IEquatable<T>` (unless equality tested)
- Null checks in constructors
- Argument validation attributes
- XML documentation
- Logging statements
- Configuration options
