from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.device import Device
from app.db.models.enums import DeviceStatus


class DeviceRepository:
    """access to data of Device."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, device_id: UUID) -> Device | None:
        stmt = (
            select(Device)
            .where(Device.id == device_id, Device.deleted_at.is_(None))
            .options(selectinload(Device.location))
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_code(self, device_code: str) -> Device | None:
        stmt = (
            select(Device)
            .where(Device.device_code == device_code, Device.deleted_at.is_(None))
            .options(selectinload(Device.location))
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_all(
        self,
        offset: int = 0,
        limit: int = 20,
        status: DeviceStatus | None = None,
        location_id: UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[Device], int]:
        base = select(Device).where(Device.deleted_at.is_(None))
        if status is not None:
            base = base.where(Device.status == status)
        if location_id is not None:
            base = base.where(Device.location_id == location_id)
        if search:
            like = f"%{search}%"
            base = base.where(
                (Device.device_code.ilike(like)) | (Device.name.ilike(like))
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base.order_by(Device.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(selectinload(Device.location))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, device: Device) -> Device:
        self.db.add(device)
        await self.db.flush()
        return device

    async def soft_delete(self, device: Device) -> None:
        device.deleted_at = datetime.now(tz=timezone.utc)
        await self.db.flush()

    async def touch_seen(
        self,
        device: Device,
        *,
        ip: str | None = None,
        heartbeat: bool = False,
    ) -> None:
        now = datetime.now(tz=timezone.utc)
        device.last_seen_at = now
        if heartbeat:
            device.last_heartbeat_at = now
        if ip is not None:
            device.last_ip_address = ip
        device.status = DeviceStatus.ONLINE
        await self.db.flush()

    async def apply_config(self, device: Device, config: dict[str, Any]) -> None:
        """set (price, power, toggle) on the models."""
        for key, value in config.items():
            if value is None:
                continue
            if hasattr(device, key):
                setattr(device, key, value)
        await self.db.flush()
