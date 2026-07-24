"""
Auth service — manager.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    ForbiddenException,
    InvalidCredentialsException,
    TokenExpiredException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.models.enums import UserStatus
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schema.auth import TokenPair

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    """auth service manager."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)

    # ---------- Login ----------
    async def login(
        self,
        identifier: str,
        password: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, TokenPair]:
        """validate and give token."""

        user = await self.users.get_by_identifier(identifier)
        if user is None:
            raise InvalidCredentialsException()

        # بررسی lock
        if user.locked_until and user.locked_until > datetime.now(tz=timezone.utc):
            raise ForbiddenException("User account has been locked for too many Invalid requests.")

        # بررسی وضعیت
        if user.status == UserStatus.INACTIVE:
            raise ForbiddenException("User account is inactive.")
        if user.status == UserStatus.LOCKED:
            raise ForbiddenException("User account has been locked.")

        # check the password 
        if not verify_password(password, user.password_hash):
            await self.users.increment_failed_login(user)
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(tz=timezone.utc) + timedelta(
                    minutes=LOCK_DURATION_MINUTES
                )
                await self.db.flush()
            await self.db.commit()
            raise InvalidCredentialsException()

        # success
        await self.users.update_last_login(user)
        pair = await self._issue_tokens(user, user_agent=user_agent, ip_address=ip_address)
        await self.db.commit()
        return user, pair

    # ---------- Refresh ----------
    async def refresh(self, refresh_token: str) -> TokenPair:
        """gives new access token from refresh token."""

        try:
            payload = decode_token(refresh_token, refresh=True)
        except JWTError:
            raise TokenExpiredException("Invalid or expired Refresh token.")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Token type is invalid.")

        token_hash = _hash_token(refresh_token)
        stored = await self.tokens.get_by_hash(token_hash)
        if stored is None or stored.revoked:
            raise UnauthorizedException("Refresh token is expired.")

        if stored.expires_at < datetime.now(tz=timezone.utc):
            raise TokenExpiredException()

        user = await self.users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or it has been disabled.")

        # rotation:creates a new token 
        await self.tokens.revoke(stored)
        pair = await self._issue_tokens(user)
        await self.db.commit()
        return pair

    # ---------- Logout ----------
    async def logout(
        self,
        user_id: UUID,
        *,
        refresh_token: str | None = None,
        all_devices: bool = False,
    ) -> int:
        """
        expire refresh token.

        Returns:
            number of expired tokens.
        """
        if all_devices:
            count = await self.tokens.revoke_all_for_user(user_id)
            await self.db.commit()
            return count

        if refresh_token:
            stored = await self.tokens.get_by_hash(_hash_token(refresh_token))
            if stored and stored.user_id == user_id and not stored.revoked:
                await self.tokens.revoke(stored)
                await self.db.commit()
                return 1

        return 0

    # ---------- Internal ----------
    async def _issue_tokens(
        self,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        access = create_access_token(
            subject=str(user.id),
            extra_claims={
                "username": user.username,
                "is_superuser": user.is_superuser,
            },
        )
        refresh = create_refresh_token(subject=str(user.id))

        # store refresh token
        stored = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(refresh),
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self.tokens.create(stored)

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
