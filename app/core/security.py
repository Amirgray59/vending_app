"""
validate and encrypt JWT.

adding :  (RBAC, permissions, ...).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------- Password hashing (bcrypt) ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """hash the password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool: 
    """validate the password."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT ----------
def _create_token(
    subject: str | int,
    expires_delta: timedelta,
    secret: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """generate JWT access token short live."""
    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        secret=settings.JWT_SECRET_KEY,
        extra_claims={"type": "access", **(extra_claims or {})},
    )


def create_refresh_token(subject: str | int) -> str:
    """generate JWT refresh token long live."""
    return _create_token(
        subject=subject,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        secret=settings.JWT_REFRESH_SECRET_KEY,
        extra_claims={"type": "refresh"},
    )


def decode_token(token: str, refresh: bool = False) -> dict[str, Any]:
    """
    validate and decrypt JWT.

    Raises:
        JWTError: invalid tokens.
    """
    secret = settings.JWT_REFRESH_SECRET_KEY if refresh else settings.JWT_SECRET_KEY
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise JWTError(f"Invalid token: {exc}") from exc
    return payload
