"""
Payment — payment transaction.

doc:  Excel Command 7 (new purchase) + Command 8 (offline purchases).
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import PaymentStatus


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "payments"

    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, doc="تومان")
    status: Mapped[PaymentStatus] = mapped_column(
        PGEnum(PaymentStatus, name="payment_status_enum", create_type=True),
        default=PaymentStatus.SUCCESS,
        nullable=False,
        index=True,
    )
    tracking_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # اگر offline بوده و بعد sync شده
    is_offline_recovered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="زمان واقعی خرید در دستگاه (نه زمان ذخیره در سرور)",
    )

    hardware_event_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("hardware_events.id", ondelete="SET NULL"),
        nullable=True,
    )
