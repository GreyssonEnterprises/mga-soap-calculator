"""
Resource discovery endpoints for oils.

Provides public access to reference data for recipe formulation.
No authentication required - this is public reference information.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.oil import Oil
from app.schemas.resource import (
    OilListItem,
    OilListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["resources"])


@router.get("/oils", response_model=OilListResponse)
async def list_oils(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: str | None = Query(None, description="Search by common name or INCI name"),
    sort_by: Literal["common_name", "ins_value", "iodine_value"] = Query(
        "common_name", description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
) -> OilListResponse:
    """
    List available oils with pagination and filtering.

    Returns complete oil properties including SAP values, fatty acids,
    and quality contributions for recipe formulation.

    Query Parameters:
        limit: Items per page (1-100, default 50)
        offset: Pagination offset (default 0)
        search: Case-insensitive search on common_name or inci_name
        sort_by: Field to sort by (common_name, ins_value, iodine_value)
        sort_order: Sort direction (asc, desc)

    Returns:
        Paginated list of oils with metadata
    """
    # Build base query
    query = select(Oil)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(Oil.common_name.ilike(search_pattern), Oil.inci_name.ilike(search_pattern))
        )

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_query)).scalar() or 0

    # Apply sorting
    sort_column = getattr(Oil, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    oils = result.scalars().all()

    # Build response
    return OilListResponse(
        oils=[OilListItem.from_orm(oil) for oil in oils],
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total_count,
    )
