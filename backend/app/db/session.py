"""
Async SQLAlchemy engine/session. This is the only module that constructs
the engine — repositories receive a session via dependency injection,
never build their own connection.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# NullPool: asyncpg connections are bound to the event loop they were
# created on. A pooled connection reused from a previous loop (as happens
# under TestClient, which opens a fresh loop per call) raises
# "another operation is in progress". NullPool opens a fresh connection
# per checkout, trading a little latency for correctness across loops.
engine = create_async_engine(
    settings.database_url, echo=settings.debug, future=True, poolclass=NullPool
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped DB session."""
    async with async_session_factory() as session:
        yield session
