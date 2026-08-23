"""
Memory domain entity. Per the W1 architecture, `domain/` never imports
SQLAlchemy, FastAPI, or any infrastructure concern — this is a plain
dataclass, and the ORM model in db/models/memory.py is a separate,
mapped representation of the same concept.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Memory:
    content: str
    tags: list[str] = field(default_factory=list)
    metadata_: dict = field(default_factory=dict)
    expires_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_expired(self, *, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now
