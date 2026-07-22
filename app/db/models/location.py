"""
Location — installed device location.
city , address, owner , phone number
"""


from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.device import Device


class Location(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """location of installed devices."""

    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(150), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # مختصات مرکز مکان (برای geofence)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geofence_radius_m: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="شعاع مجاز به متر",
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- relationships ----
    devices: Mapped[list["Device"]] = relationship(
        back_populates="location",
        lazy="noload",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Location name={self.name} city={self.city}>"
