"""InventoryRepository interface — lives in domain/, per W1 architecture."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.inventory.entity import InventoryItem


class InventoryRepository(ABC):
    @abstractmethod
    async def create(self, item: InventoryItem) -> InventoryItem: ...

    @abstractmethod
    async def get(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> InventoryItem | None: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        location: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InventoryItem]: ...

    @abstractmethod
    async def update(self, item: InventoryItem) -> InventoryItem: ...

    @abstractmethod
    async def delete(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[InventoryItem]: ...

    @abstractmethod
    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[InventoryItem, float]]: ...
