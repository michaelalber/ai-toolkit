# Security Patterns — FastAPI Scaffolder

Reference for the `fastapi-scaffolder` skill. JWT authentication, API key auth, OAuth2, role-based access, and CORS configuration patterns.

---

## JWT Bearer Token Authentication

```python
# app/dependencies.py
from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import settings

security = HTTPBearer()


class CurrentUser(BaseModel):
    """Authenticated user context."""
    id: int
    email: str
    roles: list[str]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """Validate JWT and return the current user."""
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],  # e.g., "HS256" or "RS256"
            options={"require": ["exp", "sub", "iat"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=int(payload["sub"]),
        email=payload.get("email", ""),
        roles=payload.get("roles", []),
    )


def require_role(role: str):
    """Factory for role-based authorization dependencies."""
    async def check_role(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return current_user
    return check_role
```

---

## API Key Authentication

```python
# app/dependencies.py (alternative to JWT)
from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(
    api_key: Annotated[str, Security(api_key_header)],
) -> str:
    """Validate API key from X-API-Key header."""
    # In production: look up in database or cache
    if api_key not in settings.valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key
```

---

## OAuth2 Password Flow (for user login endpoint)

```python
# app/routers/v1/auth.py
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import jwt

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Login",
    description="Exchange username and password for a JWT access token.",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserReadService, Depends(get_user_read_service)],
) -> TokenResponse:
    user = await user_service.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_in = 3600  # 1 hour
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": user.roles,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return TokenResponse(access_token=token, expires_in=expires_in)
```

---

## Rate Limiting with slowapi

```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app/routers/v1/auth.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/token")
@limiter.limit("5/minute")  # Strict limit on auth endpoints
async def login(request: Request, ...) -> TokenResponse:
    ...

# app/routers/v1/orders.py
@router.get("/")
@limiter.limit("100/minute")  # Relaxed limit on read endpoints
async def list_orders(request: Request, ...) -> OrderListResponse:
    ...
```

---

## CORS Configuration

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # List of allowed origins from config
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Development: ["http://localhost:3000", "http://localhost:8080"]
    # Production: ["https://app.example.com"]
    cors_origins: list[str] = ["http://localhost:3000"]

    # NEVER: allow_origins=["*"] with allow_credentials=True
    # This is a CORS security violation

settings = Settings()
```

---

## Settings with pydantic-settings

```python
# app/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "My API"
    debug: bool = False  # NEVER True in production
    version: str = "1.0.0"

    # Security
    jwt_secret: str = Field(..., min_length=32)  # Required; no default
    jwt_algorithm: str = "HS256"
    jwt_expiry_seconds: int = 3600

    # Database
    database_url: str = Field(...)  # Required; no default

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Rate limiting
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "5/minute"


settings = Settings()
```

---

## Router Registration in main.py

```python
# app/main.py
from fastapi import FastAPI
from app.config import settings
from app.exceptions import register_exception_handlers
from app.health import router as health_router
from app.routers.v1 import orders, users, auth

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs" if not settings.debug else "/docs",  # Disable in production if needed
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register exception handlers
register_exception_handlers(app)

# Register health checks (no version prefix — used by load balancers)
app.include_router(health_router)

# Register versioned API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
```
