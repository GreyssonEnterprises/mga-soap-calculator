"""
Additive-specific schemas for smart calculator recommendations.

These schemas handle usage recommendations, warnings, and instructions.
"""
from typing import List, Optional, Dict
from decimal import Decimal
from pydantic import BaseModel, Field


class UsageRecommendation(BaseModel):
    """Usage recommendation for a specific level (light/standard/heavy)"""
    amount_g: float = Field(..., description="Recommended amount in grams")
    amount_oz: float = Field(..., description="Recommended amount in ounces")
    usage_percentage: float = Field(..., description="Usage rate as % of batch weight")


class AdditiveRecommendationResponse(BaseModel):
    """Complete additive recommendation with all usage levels and instructions"""
    id: str
    common_name: str
    inci_name: str
    batch_size_g: float = Field(..., description="Requested batch size in grams")

    recommendations: Dict[str, UsageRecommendation] = Field(
        ...,
        description="Usage recommendations: light, standard, heavy"
    )

    when_to_add: Optional[str] = Field(None, description="When to add to batch")
    preparation_instructions: Optional[str] = Field(None, description="How to prepare")

    warnings: List[str] = Field(
        default_factory=list,
        description="Safety and usage warnings"
    )

    quality_effects: Dict[str, float] = Field(
        ...,
        description="Effects on soap quality metrics"
    )


class AdditiveListItem(BaseModel):
    """Individual additive in filtered list response"""
    id: str
    common_name: str
    inci_name: str
    category: Optional[str] = Field(None, description="Additive category")
    usage_rate_min_pct: Optional[Decimal] = Field(None, description="Minimum usage %")
    usage_rate_max_pct: Optional[Decimal] = Field(None, description="Maximum usage %")
    usage_rate_standard_pct: Optional[Decimal] = Field(None, description="Standard usage %")
    when_to_add: Optional[str] = Field(None, description="When to add")

    class Config:
        from_attributes = True


class AdditiveListResponse(BaseModel):
    """Paginated list of additives with category filtering"""
    additives: List[AdditiveListItem]
    total_count: int = Field(..., description="Total matching additives")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="More results available")
