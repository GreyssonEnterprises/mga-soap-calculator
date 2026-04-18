"""Tests for authentication endpoints (registration and login)"""

import pytest
from fastapi import status
from httpx import AsyncClient
from passlib.hash import bcrypt
from sqlalchemy import select

from app.core.security import decode_access_token
from app.models.user import User


class TestUserRegistration:
    """Test user registration endpoint"""

    @pytest.mark.asyncio
    async def test_register_user_success(self, async_client: AsyncClient, test_db_session):
        """Test successful user registration"""
        request_data = {"email": "newuser@example.com", "password": "SecurePassword123!"}

        response = await async_client.post("/api/v1/auth/register", json=request_data)

        assert response.status_code == status.HTTP_201_CREATED

        # Verify response structure
        data = response.json()
        assert "id" in data
        assert data["email"] == request_data["email"]
        assert "message" in data
        assert data["message"] == "User registered successfully"

        # Verify user was created in database
        stmt = select(User).where(User.email == request_data["email"])
        result = await test_db_session.execute(stmt)
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.email == request_data["email"]
        # Verify password was hashed
        assert bcrypt.verify(request_data["password"], user.hashed_password)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient, test_db_session):
        """Test registration with duplicate email"""
        # Create existing user
        existing_user = User(
            email="existing@example.com", hashed_password=bcrypt.hash("ExistingPassword123!")
        )
        test_db_session.add(existing_user)
        await test_db_session.commit()

        # Try to register with same email
        request_data = {"email": "existing@example.com", "password": "NewPassword456!"}

        response = await async_client.post("/api/v1/auth/register", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email_format(self, async_client: AsyncClient):
        """Test registration with invalid email format"""
        request_data = {"email": "not-an-email", "password": "SecurePassword123!"}

        response = await async_client.post("/api/v1/auth/register", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password"""
        request_data = {
            "email": "newuser@example.com",
            "password": "weak",  # Too short
        }

        response = await async_client.post("/api/v1/auth/register", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "password" in data["detail"].lower()


class TestUserLogin:
    """Test user login endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_db_session):
        """Test successful login with valid credentials"""
        # Create a user
        password = "TestPassword123!"
        user = User(email="testuser@example.com", hashed_password=bcrypt.hash(password))
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Login request
        request_data = {"email": "testuser@example.com", "password": password}

        response = await async_client.post("/api/v1/auth/login", json=request_data)

        assert response.status_code == status.HTTP_200_OK

        # Verify response structure
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["id"] == str(user.id)
        assert data["user"]["email"] == user.email

        # Verify token is valid
        token_payload = decode_access_token(data["access_token"])
        assert token_payload["sub"] == str(user.id)
        assert token_payload["email"] == user.email

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client: AsyncClient, test_db_session):
        """Test login with incorrect password"""
        # Create a user
        user = User(
            email="testuser@example.com", hashed_password=bcrypt.hash("CorrectPassword123!")
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Login with wrong password
        request_data = {"email": "testuser@example.com", "password": "WrongPassword456!"}

        response = await async_client.post("/api/v1/auth/login", json=request_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent email"""
        request_data = {"email": "nonexistent@example.com", "password": "SomePassword123!"}

        response = await async_client.post("/api/v1/auth/login", json=request_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, async_client: AsyncClient):
        """Test login with invalid email format"""
        request_data = {"email": "not-an-email", "password": "SomePassword123!"}

        response = await async_client.post("/api/v1/auth/login", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
