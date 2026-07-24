"""
FastAPI dependencies — authentication .
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.core.exceptions import (
    ForbiddenException,
    TokenExpiredException,
    UnauthorizedException,
)
from app.core.security import decode_token
from app.db.models.user import User
from app.repositories.user_repository import UserRepository

# ---------- OAuth2 scheme ----------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login",
    auto_error=False,
)


# ---------- DB session ----------
DBSession = Annotated[AsyncSession, Depends(get_db)]


# ---------- Auth ----------
async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DBSession,
) -> User:
    if not token:
        raise UnauthorizedException("no token recived.")

    try:
        payload = decode_token(token, refresh=False)
    except JWTError as exc:
        raise TokenExpiredException(f"Invalid token: {exc}") from exc

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type.")

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("no token in Subject.")

    try:
        user_id = UUID(sub)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user.")

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("User not found.")
    if not user.is_active:
        raise ForbiddenException("Account is disable.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------- Permission check ----------
def require_permission(*required: str):
    """
    Dependency factory to check permissionها.

        @router.get(..., dependencies=[Depends(require_permission("device.view"))])
        async def endpoint(...): ...
    """

    async def _checker(current: CurrentUser) -> User:
        if current.is_superuser:
            return current
        missing = [p for p in required if p not in current.permission_codes]
        if missing:
            raise ForbiddenException(
                f"required permissions: {', '.join(missing)}",
                details={"missing_permissions": missing},
            )
        return current

    return _checker


def require_role(*required: str):
    """check to see the least roles."""

    async def _checker(current: CurrentUser) -> User:
        if current.is_superuser:
            return current
        user_role_codes = set(current.role_codes)
        if not user_role_codes.intersection(required):
            raise ForbiddenException(
                f"required role:  {', '.join(required)}",
            )
        return current

    return _checker


# ---------- Request meta ----------
def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")
