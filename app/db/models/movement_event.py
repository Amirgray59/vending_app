"""
MovementEvent — events of moving of the machine.

doc:  Excel Command 9 (movement alarm) + Command 10 (offline movements).

levels:
  1 = movement_level1
  2 = movement_level2
"""

from datetime import datetime
from enum import IntEnum
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class MovementLevel(IntEnum):
    LEVEL_1 = 1
    LEVEL_2 = 2


class MovementEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """رویداد جابه‌جایی/لرزش."""

    __tablename__ = "movement_events"

    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_offline_recovered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    hardware_event_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("hardware_events.id", ondelete="SET NULL"),
        nullable=True,
    )
