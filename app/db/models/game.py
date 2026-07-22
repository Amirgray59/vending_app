"""
Game — result of the game.

doc: Excel Command 13 (reward alarm) + Command 14 (offline rewards).
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

from app.db.models.enums import GameResult


class Game(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """record of a game."""

    __tablename__ = "games"

    device_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    result: Mapped[GameResult] = mapped_column(
        PGEnum(GameResult, name="game_result_enum", create_type=True),
        nullable=False,
        index=True,
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prize_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reward_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="number of gained rewards ",
    )
    is_offline_recovered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    payment_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )
    hardware_event_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("hardware_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
