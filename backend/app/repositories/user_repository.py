"""Postgres implementation of UserRepository."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import UserModel
from app.domain.users.entity import User
from app.domain.users.repository import UserRepository


def _to_entity(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        hashed_password=row.hashed_password,
        is_active=row.is_active,
        must_change_password=row.must_change_password,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        row = UserModel(
            id=user.id,
            email=user.email.lower(),
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            must_change_password=user.must_change_password,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        row = await self._session.get(UserModel, user_id)
        if row is None or row.deleted_at is not None:
            return None
        return _to_entity(row)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email.lower(), UserModel.deleted_at.is_(None)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def update(self, user: User) -> User:
        row = await self._session.get(UserModel, user.id)
        if row is None or row.deleted_at is not None:
            raise ValueError(f"User {user.id} not found")
        row.email = user.email.lower()
        row.hashed_password = user.hashed_password
        row.is_active = user.is_active
        row.must_change_password = user.must_change_password
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)
