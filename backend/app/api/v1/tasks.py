"""
Task API — create, edit, delete, retrieve, list (with filters), search,
and a dedicated status-transition endpoint enforcing valid transitions.
Protected: every endpoint requires authentication (W12), scoped to the
current user.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.task import TaskCreate, TaskOut, TaskStatusUpdate, TaskUpdate
from app.domain.tasks.entity import TaskPriority, TaskStatus
from app.domain.timeline.entity import TimelineEventType
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.task_service import TaskService, get_task_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> TaskOut:
    task = await service.create_task(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    await timeline.record(
        event_type=TimelineEventType.TASK_CREATED,
        entity_type="task",
        entity_id=task.id,
        title=task.title,
        user_id=current_user.id,
    )
    return TaskOut.model_validate(task)


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = Query(default=None),
    overdue: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> list[TaskOut]:
    tasks = await service.list_tasks(
        user_id=current_user.id,
        status=status_filter,
        priority=priority,
        overdue_only=overdue,
        limit=limit,
        offset=offset,
    )
    return [TaskOut.model_validate(t) for t in tasks]


@router.get("/search", response_model=list[TaskOut])
async def search_tasks(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> list[TaskOut]:
    tasks = await service.search_tasks(q, user_id=current_user.id, limit=limit)
    return [TaskOut.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskOut:
    task = await service.get_task(task_id, user_id=current_user.id)
    return TaskOut.model_validate(task)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskOut:
    task = await service.update_task(
        task_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        due_date_provided=payload.due_date_provided,
    )
    return TaskOut.model_validate(task)


@router.put("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
    task_id: uuid.UUID,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> TaskOut:
    task = await service.set_status(task_id, payload.status, user_id=current_user.id)
    if payload.status == TaskStatus.DONE:
        await timeline.record(
            event_type=TimelineEventType.TASK_COMPLETED,
            entity_type="task",
            entity_id=task.id,
            title=task.title,
            user_id=current_user.id,
        )
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete_task(task_id, user_id=current_user.id)
