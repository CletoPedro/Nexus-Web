"""
get_current_user: the single dependency every protected router uses.
Reads the httpOnly session cookie, verifies the JWT, and confirms the
user still exists and is active in the database (a revoked/deactivated
user is rejected even if their token hasn't expired yet).
"""
from __future__ import annotations

from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NexusError
from app.db.session import get_db_session
from app.domain.users.entity import User
from app.repositories.user_repository import PostgresUserRepository
from app.security.tokens import InvalidTokenError, decode_access_token


class UnauthorizedError(NexusError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> User:
    settings = get_settings()
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        raise UnauthorizedError("Not authenticated.")

    try:
        user_id = decode_access_token(token)
    except InvalidTokenError as exc:
        raise UnauthorizedError("Session expired or invalid. Please log in again.") from exc

    repository = PostgresUserRepository(session)
    user = await repository.get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Session no longer valid. Please log in again.")

    return user
