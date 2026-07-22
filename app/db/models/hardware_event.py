"""
HardwareEvent —.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class HardwareEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    get events from hardware.
    """

    __tablename__ = "hardware_events"

    device_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    device_code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="device code",
    )

    # ---- Protocol fields ----
    command_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    method_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    command_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    tt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tf: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ---- Payload ----
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    raw_message: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc="main json message to debug audit",
    )

    # ---- Meta ----
    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    processed: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    processing_error: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("ix_hw_events_dev_created", "device_code", "created_at"),
        Index("ix_hw_events_command_created", "command_code", "created_at"),
    )
