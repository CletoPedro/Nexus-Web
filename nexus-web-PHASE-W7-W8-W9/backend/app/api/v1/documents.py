"""Document API — create, edit, delete, retrieve, list (+category filter), search."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.document import DocumentCreate, DocumentOut, DocumentUpdate
from app.domain.timeline.entity import TimelineEventType
from app.services.document_service import DocumentService, get_document_service
from app.services.timeline_service import TimelineService, get_timeline_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
    timeline: TimelineService = Depends(get_timeline_service),
) -> DocumentOut:
    document = await service.create_document(**payload.model_dump())
    await timeline.record(
        event_type=TimelineEventType.DOCUMENT_CREATED,
        entity_type="document",
        entity_id=document.id,
        title=document.title,
    )
    return DocumentOut.model_validate(document)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentOut]:
    documents = await service.list_documents(category=category, limit=limit, offset=offset)
    return [DocumentOut.model_validate(d) for d in documents]


@router.get("/search", response_model=list[DocumentOut])
async def search_documents(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentOut]:
    documents = await service.search_documents(q, limit=limit)
    return [DocumentOut.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> DocumentOut:
    document = await service.get_document(document_id)
    return DocumentOut.model_validate(document)


@router.put("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentOut:
    document = await service.update_document(
        document_id,
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
    service: DocumentService = Depends(get_document_service),
) -> None:
    await service.delete_document(document_id)
