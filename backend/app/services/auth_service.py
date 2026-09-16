"""Auth service — verifies credentials and issues access tokens."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.users.entity import User
from app.security.hashing import verify_password
from app.security.tokens import create_access_token
from app.services.user_service import UserService, get_user_service


class AuthService:
    def __init__(self, user_service: UserService):
        self._users = user_service

    async def authenticate(self, *, email: str, password: str) -> User | None:
        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(user.id)


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(get_user_service(session))
