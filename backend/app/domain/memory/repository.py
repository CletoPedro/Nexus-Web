"""
MemoryRepository interface. Defined in `domain/` so that services can
depend on the abstraction rather than a concrete database implementation
(the Postgres implementation lives in repositories/memory_repository.py).
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.memory.entity import Memory


class MemoryRepository(ABC):
    @abstractmethod
    async def create(self, memory: Memory) -> Memory: ...

    @abstractmethod
    async def get(self, memory_id: uuid.UUID) -> Memory | None: ...

    @abstractmethod
    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[Memory]: ...

    @abstractmethod
    async def update(self, memory: Memory) -> Memory: ...

    @abstractmethod
    async def delete(self, memory_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 50) -> list[Memory]: ...
