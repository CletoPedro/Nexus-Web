"""
JWT access tokens, carried in an httpOnly cookie (never localStorage —
per W12, "NÃO colocar tokens em localStorage se existir alternativa
segura"). Stateless: there is no server-side session store, so a token
remains valid until it expires even after "logout" clears the cookie.
This is a documented limitation (see PHASE_W12_REPORT.md) — true
server-side revocation would need a token blocklist or session table,
deferred to a future hardening pass.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings


class InvalidTokenError(Exception):
    pass


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> uuid.UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise InvalidTokenError("Invalid or expired session token.") from exc
