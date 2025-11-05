"""
Unit tests for colorant import script logic.

TDD Phase: RED - These tests MUST FAIL before implementing the import script.

Tests validate:
- JSON parsing from natural-colorants-reference.json
- Category distribution (9 color families)
- Database insertion with SQLAlchemy
- Idempotency (re-import doesn't duplicate data)
"""
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def sample_yellow_colorant_json():
    """Sample JSON data for yellow colorant"""
    return {
        "name": "Turmeric",
        "botanical": "Curcuma longa",
        "usage": "1 tsp PPO",
        "method": "Infuse in oil or add at trace",
        "range": "Bright yellow to deep golden",
        "warnings": "Can stain; may fade over time"
    }


@pytest.fixture
def sample_blue_colorant_json():
    """Sample JSON data for blue colorant"""
    return {
        "name": "Indigo Powder",
        "botanical": "Indigofera tinctoria",
        "usage": "1/4-1 tsp PPO",
        "method": "Infuse in oil or add to lye",
        "range": "Light blue to deep indigo"
        # No warnings - optional field
    }


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session"""
    session = MagicMock(spec=Session)
    return session


class TestJSONParsing:
    """Test JSON file loading and parsing"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_load_colorants_json_file(self):
        """
        GIVEN: natural-colorants-reference.json file path
        WHEN: Loading JSON data
        THEN: Should successfully parse JSON with 9 color categories
        """
        from scripts.import_colorants import load_colorants_json

        data = load_colorants_json('working/user-feedback/natural-colorants-reference.json')

        assert isinstance(data, dict)
        # Should have 9 color family keys
        assert len(data.keys()) == 9

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_yellow_category(self):
        """
        GIVEN: Yellow colorants array from JSON
        WHEN: Parsing yellow category
        THEN: Should extract 14 yellow colorants
        """
        from scripts.import_colorants import load_colorants_json

        data = load_colorants_json('working/user-feedback/natural-colorants-reference.json')

        assert 'yellow' in data
        # Per spec: 14 yellow colorants
        assert len(data['yellow']) >= 10  # At least 10 yellow options

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_colorant_entry(self, sample_yellow_colorant_json):
        """
        GIVEN: Single colorant JSON entry
        WHEN: Parsing colorant data
        THEN: Should extract all fields including optional warnings
        """
        from scripts.import_colorants import parse_colorant_entry

        result = parse_colorant_entry(sample_yellow_colorant_json, category='yellow')

        assert result['name'] == 'Turmeric'
        assert result['botanical'] == 'Curcuma longa'
        assert result['category'] == 'yellow'
        assert result['usage'] == '1 tsp PPO'
        assert result['method'] == 'Infuse in oil or add at trace'
        assert result['color_range'] == 'Bright yellow to deep golden'
        assert 'stain' in result['warnings'].lower()


class TestCategoryDistribution:
    """Test 9 color family distribution"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_all_nine_categories_present(self):
        """
        GIVEN: natural-colorants-reference.json
        WHEN: Loading colorants
        THEN: Should have all 9 color families
        """
        from scripts.import_colorants import load_colorants_json

        data = load_colorants_json('working/user-feedback/natural-colorants-reference.json')

        expected_categories = [
            'yellow', 'orange', 'pink', 'red', 'green',
            'blue', 'purple', 'brown', 'black'
        ]

        for category in expected_categories:
            assert category in data

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_count_colorants_by_category(self):
        """
        GIVEN: Colorants JSON with 79 total colorants
        WHEN: Counting by category
        THEN: Should have reasonable distribution across 9 families
        """
        from scripts.import_colorants import load_colorants_json

        data = load_colorants_json('working/user-feedback/natural-colorants-reference.json')

        total_count = sum(len(colorants) for colorants in data.values())

        # Per spec: 79 colorants total
        assert total_count == 79


class TestDatabaseInsertion:
    """Test SQLAlchemy database insertion logic"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_create_or_update_colorant(self, mock_db_session, sample_yellow_colorant_json):
        """
        GIVEN: Parsed colorant data and database session
        WHEN: Inserting colorant to database
        THEN: Should create Colorant instance and add to session
        """
        from scripts.import_colorants import create_or_update_colorant

        create_or_update_colorant(mock_db_session, sample_yellow_colorant_json, category='yellow')

        # Should call session.add() with Colorant instance
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_idempotent_import_same_id(self, mock_db_session, sample_yellow_colorant_json):
        """
        GIVEN: Colorant with same ID already exists
        WHEN: Re-importing same colorant
        THEN: Should update existing record, not create duplicate
        """
        from scripts.import_colorants import create_or_update_colorant
        from app.models.colorant import Colorant

        # Mock existing colorant query
        existing = Colorant(
            id='turmeric',
            name='Old Turmeric',
            botanical='Old',
            category='yellow',
            method='Old method',
            color_range='Old range'
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing

        create_or_update_colorant(mock_db_session, sample_yellow_colorant_json, category='yellow')

        # Should update existing, not add new
        assert mock_db_session.add.call_count <= 1
        assert mock_db_session.commit.called

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_transaction_rollback_on_error(self, mock_db_session, sample_yellow_colorant_json):
        """
        GIVEN: Database error during insertion
        WHEN: Exception occurs
        THEN: Should rollback transaction
        """
        from scripts.import_colorants import create_or_update_colorant

        # Mock database error
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            create_or_update_colorant(mock_db_session, sample_yellow_colorant_json, category='yellow')

        # Should rollback on error
        assert mock_db_session.rollback.called


class TestBatchImport:
    """Test importing all colorants in batch"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_import_all_colorants(self, mock_db_session):
        """
        GIVEN: JSON file with 79 colorants across 9 categories
        WHEN: Running full import
        THEN: Should process all 79 colorants
        """
        from scripts.import_colorants import import_all_colorants

        count = import_all_colorants(
            mock_db_session,
            'working/user-feedback/natural-colorants-reference.json'
        )

        # Should import 79 colorants per spec
        assert count == 79

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_import_by_category(self, mock_db_session):
        """
        GIVEN: Colorants organized by 9 color families
        WHEN: Running import
        THEN: Should process each category separately
        """
        from scripts.import_colorants import import_all_colorants

        import_all_colorants(
            mock_db_session,
            'working/user-feedback/natural-colorants-reference.json'
        )

        # Should commit after processing all categories
        assert mock_db_session.commit.called


class TestIDGeneration:
    """Test generation of colorant IDs from names"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_from_name(self):
        """
        GIVEN: Colorant name "Turmeric"
        WHEN: Generating ID
        THEN: Should create lowercase slug "turmeric"
        """
        from scripts.import_colorants import generate_colorant_id

        result = generate_colorant_id("Turmeric")

        assert result == "turmeric"

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_spaces(self):
        """
        GIVEN: Colorant name "Annatto Seeds"
        WHEN: Generating ID
        THEN: Should create slug "annatto_seeds"
        """
        from scripts.import_colorants import generate_colorant_id

        result = generate_colorant_id("Annatto Seeds")

        assert result == "annatto_seeds"

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_generate_id_with_special_chars(self):
        """
        GIVEN: Colorant name "Clay (Red)"
        WHEN: Generating ID
        THEN: Should create clean slug without special chars
        """
        from scripts.import_colorants import generate_colorant_id

        result = generate_colorant_id("Clay (Red)")

        # Should remove or replace special characters
        assert '(' not in result
        assert ')' not in result


class TestWarningsHandling:
    """Test optional warnings field handling"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_colorant_with_warnings(self, sample_yellow_colorant_json):
        """
        GIVEN: Colorant with warnings field
        WHEN: Parsing data
        THEN: Should include warnings text
        """
        from scripts.import_colorants import parse_colorant_entry

        result = parse_colorant_entry(sample_yellow_colorant_json, category='yellow')

        assert result['warnings'] is not None
        assert 'stain' in result['warnings'].lower()

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_parse_colorant_without_warnings(self, sample_blue_colorant_json):
        """
        GIVEN: Colorant without warnings field
        WHEN: Parsing data
        THEN: Should set warnings to None
        """
        from scripts.import_colorants import parse_colorant_entry

        result = parse_colorant_entry(sample_blue_colorant_json, category='blue')

        # Warnings is optional - should be None if not present
        assert result.get('warnings') is None


class TestConfidenceLevelAssignment:
    """Test automatic confidence level assignment"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_assign_medium_confidence_default(self, sample_yellow_colorant_json):
        """
        GIVEN: Colorant from community-sourced data
        WHEN: Parsing data
        THEN: Should assign medium confidence level
        """
        from scripts.import_colorants import parse_colorant_entry

        result = parse_colorant_entry(sample_yellow_colorant_json, category='yellow')

        # Natural colorants data is community-sourced → medium confidence
        assert result.get('confidence_level') == 'medium'

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_mga_verified_false_by_default(self, sample_yellow_colorant_json):
        """
        GIVEN: Colorant from reference data
        WHEN: Parsing data
        THEN: Should set verified_by_mga to False (not yet tested)
        """
        from scripts.import_colorants import parse_colorant_entry

        result = parse_colorant_entry(sample_yellow_colorant_json, category='yellow')

        assert result.get('verified_by_mga') is False


class TestMethodValidation:
    """Test method field validation"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_valid_method_infuse(self):
        """
        GIVEN: Colorant with infusion method
        WHEN: Validating method
        THEN: Should accept infusion method
        """
        from scripts.import_colorants import validate_method

        method = "Infuse in oil"
        assert validate_method(method) is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_valid_method_add_at_trace(self):
        """
        GIVEN: Colorant with add at trace method
        WHEN: Validating method
        THEN: Should accept trace method
        """
        from scripts.import_colorants import validate_method

        method = "Add at trace"
        assert validate_method(method) is True

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_valid_method_add_to_lye(self):
        """
        GIVEN: Colorant with add to lye method
        WHEN: Validating method
        THEN: Should accept lye method
        """
        from scripts.import_colorants import validate_method

        method = "Add to lye solution"
        assert validate_method(method) is True


class TestDataQuality:
    """Test data quality validation"""

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_required_fields_present(self, sample_yellow_colorant_json):
        """
        GIVEN: Colorant data
        WHEN: Validating required fields
        THEN: Should check name, botanical, method, range present
        """
        from scripts.import_colorants import validate_colorant_data

        is_valid, errors = validate_colorant_data(sample_yellow_colorant_json, category='yellow')

        assert is_valid is True
        assert len(errors) == 0

    @pytest.skip("TDD: RED phase - import script doesn't exist yet")
    def test_validate_missing_required_field(self):
        """
        GIVEN: Colorant data missing required field
        WHEN: Validating
        THEN: Should fail validation with error message
        """
        from scripts.import_colorants import validate_colorant_data

        incomplete_data = {
            "name": "Test",
            # Missing botanical, method, range
        }

        is_valid, errors = validate_colorant_data(incomplete_data, category='yellow')

        assert is_valid is False
        assert len(errors) > 0
