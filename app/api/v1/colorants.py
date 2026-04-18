"""
Colorant endpoints for natural color recommendations.

Provides color filtering by 9 color families.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api._pagination import paginate_query
from app.db import get_db
from app.models.colorant import Colorant
from app.schemas.colorant import (
    ColorantListItem,
    ColorantListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["colorants"])


@router.get("/colorants", response_model=ColorantListResponse)
async def list_colorants(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: str | None = Query(None, description="Search by name or botanical name"),
    color: Literal["yellow", "orange", "pink", "red", "blue", "purple", "brown", "green", "black"]
    | None = Query(None, description="Filter by color category", alias="category"),
    sort_by: Literal["name", "color_category"] = Query("name", description="Field to sort by"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
) -> ColorantListResponse:
    """
    List available colorants with pagination and filtering.

    Returns natural colorants with usage methods, color ranges,
    and safety warnings for 9 color families.

    Query Parameters:
        limit: Items per page (1-100, default 50)
        offset: Pagination offset (default 0)
        search: Case-insensitive search on name or botanical_name
        color: Filter by color category
            (yellow, orange, pink, red, blue, purple, brown, green, black)
        sort_by: Field to sort by (name, color_category)
        sort_order: Sort direction (asc, desc)

    Returns:
        Paginated list of colorants with metadata
    """
    query = select(Colorant)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(Colorant.name.ilike(search_pattern), Colorant.botanical_name.ilike(search_pattern))
        )

    if color:
        query = query.where(Colorant.color_category == color)

    colorants, total_count, has_more = await paginate_query(
        db,
        query,
        sort_column=getattr(Colorant, sort_by),
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    # Colorant list response uses renamed fields, so build items explicitly
    # rather than going through model_validate.
    colorant_items = [
        ColorantListItem(
            id=colorant.id,
            name=colorant.name,
            botanical=colorant.botanical_name,
            category=colorant.color_category,
            usage=colorant.usage_rate,
            method=colorant.method,
            color_range=colorant.color_range_description,
            warnings=colorant.warnings,
            notes=colorant.notes,
        )
        for colorant in colorants
    ]

    return ColorantListResponse(
        colorants=colorant_items,
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )
