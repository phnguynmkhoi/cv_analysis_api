from functools import lru_cache
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

@lru_cache(maxsize=None)
def _session_factory(
    username: str,
    password: str,
    host: str,
    db: str,
) -> async_sessionmaker[AsyncSession]:
    dsn = f"postgresql+asyncpg://{username}:{password}@{host}/{db}"
    engine = create_async_engine(
        dsn,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

@asynccontextmanager
async def get_db(
    username: str,
    password: str,
    host: str = "localhost:5432",
    db: str = "cvdb",
) -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous DB session provider.

    Example for FastAPI:
        from functools import partial
        from fastapi import Depends

        db_dep = partial(
            get_db,
            username="cvadmin",
            password="cvpassword",
            host="localhost:5432",
            db="cvdb"
        )

        @app.get("/people")
        async def list_people(db: AsyncSession = Depends(db_dep)):
            ...
    """
    SessionLocal = _session_factory(username, password, host, db)

    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise Exception(str(e))