"""
T022 [P] [US2]: Unit test for percentage sorting

Tests percentage-based ingredient sorting in descending order.
Verifies that all ingredient types (oils, water, lye, additives) are properly sorted.

User Story 2: Percentage-based sorting for regulatory compliance
"""
import pytest
from decimal import Decimal
from app.services.label_generator import sort_ingredients_by_percentage


class TestPercentageSorting:
    """Unit tests for percentage-based ingredient sorting"""

    def test_sort_simple_ingredients_descending(self):
        """Should sort ingredients by percentage in descending order"""
        ingredients = [
            {'name': 'Water', 'percentage': Decimal('35.0')},
            {'name': 'Olive Oil', 'percentage': Decimal('50.0')},
            {'name': 'Coconut Oil', 'percentage': Decimal('10.0')},
            {'name': 'Sodium Hydroxide', 'percentage': Decimal('5.0')},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # Verify descending order
        assert sorted_ingredients[0]['name'] == 'Olive Oil'
        assert sorted_ingredients[0]['percentage'] == Decimal('50.0')
        assert sorted_ingredients[1]['name'] == 'Water'
        assert sorted_ingredients[1]['percentage'] == Decimal('35.0')
        assert sorted_ingredients[2]['name'] == 'Coconut Oil'
        assert sorted_ingredients[2]['percentage'] == Decimal('10.0')
        assert sorted_ingredients[3]['name'] == 'Sodium Hydroxide'
        assert sorted_ingredients[3]['percentage'] == Decimal('5.0')

    def test_sort_with_equal_percentages(self):
        """Should maintain stable sort when percentages are equal"""
        ingredients = [
            {'name': 'Coconut Oil', 'percentage': Decimal('30.0')},
            {'name': 'Olive Oil', 'percentage': Decimal('30.0')},
            {'name': 'Palm Oil', 'percentage': Decimal('30.0')},
            {'name': 'Water', 'percentage': Decimal('10.0')},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # All 30% ingredients should be first
        assert sorted_ingredients[0]['percentage'] == Decimal('30.0')
        assert sorted_ingredients[1]['percentage'] == Decimal('30.0')
        assert sorted_ingredients[2]['percentage'] == Decimal('30.0')
        assert sorted_ingredients[3]['percentage'] == Decimal('10.0')

    def test_sort_mixed_ingredient_types(self):
        """Should sort all ingredient types together by percentage"""
        ingredients = [
            {'name': 'Lavender Essential Oil', 'percentage': Decimal('2.0'), 'type': 'additive'},
            {'name': 'Sodium Hydroxide', 'percentage': Decimal('12.5'), 'type': 'lye'},
            {'name': 'Coconut Oil', 'percentage': Decimal('20.0'), 'type': 'oil'},
            {'name': 'Water', 'percentage': Decimal('38.0'), 'type': 'water'},
            {'name': 'Olive Oil', 'percentage': Decimal('25.0'), 'type': 'oil'},
            {'name': 'Titanium Dioxide', 'percentage': Decimal('0.5'), 'type': 'colorant'},
            {'name': 'Palm Oil', 'percentage': Decimal('2.0'), 'type': 'oil'},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # Verify descending order regardless of type
        percentages = [ing['percentage'] for ing in sorted_ingredients]
        assert percentages == sorted(percentages, reverse=True)

        # Check specific order
        assert sorted_ingredients[0]['name'] == 'Water'  # 38.0%
        assert sorted_ingredients[1]['name'] == 'Olive Oil'  # 25.0%
        assert sorted_ingredients[2]['name'] == 'Coconut Oil'  # 20.0%
        assert sorted_ingredients[3]['name'] == 'Sodium Hydroxide'  # 12.5%

    def test_sort_with_trace_ingredients(self):
        """Should include trace ingredients (<1%) in sorted list"""
        ingredients = [
            {'name': 'Water', 'percentage': Decimal('40.0')},
            {'name': 'Olive Oil', 'percentage': Decimal('35.0')},
            {'name': 'Coconut Oil', 'percentage': Decimal('20.0')},
            {'name': 'Sodium Hydroxide', 'percentage': Decimal('4.5')},
            {'name': 'Lavender EO', 'percentage': Decimal('0.3')},
            {'name': 'Titanium Dioxide', 'percentage': Decimal('0.2')},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # All ingredients should be present
        assert len(sorted_ingredients) == 6

        # Trace ingredients at the end
        assert sorted_ingredients[-2]['name'] == 'Lavender EO'
        assert sorted_ingredients[-2]['percentage'] == Decimal('0.3')
        assert sorted_ingredients[-1]['name'] == 'Titanium Dioxide'
        assert sorted_ingredients[-1]['percentage'] == Decimal('0.2')

    def test_sort_empty_list(self):
        """Should handle empty ingredient list"""
        ingredients = []
        sorted_ingredients = sort_ingredients_by_percentage(ingredients)
        assert sorted_ingredients == []

    def test_sort_single_ingredient(self):
        """Should handle single ingredient"""
        ingredients = [
            {'name': 'Olive Oil', 'percentage': Decimal('100.0')}
        ]
        sorted_ingredients = sort_ingredients_by_percentage(ingredients)
        assert len(sorted_ingredients) == 1
        assert sorted_ingredients[0]['name'] == 'Olive Oil'

    def test_sort_preserves_all_fields(self):
        """Should preserve all ingredient fields during sorting"""
        ingredients = [
            {
                'name': 'Olive Oil',
                'percentage': Decimal('60.0'),
                'inci_name': 'Sodium Olivate',
                'category': 'oil',
                'is_generated': False
            },
            {
                'name': 'Water',
                'percentage': Decimal('40.0'),
                'inci_name': 'Aqua',
                'category': 'water',
                'is_generated': False
            },
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # All fields should be preserved
        assert sorted_ingredients[0]['inci_name'] == 'Sodium Olivate'
        assert sorted_ingredients[0]['category'] == 'oil'
        assert sorted_ingredients[0]['is_generated'] is False

    def test_sort_with_high_precision_percentages(self):
        """Should handle high-precision decimal percentages"""
        ingredients = [
            {'name': 'Water', 'percentage': Decimal('35.123456')},
            {'name': 'Olive Oil', 'percentage': Decimal('35.123457')},  # Slightly higher
            {'name': 'Coconut Oil', 'percentage': Decimal('29.753087')},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # Should respect precision difference
        assert sorted_ingredients[0]['name'] == 'Olive Oil'
        assert sorted_ingredients[1]['name'] == 'Water'
        assert sorted_ingredients[2]['name'] == 'Coconut Oil'
