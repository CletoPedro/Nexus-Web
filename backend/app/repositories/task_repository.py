"""Postgres implementation of TaskRepository, using SQLAlchemy."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import TaskModel
from app.domain.tasks.entity import Task, TaskPriority, TaskStatus
from app.domain.tasks.repository import TaskRepository


def _to_entity(row: TaskModel) -> Task:
    return Task(
        id=row.id,
        title=row.title,
        user_id=row.user_id,
        description=row.description,
        status=row.status,
        priority=row.priority,
        due_date=row.due_date,
        completed_at=row.completed_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_row(self, task_id: uuid.UUID, *, user_id: uuid.UUID) -> TaskModel | None:
        stmt = select(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id,
            TaskModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, task: Task) -> Task:
        row = TaskModel(
            id=task.id,
            title=task.title,
            user_id=task.user_id,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            completed_at=task.completed_at,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, task_id: uuid.UUID, *, user_id: uuid.UUID) -> Task | None:
        row = await self._get_row(task_id, user_id=user_id)
        return _to_entity(row) if row else None

    async def list_all(
        self,
        *,
        user_id: uuid.UUID,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        overdue_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Task]:
        stmt = select(TaskModel).where(
            TaskModel.user_id == user_id, TaskModel.deleted_at.is_(None)
        )
        if status is not None:
            stmt = stmt.where(TaskModel.status == status)
        if priority is not None:
            stmt = stmt.where(TaskModel.priority == priority)
        if overdue_only:
            now = datetime.now(UTC)
            stmt = stmt.where(
                TaskModel.due_date.is_not(None),
                TaskModel.due_date < now,
                TaskModel.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            )
        stmt = (
            stmt.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, task: Task) -> Task:
        row = await self._get_row(task.id, user_id=task.user_id)
        if row is None:
            raise ValueError(f"Task {task.id} not found")
        row.title = task.title
        row.description = task.description
        row.status = task.status
        row.priority = task.priority
        row.due_date = task.due_date
        row.completed_at = task.completed_at
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, task_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        row = await self._get_row(task_id, user_id=user_id)
        if row is None:
            return
        row.deleted_at = func.now()
        await self._session.commit()

    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Task]:
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(TaskModel)
            .where(
                TaskModel.user_id == user_id,
                TaskModel.deleted_at.is_(None),
                TaskModel.search_vector.op("@@")(ts_query),
            )
            .order_by(func.ts_rank(TaskModel.search_vector, ts_query).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[Task, float]]:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank(TaskModel.search_vector, ts_query).label("rank")
        stmt = (
            select(TaskModel, rank)
            .where(
                TaskModel.user_id == user_id,
                TaskModel.deleted_at.is_(None),
                TaskModel.search_vector.op("@@")(ts_query),
            )
            .order_by(rank.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(_to_entity(row), float(r)) for row, r in result.all()]
