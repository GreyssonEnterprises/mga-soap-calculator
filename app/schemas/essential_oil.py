"""
Essential oil schemas for scent recommendations and max usage rates.

Handles safe usage calculations and blending guidance.
"""
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class EssentialOilRecommendationResponse(BaseModel):
    """Essential oil recommendation with max safe usage"""
    id: str
    common_name: str
    botanical_name: Optional[str] = Field(None, description="Scientific name")
    batch_size_g: float = Field(..., description="Requested batch size in grams")

    amount_g: float = Field(..., description="Recommended amount in grams at max safe rate")
    amount_oz: float = Field(..., description="Recommended amount in ounces")
    usage_percentage: float = Field(..., description="Max safe usage rate as %")

    scent_profile: Optional[str] = Field(None, description="Scent characteristics")
    note: Optional[str] = Field(None, description="Fragrance note: top, middle, or base")
    category: Optional[str] = Field(None, description="Scent category")

    blends_with: Optional[List[str]] = Field(
        None,
        description="Essential oils that blend well"
    )

    warnings: Optional[str] = Field(None, description="Safety warnings")


class EssentialOilListItem(BaseModel):
    """Individual essential oil in list response"""
    id: str
    name: str = Field(..., alias="common_name", description="Common name of essential oil")
    botanical_name: Optional[str] = Field(None, description="Scientific name")
    max_usage_rate_pct: Decimal = Field(..., description="Max safe usage %")
    scent_profile: Optional[str] = Field(None, description="Scent characteristics")
    note: Optional[str] = Field(None, description="Fragrance note")
    category: Optional[str] = Field(None, description="Scent category")

    class Config:
        from_attributes = True
        populate_by_name = True


class EssentialOilListResponse(BaseModel):
    """Paginated list of essential oils"""
    essential_oils: List[EssentialOilListItem]
    total_count: int = Field(..., description="Total matching essential oils")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="More results available")
