# Minimal Implementation Patterns

## The YAGNI Principle

"You Aren't Gonna Need It" — Don't implement features until tests require them.

## Pattern Catalog

### Pattern 1: Constant Return

When a test expects a specific value:

```
Test: expects function to return "hello"
Minimal: return "hello"
```

This is valid. Let future tests force parameterization.

### Pattern 2: Identity Return

When a test expects the same value back:

```
Test: expects save(user) to return user
Minimal: return the input parameter
```

Don't add actual persistence until tested.

### Pattern 3: First Element

When a test expects an item from a collection:

```
Test: expects getFirst() to return first item
Minimal: return collection[0]
```

Don't handle empty collections until tested.

### Pattern 4: Empty Collection

When a test expects a result set:

```
Test: expects search("nonexistent") to return []
Minimal: return []
```

For the non-empty case, wait for that test.

### Pattern 5: Constructor Assignment

When a test expects an object with properties:

```
Test: expects User(name).name == name
Minimal: self.name = name in __init__
```

Only store what tests access.

### Pattern 6: Delegation

When a test expects behavior via dependency:

```
Test: expects service.process() to call dependency.handle()
Minimal: self.dependency.handle()
```

Don't add logic around the delegation unless tested.

### Pattern 7: Boolean Short-Circuit

When a test expects boolean result:

```
Test: expects isEmpty([]) to return True
Minimal: return True (if only test)
         return len(items) == 0 (if obvious)
```

### Pattern 8: Exception Throw

When a test expects an error:

```
Test: expects validate("") to raise ValueError
Minimal: raise ValueError()
```

Message and details come with tests for them.

## Decision Matrix

| Test Complexity | Single Test | Multiple Tests |
|----------------|-------------|----------------|
| Single value | Fake It (hardcode) | Triangulate to algorithm |
| Simple logic | Obvious if < 3 lines | Generalize |
| Complex logic | Fake first example | Triangulate carefully |
| External deps | Mock and fake | Build real gradually |

## Anti-Patterns to Avoid

### Over-Implementation

```
# Test
def test_add_two_numbers():
    assert add(2, 3) == 5

# Over-implementation (BAD)
def add(a, b):
    if not isinstance(a, (int, float)):
        raise TypeError("a must be numeric")
    if not isinstance(b, (int, float)):
        raise TypeError("b must be numeric")
    result = a + b
    logger.info(f"Added {a} + {b} = {result}")
    return result

# Minimal (GOOD)
def add(a, b):
    return a + b
```

### Premature Abstraction

```
# Test
def test_greet_returns_hello():
    assert greet("Alice") == "Hello, Alice!"

# Over-abstracted (BAD)
class GreetingStrategy(ABC):
    @abstractmethod
    def format(self, name): pass

class HelloGreeting(GreetingStrategy):
    def format(self, name):
        return f"Hello, {name}!"

def greet(name, strategy=None):
    strategy = strategy or HelloGreeting()
    return strategy.format(name)

# Minimal (GOOD)
def greet(name):
    return f"Hello, {name}!"
```

### Defense Against Untested Cases

```
# Test
def test_get_user_by_id():
    db = MockDB(users=[User(id=1, name="Alice")])
    assert get_user(db, 1).name == "Alice"

# Over-defensive (BAD)
def get_user(db, user_id):
    if user_id is None:
        raise ValueError("user_id required")
    if user_id < 0:
        raise ValueError("user_id must be positive")
    user = db.find_user(user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return user

# Minimal (GOOD)
def get_user(db, user_id):
    return db.find_user(user_id)
```

## When Obvious Implementation is Safe

Use obvious implementation when:
1. Algorithm is a single expression
2. No branching logic
3. No error conditions to handle
4. Pattern is well-established (getter, setter, simple math)

Examples of safe obvious implementations:
- `return a + b`
- `return self.name`
- `return len(items)`
- `return items[0]`
- `self.value = value`

## When to Fake It First

Fake it when:
1. Not sure of the general algorithm
2. Want to verify test is correct
3. Multiple approaches possible
4. Implementation will be complex
5. First test for a new behavior

The fake validates the test; triangulation validates the algorithm.
