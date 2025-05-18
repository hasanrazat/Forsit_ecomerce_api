"""
Contains SQLAlchemy Session Instance
"""
import logging
from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import text

from instance.config import config

logger = logging.getLogger(__name__)


# -----------------------------
# DB Connection Health Checker
# -----------------------------

async def check_db_connection():
    """
    Runs a simple SELECT statement to verify DB connection.
    Should be called in app startup event.
    """
    try:
        engine = config.SQLALCHEMY_ENGINES[config.APP_ENVIRONMENT]
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT DATABASE();"))
            current_db = result.scalar()
            logger.info(f"[DB CHECK] Connected to database: {current_db}")
    except Exception as e:
        logger.error(f"[DB CHECK FAILED] Could not connect to DB: {e}")


# -----------------------------
# Routing Session Class
# -----------------------------

class RoutingSession(Session):
    """
    Responsible for query traffic routing to connection strings defined in SQLALCHEMY_ENGINES.
    """

    bind_key = config.APP_ENVIRONMENT

    def get_bind(self, mapper=None, clause=None, **kw):
        engines = config.SQLALCHEMY_ENGINES

        # Fallback to default if no mapper
        if mapper is None:
            return engines[self.bind_key].sync_engine

        if hasattr(mapper.mapped_table, "info"):
            if "bind_key" in mapper.mapped_table.info:
                self.bind_key = mapper.mapped_table.info["bind_key"]
            return engines[self.bind_key].sync_engine

        return engines["development"].sync_engine

    def set_bind_key(self, bind_key: str):
        self.bind_key = bind_key


# -----------------------------
# Retrying Session with Fallback
# -----------------------------

class RetryingSession(AsyncSession):
    retry_count: int = 3
    fallback_used: bool = False

    async def execute(self, statement, *args, **kwargs):
        retries: int = 0
        engine = self.get_bind()

        while retries < self.retry_count:
            try:
                return await super().execute(statement, *args, **kwargs)
            except (OperationalError, InterfaceError, DBAPIError) as e:
                retries += 1
                engine.dispose()
                logger.warning(f"[DB ERROR] Attempt {retries}/{self.retry_count} failed: {e}")
                if retries == self.retry_count:
                    if config.APP_ENVIRONMENT == "production" and not self.fallback_used:
                        logger.error("[DB FALLBACK] Production DB unreachable. Falling back to SQLite.")
                        self.bind = config.SQLALCHEMY_ENGINES["development"]
                        self.fallback_used = True
                        return await self.execute(statement, *args, **kwargs)
                    else:
                        raise e


# -----------------------------
# AsyncSession Factory
# -----------------------------

AsyncSessionMaker = async_sessionmaker(
    sync_session_class=RoutingSession,
    class_=RetryingSession,
    expire_on_commit=False,
)
