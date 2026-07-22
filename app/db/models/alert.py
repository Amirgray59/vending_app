"""
Alert — هشدارهای سیستم.

از رویدادهای مختلف (movement, door, offline, ...) ایجاد می‌شود.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

from app.db.models.enums import AlertSeverity, AlertStatus


class Alert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """هشدار سیستم."""

    __tablename__ = "alerts"

    device_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alert_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="movement, door_open_long, device_offline, inventory_low, ...",
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        PGEnum(AlertSeverity, name="alert_severity_enum", create_type=True),
        default=AlertSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    status: Mapped[AlertStatus] = mapped_column(
        PGEnum(AlertStatus, name="alert_status_enum", create_type=True),
        default=AlertStatus.OPEN,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
