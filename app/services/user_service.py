"""User service — user management logins."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schema.user import UserCreate, UserUpdate


class UserService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    async def create_user(self, data: UserCreate) -> User:
        # بررسی یکتا بودن username
        if await self.users.get_by_username(data.username):
            raise ConflictException("username already exist.")

        # ساخت user
        user = User(
            username=data.username,
            email=data.email,
            phone=data.phone,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            is_superuser=data.is_superuser,
        )

        # افزودن نقش‌ها
        if data.role_codes:
            roles = await self.roles.get_many_by_codes(data.role_codes)
            missing = set(data.role_codes) - {r.code for r in roles}
            if missing:
                raise ValidationException(
                    f"rols not found: {', '.join(missing)}"
                )
            user.roles = roles

        try:
            created = await self.users.create(user)
            await self.db.commit()
            return created
        except IntegrityError as exc:
            await self.db.rollback()
            raise ConflictException("duplicated (email/phone).") from exc

    async def get_user(self, user_id: UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundException("user not found.")
        return user

    async def list_users(self, offset: int, limit: int) -> tuple[list[User], int]:
        return await self.users.list_all(offset=offset, limit=limit)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)

        if data.email is not None:
            user.email = data.email
        if data.phone is not None:
            user.phone = data.phone
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.status is not None:
            user.status = data.status

        if data.role_codes is not None:
            roles = await self.roles.get_many_by_codes(data.role_codes)
            missing = set(data.role_codes) - {r.code for r in roles}
            if missing:
                raise ValidationException(
                    f"roles not found: {', '.join(missing)}"
                )
            user.roles = roles

        await self.db.commit()
        return await self.get_user(user_id)  # refresh با روابط

    async def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> None:
        if not verify_password(old_password, user.password_hash):
            raise ValidationException("Password not right.")
        user.password_hash = hash_password(new_password)
        await self.db.commit()

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user(user_id)
        if user.is_superuser:
            raise ValidationException("Delete Super Admin is not valid.")
        await self.users.soft_delete(user)
        await self.db.commit()
