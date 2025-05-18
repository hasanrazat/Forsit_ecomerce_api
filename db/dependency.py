from sqlalchemy.ext.asyncio import AsyncSession

from .session import AsyncSessionMaker
from instance.config import config


from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions.
    Uses async context manager for proper session lifecycle.
    """
    async with AsyncSessionMaker() as db:
        db.sync_session.set_bind_key(config.APP_ENVIRONMENT)
        yield db

