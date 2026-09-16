"""
Global Search API — searches Memory, Tasks, Documents, and Inventory
simultaneously using each module's existing Postgres full-text search
(no AI, per W10 scope). Protected: requires authentication, scoped to
the current user.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.search import SearchResponse, SearchResultOut
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(default="", description="Search query; empty returns no results"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results per module"),
    current_user: User = Depends(get_current_user),
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    grouped = await service.search(q, user_id=current_user.id, limit_per_type=limit)

    memory = [SearchResultOut.model_validate(r) for r in grouped["memory"]]
    tasks = [SearchResultOut.model_validate(r) for r in grouped["tasks"]]
    documents = [SearchResultOut.model_validate(r) for r in grouped["documents"]]
    inventory = [SearchResultOut.model_validate(r) for r in grouped["inventory"]]

    return SearchResponse(
        query=q,
        total=len(memory) + len(tasks) + len(documents) + len(inventory),
        memory=memory,
        tasks=tasks,
        documents=documents,
        inventory=inventory,
    )
