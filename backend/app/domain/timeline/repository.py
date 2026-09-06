"""TimelineRepository interface — lives in domain/, per W1 architecture."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.timeline.entity import TimelineEvent, TimelineEventType


class TimelineRepository(ABC):
    @abstractmethod
    async def create(self, event: TimelineEvent) -> TimelineEvent: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        event_type: TimelineEventType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TimelineEvent]: ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 50) -> list[TimelineEvent]: ...
