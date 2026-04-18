"""
Integration tests for User Story 1: INCI Label Generation API

TDD RED PHASE: These tests MUST FAIL initially (endpoint doesn't exist yet)

Tests the complete flow:
1. API request validation
2. Service orchestration (percentage calc + INCI naming)
3. Response formatting
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestInciLabelEndpointBasic:
    """Basic INCI label generation functionality"""

    def test_simple_two_oil_formula(self):
        """Generate INCI label for simple 2-oil soap"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 300},
                    {"oil_id": "olive_oil", "weight_grams": 700},
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "inci_label" in data
        assert "ingredients" in data
        assert isinstance(data["ingredients"], list)
        assert len(data["ingredients"]) == 2

        # Verify INCI label format
        label = data["inci_label"]
        assert "Sodium Olivate" in label  # 70% - should be first
        assert "Sodium Cocoate" in label  # 30% - should be second
        assert label.index("Sodium Olivate") < label.index("Sodium Cocoate")

    def test_three_oil_formula(self):
        """Generate INCI label for 3-oil soap"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 200},
                    {"oil_id": "olive_oil", "weight_grams": 500},
                    {"oil_id": "palm_oil", "weight_grams": 300},
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify ordering: Olive (50%) > Palm (30%) > Coconut (20%)
        label = data["inci_label"]
        olive_pos = label.index("Sodium Olivate")
        palm_pos = label.index("Sodium Palmate")
        coconut_pos = label.index("Sodium Cocoate")

        assert olive_pos < palm_pos < coconut_pos

    def test_koh_soap(self):
        """Generate INCI label for potassium hydroxide soap"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 500},
                    {"oil_id": "olive_oil", "weight_grams": 500},
                ]
            },
            "lye_type": "koh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()

        label = data["inci_label"]
        assert "Potassium" in label  # Should use Potassium, not Sodium
        assert "Sodium" not in label
        assert "Potassium Olivate" in label
        assert "Potassium Cocoate" in label


class TestInciLabelEndpointIngredientDetails:
    """Test detailed ingredient information in response"""

    def test_ingredient_list_contains_percentages(self):
        """Each ingredient should include its percentage"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 300},
                    {"oil_id": "olive_oil", "weight_grams": 700},
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        data = response.json()

        ingredients = data["ingredients"]

        # Find coconut and olive
        coconut = next(i for i in ingredients if i["oil_id"] == "coconut_oil")
        olive = next(i for i in ingredients if i["oil_id"] == "olive_oil")

        assert coconut["percentage"] == 30.0
        assert olive["percentage"] == 70.0

    def test_ingredient_list_contains_inci_names(self):
        """Each ingredient should include its saponified INCI name"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 500},
                    {"oil_id": "castor_oil", "weight_grams": 500},
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        data = response.json()

        ingredients = data["ingredients"]

        coconut = next(i for i in ingredients if i["oil_id"] == "coconut_oil")
        castor = next(i for i in ingredients if i["oil_id"] == "castor_oil")

        assert coconut["saponified_inci_name"] == "Sodium Cocoate"
        assert "Sodium Castorate" in castor["saponified_inci_name"]  # Dual nomenclature

    def test_ingredient_list_is_sorted_by_percentage(self):
        """Ingredients should be sorted descending by percentage"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "coconut_oil", "weight_grams": 100},  # 10%
                    {"oil_id": "olive_oil", "weight_grams": 600},  # 60%
                    {"oil_id": "palm_oil", "weight_grams": 300},  # 30%
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        data = response.json()

        ingredients = data["ingredients"]
        percentages = [i["percentage"] for i in ingredients]

        # Should be sorted: [60, 30, 10]
        assert percentages == sorted(percentages, reverse=True)
        assert ingredients[0]["oil_id"] == "olive_oil"
        assert ingredients[1]["oil_id"] == "palm_oil"
        assert ingredients[2]["oil_id"] == "coconut_oil"


class TestInciLabelEndpointValidation:
    """Test request validation and error handling"""

    def test_missing_oils_returns_422(self):
        """Request without oils should return validation error"""
        payload = {"formulation": {}, "lye_type": "naoh"}

        response = client.post("/api/v1/inci/generate-label", json=payload)
        assert response.status_code == 422

    def test_empty_oils_list_returns_422(self):
        """Empty oils list should return validation error"""
        payload = {"formulation": {"oils": []}, "lye_type": "naoh"}

        response = client.post("/api/v1/inci/generate-label", json=payload)
        assert response.status_code == 422

    def test_invalid_lye_type_returns_422(self):
        """Invalid lye type should return validation error"""
        payload = {
            "formulation": {"oils": [{"oil_id": "coconut_oil", "weight_grams": 500}]},
            "lye_type": "invalid",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        assert response.status_code == 422

    def test_negative_weight_returns_422(self):
        """Negative weight should return validation error"""
        payload = {
            "formulation": {"oils": [{"oil_id": "coconut_oil", "weight_grams": -100}]},
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        assert response.status_code == 422

    def test_nonexistent_oil_returns_404(self):
        """Requesting nonexistent oil should return 404"""
        payload = {
            "formulation": {"oils": [{"oil_id": "nonexistent-oil", "weight_grams": 500}]},
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)
        assert response.status_code == 404
        assert "oil" in response.json()["detail"].lower()


class TestInciLabelEndpointEdgeCases:
    """Test edge cases and special scenarios"""

    def test_single_oil_formula(self):
        """Single oil should produce valid INCI label at 100%"""
        payload = {
            "formulation": {"oils": [{"oil_id": "olive_oil", "weight_grams": 1000}]},
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["inci_label"] == "Sodium Olivate"
        assert len(data["ingredients"]) == 1
        assert data["ingredients"][0]["percentage"] == 100.0

    def test_many_oils_formula(self):
        """Formula with many oils should handle correctly"""
        oils = [
            {"oil_id": "coconut_oil", "weight_grams": 100},
            {"oil_id": "olive_oil", "weight_grams": 200},
            {"oil_id": "palm_oil", "weight_grams": 150},
            {"oil_id": "castor_oil", "weight_grams": 50},
            {"oil_id": "shea_butter", "weight_grams": 100},
        ]

        payload = {"formulation": {"oils": oils}, "lye_type": "naoh"}

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredients"]) == 5

        # Verify percentages sum to 100
        total_pct = sum(i["percentage"] for i in data["ingredients"])
        assert abs(total_pct - 100.0) < 0.01

    def test_very_small_percentage_handling(self):
        """Oils with very small percentages should be handled"""
        payload = {
            "formulation": {
                "oils": [
                    {"oil_id": "olive_oil", "weight_grams": 990},
                    {"oil_id": "coconut_oil", "weight_grams": 10},
                ]
            },
            "lye_type": "naoh",
        }

        response = client.post("/api/v1/inci/generate-label", json=payload)

        assert response.status_code == 200
        data = response.json()

        coconut = next(i for i in data["ingredients"] if i["oil_id"] == "coconut_oil")
        assert coconut["percentage"] == 1.0
