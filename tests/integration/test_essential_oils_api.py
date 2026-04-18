"""
Integration tests for essential oils API endpoints.

TDD Phase: RED - These tests MUST FAIL before implementing the endpoints.

Tests validate:
- GET /api/v1/essential-oils (list endpoint)
- GET /api/v1/essential-oils/{id}/recommend (recommendation endpoint)
- Max usage rate validation
- Scent profile and blending recommendations
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_lavender_in_db(db_session):
    """Create lavender essential oil in test database"""
    from app.models.essential_oil import EssentialOil

    lavender = EssentialOil(
        id="lavender",
        name="Lavender",
        botanical_name="Lavandula angustifolia",
        max_usage_rate_pct=3.0,
        scent_profile="Floral, sweet, herbaceous",
        blends_with=["Bergamot", "Clary Sage", "Geranium", "Patchouli"],
        note="Middle",
        category="floral",
        warnings=None,
        color_effect="May slightly darken soap",
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(lavender)
    db_session.commit()
    return lavender


@pytest.fixture
def sample_rose_otto_in_db(db_session):
    """Create rose otto essential oil with very low max rate"""
    from app.models.essential_oil import EssentialOil

    rose_otto = EssentialOil(
        id="rose_otto",
        name="Rose Otto",
        botanical_name="Rosa damascena",
        max_usage_rate_pct=0.025,  # Very low - expensive and potent
        scent_profile="Deep, rich, floral rose",
        blends_with=["Bergamot", "Geranium", "Jasmine", "Sandalwood"],
        note="Middle",
        category="floral",
        warnings="Extremely expensive; use sparingly",
        color_effect=None,
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(rose_otto)
    db_session.commit()
    return rose_otto


@pytest.fixture
def sample_peppermint_in_db(db_session):
    """Create peppermint essential oil"""
    from app.models.essential_oil import EssentialOil

    peppermint = EssentialOil(
        id="peppermint",
        name="Peppermint",
        botanical_name="Mentha piperita",
        max_usage_rate_pct=2.0,
        scent_profile="Fresh, minty, invigorating",
        blends_with=["Eucalyptus", "Lavender", "Rosemary", "Tea Tree"],
        note="Top",
        category="herbal",
        warnings="May cause skin sensitivity in high concentrations",
        color_effect=None,
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(peppermint)
    db_session.commit()
    return peppermint


class TestEssentialOilsList:
    """Test GET /api/v1/essential-oils endpoint"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_all_essential_oils(
        self, client: TestClient, sample_lavender_in_db, sample_peppermint_in_db
    ):
        """
        GIVEN: Multiple essential oils in database
        WHEN: GET /api/v1/essential-oils
        THEN: Should return list of all essential oils
        """
        response = client.get("/api/v1/essential-oils")

        assert response.status_code == 200
        data = response.json()
        assert "essential_oils" in data or "items" in data
        assert data["total_count"] >= 2

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_with_pagination(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Essential oils in database
        WHEN: GET /api/v1/essential-oils?limit=10&offset=0
        THEN: Should return paginated results
        """
        response = client.get("/api/v1/essential-oils?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "limit" in data or "page_size" in data

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_includes_essential_fields(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Essential oils in database
        WHEN: GET /api/v1/essential-oils
        THEN: Should include name, botanical_name, max_usage_rate_pct, category
        """
        response = client.get("/api/v1/essential-oils")

        assert response.status_code == 200
        data = response.json()

        items = data.get("essential_oils") or data.get("items")
        assert len(items) >= 1

        first_item = items[0]
        assert "name" in first_item
        assert "botanical_name" in first_item
        assert "max_usage_rate_pct" in first_item
        assert "category" in first_item


class TestEssentialOilRecommendation:
    """Test GET /api/v1/essential-oils/{id}/recommend endpoint"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_lavender_500g_batch(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender at 3% max usage rate
        WHEN: GET /api/v1/essential-oils/lavender/recommend?batch_size_g=500
        THEN: Should return 15g recommendation (500g × 3% = 15g)
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert data["amount_g"] == pytest.approx(15.0, rel=0.01)
        assert data["usage_percentage"] == 3.0

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_rose_otto_very_low_rate(self, client: TestClient, sample_rose_otto_in_db):
        """
        GIVEN: Rose Otto at 0.025% max usage rate
        WHEN: GET /api/v1/essential-oils/rose_otto/recommend?batch_size_g=500
        THEN: Should return 0.125g recommendation (500g × 0.025% = 0.125g)
        """
        response = client.get("/api/v1/essential-oils/rose_otto/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # 500 × 0.025% = 0.125g
        assert data["amount_g"] == pytest.approx(0.125, rel=0.01)
        assert data["usage_percentage"] == 0.025

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_peppermint_2_percent(self, client: TestClient, sample_peppermint_in_db):
        """
        GIVEN: Peppermint at 2% max usage rate
        WHEN: GET /api/v1/essential-oils/peppermint/recommend?batch_size_g=500
        THEN: Should return 10g recommendation (500g × 2% = 10g)
        """
        response = client.get("/api/v1/essential-oils/peppermint/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert data["amount_g"] == pytest.approx(10.0, rel=0.01)
        assert data["usage_percentage"] == 2.0

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_scent_profile(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender with scent profile
        WHEN: GET /api/v1/essential-oils/lavender/recommend
        THEN: Should include scent_profile in response
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert "scent_profile" in data
        assert "floral" in data["scent_profile"].lower()

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_blends_with(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender with blends_with recommendations
        WHEN: GET /api/v1/essential-oils/lavender/recommend
        THEN: Should include blends_with array
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert "blends_with" in data
        assert isinstance(data["blends_with"], list)
        assert len(data["blends_with"]) >= 3
        assert "Bergamot" in data["blends_with"]

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_note_category(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender with note and category
        WHEN: GET /api/v1/essential-oils/lavender/recommend
        THEN: Should include note (Middle) and category (floral)
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert data["note"] == "Middle"
        assert data["category"] == "floral"

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_includes_warnings(self, client: TestClient, sample_peppermint_in_db):
        """
        GIVEN: Peppermint with warnings
        WHEN: GET /api/v1/essential-oils/peppermint/recommend
        THEN: Should include warnings text
        """
        response = client.get("/api/v1/essential-oils/peppermint/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        assert "warnings" in data
        assert "sensitivity" in data["warnings"].lower()

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_no_warnings_if_none(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender without warnings
        WHEN: GET /api/v1/essential-oils/lavender/recommend
        THEN: Should have warnings=None or empty
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Warnings should be None or not present
        assert data.get("warnings") is None or data.get("warnings") == ""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_different_batch_sizes(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender recommendations
        WHEN: Requesting different batch sizes
        THEN: Should scale amounts proportionally
        """
        # Test 100g batch: 100 × 3% = 3g
        response_100 = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=100")
        assert response_100.status_code == 200
        assert response_100.json()["amount_g"] == pytest.approx(3.0, rel=0.01)

        # Test 1000g batch: 1000 × 3% = 30g
        response_1000 = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=1000")
        assert response_1000.status_code == 200
        assert response_1000.json()["amount_g"] == pytest.approx(30.0, rel=0.01)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_gram_to_ounce_conversion(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender recommendation in grams
        WHEN: Response includes ounce conversion
        THEN: Should convert grams to ounces (g / 28.35)
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        amount_g = data["amount_g"]
        amount_oz = data["amount_oz"]

        # 15g / 28.35 ≈ 0.53 oz
        assert amount_oz == pytest.approx(amount_g / 28.35, rel=0.01)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_invalid_eo_id(self, client: TestClient):
        """
        GIVEN: Non-existent essential oil ID
        WHEN: GET /api/v1/essential-oils/nonexistent/recommend
        THEN: Should return 404 Not Found
        """
        response = client.get("/api/v1/essential-oils/nonexistent/recommend?batch_size_g=500")

        assert response.status_code == 404

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_missing_batch_size(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender essential oil
        WHEN: GET /api/v1/essential-oils/lavender/recommend (no batch_size_g)
        THEN: Should return 422 Unprocessable Entity
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend")

        assert response.status_code == 422

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_recommend_negative_batch_size(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender essential oil
        WHEN: GET /api/v1/essential-oils/lavender/recommend?batch_size_g=-500
        THEN: Should return 422 Unprocessable Entity
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=-500")

        assert response.status_code == 422


class TestMaxUsageRateCalculation:
    """Test max usage rate validation and calculation"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_calculation_uses_max_rate(self, client: TestClient, sample_lavender_in_db):
        """
        GIVEN: Lavender with 3% max usage rate
        WHEN: Calculating recommendation
        THEN: Should use max_usage_rate_pct in formula
        """
        response = client.get("/api/v1/essential-oils/lavender/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Formula: (500 × 3) / 100 = 15.0
        assert data["amount_g"] == 15.0
        assert data["usage_percentage"] == 3.0

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_calculation_precision_for_low_rates(self, client: TestClient, sample_rose_otto_in_db):
        """
        GIVEN: Rose Otto with very low max rate (0.025%)
        WHEN: Calculating recommendation
        THEN: Should maintain precision for small amounts
        """
        response = client.get("/api/v1/essential-oils/rose_otto/recommend?batch_size_g=500")

        assert response.status_code == 200
        data = response.json()

        # Should maintain precision: 500 × 0.025% = 0.125g
        assert data["amount_g"] == pytest.approx(0.125, rel=0.001)
