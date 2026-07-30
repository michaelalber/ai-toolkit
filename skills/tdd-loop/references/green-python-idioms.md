# Python Implementation Idioms

## Minimal Class Patterns

### Simple Class

```python
# Test
def test_user_has_email():
    user = User("alice@example.com")
    assert user.email == "alice@example.com"

# Minimal
class User:
    def __init__(self, email):
        self.email = email
```

No `__str__`, no `__repr__`, no `__eq__`, no validation.

### Dataclass

When multiple attributes are tested:

```python
# Test
def test_user_attributes():
    user = User(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"

# Minimal with dataclass
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
```

### Named Tuple

For immutable value objects:

```python
# Test expects immutability
def test_point_is_immutable():
    p = Point(3, 4)
    with pytest.raises(AttributeError):
        p.x = 5

# Minimal
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int
```

## Test Framework Patterns

### pytest Minimal Test

```python
def test_add_returns_sum():
    assert add(2, 3) == 5
```

### pytest with Fixture

```python
@pytest.fixture
def user():
    return User("alice@example.com")

def test_user_email(user):
    assert user.email == "alice@example.com"
```

### unittest Minimal Test

```python
import unittest

class TestCalculator(unittest.TestCase):
    def test_add_returns_sum(self):
        self.assertEqual(add(2, 3), 5)
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::test_add_returns_sum

# Run with verbosity
pytest -v

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf
```

## Exception Handling

```python
# Test
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

# Minimal
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError()
    return a / b
```

### With Message Verification

```python
# Test
def test_invalid_email_error_message():
    with pytest.raises(ValueError, match="invalid email"):
        validate_email("not-an-email")

# Minimal
def validate_email(email):
    if "@" not in email:
        raise ValueError("invalid email")
```

## Async Patterns

```python
# Test
@pytest.mark.asyncio
async def test_fetch_user():
    user = await service.fetch_user(1)
    assert user.name == "Alice"

# Minimal
async def fetch_user(self, user_id):
    return await self.db.find(user_id)

# Faking async
async def fetch_user(self, user_id):
    return User(name="Alice")
```

## Mocking Patterns

```python
# Test with mock
def test_service_saves_to_repository(mocker):
    mock_repo = mocker.Mock()
    service = UserService(mock_repo)
    user = User("Alice")

    service.save(user)

    mock_repo.save.assert_called_once_with(user)

# Minimal
class UserService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, user):
        self.repository.save(user)
```

## Type Hints

Add type hints only when tests or typing systems require:

```python
# Test uses typed interface
def test_add_numbers() -> None:
    result: int = add(2, 3)
    assert result == 5

# Minimal with types
def add(a: int, b: int) -> int:
    return a + b
```

## Common Minimal Implementations

### Property Access
```python
@property
def name(self):
    return self._name
```

### Delegation
```python
def save(self, entity):
    self.repository.save(entity)
```

### List Operations
```python
def get_all(self):
    return list(self._items)

def add(self, item):
    self._items.append(item)
```

### Dictionary Access
```python
def get(self, key):
    return self._data.get(key)
```

### Generator (when tested)
```python
def iter_items(self):
    yield from self._items
```

## What NOT to Add

Unless tested:
- `__str__` / `__repr__` methods
- `__eq__` / `__hash__` methods
- Property setters with validation
- Type checking at runtime
- Docstrings
- Default parameter values
- Keyword-only arguments
- *args / **kwargs
