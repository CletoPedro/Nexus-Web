"""
SearchResult: a normalized representation of a hit from any module. Not
persisted — Global Search has no table of its own; it composes the
existing search_with_rank() methods on Memory/Task/Document/Inventory
repositories, per W10 ("não duplicar lógica de pesquisa").
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    id: uuid.UUID
    type: str  # "memory" | "task" | "document" | "inventory"
    title: str
    content: str
    relevance: float
    created_at: datetime | None
    target_url: str
