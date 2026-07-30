# TypeScript Implementation Idioms

## Minimal Class Patterns

### Simple Class

```typescript
// Test
test('User has email', () => {
    const user = new User('alice@example.com');
    expect(user.email).toBe('alice@example.com');
});

// Minimal
class User {
    constructor(public readonly email: string) {}
}
```

No getters, no setters, no validation, no toJSON().

### Interface Implementation

```typescript
// Test
test('Service calls repository', () => {
    const mockRepo = { save: jest.fn() };
    const service = new UserService(mockRepo);
    const user = { name: 'Alice' };

    service.save(user);

    expect(mockRepo.save).toHaveBeenCalledWith(user);
});

// Minimal
interface UserRepository {
    save(user: User): void;
}

class UserService {
    constructor(private repo: UserRepository) {}

    save(user: User): void {
        this.repo.save(user);
    }
}
```

### Type-Only (No Class)

When behavior isn't tested, prefer types:

```typescript
// Test only checks data shape
test('createUser returns user object', () => {
    const user = createUser('Alice', 'alice@example.com');
    expect(user.name).toBe('Alice');
    expect(user.email).toBe('alice@example.com');
});

// Minimal - just a type and factory
type User = {
    name: string;
    email: string;
};

function createUser(name: string, email: string): User {
    return { name, email };
}
```

## Test Framework Patterns

### Jest Minimal Test

```typescript
test('add returns sum', () => {
    expect(add(2, 3)).toBe(5);
});
```

### Jest with Describe

```typescript
describe('Calculator', () => {
    describe('add', () => {
        test('returns sum of two numbers', () => {
            expect(add(2, 3)).toBe(5);
        });
    });
});
```

### Vitest Minimal Test

```typescript
import { test, expect } from 'vitest';

test('add returns sum', () => {
    expect(add(2, 3)).toBe(5);
});
```

### Mocha + Chai

```typescript
import { expect } from 'chai';

describe('Calculator', () => {
    it('adds two numbers', () => {
        expect(add(2, 3)).to.equal(5);
    });
});
```

## Running Tests

```bash
# Jest
npm test
npm test -- --testNamePattern="add returns sum"
npm test -- --watch

# Vitest
npx vitest
npx vitest run
npx vitest --reporter=verbose

# Mocha
npm test
npx mocha --grep "adds two numbers"
```

## Exception Handling

```typescript
// Test
test('divide by zero throws', () => {
    expect(() => divide(10, 0)).toThrow();
});

// Minimal
function divide(a: number, b: number): number {
    if (b === 0) throw new Error();
    return a / b;
}
```

### With Specific Error

```typescript
// Test
test('divide by zero throws DivisionError', () => {
    expect(() => divide(10, 0)).toThrow(DivisionError);
});

// Minimal
class DivisionError extends Error {}

function divide(a: number, b: number): number {
    if (b === 0) throw new DivisionError();
    return a / b;
}
```

## Async Patterns

```typescript
// Test
test('fetches user', async () => {
    const user = await service.fetchUser(1);
    expect(user.name).toBe('Alice');
});

// Minimal
async fetchUser(id: number): Promise<User> {
    return this.db.find(id);
}

// Faking
async fetchUser(id: number): Promise<User> {
    return { id, name: 'Alice', email: 'alice@example.com' };
}
```

### Promise-based

```typescript
// Test
test('resolves with user', () => {
    return service.getUser(1).then(user => {
        expect(user.name).toBe('Alice');
    });
});

// Minimal
getUser(id: number): Promise<User> {
    return Promise.resolve({ id, name: 'Alice' });
}
```

## Mocking Patterns

### Jest Mocks

```typescript
// Test
test('service saves user', () => {
    const mockSave = jest.fn();
    const service = new UserService({ save: mockSave });

    service.save({ name: 'Alice' });

    expect(mockSave).toHaveBeenCalledWith({ name: 'Alice' });
});
```

### Module Mocks

```typescript
// Test
jest.mock('./database');
import { db } from './database';

test('uses database', () => {
    (db.find as jest.Mock).mockReturnValue({ id: 1 });
    // ...
});
```

## Type Patterns

### Minimal Interface

```typescript
interface User {
    email: string;
}
```

Don't add properties until tests require them.

### Generic Minimal

```typescript
// Test
test('box contains value', () => {
    const box = new Box(42);
    expect(box.value).toBe(42);
});

// Minimal
class Box<T> {
    constructor(public readonly value: T) {}
}
```

### Union Types

```typescript
// Test
test('status is valid', () => {
    const order = createOrder('pending');
    expect(['pending', 'shipped', 'delivered']).toContain(order.status);
});

// Minimal
type OrderStatus = 'pending' | 'shipped' | 'delivered';

interface Order {
    status: OrderStatus;
}
```

## Common Minimal Implementations

### Property Access
```typescript
get name(): string {
    return this._name;
}
```

### Arrow Function
```typescript
const add = (a: number, b: number) => a + b;
```

### Array Operations
```typescript
getAll(): User[] {
    return [...this.users];
}

add(user: User): void {
    this.users.push(user);
}
```

### Object Spread
```typescript
update(user: User, changes: Partial<User>): User {
    return { ...user, ...changes };
}
```

## What NOT to Add

Unless tested:
- Private methods (prefer public API testing)
- Getters/setters with logic
- Validation decorators
- Console.log statements
- Optional parameters
- Default values
- JSDoc comments
- Overloaded signatures
