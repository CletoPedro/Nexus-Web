"""Postgres implementation of DocumentRepository."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import DocumentModel
from app.domain.documents.entity import Document
from app.domain.documents.repository import DocumentRepository


def _to_entity(row: DocumentModel) -> Document:
    return Document(
        id=row.id,
        title=row.title,
        user_id=row.user_id,
        description=row.description,
        category=row.category,
        file_name=row.file_name,
        file_type=row.file_type,
        file_size=row.file_size,
        storage_path=row.storage_path,
        tags=list(row.tags or []),
        expiry_date=row.expiry_date,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresDocumentRepository(DocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_row(
        self, document_id: uuid.UUID, *, user_id: uuid.UUID
    ) -> DocumentModel | None:
        stmt = select(DocumentModel).where(
            DocumentModel.id == document_id,
            DocumentModel.user_id == user_id,
            DocumentModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, document: Document) -> Document:
        row = DocumentModel(
            id=document.id,
            title=document.title,
            user_id=document.user_id,
            description=document.description,
            category=document.category,
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            storage_path=document.storage_path,
            tags=document.tags,
            expiry_date=document.expiry_date,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> Document | None:
        row = await self._get_row(document_id, user_id=user_id)
        return _to_entity(row) if row else None

    async def list_all(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Document]:
        stmt = select(DocumentModel).where(
            DocumentModel.user_id == user_id, DocumentModel.deleted_at.is_(None)
        )
        if category:
            stmt = stmt.where(DocumentModel.category == category)
        stmt = (
            stmt.order_by(DocumentModel.created_at.desc()).limit(limit).offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, document: Document) -> Document:
        row = await self._get_row(document.id, user_id=document.user_id)
        if row is None:
            raise ValueError(f"Document {document.id} not found")
        row.title = document.title
        row.description = document.description
        row.category = document.category
        row.file_name = document.file_name
        row.file_type = document.file_type
        row.file_size = document.file_size
        row.storage_path = document.storage_path
        row.tags = document.tags
        row.expiry_date = document.expiry_date
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, document_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        row = await self._get_row(document_id, user_id=user_id)
        if row is None:
            return
        row.deleted_at = func.now()
        await self._session.commit()

    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[Document]:
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(DocumentModel)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.deleted_at.is_(None),
                DocumentModel.search_vector.op("@@")(ts_query),
            )
            .order_by(func.ts_rank(DocumentModel.search_vector, ts_query).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[Document, float]]:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank(DocumentModel.search_vector, ts_query).label("rank")
        stmt = (
            select(DocumentModel, rank)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.deleted_at.is_(None),
                DocumentModel.search_vector.op("@@")(ts_query),
            )
            .order_by(rank.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(_to_entity(row), float(r)) for row, r in result.all()]
