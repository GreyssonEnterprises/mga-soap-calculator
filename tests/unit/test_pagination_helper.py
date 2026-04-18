"""
Unit tests for the shared pagination helper in app/api/_pagination.py.

Covers the paginate_query utility used by list endpoints (oils, additives,
essential oils, colorants) to eliminate the duplicated boilerplate called
out in audit findings CQ-05/CQ-06.

Uses the existing test postgres database (mga_soap_calculator_test) through
a temporary throwaway table, keeping the helper validation close to the
runtime dialect while avoiding overlap with model fixtures.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool

from app.api._pagination import paginate_query
from app.core.config import settings

pytestmark = pytest.mark.asyncio

_TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "/mga_soap_calculator", "/mga_soap_calculator_test"
)


class _Base(DeclarativeBase):
    pass


class _Widget(_Base):
    # Unique per-run table name prevents cross-test collisions if the suite
    # aborts before teardown drops the table.
    __tablename__ = f"pagination_widgets_{uuid.uuid4().hex[:8]}"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """Per-test postgres session populated with widgets.

    Creates a short-lived table on the existing test database, seeds it with
    deterministic fixture data, and drops it after the test. This keeps the
    helper test hermetic without requiring extra DB drivers.
    """
    engine = create_async_engine(_TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_maker() as sess:
            sess.add_all(
                [
                    _Widget(id=1, name="alpha", rank=30),
                    _Widget(id=2, name="bravo", rank=10),
                    _Widget(id=3, name="charlie", rank=20),
                    _Widget(id=4, name="delta", rank=40),
                    _Widget(id=5, name="echo", rank=50),
                ]
            )
            await sess.commit()
            yield sess
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(_Base.metadata.drop_all)
        await engine.dispose()


async def test_paginate_query_returns_all_items_by_default(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=50,
        offset=0,
    )

    assert total == 5
    assert has_more is False
    assert [w.name for w in items] == ["alpha", "bravo", "charlie", "delta", "echo"]


async def test_paginate_query_respects_limit_and_reports_has_more(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=2,
        offset=0,
    )

    assert total == 5
    assert has_more is True
    assert [w.name for w in items] == ["alpha", "bravo"]


async def test_paginate_query_applies_offset(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=2,
        offset=2,
    )

    assert total == 5
    assert has_more is True
    assert [w.name for w in items] == ["charlie", "delta"]


async def test_paginate_query_has_more_false_at_last_page(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=2,
        offset=4,
    )

    assert total == 5
    assert has_more is False
    assert [w.name for w in items] == ["echo"]


async def test_paginate_query_sort_desc(session: AsyncSession) -> None:
    items, _total, _has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.rank,
        sort_order="desc",
        limit=50,
        offset=0,
    )

    assert [w.rank for w in items] == [50, 40, 30, 20, 10]


async def test_paginate_query_total_reflects_filtered_query(session: AsyncSession) -> None:
    filtered = select(_Widget).where(_Widget.rank >= 30)

    items, total, has_more = await paginate_query(
        session,
        filtered,
        sort_column=_Widget.rank,
        sort_order="asc",
        limit=50,
        offset=0,
    )

    # rank >= 30 matches 3 widgets; total must reflect the filter, not the
    # table size. This guards against regressing to `select count from table`.
    assert total == 3
    assert has_more is False
    assert [w.rank for w in items] == [30, 40, 50]


async def test_paginate_query_empty_result(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget).where(_Widget.name == "does-not-exist"),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=50,
        offset=0,
    )

    assert items == []
    assert total == 0
    assert has_more is False


async def test_paginate_query_offset_beyond_total(session: AsyncSession) -> None:
    items, total, has_more = await paginate_query(
        session,
        select(_Widget),
        sort_column=_Widget.name,
        sort_order="asc",
        limit=10,
        offset=100,
    )

    assert items == []
    assert total == 5
    assert has_more is False
