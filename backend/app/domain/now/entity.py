"""
NowSnapshot: an aggregated "what's happening now" view. Not persisted —
NOW has no table of its own; it composes the existing Task/Memory/
Document/Inventory/Timeline services, per W11 ("não duplicar lógica").
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.documents.entity import Document
from app.domain.inventory.entity import InventoryItem
from app.domain.memory.entity import Memory
from app.domain.tasks.entity import Task
from app.domain.timeline.entity import TimelineEvent


@dataclass
class NowSnapshot:
    overdue_tasks: list[Task]
    high_priority_tasks: list[Task]
    upcoming_tasks: list[Task]
    recent_memories: list[Memory]
    recent_documents: list[Document]
    recent_inventory: list[InventoryItem]
    recent_timeline: list[TimelineEvent]
