"""
MemoryRepository interface. Defined in `domain/` so that services can
depend on the abstraction rather than a concrete database implementation
(the Postgres implementation lives in repositories/memory_repository.py).

W12: every method takes `user_id` and filters/verifies ownership — a
user must never be able to read, modify, or delete another user's data.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.memory.entity import Memory


class MemoryRepository(ABC):
    @abstractmethod
    async def create(self, memory: Memory) -> Memory: ...

    @abstractmethod
    async def get(self, memory_id: uuid.UUID, *, user_id: uuid.UUID) -> Memory | None: ...

    @abstractmethod
    async def list_all(
        self, *, user_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Memory]: ...

    @abstractmethod
    async def update(self, memory: Memory) -> Memory: ...

    @abstractmethod
    async def delete(self, memory_id: uuid.UUID, *, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Memory]: ...

    @abstractmethod
    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[Memory, float]]:
        """Same as search(), but also returns each result's ts_rank score.
        Used by the global search (W10) to normalize relevance across
        modules. Additive — does not replace search()."""
        ...
