"""
Essential oil endpoints for safe usage recommendations.

Provides max safe usage calculations and blending guidance.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api._pagination import paginate_query
from app.db import get_db
from app.models.essential_oil import EssentialOil
from app.schemas.essential_oil import (
    EssentialOilListItem,
    EssentialOilListResponse,
    EssentialOilRecommendationResponse,
)

router = APIRouter(prefix="/api/v1", tags=["essential_oils"])


@router.get("/essential-oils", response_model=EssentialOilListResponse)
async def list_essential_oils(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: str | None = Query(None, description="Search by common name or botanical name"),
    category: Literal["citrus", "floral", "herbaceous", "woody", "spicy"] | None = Query(
        None, description="Filter by scent category"
    ),
    note: Literal["top", "middle", "base"] | None = Query(
        None, description="Filter by fragrance note"
    ),
    sort_by: Literal["common_name", "max_usage_rate_pct"] = Query(
        "common_name", description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
) -> EssentialOilListResponse:
    """
    List available essential oils with pagination and filtering.

    Returns essential oils with max safe usage rates, scent profiles,
    and blending recommendations.

    Query Parameters:
        limit: Items per page (1-100, default 50)
        offset: Pagination offset (default 0)
        search: Case-insensitive search on common_name or botanical_name
        category: Filter by scent category (citrus, floral, herbaceous, etc.)
        note: Filter by fragrance note (top, middle, base)
        sort_by: Field to sort by (common_name, max_usage_rate_pct)
        sort_order: Sort direction (asc, desc)

    Returns:
        Paginated list of essential oils with metadata
    """
    query = select(EssentialOil)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                EssentialOil.common_name.ilike(search_pattern),
                EssentialOil.botanical_name.ilike(search_pattern),
            )
        )

    if category:
        query = query.where(EssentialOil.category == category)

    if note:
        query = query.where(EssentialOil.note == note)

    essential_oils, total_count, has_more = await paginate_query(
        db,
        query,
        sort_column=getattr(EssentialOil, sort_by),
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    return EssentialOilListResponse(
        essential_oils=[EssentialOilListItem.model_validate(eo) for eo in essential_oils],
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


@router.get("/essential-oils/{eo_id}/recommend", response_model=EssentialOilRecommendationResponse)
async def recommend_essential_oil(
    eo_id: str,
    batch_size_g: float = Query(..., ge=0.1, description="Batch size in grams"),
    db: AsyncSession = Depends(get_db),
) -> EssentialOilRecommendationResponse:
    """
    Calculate essential oil amount at max safe usage rate.

    Provides recommended amount based on CPSR-validated maximum usage rates
    with scent profile and blending suggestions.

    Path Parameters:
        eo_id: Unique identifier for essential oil

    Query Parameters:
        batch_size_g: Batch size in grams (must be > 0)

    Returns:
        Recommendation with safe usage amount and blending guidance

    Raises:
        404: Essential oil not found
        422: Invalid batch_size_g
    """
    # Fetch essential oil from database
    query = select(EssentialOil).where(EssentialOil.id == eo_id)
    result = await db.execute(query)
    eo = result.scalar_one_or_none()

    if not eo:
        raise HTTPException(status_code=404, detail=f"Essential oil '{eo_id}' not found")

    # Calculate amount at max safe usage rate
    # Formula: (batch_size_g × max_usage_rate_pct) / 100
    amount_g = round((batch_size_g * float(eo.max_usage_rate_pct)) / 100, 3)
    amount_oz = round(amount_g / 28.35, 2)

    # Convert warnings array to single string if present
    warnings_text = None
    if eo.warnings and isinstance(eo.warnings, list):
        warnings_text = "; ".join(eo.warnings)
    elif eo.warnings and isinstance(eo.warnings, str):
        warnings_text = eo.warnings

    # Build response
    return EssentialOilRecommendationResponse(
        id=eo.id,
        common_name=eo.common_name,
        botanical_name=eo.botanical_name,
        batch_size_g=batch_size_g,
        amount_g=amount_g,
        amount_oz=amount_oz,
        usage_percentage=float(eo.max_usage_rate_pct),
        scent_profile=eo.scent_profile,
        note=eo.note,
        category=eo.category,
        blends_with=eo.blends_with,
        warnings=warnings_text,
    )
