"""
Resource listing response schemas for oils and additives endpoints.

These schemas support pagination, search, and filtering for resource discovery.
"""

from pydantic import BaseModel, Field


class OilListItem(BaseModel):
    """Individual oil in list response with complete properties"""

    id: str
    common_name: str
    inci_name: str
    sap_value_naoh: float = Field(..., description="Grams NaOH per gram of oil")
    sap_value_koh: float = Field(..., description="Grams KOH per gram of oil")
    iodine_value: float = Field(..., description="Measure of unsaturation")
    ins_value: float = Field(..., description="Iodine Number Saponification (hardness indicator)")
    fatty_acids: dict[str, float] = Field(..., description="Percentages of 8 fatty acids")
    quality_contributions: dict[str, float] = Field(
        ..., description="Contribution to 7 quality metrics"
    )

    class Config:
        from_attributes = True


class OilListResponse(BaseModel):
    """Paginated list of oils with metadata"""

    oils: list[OilListItem]
    total_count: int = Field(..., description="Total matching oils before pagination")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether more results exist beyond this page")


class AdditiveListItem(BaseModel):
    """Individual additive in list response with complete properties"""

    id: str
    common_name: str
    inci_name: str
    typical_usage_min_percent: float = Field(
        ..., description="Minimum recommended usage as % of oil weight"
    )
    typical_usage_max_percent: float = Field(
        ..., description="Maximum recommended usage as % of oil weight"
    )
    quality_effects: dict[str, float] = Field(
        ..., description="Absolute modifiers to quality metrics at 2% usage"
    )
    confidence_level: str = Field(..., description="Research confidence: high, medium, low")
    verified_by_mga: bool = Field(..., description="Whether MGA has empirically validated effects")
    safety_warnings: dict[str, str] | None = Field(
        None, description="Optional safety information and usage notes"
    )

    class Config:
        from_attributes = True


class AdditiveListResponse(BaseModel):
    """Paginated list of additives with metadata"""

    additives: list[AdditiveListItem]
    total_count: int = Field(..., description="Total matching additives before pagination")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether more results exist beyond this page")
