"""
Additive endpoints for smart calculator recommendations.

Provides usage recommendations with light/standard/heavy options and warnings.
"""
from typing import Optional, Literal, List, Dict
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.additive import Additive
from app.schemas.additive import (
    AdditiveListResponse,
    AdditiveListItem,
    AdditiveRecommendationResponse,
    UsageRecommendation,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["additives"]
)


@router.get("/additives", response_model=AdditiveListResponse)
async def list_additives(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search by common name or INCI name"),
    category: Optional[Literal["exfoliant", "hardener", "lather_booster", "skin_benefit", "clay"]] = Query(
        None,
        description="Filter by category"
    ),
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

    Returns additives with usage rates, categories, and preparation instructions
    for smart calculator recommendations.

    Query Parameters:
        limit: Items per page (1-100, default 50)
        offset: Pagination offset (default 0)
        search: Case-insensitive search on common_name or inci_name
        category: Filter by category (exfoliant, hardener, lather_booster, etc.)
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

    # Apply category filter
    if category:
        query = query.where(Additive.category == category)

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


@router.get("/additives/{additive_id}/recommend", response_model=AdditiveRecommendationResponse)
async def recommend_additive(
    additive_id: str,
    batch_size_g: float = Query(..., ge=0.1, description="Batch size in grams"),
    db: AsyncSession = Depends(get_db)
) -> AdditiveRecommendationResponse:
    """
    Calculate additive amount recommendations for given batch size.

    Provides light, standard, and heavy usage recommendations with preparation
    instructions and safety warnings.

    Path Parameters:
        additive_id: Unique identifier for additive

    Query Parameters:
        batch_size_g: Batch size in grams (must be > 0)

    Returns:
        Complete recommendation with amounts, instructions, and warnings

    Raises:
        404: Additive not found
        422: Invalid batch_size_g
    """
    # Fetch additive from database
    query = select(Additive).where(Additive.id == additive_id)
    result = await db.execute(query)
    additive = result.scalar_one_or_none()

    if not additive:
        raise HTTPException(status_code=404, detail=f"Additive '{additive_id}' not found")

    # Calculate recommendations for light/standard/heavy usage
    recommendations = {}

    # Light usage (minimum)
    if additive.usage_rate_min_pct:
        light_amount_g = round((batch_size_g * float(additive.usage_rate_min_pct)) / 100, 1)
        recommendations["light"] = UsageRecommendation(
            amount_g=light_amount_g,
            amount_oz=round(light_amount_g / 28.35, 2),
            usage_percentage=float(additive.usage_rate_min_pct)
        )

    # Standard usage
    if additive.usage_rate_standard_pct:
        standard_amount_g = round((batch_size_g * float(additive.usage_rate_standard_pct)) / 100, 1)
        recommendations["standard"] = UsageRecommendation(
            amount_g=standard_amount_g,
            amount_oz=round(standard_amount_g / 28.35, 2),
            usage_percentage=float(additive.usage_rate_standard_pct)
        )

    # Heavy usage (maximum)
    if additive.usage_rate_max_pct:
        heavy_amount_g = round((batch_size_g * float(additive.usage_rate_max_pct)) / 100, 1)
        recommendations["heavy"] = UsageRecommendation(
            amount_g=heavy_amount_g,
            amount_oz=round(heavy_amount_g / 28.35, 2),
            usage_percentage=float(additive.usage_rate_max_pct)
        )

    # Build warnings list from JSONB warnings field
    warnings_list: List[str] = []
    if additive.warnings:
        if additive.warnings.get("accelerates_trace"):
            warnings_list.append("May accelerate trace")
        if additive.warnings.get("causes_overheating"):
            warnings_list.append("Can cause overheating")
        if additive.warnings.get("can_be_scratchy"):
            warnings_list.append("Can be scratchy in final soap")
        if additive.warnings.get("turns_brown"):
            warnings_list.append("May turn brown over time")

    # Build response
    return AdditiveRecommendationResponse(
        id=additive.id,
        common_name=additive.common_name,
        inci_name=additive.inci_name,
        batch_size_g=batch_size_g,
        recommendations=recommendations,
        when_to_add=additive.when_to_add,
        preparation_instructions=additive.preparation_instructions,
        warnings=warnings_list,
        quality_effects=additive.quality_effects or {}
    )
