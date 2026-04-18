"""
Colorant schemas for natural soap color recommendations.

Handles color filtering by 9 color families.
"""

from pydantic import BaseModel, ConfigDict, Field


class ColorantListItem(BaseModel):
    """Individual colorant in list response"""

    id: str
    name: str
    botanical_name: str | None = Field(
        None, description="Scientific botanical name", alias="botanical"
    )
    color_category: str = Field(..., description="Color family", alias="category")
    usage_rate: str | None = Field(None, description="Usage rate guidance", alias="usage")
    method: str | None = Field(None, description="Application method")
    color_range_description: str | None = Field(
        None, description="Color range achievable", alias="color_range"
    )
    warnings: str | None = Field(None, description="Usage warnings")
    notes: str | None = Field(None, description="Additional notes")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ColorantListResponse(BaseModel):
    """Paginated list of colorants with color family filtering"""

    colorants: list[ColorantListItem]
    total_count: int = Field(..., description="Total matching colorants")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="More results available")
