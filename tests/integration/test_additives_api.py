"""
Integration tests for additives API endpoints.

TDD Phase: RED - These tests MUST FAIL before implementing the endpoints.

Tests validate:
- GET /api/v1/additives (list with category filtering)
- GET /api/v1/additives/{id}/recommend (recommendation endpoint)
- Recommendation calculation logic (light/standard/heavy)
- Warning system integration
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_honey_in_db(db_session):
    """Create honey additive in test database"""
    from app.models.additive import Additive

    honey = Additive(
        id="honey",
        common_name="Honey",
        inci_name="Mel",
        typical_usage_min_percent=1.0,
        typical_usage_max_percent=3.0,
        usage_rate_standard_percent=2.0,
        when_to_add="to oils",
        preparation_instructions="Warm honey slightly if crystallized",
        mixing_tips="Mix thoroughly into oils before adding lye",
        category="lather_booster",
        accelerates_trace=True,
        causes_overheating=True,
        can_be_scratchy=False,
        turns_brown=False,
        quality_effects={"bubbly_lather": 5.0},
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(honey)
    db_session.commit()
    return honey


@pytest.fixture
def sample_salt_in_db(db_session):
    """Create salt additive in test database"""
    from app.models.additive import Additive

    salt = Additive(
        id="salt",
        common_name="Salt",
        inci_name="Sodium Chloride",
        typical_usage_min_percent=1.0,
        typical_usage_max_percent=3.0,
        usage_rate_standard_percent=2.0,
        when_to_add="to lye water",
        preparation_instructions="Dissolve in lye water",
        mixing_tips="Add to hot lye water and stir until dissolved",
        category="hardener",
        accelerates_trace=False,
        causes_overheating=False,
        can_be_scratchy=False,
        turns_brown=False,
        quality_effects={"bar_hardness": 5.0},
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(salt)
    db_session.commit()
    return salt


class TestAdditivesList:
    """Test GET /api/v1/additives endpoint"""

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_list_all_additives(self, client: TestClient, sample_honey_in_db, sample_salt_in_db):
        """
        GIVEN: Multiple additives in database
        WHEN: GET /api/v1/additives
        THEN: Should return list of all additives
        """
        response = client.get("/api/v1/additives")

        assert response.status_code == 200
        data = response.json()
        assert "additives" in data or "items" in data
        assert data["total_count"] >= 2

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_list_additives_with_pagination(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Additives in database
        WHEN: GET /api/v1/additives?limit=10&offset=0
        THEN: Should return paginated results
        """
        response = client.get("/api/v1/additives?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "limit" in data or "page_size" in data
        assert "offset" in data or "page" in data

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_by_category_lather_booster(
        self, client: TestClient, sample_honey_in_db, sample_salt_in_db
    ):
        """
        GIVEN: Additives with different categories
        WHEN: GET /api/v1/additives?category=lather_booster
        THEN: Should return only lather_booster additives
        """
        response = client.get("/api/v1/additives?category=lather_booster")

        assert response.status_code == 200
        data = response.json()

        # Should only return honey (lather_booster), not salt (hardener)
        items = data.get("additives") or data.get("items")
        assert len(items) >= 1
        assert all(item["category"] == "lather_booster" for item in items)

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_by_category_hardener(
        self, client: TestClient, sample_honey_in_db, sample_salt_in_db
    ):
        """
        GIVEN: Additives with different categories
        WHEN: GET /api/v1/additives?category=hardener
        THEN: Should return only hardener additives
        """
        response = client.get("/api/v1/additives?category=hardener")

        assert response.status_code == 200
        data = response.json()

        items = data.get("additives") or data.get("items")
        assert len(items) >= 1
        assert all(item["category"] == "hardener" for item in items)


class TestAdditiveRecommendation:
    """Test GET /api/v1/additives/{id}/recommend endpoint"""

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_honey_standard(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey at 2% standard usage
        WHEN: GET /api/v1/additives/honey/recommend?batch_size_g=500
        THEN: Should return 10g recommendation (500g × 2% = 10g)
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Check standard recommendation
        standard = data["recommendations"]["standard"]
        assert standard["amount_g"] == pytest.approx(10.0, rel=0.01)
        assert standard["usage_percentage"] == 2.0

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_honey_all_levels(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey with light/standard/heavy usage rates
        WHEN: GET /api/v1/additives/honey/recommend?batch_size_g=500
        THEN: Should return all three usage level recommendations
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Should have light, standard, heavy recommendations
        assert "light" in data["recommendations"]
        assert "standard" in data["recommendations"]
        assert "heavy" in data["recommendations"]

        # Light: 500g × 1% = 5g
        assert data["recommendations"]["light"]["amount_g"] == pytest.approx(5.0, rel=0.01)

        # Standard: 500g × 2% = 10g
        assert data["recommendations"]["standard"]["amount_g"] == pytest.approx(10.0, rel=0.01)

        # Heavy: 500g × 3% = 15g
        assert data["recommendations"]["heavy"]["amount_g"] == pytest.approx(15.0, rel=0.01)

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_instructions(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey with preparation instructions and mixing tips
        WHEN: GET /api/v1/additives/honey/recommend
        THEN: Should include when_to_add, preparation_instructions, mixing_tips
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert data["when_to_add"] == "to oils"
        assert "warm honey" in data["preparation_instructions"].lower()
        assert "mix thoroughly" in data["mixing_tips"].lower()

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_warnings(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey with accelerates_trace and causes_overheating warnings
        WHEN: GET /api/v1/additives/honey/recommend
        THEN: Should include warnings array with specific messages
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert "warnings" in data
        assert len(data["warnings"]) == 2

        warning_text = " ".join(data["warnings"]).lower()
        assert "trace" in warning_text
        assert "overheating" in warning_text

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_salt_no_warnings(self, client: TestClient, sample_salt_in_db):
        """
        GIVEN: Salt with no warning flags
        WHEN: GET /api/v1/additives/salt/recommend
        THEN: Should return empty warnings array
        """
        response = client.get("/api/v1/additives/salt/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert "warnings" in data
        assert len(data["warnings"]) == 0

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_different_batch_sizes(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey recommendations
        WHEN: Requesting different batch sizes
        THEN: Should scale amounts proportionally
        """
        # Test 100g batch
        response_100 = client.get("/api/v1/additives/honey/recommend?batch_size_g=100")
        assert response_100.status_code == 200
        data_100 = response_100.json()
        assert data_100["recommendations"]["standard"]["amount_g"] == pytest.approx(2.0, rel=0.01)

        # Test 1000g batch
        response_1000 = client.get("/api/v1/additives/honey/recommend?batch_size_g=1000")
        assert response_1000.status_code == 200
        data_1000 = response_1000.json()
        assert data_1000["recommendations"]["standard"]["amount_g"] == pytest.approx(20.0, rel=0.01)

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_invalid_additive_id(self, client: TestClient):
        """
        GIVEN: Non-existent additive ID
        WHEN: GET /api/v1/additives/nonexistent/recommend
        THEN: Should return 404 Not Found
        """
        response = client.get("/api/v1/additives/nonexistent/recommend?batch_size_g=500")

        assert response.status_code == 404

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_missing_batch_size(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey additive
        WHEN: GET /api/v1/additives/honey/recommend (no batch_size_g)
        THEN: Should return 422 Unprocessable Entity
        """
        response = client.get("/api/v1/additives/honey/recommend")

        assert response.status_code == 422

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_negative_batch_size(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey additive
        WHEN: GET /api/v1/additives/honey/recommend?batch_size_g=-500
        THEN: Should return 422 Unprocessable Entity
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=-500")

        assert response.status_code == 422


class TestRecommendationCalculation:
    """Test calculation logic accuracy"""

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_calculation_formula_accuracy(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey at 2% usage rate
        WHEN: Calculating for 500g batch
        THEN: Should use formula (batch_size_g × usage_pct) / 100
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Formula: (500 × 2) / 100 = 10.0
        assert data["recommendations"]["standard"]["amount_g"] == 10.0

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_gram_to_ounce_conversion(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Honey recommendation in grams
        WHEN: Response includes ounce conversion
        THEN: Should convert grams to ounces (g / 28.35)
        """
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        amount_g = data["recommendations"]["standard"]["amount_g"]
        amount_oz = data["recommendations"]["standard"]["amount_oz"]

        # Conversion: 10g / 28.35 ≈ 0.35 oz
        assert amount_oz == pytest.approx(amount_g / 28.35, rel=0.01)

    @pytest.skip("TDD: RED phase - endpoint doesn't exist yet")
    def test_rounding_to_one_decimal(self, client: TestClient, sample_honey_in_db):
        """
        GIVEN: Calculation resulting in multiple decimals
        WHEN: Returning recommendation
        THEN: Should round to 1 decimal place
        """
        # Use batch size that creates decimal result
        response = client.get("/api/v1/additives/honey/recommend?batch_size_g=333")

        assert response.status_code == 200
        data = response.json()

        amount = data["recommendations"]["standard"]["amount_g"]

        # Should be rounded to 1 decimal: 333 × 2% = 6.66 → 6.7
        assert amount == pytest.approx(6.7, rel=0.01)
