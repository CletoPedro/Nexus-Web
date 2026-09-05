"""
Memory API — create, edit, delete, retrieve, list, search. Works without
any AI, per Phase W1/W4.5: this is the first fully usable NEXUS feature.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.memory import MemoryCreate, MemoryOut, MemoryUpdate
from app.domain.timeline.entity import TimelineEventType
from app.services.memory_service import MemoryService, get_memory_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/memories", tags=["memory"])


@router.post("", response_model=MemoryOut, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    service: MemoryService = Depends(get_memory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> MemoryOut:
    memory = await service.create_memory(
        content=payload.content, tags=payload.tags, metadata=payload.metadata
    )
    await timeline.record(
        event_type=TimelineEventType.MEMORY_CREATED,
        entity_type="memory",
        entity_id=memory.id,
        title=memory.content[:200],
    )
    return MemoryOut.model_validate(memory)


@router.get("", response_model=list[MemoryOut])
async def list_memories(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: MemoryService = Depends(get_memory_service),
) -> list[MemoryOut]:
    memories = await service.list_memories(limit=limit, offset=offset)
    return [MemoryOut.model_validate(m) for m in memories]


@router.get("/search", response_model=list[MemoryOut])
async def search_memories(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: MemoryService = Depends(get_memory_service),
) -> list[MemoryOut]:
    memories = await service.search_memories(q, limit=limit)
    return [MemoryOut.model_validate(m) for m in memories]


@router.get("/{memory_id}", response_model=MemoryOut)
async def get_memory(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
) -> MemoryOut:
    memory = await service.get_memory(memory_id)
    return MemoryOut.model_validate(memory)


@router.put("/{memory_id}", response_model=MemoryOut)
async def update_memory(
    memory_id: uuid.UUID,
    payload: MemoryUpdate,
    service: MemoryService = Depends(get_memory_service),
) -> MemoryOut:
    memory = await service.update_memory(
        memory_id,
        content=payload.content,
        tags=payload.tags,
        metadata=payload.metadata,
    )
    return MemoryOut.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    service: MemoryService = Depends(get_memory_service),
) -> None:
    await service.delete_memory(memory_id)
