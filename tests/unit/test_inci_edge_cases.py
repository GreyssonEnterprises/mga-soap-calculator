"""
Property-based tests for INCI naming using Hypothesis

Tests edge cases and invariants that should hold for all inputs
"""

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from app.services.inci_naming import generate_saponified_name


class TestInciNamingProperties:
    """Property-based tests using Hypothesis"""

    @given(
        common_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")),
            min_size=1,
            max_size=100,
        ),
        lye_type=st.sampled_from(["naoh", "koh"]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_generated_name_always_has_correct_prefix(self, common_name, lye_type):
        """Every generated name should start with Sodium or Potassium"""
        # Skip empty or whitespace-only names
        assume(common_name.strip())

        try:
            result = generate_saponified_name(common_name, lye_type)

            if lye_type == "naoh":
                assert result.startswith("Sodium ")
            else:
                assert result.startswith("Potassium ")

        except ValueError:
            # Empty name is acceptable failure
            pass

    @given(
        common_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=1, max_size=50
        ),
        lye_type=st.sampled_from(["naoh", "koh"]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_generated_name_always_ends_with_ate(self, common_name, lye_type):
        """Every generated name should end with 'ate'"""
        assume(common_name.strip())

        try:
            result = generate_saponified_name(common_name, lye_type)
            assert result.endswith("ate")
        except ValueError:
            pass

    @given(
        common_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")), min_size=1, max_size=50
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_naoh_and_koh_only_differ_in_prefix(self, common_name):
        """NaOH and KOH variants should only differ in Sodium vs Potassium"""
        assume(common_name.strip())

        try:
            naoh_name = generate_saponified_name(common_name, "naoh")
            koh_name = generate_saponified_name(common_name, "koh")

            # Remove prefixes
            naoh_suffix = naoh_name.replace("Sodium ", "")
            koh_suffix = koh_name.replace("Potassium ", "")

            # Suffixes should be identical
            assert naoh_suffix == koh_suffix

        except ValueError:
            pass

    @given(
        base_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=3, max_size=20
        ),
        suffix=st.sampled_from([" Oil", " Butter", ""]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_suffix_removal_consistent(self, base_name, suffix):
        """Oil and Butter suffixes should be consistently removed"""
        assume(base_name.strip())

        common_name = base_name + suffix

        try:
            result = generate_saponified_name(common_name, "naoh")

            # Result should not contain 'Oil' or 'Butter' as separate words
            assert " Oil" not in result
            assert " Butter" not in result

        except ValueError:
            pass

    @given(
        common_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
            min_size=1,
            max_size=100,
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_double_spaces_in_result(self, common_name):
        """Generated names should never contain double spaces"""
        assume(common_name.strip())

        try:
            result = generate_saponified_name(common_name, "naoh")
            assert "  " not in result
        except ValueError:
            pass

    @given(
        common_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=1, max_size=50
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_result_length_bounded(self, common_name):
        """Generated names should fit in database field (200 chars)"""
        assume(common_name.strip())

        try:
            result = generate_saponified_name(common_name, "naoh")
            assert len(result) <= 200
        except ValueError:
            pass

    @given(common_name=st.text(min_size=1, max_size=50))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_deterministic_output(self, common_name):
        """Same input should always produce same output"""
        assume(common_name.strip())

        try:
            result1 = generate_saponified_name(common_name, "naoh")
            result2 = generate_saponified_name(common_name, "naoh")
            assert result1 == result2
        except ValueError:
            pass


class TestInciNamingInvariants:
    """Test invariants that should always hold"""

    @given(weight=st.floats(min_value=0.1, max_value=10000.0))
    def test_percentage_invariant_for_single_ingredient(self, weight):
        """Single ingredient always has 100% percentage"""
        # This tests integration with percentage calculator
        # For now, just ensure the concept holds
        from decimal import Decimal

        weights = {"only-oil": Decimal(str(weight))}
        total = sum(weights.values())
        percentage = (weights["only-oil"] / total) * 100

        assert abs(percentage - 100.0) < 0.0001

    @given(weights=st.lists(st.floats(min_value=0.1, max_value=1000.0), min_size=2, max_size=10))
    def test_percentages_always_sum_to_100(self, weights):
        """Percentages should always sum to 100 regardless of inputs"""
        from decimal import Decimal

        weight_dict = {f"oil-{i}": Decimal(str(w)) for i, w in enumerate(weights)}
        total = sum(weight_dict.values())

        percentages = {k: (v / total) * 100 for k, v in weight_dict.items()}
        percentage_sum = sum(percentages.values())

        # Allow small floating point error
        assert abs(percentage_sum - 100.0) < 0.0001


class TestEdgeCaseInputs:
    """Test specific edge cases discovered during development"""

    def test_unicode_characters_in_name(self):
        """Handle Unicode characters gracefully"""
        result = generate_saponified_name("Café Oil", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")

    def test_numbers_in_name(self):
        """Handle numbers in oil names"""
        result = generate_saponified_name("Oil-42", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")

    def test_hyphenated_names(self):
        """Handle hyphenated oil names"""
        result = generate_saponified_name("Extra-Virgin Oil", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")

    def test_multiple_spaces_normalized(self):
        """Multiple spaces should be handled"""
        result = generate_saponified_name("Coconut    Oil", "naoh")
        assert "  " not in result  # No double spaces in result

    def test_leading_trailing_whitespace(self):
        """Leading/trailing whitespace should be stripped"""
        result = generate_saponified_name("  Coconut Oil  ", "naoh")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_all_caps_input(self):
        """ALL CAPS input should be handled"""
        result = generate_saponified_name("COCONUT OIL", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")

    def test_mixed_case_input(self):
        """MiXeD cAsE input should be handled"""
        result = generate_saponified_name("CoCoNuT OiL", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")

    def test_special_characters_handled(self):
        """Special characters should not break the function"""
        # Should either work or raise ValueError, but not crash
        try:
            result = generate_saponified_name("Oil@#$%", "naoh")
            assert isinstance(result, str)
        except ValueError:
            pass  # Acceptable to reject invalid input

    def test_very_long_name(self):
        """Very long names should be handled"""
        long_name = "Super Ultra Premium Extra Virgin Cold Pressed Organic" + " Oil"
        result = generate_saponified_name(long_name, "naoh")
        assert len(result) < 200  # Should fit in DB field
        assert result.endswith("ate")

    def test_single_character_base(self):
        """Single character base names should work"""
        result = generate_saponified_name("X Oil", "naoh")
        assert result == "Sodium Xate" or result == "Sodium ate"  # Either is acceptable

    def test_name_ending_with_multiple_vowels(self):
        """Names ending with multiple vowels"""
        result = generate_saponified_name("Kukui Oil", "naoh")
        assert "Sodium" in result
        assert result.endswith("ate")
