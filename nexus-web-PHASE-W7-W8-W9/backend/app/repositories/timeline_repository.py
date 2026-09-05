"""Postgres implementation of TimelineRepository."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.timeline_event import TimelineEventModel
from app.domain.timeline.entity import TimelineEvent, TimelineEventType
from app.domain.timeline.repository import TimelineRepository


def _to_entity(row: TimelineEventModel) -> TimelineEvent:
    return TimelineEvent(
        id=row.id,
        event_type=row.event_type,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        title=row.title,
        occurred_at=row.occurred_at,
        created_at=row.created_at,
    )


class PostgresTimelineRepository(TimelineRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: TimelineEvent) -> TimelineEvent:
        row = TimelineEventModel(
            id=event.id,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            title=event.title,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def list_all(
        self,
        *,
        event_type: TimelineEventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TimelineEvent]:
        stmt = select(TimelineEventModel)
        if event_type is not None:
            stmt = stmt.where(TimelineEventModel.event_type == event_type)
        if start_date is not None:
            stmt = stmt.where(TimelineEventModel.occurred_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(TimelineEventModel.occurred_at <= end_date)
        stmt = (
            stmt.order_by(TimelineEventModel.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def search(self, query: str, *, limit: int = 50) -> list[TimelineEvent]:
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(TimelineEventModel)
            .where(TimelineEventModel.search_vector.op("@@")(ts_query))
            .order_by(TimelineEventModel.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]
