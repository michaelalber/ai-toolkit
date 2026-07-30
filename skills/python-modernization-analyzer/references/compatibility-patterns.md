# Compatibility Patterns — Python Modernization

Reference for the `python-modernization-analyzer` skill. Common Python 2→3 and sync→async compatibility patterns with before/after examples.

---

## Python 2 → Python 3 Patterns

### Print Statement → Function

```python
# Python 2
print "Hello, world"
print "Value:", x

# Python 3
print("Hello, world")
print("Value:", x)
```

**Tool:** `2to3` handles this automatically.

---

### Unicode and String Types

```python
# Python 2
s = u"unicode string"
b = "byte string"
isinstance(s, unicode)  # Python 2 only
isinstance(b, str)

# Python 3
s = "string (always unicode)"
b = b"byte string"
isinstance(s, str)
isinstance(b, bytes)
```

**Tool:** `2to3` handles most cases. Manual review needed for `encode()`/`decode()` calls.

---

### Dictionary Methods

```python
# Python 2
d.iteritems()  # Returns iterator
d.iterkeys()
d.itervalues()
d.has_key("key")

# Python 3
d.items()   # Returns view (use list(d.items()) if you need a list)
d.keys()
d.values()
"key" in d  # has_key() removed
```

**Tool:** `2to3` handles this automatically.

---

### Integer Division

```python
# Python 2
5 / 2  # Returns 2 (integer division)
5 // 2  # Returns 2 (explicit integer division)

# Python 3
5 / 2   # Returns 2.5 (float division)
5 // 2  # Returns 2 (integer division)
```

**Risk:** Silent behavior change. `2to3` does NOT fix this automatically. Manual review required for all `/` operations on integers.

---

### Exception Syntax

```python
# Python 2
except Exception, e:
    print e

# Python 3
except Exception as e:
    print(e)
```

**Tool:** `2to3` handles this automatically.

---

### `xrange` → `range`

```python
# Python 2
for i in xrange(1000000):  # Memory-efficient iterator
    pass

# Python 3
for i in range(1000000):  # range() is now an iterator in Python 3
    pass
```

**Tool:** `2to3` handles this automatically.

---

### `map`, `filter`, `zip` Return Types

```python
# Python 2
result = map(str, [1, 2, 3])  # Returns list
result = filter(None, [0, 1, 2])  # Returns list

# Python 3
result = list(map(str, [1, 2, 3]))  # Returns map object; wrap in list() if needed
result = list(filter(None, [0, 1, 2]))  # Returns filter object
```

**Risk:** If the result is used as a list (indexed, iterated multiple times), wrapping in `list()` is required. `2to3` adds `list()` wrappers automatically.

---

### `super()` Syntax

```python
# Python 2
class Child(Parent):
    def __init__(self):
        super(Child, self).__init__()

# Python 3
class Child(Parent):
    def __init__(self):
        super().__init__()
```

**Tool:** `pyupgrade` handles this automatically.

---

## Sync → Async Patterns

### HTTP Requests

```python
# Sync (requests)
import requests

def get_user(user_id: int) -> dict:
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

# Async (httpx)
import httpx

async def get_user(user_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()
```

---

### Database Queries (SQLAlchemy)

```python
# Sync SQLAlchemy 2.0
from sqlalchemy.orm import Session

def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

# Async SQLAlchemy 2.0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

**Key difference:** `AsyncSession` requires `await` on all database operations. The session factory also changes: `async_sessionmaker` instead of `sessionmaker`.

---

### Running Async Code

```python
# Running async from sync context (entry points, scripts)
import asyncio

async def main() -> None:
    result = await some_async_function()
    print(result)

# Python 3.7+
asyncio.run(main())

# NOT: asyncio.get_event_loop().run_until_complete(main())  # Deprecated pattern
```

---

### FastAPI Dependency Injection (Async)

```python
# Sync FastAPI handler
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return UserResponse.model_validate(user)

# Async FastAPI handler
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404)
    return UserResponse.model_validate(user)
```

---

### Background Tasks

```python
# Sync (threading)
import threading

def send_email_sync(to: str, subject: str) -> None:
    # Blocking email send
    pass

thread = threading.Thread(target=send_email_sync, args=(to, subject))
thread.start()

# Async (asyncio)
import asyncio

async def send_email_async(to: str, subject: str) -> None:
    # Non-blocking email send
    pass

# In FastAPI: use BackgroundTasks
from fastapi import BackgroundTasks

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    background_tasks: BackgroundTasks,
) -> UserResponse:
    user = await user_service.create_user(request)
    background_tasks.add_task(send_email_async, user.email, "Welcome!")
    return user
```

---

## Flask → FastAPI Migration Patterns

### Route Definition

```python
# Flask
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    user = UserService.get(user_id)
    if user is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user.to_dict())

# FastAPI
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    user = await user_service.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

### Request Body

```python
# Flask
from flask import request

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")  # No validation
    email = data.get("email")  # No validation
    ...

# FastAPI
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    email: str  # Validated automatically

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(request: CreateUserRequest) -> UserResponse:
    # request.name and request.email are already validated
    ...
```

### Error Handling

```python
# Flask
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

# FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Not found"})
```
