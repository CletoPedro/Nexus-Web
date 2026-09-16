"""Inventory API — protected: every endpoint requires authentication (W12), scoped to the current user."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
)
from app.domain.timeline.entity import TimelineEventType
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.inventory_service import InventoryService, get_inventory_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: InventoryItemCreate,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> InventoryItemOut:
    item = await service.create_item(user_id=current_user.id, **payload.model_dump())
    await timeline.record(
        event_type=TimelineEventType.INVENTORY_CREATED,
        entity_type="inventory_item",
        entity_id=item.id,
        title=item.name,
        user_id=current_user.id,
    )
    return InventoryItemOut.model_validate(item)


@router.get("", response_model=list[InventoryItemOut])
async def list_items(
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemOut]:
    items = await service.list_items(
        user_id=current_user.id, category=category, location=location, limit=limit, offset=offset
    )
    return [InventoryItemOut.model_validate(i) for i in items]


@router.get("/search", response_model=list[InventoryItemOut])
async def search_items(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemOut]:
    items = await service.search_items(q, user_id=current_user.id, limit=limit)
    return [InventoryItemOut.model_validate(i) for i in items]


@router.get("/{item_id}", response_model=InventoryItemOut)
async def get_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemOut:
    item = await service.get_item(item_id, user_id=current_user.id)
    return InventoryItemOut.model_validate(item)


@router.put("/{item_id}", response_model=InventoryItemOut)
async def update_item(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> InventoryItemOut:
    item = await service.update_item(
        item_id,
        user_id=current_user.id,
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
        user_id=current_user.id,
    )
    return InventoryItemOut.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service),
) -> None:
    await service.delete_item(item_id, user_id=current_user.id)
