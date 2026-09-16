"""
Timeline service. `list_events`/`search_events` serve the Timeline feed.
`record` is the integration point other API routers call after a
create/complete action in Memory, Tasks, Documents, or Inventory.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.timeline.entity import TimelineEvent, TimelineEventType
from app.domain.timeline.repository import TimelineRepository
from app.repositories.timeline_repository import PostgresTimelineRepository


class TimelineService:
    def __init__(self, repository: TimelineRepository):
        self._repo = repository

    async def record(
        self,
        *,
        event_type: TimelineEventType,
        entity_type: str,
        entity_id: uuid.UUID,
        title: str,
        user_id: uuid.UUID,
    ) -> TimelineEvent:
        event = TimelineEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            user_id=user_id,
        )
        return await self._repo.create(event)

    async def list_events(
        self,
        *,
        user_id: uuid.UUID,
        event_type: TimelineEventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TimelineEvent]:
        return await self._repo.list_all(
            user_id=user_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    async def search_events(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[TimelineEvent]:
        if not query or not query.strip():
            return []
        return await self._repo.search(query.strip(), user_id=user_id, limit=limit)


def get_timeline_service(
    session: AsyncSession = Depends(get_db_session),
) -> TimelineService:
    repository = PostgresTimelineRepository(session)
    return TimelineService(repository)
