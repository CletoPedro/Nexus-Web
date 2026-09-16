"""DocumentRepository interface — lives in domain/, per W1 architecture."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.documents.entity import Document


class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, document: Document) -> Document: ...

    @abstractmethod
    async def get(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> Document | None: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Document]: ...

    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Document]: ...

    @abstractmethod
    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[Document, float]]: ...
