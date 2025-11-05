"""
T024 [P] [US2]: Property-based test for percentage sum validation

Uses Hypothesis to generate random batches and verify percentages sum to ~100%.
Tests mathematical properties that should hold for ANY valid batch.

User Story 2: Percentage calculation accuracy with property-based testing
"""
import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, assume
from app.services.percentage_calculator import calculate_batch_percentages


# Strategy for generating positive decimal weights
positive_weight = st.decimals(
    min_value=Decimal('0.1'),
    max_value=Decimal('10000'),
    places=2
)


@given(
    coconut=positive_weight,
    olive=positive_weight,
    palm=positive_weight,
    water=positive_weight,
    naoh=positive_weight,
)
def test_percentages_always_sum_to_100(coconut, olive, palm, water, naoh):
    """Property: Percentages should always sum to ~100% regardless of weights"""
    batch_weights = {
        'oils': {
            'coconut-oil': coconut,
            'olive-oil': olive,
            'palm-oil': palm,
        },
        'water': water,
        'lye': {
            'naoh': naoh,
        },
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)
    total_percentage = sum(percentages.values())

    # Should sum to 100% within small tolerance
    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1'), \
        f"Percentages sum to {total_percentage}, expected ~100.0"


@given(
    oil_count=st.integers(min_value=1, max_value=10),
    weights=st.lists(positive_weight, min_size=1, max_size=10),
)
def test_percentages_sum_with_variable_oil_count(oil_count, weights):
    """Property: Should handle any number of oils (1-10)"""
    # Generate oil weights dict
    oils = {}
    for i in range(min(oil_count, len(weights))):
        oils[f'oil-{i}'] = weights[i]

    assume(len(oils) > 0)  # Ensure we have at least one oil

    batch_weights = {
        'oils': oils,
        'water': Decimal('380'),
        'lye': {'naoh': Decimal('143')},
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)
    total_percentage = sum(percentages.values())

    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')


@given(
    oil_weight=positive_weight,
    water_weight=positive_weight,
    lye_weight=positive_weight,
    additive_count=st.integers(min_value=0, max_value=5),
)
def test_percentages_with_variable_additives(oil_weight, water_weight, lye_weight, additive_count):
    """Property: Should handle 0-5 additives correctly"""
    # Generate additive weights
    additives = {}
    for i in range(additive_count):
        additives[f'additive-{i}'] = oil_weight * Decimal('0.02')  # 2% of oil weight

    batch_weights = {
        'oils': {'coconut-oil': oil_weight},
        'water': water_weight,
        'lye': {'naoh': lye_weight},
        'additives': additives
    }

    percentages = calculate_batch_percentages(batch_weights)
    total_percentage = sum(percentages.values())

    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')


@given(
    oil_weight=positive_weight,
    water_ratio=st.decimals(min_value=Decimal('0.3'), max_value=Decimal('0.5'), places=2),
    lye_ratio=st.decimals(min_value=Decimal('0.10'), max_value=Decimal('0.20'), places=2),
)
def test_realistic_soap_ratios(oil_weight, water_ratio, lye_ratio):
    """Property: Should work with realistic soap formulation ratios"""
    water_weight = oil_weight * water_ratio
    lye_weight = oil_weight * lye_ratio

    batch_weights = {
        'oils': {'coconut-oil': oil_weight},
        'water': water_weight,
        'lye': {'naoh': lye_weight},
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)
    total_percentage = sum(percentages.values())

    # Should sum to 100%
    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')

    # Oil should be largest component (typically 60-70%)
    assert percentages['coconut-oil'] > Decimal('50.0')


@given(
    coconut=positive_weight,
    olive=positive_weight,
)
def test_percentage_ratio_preservation(coconut, olive):
    """Property: Ratio between ingredients should be preserved"""
    assume(olive > 0)  # Avoid division by zero

    batch_weights = {
        'oils': {
            'coconut-oil': coconut,
            'olive-oil': olive,
        },
        'water': Decimal('380'),
        'lye': {'naoh': Decimal('143')},
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)

    # Calculate weight ratio
    weight_ratio = coconut / olive

    # Calculate percentage ratio
    percentage_ratio = percentages['coconut-oil'] / percentages['olive-oil']

    # Ratios should be equal (percentages preserve proportions)
    assert abs(weight_ratio - percentage_ratio) < Decimal('0.001')


@given(
    base_weight=positive_weight,
    multiplier=st.decimals(min_value=Decimal('1'), max_value=Decimal('10'), places=1),
)
def test_scaling_preserves_percentages(base_weight, multiplier):
    """Property: Scaling all weights by same factor preserves percentages"""
    # Original batch
    original_batch = {
        'oils': {'coconut-oil': base_weight},
        'water': base_weight * Decimal('0.38'),
        'lye': {'naoh': base_weight * Decimal('0.14')},
        'additives': {}
    }

    # Scaled batch
    scaled_batch = {
        'oils': {'coconut-oil': base_weight * multiplier},
        'water': base_weight * Decimal('0.38') * multiplier,
        'lye': {'naoh': base_weight * Decimal('0.14') * multiplier},
        'additives': {}
    }

    original_percentages = calculate_batch_percentages(original_batch)
    scaled_percentages = calculate_batch_percentages(scaled_batch)

    # Percentages should be identical
    for ingredient in original_percentages:
        assert abs(original_percentages[ingredient] - scaled_percentages[ingredient]) < Decimal('0.01')


@given(
    weights=st.lists(positive_weight, min_size=2, max_size=2),
)
def test_two_equal_ingredients_get_equal_percentages(weights):
    """Property: Equal weights should result in equal percentages"""
    equal_weight = weights[0]

    batch_weights = {
        'oils': {
            'coconut-oil': equal_weight,
            'olive-oil': equal_weight,
        },
        'water': Decimal('380'),
        'lye': {'naoh': Decimal('143')},
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)

    # Equal weights should produce equal percentages
    assert abs(percentages['coconut-oil'] - percentages['olive-oil']) < Decimal('0.001')


@given(
    naoh_weight=positive_weight,
    koh_weight=positive_weight,
)
def test_mixed_lye_percentages_sum_correctly(naoh_weight, koh_weight):
    """Property: Mixed lye batch should sum correctly"""
    batch_weights = {
        'oils': {'coconut-oil': Decimal('1000')},
        'water': Decimal('380'),
        'lye': {
            'naoh': naoh_weight,
            'koh': koh_weight,
        },
        'additives': {}
    }

    percentages = calculate_batch_percentages(batch_weights)
    total_percentage = sum(percentages.values())

    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')

    # Combined lye percentage should equal individual sum
    total_lye_percentage = percentages['naoh'] + percentages['koh']
    total_weight = Decimal('1000') + Decimal('380') + naoh_weight + koh_weight
    expected_lye_percentage = ((naoh_weight + koh_weight) / total_weight) * 100

    assert abs(total_lye_percentage - expected_lye_percentage) < Decimal('0.01')


@given(
    oil_weight=positive_weight,
    trace_additive=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1.0'), places=2),
)
def test_trace_ingredients_included_in_total(oil_weight, trace_additive):
    """Property: Even trace ingredients should be counted in total"""
    batch_weights = {
        'oils': {'coconut-oil': oil_weight},
        'water': oil_weight * Decimal('0.38'),
        'lye': {'naoh': oil_weight * Decimal('0.14')},
        'additives': {
            'trace-colorant': trace_additive,
        }
    }

    percentages = calculate_batch_percentages(batch_weights)

    # Should have percentage for trace ingredient
    assert 'trace-colorant' in percentages
    assert percentages['trace-colorant'] > Decimal('0')

    # Total should still be 100%
    total_percentage = sum(percentages.values())
    assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')


class TestPercentageSumEdgeCases:
    """Additional edge case tests for percentage sum validation"""

    def test_minimum_batch_size(self):
        """Should handle minimum viable batch (1g each component)"""
        batch_weights = {
            'oils': {'coconut-oil': Decimal('1')},
            'water': Decimal('1'),
            'lye': {'naoh': Decimal('1')},
            'additives': {}
        }

        percentages = calculate_batch_percentages(batch_weights)
        total = sum(percentages.values())

        assert abs(total - Decimal('100.0')) < Decimal('0.1')

    def test_large_batch_size(self):
        """Should handle large batch sizes (10000g)"""
        batch_weights = {
            'oils': {'coconut-oil': Decimal('10000')},
            'water': Decimal('3800'),
            'lye': {'naoh': Decimal('1430')},
            'additives': {}
        }

        percentages = calculate_batch_percentages(batch_weights)
        total = sum(percentages.values())

        assert abs(total - Decimal('100.0')) < Decimal('0.1')

    def test_high_precision_weights(self):
        """Should handle weights with many decimal places"""
        batch_weights = {
            'oils': {'coconut-oil': Decimal('333.333333')},
            'water': Decimal('126.666667'),
            'lye': {'naoh': Decimal('46.666667')},
            'additives': {}
        }

        percentages = calculate_batch_percentages(batch_weights)
        total = sum(percentages.values())

        # Should still sum to 100% despite high precision
        assert abs(total - Decimal('100.0')) < Decimal('0.1')
