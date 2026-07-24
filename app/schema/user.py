"""Pydantic schemas for User."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserStatus
from app.schema.role import RoleReadBrief

# ---------- validators ----------
_USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"
_PHONE_PATTERN = r"^09\d{9}$"


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=_USERNAME_PATTERN)
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=_PHONE_PATTERN)
    full_name: str | None = Field(None, max_length=150)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role_codes: list[str] = Field(default_factory=list)
    is_superuser: bool = False

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contains at least one number")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contains at least one word.")
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=_PHONE_PATTERN)
    full_name: str | None = Field(None, max_length=150)
    status: UserStatus | None = None
    role_codes: list[str] | None = None


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    """نمایش کامل کاربر."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: UserStatus
    is_superuser: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleReadBrief] = []


class UserMe(UserRead):
    """اطلاعات کاربر جاری + permissions."""

    permissions: list[str] = []
