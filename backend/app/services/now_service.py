"""
NOW service (W11). Composes the existing Task/Memory/Document/Inventory/
Timeline services — no query logic is duplicated here, only aggregation,
filtering (overdue/high-priority/upcoming), and sorting for the dashboard.

W12: every call is scoped to user_id.

Sequential awaits, not asyncio.gather: all underlying services share the
same request-scoped AsyncSession, which is not safe for concurrent use.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.now.entity import NowSnapshot
from app.domain.tasks.entity import TaskPriority, TaskStatus
from app.services.document_service import DocumentService, get_document_service
from app.services.inventory_service import InventoryService, get_inventory_service
from app.services.memory_service import MemoryService, get_memory_service
from app.services.task_service import TaskService, get_task_service
from app.services.timeline_service import TimelineService, get_timeline_service


class NowService:
    def __init__(
        self,
        task_service: TaskService,
        memory_service: MemoryService,
        document_service: DocumentService,
        inventory_service: InventoryService,
        timeline_service: TimelineService,
    ):
        self._tasks = task_service
        self._memory = memory_service
        self._documents = document_service
        self._inventory = inventory_service
        self._timeline = timeline_service

    async def get_snapshot(
        self,
        *,
        user_id: uuid.UUID,
        recent_limit: int = 5,
        upcoming_days: int = 7,
        task_limit: int = 10,
    ) -> NowSnapshot:
        todo = await self._tasks.list_tasks(user_id=user_id, status=TaskStatus.TODO, limit=200)
        in_progress = await self._tasks.list_tasks(
            user_id=user_id, status=TaskStatus.IN_PROGRESS, limit=200
        )
        pending = todo + in_progress

        now = datetime.now(UTC)
        upcoming_cutoff = now + timedelta(days=upcoming_days)

        overdue = sorted(
            (t for t in pending if t.is_overdue(now=now)),
            key=lambda t: t.due_date,
        )
        overdue_ids = {t.id for t in overdue}

        high_priority = sorted(
            (
                t
                for t in pending
                if t.priority in (TaskPriority.HIGH, TaskPriority.CRITICAL)
                and t.id not in overdue_ids
            ),
            key=lambda t: (t.priority != TaskPriority.CRITICAL, t.due_date or datetime.max.replace(tzinfo=UTC)),
        )

        upcoming = sorted(
            (
                t
                for t in pending
                if t.due_date
                and t.id not in overdue_ids
                and now <= t.due_date <= upcoming_cutoff
            ),
            key=lambda t: t.due_date,
        )

        recent_memories = await self._memory.list_memories(user_id=user_id, limit=recent_limit)
        recent_documents = await self._documents.list_documents(user_id=user_id, limit=recent_limit)
        recent_inventory = await self._inventory.list_items(user_id=user_id, limit=recent_limit)
        recent_timeline = await self._timeline.list_events(user_id=user_id, limit=recent_limit)

        return NowSnapshot(
            overdue_tasks=overdue[:task_limit],
            high_priority_tasks=high_priority[:task_limit],
            upcoming_tasks=upcoming[:task_limit],
            recent_memories=recent_memories,
            recent_documents=recent_documents,
            recent_inventory=recent_inventory,
            recent_timeline=recent_timeline,
        )


def get_now_service(session: AsyncSession = Depends(get_db_session)) -> NowService:
    return NowService(
        task_service=get_task_service(session),
        memory_service=get_memory_service(session),
        document_service=get_document_service(session),
        inventory_service=get_inventory_service(session),
        timeline_service=get_timeline_service(session),
    )
