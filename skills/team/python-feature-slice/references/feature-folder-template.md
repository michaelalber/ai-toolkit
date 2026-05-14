# Feature Folder Template — Python Feature Slice

Reference for the `python-feature-slice` skill. Complete file-by-file content for scaffolding a new feature.

Replace `<name>` with the feature name (e.g., `orders`, `users`, `payments`).
Replace `<Name>` with the PascalCase feature name (e.g., `Order`, `User`, `Payment`).

---

## `features/<name>/__init__.py`

```python
# Empty — or export the public API if needed
# from features.<name>.router import router
# from features.<name>.models import <Name>Response
```

---

## `features/<name>/models.py`

```python
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


# --- Request Models ---

class Create<Name>Request(BaseModel):
    """Request body for creating a <name>."""
    model_config = ConfigDict(frozen=True)

    # Add fields here
    # name: str
    # description: str | None = None

    # Example validator
    # @field_validator("name")
    # @classmethod
    # def name_must_not_be_empty(cls, v: str) -> str:
    #     if not v.strip():
    #         raise ValueError("name must not be empty")
    #     return v.strip()


class Update<Name>Request(BaseModel):
    """Request body for updating a <name>."""
    model_config = ConfigDict(frozen=True)

    # Add fields here — all optional for partial updates


# --- Response Models ---

class <Name>Response(BaseModel):
    """Response model for a single <name>."""
    model_config = ConfigDict(frozen=True)

    id: int
    created_at: datetime
    updated_at: datetime
    # Add fields here


class <Name>ListResponse(BaseModel):
    """Response model for a list of <name>s."""
    model_config = ConfigDict(frozen=True)

    items: list[<Name>Response]
    total: int
    page: int
    page_size: int
```

---

## `features/<name>/service.py`

```python
from __future__ import annotations

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from features.<name>.models import (
    Create<Name>Request,
    Update<Name>Request,
    <Name>Response,
    <Name>ListResponse,
)


# --- Protocol (interface for testing) ---

class <Name>ReadServiceProtocol(Protocol):
    async def get_<name>(self, <name>_id: int) -> <Name>Response: ...
    async def list_<name>s(self, page: int, page_size: int) -> <Name>ListResponse: ...


class <Name>WriteServiceProtocol(Protocol):
    async def create_<name>(self, request: Create<Name>Request) -> <Name>Response: ...
    async def update_<name>(self, <name>_id: int, request: Update<Name>Request) -> <Name>Response: ...
    async def delete_<name>(self, <name>_id: int) -> None: ...


# --- Concrete Implementations ---

class <Name>ReadService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_<name>(self, <name>_id: int) -> <Name>Response:
        # TODO: implement
        raise NotImplementedError

    async def list_<name>s(self, page: int = 1, page_size: int = 20) -> <Name>ListResponse:
        # TODO: implement
        raise NotImplementedError


class <Name>WriteService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_<name>(self, request: Create<Name>Request) -> <Name>Response:
        # TODO: implement
        raise NotImplementedError

    async def update_<name>(self, <name>_id: int, request: Update<Name>Request) -> <Name>Response:
        # TODO: implement
        raise NotImplementedError

    async def delete_<name>(self, <name>_id: int) -> None:
        # TODO: implement
        raise NotImplementedError
```

---

## `features/<name>/dependencies.py`

```python
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from features.<name>.service import <Name>ReadService, <Name>WriteService


def get_<name>_read_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> <Name>ReadService:
    return <Name>ReadService(db)


def get_<name>_write_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> <Name>WriteService:
    return <Name>WriteService(db)
```

---

## `features/<name>/router.py`

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from shared.auth import get_current_user, CurrentUser
from features.<name>.dependencies import get_<name>_read_service, get_<name>_write_service
from features.<name>.models import (
    Create<Name>Request,
    Update<Name>Request,
    <Name>Response,
    <Name>ListResponse,
)
from features.<name>.service import <Name>ReadService, <Name>WriteService

router = APIRouter(prefix="/<name>s", tags=["<name>s"])


@router.get(
    "/",
    response_model=<Name>ListResponse,
    summary="List <name>s",
    description="Returns a paginated list of <name>s.",
)
async def list_<name>s(
    page: int = 1,
    page_size: int = 20,
    service: Annotated[<Name>ReadService, Depends(get_<name>_read_service)] = ...,
    _current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> <Name>ListResponse:
    return await service.list_<name>s(page=page, page_size=page_size)


@router.get(
    "/{<name>_id}",
    response_model=<Name>Response,
    summary="Get <name>",
    responses={404: {"description": "<Name> not found"}},
)
async def get_<name>(
    <name>_id: int,
    service: Annotated[<Name>ReadService, Depends(get_<name>_read_service)] = ...,
    _current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> <Name>Response:
    result = await service.get_<name>(<name>_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="<Name> not found")
    return result


@router.post(
    "/",
    response_model=<Name>Response,
    status_code=status.HTTP_201_CREATED,
    summary="Create <name>",
)
async def create_<name>(
    request: Create<Name>Request,
    service: Annotated[<Name>WriteService, Depends(get_<name>_write_service)] = ...,
    _current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> <Name>Response:
    return await service.create_<name>(request)


@router.put(
    "/{<name>_id}",
    response_model=<Name>Response,
    summary="Update <name>",
    responses={404: {"description": "<Name> not found"}},
)
async def update_<name>(
    <name>_id: int,
    request: Update<Name>Request,
    service: Annotated[<Name>WriteService, Depends(get_<name>_write_service)] = ...,
    _current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> <Name>Response:
    return await service.update_<name>(<name>_id, request)


@router.delete(
    "/{<name>_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete <name>",
    responses={404: {"description": "<Name> not found"}},
)
async def delete_<name>(
    <name>_id: int,
    service: Annotated[<Name>WriteService, Depends(get_<name>_write_service)] = ...,
    _current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> None:
    await service.delete_<name>(<name>_id)
```

---

## `tests/features/<name>/test_router.py`

```python
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from features.<name>.dependencies import get_<name>_read_service, get_<name>_write_service
from features.<name>.models import <Name>Response, <Name>ListResponse


@pytest.fixture
def mock_read_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_write_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def client(mock_read_service: AsyncMock, mock_write_service: AsyncMock) -> TestClient:
    app.dependency_overrides[get_<name>_read_service] = lambda: mock_read_service
    app.dependency_overrides[get_<name>_write_service] = lambda: mock_write_service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_<name>s_returns_200(client: TestClient, mock_read_service: AsyncMock) -> None:
    # Arrange
    mock_read_service.list_<name>s.return_value = <Name>ListResponse(
        items=[], total=0, page=1, page_size=20
    )

    # Act
    response = client.get("/<name>s/")

    # Assert
    assert response.status_code == 200
    mock_read_service.list_<name>s.assert_called_once()
```

---

## `tests/features/<name>/test_service.py`

```python
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from features.<name>.service import <Name>ReadService, <Name>WriteService
from features.<name>.models import Create<Name>Request


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def read_service(mock_db: AsyncMock) -> <Name>ReadService:
    return <Name>ReadService(db=mock_db)


@pytest.fixture
def write_service(mock_db: AsyncMock) -> <Name>WriteService:
    return <Name>WriteService(db=mock_db)


@pytest.mark.asyncio
async def test_create_<name>_calls_db(
    write_service: <Name>WriteService,
    mock_db: AsyncMock,
) -> None:
    # Arrange
    request = Create<Name>Request(...)  # Fill in required fields

    # Act
    # result = await write_service.create_<name>(request)

    # Assert
    # mock_db.add.assert_called_once()
    # mock_db.commit.assert_called_once()
    pass  # Replace with real assertions when service is implemented
```
