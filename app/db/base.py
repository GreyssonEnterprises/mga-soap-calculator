"""SQLAlchemy async database setup"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create async engine.
#
# pool_pre_ping=True emits a lightweight `SELECT 1` before handing a
# connection back to application code, catching connections that went stale
# between uses (firewall idle timeouts, server restarts, load-balancer
# recycles). Without it, the first query after an idle period fails with an
# OperationalError that the caller has to handle.
#
# pool_recycle bounds connection lifetime in seconds. 3600s (1h) is well
# below typical idle-kill thresholds (Postgres `idle_in_transaction_session_timeout`
# defaults and cloud LB TCP idle timeouts), so connections rotate out
# before any upstream silently drops them.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""

    pass


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
