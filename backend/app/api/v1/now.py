"""
NOW dashboard API (W11) — a single read-only endpoint aggregating what's
relevant right now. Protected: requires authentication, scoped to the
current user.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.now import NowResponse
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.now_service import NowService, get_now_service

router = APIRouter(prefix="/now", tags=["now"])


@router.get("", response_model=NowResponse)
async def get_now(
    recent_limit: int = Query(default=5, ge=1, le=50),
    upcoming_days: int = Query(default=7, ge=1, le=90),
    task_limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: NowService = Depends(get_now_service),
) -> NowResponse:
    snapshot = await service.get_snapshot(
        user_id=current_user.id,
        recent_limit=recent_limit,
        upcoming_days=upcoming_days,
        task_limit=task_limit,
    )
    return NowResponse.model_validate(snapshot, from_attributes=True)
