"""Pydantic schemas for the Timeline API."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.timeline.entity import TimelineEventType


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: TimelineEventType
    entity_type: str
    entity_id: uuid.UUID
    title: str
    occurred_at: datetime | None
    created_at: datetime | None
