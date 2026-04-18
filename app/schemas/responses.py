"""
Response Pydantic models for API (Task 3.1.2)

TDD Evidence: Tests written first in test_response_models.py
Implements spec Section 3.1 response schema.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class OilOutput(BaseModel):
    """Oil output with calculated weights and percentages"""

    id: str
    common_name: str  # Fixed: was 'name', spec requires 'common_name'
    weight_g: float
    percentage: float


class LyeOutput(BaseModel):
    """
    Lye calculation output.

    Feature: KOH/NaOH Purity Support (Spec 002-lye-purity)
    - koh_purity: Echo back purity percentage used in calculation
    - naoh_purity: Echo back purity percentage used in calculation
    - pure_koh_equivalent_g: Theoretical pure KOH amount
    - pure_naoh_equivalent_g: Theoretical pure NaOH amount
    """

    naoh_weight_g: float  # Fixed: was 'naoh_g', spec requires 'naoh_weight_g'
    koh_weight_g: float  # Fixed: was 'koh_g', spec requires 'koh_weight_g'
    total_lye_g: float
    naoh_percent: float
    koh_percent: float
    koh_purity: float
    naoh_purity: float
    pure_koh_equivalent_g: float
    pure_naoh_equivalent_g: float


class AdditiveOutput(BaseModel):
    """Additive output with calculated weights and percentages"""

    id: str
    name: str
    weight_g: float
    percentage: float


class RecipeOutput(BaseModel):
    """Complete normalized recipe with all ingredients"""

    total_oil_weight_g: float
    oils: list[OilOutput]
    lye: LyeOutput
    water_weight_g: float
    water_method: str  # Fixed: Added missing field from spec Section 3.1
    water_method_value: float  # Fixed: Added missing field from spec Section 3.1
    superfat_percent: float
    additives: list[AdditiveOutput]


class QualityMetrics(BaseModel):
    """
    Quality metrics for soap properties.

    Per spec Section 5.3:
    - hardness, cleansing, conditioning, bubbly_lather, creamy_lather
    - longevity, stability
    - iodine, ins (calculated values)
    """

    hardness: float
    cleansing: float
    conditioning: float
    bubbly_lather: float
    creamy_lather: float
    longevity: float
    stability: float
    iodine: float
    ins: float


class AdditiveEffect(BaseModel):
    """Per-additive quality effect breakdown"""

    additive_id: str
    additive_name: str
    effects: dict[str, float]  # Metric name -> absolute change
    confidence: str  # high, medium, low
    verified_by_mga: bool


class FattyAcidProfile(BaseModel):
    """
    Percentage breakdown of 8 fatty acids.

    Per spec Section 5.4:
    - Saturated: lauric, myristic, palmitic, stearic
    - Unsaturated: ricinoleic, oleic, linoleic, linolenic
    """

    lauric: float
    myristic: float
    palmitic: float
    stearic: float
    ricinoleic: float
    oleic: float
    linoleic: float
    linolenic: float


class SaturatedUnsaturatedRatio(BaseModel):
    """Saturated:Unsaturated fatty acid ratio"""

    saturated: float
    unsaturated: float
    ratio: str  # Format: "28:70"


class Warning(BaseModel):
    """Non-blocking warning message"""

    code: str
    message: str
    severity: str  # warning, info
    details: dict[str, Any] | None = None


class CalculationResponse(BaseModel):
    """
    Complete calculation response per spec Section 3.1.

    Includes:
    - calculation_id: UUID for retrieval
    - timestamp: When calculation was created
    - user_id: Who created it (for auth)
    - recipe: Complete normalized recipe
    - quality_metrics: Final metrics (base + additive effects)
    - quality_metrics_base: Base metrics from oils only
    - additive_effects: Per-additive breakdown
    - fatty_acid_profile: 8 fatty acids
    - saturated_unsaturated_ratio: Sat:Unsat ratio
    - warnings: Non-blocking issues
    """

    calculation_id: UUID
    timestamp: datetime
    user_id: UUID
    recipe: RecipeOutput
    quality_metrics: QualityMetrics
    quality_metrics_base: QualityMetrics
    additive_effects: list[AdditiveEffect]
    fatty_acid_profile: FattyAcidProfile
    saturated_unsaturated_ratio: SaturatedUnsaturatedRatio
    warnings: list[Warning]


class ErrorDetail(BaseModel):
    """Error information"""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """
    Error response structure per spec Section 8.

    Error codes:
    - INVALID_OIL_PERCENTAGES: Oil percentages ≠ 100%
    - INVALID_LYE_PERCENTAGES: Lye percentages ≠ 100%
    - UNKNOWN_OIL_ID: Oil ID not in database
    - UNKNOWN_ADDITIVE_ID: Additive ID not in database (warning, not error)
    - INVALID_REQUEST: Missing required fields
    - UNAUTHORIZED: Invalid/missing JWT
    - FORBIDDEN: User trying to access another user's calculation
    - NOT_FOUND: Calculation ID not found
    """

    error: ErrorDetail
