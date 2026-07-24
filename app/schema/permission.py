"""Pydantic schemas for Permission."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionRead(BaseModel):
    """show one permission."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name_fa: str
    description: str | None = None
    category: str


class PermissionCreate(BaseModel):
    code: str = Field(min_length=3, max_length=100, pattern=r"^[a-z_]+\.[a-z_]+$")
    name_fa: str = Field(min_length=2, max_length=150)
    description: str | None = None
    category: str = "general"
