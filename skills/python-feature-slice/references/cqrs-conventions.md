# CQRS Conventions — Python Feature Slice

Reference for the `python-feature-slice` skill. Structural CQRS naming and separation conventions for Python without a mediator library.

---

## Overview

CQRS (Command Query Responsibility Segregation) in Python feature slices is a **naming and structural convention**, not a library contract. There is no Python equivalent of FreeMediator or MediatR. Instead:

- **Read operations** (queries) live in `<Name>ReadService`
- **Write operations** (commands) live in `<Name>WriteService`
- Both are injected via FastAPI's `Depends()` system

This separation provides the benefits of CQRS (independent scaling, different optimization strategies, clear intent) without the overhead of a mediator library.

---

## Naming Conventions

### Read Service Methods

Read service methods return data. They never mutate state.

| Pattern | Example | Returns |
|---------|---------|---------|
| `get_<entity>` | `get_order(order_id: int)` | Single entity or `None` |
| `list_<entities>` | `list_orders(page, page_size)` | Paginated list |
| `find_<entities>_by_<criteria>` | `find_orders_by_customer(customer_id)` | Filtered list |
| `count_<entities>` | `count_orders()` | Integer count |
| `exists_<entity>` | `exists_order(order_id)` | Boolean |
| `search_<entities>` | `search_orders(query)` | Search results |

### Write Service Methods

Write service methods mutate state. They return minimal confirmation (the created/updated entity or `None`).

| Pattern | Example | Returns |
|---------|---------|---------|
| `create_<entity>` | `create_order(request)` | Created entity |
| `update_<entity>` | `update_order(order_id, request)` | Updated entity |
| `delete_<entity>` | `delete_order(order_id)` | `None` |
| `process_<action>` | `process_payment(order_id, payment)` | Result entity |
| `cancel_<entity>` | `cancel_order(order_id)` | `None` or updated entity |
| `approve_<entity>` | `approve_order(order_id)` | Updated entity |
| `publish_<entity>` | `publish_article(article_id)` | Updated entity |

---

## When to Use Separate Read/Write Services vs. One Service

### Use separate services when:

- Read and write operations have significantly different performance profiles (reads are cached; writes are not)
- The feature has more than 5-6 methods total
- Read operations need a different database connection (read replica)
- The team wants to scale read and write handlers independently
- The feature is complex enough that a single service file would exceed ~150 lines

### Use a single service when:

- The feature is simple (2-3 operations total)
- Read and write operations share significant logic
- The team is small and the overhead of two service classes is not worth it

**Rule of thumb:** Start with a single service. Split when it grows beyond ~150 lines or when you need different optimization strategies.

---

## Single Service Pattern (Simple Features)

```python
class UserService:
    """Single service for simple features with few operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # Read methods
    async def get_user(self, user_id: int) -> UserResponse | None: ...
    async def list_users(self, page: int, page_size: int) -> UserListResponse: ...

    # Write methods
    async def create_user(self, request: CreateUserRequest) -> UserResponse: ...
    async def update_user(self, user_id: int, request: UpdateUserRequest) -> UserResponse: ...
    async def delete_user(self, user_id: int) -> None: ...
```

---

## Split Service Pattern (Complex Features)

```python
class OrderReadService:
    """Read-only operations for orders. Can use read replica."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_order(self, order_id: int) -> OrderResponse | None: ...
    async def list_orders(self, customer_id: int, page: int, page_size: int) -> OrderListResponse: ...
    async def find_orders_by_status(self, status: OrderStatus) -> list[OrderResponse]: ...
    async def count_orders_by_customer(self, customer_id: int) -> int: ...


class OrderWriteService:
    """Write operations for orders. Always uses primary database."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_order(self, request: CreateOrderRequest) -> OrderResponse: ...
    async def cancel_order(self, order_id: int) -> None: ...
    async def process_fulfillment(self, order_id: int) -> OrderResponse: ...
```

---

## Async Patterns

### All I/O must be async

```python
# CORRECT: async database operation
async def get_order(self, order_id: int) -> OrderResponse | None:
    result = await self._db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        return None
    return OrderResponse.model_validate(order)

# WRONG: blocking call in async context
async def get_order(self, order_id: int) -> OrderResponse | None:
    order = self._db.execute(...)  # Missing await — blocks event loop!
    ...
```

### CPU-bound work

```python
import asyncio

# For CPU-bound operations (e.g., image processing, heavy computation):
async def process_image(self, image_data: bytes) -> ProcessedImageResponse:
    result = await asyncio.to_thread(self._process_image_sync, image_data)
    return result

def _process_image_sync(self, image_data: bytes) -> ProcessedImageResponse:
    # Synchronous CPU-bound work here
    ...
```

### External HTTP calls

```python
import httpx

class OrderWriteService:
    def __init__(self, db: AsyncSession, http_client: httpx.AsyncClient) -> None:
        self._db = db
        self._http = http_client

    async def process_payment(self, order_id: int, payment: PaymentRequest) -> PaymentResponse:
        # Async HTTP call — does not block event loop
        response = await self._http.post("/payments", json=payment.model_dump())
        response.raise_for_status()
        return PaymentResponse.model_validate(response.json())
```

---

## Dependency Injection for Split Services

```python
# dependencies.py

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, get_read_db  # read replica if available

def get_order_read_service(
    db: Annotated[AsyncSession, Depends(get_read_db)]  # read replica
) -> OrderReadService:
    return OrderReadService(db)

def get_order_write_service(
    db: Annotated[AsyncSession, Depends(get_db)]  # primary
) -> OrderWriteService:
    return OrderWriteService(db)
```

---

## Testing CQRS Services

### Unit test pattern for read service

```python
@pytest.mark.asyncio
async def test_get_order_returns_none_when_not_found(
    read_service: OrderReadService,
    mock_db: AsyncMock,
) -> None:
    # Arrange
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Act
    result = await read_service.get_order(order_id=999)

    # Assert
    assert result is None
```

### Unit test pattern for write service

```python
@pytest.mark.asyncio
async def test_create_order_persists_to_db(
    write_service: OrderWriteService,
    mock_db: AsyncMock,
) -> None:
    # Arrange
    request = CreateOrderRequest(item_id=1, quantity=2)

    # Act
    await write_service.create_order(request)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```
