"""Document API — protected: every endpoint requires authentication (W12), scoped to the current user."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.document import DocumentCreate, DocumentOut, DocumentUpdate
from app.domain.timeline.entity import TimelineEventType
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.document_service import DocumentService, get_document_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> DocumentOut:
    document = await service.create_document(user_id=current_user.id, **payload.model_dump())
    await timeline.record(
        event_type=TimelineEventType.DOCUMENT_CREATED,
        entity_type="document",
        entity_id=document.id,
        title=document.title,
        user_id=current_user.id,
    )
    return DocumentOut.model_validate(document)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentOut]:
    documents = await service.list_documents(
        user_id=current_user.id, category=category, limit=limit, offset=offset
    )
    return [DocumentOut.model_validate(d) for d in documents]


@router.get("/search", response_model=list[DocumentOut])
async def search_documents(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentOut]:
    documents = await service.search_documents(q, user_id=current_user.id, limit=limit)
    return [DocumentOut.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentOut:
    document = await service.get_document(document_id, user_id=current_user.id)
    return DocumentOut.model_validate(document)


@router.put("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentOut:
    document = await service.update_document(
        document_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        tags=payload.tags,
        expiry_date=payload.expiry_date,
        expiry_date_provided=payload.expiry_date_provided,
    )
    return DocumentOut.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> None:
    await service.delete_document(document_id, user_id=current_user.id)
