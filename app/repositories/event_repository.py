from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.db.models.device_command import DeviceCommand
from app.db.models.door_event import DoorEvent
from app.db.models.enums import CommandStatus
from app.db.models.game import Game
from app.db.models.hardware_event import HardwareEvent
from app.db.models.movement_event import MovementEvent
from app.db.models.payment import Payment


class HardwareEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, event: HardwareEvent) -> HardwareEvent:
        self.db.add(event)
        await self.db.flush()
        return event

    async def list_recent(
        self,
        device_code: str | None = None,
        command_code: int | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[HardwareEvent], int]:
        stmt = select(HardwareEvent)
        if device_code:
            stmt = stmt.where(HardwareEvent.device_code == device_code)
        if command_code is not None:
            stmt = stmt.where(HardwareEvent.command_code == command_code)

        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()

        stmt = stmt.order_by(HardwareEvent.created_at.desc()).offset(offset).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total


class _PaginatedByDeviceRepo:
    """Mixin repository برای رویدادهایی که با device_id فیلتر می‌شوند."""

    model: type

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_recent(
        self,
        *,
        device_id: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
        extra_filters: list | None = None,
    ) -> tuple[list, int]:
        stmt = select(self.model)
        if device_id is not None:
            stmt = stmt.where(self.model.device_id == device_id)
        for f in extra_filters or []:
            stmt = stmt.where(f)

        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()

        stmt = stmt.order_by(self.model.created_at.desc()).offset(offset).limit(limit)
        rows = list((await self.db.execute(stmt)).scalars().all())
        return rows, total


class PaymentRepository(_PaginatedByDeviceRepo):
    model = Payment

    async def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def sum_amount(
        self,
        *,
        device_id: UUID | None = None,
    ) -> int:
        stmt = select(func.coalesce(func.sum(Payment.amount), 0))
        if device_id is not None:
            stmt = stmt.where(Payment.device_id == device_id)
        return int((await self.db.execute(stmt)).scalar_one())


class GameRepository(_PaginatedByDeviceRepo):
    model = Game

    async def create(self, game: Game) -> Game:
        self.db.add(game)
        await self.db.flush()
        return game


class DoorEventRepository(_PaginatedByDeviceRepo):
    model = DoorEvent

    async def create(self, e: DoorEvent) -> DoorEvent:
        self.db.add(e)
        await self.db.flush()
        return e


class MovementEventRepository(_PaginatedByDeviceRepo):
    model = MovementEvent

    async def create(self, e: MovementEvent) -> MovementEvent:
        self.db.add(e)
        await self.db.flush()
        return e


class AlertRepository(_PaginatedByDeviceRepo):
    model = Alert

    async def create(self, alert: Alert) -> Alert:
        self.db.add(alert)
        await self.db.flush()
        return alert

    async def list_by_status(
        self,
        *,
        status: Any = None,
        device_id: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Alert], int]:
        extras = [Alert.status == status] if status is not None else []
        return await self.list_recent(
            device_id=device_id,
            offset=offset,
            limit=limit,
            extra_filters=extras,
        )

    async def get_by_id(self, alert_id: UUID) -> Alert | None:
        stmt = select(Alert).where(Alert.id == alert_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()


class DeviceCommandRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, cmd: DeviceCommand) -> DeviceCommand:
        self.db.add(cmd)
        await self.db.flush()
        return cmd

    async def get_by_id(self, command_id: UUID) -> DeviceCommand | None:
        stmt = select(DeviceCommand).where(DeviceCommand.id == command_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_pending_for_device(self, device_id: UUID) -> list[DeviceCommand]:
        stmt = (
            select(DeviceCommand)
            .where(
                DeviceCommand.device_id == device_id,
                DeviceCommand.status.in_([CommandStatus.PENDING, CommandStatus.SENT]),
            )
            .order_by(DeviceCommand.created_at.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_oldest_unfinished_for_device_command(
        self,
        device_id: UUID,
        command_code: int,
    ) -> DeviceCommand | None:
        stmt = (
            select(DeviceCommand)
            .where(
                DeviceCommand.device_id == device_id,
                DeviceCommand.command_code == command_code,
                DeviceCommand.status.in_([CommandStatus.PENDING, CommandStatus.SENT]),
            )
            .order_by(DeviceCommand.created_at.asc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def mark_sent(self, cmd: DeviceCommand) -> None:
        cmd.status = CommandStatus.SENT
        cmd.sent_at = datetime.now(tz=timezone.utc)
        await self.db.flush()

    async def mark_ack(
        self,
        cmd: DeviceCommand,
        *,
        applied: bool,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        cmd.status = CommandStatus.APPLIED if applied else CommandStatus.FAILED
        cmd.acknowledged_at = datetime.now(tz=timezone.utc)
        cmd.result_data = result
        cmd.error_message = error
        await self.db.flush()
