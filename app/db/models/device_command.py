"""
DeviceCommand — فرمان‌های ارسالی از سرور به دستگاه.

طبق سند: هر تغییر تنظیمات (قیمت، برق، toggle) از طریق فرمان انجام می‌شود
و ACK آن ثبت می‌گردد.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

from app.db.models.enums import CommandStatus


class DeviceCommand(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """command for each device."""

    __tablename__ = "device_commands"

    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    command_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    method_code: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    command_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[CommandStatus] = mapped_column(
        PGEnum(CommandStatus, name="command_status_enum", create_type=True),
        default=CommandStatus.PENDING,
        nullable=False,
        index=True,
    )
    result_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    issued_by_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
