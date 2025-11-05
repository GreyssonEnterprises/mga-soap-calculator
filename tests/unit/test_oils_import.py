"""
Unit tests for oils import logic.

Tests data loading, parsing, and import process mechanics.
All tests should FAIL initially (RED phase).
"""
import pytest
import json
from pathlib import Path
from scripts.import_oils_database import (
    load_oils_from_json,
    validate_all_oils,
)


class TestJSONLoading:
    """Test JSON data loading and parsing"""

    def test_load_oils_from_json_file_exists(self):
        """Load 147 oils from JSON file"""
        json_path = Path(__file__).parent.parent.parent / "working/user-feedback/oils-db-additions/complete-oils-database.json"

        oils_data = load_oils_from_json(str(json_path))

        assert oils_data is not None
        assert isinstance(oils_data, dict)
        assert len(oils_data) == 147

    def test_load_oils_from_json_structure(self):
        """Verify loaded oils have correct structure"""
        json_path = Path(__file__).parent.parent.parent / "working/user-feedback/oils-db-additions/complete-oils-database.json"

        oils_data = load_oils_from_json(str(json_path))

        # Check first oil has all required fields
        first_oil_id = list(oils_data.keys())[0]
        first_oil = oils_data[first_oil_id]

        required_fields = [
            "id", "common_name", "inci_name",
            "sap_value_naoh", "sap_value_koh",
            "iodine_value", "ins_value",
            "fatty_acids", "quality_contributions"
        ]

        for field in required_fields:
            assert field in first_oil, f"Missing field: {field}"

    def test_load_oils_from_json_file_not_found(self):
        """Loading from non-existent file should raise error"""
        with pytest.raises(FileNotFoundError):
            load_oils_from_json("/nonexistent/path/oils.json")

    def test_load_oils_from_json_invalid_json(self, tmp_path):
        """Loading invalid JSON should raise error"""
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text("{ invalid json content")

        with pytest.raises(json.JSONDecodeError):
            load_oils_from_json(str(invalid_json_file))


class TestValidationBatch:
    """Test batch validation of all oils"""

    def test_validate_all_oils_from_file(self):
        """All 147 oils should pass validation"""
        json_path = Path(__file__).parent.parent.parent / "working/user-feedback/oils-db-additions/complete-oils-database.json"

        oils_data = load_oils_from_json(str(json_path))
        is_valid, errors = validate_all_oils(oils_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_all_oils_with_invalid_data(self):
        """Validation should detect and report invalid oils"""
        oils_data = {
            "good_oil": {
                "id": "good_oil",
                "common_name": "Good Oil",
                "inci_name": "",
                "sap_value_naoh": 0.135,
                "sap_value_koh": 0.190,
                "iodine_value": 81.0,
                "ins_value": 109.0,
                "fatty_acids": {
                    "lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 4,
                    "oleic": 71, "linoleic": 10, "linolenic": 1, "ricinoleic": 0
                },
                "quality_contributions": {
                    "hardness": 17.0, "cleansing": 0.0, "conditioning": 82.0,
                    "bubbly_lather": 0.0, "creamy_lather": 17.0,
                    "longevity": 17.0, "stability": 82.0
                }
            },
            "bad_oil": {
                "id": "bad_oil",
                "common_name": "Bad Oil",
                "inci_name": "",
                "sap_value_naoh": 0.999,  # Invalid - too high
                "sap_value_koh": 1.400,
                "iodine_value": 81.0,
                "ins_value": 109.0,
                "fatty_acids": {
                    "lauric": 10, "myristic": 10, "palmitic": 10, "stearic": 10,
                    "oleic": 10, "linoleic": 10, "linolenic": 10, "ricinoleic": 0
                },  # Sum = 70% (invalid)
                "quality_contributions": {
                    "hardness": 17.0, "cleansing": 0.0, "conditioning": 82.0,
                    "bubbly_lather": 0.0, "creamy_lather": 17.0,
                    "longevity": 17.0, "stability": 82.0
                }
            }
        }

        is_valid, errors = validate_all_oils(oils_data)

        assert is_valid is False
        assert len(errors) == 1
        assert "bad_oil" in errors[0]


class TestDuplicateDetection:
    """Test duplicate oil detection logic"""

    @pytest.mark.asyncio
    async def test_duplicate_detection_existing_oil(self):
        """Detect existing oils in database"""
        # This test requires database setup
        # Will be implemented with actual database session
        pytest.skip("Requires database integration - see integration tests")

    @pytest.mark.asyncio
    async def test_duplicate_detection_new_oil(self):
        """Identify new oils not in database"""
        # This test requires database setup
        # Will be implemented with actual database session
        pytest.skip("Requires database integration - see integration tests")
