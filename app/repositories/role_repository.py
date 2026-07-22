"""Role & Permission repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.permission import Permission
from app.db.models.role import Role


class RoleRepository:
    """CRUD roles."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, role_id: UUID) -> Role | None:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Role | None:
        stmt = (
            select(Role).where(Role.code == code).options(selectinload(Role.permissions))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many_by_codes(self, codes: list[str]) -> list[Role]:
        if not codes:
            return []
        stmt = (
            select(Role)
            .where(Role.code.in_(codes))
            .options(selectinload(Role.permissions))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Role]:
        stmt = select(Role).order_by(Role.code).options(selectinload(Role.permissions))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role, attribute_names=["permissions"])
        return role


class PermissionRepository:
    """CRUD permissions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_code(self, code: str) -> Permission | None:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many_by_codes(self, codes: list[str]) -> list[Permission]:
        if not codes:
            return []
        stmt = select(Permission).where(Permission.code.in_(codes))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.category, Permission.code)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, permission: Permission) -> Permission:
        self.db.add(permission)
        await self.db.flush()
        return permission
