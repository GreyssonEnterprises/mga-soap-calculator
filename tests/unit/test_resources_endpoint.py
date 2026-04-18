"""
Unit tests for resource discovery endpoints (oils and additives).

Tests pagination, search, sorting, filtering without requiring database.
Uses mocked database queries to isolate endpoint logic.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.additives import list_additives
from app.api.v1.resources import list_oils
from app.models.additive import Additive
from app.models.oil import Oil
from app.schemas.additive import AdditiveListResponse
from app.schemas.resource import OilListResponse


class TestOilsEndpointLogic:
    """Test oils endpoint query logic with mocked database"""

    @pytest.mark.asyncio
    async def test_list_oils_default_params(self):
        """Test oils endpoint with default parameters"""
        # Mock database session
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock oil data
        mock_oil = Mock(spec=Oil)
        mock_oil.id = "olive_oil"
        mock_oil.common_name = "Olive Oil"
        mock_oil.inci_name = "Olea Europaea Fruit Oil"
        mock_oil.sap_value_naoh = 0.134
        mock_oil.sap_value_koh = 0.188
        mock_oil.iodine_value = 84.0
        mock_oil.ins_value = 109.0
        mock_oil.fatty_acids = {"lauric": 0.0, "oleic": 72.0}
        mock_oil.quality_contributions = {"hardness": 17.0, "cleansing": 0.0}

        # Mock execute results
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_oil]

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        # Configure mock_db.execute to return different results
        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        # Call endpoint
        response = await list_oils(
            limit=50, offset=0, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        # Verify response structure
        assert isinstance(response, OilListResponse)
        assert response.total_count == 1
        assert response.limit == 50
        assert response.offset == 0
        assert response.has_more is False
        assert len(response.oils) == 1
        assert response.oils[0].id == "olive_oil"

    @pytest.mark.asyncio
    async def test_list_oils_pagination_has_more_true(self):
        """Test has_more flag is True when more results exist"""
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock 15 oils total, requesting 10 at offset 0
        mock_oils = [Mock(spec=Oil) for _ in range(10)]
        for i, oil in enumerate(mock_oils):
            oil.id = f"oil_{i}"
            oil.common_name = f"Oil {i}"
            oil.inci_name = f"Oil INCI {i}"
            oil.sap_value_naoh = 0.134
            oil.sap_value_koh = 0.188
            oil.iodine_value = 84.0
            oil.ins_value = 109.0
            oil.fatty_acids = {}
            oil.quality_contributions = {}

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_oils

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 15  # Total count

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_oils(
            limit=10, offset=0, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        # has_more should be True: offset(0) + limit(10) < total(15)
        assert response.has_more is True
        assert response.total_count == 15

    @pytest.mark.asyncio
    async def test_list_oils_pagination_has_more_false(self):
        """Test has_more flag is False at end of results"""
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock 10 oils total, requesting 10 at offset 5
        mock_oils = [Mock(spec=Oil) for _ in range(5)]
        for i, oil in enumerate(mock_oils):
            oil.id = f"oil_{i}"
            oil.common_name = f"Oil {i}"
            oil.inci_name = f"Oil INCI {i}"
            oil.sap_value_naoh = 0.134
            oil.sap_value_koh = 0.188
            oil.iodine_value = 84.0
            oil.ins_value = 109.0
            oil.fatty_acids = {}
            oil.quality_contributions = {}

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_oils

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 10  # Total count

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_oils(
            limit=10, offset=5, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        # has_more should be False: offset(5) + limit(10) >= total(10)
        assert response.has_more is False
        assert response.total_count == 10

    @pytest.mark.asyncio
    async def test_list_oils_empty_database(self):
        """Test oils endpoint with no data returns empty list"""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_oils(
            limit=50, offset=0, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        assert response.total_count == 0
        assert len(response.oils) == 0
        assert response.has_more is False

    @pytest.mark.asyncio
    async def test_list_oils_all_sort_options_asc(self):
        """Test oils endpoint supports all sort_by fields ascending"""
        sort_fields = ["common_name", "ins_value", "iodine_value"]

        for sort_field in sort_fields:
            mock_db = AsyncMock(spec=AsyncSession)

            mock_oil = Mock(spec=Oil)
            mock_oil.id = "test_oil"
            mock_oil.common_name = "Test Oil"
            mock_oil.inci_name = "Test INCI"
            mock_oil.sap_value_naoh = 0.134
            mock_oil.sap_value_koh = 0.188
            mock_oil.iodine_value = 84.0
            mock_oil.ins_value = 109.0
            mock_oil.fatty_acids = {}
            mock_oil.quality_contributions = {}

            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_oil]

            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1

            mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

            # Should not raise exception
            response = await list_oils(
                limit=50, offset=0, search=None, sort_by=sort_field, sort_order="asc", db=mock_db
            )

            assert len(response.oils) == 1

    @pytest.mark.asyncio
    async def test_list_oils_all_sort_options_desc(self):
        """Test oils endpoint supports all sort_by fields descending"""
        sort_fields = ["common_name", "ins_value", "iodine_value"]

        for sort_field in sort_fields:
            mock_db = AsyncMock(spec=AsyncSession)

            mock_oil = Mock(spec=Oil)
            mock_oil.id = "test_oil"
            mock_oil.common_name = "Test Oil"
            mock_oil.inci_name = "Test INCI"
            mock_oil.sap_value_naoh = 0.134
            mock_oil.sap_value_koh = 0.188
            mock_oil.iodine_value = 84.0
            mock_oil.ins_value = 109.0
            mock_oil.fatty_acids = {}
            mock_oil.quality_contributions = {}

            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_oil]

            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1

            mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

            response = await list_oils(
                limit=50, offset=0, search=None, sort_by=sort_field, sort_order="desc", db=mock_db
            )

            assert len(response.oils) == 1


class TestAdditivesEndpointLogic:
    """Test additives endpoint query logic with mocked database"""

    @pytest.mark.asyncio
    async def test_list_additives_default_params(self):
        """Test additives endpoint with default parameters"""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_additive = Mock(spec=Additive)
        mock_additive.id = "kaolin_clay"
        mock_additive.common_name = "Kaolin Clay"
        mock_additive.inci_name = "Kaolin"
        mock_additive.category = None
        mock_additive.usage_rate_min_pct = None
        mock_additive.usage_rate_max_pct = None
        mock_additive.usage_rate_standard_pct = None
        mock_additive.when_to_add = None
        mock_additive.confidence_level = "high"
        mock_additive.verified_by_mga = True

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_additive]

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_additives(
            limit=50,
            offset=0,
            search=None,
            confidence=None,
            verified_only=False,
            sort_by="common_name",
            sort_order="asc",
            db=mock_db,
        )

        assert isinstance(response, AdditiveListResponse)
        assert response.total_count == 1
        assert response.limit == 50
        assert response.offset == 0
        assert response.has_more is False
        assert len(response.additives) == 1
        assert response.additives[0].id == "kaolin_clay"

    @pytest.mark.asyncio
    async def test_list_additives_confidence_filter_high(self):
        """Test additives endpoint filters by confidence level"""
        mock_db = AsyncMock(spec=AsyncSession)

        # Mock only high-confidence additives
        mock_additive = Mock(spec=Additive)
        mock_additive.id = "high_confidence"
        mock_additive.common_name = "High Confidence Additive"
        mock_additive.inci_name = "Test INCI"
        mock_additive.category = None
        mock_additive.usage_rate_min_pct = None
        mock_additive.usage_rate_max_pct = None
        mock_additive.usage_rate_standard_pct = None
        mock_additive.when_to_add = None
        mock_additive.confidence_level = "high"
        mock_additive.verified_by_mga = False

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_additive]

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_additives(
            limit=50,
            offset=0,
            search=None,
            confidence="high",
            verified_only=False,
            sort_by="common_name",
            sort_order="asc",
            db=mock_db,
        )

        assert len(response.additives) == 1
        assert response.additives[0].id == "high_confidence"

    @pytest.mark.asyncio
    async def test_list_additives_verified_only_true(self):
        """Test additives endpoint filters by verified_by_mga"""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_additive = Mock(spec=Additive)
        mock_additive.id = "verified"
        mock_additive.common_name = "Verified Additive"
        mock_additive.inci_name = "Test INCI"
        mock_additive.category = None
        mock_additive.usage_rate_min_pct = None
        mock_additive.usage_rate_max_pct = None
        mock_additive.usage_rate_standard_pct = None
        mock_additive.when_to_add = None
        mock_additive.confidence_level = "high"
        mock_additive.verified_by_mga = True

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_additive]

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_additives(
            limit=50,
            offset=0,
            search=None,
            confidence=None,
            verified_only=True,
            sort_by="common_name",
            sort_order="asc",
            db=mock_db,
        )

        assert len(response.additives) == 1
        assert response.additives[0].id == "verified"

    @pytest.mark.asyncio
    async def test_list_additives_combined_filters(self):
        """Test additives endpoint with multiple filters combined"""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_additive = Mock(spec=Additive)
        mock_additive.id = "filtered"
        mock_additive.common_name = "Filtered Additive"
        mock_additive.inci_name = "Test INCI"
        mock_additive.category = None
        mock_additive.usage_rate_min_pct = None
        mock_additive.usage_rate_max_pct = None
        mock_additive.usage_rate_standard_pct = None
        mock_additive.when_to_add = None
        mock_additive.confidence_level = "high"
        mock_additive.verified_by_mga = True

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [mock_additive]

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_additives(
            limit=50,
            offset=0,
            search=None,
            confidence="high",
            verified_only=True,
            sort_by="common_name",
            sort_order="asc",
            db=mock_db,
        )

        assert len(response.additives) == 1
        assert response.additives[0].id == "filtered"

    @pytest.mark.asyncio
    async def test_list_additives_all_confidence_levels(self):
        """Test additives endpoint accepts all confidence levels"""
        confidence_levels = ["high", "medium", "low"]

        for confidence in confidence_levels:
            mock_db = AsyncMock(spec=AsyncSession)

            mock_additive = Mock(spec=Additive)
            mock_additive.id = f"{confidence}_additive"
            mock_additive.common_name = f"{confidence.title()} Additive"
            mock_additive.inci_name = "Test INCI"
            mock_additive.category = None
            mock_additive.usage_rate_min_pct = None
            mock_additive.usage_rate_max_pct = None
            mock_additive.usage_rate_standard_pct = None
            mock_additive.when_to_add = None
            mock_additive.confidence_level = confidence
            mock_additive.verified_by_mga = False

            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_additive]

            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1

            mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

            response = await list_additives(
                limit=50,
                offset=0,
                search=None,
                confidence=confidence,
                verified_only=False,
                sort_by="common_name",
                sort_order="asc",
                db=mock_db,
            )

            assert len(response.additives) == 1
            assert response.additives[0].id == f"{confidence}_additive"

    @pytest.mark.asyncio
    async def test_list_additives_empty_database(self):
        """Test additives endpoint with no data returns empty list"""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_additives(
            limit=50,
            offset=0,
            search=None,
            confidence=None,
            verified_only=False,
            sort_by="common_name",
            sort_order="asc",
            db=mock_db,
        )

        assert response.total_count == 0
        assert len(response.additives) == 0
        assert response.has_more is False

    @pytest.mark.asyncio
    async def test_list_additives_all_sort_options(self):
        """Test additives endpoint supports all sort_by fields"""
        sort_fields = ["common_name", "confidence_level"]

        for sort_field in sort_fields:
            mock_db = AsyncMock(spec=AsyncSession)

            mock_additive = Mock(spec=Additive)
            mock_additive.id = "test_additive"
            mock_additive.common_name = "Test Additive"
            mock_additive.inci_name = "Test INCI"
            mock_additive.category = None
            mock_additive.usage_rate_min_pct = None
            mock_additive.usage_rate_max_pct = None
            mock_additive.usage_rate_standard_pct = None
            mock_additive.when_to_add = None
            mock_additive.confidence_level = "high"
            mock_additive.verified_by_mga = False

            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [mock_additive]

            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 1

            mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

            response = await list_additives(
                limit=50,
                offset=0,
                search=None,
                confidence=None,
                verified_only=False,
                sort_by=sort_field,
                sort_order="asc",
                db=mock_db,
            )

            assert len(response.additives) == 1


class TestPaginationCalculations:
    """Test pagination metadata calculations"""

    @pytest.mark.asyncio
    async def test_has_more_calculation_exact_boundary(self):
        """Test has_more is False when offset+limit exactly equals total"""
        mock_db = AsyncMock(spec=AsyncSession)

        # Total 50, offset 0, limit 50
        mock_oils = [Mock(spec=Oil) for _ in range(50)]
        for i, oil in enumerate(mock_oils):
            oil.id = f"oil_{i}"
            oil.common_name = f"Oil {i}"
            oil.inci_name = f"INCI {i}"
            oil.sap_value_naoh = 0.134
            oil.sap_value_koh = 0.188
            oil.iodine_value = 84.0
            oil.ins_value = 109.0
            oil.fatty_acids = {}
            oil.quality_contributions = {}

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_oils

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 50

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_oils(
            limit=50, offset=0, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        # 0 + 50 = 50 (not less than 50, so has_more = False)
        assert response.has_more is False

    @pytest.mark.asyncio
    async def test_has_more_calculation_one_more(self):
        """Test has_more is True when one more result exists"""
        mock_db = AsyncMock(spec=AsyncSession)

        # Total 51, offset 0, limit 50
        mock_oils = [Mock(spec=Oil) for _ in range(50)]
        for i, oil in enumerate(mock_oils):
            oil.id = f"oil_{i}"
            oil.common_name = f"Oil {i}"
            oil.inci_name = f"INCI {i}"
            oil.sap_value_naoh = 0.134
            oil.sap_value_koh = 0.188
            oil.iodine_value = 84.0
            oil.ins_value = 109.0
            oil.fatty_acids = {}
            oil.quality_contributions = {}

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_oils

        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 51

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        response = await list_oils(
            limit=50, offset=0, search=None, sort_by="common_name", sort_order="asc", db=mock_db
        )

        # 0 + 50 = 50 < 51 (has_more = True)
        assert response.has_more is True
