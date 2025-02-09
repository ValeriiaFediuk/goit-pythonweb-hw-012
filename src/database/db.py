import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DB_URL)

async def get_db():
    """
    Provides an asynchronous database session for dependency injection.

    This function uses the `DatabaseSessionManager` to yield a session that can be used
    in FastAPI endpoint functions for interacting with the database.

    Yields:
        AsyncSession: A session for executing database queries and transactions.
    """
    async with sessionmanager.session() as session:
        yield session
