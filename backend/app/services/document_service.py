"""Document service. DI factory lives here, same rationale as Memory/Task."""
from __future__ import annotations

import uuid
from datetime import date

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db_session
from app.domain.documents.entity import Document
from app.domain.documents.repository import DocumentRepository
from app.repositories.document_repository import PostgresDocumentRepository


class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self._repo = repository

    async def create_document(
        self,
        *,
        user_id: uuid.UUID,
        title: str,
        description: str = "",
        category: str = "",
        file_name: str = "",
        file_type: str = "",
        file_size: int | None = None,
        storage_path: str = "",
        tags: list[str] | None = None,
        expiry_date: date | None = None,
    ) -> Document:
        if not title or not title.strip():
            raise ValidationError("Document title cannot be empty.")
        document = Document(
            title=title.strip(),
            user_id=user_id,
            description=description.strip() if description else "",
            category=category.strip() if category else "",
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            tags=tags or [],
            expiry_date=expiry_date,
        )
        return await self._repo.create(document)

    async def get_document(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> Document:
        document = await self._repo.get(document_id, user_id=user_id)
        if document is None:
            raise NotFoundError(f"Document {document_id} not found.")
        return document

    async def list_documents(
        self, *, user_id: uuid.UUID, category: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Document]:
        return await self._repo.list_all(
            user_id=user_id, category=category, limit=limit, offset=offset
        )

    async def update_document(
        self,
        document_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        title: str,
        description: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        expiry_date: date | None = None,
        expiry_date_provided: bool = False,
    ) -> Document:
        if not title or not title.strip():
            raise ValidationError("Document title cannot be empty.")
        existing = await self.get_document(document_id, user_id=user_id)
        existing.title = title.strip()
        if description is not None:
            existing.description = description.strip()
        if category is not None:
            existing.category = category.strip()
        if tags is not None:
            existing.tags = tags
        if expiry_date_provided:
            existing.expiry_date = expiry_date
        return await self._repo.update(existing)

    async def delete_document(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        await self.get_document(document_id, user_id=user_id)
        await self._repo.delete(document_id, user_id=user_id)

    async def search_documents(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Document]:
        if not query or not query.strip():
            return []
        return await self._repo.search(query.strip(), user_id=user_id, limit=limit)


def get_document_service(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentService:
    repository = PostgresDocumentRepository(session)
    return DocumentService(repository)
