"""
T023 [P] [US2]: Integration test for complete ingredient breakdown

Tests full batch percentage calculation including oils, water, lye, and additives.
Verifies all percentages sum to approximately 100%.

User Story 2: Complete ingredient breakdown with percentage sorting
"""
import pytest
from decimal import Decimal
from app.services.percentage_calculator import calculate_batch_percentages


class TestInciPercentageBreakdown:
    """Integration tests for complete ingredient percentage breakdown"""

    def test_complete_batch_percentages_sum_to_100(self):
        """Should calculate percentages for all ingredients summing to ~100%"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('300'),
                'olive-oil': Decimal('500'),
                'palm-oil': Decimal('200'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('142.5'),
            },
            'additives': {
                'lavender-eo': Decimal('15'),
                'titanium-dioxide': Decimal('2.5'),
            }
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Calculate total percentage
        total_percentage = sum(percentages.values())

        # Should sum to approximately 100% (within 0.1% tolerance for rounding)
        assert abs(total_percentage - Decimal('100.0')) < Decimal('0.1')

    def test_batch_breakdown_all_ingredient_types(self):
        """Should return percentages for all ingredient types"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('400'),
                'olive-oil': Decimal('600'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('143'),
            },
            'additives': {
                'lavender-eo': Decimal('20'),
            }
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Should have entries for all ingredients
        assert 'coconut-oil' in percentages
        assert 'olive-oil' in percentages
        assert 'water' in percentages
        assert 'naoh' in percentages
        assert 'lavender-eo' in percentages

        # Each should be > 0
        for ingredient_id, percentage in percentages.items():
            assert percentage > 0

    def test_batch_with_mixed_lye_types(self):
        """Should handle both NaOH and KOH in same batch"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('500'),
                'olive-oil': Decimal('500'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('100'),  # Mixed lye batch
                'koh': Decimal('50'),
            },
            'additives': {}
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Both lye types should have percentages
        assert 'naoh' in percentages
        assert 'koh' in percentages

        # NaOH should be higher percentage than KOH (100g vs 50g)
        assert percentages['naoh'] > percentages['koh']

        # Total should still be ~100%
        total = sum(percentages.values())
        assert abs(total - Decimal('100.0')) < Decimal('0.1')

    def test_batch_with_no_additives(self):
        """Should handle batch with no additives"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('400'),
                'olive-oil': Decimal('600'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('143'),
            },
            'additives': {}  # No additives
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Should only have oils, water, and lye
        assert len(percentages) == 4  # 2 oils + water + lye
        assert 'coconut-oil' in percentages
        assert 'olive-oil' in percentages
        assert 'water' in percentages
        assert 'naoh' in percentages

    def test_batch_with_multiple_additives(self):
        """Should handle batch with multiple additives"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('500'),
                'olive-oil': Decimal('500'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('143'),
            },
            'additives': {
                'lavender-eo': Decimal('15'),
                'peppermint-eo': Decimal('10'),
                'titanium-dioxide': Decimal('5'),
                'french-green-clay': Decimal('20'),
            }
        }

        percentages = calculate_batch_percentages(batch_weights)

        # All additives should be present
        assert 'lavender-eo' in percentages
        assert 'peppermint-eo' in percentages
        assert 'titanium-dioxide' in percentages
        assert 'french-green-clay' in percentages

        # Additives should have small percentages
        for additive in ['lavender-eo', 'peppermint-eo', 'titanium-dioxide', 'french-green-clay']:
            assert percentages[additive] < Decimal('5.0')

    def test_realistic_soap_recipe_percentages(self):
        """Should produce realistic percentages for typical soap recipe"""
        # Realistic recipe: 1000g oils, 38% water, standard lye
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('300'),   # 30% of oils
                'olive-oil': Decimal('400'),      # 40% of oils
                'palm-oil': Decimal('200'),       # 20% of oils
                'castor-oil': Decimal('100'),     # 10% of oils
            },
            'water': Decimal('380'),              # 38% of oil weight
            'lye': {
                'naoh': Decimal('142.5'),         # SAP value calculation
            },
            'additives': {
                'lavender-eo': Decimal('20'),     # 2% of oil weight
            }
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Total batch weight
        total_weight = (
            Decimal('1000') +  # oils
            Decimal('380') +   # water
            Decimal('142.5') + # lye
            Decimal('20')      # additives
        )
        # = 1542.5g

        # Verify realistic percentages
        # Olive oil should be highest oil (~26% of total batch)
        assert Decimal('25') < percentages['olive-oil'] < Decimal('27')

        # Water should be ~24-25% of total batch
        assert Decimal('24') < percentages['water'] < Decimal('26')

        # Lye should be ~9% of total batch
        assert Decimal('8') < percentages['naoh'] < Decimal('10')

        # Lavender EO should be ~1.3% of total batch
        assert Decimal('1') < percentages['lavender-eo'] < Decimal('2')

    def test_percentages_maintain_precision(self):
        """Should maintain high precision in percentage calculations"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('333.33'),
                'olive-oil': Decimal('333.33'),
                'palm-oil': Decimal('333.34'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('142.5'),
            },
            'additives': {}
        }

        percentages = calculate_batch_percentages(batch_weights)

        # All percentages should be Decimal type (not float)
        for percentage in percentages.values():
            assert isinstance(percentage, Decimal)

        # Total should be very close to 100.0
        total = sum(percentages.values())
        assert abs(total - Decimal('100.0')) < Decimal('0.01')

    def test_batch_with_trace_ingredients(self):
        """Should handle trace ingredients (<1%) correctly"""
        batch_weights = {
            'oils': {
                'coconut-oil': Decimal('500'),
                'olive-oil': Decimal('500'),
            },
            'water': Decimal('380'),
            'lye': {
                'naoh': Decimal('143'),
            },
            'additives': {
                'lavender-eo': Decimal('15'),         # ~1%
                'titanium-dioxide': Decimal('3'),     # ~0.2%
                'ultramarine-blue': Decimal('0.5'),   # ~0.03%
            }
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Trace ingredients should have very small percentages
        assert percentages['ultramarine-blue'] < Decimal('0.1')
        assert percentages['titanium-dioxide'] < Decimal('0.5')

        # But should still be > 0
        assert percentages['ultramarine-blue'] > Decimal('0')
        assert percentages['titanium-dioxide'] > Decimal('0')

    def test_batch_percentage_consistency_with_oil_only(self):
        """Should match oil-only percentage calculator for oil percentages"""
        from app.services.percentage_calculator import calculate_ingredient_percentages

        oil_weights = {
            'coconut-oil': Decimal('300'),
            'olive-oil': Decimal('700'),
        }

        # Oil-only percentages
        oil_percentages = calculate_ingredient_percentages(oil_weights)

        # Full batch
        batch_weights = {
            'oils': oil_weights,
            'water': Decimal('380'),
            'lye': {'naoh': Decimal('143')},
            'additives': {}
        }
        batch_percentages = calculate_batch_percentages(batch_weights)

        # Oil percentages within batch should maintain ratio
        batch_coconut = batch_percentages['coconut-oil']
        batch_olive = batch_percentages['olive-oil']

        # Ratio should be 30:70 (3:7)
        ratio = batch_coconut / batch_olive
        expected_ratio = Decimal('3') / Decimal('7')

        # Ratio should match within small tolerance
        assert abs(ratio - expected_ratio) < Decimal('0.001')
