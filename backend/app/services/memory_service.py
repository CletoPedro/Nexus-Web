"""Memory service, plus its dependency-injection factory."""
from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db_session
from app.domain.memory.entity import Memory
from app.domain.memory.repository import MemoryRepository
from app.repositories.memory_repository import PostgresMemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository):
        self._repo = repository

    async def create_memory(
        self,
        *,
        user_id: uuid.UUID,
        content: str,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Memory:
        if not content or not content.strip():
            raise ValidationError("Memory content cannot be empty.")
        memory = Memory(
            content=content.strip(),
            user_id=user_id,
            tags=tags or [],
            metadata_=metadata or {},
        )
        return await self._repo.create(memory)

    async def get_memory(self, memory_id: uuid.UUID, *, user_id: uuid.UUID) -> Memory:
        memory = await self._repo.get(memory_id, user_id=user_id)
        if memory is None:
            raise NotFoundError(f"Memory {memory_id} not found.")
        return memory

    async def list_memories(
        self, *, user_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Memory]:
        return await self._repo.list_all(user_id=user_id, limit=limit, offset=offset)

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        content: str,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Memory:
        if not content or not content.strip():
            raise ValidationError("Memory content cannot be empty.")
        existing = await self.get_memory(memory_id, user_id=user_id)  # raises NotFoundError
        existing.content = content.strip()
        existing.tags = tags if tags is not None else existing.tags
        existing.metadata_ = metadata if metadata is not None else existing.metadata_
        return await self._repo.update(existing)

    async def delete_memory(self, memory_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        await self.get_memory(memory_id, user_id=user_id)  # raises NotFoundError if missing
        await self._repo.delete(memory_id, user_id=user_id)

    async def search_memories(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Memory]:
        if not query or not query.strip():
            return []
        return await self._repo.search(query.strip(), user_id=user_id, limit=limit)


def get_memory_service(
    session: AsyncSession = Depends(get_db_session),
) -> MemoryService:
    """
    FastAPI DI provider. Lives here (services/), not in api/dependencies.py,
    because per the W1 dependency-boundary table `api` may import
    `services` but not `repositories` directly — only `services` is
    allowed to import `repositories`. Composing repository -> service is
    therefore a services-layer responsibility.
    """
    repository = PostgresMemoryRepository(session)
    return MemoryService(repository)
