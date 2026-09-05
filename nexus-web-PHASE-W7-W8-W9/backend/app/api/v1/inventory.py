"""Inventory API — create, edit, delete, retrieve, list (+filters), search."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
)
from app.domain.timeline.entity import TimelineEventType
from app.services.inventory_service import InventoryService, get_inventory_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: InventoryItemCreate,
    service: InventoryService = Depends(get_inventory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> InventoryItemOut:
    item = await service.create_item(**payload.model_dump())
    await timeline.record(
        event_type=TimelineEventType.INVENTORY_CREATED,
        entity_type="inventory_item",
        entity_id=item.id,
        title=item.name,
    )
    return InventoryItemOut.model_validate(item)


@router.get("", response_model=list[InventoryItemOut])
async def list_items(
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemOut]:
    items = await service.list_items(
        category=category, location=location, limit=limit, offset=offset
    )
    return [InventoryItemOut.model_validate(i) for i in items]


@router.get("/search", response_model=list[InventoryItemOut])
async def search_items(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemOut]:
    items = await service.search_items(q, limit=limit)
    return [InventoryItemOut.model_validate(i) for i in items]


@router.get("/{item_id}", response_model=InventoryItemOut)
async def get_item(
    item_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemOut:
    item = await service.get_item(item_id)
    return InventoryItemOut.model_validate(item)


@router.put("/{item_id}", response_model=InventoryItemOut)
async def update_item(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    service: InventoryService = Depends(get_inventory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> InventoryItemOut:
    item = await service.update_item(
        item_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        location=payload.location,
        quantity=payload.quantity,
        document_id=payload.document_id,
        document_id_provided=payload.document_id_provided,
    )
    await timeline.record(
        event_type=TimelineEventType.INVENTORY_UPDATED,
        entity_type="inventory_item",
        entity_id=item.id,
        title=item.name,
    )
    return InventoryItemOut.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
) -> None:
    await service.delete_item(item_id)
