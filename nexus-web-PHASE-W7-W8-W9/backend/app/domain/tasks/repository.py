"""TaskRepository interface — lives in domain/, per W1 architecture."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.tasks.entity import Task, TaskPriority, TaskStatus


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task: ...

    @abstractmethod
    async def get(self, task_id: uuid.UUID) -> Task | None: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        overdue_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Task]: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 50) -> list[Task]: ...
