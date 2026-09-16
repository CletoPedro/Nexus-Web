"""User service. DI factory lives here, same rationale as other modules."""
from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.session import get_db_session
from app.domain.users.entity import User
from app.domain.users.repository import UserRepository
from app.repositories.user_repository import PostgresUserRepository
from app.security.hashing import hash_password


class UserService:
    def __init__(self, repository: UserRepository):
        self._repo = repository

    async def create_user(
        self, *, email: str, password: str, must_change_password: bool = False
    ) -> User:
        if not email or "@" not in email:
            raise ValidationError("A valid email is required.")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        existing = await self._repo.get_by_email(email)
        if existing is not None:
            raise ConflictError(f"A user with email {email} already exists.")
        user = User(
            email=email.strip().lower(),
            hashed_password=hash_password(password),
            must_change_password=must_change_password,
        )
        return await self._repo.create(user)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found.")
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self._repo.get_by_email(email)


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    repository = PostgresUserRepository(session)
    return UserService(repository)
