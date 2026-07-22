"""
Permission — permissions for each action.

permissions have codes : 
    device.view, device.create, finance.export, ...

doc :
- device.view, device.create, device.configure
- location.view
- finance.export
- report.view
- alert.resolve
- inventory.refill
- device_control.execute
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        doc="permission code device.view",
    )
    name_fa: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="نام فارسی نمایشی",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="general",
        index=True,
        doc="گروه‌بندی برای نمایش (device / finance / report / ...)",
    )

    def __repr__(self) -> str:  
        return f"<Permission code={self.code}>"
