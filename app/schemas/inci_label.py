"""
Pydantic schemas for INCI label generation

Request/response models for User Story 1 and Spec 003 three-format support
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OilFormulationItem(BaseModel):
    """Single oil in a soap formulation"""

    oil_id: str = Field(
        ..., description="Oil database ID (e.g., 'coconut-oil')", min_length=1, max_length=50
    )
    weight_grams: float = Field(..., description="Weight of oil in grams", gt=0, le=100000)


class SoapFormulation(BaseModel):
    """Complete soap formulation with oils"""

    oils: list[OilFormulationItem] = Field(
        ..., description="List of oils in the formulation", min_length=1, max_length=20
    )


class InciLabelRequest(BaseModel):
    """Request to generate INCI label"""

    formulation: SoapFormulation = Field(..., description="Soap formulation details")
    lye_type: str = Field(
        ..., description="Type of lye: 'naoh' (sodium hydroxide) or 'koh' (potassium hydroxide)"
    )

    @field_validator("lye_type")
    @classmethod
    def validate_lye_type(cls, v: str) -> str:
        """Ensure lye_type is valid"""
        if v not in ("naoh", "koh"):
            raise ValueError("lye_type must be 'naoh' or 'koh'")
        return v


class InciIngredient(BaseModel):
    """Single ingredient in INCI label with details"""

    oil_id: str = Field(..., description="Oil database ID")
    common_name: str = Field(..., description="Common name of the oil")
    saponified_inci_name: str = Field(
        ..., description="Saponified INCI name (e.g., 'Sodium Cocoate')"
    )
    percentage: float = Field(
        ..., description="Percentage of this ingredient in formulation", ge=0, le=100
    )
    is_generated: bool = Field(
        ...,
        description="Whether INCI name was pattern-generated (true) or from reference data (false)",
    )


class InciLabelResponse(BaseModel):
    """Response with generated INCI label"""

    inci_label: str = Field(
        ..., description="Complete INCI label (comma-separated, descending percentage order)"
    )
    ingredients: list[InciIngredient] = Field(
        ..., description="Detailed list of ingredients (sorted by percentage descending)"
    )
    total_oil_weight: float = Field(..., description="Total weight of oils in grams")
    lye_type_used: str = Field(..., description="Type of lye used: 'naoh' or 'koh'")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inci_label": "Sodium Olivate, Sodium Cocoate",
                "ingredients": [
                    {
                        "oil_id": "olive-oil",
                        "common_name": "Olive Oil",
                        "saponified_inci_name": "Sodium Olivate",
                        "percentage": 70.0,
                        "is_generated": False,
                    },
                    {
                        "oil_id": "coconut-oil",
                        "common_name": "Coconut Oil",
                        "saponified_inci_name": "Sodium Cocoate",
                        "percentage": 30.0,
                        "is_generated": False,
                    },
                ],
                "total_oil_weight": 1000.0,
                "lye_type_used": "naoh",
            }
        }
    )


# ============================================================================
# Spec 003: Three-Format INCI Label Response for Calculation-Based Endpoint
# ============================================================================


class IngredientBreakdown(BaseModel):
    """
    Detailed ingredient information with percentage

    Used in three-format INCI label response for regulatory compliance
    and debugging/verification purposes.
    """

    name: str = Field(
        ..., description="Ingredient name (format depends on context: INCI, saponified, or common)"
    )
    percentage: float = Field(
        ..., description="Percentage of total batch weight (to 1 decimal place)", ge=0.0, le=100.0
    )
    category: str = Field(..., description="Ingredient category (water, oil, lye, additive, etc.)")
    notes: str | None = Field(
        None, description="Optional notes (e.g., saponification details, warnings)"
    )


class ThreeFormatInciResponse(BaseModel):
    """
    Three-format INCI label response per Spec 003

    Provides raw_inci (pre-saponification), saponified_inci (post-saponification),
    and common_names formats for professional label generation.

    All ingredients sorted by percentage (descending) per regulatory requirements.
    """

    raw_inci: str | None = Field(
        None, description="Pre-saponification INCI format (oils + lye listed separately)"
    )
    saponified_inci: str | None = Field(
        None, description="Post-saponification INCI format (sodium/potassium salts, lye excluded)"
    )
    common_names: str | None = Field(None, description="Consumer-friendly common names format")
    ingredients_breakdown: list[IngredientBreakdown] | None = Field(
        None, description="Detailed ingredient breakdown with percentages (for verification)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "raw_inci": "Aqua, Olea Europaea Fruit Oil, Cocos Nucifera Oil, Sodium Hydroxide",
                "saponified_inci": "Aqua, Sodium Olivate, Sodium Cocoate",
                "common_names": "Water, Olive Oil, Coconut Oil, Sodium Hydroxide",
                "ingredients_breakdown": [
                    {"name": "Aqua", "percentage": 30.5, "category": "water", "notes": None},
                    {
                        "name": "Olea Europaea Fruit Oil",
                        "percentage": 40.0,
                        "category": "oil",
                        "notes": "Saponifies to Sodium Olivate",
                    },
                ],
            }
        }
    )
