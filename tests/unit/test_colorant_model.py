"""
Unit tests for Colorant model.

TDD Phase: RED - These tests MUST FAIL before implementing the model.

Tests validate:
- Required fields (name, botanical, category, method, color_range)
- Optional fields (usage, warnings)
- Category validation (9 color families)
- Confidence level and verification flags
"""
import pytest
from sqlalchemy import inspect
from app.models.colorant import Colorant


class TestColorantModelStructure:
    """Test Colorant model field structure"""

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_required_id_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have id field (string primary key)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'id' in columns
        assert columns['id'].primary_key is True

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_name_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have name field (string, not nullable)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'name' in columns
        assert columns['name'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_botanical_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have botanical field (string, not nullable)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'botanical' in columns
        assert columns['botanical'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_category_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have category field (string: 9 color families)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'category' in columns
        assert columns['category'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_usage_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have usage field (string, nullable - descriptive rates)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'usage' in columns
        assert columns['usage'].nullable is True

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_method_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have method field (string: infuse/add at trace/add to lye)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'method' in columns
        assert columns['method'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_color_range_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have color_range field (string - expected outcome)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'color_range' in columns
        assert columns['color_range'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_warnings_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have warnings field (text, nullable)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'warnings' in columns
        assert columns['warnings'].nullable is True

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_confidence_level_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have confidence_level field (string)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'confidence_level' in columns
        assert columns['confidence_level'].nullable is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_has_verified_by_mga_field(self):
        """
        GIVEN: Colorant model definition
        WHEN: Inspecting model columns
        THEN: Should have verified_by_mga field (boolean, default False)
        """
        inspector = inspect(Colorant)
        columns = {col.name: col for col in inspector.columns}

        assert 'verified_by_mga' in columns
        assert columns['verified_by_mga'].type.python_type == bool


class TestColorantInstanceCreation:
    """Test creating Colorant instances"""

    @pytest.fixture
    def sample_colorant_data(self):
        """Sample data for testing colorant creation"""
        return {
            'id': 'turmeric',
            'name': 'Turmeric',
            'botanical': 'Curcuma longa',
            'category': 'yellow',
            'usage': '1 tsp PPO',
            'method': 'Infuse in oil or add at trace',
            'color_range': 'Bright yellow to deep golden',
            'warnings': 'Can stain; may fade over time',
            'confidence_level': 'high',
            'verified_by_mga': True,
        }

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_create_colorant_with_all_fields(self, sample_colorant_data):
        """
        GIVEN: Sample colorant data
        WHEN: Creating Colorant instance
        THEN: Should create instance with all fields populated
        """
        colorant = Colorant(**sample_colorant_data)

        assert colorant.id == 'turmeric'
        assert colorant.name == 'Turmeric'
        assert colorant.botanical == 'Curcuma longa'
        assert colorant.category == 'yellow'
        assert colorant.usage == '1 tsp PPO'
        assert colorant.method == 'Infuse in oil or add at trace'
        assert colorant.color_range == 'Bright yellow to deep golden'
        assert colorant.warnings == 'Can stain; may fade over time'
        assert colorant.confidence_level == 'high'
        assert colorant.verified_by_mga is True

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_create_colorant_minimal_fields(self):
        """
        GIVEN: Minimal colorant data
        WHEN: Creating Colorant instance
        THEN: Should create instance with required fields only
        """
        colorant = Colorant(
            id='test',
            name='Test Colorant',
            botanical='Testus colorantus',
            category='blue',
            method='Add at trace',
            color_range='Light to dark blue',
            confidence_level='low',
            verified_by_mga=False,
        )

        assert colorant.id == 'test'
        assert colorant.name == 'Test Colorant'
        assert colorant.botanical == 'Testus colorantus'
        assert colorant.category == 'blue'
        assert colorant.method == 'Add at trace'
        assert colorant.color_range == 'Light to dark blue'
        assert colorant.confidence_level == 'low'
        assert colorant.verified_by_mga is False

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_nullable_fields_can_be_none(self):
        """
        GIVEN: Colorant without optional fields
        WHEN: Creating instance
        THEN: Should accept None for usage and warnings
        """
        colorant = Colorant(
            id='test_null',
            name='Test Null',
            botanical='Testus nullus',
            category='green',
            method='Infuse',
            color_range='Green',
            usage=None,  # Nullable
            warnings=None,  # Nullable
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert colorant.usage is None
        assert colorant.warnings is None


class TestColorantCategoryValidation:
    """Test category field validation for 9 color families"""

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_all_nine_color_categories(self):
        """
        GIVEN: Colorants with all 9 valid color categories
        WHEN: Creating instances
        THEN: Should accept all 9 color family values
        """
        # 9 color families from natural-colorants-reference.json
        valid_categories = [
            'yellow',
            'orange',
            'pink',
            'red',
            'green',
            'blue',
            'purple',
            'brown',
            'black',
        ]

        for category in valid_categories:
            colorant = Colorant(
                id=f'test_{category}',
                name=f'Test {category.title()}',
                botanical=f'Testus {category}',
                category=category,
                method='Test method',
                color_range=f'{category.title()} range',
                confidence_level='medium',
                verified_by_mga=False,
            )
            assert colorant.category == category

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_yellow_category_examples(self):
        """
        GIVEN: Yellow colorants (turmeric, calendula, etc.)
        WHEN: Creating instances
        THEN: Should accept yellow category
        """
        yellow_colorants = [
            ('turmeric', 'Curcuma longa'),
            ('calendula', 'Calendula officinalis'),
            ('lemon_zest', 'Citrus limon'),
        ]

        for colorant_id, botanical in yellow_colorants:
            colorant = Colorant(
                id=colorant_id,
                name=colorant_id.replace('_', ' ').title(),
                botanical=botanical,
                category='yellow',
                method='Infuse or add at trace',
                color_range='Yellow',
                confidence_level='high',
                verified_by_mga=True,
            )
            assert colorant.category == 'yellow'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_orange_category_examples(self):
        """
        GIVEN: Orange colorants (annatto, paprika, etc.)
        WHEN: Creating instances
        THEN: Should accept orange category
        """
        colorant = Colorant(
            id='annatto',
            name='Annatto Seeds',
            botanical='Bixa orellana',
            category='orange',
            method='Infuse seeds in oil',
            color_range='Buttery yellow to pumpkin orange',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert colorant.category == 'orange'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_red_category_examples(self):
        """
        GIVEN: Red colorants (madder root, rose clay, etc.)
        WHEN: Creating instances
        THEN: Should accept red category
        """
        colorant = Colorant(
            id='madder_root',
            name='Madder Root',
            botanical='Rubia tinctorum',
            category='red',
            method='Infuse in oil',
            color_range='Coral to brick red',
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert colorant.category == 'red'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_green_category_examples(self):
        """
        GIVEN: Green colorants (spirulina, chlorella, etc.)
        WHEN: Creating instances
        THEN: Should accept green category
        """
        colorant = Colorant(
            id='spirulina',
            name='Spirulina Powder',
            botanical='Arthrospira platensis',
            category='green',
            method='Mix with water, add at trace',
            color_range='Sage green to teal',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert colorant.category == 'green'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_blue_category_examples(self):
        """
        GIVEN: Blue colorants (woad, indigo, etc.)
        WHEN: Creating instances
        THEN: Should accept blue category
        """
        colorant = Colorant(
            id='indigo',
            name='Indigo Powder',
            botanical='Indigofera tinctoria',
            category='blue',
            method='Infuse in oil or add to lye',
            color_range='Light blue to deep indigo',
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert colorant.category == 'blue'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_purple_category_examples(self):
        """
        GIVEN: Purple colorants (alkanet root, purple sweet potato, etc.)
        WHEN: Creating instances
        THEN: Should accept purple category
        """
        colorant = Colorant(
            id='alkanet_root',
            name='Alkanet Root',
            botanical='Alkanna tinctoria',
            category='purple',
            method='Infuse in oil',
            color_range='Purple to burgundy',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert colorant.category == 'purple'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_brown_category_examples(self):
        """
        GIVEN: Brown colorants (coffee, cocoa, cinnamon, etc.)
        WHEN: Creating instances
        THEN: Should accept brown category
        """
        colorant = Colorant(
            id='coffee',
            name='Coffee Grounds',
            botanical='Coffea arabica',
            category='brown',
            method='Infuse in oil or add at trace',
            color_range='Tan to dark brown',
            warnings='Can be scratchy if not ground finely',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert colorant.category == 'brown'

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_black_category_examples(self):
        """
        GIVEN: Black colorants (activated charcoal, black oxide, etc.)
        WHEN: Creating instances
        THEN: Should accept black category
        """
        colorant = Colorant(
            id='activated_charcoal',
            name='Activated Charcoal',
            botanical='Carbon',
            category='black',
            method='Mix with water, add at light trace',
            color_range='Gray to black',
            warnings='Can be messy; may accelerate trace',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert colorant.category == 'black'


class TestColorantMethodValidation:
    """Test method field validation"""

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_infusion_method(self):
        """
        GIVEN: Colorant using infusion method
        WHEN: Creating instance
        THEN: Should accept infusion method description
        """
        colorant = Colorant(
            id='test_infuse',
            name='Test Infuse',
            botanical='Testus infusus',
            category='yellow',
            method='Infuse in liquid oil, strain, use infused oil',
            color_range='Yellow',
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert 'infuse' in colorant.method.lower()

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_add_at_trace_method(self):
        """
        GIVEN: Colorant using add at trace method
        WHEN: Creating instance
        THEN: Should accept add at trace method description
        """
        colorant = Colorant(
            id='test_trace',
            name='Test Trace',
            botanical='Testus tracus',
            category='green',
            method='Add at trace',
            color_range='Green',
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert 'trace' in colorant.method.lower()

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_add_to_lye_method(self):
        """
        GIVEN: Colorant using add to lye method
        WHEN: Creating instance
        THEN: Should accept add to lye method description
        """
        colorant = Colorant(
            id='test_lye',
            name='Test Lye',
            botanical='Testus lyeus',
            category='blue',
            method='Add to lye solution',
            color_range='Blue',
            confidence_level='medium',
            verified_by_mga=False,
        )

        assert 'lye' in colorant.method.lower()


class TestColorantWarnings:
    """Test warnings field handling"""

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_scratchy_warning(self):
        """
        GIVEN: Colorant with scratchy warning
        WHEN: Creating instance
        THEN: Should store scratchy warning
        """
        colorant = Colorant(
            id='coffee',
            name='Coffee Grounds',
            botanical='Coffea arabica',
            category='brown',
            method='Add at trace',
            color_range='Brown',
            warnings='Can be scratchy if not ground finely',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert 'scratchy' in colorant.warnings.lower()

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_staining_warning(self):
        """
        GIVEN: Colorant with staining warning
        WHEN: Creating instance
        THEN: Should store staining warning
        """
        colorant = Colorant(
            id='turmeric',
            name='Turmeric',
            botanical='Curcuma longa',
            category='yellow',
            method='Add at trace',
            color_range='Yellow',
            warnings='Can stain; may fade over time',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert 'stain' in colorant.warnings.lower()

    @pytest.skip("TDD: RED phase - model doesn't exist yet")
    def test_accelerates_trace_warning(self):
        """
        GIVEN: Colorant with accelerates trace warning
        WHEN: Creating instance
        THEN: Should store accelerates trace warning
        """
        colorant = Colorant(
            id='charcoal',
            name='Activated Charcoal',
            botanical='Carbon',
            category='black',
            method='Add at light trace',
            color_range='Gray to black',
            warnings='May accelerate trace',
            confidence_level='high',
            verified_by_mga=True,
        )

        assert 'accelerate' in colorant.warnings.lower()
