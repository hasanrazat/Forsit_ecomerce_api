# scripts/init_mysql_db.py

from instance.config import config
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base  # import all your models in __init__.py
import asyncio

DATABASE_URL = config.PROD_DB_CONFIG.PROD_CONN_STRING.format(
    username=config.PROD_DB_CONFIG.PROD_DB_USERNAME,
    password=config.PROD_DB_CONFIG.PROD_DB_PASSWORD,
    host=config.PROD_DB_CONFIG.PROD_DB_HOST,
    port=config.PROD_DB_CONFIG.PROD_DB_PORT,
    database=config.PROD_DB_CONFIG.PROD_DB_DATABASE,
)

engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
