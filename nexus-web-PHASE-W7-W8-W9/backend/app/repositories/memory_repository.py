"""Postgres implementation of MemoryRepository, using SQLAlchemy."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.memory import MemoryModel
from app.domain.memory.entity import Memory
from app.domain.memory.repository import MemoryRepository


def _to_entity(row: MemoryModel) -> Memory:
    return Memory(
        id=row.id,
        content=row.content,
        tags=list(row.tags or []),
        metadata_=dict(row.metadata_ or {}),
        expires_at=row.expires_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresMemoryRepository(MemoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, memory: Memory) -> Memory:
        row = MemoryModel(
            id=memory.id,
            content=memory.content,
            tags=memory.tags,
            metadata_=memory.metadata_,
            expires_at=memory.expires_at,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, memory_id: uuid.UUID) -> Memory | None:
        row = await self._session.get(MemoryModel, memory_id)
        if row is None or row.deleted_at is not None:
            return None
        return _to_entity(row)

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[Memory]:
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.deleted_at.is_(None))
            .order_by(MemoryModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, memory: Memory) -> Memory:
        row = await self._session.get(MemoryModel, memory.id)
        if row is None or row.deleted_at is not None:
            raise ValueError(f"Memory {memory.id} not found")
        row.content = memory.content
        row.tags = memory.tags
        row.metadata_ = memory.metadata_
        row.expires_at = memory.expires_at
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, memory_id: uuid.UUID) -> None:
        row = await self._session.get(MemoryModel, memory_id)
        if row is None:
            return
        row.deleted_at = func.now()
        await self._session.commit()

    async def search(self, query: str, *, limit: int = 50) -> list[Memory]:
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(MemoryModel)
            .where(
                MemoryModel.deleted_at.is_(None),
                MemoryModel.search_vector.op("@@")(ts_query),
            )
            .order_by(
                func.ts_rank(MemoryModel.search_vector, ts_query).desc()
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]
