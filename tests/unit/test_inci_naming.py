"""
Unit tests for INCI naming service

TDD RED PHASE: These tests MUST FAIL initially (no implementation exists yet)
"""

from unittest.mock import Mock

import pytest

from app.models.oil import Oil

# Import will fail initially - this is expected in RED phase
from app.services.inci_naming import (
    generate_saponified_name,
    get_saponified_inci_name,
    load_reference_data,
)


class TestLoadReferenceData:
    """Test loading saponified INCI reference data from JSON"""

    def test_load_reference_data_returns_dict(self):
        """Reference data should be loaded as dictionary"""
        data = load_reference_data()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_load_reference_data_has_expected_oils(self):
        """Reference data should contain common oils"""
        data = load_reference_data()
        # Test subset of 37 oils from research.md
        expected_oils = ["coconut-oil", "olive-oil", "palm-oil", "castor-oil", "shea-butter"]
        for oil_id in expected_oils:
            assert oil_id in data, f"Expected oil {oil_id} not in reference data"

    def test_reference_data_structure(self):
        """Each entry should have required fields"""
        data = load_reference_data()
        first_oil = next(iter(data.values()))

        assert "saponified_inci_naoh" in first_oil
        assert "saponified_inci_koh" in first_oil
        assert isinstance(first_oil["saponified_inci_naoh"], str)
        assert isinstance(first_oil["saponified_inci_koh"], str)


class TestGenerateSaponifiedName:
    """Test pattern-based saponified name generation"""

    def test_generate_naoh_name_simple(self):
        """Generate sodium salt name for simple oil"""
        result = generate_saponified_name("Coconut Oil", "naoh")
        assert result == "Sodium Cocoate"

    def test_generate_koh_name_simple(self):
        """Generate potassium salt name for simple oil"""
        result = generate_saponified_name("Coconut Oil", "koh")
        assert result == "Potassium Cocoate"

    def test_generate_name_removes_oil_suffix(self):
        """Should remove 'Oil' suffix before adding '-ate'"""
        result = generate_saponified_name("Olive Oil", "naoh")
        assert result == "Sodium Olivate"
        assert "Oil" not in result

    def test_generate_name_removes_butter_suffix(self):
        """Should remove 'Butter' suffix for butter-type ingredients"""
        result = generate_saponified_name("Shea Butter", "naoh")
        assert result == "Sodium Sheaate"
        assert "Butter" not in result

    def test_generate_name_preserves_multi_word(self):
        """Should preserve multi-word base names"""
        result = generate_saponified_name("Sweet Almond Oil", "naoh")
        assert "Sweet Almond" in result
        assert result == "Sodium Sweet Almondate"

    def test_generate_name_handles_spaces(self):
        """Should handle spacing correctly"""
        result = generate_saponified_name("Shea Butter", "naoh")
        # Should have space after Sodium, no extra spaces
        assert "Sodium " in result
        assert "  " not in result  # No double spaces

    def test_generate_name_invalid_lye_type(self):
        """Should raise error for invalid lye type"""
        with pytest.raises((ValueError, KeyError)):
            generate_saponified_name("Coconut Oil", "invalid")


class TestGetSaponifiedInciName:
    """Test getting saponified INCI name with fallback logic"""

    def test_get_name_from_oil_with_reference_data_naoh(self):
        """Should use oil's saponified_inci_name field for NaOH"""
        oil = Mock(spec=Oil)
        oil.id = "coconut-oil"
        oil.common_name = "Coconut Oil"
        oil.saponified_inci_name = "Sodium Cocoate"

        name, is_generated = get_saponified_inci_name(oil, "naoh")

        assert name == "Sodium Cocoate"
        assert is_generated is False

    def test_get_name_from_oil_with_reference_data_koh(self):
        """Should convert Sodium to Potassium for KOH"""
        oil = Mock(spec=Oil)
        oil.id = "coconut-oil"
        oil.common_name = "Coconut Oil"
        oil.saponified_inci_name = "Sodium Cocoate"

        name, is_generated = get_saponified_inci_name(oil, "koh")

        assert name == "Potassium Cocoate"
        assert is_generated is False

    def test_get_name_fallback_to_pattern_generation(self):
        """Should use pattern generation when no reference data"""
        oil = Mock(spec=Oil)
        oil.id = "exotic-oil"
        oil.common_name = "Exotic Oil"
        oil.saponified_inci_name = None  # No reference data

        name, is_generated = get_saponified_inci_name(oil, "naoh")

        assert name == "Sodium Exoticate"
        assert is_generated is True

    def test_get_name_handles_castor_dual_nomenclature(self):
        """Should preserve 'or' in dual nomenclature oils like Castor"""
        oil = Mock(spec=Oil)
        oil.id = "castor-oil"
        oil.common_name = "Castor Oil"
        oil.saponified_inci_name = "Sodium Castorate or Sodium Ricinoleate"

        name, is_generated = get_saponified_inci_name(oil, "naoh")

        assert " or " in name
        assert "Castorate" in name
        assert "Ricinoleate" in name

    def test_get_name_castor_converted_to_koh(self):
        """Should convert dual nomenclature to potassium form"""
        oil = Mock(spec=Oil)
        oil.id = "castor-oil"
        oil.common_name = "Castor Oil"
        oil.saponified_inci_name = "Sodium Castorate or Sodium Ricinoleate"

        name, is_generated = get_saponified_inci_name(oil, "koh")

        assert "Potassium Castorate" in name
        assert "Potassium Ricinoleate" in name
        assert "Sodium" not in name


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_common_name(self):
        """Should handle empty common name gracefully"""
        with pytest.raises(ValueError):
            generate_saponified_name("", "naoh")

    def test_none_common_name(self):
        """Should handle None common name"""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            generate_saponified_name(None, "naoh")

    def test_special_characters_in_name(self):
        """Should handle special characters appropriately"""
        result = generate_saponified_name("Oil-X/Y", "naoh")
        # Should still generate valid INCI name
        assert "Sodium" in result
        assert "ate" in result

    def test_very_long_oil_name(self):
        """Should handle very long oil names"""
        long_name = "Super Ultra Premium Extra Virgin Cold Pressed Oil"
        result = generate_saponified_name(long_name, "naoh")
        assert "Sodium" in result
        assert len(result) < 200  # Should fit in database field
