"""
DoorEvent — events for doors.

doc :  Command 11 (door alarm) + Command 12 (offline door events).

door type:
  1 = open_door_alarm
  2 = close_door_alarm
  3 = open_door_for_past_1min (long open door)
"""

from datetime import datetime
from enum import IntEnum
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DoorEventType(IntEnum):
    OPEN = 1
    CLOSE = 2
    LONG_OPEN = 3


class DoorEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """open and close events."""

    __tablename__ = "door_events"

    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
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
