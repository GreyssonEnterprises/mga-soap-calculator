"""
Resource discovery endpoints for oils and additives.

Provides public access to reference data for recipe formulation.
No authentication required - this is public reference information.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.oil import Oil
from app.models.additive import Additive
from app.schemas.resource import (
    OilListResponse,
    OilListItem,
    AdditiveListResponse,
    AdditiveListItem
)

router = APIRouter(
    prefix="/api/v1",
    tags=["resources"]
)


@router.get("/oils", response_model=OilListResponse)
async def list_oils(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by common name or INCI name"),
    sort_by: Literal["common_name", "ins_value", "iodine_value"] = Query(
        "common_name",
        description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction"),
    db: AsyncSession = Depends(get_db)
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
            or_(
                Oil.common_name.ilike(search_pattern),
                Oil.inci_name.ilike(search_pattern)
            )
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
        has_more=(offset + limit) < total_count
    )


@router.get("/additives", response_model=AdditiveListResponse)
async def list_additives(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search by common name or INCI name"),
    confidence: Optional[Literal["high", "medium", "low"]] = Query(
        None,
        description="Filter by confidence level"
    ),
    verified_only: bool = Query(False, description="Only show MGA-verified additives"),
    sort_by: Literal["common_name", "confidence_level"] = Query(
        "common_name",
        description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction"),
    db: AsyncSession = Depends(get_db)
) -> AdditiveListResponse:
    """
    List available additives with pagination and filtering.

    Returns complete additive properties including usage guidelines,
    quality effects, and confidence levels for recipe formulation.

    Query Parameters:
        limit: Items per page (1-100, default 50)
        offset: Pagination offset (default 0)
        search: Case-insensitive search on common_name or inci_name
        confidence: Filter by confidence level (high, medium, low)
        verified_only: Only show MGA-verified additives
        sort_by: Field to sort by (common_name, confidence_level)
        sort_order: Sort direction (asc, desc)

    Returns:
        Paginated list of additives with metadata
    """
    # Build base query
    query = select(Additive)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Additive.common_name.ilike(search_pattern),
                Additive.inci_name.ilike(search_pattern)
            )
        )

    # Apply confidence filter
    if confidence:
        query = query.where(Additive.confidence_level == confidence)

    # Apply verified filter
    if verified_only:
        query = query.where(Additive.verified_by_mga == True)

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_query)).scalar() or 0

    # Apply sorting
    sort_column = getattr(Additive, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    additives = result.scalars().all()

    # Build response
    return AdditiveListResponse(
        additives=[AdditiveListItem.from_orm(additive) for additive in additives],
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total_count
    )
