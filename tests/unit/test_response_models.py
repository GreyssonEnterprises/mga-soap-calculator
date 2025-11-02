"""
Tests for Pydantic response models (Task 3.1.2)

TDD Evidence:
- Written BEFORE implementation
- Tests validate response schema against spec Section 3.1
- Covers complete calculation response structure
"""
import pytest
from datetime import datetime
from uuid import uuid4


def test_oil_output_model():
    """Test OilOutput response model"""
    from app.schemas.responses import OilOutput

    oil = OilOutput(
        id="olive_oil",
        common_name="Olive Oil",  # Fixed: spec requires 'common_name' not 'name'
        weight_g=450.0,
        percentage=45.0
    )

    assert oil.id == "olive_oil"
    assert oil.common_name == "Olive Oil"  # Fixed
    assert oil.weight_g == 450.0
    assert oil.percentage == 45.0


def test_lye_output_model():
    """Test LyeOutput response model"""
    from app.schemas.responses import LyeOutput

    lye = LyeOutput(
        naoh_weight_g=142.6,  # Fixed: spec requires 'naoh_weight_g' not 'naoh_g'
        koh_weight_g=0.0,     # Fixed: spec requires 'koh_weight_g' not 'koh_g'
        total_lye_g=142.6,
        naoh_percent=100.0,
        koh_percent=0.0
    )

    assert lye.naoh_weight_g == 142.6  # Fixed
    assert lye.koh_weight_g == 0.0     # Fixed
    assert lye.total_lye_g == 142.6
    assert lye.naoh_percent == 100.0
    assert lye.koh_percent == 0.0


def test_additive_output_model():
    """Test AdditiveOutput response model"""
    from app.schemas.responses import AdditiveOutput

    additive = AdditiveOutput(
        id="kaolin_clay",
        name="Kaolin Clay (White)",
        weight_g=20.0,
        percentage=2.0
    )

    assert additive.id == "kaolin_clay"
    assert additive.name == "Kaolin Clay (White)"
    assert additive.weight_g == 20.0
    assert additive.percentage == 2.0


def test_recipe_output_model():
    """Test RecipeOutput response model"""
    from app.schemas.responses import RecipeOutput, OilOutput, LyeOutput, AdditiveOutput

    recipe = RecipeOutput(
        total_oil_weight_g=1000.0,
        oils=[
            OilOutput(id="olive_oil", common_name="Olive Oil", weight_g=500.0, percentage=50.0)  # Fixed
        ],
        lye=LyeOutput(
            naoh_weight_g=142.6,  # Fixed
            koh_weight_g=0.0,     # Fixed
            total_lye_g=142.6,
            naoh_percent=100.0,
            koh_percent=0.0
        ),
        water_weight_g=289.5,
        water_method="lye_concentration",  # Fixed: Added missing field
        water_method_value=33.0,           # Fixed: Added missing field
        superfat_percent=5.0,
        additives=[]
    )

    assert recipe.total_oil_weight_g == 1000.0
    assert len(recipe.oils) == 1
    assert recipe.lye.total_lye_g == 142.6
    assert recipe.water_weight_g == 289.5
    assert recipe.superfat_percent == 5.0


def test_quality_metrics_model():
    """Test QualityMetrics response model"""
    from app.schemas.responses import QualityMetrics

    metrics = QualityMetrics(
        hardness=58.0,
        cleansing=41.0,
        conditioning=34.0,
        bubbly_lather=41.0,
        creamy_lather=17.0,
        longevity=45.0,
        stability=52.0,
        iodine=67.8,
        ins=148.5
    )

    assert metrics.hardness == 58.0
    assert metrics.cleansing == 41.0
    assert metrics.conditioning == 34.0
    assert metrics.bubbly_lather == 41.0
    assert metrics.creamy_lather == 17.0
    assert metrics.longevity == 45.0
    assert metrics.stability == 52.0
    assert metrics.iodine == 67.8
    assert metrics.ins == 148.5


def test_additive_effect_model():
    """Test AdditiveEffect response model"""
    from app.schemas.responses import AdditiveEffect

    effect = AdditiveEffect(
        additive_id="kaolin_clay",
        additive_name="Kaolin Clay (White)",
        effects={
            "hardness": 4.0,
            "creamy_lather": 7.0,
            "conditioning": 0.8
        },
        confidence="high",
        verified_by_mga=False
    )

    assert effect.additive_id == "kaolin_clay"
    assert effect.additive_name == "Kaolin Clay (White)"
    assert effect.effects["hardness"] == 4.0
    assert effect.effects["creamy_lather"] == 7.0
    assert effect.confidence == "high"
    assert effect.verified_by_mga is False


def test_fatty_acid_profile_model():
    """Test FattyAcidProfile response model"""
    from app.schemas.responses import FattyAcidProfile

    profile = FattyAcidProfile(
        lauric=8.5,
        myristic=5.2,
        palmitic=10.3,
        stearic=4.1,
        ricinoleic=0.0,
        oleic=52.3,
        linoleic=15.6,
        linolenic=1.8
    )

    assert profile.lauric == 8.5
    assert profile.myristic == 5.2
    assert profile.palmitic == 10.3
    assert profile.stearic == 4.1
    assert profile.ricinoleic == 0.0
    assert profile.oleic == 52.3
    assert profile.linoleic == 15.6
    assert profile.linolenic == 1.8


def test_saturated_unsaturated_ratio_model():
    """Test SaturatedUnsaturatedRatio response model"""
    from app.schemas.responses import SaturatedUnsaturatedRatio

    ratio = SaturatedUnsaturatedRatio(
        saturated=28.1,
        unsaturated=69.7,
        ratio="28:70"
    )

    assert ratio.saturated == 28.1
    assert ratio.unsaturated == 69.7
    assert ratio.ratio == "28:70"


def test_warning_model():
    """Test Warning response model"""
    from app.schemas.responses import Warning

    warning = Warning(
        code="HIGH_SUPERFAT",
        message="Superfat >20% may produce soft, greasy bars",
        severity="warning",
        details={"superfat_percent": 25.0}
    )

    assert warning.code == "HIGH_SUPERFAT"
    assert warning.message.startswith("Superfat >20%")
    assert warning.severity == "warning"
    assert warning.details["superfat_percent"] == 25.0


def test_calculation_response_model_complete():
    """Test complete CalculationResponse model"""
    from app.schemas.responses import (
        CalculationResponse,
        RecipeOutput,
        OilOutput,
        LyeOutput,
        QualityMetrics,
        FattyAcidProfile,
        SaturatedUnsaturatedRatio,
        Warning
    )

    calculation_id = uuid4()
    user_id = uuid4()

    response = CalculationResponse(
        calculation_id=calculation_id,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        recipe=RecipeOutput(
            total_oil_weight_g=1000.0,
            oils=[
                OilOutput(id="olive_oil", common_name="Olive Oil", weight_g=500.0, percentage=50.0)  # Fixed
            ],
            lye=LyeOutput(
                naoh_weight_g=142.6,  # Fixed
                koh_weight_g=0.0,     # Fixed
                total_lye_g=142.6,
                naoh_percent=100.0,
                koh_percent=0.0
            ),
            water_weight_g=289.5,
            water_method="lye_concentration",  # Fixed: Added missing field
            water_method_value=33.0,           # Fixed: Added missing field
            superfat_percent=5.0,
            additives=[]
        ),
        quality_metrics=QualityMetrics(
            hardness=58.0,
            cleansing=41.0,
            conditioning=34.0,
            bubbly_lather=41.0,
            creamy_lather=17.0,
            longevity=45.0,
            stability=52.0,
            iodine=67.8,
            ins=148.5
        ),
        quality_metrics_base=QualityMetrics(
            hardness=54.0,
            cleansing=41.0,
            conditioning=33.2,
            bubbly_lather=41.0,
            creamy_lather=10.0,
            longevity=45.0,
            stability=52.0,
            iodine=67.8,
            ins=148.5
        ),
        additive_effects=[],
        fatty_acid_profile=FattyAcidProfile(
            lauric=8.5,
            myristic=5.2,
            palmitic=10.3,
            stearic=4.1,
            ricinoleic=0.0,
            oleic=52.3,
            linoleic=15.6,
            linolenic=1.8
        ),
        saturated_unsaturated_ratio=SaturatedUnsaturatedRatio(
            saturated=28.1,
            unsaturated=69.7,
            ratio="28:70"
        ),
        warnings=[]
    )

    assert response.calculation_id == calculation_id
    assert response.user_id == user_id
    assert response.recipe.total_oil_weight_g == 1000.0
    assert response.quality_metrics.hardness == 58.0
    assert response.fatty_acid_profile.oleic == 52.3
    assert response.saturated_unsaturated_ratio.ratio == "28:70"
    assert len(response.warnings) == 0


def test_error_response_model():
    """Test ErrorResponse model for error handling"""
    from app.schemas.responses import ErrorResponse, ErrorDetail

    error = ErrorResponse(
        error=ErrorDetail(
            code="INVALID_OIL_PERCENTAGES",
            message="Oil percentages must sum to exactly 100%",
            details={"calculated_sum": 99.5, "expected_sum": 100.0}
        )
    )

    assert error.error.code == "INVALID_OIL_PERCENTAGES"
    assert "100%" in error.error.message
    assert error.error.details["calculated_sum"] == 99.5
