"""
Memory API — create, edit, delete, retrieve, list, search. Works without
any AI, per Phase W1/W4.5. Protected: every endpoint requires
authentication (W12), and every operation is scoped to the current user.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.memory import MemoryCreate, MemoryOut, MemoryUpdate
from app.domain.timeline.entity import TimelineEventType
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.memory_service import MemoryService, get_memory_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/memories", tags=["memory"])


@router.post("", response_model=MemoryOut, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> MemoryOut:
    memory = await service.create_memory(
        user_id=current_user.id,
        content=payload.content,
        tags=payload.tags,
        metadata=payload.metadata,
    )
    await timeline.record(
        event_type=TimelineEventType.MEMORY_CREATED,
        entity_type="memory",
        entity_id=memory.id,
        title=memory.content[:200],
        user_id=current_user.id,
    )
    return MemoryOut.model_validate(memory)


@router.get("", response_model=list[MemoryOut])
async def list_memories(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
) -> list[MemoryOut]:
    memories = await service.list_memories(user_id=current_user.id, limit=limit, offset=offset)
    return [MemoryOut.model_validate(m) for m in memories]


@router.get("/search", response_model=list[MemoryOut])
async def search_memories(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
) -> list[MemoryOut]:
    memories = await service.search_memories(q, user_id=current_user.id, limit=limit)
    return [MemoryOut.model_validate(m) for m in memories]


@router.get("/{memory_id}", response_model=MemoryOut)
async def get_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
) -> MemoryOut:
    memory = await service.get_memory(memory_id, user_id=current_user.id)
    return MemoryOut.model_validate(memory)


@router.put("/{memory_id}", response_model=MemoryOut)
async def update_memory(
    memory_id: uuid.UUID,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
) -> MemoryOut:
    memory = await service.update_memory(
        memory_id,
        user_id=current_user.id,
        content=payload.content,
        tags=payload.tags,
        metadata=payload.metadata,
    )
    return MemoryOut.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
) -> None:
    await service.delete_memory(memory_id, user_id=current_user.id)
