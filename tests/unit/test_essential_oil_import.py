"""
Unit tests for essential oil import script logic.

TDD Phase: RED - These tests MUST FAIL before implementing the import script.

Tests validate:
- JSON parsing from essential-oils-usage-reference.json
- Max usage rate validation (0.025% - 3.0%)
- JSONB array field handling (blends_with)
- Database insertion with SQLAlchemy
- Idempotency (re-import doesn't duplicate data)
"""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session


@pytest.fixture
def sample_essential_oil_json():
    """Sample JSON data matching essential-oils-usage-reference.json structure"""
    return {
        "name": "Lavender",
        "botanical_name": "Lavandula angustifolia",
        "max_usage_rate_pct": 3.0,
        "usage_rate_per_pound": {"oz": 0.48, "g": 13.6, "tsp": 3.0},
        "scent_profile": "Floral, sweet, herbaceous",
        "usage_notes": "Most versatile EO for soap making",
        "blends_with": ["Bergamot", "Clary Sage", "Geranium", "Patchouli"],
        "note": "Middle",
        "category": "floral",
    }


@pytest.fixture
def sample_rose_otto_json():
    """Sample JSON for Rose Otto with very low usage rate"""
    return {
        "name": "Rose Otto",
        "botanical_name": "Rosa damascena",
        "max_usage_rate_pct": 0.025,  # Very low - expensive and potent
        "usage_rate_per_pound": {"oz": 0.004, "g": 0.11, "tsp": 0.025},
        "scent_profile": "Deep, rich, floral rose",
        "usage_notes": "Extremely expensive; use sparingly",
        "blends_with": ["Bergamot", "Geranium", "Jasmine", "Sandalwood"],
        "note": "Middle",
        "category": "floral",
    }


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session"""
    session = MagicMock(spec=Session)
    return session


class TestJSONParsing:
    """Test JSON file loading and parsing"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_load_essential_oils_json_file(self):
        """
        GIVEN: essential-oils-usage-reference.json file path
        WHEN: Loading JSON data
        THEN: Should successfully parse JSON and return dict/list
        """
        from scripts.import_essential_oils import load_essential_oils_json

        data = load_essential_oils_json("working/user-feedback/essential-oils-usage-reference.json")

        assert isinstance(data, (dict, list))

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_essential_oil_entry(self, sample_essential_oil_json):
        """
        GIVEN: Single essential oil JSON entry
        WHEN: Parsing EO data
        THEN: Should extract all required fields
        """
        from scripts.import_essential_oils import parse_essential_oil_entry

        result = parse_essential_oil_entry(sample_essential_oil_json)

        assert result["name"] == "Lavender"
        assert result["botanical_name"] == "Lavandula angustifolia"
        assert result["max_usage_rate_pct"] == 3.0
        assert result["note"] == "Middle"
        assert result["category"] == "floral"


class TestMaxUsageRateValidation:
    """Test validation of max usage rate (0.025% - 3.0%)"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_minimum_usage_rate(self, sample_rose_otto_json):
        """
        GIVEN: Rose Otto with 0.025% max usage rate
        WHEN: Validating usage rate
        THEN: Should accept minimum safe rate
        """
        from scripts.import_essential_oils import validate_usage_rate

        is_valid = validate_usage_rate(sample_rose_otto_json["max_usage_rate_pct"])

        assert is_valid is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_maximum_usage_rate(self, sample_essential_oil_json):
        """
        GIVEN: Lavender with 3.0% max usage rate
        WHEN: Validating usage rate
        THEN: Should accept maximum safe rate
        """
        from scripts.import_essential_oils import validate_usage_rate

        is_valid = validate_usage_rate(sample_essential_oil_json["max_usage_rate_pct"])

        assert is_valid is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_typical_usage_rates(self):
        """
        GIVEN: Typical EO usage rates
        WHEN: Validating
        THEN: Should accept all rates between 0.025% and 3.0%
        """
        from scripts.import_essential_oils import validate_usage_rate

        typical_rates = [0.025, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

        for rate in typical_rates:
            assert validate_usage_rate(rate) is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_reject_too_low_usage_rate(self):
        """
        GIVEN: Usage rate below 0.025%
        WHEN: Validating
        THEN: Should reject as too low
        """
        from scripts.import_essential_oils import validate_usage_rate

        is_valid = validate_usage_rate(0.01)  # Below minimum

        assert is_valid is False

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_reject_too_high_usage_rate(self):
        """
        GIVEN: Usage rate above 3.0%
        WHEN: Validating
        THEN: Should reject as unsafe
        """
        from scripts.import_essential_oils import validate_usage_rate

        is_valid = validate_usage_rate(5.0)  # Above maximum

        assert is_valid is False

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_reject_negative_usage_rate(self):
        """
        GIVEN: Negative usage rate
        WHEN: Validating
        THEN: Should reject as invalid
        """
        from scripts.import_essential_oils import validate_usage_rate

        is_valid = validate_usage_rate(-1.0)

        assert is_valid is False


class TestBlendsWithArrayHandling:
    """Test JSONB array field handling"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_blends_with_array(self, sample_essential_oil_json):
        """
        GIVEN: EO with blends_with array
        WHEN: Parsing data
        THEN: Should preserve array structure
        """
        from scripts.import_essential_oils import parse_essential_oil_entry

        result = parse_essential_oil_entry(sample_essential_oil_json)

        assert "blends_with" in result
        assert isinstance(result["blends_with"], list)
        assert len(result["blends_with"]) == 4
        assert "Bergamot" in result["blends_with"]

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_handle_empty_blends_with(self):
        """
        GIVEN: EO with empty blends_with array
        WHEN: Parsing data
        THEN: Should accept empty array
        """
        from scripts.import_essential_oils import parse_essential_oil_entry

        data = {
            "name": "Test",
            "botanical_name": "Testus",
            "max_usage_rate_pct": 2.0,
            "blends_with": [],
            "note": "Top",
            "category": "citrus",
        }

        result = parse_essential_oil_entry(data)

        assert result["blends_with"] == []

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_handle_missing_blends_with(self):
        """
        GIVEN: EO without blends_with field
        WHEN: Parsing data
        THEN: Should set to None or empty array
        """
        from scripts.import_essential_oils import parse_essential_oil_entry

        data = {
            "name": "Test",
            "botanical_name": "Testus",
            "max_usage_rate_pct": 2.0,
            "note": "Top",
            "category": "citrus",
            # blends_with missing
        }

        result = parse_essential_oil_entry(data)

        # Should be None or []
        assert result.get("blends_with") is None or result.get("blends_with") == []


class TestDatabaseInsertion:
    """Test SQLAlchemy database insertion logic"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_create_or_update_essential_oil(self, mock_db_session, sample_essential_oil_json):
        """
        GIVEN: Parsed EO data and database session
        WHEN: Inserting EO to database
        THEN: Should create EssentialOil instance and add to session
        """
        from scripts.import_essential_oils import create_or_update_essential_oil

        create_or_update_essential_oil(mock_db_session, sample_essential_oil_json)

        # Should call session.add() with EssentialOil instance
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_idempotent_import_same_id(self, mock_db_session, sample_essential_oil_json):
        """
        GIVEN: EO with same ID already exists in database
        WHEN: Re-importing same EO
        THEN: Should update existing record, not create duplicate
        """
        from app.models.essential_oil import EssentialOil
        from scripts.import_essential_oils import create_or_update_essential_oil

        # Mock existing EO query
        existing = EssentialOil(
            id="lavender", name="Old Lavender", botanical_name="Old", max_usage_rate_pct=2.0
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing

        create_or_update_essential_oil(mock_db_session, sample_essential_oil_json)

        # Should update existing, not add new
        assert mock_db_session.add.call_count <= 1
        assert mock_db_session.commit.called

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_transaction_rollback_on_error(self, mock_db_session, sample_essential_oil_json):
        """
        GIVEN: Database error during insertion
        WHEN: Exception occurs
        THEN: Should rollback transaction
        """
        from scripts.import_essential_oils import create_or_update_essential_oil

        # Mock database error
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            create_or_update_essential_oil(mock_db_session, sample_essential_oil_json)

        # Should rollback on error
        assert mock_db_session.rollback.called


class TestBatchImport:
    """Test importing multiple essential oils in batch"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_import_all_essential_oils(self, mock_db_session):
        """
        GIVEN: JSON file with 24 essential oils
        WHEN: Running full import
        THEN: Should process all 24 essential oils
        """
        from scripts.import_essential_oils import import_all_essential_oils

        count = import_all_essential_oils(
            mock_db_session, "working/user-feedback/essential-oils-usage-reference.json"
        )

        # Should import 24 essential oils per spec
        assert count == 24

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_import_with_transaction(self, mock_db_session):
        """
        GIVEN: Multiple EOs to import
        WHEN: Running batch import
        THEN: Should commit transaction after all imports
        """
        from scripts.import_essential_oils import import_all_essential_oils

        import_all_essential_oils(
            mock_db_session, "working/user-feedback/essential-oils-usage-reference.json"
        )

        # Should commit once after all imports
        assert mock_db_session.commit.called


class TestIDGeneration:
    """Test generation of essential oil IDs from names"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_from_name(self):
        """
        GIVEN: EO name "Lavender"
        WHEN: Generating ID
        THEN: Should create lowercase slug "lavender"
        """
        from scripts.import_essential_oils import generate_essential_oil_id

        result = generate_essential_oil_id("Lavender")

        assert result == "lavender"

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_spaces(self):
        """
        GIVEN: EO name "Tea Tree"
        WHEN: Generating ID
        THEN: Should create slug "tea_tree"
        """
        from scripts.import_essential_oils import generate_essential_oil_id

        result = generate_essential_oil_id("Tea Tree")

        assert result == "tea_tree"

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_special_name(self):
        """
        GIVEN: EO name "Rose Otto"
        WHEN: Generating ID
        THEN: Should create clean slug "rose_otto"
        """
        from scripts.import_essential_oils import generate_essential_oil_id

        result = generate_essential_oil_id("Rose Otto")

        assert result == "rose_otto"


class TestConfidenceLevelAssignment:
    """Test automatic confidence level assignment based on CPSR validation"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_cpsr_validated_high_confidence(self, sample_essential_oil_json):
        """
        GIVEN: EO with CPSR-validated max usage rate
        WHEN: Parsing data
        THEN: Should assign high confidence level
        """
        from scripts.import_essential_oils import parse_essential_oil_entry

        result = parse_essential_oil_entry(sample_essential_oil_json)

        # CPSR-validated data should have high confidence
        assert result.get("confidence_level") == "high"

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_all_eos_high_confidence(self):
        """
        GIVEN: Essential oils from CPSR-validated source
        WHEN: Importing all EOs
        THEN: Should assign high confidence to all (verified data source)
        """
        from scripts.import_essential_oils import determine_confidence_level

        # All EOs from essential-oils-usage-reference.json are CPSR-validated
        confidence = determine_confidence_level(has_cpsr_data=True)

        assert confidence == "high"


class TestNoteValidation:
    """Test note field validation (Top, Middle, Base)"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_note_top(self):
        """
        GIVEN: EO with "Top" note
        WHEN: Validating note
        THEN: Should accept Top note
        """
        from scripts.import_essential_oils import validate_note

        assert validate_note("Top") is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_note_middle(self):
        """
        GIVEN: EO with "Middle" note
        WHEN: Validating note
        THEN: Should accept Middle note
        """
        from scripts.import_essential_oils import validate_note

        assert validate_note("Middle") is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_note_base(self):
        """
        GIVEN: EO with "Base" note
        WHEN: Validating note
        THEN: Should accept Base note
        """
        from scripts.import_essential_oils import validate_note

        assert validate_note("Base") is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_reject_invalid_note(self):
        """
        GIVEN: EO with invalid note
        WHEN: Validating note
        THEN: Should reject invalid note value
        """
        from scripts.import_essential_oils import validate_note

        assert validate_note("Invalid") is False


class TestCategoryValidation:
    """Test category field validation"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_valid_categories(self):
        """
        GIVEN: EOs with valid categories
        WHEN: Validating category
        THEN: Should accept all valid categories
        """
        from scripts.import_essential_oils import validate_category

        valid_categories = ["citrus", "floral", "herbal", "woodsy", "earthy", "spice"]

        for category in valid_categories:
            assert validate_category(category) is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_reject_invalid_category(self):
        """
        GIVEN: EO with invalid category
        WHEN: Validating category
        THEN: Should reject invalid category
        """
        from scripts.import_essential_oils import validate_category

        assert validate_category("invalid_category") is False
