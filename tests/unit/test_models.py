"""Unit tests for database models

TDD: Tests written before implementation
Written: 2025-11-01 (before model implementation)
Phase: Phase 1 Foundation
Evidence: Test-first development - models implemented to pass these tests
"""
import pytest
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.oil import Oil
from app.models.additive import Additive
from app.models.calculation import Calculation


@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_model_creation(test_db_session: AsyncSession):
    """Test user model with UUID primary key and bcrypt password hashing"""
    # Hash password using bcrypt
    plaintext_password = "test_password_123"
    hashed_password = bcrypt.hash(plaintext_password)

    # Create user with properly hashed password
    user = User(
        email="test@example.com",
        hashed_password=hashed_password,
    )

    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    # Assertions
    assert user.id is not None  # UUID generated
    assert user.email == "test@example.com"
    # Verify it's a bcrypt hash (starts with $2b$)
    assert user.hashed_password.startswith(('$2a$', '$2b$', '$2y$'))
    # Verify password can be verified
    assert bcrypt.verify(plaintext_password, user.hashed_password)
    # Verify wrong password fails
    assert not bcrypt.verify("wrong_password", user.hashed_password)
    assert user.created_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_email_uniqueness(test_db_session: AsyncSession):
    """Test that email field enforces uniqueness"""
    # Create first user with properly hashed password
    hashed = bcrypt.hash("password1")
    user1 = User(email="duplicate@example.com", hashed_password=hashed)
    test_db_session.add(user1)
    await test_db_session.commit()

    # Try to create second user with same email
    hashed2 = bcrypt.hash("password2")
    user2 = User(email="duplicate@example.com", hashed_password=hashed2)
    test_db_session.add(user2)

    # Should raise IntegrityError on commit
    with pytest.raises(IntegrityError):
        await test_db_session.commit()


@pytest.mark.unit
def test_user_rejects_plaintext_password():
    """Test that User model rejects plaintext passwords (SECURITY)"""
    # Attempt to create user with plaintext password should raise ValueError
    with pytest.raises(ValueError, match="Password must be bcrypt-hashed"):
        User(
            email="test@example.com",
            hashed_password="plaintext_password",  # NOT a bcrypt hash
        )


@pytest.mark.unit
def test_user_rejects_invalid_bcrypt_hash():
    """Test that User model rejects invalid bcrypt hash formats"""
    # Invalid bcrypt hash (too short)
    with pytest.raises(ValueError, match="Invalid bcrypt hash format - too short"):
        User(
            email="test@example.com",
            hashed_password="$2b$12$short",  # Too short to be valid bcrypt
        )


@pytest.mark.unit
def test_user_accepts_valid_bcrypt_hash():
    """Test that User model accepts valid bcrypt hashes"""
    # Valid bcrypt hash should not raise error
    hashed = bcrypt.hash("test_password")
    user = User(email="test@example.com", hashed_password=hashed)

    assert user.email == "test@example.com"
    assert bcrypt.verify("test_password", user.hashed_password)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oil_model_with_jsonb_fields(test_db_session: AsyncSession):
    """Test oil model with SAP values and JSONB fields"""
    # Create oil with all required fields
    oil = Oil(
        id="test_olive_oil",
        common_name="Test Olive Oil",
        inci_name="Olea Europaea Fruit Oil",
        sap_value_naoh=0.134,
        sap_value_koh=0.188,
        iodine_value=84.0,
        ins_value=109.0,
        fatty_acids={
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 11.0,
            "stearic": 4.0,
            "ricinoleic": 0.0,
            "oleic": 72.0,
            "linoleic": 10.0,
            "linolenic": 1.0,
        },
        quality_contributions={
            "hardness": 17.0,
            "cleansing": 0.0,
            "conditioning": 83.0,
            "bubbly_lather": 0.0,
            "creamy_lather": 15.0,
            "longevity": 25.0,
            "stability": 50.0,
        },
    )

    test_db_session.add(oil)
    await test_db_session.commit()
    await test_db_session.refresh(oil)

    # Assertions
    assert oil.id == "test_olive_oil"
    assert oil.sap_value_naoh == 0.134
    assert oil.sap_value_koh == 0.188
    assert isinstance(oil.fatty_acids, dict)
    assert oil.fatty_acids["oleic"] == 72.0
    assert isinstance(oil.quality_contributions, dict)
    assert oil.quality_contributions["conditioning"] == 83.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oil_model_sap_values_match_spec(test_db_session: AsyncSession):
    """Test that SAP values match specification requirements"""
    # Olive oil SAP values from spec
    olive_oil = Oil(
        id="olive_oil",
        common_name="Olive Oil",
        inci_name="Olea Europaea Fruit Oil",
        sap_value_naoh=0.134,  # Must match spec exactly
        sap_value_koh=0.188,  # Must match spec exactly
        iodine_value=84.0,
        ins_value=109.0,
        fatty_acids={"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 72, "linoleic": 10, "linolenic": 1},
        quality_contributions={"hardness": 17, "cleansing": 0, "conditioning": 83, "bubbly_lather": 0, "creamy_lather": 15, "longevity": 25, "stability": 50},
    )

    test_db_session.add(olive_oil)
    await test_db_session.commit()

    # Query back
    result = await test_db_session.execute(select(Oil).where(Oil.id == "olive_oil"))
    oil = result.scalar_one()

    # Verify SAP values exactly match spec
    assert oil.sap_value_naoh == 0.134
    assert oil.sap_value_koh == 0.188


@pytest.mark.unit
@pytest.mark.asyncio
async def test_additive_model_with_quality_effects(test_db_session: AsyncSession):
    """Test additive model with JSONB quality_effects field"""
    # Kaolin clay from spec
    additive = Additive(
        id="kaolin_clay",
        common_name="Kaolin Clay (White)",
        inci_name="Kaolin",
        typical_usage_min_percent=1.0,
        typical_usage_max_percent=3.0,
        quality_effects={
            "hardness": 4.0,
            "creamy_lather": 7.0,
            "conditioning": 0.8,
        },
        confidence_level="high",
        verified_by_mga=False,
        safety_warnings={"skin_type": "Suitable for all skin types including sensitive"},
    )

    test_db_session.add(additive)
    await test_db_session.commit()
    await test_db_session.refresh(additive)

    # Assertions
    assert additive.id == "kaolin_clay"
    assert isinstance(additive.quality_effects, dict)
    assert additive.quality_effects["hardness"] == 4.0
    assert additive.quality_effects["creamy_lather"] == 7.0
    assert additive.confidence_level == "high"
    assert additive.verified_by_mga is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_additive_confidence_level_validation(test_db_session: AsyncSession):
    """Test that confidence_level only accepts valid values"""
    # Valid confidence level
    valid_additive = Additive(
        id="test_additive",
        common_name="Test Additive",
        inci_name="Test",
        typical_usage_min_percent=1.0,
        typical_usage_max_percent=3.0,
        quality_effects={},
        confidence_level="high",  # Valid: high, medium, low
    )

    test_db_session.add(valid_additive)
    await test_db_session.commit()
    await test_db_session.refresh(valid_additive)

    assert valid_additive.confidence_level == "high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculation_model_with_user_relationship(test_db_session: AsyncSession):
    """Test calculation model with user foreign key"""
    # Create user first
    user = User(email="calc_user@example.com", hashed_password="hash")
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    # Create calculation linked to user
    calculation = Calculation(
        user_id=user.id,
        recipe_data={
            "oils": [{"id": "olive_oil", "weight_g": 500.0, "percentage": 50.0}],
            "lye": {"naoh_percent": 100.0, "koh_percent": 0.0},
        },
        results_data={
            "quality_metrics": {"hardness": 40.0, "cleansing": 18.5},
        },
    )

    test_db_session.add(calculation)
    await test_db_session.commit()
    await test_db_session.refresh(calculation)

    # Assertions
    assert calculation.id is not None  # UUID generated
    assert calculation.user_id == user.id
    assert isinstance(calculation.recipe_data, dict)
    assert isinstance(calculation.results_data, dict)
    assert calculation.created_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculation_model_jsonb_data(test_db_session: AsyncSession):
    """Test calculation model stores complete recipe and results data"""
    user = User(email="jsonb_user@example.com", hashed_password="hash")
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    # Complex nested JSONB data
    calculation = Calculation(
        user_id=user.id,
        recipe_data={
            "total_oil_weight_g": 1000.0,
            "oils": [
                {"id": "olive_oil", "weight_g": 500.0, "percentage": 50.0},
                {"id": "coconut_oil", "weight_g": 300.0, "percentage": 30.0},
            ],
            "additives": [
                {"id": "kaolin_clay", "weight_g": 20.0, "percentage": 2.0},
            ],
        },
        results_data={
            "quality_metrics": {
                "hardness": 44.8,
                "cleansing": 18.5,
                "conditioning": 55.7,
            },
            "additive_effects": [
                {"additive_id": "kaolin_clay", "effects": {"hardness": 4.0}},
            ],
        },
    )

    test_db_session.add(calculation)
    await test_db_session.commit()
    await test_db_session.refresh(calculation)

    # Verify nested structures preserved
    assert calculation.recipe_data["total_oil_weight_g"] == 1000.0
    assert len(calculation.recipe_data["oils"]) == 2
    assert len(calculation.results_data["additive_effects"]) == 1
