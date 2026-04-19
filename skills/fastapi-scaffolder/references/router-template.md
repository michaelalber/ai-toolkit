# Router Template — FastAPI Scaffolder

Reference for the `fastapi-scaffolder` skill. Complete FastAPI router scaffold with OpenAPI metadata, Pydantic v2 models, authentication, and error handling.

---

## Complete Router Template

```python
# app/routers/v1/orders.py
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, field_validator

from app.dependencies import get_current_user, CurrentUser
from app.features.orders.dependencies import (
    get_order_read_service,
    get_order_write_service,
)
from app.features.orders.service import OrderReadService, OrderWriteService

# --- Router ---

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(get_current_user)],  # Auth applied to all routes
    responses={
        401: {"description": "Unauthorized — valid JWT required"},
        403: {"description": "Forbidden — insufficient permissions"},
    },
)

# --- Request Models ---

class CreateOrderRequest(BaseModel):
    """Request body for creating a new order."""
    model_config = ConfigDict(frozen=True)

    item_id: int
    quantity: int
    notes: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v


class UpdateOrderRequest(BaseModel):
    """Request body for updating an existing order."""
    model_config = ConfigDict(frozen=True)

    quantity: int | None = None
    notes: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v


# --- Response Models ---

class OrderResponse(BaseModel):
    """Response model for a single order."""
    model_config = ConfigDict(frozen=True)

    id: int
    item_id: int
    quantity: int
    status: str
    notes: str | None
    created_at: str
    updated_at: str


class OrderListResponse(BaseModel):
    """Response model for a paginated list of orders."""
    model_config = ConfigDict(frozen=True)

    items: list[OrderResponse]
    total: int
    page: int
    page_size: int


# --- Routes ---

@router.get(
    "/",
    response_model=OrderListResponse,
    summary="List orders",
    description="""
    Returns a paginated list of orders for the authenticated user.

    Results are sorted by creation date, newest first.
    Use `page` and `page_size` for pagination.
    """,
    responses={
        200: {"description": "Paginated list of orders"},
    },
)
async def list_orders(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    service: Annotated[OrderReadService, Depends(get_order_read_service)] = ...,
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> OrderListResponse:
    return await service.list_orders(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Returns a single order by its ID. Returns 404 if the order does not exist or belongs to another user.",
    responses={
        200: {"description": "Order found"},
        404: {"description": "Order not found"},
    },
)
async def get_order(
    order_id: int,
    service: Annotated[OrderReadService, Depends(get_order_read_service)] = ...,
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> OrderResponse:
    order = await service.get_order(order_id=order_id, user_id=current_user.id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Creates a new order for the authenticated user.",
    responses={
        201: {"description": "Order created successfully"},
        422: {"description": "Validation error — check request body"},
    },
)
async def create_order(
    request: CreateOrderRequest,
    service: Annotated[OrderWriteService, Depends(get_order_write_service)] = ...,
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> OrderResponse:
    return await service.create_order(request=request, user_id=current_user.id)


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order",
    description="Updates an existing order. Only the order owner can update it.",
    responses={
        200: {"description": "Order updated successfully"},
        404: {"description": "Order not found"},
        422: {"description": "Validation error — check request body"},
    },
)
async def update_order(
    order_id: int,
    request: UpdateOrderRequest,
    service: Annotated[OrderWriteService, Depends(get_order_write_service)] = ...,
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> OrderResponse:
    order = await service.update_order(
        order_id=order_id,
        request=request,
        user_id=current_user.id,
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete order",
    description="Deletes an order. Only the order owner can delete it.",
    responses={
        204: {"description": "Order deleted successfully"},
        404: {"description": "Order not found"},
    },
)
async def delete_order(
    order_id: int,
    service: Annotated[OrderWriteService, Depends(get_order_write_service)] = ...,
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = ...,
) -> None:
    deleted = await service.delete_order(order_id=order_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
```

---

## Health Check Template

```python
# app/health.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.dependencies import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@router.get("/health", response_model=HealthResponse, summary="Basic health check")
async def health() -> HealthResponse:
    """Returns 200 if the process is alive."""
    return HealthResponse(status="ok", version="1.0.0")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Returns 200 if all dependencies (database, etc.) are ready.",
    responses={503: {"description": "Service not ready"}},
)
async def readiness(db: AsyncSession = Depends(get_db)) -> ReadinessResponse:
    """Returns 200 if the application is ready to serve traffic."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    if db_status != "ok":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")

    return ReadinessResponse(status="ok", database=db_status)


@router.get("/health/live", response_model=HealthResponse, summary="Liveness check")
async def liveness() -> HealthResponse:
    """Returns 200 if the process is alive (no dependency checks)."""
    return HealthResponse(status="ok", version="1.0.0")
```

---

## Exception Handler Template

```python
# app/exceptions.py
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """RFC 7807 Problem Details for validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "https://example.com/problems/validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all handler — never expose stack traces."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://example.com/problems/internal-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred.",
                # Never include: str(exc), traceback, internal paths
            },
        )
```
