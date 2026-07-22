"""
Device —  (Vending Machine).

- device_code: like (VM0001  ))
- firmware_version
- api_key_hash: for authenticate 
- aes_key: device unique keys (encrypt/decrypt)
- last online status :  heartbeat
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import DeviceStatus

if TYPE_CHECKING:
    from app.models.location import Location


class Device(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """ماشین فروش."""

    __tablename__ = "devices"

    device_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        doc="شناسه یکتای دستگاه مثل VM0001",
    )
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hardware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ---- Security ----
    api_key_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="SHA-256 hash of the device API key",
    )
    aes_key: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="AES-128 key unique for each device (hex or ASCII 16-char)",
    )
    aes_iv: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="IV for firmware with static IV ",
    )

    # ---- Status ----
    status: Mapped[DeviceStatus] = mapped_column(
        PGEnum(DeviceStatus, name="device_status_enum", create_type=True),
        default=DeviceStatus.OFFLINE,
        nullable=False,
        index=True,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # ---- Business config ----
    price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="price for each game",
    )
    power_on: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        doc="status of power",
    )
    toggle_interval_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
    toggle_duration_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
    toggle_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ---- Location ----
    location_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- relationships ----
    location: Mapped["Location | None"] = relationship(
        back_populates="devices",
        lazy="joined",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Device code={self.device_code} status={self.status}>"
