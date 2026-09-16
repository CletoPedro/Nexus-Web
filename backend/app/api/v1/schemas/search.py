"""Pydantic schemas for the Global Search API."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SearchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    title: str
    content: str
    relevance: float
    created_at: datetime | None
    target_url: str


class SearchResponse(BaseModel):
    query: str
    total: int
    memory: list[SearchResultOut]
    tasks: list[SearchResultOut]
    documents: list[SearchResultOut]
    inventory: list[SearchResultOut]
