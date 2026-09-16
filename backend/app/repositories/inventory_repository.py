"""Postgres implementation of InventoryRepository."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.inventory_item import InventoryItemModel
from app.domain.inventory.entity import InventoryItem
from app.domain.inventory.repository import InventoryRepository


def _to_entity(row: InventoryItemModel) -> InventoryItem:
    return InventoryItem(
        id=row.id,
        name=row.name,
        user_id=row.user_id,
        description=row.description,
        category=row.category,
        location=row.location,
        quantity=row.quantity,
        purchase_date=row.purchase_date,
        purchase_price=row.purchase_price,
        serial_number=row.serial_number,
        document_id=row.document_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_row(
        self, item_id: uuid.UUID, *, user_id: uuid.UUID
    ) -> InventoryItemModel | None:
        stmt = select(InventoryItemModel).where(
            InventoryItemModel.id == item_id,
            InventoryItemModel.user_id == user_id,
            InventoryItemModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, item: InventoryItem) -> InventoryItem:
        row = InventoryItemModel(
            id=item.id,
            name=item.name,
            user_id=item.user_id,
            description=item.description,
            category=item.category,
            location=item.location,
            quantity=item.quantity,
            purchase_date=item.purchase_date,
            purchase_price=item.purchase_price,
            serial_number=item.serial_number,
            document_id=item.document_id,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> InventoryItem | None:
        row = await self._get_row(item_id, user_id=user_id)
        return _to_entity(row) if row else None

    async def list_all(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        location: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InventoryItem]:
        stmt = select(InventoryItemModel).where(
            InventoryItemModel.user_id == user_id, InventoryItemModel.deleted_at.is_(None)
        )
        if category:
            stmt = stmt.where(InventoryItemModel.category == category)
        if location:
            stmt = stmt.where(InventoryItemModel.location == location)
        stmt = (
            stmt.order_by(InventoryItemModel.created_at.desc()).limit(limit).offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, item: InventoryItem) -> InventoryItem:
        row = await self._get_row(item.id, user_id=item.user_id)
        if row is None:
            raise ValueError(f"Inventory item {item.id} not found")
        row.name = item.name
        row.description = item.description
        row.category = item.category
        row.location = item.location
        row.quantity = item.quantity
        row.purchase_date = item.purchase_date
        row.purchase_price = item.purchase_price
        row.serial_number = item.serial_number
        row.document_id = item.document_id
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, item_id: uuid.UUID, *, user_id: uuid.UUID) -> None:
        row = await self._get_row(item_id, user_id=user_id)
        if row is None:
            return
        row.deleted_at = func.now()
        await self._session.commit()

    async def search(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[InventoryItem]:
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(InventoryItemModel)
            .where(
                InventoryItemModel.user_id == user_id,
                InventoryItemModel.deleted_at.is_(None),
                InventoryItemModel.search_vector.op("@@")(ts_query),
            )
            .order_by(func.ts_rank(InventoryItemModel.search_vector, ts_query).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def search_with_rank(
        self, query: str, *, user_id: uuid.UUID, limit: int = 50
    ) -> list[tuple[InventoryItem, float]]:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank(InventoryItemModel.search_vector, ts_query).label("rank")
        stmt = (
            select(InventoryItemModel, rank)
            .where(
                InventoryItemModel.user_id == user_id,
                InventoryItemModel.deleted_at.is_(None),
                InventoryItemModel.search_vector.op("@@")(ts_query),
            )
            .order_by(rank.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(_to_entity(row), float(r)) for row, r in result.all()]
