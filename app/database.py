import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings

engine = create_async_engine(url=settings.DATABASE_URL_asyncpg)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_models():
    async with engine.begin() as conn: #Core connection, where Data Defenition Language can be executed(CREATE, INSERT, UPDATE)
        await conn.run_sync(Base.metadata.create_all)

