"""Task service. DI factory lives here, same rationale as Memory's."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db_session
from app.domain.tasks.entity import Task, TaskPriority, TaskStatus
from app.domain.tasks.repository import TaskRepository
from app.repositories.task_repository import PostgresTaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    async def create_task(
        self,
        *,
        user_id: uuid.UUID,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime | None = None,
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty.")
        task = Task(
            title=title.strip(),
            user_id=user_id,
            description=description.strip() if description else "",
            priority=priority,
            due_date=due_date,
        )
        return await self._repo.create(task)

    async def get_task(self, task_id: uuid.UUID, *, user_id: uuid.UUID) -> Task:
        task = await self._repo.get(task_id, user_id=user_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found.")
        return task

    async def list_tasks(
        self,
        *,
        user_id: uuid.UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        overdue_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Task]:
        return await self._repo.list_all(
            user_id=user_id,
            status=status,
            priority=priority,
            overdue_only=overdue_only,
            limit=limit,
            offset=offset,
        )

    async def update_task(
        self,
        task_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        title: str,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
        due_date_provided: bool = False,
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty.")
        existing = await self.get_task(task_id, user_id=user_id)
        existing.title = title.strip()
        if description is not None:
            existing.description = description.strip()
        if priority is not None:
            existing.priority = priority
        if due_date_provided:
            existing.due_date = due_date
        return await self._repo.update(existing)

    async def set_status(
        self, task_id: uuid.UUID, new_status: TaskStatus, *, user_id: uuid.UUID
    ) -> Task:
        existing = await self.get_task(task_id, user_id=user_id)
        if not existing.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot transition task from {existing.status.value} to {new_status.value}."
            )
        existing.status = new_status
        existing.completed_at = (
            datetime.now(UTC) if new_status == TaskStatus.DONE else existing.completed_at
        )
        return await self._repo.update(existing)

    async def delete_task(self, task_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        await self.get_task(task_id, user_id=user_id)
        await self._repo.delete(task_id, user_id=user_id)

    async def search_tasks(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Task]:
        if not query or not query.strip():
            return []
        return await self._repo.search(query.strip(), user_id=user_id, limit=limit)


def get_task_service(session: AsyncSession = Depends(get_db_session)) -> TaskService:
    repository = PostgresTaskRepository(session)
    return TaskService(repository)
