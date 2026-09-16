"""
Timeline domain entity. Framework-independent, per W1 architecture.

Note (W9 spec deviation): the spec states "TimelineEvent table already
exists. Use it." This is not accurate for this codebase — no such table,
model, domain, or API existed before this phase. Documented explicitly in
the phase report rather than silently treated as true. The table is
created fresh in this phase's migration; no data loss is possible since
nothing existed to lose.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TimelineEventType(str, Enum):
    MEMORY_CREATED = "MEMORY_CREATED"
    TASK_CREATED = "TASK_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    DOCUMENT_CREATED = "DOCUMENT_CREATED"
    INVENTORY_CREATED = "INVENTORY_CREATED"
    INVENTORY_UPDATED = "INVENTORY_UPDATED"


@dataclass
class TimelineEvent:
    event_type: TimelineEventType
    entity_type: str
    entity_id: uuid.UUID
    title: str
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime | None = None
    created_at: datetime | None = None
