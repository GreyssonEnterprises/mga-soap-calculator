"""
Integration tests for colorants API endpoints.

TDD Phase: RED - These tests MUST FAIL before implementing the endpoints.

Tests validate:
- GET /api/v1/colorants (list endpoint)
- Category filtering (9 color families)
- Pagination
- Response schema validation
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_turmeric_in_db(db_session):
    """Create turmeric colorant in test database"""
    from app.models.colorant import Colorant

    turmeric = Colorant(
        id="turmeric",
        name="Turmeric",
        botanical="Curcuma longa",
        category="yellow",
        usage="1 tsp PPO",
        method="Infuse in oil or add at trace",
        color_range="Bright yellow to deep golden",
        warnings="Can stain; may fade over time",
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(turmeric)
    db_session.commit()
    return turmeric


@pytest.fixture
def sample_annatto_in_db(db_session):
    """Create annatto colorant in test database"""
    from app.models.colorant import Colorant

    annatto = Colorant(
        id="annatto_seeds",
        name="Annatto Seeds",
        botanical="Bixa orellana",
        category="orange",
        usage="1 tsp PPO infused oil",
        method="Infuse seeds in liquid oil, strain, use infused oil",
        color_range="Buttery yellow to pumpkin orange",
        warnings=None,
        confidence_level="high",
        verified_by_mga=False,
    )
    db_session.add(annatto)
    db_session.commit()
    return annatto


@pytest.fixture
def sample_spirulina_in_db(db_session):
    """Create spirulina colorant in test database"""
    from app.models.colorant import Colorant

    spirulina = Colorant(
        id="spirulina",
        name="Spirulina Powder",
        botanical="Arthrospira platensis",
        category="green",
        usage="1/4-1 tsp PPO",
        method="Mix with water, add at trace",
        color_range="Sage green to teal",
        warnings=None,
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(spirulina)
    db_session.commit()
    return spirulina


@pytest.fixture
def sample_charcoal_in_db(db_session):
    """Create activated charcoal colorant in test database"""
    from app.models.colorant import Colorant

    charcoal = Colorant(
        id="activated_charcoal",
        name="Activated Charcoal",
        botanical="Carbon",
        category="black",
        usage="1/4-1 tsp PPO",
        method="Mix with water, add at light trace",
        color_range="Gray to black",
        warnings="Can be messy; may accelerate trace",
        confidence_level="high",
        verified_by_mga=True,
    )
    db_session.add(charcoal)
    db_session.commit()
    return charcoal


class TestColorantsList:
    """Test GET /api/v1/colorants endpoint"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_all_colorants(
        self,
        client: TestClient,
        sample_turmeric_in_db,
        sample_annatto_in_db,
        sample_spirulina_in_db,
    ):
        """
        GIVEN: Multiple colorants in database
        WHEN: GET /api/v1/colorants
        THEN: Should return list of all colorants
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()
        assert "colorants" in data or "items" in data
        assert data["total_count"] >= 3

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_with_pagination(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorants in database
        WHEN: GET /api/v1/colorants?limit=10&offset=0
        THEN: Should return paginated results
        """
        response = client.get("/api/v1/colorants?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "limit" in data or "page_size" in data
        assert "offset" in data or "page" in data

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_list_includes_essential_fields(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorants in database
        WHEN: GET /api/v1/colorants
        THEN: Should include name, botanical, category, method, color_range
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) >= 1

        first_item = items[0]
        assert "name" in first_item
        assert "botanical" in first_item
        assert "category" in first_item
        assert "method" in first_item
        assert "color_range" in first_item


class TestColorantCategoryFiltering:
    """Test category filtering for 9 color families"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_yellow_category(
        self, client: TestClient, sample_turmeric_in_db, sample_annatto_in_db
    ):
        """
        GIVEN: Colorants with different categories
        WHEN: GET /api/v1/colorants?category=yellow
        THEN: Should return only yellow colorants
        """
        response = client.get("/api/v1/colorants?category=yellow")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) >= 1
        # All returned items should be yellow category
        assert all(item["category"] == "yellow" for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_orange_category(
        self, client: TestClient, sample_turmeric_in_db, sample_annatto_in_db
    ):
        """
        GIVEN: Colorants with different categories
        WHEN: GET /api/v1/colorants?category=orange
        THEN: Should return only orange colorants
        """
        response = client.get("/api/v1/colorants?category=orange")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) >= 1
        assert all(item["category"] == "orange" for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_green_category(self, client: TestClient, sample_spirulina_in_db):
        """
        GIVEN: Green colorant in database
        WHEN: GET /api/v1/colorants?category=green
        THEN: Should return only green colorants
        """
        response = client.get("/api/v1/colorants?category=green")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) >= 1
        assert all(item["category"] == "green" for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_black_category(self, client: TestClient, sample_charcoal_in_db):
        """
        GIVEN: Black colorant in database
        WHEN: GET /api/v1/colorants?category=black
        THEN: Should return only black colorants
        """
        response = client.get("/api/v1/colorants?category=black")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) >= 1
        assert all(item["category"] == "black" for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_all_nine_categories(self, client: TestClient, db_session):
        """
        GIVEN: Database with colorants in all 9 categories
        WHEN: Filtering by each category
        THEN: Should return results for each valid category
        """
        from app.models.colorant import Colorant

        # Create one colorant for each color family
        categories = [
            "yellow",
            "orange",
            "pink",
            "red",
            "green",
            "blue",
            "purple",
            "brown",
            "black",
        ]

        for idx, category in enumerate(categories):
            colorant = Colorant(
                id=f"test_{category}",
                name=f"Test {category.title()}",
                botanical=f"Testus {category}",
                category=category,
                method="Test method",
                color_range=f"{category.title()} range",
                confidence_level="medium",
                verified_by_mga=False,
            )
            db_session.add(colorant)
        db_session.commit()

        # Test filtering by each category
        for category in categories:
            response = client.get(f"/api/v1/colorants?category={category}")
            assert response.status_code == 200

            data = response.json()
            items = data.get("colorants") or data.get("items")
            assert len(items) >= 1
            assert all(item["category"] == category for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_filter_invalid_category(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorants in database
        WHEN: GET /api/v1/colorants?category=invalid
        THEN: Should return empty results or 400 Bad Request
        """
        response = client.get("/api/v1/colorants?category=invalid")

        # Should either return 400 or empty results
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            items = data.get("colorants") or data.get("items")
            assert len(items) == 0


class TestColorantResponseSchema:
    """Test response schema validation"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_response_includes_usage(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorant with usage information
        WHEN: GET /api/v1/colorants
        THEN: Should include usage field
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        turmeric = next(item for item in items if item["id"] == "turmeric")

        assert "usage" in turmeric
        assert "1 tsp PPO" in turmeric["usage"]

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_response_includes_method(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorant with method information
        WHEN: GET /api/v1/colorants
        THEN: Should include method field
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        turmeric = next(item for item in items if item["id"] == "turmeric")

        assert "method" in turmeric
        assert "infuse" in turmeric["method"].lower()

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_response_includes_color_range(self, client: TestClient, sample_turmeric_in_db):
        """
        GIVEN: Colorant with color_range information
        WHEN: GET /api/v1/colorants
        THEN: Should include color_range field
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        turmeric = next(item for item in items if item["id"] == "turmeric")

        assert "color_range" in turmeric
        assert "yellow" in turmeric["color_range"].lower()

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_response_includes_warnings_when_present(
        self, client: TestClient, sample_turmeric_in_db
    ):
        """
        GIVEN: Colorant with warnings
        WHEN: GET /api/v1/colorants
        THEN: Should include warnings field
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        turmeric = next(item for item in items if item["id"] == "turmeric")

        assert "warnings" in turmeric
        assert "stain" in turmeric["warnings"].lower()

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_response_warnings_null_when_absent(self, client: TestClient, sample_annatto_in_db):
        """
        GIVEN: Colorant without warnings
        WHEN: GET /api/v1/colorants
        THEN: Should have warnings=null
        """
        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        annatto = next(item for item in items if item["id"] == "annatto_seeds")

        # Warnings should be null or not present
        assert annatto.get("warnings") is None or "warnings" not in annatto


class TestColorantPagination:
    """Test pagination with colorants"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_pagination_with_category_filter(self, client: TestClient, db_session):
        """
        GIVEN: Multiple colorants in same category
        WHEN: GET /api/v1/colorants?category=yellow&limit=5&offset=0
        THEN: Should return paginated yellow colorants
        """
        from app.models.colorant import Colorant

        # Create 10 yellow colorants
        for i in range(10):
            colorant = Colorant(
                id=f"yellow_test_{i}",
                name=f"Yellow Test {i}",
                botanical=f"Testus yellow {i}",
                category="yellow",
                method="Test",
                color_range="Yellow",
                confidence_level="medium",
                verified_by_mga=False,
            )
            db_session.add(colorant)
        db_session.commit()

        # Request first page
        response = client.get("/api/v1/colorants?category=yellow&limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        assert len(items) == 5
        assert all(item["category"] == "yellow" for item in items)

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_pagination_has_more_indicator(self, client: TestClient, db_session):
        """
        GIVEN: More colorants than page size
        WHEN: Requesting first page
        THEN: Should indicate more results available
        """
        from app.models.colorant import Colorant

        # Create 15 colorants
        for i in range(15):
            colorant = Colorant(
                id=f"test_{i}",
                name=f"Test {i}",
                botanical=f"Testus {i}",
                category="yellow",
                method="Test",
                color_range="Yellow",
                confidence_level="medium",
                verified_by_mga=False,
            )
            db_session.add(colorant)
        db_session.commit()

        response = client.get("/api/v1/colorants?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()

        # Should indicate more results available
        assert data.get("has_more") is True or data["total_count"] > 10


class TestColorantSorting:
    """Test default sorting behavior"""

    @pytest.mark.skip(reason="TDD: RED phase - endpoint doesn't exist yet")
    def test_default_sort_by_name(self, client: TestClient, db_session):
        """
        GIVEN: Multiple colorants
        WHEN: GET /api/v1/colorants
        THEN: Should return results sorted alphabetically by name
        """
        from app.models.colorant import Colorant

        # Create colorants with different names
        names = ["Turmeric", "Annatto", "Spirulina", "Charcoal"]
        for name in names:
            colorant = Colorant(
                id=name.lower(),
                name=name,
                botanical=f"{name} botanical",
                category="yellow",
                method="Test",
                color_range="Test",
                confidence_level="medium",
                verified_by_mga=False,
            )
            db_session.add(colorant)
        db_session.commit()

        response = client.get("/api/v1/colorants")

        assert response.status_code == 200
        data = response.json()

        items = data.get("colorants") or data.get("items")
        names_returned = [item["name"] for item in items]

        # Should be sorted alphabetically
        assert names_returned == sorted(names_returned)
