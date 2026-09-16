"""
Global Search service (W10). Composes the search_with_rank() methods
already implemented on the Memory/Task/Document/Inventory repositories —
no search logic is duplicated here, only normalization and grouping.

W12: every call is scoped to user_id — a user only ever searches their
own data.

Queries run sequentially, not via asyncio.gather: a single SQLAlchemy
AsyncSession is not safe for concurrent use by multiple coroutines, and
all four repositories share the same request-scoped session.
"""
from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.search.entity import SearchResult
from app.repositories.document_repository import PostgresDocumentRepository
from app.repositories.inventory_repository import PostgresInventoryRepository
from app.repositories.memory_repository import PostgresMemoryRepository
from app.repositories.task_repository import PostgresTaskRepository


def _memory_to_result(memory, rank: float) -> SearchResult:
    return SearchResult(
        id=memory.id,
        type="memory",
        title=memory.content[:80],
        content=memory.content,
        relevance=rank,
        created_at=memory.created_at,
        target_url="/memory",
    )


def _task_to_result(task, rank: float) -> SearchResult:
    return SearchResult(
        id=task.id,
        type="task",
        title=task.title,
        content=task.description,
        relevance=rank,
        created_at=task.created_at,
        target_url="/tasks",
    )


def _document_to_result(document, rank: float) -> SearchResult:
    return SearchResult(
        id=document.id,
        type="document",
        title=document.title,
        content=document.description,
        relevance=rank,
        created_at=document.created_at,
        target_url="/documents",
    )


def _inventory_to_result(item, rank: float) -> SearchResult:
    return SearchResult(
        id=item.id,
        type="inventory",
        title=item.name,
        content=item.description,
        relevance=rank,
        created_at=item.created_at,
        target_url="/inventory",
    )


class SearchService:
    def __init__(
        self,
        memory_repo: PostgresMemoryRepository,
        task_repo: PostgresTaskRepository,
        document_repo: PostgresDocumentRepository,
        inventory_repo: PostgresInventoryRepository,
    ):
        self._memory_repo = memory_repo
        self._task_repo = task_repo
        self._document_repo = document_repo
        self._inventory_repo = inventory_repo

    async def search(
        self, query: str, *, user_id: uuid.UUID, limit_per_type: int = 20
    ) -> dict[str, list[SearchResult]]:
        empty = {"memory": [], "tasks": [], "documents": [], "inventory": []}
        if not query or not query.strip():
            return empty

        q = query.strip()

        memory_hits = await self._memory_repo.search_with_rank(
            q, user_id=user_id, limit=limit_per_type
        )
        task_hits = await self._task_repo.search_with_rank(
            q, user_id=user_id, limit=limit_per_type
        )
        document_hits = await self._document_repo.search_with_rank(
            q, user_id=user_id, limit=limit_per_type
        )
        inventory_hits = await self._inventory_repo.search_with_rank(
            q, user_id=user_id, limit=limit_per_type
        )

        return {
            "memory": [_memory_to_result(m, r) for m, r in memory_hits],
            "tasks": [_task_to_result(t, r) for t, r in task_hits],
            "documents": [_document_to_result(d, r) for d, r in document_hits],
            "inventory": [_inventory_to_result(i, r) for i, r in inventory_hits],
        }


def get_search_service(session: AsyncSession = Depends(get_db_session)) -> SearchService:
    return SearchService(
        memory_repo=PostgresMemoryRepository(session),
        task_repo=PostgresTaskRepository(session),
        document_repo=PostgresDocumentRepository(session),
        inventory_repo=PostgresInventoryRepository(session),
    )
