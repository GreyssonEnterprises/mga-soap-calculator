"""
T030 [US2]: Validation of User Story 2 acceptance criteria

Verifies that all ingredients (oils, water, lye, additives) are sorted by percentage
in descending order for regulatory compliance.

Acceptance Criteria:
1. All ingredient types included in percentage calculation
2. Ingredients sorted descending by percentage
3. Percentages sum to ~100%
4. Trace ingredients (<1%) included
5. Works with mixed lye types (NaOH + KOH)
"""

from decimal import Decimal

from app.services.label_generator import sort_ingredients_by_percentage
from app.services.percentage_calculator import calculate_batch_percentages


class TestUserStory2Acceptance:
    """
    User Story 2: As a product developer, I want labels sorted by percentage
    so that my product labels meet regulatory requirements
    """

    def test_ac1_all_ingredient_types_included(self):
        """AC1: All ingredient types (oils, water, lye, additives) included in calculation"""
        batch_weights = {
            "oils": {
                "coconut-oil": Decimal("300"),
                "olive-oil": Decimal("700"),
            },
            "water": Decimal("380"),
            "lye": {
                "naoh": Decimal("143"),
            },
            "additives": {
                "lavender-eo": Decimal("15"),
                "titanium-dioxide": Decimal("2.5"),
            },
        }

        percentages = calculate_batch_percentages(batch_weights)

        # All ingredient types should be present
        assert "coconut-oil" in percentages  # Oil type
        assert "olive-oil" in percentages  # Oil type
        assert "water" in percentages  # Water type
        assert "naoh" in percentages  # Lye type
        assert "lavender-eo" in percentages  # Additive type
        assert "titanium-dioxide" in percentages  # Additive type

        # Should have exactly 6 ingredients
        assert len(percentages) == 6

    def test_ac2_sorted_descending_by_percentage(self):
        """AC2: Ingredients sorted in descending order by percentage"""
        ingredients = [
            {"name": "Olive Oil", "percentage": Decimal("45.6")},
            {"name": "Water", "percentage": Decimal("24.8")},
            {"name": "Coconut Oil", "percentage": Decimal("19.5")},
            {"name": "Sodium Hydroxide", "percentage": Decimal("9.3")},
            {"name": "Lavender EO", "percentage": Decimal("1.0")},
            {"name": "Titanium Dioxide", "percentage": Decimal("0.2")},
        ]

        sorted_ingredients = sort_ingredients_by_percentage(ingredients)

        # Verify descending order
        for i in range(len(sorted_ingredients) - 1):
            current = sorted_ingredients[i]["percentage"]
            next_item = sorted_ingredients[i + 1]["percentage"]
            assert current >= next_item, f"Not sorted: {current} should be >= {next_item}"

        # Verify specific order for this data
        assert sorted_ingredients[0]["name"] == "Olive Oil"
        assert sorted_ingredients[1]["name"] == "Water"
        assert sorted_ingredients[2]["name"] == "Coconut Oil"
        assert sorted_ingredients[3]["name"] == "Sodium Hydroxide"
        assert sorted_ingredients[4]["name"] == "Lavender EO"
        assert sorted_ingredients[5]["name"] == "Titanium Dioxide"

    def test_ac3_percentages_sum_to_100(self):
        """AC3: All ingredient percentages sum to approximately 100%"""
        batch_weights = {
            "oils": {
                "coconut-oil": Decimal("400"),
                "olive-oil": Decimal("600"),
            },
            "water": Decimal("380"),
            "lye": {
                "naoh": Decimal("143"),
            },
            "additives": {
                "lavender-eo": Decimal("20"),
            },
        }

        percentages = calculate_batch_percentages(batch_weights)
        total = sum(percentages.values())

        # Should sum to 100% within tolerance
        assert abs(total - Decimal("100.0")) < Decimal("0.1"), (
            f"Percentages sum to {total}, expected ~100.0"
        )

    def test_ac4_trace_ingredients_included(self):
        """AC4: Trace ingredients (<1%) are included in sorted list"""
        batch_weights = {
            "oils": {
                "coconut-oil": Decimal("500"),
                "olive-oil": Decimal("500"),
            },
            "water": Decimal("380"),
            "lye": {
                "naoh": Decimal("143"),
            },
            "additives": {
                "lavender-eo": Decimal("15"),  # ~1%
                "titanium-dioxide": Decimal("3"),  # ~0.2%
                "ultramarine-blue": Decimal("0.5"),  # ~0.03%
            },
        }

        percentages = calculate_batch_percentages(batch_weights)

        # All trace ingredients should be present
        assert "titanium-dioxide" in percentages
        assert "ultramarine-blue" in percentages

        # Verify they are < 1%
        assert percentages["titanium-dioxide"] < Decimal("1.0")
        assert percentages["ultramarine-blue"] < Decimal("1.0")

        # But > 0%
        assert percentages["titanium-dioxide"] > Decimal("0")
        assert percentages["ultramarine-blue"] > Decimal("0")

    def test_ac5_mixed_lye_types_handled(self):
        """AC5: Both NaOH and KOH lye types handled correctly"""
        batch_weights = {
            "oils": {
                "coconut-oil": Decimal("500"),
                "olive-oil": Decimal("500"),
            },
            "water": Decimal("380"),
            "lye": {
                "naoh": Decimal("100"),  # Sodium hydroxide
                "koh": Decimal("50"),  # Potassium hydroxide
            },
            "additives": {},
        }

        percentages = calculate_batch_percentages(batch_weights)

        # Both lye types should be present
        assert "naoh" in percentages
        assert "koh" in percentages

        # NaOH should have higher percentage (100g vs 50g)
        assert percentages["naoh"] > percentages["koh"]

        # Total should still be ~100%
        total = sum(percentages.values())
        assert abs(total - Decimal("100.0")) < Decimal("0.1")

    def test_complete_user_story_2_scenario(self):
        """
        Complete User Story 2 scenario:
        Professional soap maker needs regulatory-compliant ingredient list
        sorted by percentage for product labeling.
        """
        # Realistic soap recipe
        batch_weights = {
            "oils": {
                "coconut-oil": Decimal("300"),  # 30% of oils
                "olive-oil": Decimal("400"),  # 40% of oils
                "palm-oil": Decimal("200"),  # 20% of oils
                "castor-oil": Decimal("100"),  # 10% of oils
            },
            "water": Decimal("380"),  # 38% of oil weight
            "lye": {
                "naoh": Decimal("142.5"),  # Standard SAP calculation
            },
            "additives": {
                "lavender-eo": Decimal("20"),  # 2% of oil weight
                "titanium-dioxide": Decimal("5"),  # Colorant
            },
        }

        # Step 1: Calculate percentages for ALL ingredients
        percentages = calculate_batch_percentages(batch_weights)

        # Step 2: Create ingredient list with percentages
        ingredients_list = [
            {"name": ingredient_id, "percentage": percentage}
            for ingredient_id, percentage in percentages.items()
        ]

        # Step 3: Sort by percentage (regulatory requirement)
        sorted_ingredients = sort_ingredients_by_percentage(ingredients_list)

        # Verify regulatory compliance
        # 1. All ingredients present (no missing types)
        assert len(sorted_ingredients) == 8  # 4 oils + water + lye + 2 additives

        # 2. Sorted descending
        percentages_only = [ing["percentage"] for ing in sorted_ingredients]
        assert percentages_only == sorted(percentages_only, reverse=True)

        # 3. Highest percentage first (olive oil in this recipe ~25.8%)
        assert sorted_ingredients[0]["name"] == "olive-oil"

        # 4. Oils sorted correctly by percentage (olive > coconut > palm > castor)
        oil_names = [ing["name"] for ing in sorted_ingredients if "-oil" in ing["name"]]
        assert oil_names[0] == "olive-oil"  # Highest oil percentage
        assert oil_names[1] == "coconut-oil"
        assert oil_names[2] == "palm-oil"
        assert oil_names[3] == "castor-oil"  # Lowest oil percentage

        # 5. Trace ingredients at end but still included
        # (titanium-dioxide should be last as smallest percentage)
        assert sorted_ingredients[-1]["name"] == "titanium-dioxide"
        assert sorted_ingredients[-1]["percentage"] < Decimal("1.0")

        # 6. Total percentage = 100%
        total = sum(ing["percentage"] for ing in sorted_ingredients)
        assert abs(total - Decimal("100.0")) < Decimal("0.1")

        print("\n✓ User Story 2 Complete:")
        print("  All ingredients sorted by percentage (descending)")
        print("  Regulatory compliance achieved")
        print("\nIngredient List:")
        for ing in sorted_ingredients:
            print(f"  {ing['name']}: {float(ing['percentage']):.1f}%")
