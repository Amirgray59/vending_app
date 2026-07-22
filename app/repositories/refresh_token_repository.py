from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, update


from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """manage refresh token"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        token.revoked_at = datetime.now(tz=timezone.utc)
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """باطل کردن تمام توکن‌های فعال یک کاربر."""
        now = datetime.now(tz=timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=now)
        )
        result = await self.db.execute(stmt)
        return result.rowcount or 0
