"""
Pydantic schema for the NOW dashboard (W11). Reuses the existing Out
schemas from each module rather than redefining fields — no duplication.
"""
from __future__ import annotations

from pydantic import BaseModel

from app.api.v1.schemas.document import DocumentOut
from app.api.v1.schemas.inventory import InventoryItemOut
from app.api.v1.schemas.memory import MemoryOut
from app.api.v1.schemas.task import TaskOut
from app.api.v1.schemas.timeline import TimelineEventOut


class NowResponse(BaseModel):
    overdue_tasks: list[TaskOut]
    high_priority_tasks: list[TaskOut]
    upcoming_tasks: list[TaskOut]
    recent_memories: list[MemoryOut]
    recent_documents: list[DocumentOut]
    recent_inventory: list[InventoryItemOut]
    recent_timeline: list[TimelineEventOut]
