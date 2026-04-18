"""
Unit tests for additive import script logic.

TDD Phase: RED - These tests MUST FAIL before implementing the import script.

Tests validate:
- JSON parsing from additives-usage-reference.json
- Data transformation (tablespoon PPO → percentage conversion)
- Database insertion logic with SQLAlchemy
- Idempotency (re-import doesn't duplicate data)
- Warning flag mapping
"""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session


@pytest.fixture
def sample_additive_json():
    """Sample JSON data matching additives-usage-reference.json structure"""
    return {
        "name": "Honey",
        "inci": "Mel",
        "typical_usage": "1-2 tablespoons PPO",
        "when_to_add": "to oils",
        "preparation": "Warm honey slightly if crystallized",
        "mixing_tips": "Mix thoroughly into oils before adding lye",
        "category": "lather_booster",
        "effects": {"bubbly_lather": 5.0, "bar_longevity": -2.0},
        "warnings": ["accelerates trace", "causes overheating"],
        "confidence": "high",
        "mga_verified": True,
    }


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session"""
    session = MagicMock(spec=Session)
    return session


class TestJSONParsing:
    """Test JSON file loading and parsing"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_load_additives_json_file(self):
        """
        GIVEN: additives-usage-reference.json file path
        WHEN: Loading JSON data
        THEN: Should successfully parse JSON and return dict
        """
        from scripts.import_additives_extended import load_additives_json

        data = load_additives_json(
            "working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json"
        )

        assert isinstance(data, dict)
        assert "additives" in data or isinstance(data, list)

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_parse_additive_entry(self, sample_additive_json):
        """
        GIVEN: Single additive JSON entry
        WHEN: Parsing additive data
        THEN: Should extract all required fields
        """
        from scripts.import_additives_extended import parse_additive_entry

        result = parse_additive_entry(sample_additive_json)

        assert result["common_name"] == "Honey"
        assert result["inci_name"] == "Mel"
        assert result["when_to_add"] == "to oils"
        assert result["category"] == "lather_booster"
        assert result["confidence_level"] == "high"
        assert result["verified_by_mga"] is True


class TestUsageRateConversion:
    """Test conversion from tablespoon PPO to percentage"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_convert_tablespoon_to_percent(self):
        """
        GIVEN: Usage rate "1 tablespoon PPO"
        WHEN: Converting to percentage
        THEN: Should convert to approximately 2.0%

        Formula: 1 tablespoon ≈ 2% of oil weight (standard conversion)
        """
        from scripts.import_additives_extended import convert_usage_to_percent

        result = convert_usage_to_percent("1 tablespoon PPO")

        assert result == pytest.approx(2.0, rel=0.1)

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_convert_teaspoon_to_percent(self):
        """
        GIVEN: Usage rate "1 teaspoon PPO"
        WHEN: Converting to percentage
        THEN: Should convert to approximately 1.0%

        Formula: 1 teaspoon ≈ 1% of oil weight (standard conversion)
        """
        from scripts.import_additives_extended import convert_usage_to_percent

        result = convert_usage_to_percent("1 teaspoon PPO")

        assert result == pytest.approx(1.0, rel=0.1)

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_convert_range_to_min_max_percent(self):
        """
        GIVEN: Usage rate "1-3 tablespoons PPO"
        WHEN: Converting to percentage range
        THEN: Should return min and max percentages
        """
        from scripts.import_additives_extended import parse_usage_range

        min_pct, max_pct = parse_usage_range("1-3 tablespoons PPO")

        assert min_pct == pytest.approx(2.0, rel=0.1)  # 1 tablespoon
        assert max_pct == pytest.approx(6.0, rel=0.1)  # 3 tablespoons

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_convert_percent_to_percent(self):
        """
        GIVEN: Usage rate already in percent "2%"
        WHEN: Converting to percentage
        THEN: Should return same percentage value
        """
        from scripts.import_additives_extended import convert_usage_to_percent

        result = convert_usage_to_percent("2%")

        assert result == 2.0

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_handle_descriptive_usage(self):
        """
        GIVEN: Descriptive usage "Light dusting"
        WHEN: Converting to percentage
        THEN: Should return reasonable default or None
        """
        from scripts.import_additives_extended import convert_usage_to_percent

        result = convert_usage_to_percent("Light dusting")

        # Should return None or a reasonable default
        assert result is None or (0.5 <= result <= 2.0)


class TestWarningFlagMapping:
    """Test mapping warning strings to boolean flags"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_accelerates_trace_warning(self):
        """
        GIVEN: Warning list containing "accelerates trace"
        WHEN: Mapping warnings to flags
        THEN: Should set accelerates_trace=True
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = ["accelerates trace", "causes overheating"]
        flags = map_warning_flags(warnings)

        assert flags["accelerates_trace"] is True

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_causes_overheating_warning(self):
        """
        GIVEN: Warning list containing "causes overheating"
        WHEN: Mapping warnings to flags
        THEN: Should set causes_overheating=True
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = ["causes overheating"]
        flags = map_warning_flags(warnings)

        assert flags["causes_overheating"] is True

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_can_be_scratchy_warning(self):
        """
        GIVEN: Warning list containing "can be scratchy"
        WHEN: Mapping warnings to flags
        THEN: Should set can_be_scratchy=True
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = ["can be scratchy"]
        flags = map_warning_flags(warnings)

        assert flags["can_be_scratchy"] is True

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_turns_brown_warning(self):
        """
        GIVEN: Warning list containing "turns brown"
        WHEN: Mapping warnings to flags
        THEN: Should set turns_brown=True
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = ["turns brown"]
        flags = map_warning_flags(warnings)

        assert flags["turns_brown"] is True

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_multiple_warnings(self):
        """
        GIVEN: Warning list with multiple warnings
        WHEN: Mapping warnings to flags
        THEN: Should set multiple flags to True
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = ["accelerates trace", "can be scratchy", "turns brown"]
        flags = map_warning_flags(warnings)

        assert flags["accelerates_trace"] is True
        assert flags["can_be_scratchy"] is True
        assert flags["turns_brown"] is True
        assert flags["causes_overheating"] is False  # Not in list

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_map_no_warnings(self):
        """
        GIVEN: Empty warning list
        WHEN: Mapping warnings to flags
        THEN: Should set all flags to False
        """
        from scripts.import_additives_extended import map_warning_flags

        warnings = []
        flags = map_warning_flags(warnings)

        assert flags["accelerates_trace"] is False
        assert flags["causes_overheating"] is False
        assert flags["can_be_scratchy"] is False
        assert flags["turns_brown"] is False


class TestDatabaseInsertion:
    """Test SQLAlchemy database insertion logic"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_create_or_update_additive(self, mock_db_session, sample_additive_json):
        """
        GIVEN: Parsed additive data and database session
        WHEN: Inserting additive to database
        THEN: Should create Additive instance and add to session
        """
        from scripts.import_additives_extended import create_or_update_additive

        create_or_update_additive(mock_db_session, sample_additive_json)

        # Should call session.add() with Additive instance
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_idempotent_import_same_id(self, mock_db_session, sample_additive_json):
        """
        GIVEN: Additive with same ID already exists in database
        WHEN: Re-importing same additive
        THEN: Should update existing record, not create duplicate
        """
        from scripts.import_additives_extended import create_or_update_additive

        from app.models.additive import Additive

        # Mock existing additive query
        existing = Additive(id="honey", common_name="Old Honey")
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing

        create_or_update_additive(mock_db_session, sample_additive_json)

        # Should update existing, not add new
        assert mock_db_session.add.call_count <= 1
        assert mock_db_session.commit.called

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_transaction_rollback_on_error(self, mock_db_session, sample_additive_json):
        """
        GIVEN: Database error during insertion
        WHEN: Exception occurs
        THEN: Should rollback transaction
        """
        from scripts.import_additives_extended import create_or_update_additive

        # Mock database error
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            create_or_update_additive(mock_db_session, sample_additive_json)

        # Should rollback on error
        assert mock_db_session.rollback.called


class TestBatchImport:
    """Test importing multiple additives in batch"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_import_all_additives(self, mock_db_session):
        """
        GIVEN: JSON file with 19 additives
        WHEN: Running full import
        THEN: Should process all 19 additives
        """
        from scripts.import_additives_extended import import_all_additives

        count = import_all_additives(
            mock_db_session,
            "working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json",
        )

        # Should import 19 additives per spec
        assert count == 19

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_import_with_transaction(self, mock_db_session):
        """
        GIVEN: Multiple additives to import
        WHEN: Running batch import
        THEN: Should commit transaction after all imports
        """
        from scripts.import_additives_extended import import_all_additives

        import_all_additives(
            mock_db_session,
            "working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json",
        )

        # Should commit once after all imports
        assert mock_db_session.commit.called

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_import_reports_progress(self, mock_db_session, capsys):
        """
        GIVEN: Multiple additives to import
        WHEN: Running batch import
        THEN: Should print progress information
        """
        from scripts.import_additives_extended import import_all_additives

        import_all_additives(
            mock_db_session,
            "working/user-feedback/additive-calculator-feature-request/additives-usage-reference.json",
        )

        captured = capsys.readouterr()

        # Should print progress
        assert "imported" in captured.out.lower() or "importing" in captured.out.lower()


class TestIDGeneration:
    """Test generation of additive IDs from names"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_from_name(self):
        """
        GIVEN: Additive name "Honey"
        WHEN: Generating ID
        THEN: Should create lowercase slug "honey"
        """
        from scripts.import_additives_extended import generate_additive_id

        result = generate_additive_id("Honey")

        assert result == "honey"

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_spaces(self):
        """
        GIVEN: Additive name "Sodium Lactate"
        WHEN: Generating ID
        THEN: Should create slug "sodium_lactate"
        """
        from scripts.import_additives_extended import generate_additive_id

        result = generate_additive_id("Sodium Lactate")

        assert result == "sodium_lactate"

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_special_chars(self):
        """
        GIVEN: Additive name "Salt (Sea Salt)"
        WHEN: Generating ID
        THEN: Should create clean slug without special chars
        """
        from scripts.import_additives_extended import generate_additive_id

        result = generate_additive_id("Salt (Sea Salt)")

        # Should remove or replace special characters
        assert "(" not in result
        assert ")" not in result


class TestDataValidation:
    """Test validation of imported data"""

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_validate_required_fields(self, sample_additive_json):
        """
        GIVEN: Additive data
        WHEN: Validating required fields
        THEN: Should check all required fields present
        """
        from scripts.import_additives_extended import validate_additive_data

        # Should pass validation
        is_valid, errors = validate_additive_data(sample_additive_json)

        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_validate_missing_required_field(self):
        """
        GIVEN: Additive data missing required field
        WHEN: Validating
        THEN: Should fail validation with error message
        """
        from scripts.import_additives_extended import validate_additive_data

        incomplete_data = {
            "name": "Test",
            # Missing inci_name, typical_usage, etc.
        }

        is_valid, errors = validate_additive_data(incomplete_data)

        assert is_valid is False
        assert len(errors) > 0

    @pytest.mark.skip(reason="TDD: RED phase - import script doesn't exist yet")
    def test_validate_usage_rate_range(self):
        """
        GIVEN: Additive with invalid usage rate (negative or >100%)
        WHEN: Validating
        THEN: Should fail validation
        """
        from scripts.import_additives_extended import validate_usage_rate

        # Negative rate
        assert validate_usage_rate(-1.0) is False

        # Excessive rate
        assert validate_usage_rate(150.0) is False

        # Valid rates
        assert validate_usage_rate(1.0) is True
        assert validate_usage_rate(5.0) is True
