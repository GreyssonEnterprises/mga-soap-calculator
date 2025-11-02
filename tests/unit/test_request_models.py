"""
Tests for Pydantic request models (Task 3.1.1)

TDD Evidence:
- Written BEFORE implementation
- Tests validate request schema against spec Section 3.1
- Covers validation rules for oil inputs, lye config, water config, additives
"""
import pytest
from pydantic import ValidationError


def test_oil_input_with_weight():
    """Test OilInput with weight specified"""
    from app.schemas.requests import OilInput

    oil = OilInput(id="olive_oil", weight_g=450.0, percentage=None)
    assert oil.id == "olive_oil"
    assert oil.weight_g == 450.0
    assert oil.percentage is None


def test_oil_input_with_percentage():
    """Test OilInput with percentage specified"""
    from app.schemas.requests import OilInput

    oil = OilInput(id="coconut_oil", weight_g=None, percentage=30.0)
    assert oil.id == "coconut_oil"
    assert oil.weight_g is None
    assert oil.percentage == 30.0


def test_oil_input_requires_weight_or_percentage():
    """Test that at least one of weight or percentage must be provided"""
    from app.schemas.requests import OilInput

    # Both None should fail
    with pytest.raises(ValidationError) as exc_info:
        OilInput(id="olive_oil", weight_g=None, percentage=None)

    assert "weight_g or percentage" in str(exc_info.value).lower()


def test_lye_config_percentages_sum_to_100():
    """Test LyeConfig validates percentages sum to 100"""
    from app.schemas.requests import LyeConfig

    # Valid: 100% NaOH
    lye = LyeConfig(naoh_percent=100.0, koh_percent=0.0)
    assert lye.naoh_percent == 100.0
    assert lye.koh_percent == 0.0

    # Valid: 70% NaOH, 30% KOH
    lye = LyeConfig(naoh_percent=70.0, koh_percent=30.0)
    assert lye.naoh_percent == 70.0
    assert lye.koh_percent == 30.0


def test_lye_config_rejects_invalid_percentages():
    """Test LyeConfig rejects percentages that don't sum to 100"""
    from app.schemas.requests import LyeConfig

    with pytest.raises(ValidationError) as exc_info:
        LyeConfig(naoh_percent=90.0, koh_percent=5.0)  # Sum = 95

    assert "100" in str(exc_info.value)


def test_water_config_lye_concentration_method():
    """Test WaterConfig with lye concentration method"""
    from app.schemas.requests import WaterConfig

    water = WaterConfig(method="lye_concentration", value=33.0)
    assert water.method == "lye_concentration"
    assert water.value == 33.0


def test_water_config_oil_percent_method():
    """Test WaterConfig with water as % of oils method"""
    from app.schemas.requests import WaterConfig

    water = WaterConfig(method="water_percent_of_oils", value=38.0)
    assert water.method == "water_percent_of_oils"
    assert water.value == 38.0


def test_water_config_lye_ratio_method():
    """Test WaterConfig with water:lye ratio method"""
    from app.schemas.requests import WaterConfig

    water = WaterConfig(method="water_lye_ratio", value=2.0)
    assert water.method == "water_lye_ratio"
    assert water.value == 2.0


def test_water_config_rejects_invalid_method():
    """Test WaterConfig rejects invalid method"""
    from app.schemas.requests import WaterConfig

    with pytest.raises(ValidationError):
        WaterConfig(method="invalid_method", value=33.0)


def test_additive_input_with_weight():
    """Test AdditiveInput with weight specified"""
    from app.schemas.requests import AdditiveInput

    additive = AdditiveInput(id="kaolin_clay", weight_g=20.0, percentage=None)
    assert additive.id == "kaolin_clay"
    assert additive.weight_g == 20.0
    assert additive.percentage is None


def test_additive_input_with_percentage():
    """Test AdditiveInput with percentage specified"""
    from app.schemas.requests import AdditiveInput

    additive = AdditiveInput(id="sodium_lactate", weight_g=None, percentage=2.0)
    assert additive.id == "sodium_lactate"
    assert additive.weight_g is None
    assert additive.percentage == 2.0


def test_calculation_request_valid():
    """Test complete CalculationRequest with all required fields"""
    from app.schemas.requests import CalculationRequest, OilInput, LyeConfig, WaterConfig

    request = CalculationRequest(
        oils=[
            OilInput(id="olive_oil", weight_g=450.0, percentage=None),
            OilInput(id="coconut_oil", weight_g=None, percentage=30.0),
        ],
        lye=LyeConfig(naoh_percent=100.0, koh_percent=0.0),
        water=WaterConfig(method="lye_concentration", value=33.0),
        superfat_percent=5.0,
        additives=[]
    )

    assert len(request.oils) == 2
    assert request.lye.naoh_percent == 100.0
    assert request.water.method == "lye_concentration"
    assert request.superfat_percent == 5.0
    assert request.additives == []


def test_calculation_request_with_additives():
    """Test CalculationRequest with additives"""
    from app.schemas.requests import CalculationRequest, OilInput, LyeConfig, WaterConfig, AdditiveInput

    request = CalculationRequest(
        oils=[OilInput(id="olive_oil", weight_g=500.0, percentage=None)],
        lye=LyeConfig(naoh_percent=100.0, koh_percent=0.0),
        water=WaterConfig(method="lye_concentration", value=33.0),
        superfat_percent=5.0,
        additives=[
            AdditiveInput(id="kaolin_clay", weight_g=20.0, percentage=None),
            AdditiveInput(id="sodium_lactate", weight_g=None, percentage=2.0)
        ]
    )

    assert len(request.additives) == 2
    assert request.additives[0].id == "kaolin_clay"
    assert request.additives[1].id == "sodium_lactate"


def test_calculation_request_missing_required_fields():
    """Test CalculationRequest rejects missing required fields"""
    from app.schemas.requests import CalculationRequest

    # Missing oils
    with pytest.raises(ValidationError):
        CalculationRequest(
            lye={"naoh_percent": 100.0, "koh_percent": 0.0},
            water={"method": "lye_concentration", "value": 33.0},
            superfat_percent=5.0
        )
