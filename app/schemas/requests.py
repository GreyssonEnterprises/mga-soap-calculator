"""
Request Pydantic models for API validation (Task 3.1.1)

TDD Evidence: Tests written first in test_request_models.py
Implements spec Section 3.1 request schema with validation rules.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class OilInput(BaseModel):
    """
    Oil input with either weight_g OR percentage specified.

    Validation per spec Section 6.1:
    - At least one of weight_g or percentage must be provided
    - Not both (one must be None)
    """

    id: str
    weight_g: float | None = None
    percentage: float | None = None

    @model_validator(mode="after")
    def validate_weight_or_percentage(self):
        """Ensure at least one of weight_g or percentage is provided"""
        if self.weight_g is None and self.percentage is None:
            raise ValueError("Either weight_g or percentage must be provided")
        return self


class LyeConfig(BaseModel):
    """
    Lye configuration with NaOH and KOH percentages.

    Validation per spec Section 6.1:
    - naoh_percent + koh_percent must equal 100.0 (with 0.01 tolerance for floating point)
    - koh_purity: Optional purity percentage (50-100%), default 90%
    - naoh_purity: Optional purity percentage (50-100%), default 100%

    Feature: KOH/NaOH Purity Support (Spec 002-lye-purity)
    """

    naoh_percent: float
    koh_percent: float
    koh_purity: float | None = Field(default=90.0, ge=50.0, le=100.0)
    naoh_purity: float | None = Field(default=100.0, ge=50.0, le=100.0)

    @model_validator(mode="after")
    def validate_percentage_sum(self):
        """Ensure lye percentages sum to 100%"""
        total = self.naoh_percent + self.koh_percent
        if abs(total - 100.0) > 0.01:  # Floating point tolerance
            raise ValueError(f"NaOH and KOH percentages must sum to 100%, got {total}")
        return self


class WaterConfig(BaseModel):
    """
    Water calculation configuration.

    Three methods per spec Section 5.2:
    1. water_percent_of_oils: Water as % of total oil weight
    2. lye_concentration: Lye concentration (% of water+lye solution)
    3. water_lye_ratio: Water:lye ratio
    """

    method: Literal["water_percent_of_oils", "lye_concentration", "water_lye_ratio"]
    value: float


class AdditiveInput(BaseModel):
    """
    Additive input with either weight_g OR percentage specified.

    Similar validation to OilInput - at least one must be provided.
    """

    id: str
    weight_g: float | None = None
    percentage: float | None = None

    @model_validator(mode="after")
    def validate_weight_or_percentage(self):
        """Ensure at least one of weight_g or percentage is provided"""
        if self.weight_g is None and self.percentage is None:
            raise ValueError("Either weight_g or percentage must be provided")
        return self


class CalculationRequest(BaseModel):
    """
    Complete calculation request matching spec Section 3.1.

    Required fields:
    - oils: List of oil inputs (at least 1)
    - lye: Lye configuration (NaOH + KOH percentages)
    - water: Water calculation configuration
    - superfat_percent: Superfat percentage (0-100)

    Optional fields:
    - additives: List of additive inputs (default: empty list)
    - total_oil_weight_g: Total batch size when using percentages (default: 1000g)
    """

    oils: list[OilInput]
    lye: LyeConfig
    water: WaterConfig
    superfat_percent: float
    additives: list[AdditiveInput] = []
    total_oil_weight_g: float | None = Field(default=1000.0, gt=0)

    @field_validator("oils")
    @classmethod
    def validate_oils_not_empty(cls, v):
        """Ensure at least one oil is provided"""
        if not v:
            raise ValueError("At least one oil must be provided")
        return v

    @field_validator("superfat_percent")
    @classmethod
    def validate_superfat_range(cls, v):
        """Ensure superfat is in valid range"""
        if not 0 <= v <= 100:
            raise ValueError(f"Superfat must be 0-100%, got {v}")
        return v
