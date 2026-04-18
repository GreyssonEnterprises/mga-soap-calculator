"""
Unit tests for oils validation logic.

Tests validate scientific ranges and data quality requirements
for oil import process, adjusted for real-world data including waxes and exotic oils.
"""

from scripts.import_oils_database import (
    validate_fatty_acids_sum,
    validate_oil_data,
    validate_quality_metrics_range,
    validate_sap_koh_range,
    validate_sap_naoh_range,
)


class TestSAPValidation:
    """Test SAP value range validation"""

    def test_validate_sap_naoh_range_valid(self):
        """Valid SAP NaOH values (0.000-0.350) should pass"""
        assert validate_sap_naoh_range(0.000) == (True, "")  # Pine tar, waxes
        assert validate_sap_naoh_range(0.100) == (True, "")
        assert validate_sap_naoh_range(0.200) == (True, "")
        assert validate_sap_naoh_range(0.325) == (True, "")  # Fractionated coconut oil
        assert validate_sap_naoh_range(0.350) == (True, "")

    def test_validate_sap_naoh_range_too_low(self):
        """SAP NaOH below 0.000 should fail"""
        is_valid, error = validate_sap_naoh_range(-0.050)
        assert is_valid is False
        assert "0.000" in error

    def test_validate_sap_naoh_range_too_high(self):
        """SAP NaOH above 0.350 should fail"""
        is_valid, error = validate_sap_naoh_range(0.400)
        assert is_valid is False
        assert "0.350" in error
        assert "0.400" in error

    def test_validate_sap_koh_range_valid(self):
        """Valid SAP KOH values (0.000-0.490) should pass"""
        assert validate_sap_koh_range(0.000) == (True, "")  # Pine tar, waxes
        assert validate_sap_koh_range(0.140) == (True, "")
        assert validate_sap_koh_range(0.280) == (True, "")
        assert validate_sap_koh_range(0.456) == (True, "")  # Fractionated coconut oil
        assert validate_sap_koh_range(0.490) == (True, "")

    def test_validate_sap_koh_range_too_low(self):
        """SAP KOH below 0.000 should fail"""
        is_valid, error = validate_sap_koh_range(-0.050)
        assert is_valid is False
        assert "0.000" in error

    def test_validate_sap_koh_range_too_high(self):
        """SAP KOH above 0.490 should fail"""
        is_valid, error = validate_sap_koh_range(0.550)
        assert is_valid is False
        assert "0.490" in error


class TestFattyAcidValidation:
    """Test fatty acid profile validation"""

    def test_validate_fatty_acids_sum_valid(self):
        """Fatty acids summing to 30-105% should pass (realistic range for exotic oils/waxes)"""
        fatty_acids_99 = {
            "lauric": 0,
            "myristic": 0,
            "palmitic": 13,
            "stearic": 4,
            "oleic": 71,
            "linoleic": 10,
            "linolenic": 1,
            "ricinoleic": 0,
        }  # Sum = 99%
        assert validate_fatty_acids_sum(fatty_acids_99, "test_oil") == (True, "")

        fatty_acids_38 = {
            "lauric": 5,
            "myristic": 5,
            "palmitic": 5,
            "stearic": 5,
            "oleic": 8,
            "linoleic": 8,
            "linolenic": 2,
            "ricinoleic": 0,
        }  # Sum = 38% (some exotic oils)
        assert validate_fatty_acids_sum(fatty_acids_38, "test_oil") == (True, "")

        fatty_acids_104 = {
            "lauric": 20,
            "myristic": 20,
            "palmitic": 20,
            "stearic": 20,
            "oleic": 10,
            "linoleic": 10,
            "linolenic": 3,
            "ricinoleic": 1,
        }  # Sum = 104% (measurement variation)
        assert validate_fatty_acids_sum(fatty_acids_104, "test_oil") == (True, "")

    def test_validate_fatty_acids_sum_too_low(self):
        """Fatty acids summing below 30% should fail"""
        fatty_acids_low = {
            "lauric": 5,
            "myristic": 3,
            "palmitic": 5,
            "stearic": 3,
            "oleic": 5,
            "linoleic": 3,
            "linolenic": 0,
            "ricinoleic": 0,
        }  # Sum = 24%
        is_valid, error = validate_fatty_acids_sum(fatty_acids_low, "test_oil")
        assert is_valid is False
        assert "24" in error or "30" in error

    def test_validate_fatty_acids_sum_too_high(self):
        """Fatty acids summing above 105% should fail"""
        fatty_acids_high = {
            "lauric": 30,
            "myristic": 25,
            "palmitic": 20,
            "stearic": 15,
            "oleic": 15,
            "linoleic": 10,
            "linolenic": 5,
            "ricinoleic": 0,
        }  # Sum = 120%
        is_valid, error = validate_fatty_acids_sum(fatty_acids_high, "test_oil")
        assert is_valid is False
        assert "120" in error or "105" in error

    def test_pine_tar_special_case(self):
        """Pine Tar can have zero fatty acids (resin-based)"""
        fatty_acids_zero = {
            "lauric": 0,
            "myristic": 0,
            "palmitic": 0,
            "stearic": 0,
            "oleic": 0,
            "linoleic": 0,
            "linolenic": 0,
            "ricinoleic": 0,
        }
        is_valid, error = validate_fatty_acids_sum(fatty_acids_zero, "pine_tar")
        assert is_valid is True
        assert error == ""


class TestQualityMetricsValidation:
    """Test quality metrics range validation"""

    def test_validate_quality_metrics_range_valid(self):
        """Quality metrics in 0-100 range should pass"""
        quality_metrics = {
            "hardness": 17.0,
            "cleansing": 0.0,
            "conditioning": 82.0,
            "bubbly_lather": 0.0,
            "creamy_lather": 17.0,
            "longevity": 17.0,
            "stability": 82.0,
        }
        assert validate_quality_metrics_range(quality_metrics) == (True, "")

        # Pure fatty acids can have 100
        quality_metrics_100 = {
            "hardness": 100.0,
            "cleansing": 100.0,
            "conditioning": 0.0,
            "bubbly_lather": 100.0,
            "creamy_lather": 0.0,
            "longevity": 100.0,
            "stability": 0.0,
        }
        assert validate_quality_metrics_range(quality_metrics_100) == (True, "")

    def test_validate_quality_metrics_range_negative(self):
        """Negative quality metrics should fail"""
        quality_metrics = {
            "hardness": -5.0,
            "cleansing": 0.0,
            "conditioning": 82.0,
            "bubbly_lather": 0.0,
            "creamy_lather": 17.0,
            "longevity": 17.0,
            "stability": 82.0,
        }
        is_valid, error = validate_quality_metrics_range(quality_metrics)
        assert is_valid is False
        assert "hardness" in error

    def test_validate_quality_metrics_range_too_high(self):
        """Quality metrics above 100 should fail"""
        quality_metrics = {
            "hardness": 150.0,
            "cleansing": 0.0,
            "conditioning": 82.0,
            "bubbly_lather": 0.0,
            "creamy_lather": 17.0,
            "longevity": 17.0,
            "stability": 82.0,
        }
        is_valid, error = validate_quality_metrics_range(quality_metrics)
        assert is_valid is False
        assert "hardness" in error or "100" in error


class TestOilDataValidation:
    """Test complete oil data validation (wrapper)"""

    def test_validate_oil_data_complete_valid(self):
        """Complete valid oil data should pass all validations"""
        oil_data = {
            "id": "olive_oil",
            "common_name": "Olive Oil",
            "inci_name": "Olea Europaea (Olive) Fruit Oil",
            "sap_value_naoh": 0.135,
            "sap_value_koh": 0.190,
            "iodine_value": 81.0,
            "ins_value": 109.0,
            "fatty_acids": {
                "lauric": 0,
                "myristic": 0,
                "palmitic": 13,
                "stearic": 4,
                "oleic": 71,
                "linoleic": 10,
                "linolenic": 1,
                "ricinoleic": 0,
            },
            "quality_contributions": {
                "hardness": 17.0,
                "cleansing": 0.0,
                "conditioning": 82.0,
                "bubbly_lather": 0.0,
                "creamy_lather": 17.0,
                "longevity": 17.0,
                "stability": 82.0,
            },
        }
        is_valid, error = validate_oil_data("olive_oil", oil_data)
        assert is_valid is True
        assert error == ""

    def test_validate_oil_data_invalid_sap(self):
        """Oil with invalid SAP values should fail"""
        oil_data = {
            "id": "invalid_oil",
            "common_name": "Invalid Oil",
            "inci_name": "",
            "sap_value_naoh": 0.500,  # Too high
            "sap_value_koh": 0.700,
            "iodine_value": 81.0,
            "ins_value": 109.0,
            "fatty_acids": {
                "lauric": 0,
                "myristic": 0,
                "palmitic": 13,
                "stearic": 4,
                "oleic": 71,
                "linoleic": 10,
                "linolenic": 1,
                "ricinoleic": 0,
            },
            "quality_contributions": {
                "hardness": 17.0,
                "cleansing": 0.0,
                "conditioning": 82.0,
                "bubbly_lather": 0.0,
                "creamy_lather": 17.0,
                "longevity": 17.0,
                "stability": 82.0,
            },
        }
        is_valid, error = validate_oil_data("invalid_oil", oil_data)
        assert is_valid is False
        assert "SAP" in error or "0.500" in error

    def test_validate_oil_data_invalid_fatty_acids(self):
        """Oil with invalid fatty acid sum should fail"""
        oil_data = {
            "id": "invalid_oil",
            "common_name": "Invalid Oil",
            "inci_name": "",
            "sap_value_naoh": 0.135,
            "sap_value_koh": 0.190,
            "iodine_value": 81.0,
            "ins_value": 109.0,
            "fatty_acids": {
                "lauric": 5,
                "myristic": 3,
                "palmitic": 5,
                "stearic": 3,
                "oleic": 3,
                "linoleic": 3,
                "linolenic": 2,
                "ricinoleic": 0,
            },  # Sum = 24% (too low, below 30%)
            "quality_contributions": {
                "hardness": 17.0,
                "cleansing": 0.0,
                "conditioning": 82.0,
                "bubbly_lather": 0.0,
                "creamy_lather": 17.0,
                "longevity": 17.0,
                "stability": 82.0,
            },
        }
        is_valid, error = validate_oil_data("invalid_oil", oil_data)
        assert is_valid is False
        assert "fatty" in error.lower() or "24" in error
