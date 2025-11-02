"""Pydantic schemas for authentication requests and responses"""
import uuid
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class UserRegisterRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength

        Requirements:
        - At least 8 characters (enforced by Field)
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRegisterResponse(BaseModel):
    """Response schema for user registration"""
    id: uuid.UUID
    email: str
    message: str = "User registered successfully"


class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    """User information in login response"""
    id: uuid.UUID
    email: str


class UserLoginResponse(BaseModel):
    """Response schema for user login"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class TokenPayload(BaseModel):
    """JWT token payload structure"""
    sub: str  # User ID as string
    email: str
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp