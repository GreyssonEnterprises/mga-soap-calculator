"""
Colorant schemas for natural soap color recommendations.

Handles color filtering by 9 color families.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ColorantListItem(BaseModel):
    """Individual colorant in list response"""
    id: str
    name: str
    botanical_name: Optional[str] = Field(None, description="Scientific botanical name", alias="botanical")
    color_category: str = Field(..., description="Color family", alias="category")
    usage_rate: Optional[str] = Field(None, description="Usage rate guidance", alias="usage")
    method: Optional[str] = Field(None, description="Application method")
    color_range_description: Optional[str] = Field(None, description="Color range achievable", alias="color_range")
    warnings: Optional[str] = Field(None, description="Usage warnings")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        from_attributes = True
        populate_by_name = True


class ColorantListResponse(BaseModel):
    """Paginated list of colorants with color family filtering"""
    colorants: List[ColorantListItem]
    total_count: int = Field(..., description="Total matching colorants")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="More results available")
