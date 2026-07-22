"""User repository — دسترسی به داده."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.user import User


class UserRepository:
    """CRUD users."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        stmt = (
            select(User)
            .where(
                User.deleted_at.is_(None),
                or_(
                    User.username == identifier,
                    User.email == identifier,
                    User.phone == identifier,
                ),
            )
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(
            User.username == username, User.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        """لیست + شمارش کل."""
        from sqlalchemy import func

        count_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user, attribute_names=["roles"])
        return user

    async def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(tz=timezone.utc)
        user.failed_login_attempts = 0
        await self.db.flush()

    async def increment_failed_login(self, user: User) -> None:
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        await self.db.flush()

    async def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.now(tz=timezone.utc)
        await self.db.flush()
