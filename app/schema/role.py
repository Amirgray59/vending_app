"""Pydantic schemas for Role."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schema.permission import PermissionRead


class RoleBase(BaseModel):
    code: str = Field(min_length=2, max_length=50, pattern=r"^[a-z_]+$")
    name_fa: str = Field(min_length=2, max_length=100)
    description: str | None = None


class RoleCreate(RoleBase):
    permission_codes: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name_fa: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    permission_codes: list[str] | None = None


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_system: bool
    permissions: list[PermissionRead] = []


class RoleReadBrief(BaseModel):
    """show the roles (for embed in User)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name_fa: str
