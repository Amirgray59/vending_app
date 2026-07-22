"""Location repository."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.location import Location


class LocationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, location_id: UUID) -> Location | None:
        stmt = select(Location).where(
            Location.id == location_id, Location.deleted_at.is_(None)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 20) -> tuple[list[Location], int]:
        base = select(Location).where(Location.deleted_at.is_(None))
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        stmt = base.order_by(Location.created_at.desc()).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all()), total

    async def create(self, loc: Location) -> Location:
        self.db.add(loc)
        await self.db.flush()
        return loc

    async def soft_delete(self, loc: Location) -> None:
        loc.deleted_at = datetime.now(tz=timezone.utc)
        await self.db.flush()
