"""
Health endpoints. `/health` is a pure liveness check with no dependencies.
`/health/db` performs a real database round-trip.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - reported, not swallowed
        return {"status": "error", "message": str(exc)}
