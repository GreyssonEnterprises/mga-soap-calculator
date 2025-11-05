"""
Unit tests for extended Additive model with calculator fields.

TDD Phase: RED - These tests MUST FAIL before implementing new fields.

Tests validate:
- New calculator fields (usage_rate_standard_percent, when_to_add, category)
- Warning boolean flags (accelerates_trace, causes_overheating, etc.)
- JSONB fields (preparation_instructions, mixing_tips)
- Field constraints and validation
"""
import pytest
from sqlalchemy import inspect
from app.models.additive import Additive


class TestAdditiveModelExtension:
    """Test extended Additive model fields for calculator feature"""

    def test_has_usage_rate_standard_percent_field(self):
        """New field: usage_rate_standard_percent (float)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'usage_rate_standard_percent' in columns
        assert columns['usage_rate_standard_percent'].type.python_type == float

    def test_has_when_to_add_field(self):
        """New field: when_to_add (string: 'to oils', 'to lye water', 'at trace')"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'when_to_add' in columns
        # Should be string type
        assert hasattr(columns['when_to_add'].type, 'length')

    def test_has_preparation_instructions_field(self):
        """New field: preparation_instructions (text, nullable)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'preparation_instructions' in columns
        assert columns['preparation_instructions'].nullable is True

    def test_has_mixing_tips_field(self):
        """New field: mixing_tips (text, nullable)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'mixing_tips' in columns
        assert columns['mixing_tips'].nullable is True

    def test_has_category_field(self):
        """New field: category (string)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'category' in columns
        # Valid categories: exfoliant, colorant, lather_booster, hardener,
        #                   clay, botanical, luxury_additive, skin_benefit

    def test_has_accelerates_trace_flag(self):
        """Warning flag: accelerates_trace (boolean, default False)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'accelerates_trace' in columns
        assert columns['accelerates_trace'].type.python_type == bool
        assert columns['accelerates_trace'].default is not None  # Has default

    def test_has_causes_overheating_flag(self):
        """Warning flag: causes_overheating (boolean, default False)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'causes_overheating' in columns
        assert columns['causes_overheating'].type.python_type == bool

    def test_has_can_be_scratchy_flag(self):
        """Warning flag: can_be_scratchy (boolean, default False)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'can_be_scratchy' in columns
        assert columns['can_be_scratchy'].type.python_type == bool

    def test_has_turns_brown_flag(self):
        """Warning flag: turns_brown (boolean, default False)"""
        inspector = inspect(Additive)
        columns = {col.name: col for col in inspector.columns}

        assert 'turns_brown' in columns
        assert columns['turns_brown'].type.python_type == bool


class TestAdditiveInstanceCreation:
    """Test creating Additive instances with new fields"""

    @pytest.fixture
    def sample_additive_data(self):
        """Sample data for testing additive creation"""
        return {
            'id': 'honey',
            'common_name': 'Honey',
            'inci_name': 'Mel',
            'typical_usage_min_percent': 1.0,
            'typical_usage_max_percent': 3.0,
            'usage_rate_standard_percent': 2.0,
            'when_to_add': 'to oils',
            'preparation_instructions': 'Warm honey slightly if crystallized',
            'mixing_tips': 'Mix thoroughly into oils before adding lye',
            'category': 'lather_booster',
            'accelerates_trace': True,
            'causes_overheating': True,
            'can_be_scratchy': False,
            'turns_brown': False,
            'quality_effects': {'bubbly_lather': 5.0},
            'confidence_level': 'high',
            'verified_by_mga': True,
        }

    def test_create_additive_with_calculator_fields(self, sample_additive_data):
        """Should create Additive instance with all calculator fields"""
        additive = Additive(**sample_additive_data)

        assert additive.id == 'honey'
        assert additive.usage_rate_standard_percent == 2.0
        assert additive.when_to_add == 'to oils'
        assert additive.category == 'lather_booster'
        assert additive.accelerates_trace is True
        assert additive.causes_overheating is True
        assert additive.can_be_scratchy is False
        assert additive.turns_brown is False

    def test_warning_flags_default_to_false(self):
        """Warning flags should default to False when not specified"""
        additive = Additive(
            id='test',
            common_name='Test',
            inci_name='Test INCI',
            typical_usage_min_percent=1.0,
            typical_usage_max_percent=2.0,
            usage_rate_standard_percent=1.5,
            when_to_add='at trace',
            category='exfoliant',
            quality_effects={},
            confidence_level='medium',
            verified_by_mga=False,
        )

        # All warning flags should default to False
        assert additive.accelerates_trace is False
        assert additive.causes_overheating is False
        assert additive.can_be_scratchy is False
        assert additive.turns_brown is False

    def test_nullable_fields_can_be_none(self):
        """preparation_instructions and mixing_tips can be None"""
        additive = Additive(
            id='test2',
            common_name='Test 2',
            inci_name='Test INCI 2',
            typical_usage_min_percent=1.0,
            typical_usage_max_percent=2.0,
            usage_rate_standard_percent=1.5,
            when_to_add='at trace',
            category='clay',
            preparation_instructions=None,  # Nullable
            mixing_tips=None,  # Nullable
            quality_effects={},
            confidence_level='low',
            verified_by_mga=False,
        )

        assert additive.preparation_instructions is None
        assert additive.mixing_tips is None
