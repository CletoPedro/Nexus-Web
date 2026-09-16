"""
Timeline API — read-only feed aggregating events across Memory, Tasks,
Documents, and Inventory. Protected: requires authentication, scoped to
the current user.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.timeline import TimelineEventOut
from app.domain.timeline.entity import TimelineEventType
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("", response_model=list[TimelineEventOut])
async def list_timeline(
    event_type: TimelineEventType | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service),
) -> list[TimelineEventOut]:
    events = await service.list_events(
        user_id=current_user.id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return [TimelineEventOut.model_validate(e) for e in events]


@router.get("/search", response_model=list[TimelineEventOut])
async def search_timeline(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service),
) -> list[TimelineEventOut]:
    events = await service.search_events(q, user_id=current_user.id, limit=limit)
    return [TimelineEventOut.model_validate(e) for e in events]
