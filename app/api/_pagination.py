"""
Shared pagination helper for list endpoints.

Before this helper existed, four list endpoints (oils, additives, essential
oils, colorants) duplicated the same count-then-page-then-sort block —
~100 lines of boilerplate flagged by audit findings CQ-05 and CQ-06.

Callers supply a partially-built SELECT (already filtered) plus sort + page
parameters, and receive the rows together with the total count and a
has_more flag. Response-shape construction stays in the router so endpoint
contracts remain explicit.
"""

from __future__ import annotations

from typing import Any, Literal, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

SortOrder = Literal["asc", "desc"]

T = TypeVar("T")


async def paginate_query(
    session: AsyncSession,
    query: Select[tuple[T]],
    *,
    sort_column: InstrumentedAttribute[Any] | ColumnElement[Any],
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> tuple[list[T], int, bool]:
    """Execute a paginated, sorted list query.

    Args:
        session: Active async SQLAlchemy session.
        query: Base SELECT with all filters already applied. Must select a
            single mapped entity (e.g. ``select(Oil)``) — the helper returns
            the scalar rows.
        sort_column: Column/attribute to sort by. Taken as-is so the caller
            controls which fields are sortable (prevents arbitrary sort
            injection via user input).
        sort_order: ``"asc"`` or ``"desc"``.
        limit: Max rows to return for this page.
        offset: Rows to skip before the page starts.

    Returns:
        Tuple of ``(items, total_count, has_more)`` where
        ``total_count`` is the unpaginated match count, and ``has_more`` is
        ``True`` if more rows exist beyond this page.
    """
    # Count before ordering/pagination. Wrapping in a subquery keeps all
    # user-supplied WHERE clauses intact while remaining backend-agnostic.
    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await session.execute(count_query)).scalar() or 0

    ordered = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
    paged = ordered.limit(limit).offset(offset)

    result = await session.execute(paged)
    items = list(result.scalars().all())

    has_more = (offset + limit) < total_count
    return items, total_count, has_more
