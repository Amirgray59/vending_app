"""
Audit Log — لاگ عملیات حساس کاربران.

طبق سند: تمام عملیات حساس باید در Audit Log ثبت شود.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """لاگ عملیات کاربران."""

    __tablename__ = "audit_logs"

    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="like: user.login, device.update, permission.grant",
    )
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)

    __table_args__ = (
        Index("ix_audit_action_created", "action", "created_at"),
    )
