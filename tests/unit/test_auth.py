"""Tests for JWT authentication and authorization"""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.hash import bcrypt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_access_token,
    get_current_user,
)
from app.models.user import User


class TestPasswordSecurity:
    """Test password hashing and verification"""

    def test_get_password_hash(self):
        """Test password hashing with bcrypt"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Verify it's a bcrypt hash
        assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
        assert len(hashed) >= 59

        # Verify the password verifies correctly
        assert bcrypt.verify(password, hashed)

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = bcrypt.hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = bcrypt.hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        password = "TestPassword123!"
        hashed = bcrypt.hash(password)

        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token generation and validation"""

    def test_create_access_token_structure(self):
        """Test JWT token contains required claims"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"

        token = create_access_token(
            data={"sub": user_id, "email": email}
        )

        # Decode token to verify structure
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Verify required claims
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_expiry(self):
        """Test token has correct 24-hour expiration"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"

        # Create token with default expiry
        token = create_access_token(
            data={"sub": user_id, "email": email}
        )

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Check expiration is approximately 24 hours from now
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_datetime = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        # Should be exactly 24 hours
        time_diff = exp_datetime - iat_datetime
        assert 23.9 <= time_diff.total_seconds() / 3600 <= 24.1

    def test_create_access_token_custom_expiry(self):
        """Test token with custom expiration time"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"
        expires_delta = timedelta(hours=1)

        token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=expires_delta
        )

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Check expiration is approximately 1 hour from now
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_datetime = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        time_diff = exp_datetime - iat_datetime
        assert 0.9 <= time_diff.total_seconds() / 3600 <= 1.1

    def test_decode_access_token_valid(self):
        """Test decoding a valid token"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"

        token = create_access_token(
            data={"sub": user_id, "email": email}
        )

        payload = decode_access_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email

    def test_decode_access_token_expired(self):
        """Test decoding an expired token raises exception"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"

        # Create token that expires immediately
        token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token has expired" in exc_info.value.detail

    def test_decode_access_token_invalid_signature(self):
        """Test decoding token with invalid signature"""
        user_id = str(uuid.uuid4())
        email = "test@example.com"

        # Create token with different secret
        token = jwt.encode(
            {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong_secret_key",
            algorithm=settings.ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate token" in exc_info.value.detail

    def test_decode_access_token_malformed(self):
        """Test decoding malformed token"""
        malformed_token = "not.a.valid.token"

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(malformed_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate token" in exc_info.value.detail


class TestGetCurrentUser:
    """Test user extraction from JWT tokens"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self, async_session):
        """Test extracting current user from valid token"""
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password=bcrypt.hash("TestPassword123!")
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create token for user
        token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Mock the HTTPBearer to return our token
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Get current user
        retrieved_user = await get_current_user(credentials, async_session)

        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_session):
        """Test get current user with invalid token"""
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, async_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub_claim(self, async_session):
        """Test get current user when token missing user_id"""
        # Create token without sub claim
        token = jwt.encode(
            {"email": "test@example.com", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, async_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token claims" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, async_session):
        """Test get current user when user doesn't exist in database"""
        fake_user_id = str(uuid.uuid4())

        token = create_access_token(
            data={"sub": fake_user_id, "email": "nonexistent@example.com"}
        )

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, async_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail