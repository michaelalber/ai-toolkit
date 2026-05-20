# PHP Implementation Idioms

## Minimal Class Patterns

### Simple Class

```php
<?php

declare(strict_types=1);

// Test
class UserTest extends TestCase
{
    public function test_user_has_email(): void
    {
        $user = new User('alice@example.com');
        $this->assertSame('alice@example.com', $user->email());
    }
}

// Minimal
class User
{
    public function __construct(private readonly string $email) {}

    public function email(): string
    {
        return $this->email;
    }
}
```

No validation, no `__toString()`, no other methods.

### Constructor Promotion (PHP 8.0+)

```php
// Minimal with promoted properties
class User
{
    public function __construct(
        private readonly string $email,
    ) {}
}
```

### Interface Implementation

```php
// Test
public function test_repository_saves_user(): void
{
    $db = new InMemoryDatabase();
    $repo = new UserRepository($db);
    $user = new User('alice');

    $repo->save($user);

    $this->assertSame($user, $repo->findByName('alice'));
}

// Minimal
class UserRepository
{
    public function __construct(private readonly DatabaseInterface $db) {}

    public function save(User $user): void
    {
        $this->db->insert('users', $user);
    }

    public function findByName(string $name): ?User
    {
        return $this->db->find('users', ['name' => $name]);
    }
}
```

## Test Framework Patterns

### PHPUnit Minimal Test

```php
<?php

declare(strict_types=1);

use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    public function test_add_returns_sum(): void
    {
        $this->assertSame(5, Calculator::add(2, 3));
    }
}
```

### PHPUnit with `#[Test]` Attribute (PHPUnit 10+)

```php
use PHPUnit\Framework\Attributes\Test;

class CalculatorTest extends TestCase
{
    #[Test]
    public function add_returns_sum(): void
    {
        $this->assertSame(5, Calculator::add(2, 3));
    }
}
```

### Pest Minimal Test

```php
test('add returns sum', function (): void {
    expect(Calculator::add(2, 3))->toBe(5);
});
```

### Pest with `describe`

```php
describe('Calculator', function (): void {
    it('adds two numbers', function (): void {
        expect(Calculator::add(2, 3))->toBe(5);
    });
});
```

## Running Tests

```bash
# PHPUnit — run all tests
./vendor/bin/phpunit

# PHPUnit — run specific test class
./vendor/bin/phpunit tests/CalculatorTest.php

# PHPUnit — run specific test by name filter
./vendor/bin/phpunit --filter test_add_returns_sum

# PHPUnit — stop on first failure
./vendor/bin/phpunit --stop-on-failure

# Pest — run all tests
./vendor/bin/pest

# Pest — run specific test file
./vendor/bin/pest tests/CalculatorTest.php

# Pest — filter by name
./vendor/bin/pest --filter "add returns sum"
```

## Exception Handling

```php
// Test
public function test_divide_by_zero_throws(): void
{
    $this->expectException(\DivisionByZeroError::class);
    Calculator::divide(10, 0);
}

// Minimal
public static function divide(int $a, int $b): int
{
    if ($b === 0) {
        throw new \DivisionByZeroError();
    }
    return intdiv($a, $b);
}
```

### With Message Assertion

```php
// Test
public function test_invalid_email_error_message(): void
{
    $this->expectException(\InvalidArgumentException::class);
    $this->expectExceptionMessage('invalid email');
    validateEmail('not-an-email');
}

// Minimal
function validateEmail(string $email): void
{
    if (!str_contains($email, '@')) {
        throw new \InvalidArgumentException('invalid email');
    }
}
```

### Pest Exception Testing

```php
test('divide by zero throws', function (): void {
    expect(fn () => Calculator::divide(10, 0))->toThrow(\DivisionByZeroError::class);
});
```

## Mocking Patterns

### PHPUnit Mock

```php
// Test
public function test_service_saves_to_repository(): void
{
    $repo = $this->createMock(UserRepositoryInterface::class);
    $repo->expects($this->once())
         ->method('save')
         ->with($this->isInstanceOf(User::class));

    $service = new UserService($repo);
    $service->save(new User('alice@example.com'));
}

// Minimal
class UserService
{
    public function __construct(private readonly UserRepositoryInterface $repo) {}

    public function save(User $user): void
    {
        $this->repo->save($user);
    }
}
```

### Pest with Mockery

```php
use Mockery\MockInterface;

test('service saves user', function (): void {
    $repo = Mockery::mock(UserRepositoryInterface::class, function (MockInterface $mock): void {
        $mock->shouldReceive('save')->once();
    });

    $service = new UserService($repo);
    $service->save(new User('alice@example.com'));
});
```

## Common Minimal Implementations

### Getter Method

```php
public function name(): string
{
    return $this->name;
}
```

### Method Delegation

```php
public function save(User $user): void
{
    $this->repository->save($user);
}
```

### Collection Return

```php
/** @return list<User> */
public function getAll(): array
{
    return $this->users;
}
```

### Nullable Return

```php
public function find(int $id): ?User
{
    return $this->store[$id] ?? null;
}
```

### Enum (PHP 8.1+)

```php
// Test
public function test_order_status_defaults_to_pending(): void
{
    $order = new Order();
    $this->assertSame(OrderStatus::Pending, $order->status());
}

// Minimal
enum OrderStatus
{
    case Pending;
    case Shipped;
    case Delivered;
}

class Order
{
    private OrderStatus $status = OrderStatus::Pending;

    public function status(): OrderStatus
    {
        return $this->status;
    }
}
```

## What NOT to Add

Unless tested:
- `__toString()` method
- `__clone()` / `__serialize()` / `__unserialize()`
- Input validation in constructors
- Getters for every property
- Type coercion logic
- `@param` / `@return` docblocks
- `clone` guards
- Fluent setters (`withX()` builders)
