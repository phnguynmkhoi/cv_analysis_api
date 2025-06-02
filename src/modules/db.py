from functools import lru_cache
from typing import Generator, Callable
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

@lru_cache(maxsize=None)
def _session_factory(
    username: str,
    password: str,
    host: str,
    db: str,
) -> sessionmaker:
    dsn = f"postgresql://{username}:{password}@{host}/{db}"  # ❗ No "+asyncpg"
    engine = create_engine(
        dsn,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )
    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

def create_get_db(
    username: str,
    password: str,
    host: str,
    db: str,
) -> Callable[[], Generator[Session, None, None]]:
    SessionLocal = _session_factory(username, password, host, db)

    def get_db() -> Generator[Session, None, None]:
        with SessionLocal() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    return get_db
