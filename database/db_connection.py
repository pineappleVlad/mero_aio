from contextlib import asynccontextmanager

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DB_PORT
from sqlalchemy import text, MetaData
from sqlalchemy.orm import sessionmaker

from config import DB_PORT, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base


DB_CONNECTION_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_async_engine(DB_CONNECTION_URL, echo=False)  # False for production
Base = declarative_base()
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
metadata = Base.metadata

@asynccontextmanager
async def get_session() -> AsyncSession:  # depends
    async with async_session() as session:
        yield session


async def init_models() -> None:  # Создание таблиц
    async with engine.begin() as conn:

        await conn.execute(text("DROP TABLE IF EXISTS advertisements CASCADE")) # not production
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS currentsessions CASCADE"))

        if (
            not (await conn.run_sync(engine.dialect.has_table, "advertisement"))
        ):
            await conn.run_sync(Base.metadata.create_all)
