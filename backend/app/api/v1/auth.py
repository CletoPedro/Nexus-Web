"""
Auth API — login, logout, current-user. Sets/clears an httpOnly session
cookie; never returns the token in the response body (no localStorage
usage on the frontend is possible even by mistake, since the token is
never exposed to JavaScript).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.api.v1.schemas.auth import LoginRequest, UserOut
from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.domain.users.entity import User
from app.security.dependencies import get_current_user
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
async def login(
    payload: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> UserOut:
    user = await service.authenticate(email=payload.email, password=payload.password)
    if user is None:
        # Deliberately identical error for "no such user" and "wrong
        # password" — do not reveal which one it was.
        raise ValidationError("Incorrect email or password.")

    settings = get_settings()
    token = service.issue_token(user)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
