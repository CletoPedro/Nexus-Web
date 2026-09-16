"""
Inventory service. Validates document_id references a real document
belonging to the same user (W12: cross-user linking must never be
possible, not even by referencing another user's document id).
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db_session
from app.domain.inventory.entity import InventoryItem
from app.domain.inventory.repository import InventoryRepository
from app.repositories.document_repository import PostgresDocumentRepository
from app.repositories.inventory_repository import PostgresInventoryRepository


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository,
        document_repository: PostgresDocumentRepository | None = None,
    ):
        self._repo = repository
        self._documents = document_repository

    async def _validate_document_reference(
        self, document_id: uuid.UUID | None, *, user_id: uuid.UUID
    ) -> None:
        if document_id is None:
            return
        if self._documents is None:
            return
        document = await self._documents.get(document_id, user_id=user_id)
        if document is None:
            raise ValidationError(f"Referenced document {document_id} does not exist.")

    async def create_item(
        self,
        *,
        user_id: uuid.UUID,
        name: str,
        description: str = "",
        category: str = "",
        location: str = "",
        quantity: int = 1,
        purchase_date: date | None = None,
        purchase_price: Decimal | None = None,
        serial_number: str = "",
        document_id: uuid.UUID | None = None,
    ) -> InventoryItem:
        if not name or not name.strip():
            raise ValidationError("Inventory item name cannot be empty.")
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        await self._validate_document_reference(document_id, user_id=user_id)
        item = InventoryItem(
            name=name.strip(),
            user_id=user_id,
            description=description.strip() if description else "",
            category=category.strip() if category else "",
            location=location.strip() if location else "",
            quantity=quantity,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            serial_number=serial_number,
            document_id=document_id,
        )
        return await self._repo.create(item)

    async def get_item(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> InventoryItem:
        item = await self._repo.get(item_id, user_id=user_id)
        if item is None:
            raise NotFoundError(f"Inventory item {item_id} not found.")
        return item

    async def list_items(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        location: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InventoryItem]:
        return await self._repo.list_all(
            user_id=user_id, category=category, location=location, limit=limit, offset=offset
        )

    async def update_item(
        self,
        item_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        name: str,
        description: str | None = None,
        category: str | None = None,
        location: str | None = None,
        quantity: int | None = None,
        document_id: uuid.UUID | None = None,
        document_id_provided: bool = False,
    ) -> InventoryItem:
        if not name or not name.strip():
            raise ValidationError("Inventory item name cannot be empty.")
        if quantity is not None and quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        existing = await self.get_item(item_id, user_id=user_id)
        existing.name = name.strip()
        if description is not None:
            existing.description = description.strip()
        if category is not None:
            existing.category = category.strip()
        if location is not None:
            existing.location = location.strip()
        if quantity is not None:
            existing.quantity = quantity
        if document_id_provided:
            await self._validate_document_reference(document_id, user_id=user_id)
            existing.document_id = document_id
        return await self._repo.update(existing)

    async def delete_item(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        await self.get_item(item_id, user_id=user_id)
        await self._repo.delete(item_id, user_id=user_id)

    async def search_items(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[InventoryItem]:
        if not query or not query.strip():
            return []
        return await self._repo.search(query.strip(), user_id=user_id, limit=limit)


def get_inventory_service(
    session: AsyncSession = Depends(get_db_session),
) -> InventoryService:
    repository = PostgresInventoryRepository(session)
    document_repository = PostgresDocumentRepository(session)
    return InventoryService(repository, document_repository)
