from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


# SQLite database file stored in this project folder.
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# Create the asynchronous database engine.
engine = create_async_engine(DATABASE_URL, echo=False)

# Create a new database session when an API request needs one.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all database models.
class Base(DeclarativeBase):
    pass


# Provide a database session to an API request.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session